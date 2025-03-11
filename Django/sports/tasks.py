import logging
from celery import shared_task
from django.core.mail import send_mail
from .models import UserBet
from sports.models import latest_Moneyline

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def check_arbitrage_opportunities():
    logger.info("Starting arbitrage opportunity check...")

    # Get active bets
    active_bets = UserBet.objects.filter(is_active=True)
    logger.info(f"Found {len(active_bets)} active bets.")

    user_alerts = {}

    for bet in active_bets:
        logger.info(f"Processing bet for user {bet.user.id} on team {bet.team_bet_on} in game {bet.game_id}")

        latest_odds = None
        if bet.bet_type == "moneyline":
            latest_odds = latest_Moneyline.objects.filter(game_id=bet.game_id)
            logger.debug(f"Found {len(latest_odds)} odds entries for game {bet.game_id}.")

        if not latest_odds:
            logger.warning(f"No odds found for bet on game {bet.game_id} for team {bet.team_bet_on}. Skipping.")
            continue

        for odds in latest_odds:
            logger.debug(f"Checking odds from bookie {odds.bookie} for game {bet.game_id}.")

            # Select odds for the opposite team
            if bet.team_bet_on == odds.home_team:
                user_line = odds.line_2  # Away team odds
                opposite_team = odds.away_team
            elif bet.team_bet_on == odds.away_team:
                user_line = odds.line_1  # Home team odds
                opposite_team = odds.home_team
            else:
                logger.debug(f"Betting team {bet.team_bet_on} does not match either team in odds. Skipping.")
                continue

            logger.debug(f"User's line: {bet.line}, Bookie's line: {user_line} for {opposite_team}.")

            # Calculate implied probability for user's bet
            if bet.line < 0:
                user_implied_prob = abs(bet.line) / (abs(bet.line) + 100)
            else:
                user_implied_prob = 100 / (bet.line + 100)

            # Calculate implied probability for bookie's odds
            if user_line < 0:
                bookie_implied_prob = abs(user_line) / (abs(user_line) + 100)
            else:
                bookie_implied_prob = 100 / (user_line + 100)

            logger.debug(f"Implied Probability for User's Bet: {user_implied_prob:.2%}")
            logger.debug(f"Implied Probability for Bookie's Odds: {bookie_implied_prob:.2%}")

            # Calculate arbitrage return
            total_implied_prob = user_implied_prob + bookie_implied_prob
            logger.debug(f"Total Implied Probability: {total_implied_prob:.2%}")

            if total_implied_prob < 1:
                arb_return = (1 - total_implied_prob) / total_implied_prob
                logger.debug(f"Arbitrage Return: {arb_return:.2%}")
            else:
                arb_return = 0
                logger.debug("No arbitrage opportunity found (implied probability >= 100%).")

            # Check if arbitrage return meets the threshold
            if arb_return >= (bet.alert_threshold / 100):

                # User's bet odds
                if bet.line < 0:
                    user_odds = (100 / abs(bet.line)) + 1
                else:
                    user_odds = (bet.line / 100) + 1

                # Bookie's odds
                if user_line < 0:
                    bookie_odds = (100 / abs(user_line)) + 1
                else:
                    bookie_odds = (user_line / 100) + 1

                opposite_bet_amount = float(bet.bet_amount) * user_odds / bookie_odds

                logger.info(f"Arbitrage opportunity found for user {bet.user.id} on team {bet.team_bet_on} in game {bet.game_id}.")
                alert_message = (
                    f"You bet ${float(bet.bet_amount):.2f} on {bet.team_bet_on} at {bet.line}. \n"
                    f"{odds.bookie} has {user_line} for {opposite_team}. \n"
                    f"Bet ${opposite_bet_amount:.2f} on {opposite_team} to secure a {arb_return:.2%} profit!"
                )

                if bet.user.email not in user_alerts:
                    user_alerts[bet.user.email] = []

                # Add the alert along with its return to sort later
                user_alerts[bet.user.email].append((alert_message, arb_return))
            else:
                logger.debug(f"No arbitrage opportunity for bet on game {bet.game_id} with return {arb_return:.2%}.")

    # Sort user alerts by the largest arbitrage return
    for email, alerts in user_alerts.items():
        user_alerts[email] = sorted(alerts, key=lambda x: x[1], reverse=True)

    # Send emails
    for email, alerts in user_alerts.items():
        logger.info(f"Sending email to {email} with {len(alerts)} alerts.")
        sorted_alerts = [alert[0] for alert in alerts]  # Extract sorted alert messages
        send_mail(
            "Arbitrage Alert!",
            "\n\n".join(sorted_alerts),
            "smartlinesinbox@gmail.com",
            [email],
        )
    logger.info("Arbitrage opportunity check completed.")
