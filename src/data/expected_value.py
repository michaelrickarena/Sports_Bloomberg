import logging
from statistics import median

logger = logging.getLogger(__name__)

class ExpectedValueAnalyzer:
    def __init__(self, bet_lines, min_bookies=2, ev_target=5, long_shot_threshold=400, long_shot_inflate=0.135, favorite_threshold=150, favorite_deflate=0.135):
        """Initialize the analyzer with bet lines (moneylines or props) and a minimum bookie threshold.
        
        Args:
            bet_lines: List of betting lines to analyze.
            min_bookies: Minimum number of bookies required (default: 2).
            ev_target: Target EV threshold for +EV bets (default: 7.5).
            long_shot_threshold: Odds threshold for long shots (default: 400).
            long_shot_inflate: Additional overround inflation for long shots (default: 0.03).
            favorite_threshold: Odds threshold for favorites (default: -100).
            favorite_deflate: Overround deflation for favorites (default: 0.015).
        """
        self.bet_lines = bet_lines
        self.min_bookies = min_bookies
        self.z_score_limit_types = ['batter_home_runs', 'batter_doubles']
        self.higher_z_limit = -2.2
        self.custom_bookie_limits = {
            'batter_doubles': 7,
            'batter_hits': 3,
            'batter_home_runs': 3,
            'batter_stolen_bases': 3,
            'player_double_double': 3,
            'player_goal_scorer_anytime': 3,
            'player_shots_on_goal': 3,
            'player_triple_double': 3,
            'batter_triples': 3
        }
        self.results = []
        self.ev_target = ev_target
        self.odds_max = 50000
        self.inflate_prop = {'player_goal_scorer_first'}
        self.inflate_rate = 0.03  # Base inflation rate for bets without both sides
        self.z_score_limit = -1.40  # Default z-score threshold
        self.multi_outcome_props = {
            'player_1st_td', 'player_last_td', 'player_first_basket', 'player_first_team_basket',
            'player_goal_scorer_first', 'player_goal_scorer_last', 'batter_first_home_run'
        }
        self.long_shot_threshold = long_shot_threshold
        self.long_shot_inflate = long_shot_inflate
        self.favorite_threshold = favorite_threshold
        self.favorite_deflate = favorite_deflate

    def get_bookie_limit(self, prop_type):
        """Return the bookie limit for a given prop type, defaulting to min_bookies if not specified."""
        return self.custom_bookie_limits.get(prop_type, self.min_bookies)

    def get_z_score_limit(self, prop_type):
        """Return the z-score limit for a given prop type, defaulting to z_score_limit if not specified."""
        if prop_type in self.z_score_limit_types:
            return self.higher_z_limit
        return self.z_score_limit

    def calculate_implied_probability(self, odds):
        """Calculate the implied probability based on American odds."""
        if odds > 0:
            return 100 / (odds + 100)
        elif odds < 0:
            return -odds / (-odds + 100)
        else:
            return None

    def calculate_expected_value(self, odds, fair_probability):
        """Calculate the expected value (EV) of a bet for a standard $100 bet."""
        bet_amount = 100
        if odds > 0:
            payout = (odds / 100) * bet_amount
        else:
            payout = (100 / abs(odds)) * bet_amount
        return (fair_probability * payout) - ((1 - fair_probability) * bet_amount)

    def calculate_z_score(self, imp_prob, imp_probs_list):
        """Calculate the z-score of an implied probability given a list of implied probabilities."""
        if len(imp_probs_list) < 2:
            return None
        mean_imp = sum(imp_probs_list) / len(imp_probs_list)
        variance = sum((p - mean_imp) ** 2 for p in imp_probs_list) / len(imp_probs_list)
        std_imp = variance ** 0.5
        if std_imp == 0:
            return 0
        return (imp_prob - mean_imp) / std_imp

    def calculate_estimated_ev(self, data, side, overround_est, best_bets):
        """Calculate EV for a single outcome prop side using an estimated overround, adjusted for long shots and favorites."""
        outcomes = data['outcomes']
        prop_type = data['Prop_Type']
        min_bookies = self.get_bookie_limit(prop_type)
        z_score_limit = self.get_z_score_limit(prop_type)
        if side not in outcomes or len(outcomes[side]) < min_bookies:
            return

        for bookie, odds in outcomes[side]:
            if odds is None or odds > self.odds_max:
                continue
            imp_prob = self.calculate_implied_probability(odds)
            if imp_prob is None:
                continue
            # Adjust overround based on odds
            adjusted_overround_est = overround_est
            if odds > self.long_shot_threshold:
                adjusted_overround_est += self.long_shot_inflate  # Increase for long shots
            elif odds < self.favorite_threshold:
                adjusted_overround_est = max(1.0, adjusted_overround_est - self.favorite_deflate)  # Decrease for favorites, ensure > 1.0
            fair_prob = imp_prob / adjusted_overround_est
            ev = self.calculate_expected_value(odds, fair_prob)
            if ev > self.ev_target:
                imp_probs = [self.calculate_implied_probability(o) for _, o in outcomes[side] if o is not None]
                z_score = self.calculate_z_score(imp_prob, imp_probs)
                if z_score is not None and z_score <= z_score_limit:
                    if side in ["yes", "no"]:
                        unique_key = (data['game_ID'], data['Prop_Type'], data['Player_Name'], side)
                        betting_point = "N/A"
                    else:  # "over" or "under"
                        unique_key = (data['game_ID'], data['Prop_Type'], data['Player_Name'], data['Betting_Point'], side)
                        betting_point = data['Betting_Point']
                    bet_tuple = (
                        data['game_ID'], bookie, data['Prop_Type'], side,
                        data['Player_Name'], betting_point, odds, round(ev, 2),
                        round(fair_prob, 4), round(imp_prob, 4), round(adjusted_overround_est, 4),
                        data['sport_type'], data['last_updated_timestamp'], len(outcomes[side]),
                        round(z_score, 2) if z_score is not None else None
                    )
                    if unique_key not in best_bets or ev > best_bets[unique_key][7]:
                        best_bets[unique_key] = bet_tuple

    def analyze_ml(self):
        """Analyze moneyline bets to find all +EV bets, returning a list of tuples."""
        logger.debug("Starting moneyline analysis...")
        game_dict = {}
        for line in self.bet_lines:
            game_id, bookie, matchup_type, team_1, odds_1, team_2, odds_2, event_timestamp, last_updated_timestamp, sport_type = line
            logger.debug(f"Processing line for game_ID {game_id} from bookie {bookie}")
            if game_id not in game_dict:
                game_dict[game_id] = {
                    'game_ID': game_id,
                    'teams': (team_1, team_2),
                    'team1_odds': [],
                    'team2_odds': [],
                    'Matchup_Type': matchup_type,
                    'sport_type': sport_type,
                    'event_timestamp': event_timestamp,
                    'last_updated_timestamp': last_updated_timestamp
                }
            game_dict[game_id]['team1_odds'].append((bookie, odds_1))
            game_dict[game_id]['team2_odds'].append((bookie, odds_2))

        self.results = []
        logger.debug(f"Grouped {len(game_dict)} games for analysis")
        for game_id, data in game_dict.items():
            team1_bookies = set(bookie for bookie, _ in data['team1_odds'])
            team2_bookies = set(bookie for bookie, _ in data['team2_odds'])
            if len(team1_bookies) < self.min_bookies or len(team2_bookies) < self.min_bookies:
                logger.info(f"Skipping game_ID {game_id}: Insufficient bookies")
                continue

            no_vig_probs_team1 = []
            for i in range(len(data['team1_odds'])):
                bookie1, odds1 = data['team1_odds'][i]
                bookie2, odds2 = data['team2_odds'][i]
                if bookie1 != bookie2:
                    logger.warning(f"Mismatch in bookies for game_ID {game_id}")
                    continue
                imp_prob1 = self.calculate_implied_probability(odds1)
                imp_prob2 = self.calculate_implied_probability(odds2)
                if imp_prob1 is None or imp_prob2 is None:
                    continue
                overround = imp_prob1 + imp_prob2
                if overround > 0:
                    no_vig_prob_team1 = imp_prob1 / overround
                    no_vig_probs_team1.append(no_vig_prob_team1)

            if not no_vig_probs_team1:
                logger.info(f"Skipping game_ID {game_id}: No valid no-vig probabilities")
                continue

            true_prob_team1 = median(no_vig_probs_team1)
            true_prob_team2 = 1 - true_prob_team1

            for bookie, odds in data['team1_odds']:
                if odds is None:
                    continue
                ev = self.calculate_expected_value(odds, true_prob_team1)
                if ev > self.ev_target:
                    imp_prob = self.calculate_implied_probability(odds)
                    self.results.append((
                        data['game_ID'], bookie, data['Matchup_Type'], data['teams'][0], odds,
                        round(ev, 2), round(true_prob_team1, 4), round(imp_prob, 4),
                        round(median(no_vig_probs_team1), 4), data['sport_type'], data['event_timestamp'],
                        data['last_updated_timestamp']
                    ))

            for bookie, odds in data['team2_odds']:
                if odds is None:
                    continue
                ev = self.calculate_expected_value(odds, true_prob_team2)
                if ev > self.ev_target:
                    imp_prob = self.calculate_implied_probability(odds)
                    self.results.append((
                        data['game_ID'], bookie, data['Matchup_Type'], data['teams'][1], odds,
                        round(ev, 2), round(true_prob_team2, 4), round(imp_prob, 4),
                        round(median(no_vig_probs_team1), 4), data['sport_type'], data['event_timestamp'],
                        data['last_updated_timestamp']
                    ))

        logger.info(f"Moneyline analysis completed. Found {len(self.results)} +EV opportunities")
        return self.results

    def analyze_prop(self):
        """Analyze prop bets to find the highest +EV bet for each unique player name, prop type, and betting point."""
        logger.info(f"Number of bet lines loaded: {len(self.bet_lines)}")
        if not self.bet_lines:
            logger.error("No bet lines to analyze.")
            return []

        multi_outcome_dict = {}
        single_outcome_dict = {}
        best_bets = {}

        # Group prop bets
        for line in self.bet_lines:
            game_id, last_updated_timestamp, bookie, prop_type, bet_type, player_name, betting_line, betting_point, sport_type = line
            if prop_type in self.multi_outcome_props and bet_type.lower() == "yes":
                game_key = (game_id, prop_type)
                if game_key not in multi_outcome_dict:
                    multi_outcome_dict[game_key] = {
                        'game_ID': game_id,
                        'Prop_Type': prop_type,
                        'sport_type': sport_type,
                        'last_updated_timestamp': last_updated_timestamp,
                        'players': {}
                    }
                if player_name not in multi_outcome_dict[game_key]['players']:
                    multi_outcome_dict[game_key]['players'][player_name] = []
                multi_outcome_dict[game_key]['players'][player_name].append((bookie, betting_line))
            elif bet_type.lower() in ["yes", "no"]:
                key = (game_id, prop_type, player_name)
                if key not in single_outcome_dict:
                    single_outcome_dict[key] = {
                        'game_ID': game_id,
                        'Prop_Type': prop_type,
                        'Player_Name': player_name,
                        'sport_type': sport_type,
                        'last_updated_timestamp': last_updated_timestamp,
                        'outcomes': {}
                    }
                if bet_type.lower() not in single_outcome_dict[key]['outcomes']:
                    single_outcome_dict[key]['outcomes'][bet_type.lower()] = []
                single_outcome_dict[key]['outcomes'][bet_type.lower()].append((bookie, betting_line))
            elif bet_type.lower() in ["over", "under"]:
                key = (game_id, prop_type, player_name, betting_point)
                if key not in single_outcome_dict:
                    single_outcome_dict[key] = {
                        'game_ID': game_id,
                        'Prop_Type': prop_type,
                        'Player_Name': player_name,
                        'Betting_Point': betting_point,
                        'sport_type': sport_type,
                        'last_updated_timestamp': last_updated_timestamp,
                        'outcomes': {}
                    }
                if bet_type.lower() not in single_outcome_dict[key]['outcomes']:
                    single_outcome_dict[key]['outcomes'][bet_type.lower()] = []
                single_outcome_dict[key]['outcomes'][bet_type.lower()].append((bookie, betting_line))
            else:
                logger.debug(f"Skipping unknown bet_type {bet_type} for prop {line}")
                continue

        logger.info(f"Grouped {len(multi_outcome_dict)} multi-outcome props and {len(single_outcome_dict)} single-outcome props")

        # Collect overrounds for median vig calculation
        all_overrounds = []
        for key, data in single_outcome_dict.items():
            outcomes = data['outcomes']
            min_bookies = self.get_bookie_limit(data['Prop_Type'])
            if "yes" in outcomes and "no" in outcomes:
                bookies_both = set(bookie for bookie, _ in outcomes["yes"]) & set(bookie for bookie, _ in outcomes["no"])
                for bookie in bookies_both:
                    odds_yes = next(odds for b, odds in outcomes["yes"] if b == bookie)
                    odds_no = next(odds for b, odds in outcomes["no"] if b == bookie)
                    imp_prob_yes = self.calculate_implied_probability(odds_yes)
                    imp_prob_no = self.calculate_implied_probability(odds_no)
                    if imp_prob_yes is not None and imp_prob_no is not None:
                        overround = imp_prob_yes + imp_prob_no
                        if overround > 0:
                            all_overrounds.append(overround)
            elif "over" in outcomes and "under" in outcomes:
                bookies_both = set(bookie for bookie, _ in outcomes["over"]) & set(bookie for bookie, _ in outcomes["under"])
                for bookie in bookies_both:
                    odds_over = next(odds for b, odds in outcomes["over"] if b == bookie)
                    odds_under = next(odds for b, odds in outcomes["under"] if b == bookie)
                    imp_prob_over = self.calculate_implied_probability(odds_over)
                    imp_prob_under = self.calculate_implied_probability(odds_under)
                    if imp_prob_over is not None and imp_prob_under is not None:
                        overround = imp_prob_over + imp_prob_under
                        if overround > 0:
                            all_overrounds.append(overround)

        # Compute estimated overround
        if all_overrounds:
            median_overround = median(all_overrounds)
            overround_est = median_overround + self.inflate_rate
        else:
            logger.warning("No overrounds collected; using default overround_est")
            overround_est = 1.15 + self.inflate_rate

        # Analyze multi-outcome props
        for game_key, game_data in multi_outcome_dict.items():
            players = game_data['players']
            all_bookies = set()
            min_bookies = self.get_bookie_limit(game_data['Prop_Type'])
            z_score_limit = self.get_z_score_limit(game_data['Prop_Type'])
            for odds_list in players.values():
                all_bookies.update(bookie for bookie, _ in odds_list)
            if len(all_bookies) < min_bookies:
                logger.debug(f"Skipping {game_key}: Only {len(all_bookies)} bookies")
                continue

            player_median_probs = {}
            for player_name, odds_list in players.items():
                odds = [o for _, o in odds_list if o is not None]
                if not odds:
                    continue
                imp_probs = [self.calculate_implied_probability(o) for o in odds if self.calculate_implied_probability(o) is not None]
                if imp_probs:
                    median_imp_prob = median(imp_probs)
                    player_median_probs[player_name] = (median_imp_prob, odds_list)

            market_overround = sum(median_imp_prob for median_imp_prob, _ in player_median_probs.values())
            if game_data['Prop_Type'] in self.inflate_prop:
                market_overround *= (1 + self.inflate_rate)
            if market_overround <= 0:
                logger.warning(f"Invalid market overround {market_overround} for {game_key}")
                continue

            for player_name, (median_imp_prob, odds_list) in player_median_probs.items():
                bookies = set(bookie for bookie, _ in odds_list)
                if len(bookies) < min_bookies:
                    continue
                fair_prob = median_imp_prob / market_overround if market_overround > 0 else 0
                imp_probs = [self.calculate_implied_probability(o) for _, o in odds_list if o is not None]
                for bookie, odds in odds_list:
                    if odds is None or odds > self.odds_max:
                        continue
                    ev = self.calculate_expected_value(odds, fair_prob)
                    if ev > self.ev_target:
                        imp_prob = self.calculate_implied_probability(odds)
                        z_score = self.calculate_z_score(imp_prob, imp_probs)
                        if z_score is not None and z_score <= z_score_limit:
                            unique_key = (game_data['game_ID'], game_data['Prop_Type'], player_name)
                            bet_tuple = (
                                game_data['game_ID'], bookie, game_data['Prop_Type'], "yes",
                                player_name, "N/A", odds, round(ev, 2), round(fair_prob, 4),
                                round(imp_prob, 4), round(market_overround, 4),
                                game_data['sport_type'], game_data['last_updated_timestamp'], len(bookies),
                                round(z_score, 2) if z_score is not None else None
                            )
                            if unique_key not in best_bets or ev > best_bets[unique_key][7]:
                                best_bets[unique_key] = bet_tuple

        # Analyze single-outcome props
        for key, data in single_outcome_dict.items():
            outcomes = data['outcomes']
            min_bookies = self.get_bookie_limit(data['Prop_Type'])
            z_score_limit = self.get_z_score_limit(data['Prop_Type'])
            if "yes" in outcomes or "no" in outcomes:
                if "yes" in outcomes and "no" in outcomes:
                    bookies_both = set(bookie for bookie, _ in outcomes["yes"]) & set(bookie for bookie, _ in outcomes["no"])
                    if len(bookies_both) >= min_bookies:
                        # Accurate method
                        no_vig_probs_yes = []
                        for bookie in bookies_both:
                            odds_yes = next(odds for b, odds in outcomes["yes"] if b == bookie)
                            odds_no = next(odds for b, odds in outcomes["no"] if b == bookie)
                            imp_prob_yes = self.calculate_implied_probability(odds_yes)
                            imp_prob_no = self.calculate_implied_probability(odds_no)
                            if imp_prob_yes is None or imp_prob_no is None:
                                continue
                            overround = imp_prob_yes + imp_prob_no
                            if overround > 0:
                                no_vig_prob_yes = imp_prob_yes / overround
                                no_vig_probs_yes.append(no_vig_prob_yes)
                        if not no_vig_probs_yes:
                            logger.debug(f"Skipping {key}: No valid no-vig probabilities")
                            continue
                        true_prob_yes = median(no_vig_probs_yes)
                        true_prob_no = 1 - true_prob_yes

                        for bookie, odds in outcomes["yes"]:
                            if odds is None or odds > self.odds_max:
                                continue
                            # Adjust true probability for long shots
                            adjusted_true_prob_yes = true_prob_yes
                            if odds > self.long_shot_threshold:
                                adjusted_true_prob_yes *= (1 - self.long_shot_inflate)  # Reduce probability by long_shot_inflate
                            ev = self.calculate_expected_value(odds, adjusted_true_prob_yes)
                            if ev > self.ev_target:
                                imp_prob = self.calculate_implied_probability(odds)
                                imp_probs_yes = [self.calculate_implied_probability(o) for _, o in outcomes["yes"] if o is not None]
                                z_score = self.calculate_z_score(imp_prob, imp_probs_yes)
                                if z_score is not None and z_score <= z_score_limit:
                                    unique_key = (data['game_ID'], data['Prop_Type'], data['Player_Name'], "yes")
                                    bet_tuple = (
                                        data['game_ID'], bookie, data['Prop_Type'], "yes",
                                        data['Player_Name'], "N/A", odds, round(ev, 2),
                                        round(adjusted_true_prob_yes, 4), round(imp_prob, 4),
                                        round(median(no_vig_probs_yes), 4), data['sport_type'],
                                        data['last_updated_timestamp'], len(bookies_both),
                                        round(z_score, 2) if z_score is not None else None
                                    )
                                    if unique_key not in best_bets or ev > best_bets[unique_key][7]:
                                        best_bets[unique_key] = bet_tuple

                        for bookie, odds in outcomes["no"]:
                            if odds is None or odds > self.odds_max:
                                continue
                            # Adjust true probability for long shots
                            adjusted_true_prob_no = true_prob_no
                            if odds > self.long_shot_threshold:
                                adjusted_true_prob_no *= (1 - self.long_shot_inflate)  # Reduce probability by long_shot_inflate
                            ev = self.calculate_expected_value(odds, adjusted_true_prob_no)
                            if ev > self.ev_target:
                                imp_prob = self.calculate_implied_probability(odds)
                                imp_probs_no = [self.calculate_implied_probability(o) for _, o in outcomes["no"] if o is not None]
                                z_score = self.calculate_z_score(imp_prob, imp_probs_no)
                                if z_score is not None and z_score <= z_score_limit:
                                    unique_key = (data['game_ID'], data['Prop_Type'], data['Player_Name'], "no")
                                    bet_tuple = (
                                        data['game_ID'], bookie, data['Prop_Type'], "no",
                                        data['Player_Name'], "N/A", odds, round(ev, 2),
                                        round(adjusted_true_prob_no, 4), round(imp_prob, 4),
                                        round(median(no_vig_probs_yes), 4), data['sport_type'],
                                        data['last_updated_timestamp'], len(bookies_both),
                                        round(z_score, 2) if z_score is not None else None
                                    )
                                    if unique_key not in best_bets or ev > best_bets[unique_key][7]:
                                        best_bets[unique_key] = bet_tuple
                    else:
                        # Estimated method when both sides exist but not enough bookies
                        self.calculate_estimated_ev(data, "yes", overround_est, best_bets)
                        self.calculate_estimated_ev(data, "no", overround_est, best_bets)
                elif "yes" in outcomes:
                    self.calculate_estimated_ev(data, "yes", overround_est, best_bets)
                elif "no" in outcomes:
                    self.calculate_estimated_ev(data, "no", overround_est, best_bets)

            elif "over" in outcomes or "under" in outcomes:
                if "over" in outcomes and "under" in outcomes:
                    bookies_both = set(bookie for bookie, _ in outcomes["over"]) & set(bookie for bookie, _ in outcomes["under"])
                    if len(bookies_both) >= min_bookies:
                        # Accurate method
                        no_vig_probs_over = []
                        for bookie in bookies_both:
                            odds_over = next(odds for b, odds in outcomes["over"] if b == bookie)
                            odds_under = next(odds for b, odds in outcomes["under"] if b == bookie)
                            imp_prob_over = self.calculate_implied_probability(odds_over)
                            imp_prob_under = self.calculate_implied_probability(odds_under)
                            if imp_prob_over is None or imp_prob_under is None:
                                continue
                            overround = imp_prob_over + imp_prob_under
                            if overround > 0:
                                no_vig_prob_over = imp_prob_over / overround
                                no_vig_probs_over.append(no_vig_prob_over)
                        if not no_vig_probs_over:
                            logger.debug(f"Skipping {key}: No valid no-vig probabilities")
                            continue
                        true_prob_over = median(no_vig_probs_over)
                        true_prob_under = 1 - true_prob_over

                        for bookie, odds in outcomes["over"]:
                            if odds is None or odds > self.odds_max:
                                continue
                            # Adjust true probability for long shots
                            adjusted_true_prob_over = true_prob_over
                            if odds > self.long_shot_threshold:
                                adjusted_true_prob_over *= (1 - self.long_shot_inflate)  # Reduce probability by long_shot_inflate
                            ev = self.calculate_expected_value(odds, adjusted_true_prob_over)
                            if ev > self.ev_target:
                                imp_prob = self.calculate_implied_probability(odds)
                                imp_probs_over = [self.calculate_implied_probability(o) for _, o in outcomes["over"] if o is not None]
                                z_score = self.calculate_z_score(imp_prob, imp_probs_over)
                                if z_score is not None and z_score <= z_score_limit:
                                    unique_key = (data['game_ID'], data['Prop_Type'], data['Player_Name'], data['Betting_Point'], "over")
                                    bet_tuple = (
                                        data['game_ID'], bookie, data['Prop_Type'], "over",
                                        data['Player_Name'], data['Betting_Point'], odds,
                                        round(ev, 2), round(adjusted_true_prob_over, 4), round(imp_prob, 4),
                                        round(median(no_vig_probs_over), 4), data['sport_type'],
                                        data['last_updated_timestamp'], len(bookies_both),
                                        round(z_score, 2) if z_score is not None else None
                                    )
                                    if unique_key not in best_bets or ev > best_bets[unique_key][7]:
                                        best_bets[unique_key] = bet_tuple

                        for bookie, odds in outcomes["under"]:
                            if odds is None or odds > self.odds_max:
                                continue
                            # Adjust true probability for long shots
                            adjusted_true_prob_under = true_prob_under
                            if odds > self.long_shot_threshold:
                                adjusted_true_prob_under *= (1 - self.long_shot_inflate)  # Reduce probability by long_shot_inflate
                            ev = self.calculate_expected_value(odds, adjusted_true_prob_under)
                            if ev > self.ev_target:
                                imp_prob = self.calculate_implied_probability(odds)
                                imp_probs_under = [self.calculate_implied_probability(o) for _, o in outcomes["under"] if o is not None]
                                z_score = self.calculate_z_score(imp_prob, imp_probs_under)
                                if z_score is not None and z_score <= z_score_limit:
                                    unique_key = (data['game_ID'], data['Prop_Type'], data['Player_Name'], data['Betting_Point'], "under")
                                    bet_tuple = (
                                        data['game_ID'], bookie, data['Prop_Type'], "under",
                                        data['Player_Name'], data['Betting_Point'], odds,
                                        round(ev, 2), round(adjusted_true_prob_under, 4), round(imp_prob, 4),
                                        round(median(no_vig_probs_over), 4), data['sport_type'],
                                        data['last_updated_timestamp'], len(bookies_both),
                                        round(z_score, 2) if z_score is not None else None
                                    )
                                    if unique_key not in best_bets or ev > best_bets[unique_key][7]:
                                        best_bets[unique_key] = bet_tuple
                    else:
                        # Estimated method when both sides exist but not enough bookies
                        self.calculate_estimated_ev(data, "over", overround_est, best_bets)
                        self.calculate_estimated_ev(data, "under", overround_est, best_bets)
                elif "over" in outcomes:
                    self.calculate_estimated_ev(data, "over", overround_est, best_bets)
                elif "under" in outcomes:
                    self.calculate_estimated_ev(data, "under", overround_est, best_bets)

        self.results = sorted(best_bets.values(), key=lambda x: x[7], reverse=True)
        logger.info(f"Found {len(self.results)} +EV bets" if self.results else "No +EV bets found")
        return self.results