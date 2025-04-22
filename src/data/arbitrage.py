import logging

logger = logging.getLogger(__name__)

class ArbitrageAnalyzer:
    def __init__(self, bet_lines, min_profit_percentage=1, max_odds=50000, min_bookies_per_outcome=1):
        """Initialize the arbitrage analyzer with betting lines and parameters.

        Args:
            bet_lines: List of betting lines to analyze.
            min_profit_percentage: Minimum profit percentage to consider (default: 1).
            max_odds: Maximum odds to consider (default: 50000).
            min_bookies_per_outcome: Minimum number of bookies per outcome (default: 1).
        """
        self.bet_lines = bet_lines
        self.min_profit_percentage = min_profit_percentage
        self.max_odds = max_odds
        self.min_bookies_per_outcome = min_bookies_per_outcome

    def american_to_decimal(self, odds):
        """Convert American odds to decimal odds.

        Args:
            odds: American odds as an integer.

        Returns:
            Decimal odds as a float, or None if invalid.
        """
        if odds > 0:
            return (odds / 100.0) + 1
        elif odds < 0:
            return (100.0 / abs(odds)) + 1
        else:
            return None

    def analyze(self):
        """Analyze betting lines to find arbitrage opportunities for two-outcome props.

        Returns:
            List of tuples, each containing arbitrage opportunity details in the order:
            (game_ID, Prop_Type, Player_Name, Betting_Point, sport_type,
             bookie_one, outcome_one, odds_one, bet_amount_one,
             bookie_two, outcome_two, odds_two, bet_amount_two,
             profit_percentage, last_updated_timestamp)
        """
        logger.info(f"Number of bet lines loaded: {len(self.bet_lines)}")
        if not self.bet_lines:
            logger.error("No bet lines to analyze.")
            return []

        # Group betting lines by prop
        prop_groups = {}
        for line in self.bet_lines:
            game_id, last_updated_timestamp, bookie, prop_type, bet_type, player_name, betting_line, betting_point, sport_type = line
            if bet_type.lower() in ["yes", "no"]:
                prop_key = (game_id, prop_type, player_name)
                outcome = bet_type.lower()
                expected_outcomes = {"yes", "no"}
            elif bet_type.lower() in ["over", "under"]:
                prop_key = (game_id, prop_type, player_name, betting_point)
                outcome = bet_type.lower()
                expected_outcomes = {"over", "under"}
            else:
                logger.debug(f"Skipping unknown bet_type {bet_type} for prop {line}")
                continue

            if prop_key not in prop_groups:
                prop_groups[prop_key] = {
                    "outcomes": {},
                    "game_ID": game_id,
                    "Prop_Type": prop_type,
                    "Player_Name": player_name,
                    "Betting_Point": betting_point if bet_type.lower() in ["over", "under"] else "N/A",
                    "sport_type": sport_type,
                    "last_updated_timestamp": last_updated_timestamp,
                    "expected_outcomes": expected_outcomes
                }
            if outcome not in prop_groups[prop_key]["outcomes"]:
                prop_groups[prop_key]["outcomes"][outcome] = []
            prop_groups[prop_key]["outcomes"][outcome].append((bookie, betting_line))

        logger.info(f"Grouped {len(prop_groups)} props for arbitrage analysis")

        # Store arbitrage opportunities
        arbitrage_opportunities = []

        # Process each prop group
        for prop_key, data in prop_groups.items():
            outcomes_dict = data["outcomes"]
            expected_outcomes = data["expected_outcomes"]

            # Only process props with exactly two outcomes
            if set(outcomes_dict.keys()) != expected_outcomes:
                logger.debug(f"Skipping {prop_key}: Missing outcomes, have {outcomes_dict.keys()}")
                continue

            # Ensure minimum bookies per outcome
            for outcome in outcomes_dict:
                bookies = set(
                    bookie for bookie, odds in outcomes_dict[outcome]
                    if odds is not None and odds <= self.max_odds
                )
                if len(bookies) < self.min_bookies_per_outcome:
                    logger.debug(f"Skipping {prop_key}: Outcome {outcome} has {len(bookies)} bookies")
                    continue

            # Find best odds for each outcome
            best_odds_dict = {}
            for outcome in outcomes_dict:
                odds_list = [
                    odds for bookie, odds in outcomes_dict[outcome]
                    if odds is not None and odds <= self.max_odds
                ]
                if odds_list:
                    best_odds = max(odds_list)  # Highest American odds are best for bettor
                    bookies_offering_best = [
                        bookie for bookie, odds in outcomes_dict[outcome] if odds == best_odds
                    ]
                    best_odds_dict[outcome] = (best_odds, bookies_offering_best[0])  # Pick first bookie
                else:
                    break
            if len(best_odds_dict) != 2:
                continue

            # Convert to decimal odds
            decimal_odds = {
                outcome: self.american_to_decimal(odds)
                for outcome, (odds, _) in best_odds_dict.items()
            }
            if None in decimal_odds.values():
                continue

            # Check for arbitrage
            S = sum(1 / d for d in decimal_odds.values())
            if S < 1:
                profit_percentage = (1 / S - 1) * 100
                if profit_percentage >= self.min_profit_percentage:
                    # Calculate bet amounts for total wager of $100
                    total_stake = 100
                    outcome1, outcome2 = list(decimal_odds.keys())
                    d1 = decimal_odds[outcome1]
                    d2 = decimal_odds[outcome2]
                    betamount1 = total_stake * (d2 / (d1 + d2))
                    betamount2 = total_stake * (d1 / (d1 + d2))

                    # Extract bookies and odds
                    bookie1 = best_odds_dict[outcome1][1]
                    bookie2 = best_odds_dict[outcome2][1]
                    odds1 = best_odds_dict[outcome1][0]
                    odds2 = best_odds_dict[outcome2][0]

                    # Create tuple in the exact order expected by insert_arbitrage
                    arbitrage_tuple = (
                        data["game_ID"],
                        data["Prop_Type"],
                        data["Player_Name"],
                        str(data["Betting_Point"]),  # Ensure Betting_Point is a string
                        data["sport_type"],
                        bookie1,
                        outcome1,
                        odds1,
                        round(betamount1, 2),
                        bookie2,
                        outcome2,
                        odds2,
                        round(betamount2, 2),
                        round(profit_percentage, 2),
                        data["last_updated_timestamp"]
                    )
                    arbitrage_opportunities.append(arbitrage_tuple)

        # Sort by profit percentage
        arbitrage_opportunities.sort(key=lambda x: x[13], reverse=True)  # Index 13 is profit_percentage
        logger.info(f"Found {len(arbitrage_opportunities)} arbitrage opportunities" if arbitrage_opportunities else "No arbitrage opportunities found")
        return arbitrage_opportunities