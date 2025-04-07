import logging

logger = logging.getLogger(__name__)

class ExpectedValueAnalyzer:
    def __init__(self, bet_lines, min_bookies=3, ev_target=5):
        """Initialize the analyzer with bet lines (moneylines or props) and a minimum bookie threshold."""
        self.bet_lines = bet_lines
        self.min_bookies = min_bookies
        self.results = []
        self.ev_target = ev_target
        self.inflate_prop = { 'player_goal_scorer_anytime', 'batter_home_runs', 'player_goal_scorer_first'}
        self.inflate_rate = 0.05
        self.multi_outcome_props = {
            'player_1st_td', 'player_last_td', 'player_first_basket', 'player_first_team_basket',
            'player_goal_scorer_first', 'player_goal_scorer_last', 'batter_first_home_run'
        }
        # Initialize dictionary to store overrounds by odds range
        self.overround_by_range = {
            (-float('inf'), -300): [],
            (-300, -200): [],
            (-200, -100): [],
            (-100, 150): [],
            (150, 250): [],
            (250, 350): [],
            (350, 500): [],
            (500, 650): [],
            (650, 800): [],
            (800, 1200): [],
            (1200, 2000): [],
            (2000, 3000): [],
            (3000, float('inf')): []
        }

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

    def get_assumed_overround(self, odds):
        """Determine the static assumed overround based on the median odds tier."""
        if odds <= -300:
            return 1.0312
        elif odds <= -200:
            return 1.0411
        elif odds <= -100:
            return 1.0497
        elif odds <= 150:
            return 1.0622
        elif odds <= 300:
            return 1.0997
        elif odds <= 500:
            return 1.1945
        elif odds <= 800:
            return 1.3997
        elif odds <= 1200:
            return 1.4989
        elif odds <= 2000:
            return 1.625
        elif odds <= 3000:
            return 1.775
        elif odds <= 5000:
            return 1.997
        else:
            return 3

    def get_odds_range(self, odds):
        """Determine the odds range for a given odds value."""
        if odds <= -300:
            return (-float('inf'), -300)
        elif odds <= -200:
            return (-300, -200)
        elif odds <= -100:
            return (-200, -100)
        elif odds <= 150:
            return (-100, 150)
        elif odds <= 250:
            return (150, 250)
        elif odds <= 350:
            return (250, 350)
        elif odds <= 500:
            return (350, 500)
        elif odds <= 650:
            return (500, 650)
        elif odds <= 800:
            return (650, 800)
        elif odds <= 1200:
            return (800, 1200)
        elif odds <= 2000:
            return (1200, 2000)
        elif odds <= 3000:
            return (2000, 3000)
        else:
            return (3000, float('inf'))

    def get_median_assumed_overround(self, median_odds, prop_type):
        """Get the median assumed overround for the given median odds, inflating for specific props if necessary."""
        range_key = self.get_odds_range(median_odds)
        logger.debug(f"Median odds: {median_odds}, Range key: {range_key}")
        overrounds = self.overround_by_range.get(range_key, [])
        if overrounds:
            sorted_overrounds = sorted(overrounds)
            n = len(sorted_overrounds)
            mid = n // 2
            overround = (sorted_overrounds[mid - 1] + sorted_overrounds[mid]) / 2 if n % 2 == 0 else sorted_overrounds[mid]  # Fixed typo: sorted_odds -> sorted_overrounds
        else:
            overround = self.get_assumed_overround(median_odds)
        if overround is not None and prop_type in self.inflate_prop:
            overround *= (1 + self.inflate_rate)
        return overround

    def analyze_ml(self):
        """Analyze moneyline bets to find all +EV bets with max EV, returning a list of tuples."""
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
            num_bookies_team1 = len(team1_bookies)
            num_bookies_team2 = len(team2_bookies)
            if num_bookies_team1 < self.min_bookies or num_bookies_team2 < self.min_bookies:
                logger.info(f"Skipping game_ID {game_id}: Only {num_bookies_team1} bookies for {data['teams'][0]} and {num_bookies_team2} for {data['teams'][1]}")
                continue

            imp_probs_team1 = [self.calculate_implied_probability(odds) for _, odds in data['team1_odds']]
            imp_probs_team2 = [self.calculate_implied_probability(odds) for _, odds in data['team2_odds']]
            avg_imp_prob_team1 = sum(imp_probs_team1) / len(imp_probs_team1)
            avg_imp_prob_team2 = sum(imp_probs_team2) / len(imp_probs_team2)
            market_overround = avg_imp_prob_team1 + avg_imp_prob_team2
            fair_prob_team1 = avg_imp_prob_team1 / market_overround if market_overround > 0 else 0
            fair_prob_team2 = avg_imp_prob_team2 / market_overround if market_overround > 0 else 0

            best_ev_team1 = None
            best_bookies_team1 = []
            for bookie, odds in data['team1_odds']:
                ev = self.calculate_expected_value(odds, fair_prob_team1)
                if best_ev_team1 is None or ev > best_ev_team1:
                    best_ev_team1 = ev
                    best_bookies_team1 = [(bookie, odds)]
                elif ev == best_ev_team1:
                    best_bookies_team1.append((bookie, odds))

            best_ev_team2 = None
            best_bookies_team2 = []
            for bookie, odds in data['team2_odds']:
                ev = self.calculate_expected_value(odds, fair_prob_team2)
                if best_ev_team2 is None or ev > best_ev_team2:
                    best_ev_team2 = ev
                    best_bookies_team2 = [(bookie, odds)]
                elif ev == best_ev_team2:
                    best_bookies_team2.append((bookie, odds))

            if best_ev_team1 is not None and best_ev_team1 > self.ev_target:
                for bookie, odds in best_bookies_team1:
                    bookie_imp_prob = self.calculate_implied_probability(odds)
                    self.results.append((
                        data['game_ID'], bookie, data['Matchup_Type'], data['teams'][0], odds,
                        round(best_ev_team1, 2), round(fair_prob_team1, 4), round(bookie_imp_prob, 4),
                        round(market_overround, 4), data['sport_type'], data['event_timestamp'],
                        data['last_updated_timestamp']
                    ))

            if best_ev_team2 is not None and best_ev_team2 > self.ev_target:
                for bookie, odds in best_bookies_team2:
                    bookie_imp_prob = self.calculate_implied_probability(odds)
                    self.results.append((
                        data['game_ID'], bookie, data['Matchup_Type'], data['teams'][1], odds,
                        round(best_ev_team2, 2), round(fair_prob_team2, 4), round(bookie_imp_prob, 4),
                        round(market_overround, 4), data['sport_type'], data['event_timestamp'],
                        data['last_updated_timestamp']
                    ))

        logger.info(f"Moneyline analysis completed. Found {len(self.results)} +EV opportunities")
        return self.results

    def analyze_prop(self):
            """Analyze prop bets to find all +EV bets with max EV, returning a list of tuples."""
            logger.info(f"Number of bet lines loaded: {len(self.bet_lines)}")
            if not self.bet_lines:
                logger.error("No bet lines to analyze.")
                return []

            multi_outcome_dict = {}
            single_outcome_dict = {}

            # Group prop bets (unchanged)
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

            self.results = []
            logger.info(f"Grouped {len(multi_outcome_dict)} multi-outcome props and {len(single_outcome_dict)} single-outcome props")

            # Analyze multi-outcome props
            for game_key, game_data in multi_outcome_dict.items():
                players = game_data['players']
                all_bookies = set()
                for odds_list in players.values():
                    all_bookies.update(bookie for bookie, _ in odds_list)
                if len(all_bookies) < self.min_bookies:
                    logger.debug(f"Skipping {game_key}: Only {len(all_bookies)} bookies")
                    continue

                total_imp_prob = 0
                player_avg_probs = {}
                for player_name, odds_list in players.items():
                    odds = [o for _, o in odds_list if o is not None]
                    if not odds:
                        continue
                    imp_probs = [self.calculate_implied_probability(o) for o in odds]
                    avg_imp_prob = sum(imp_probs) / len(imp_probs)
                    player_avg_probs[player_name] = (avg_imp_prob, odds_list)
                    total_imp_prob += avg_imp_prob

                market_overround = total_imp_prob
                if game_data['Prop_Type'] in self.inflate_prop:
                    market_overround *= (1 + self.inflate_rate)
                if market_overround <= 0:
                    logger.warning(f"Invalid market overround {market_overround} for {game_key}")
                    continue

                for player_name, (avg_imp_prob, odds_list) in player_avg_probs.items():
                    bookies = set(bookie for bookie, _ in odds_list)
                    if len(bookies) < self.min_bookies:
                        continue
                    fair_prob = avg_imp_prob / market_overround
                    for bookie, odds in odds_list:
                        if odds is None:
                            continue
                        ev = self.calculate_expected_value(odds, fair_prob)
                        if ev > self.ev_target:
                            if odds > 2000:  # Cap at +2000
                                continue
                            bookie_imp_prob = self.calculate_implied_probability(odds)
                            self.results.append((
                                game_data['game_ID'], bookie, game_data['Prop_Type'], "yes",
                                player_name, "N/A", odds, round(ev, 2), round(fair_prob, 4),
                                round(bookie_imp_prob, 4), round(market_overround, 4),
                                game_data['sport_type'], game_data['last_updated_timestamp'],
                                len(bookies)  # Appended num_bookies
                            ))

            # Pass 1: Collect overrounds for single-outcome props
            for key, data in single_outcome_dict.items():
                outcomes = data['outcomes']
                if "yes" in outcomes or "no" in outcomes:
                    bookies_yes = set(bookie for bookie, _ in outcomes.get("yes", []))
                    bookies_no = set(bookie for bookie, _ in outcomes.get("no", []))
                    odds_yes = [odds for _, odds in outcomes.get("yes", []) if odds is not None]
                    odds_no = [odds for _, odds in outcomes.get("no", []) if odds is not None]
                    imp_probs_yes = [self.calculate_implied_probability(o) for o in odds_yes] if odds_yes else []
                    imp_probs_no = [self.calculate_implied_probability(o) for o in odds_no] if odds_no else []
                    avg_imp_prob_yes = sum(imp_probs_yes) / len(imp_probs_yes) if imp_probs_yes else 0
                    avg_imp_prob_no = sum(imp_probs_no) / len(imp_probs_no) if imp_probs_no else 0

                    if ("yes" in outcomes and "no" in outcomes and
                        len(bookies_yes) >= self.min_bookies and len(bookies_no) >= self.min_bookies):
                        market_overround = avg_imp_prob_yes + avg_imp_prob_no
                        if data['Prop_Type'] in self.inflate_prop:
                            market_overround *= (1 + self.inflate_rate)
                        if market_overround > 0:
                            all_odds = odds_yes + odds_no
                            if all_odds:
                                sorted_odds = sorted(all_odds)
                                mid = len(sorted_odds) // 2
                                median_odds = (sorted_odds[mid - 1] + sorted_odds[mid]) / 2 if len(sorted_odds) % 2 == 0 else sorted_odds[mid]
                                range_key = self.get_odds_range(median_odds)
                                self.overround_by_range[range_key].append(market_overround)

                elif "over" in outcomes or "under" in outcomes:
                    bookies_over = set(bookie for bookie, _ in outcomes.get("over", []))
                    bookies_under = set(bookie for bookie, _ in outcomes.get("under", []))
                    odds_over = [odds for _, odds in outcomes.get("over", []) if odds is not None]
                    odds_under = [odds for _, odds in outcomes.get("under", []) if odds is not None]
                    imp_probs_over = [self.calculate_implied_probability(o) for o in odds_over] if odds_over else []
                    imp_probs_under = [self.calculate_implied_probability(o) for o in odds_under] if odds_under else []
                    avg_imp_prob_over = sum(imp_probs_over) / len(imp_probs_over) if imp_probs_over else 0
                    avg_imp_prob_under = sum(imp_probs_under) / len(imp_probs_under) if imp_probs_under else 0

                    if ("over" in outcomes and "under" in outcomes and
                        len(bookies_over) >= self.min_bookies and len(bookies_under) >= self.min_bookies):
                        market_overround = avg_imp_prob_over + avg_imp_prob_under
                        if data['Prop_Type'] in self.inflate_prop:
                            market_overround *= (1 + self.inflate_rate)
                        if market_overround > 0:
                            all_odds = odds_over + odds_under
                            if all_odds:
                                sorted_odds = sorted(all_odds)
                                mid = len(sorted_odds) // 2
                                median_odds = (sorted_odds[mid - 1] + sorted_odds[mid]) / 2 if len(sorted_odds) % 2 == 0 else sorted_odds[mid]
                                range_key = self.get_odds_range(median_odds)
                                self.overround_by_range[range_key].append(market_overround)

            # Pass 2: Analyze single-outcome props
            for key, data in single_outcome_dict.items():
                outcomes = data['outcomes']
                if "yes" in outcomes or "no" in outcomes:
                    bookies_yes = set(bookie for bookie, _ in outcomes.get("yes", []))
                    bookies_no = set(bookie for bookie, _ in outcomes.get("no", []))
                    odds_yes = [odds for _, odds in outcomes.get("yes", []) if odds is not None]
                    odds_no = [odds for _, odds in outcomes.get("no", []) if odds is not None]
                    imp_probs_yes = [self.calculate_implied_probability(o) for o in odds_yes] if odds_yes else []
                    imp_probs_no = [self.calculate_implied_probability(o) for o in odds_no] if odds_no else []
                    avg_imp_prob_yes = sum(imp_probs_yes) / len(imp_probs_yes) if imp_probs_yes else 0
                    avg_imp_prob_no = sum(imp_probs_no) / len(imp_probs_no) if imp_probs_no else 0

                    both_sides_sufficient = ("yes" in outcomes and "no" in outcomes and
                                            len(bookies_yes) >= self.min_bookies and len(bookies_no) >= self.min_bookies)

                    if both_sides_sufficient:
                        market_overround = avg_imp_prob_yes + avg_imp_prob_no
                        if data['Prop_Type'] in self.inflate_prop:
                            market_overround *= (1 + self.inflate_rate)
                        if market_overround <= 0:
                            logger.warning(f"Invalid market overround {market_overround} for {key}")
                            continue
                        fair_prob_yes = avg_imp_prob_yes / market_overround
                        fair_prob_no = avg_imp_prob_no / market_overround

                        for bookie, odds in outcomes.get("yes", []):
                            if odds is None:
                                continue
                            ev = self.calculate_expected_value(odds, fair_prob_yes)
                            if ev > self.ev_target:
                                if odds > 2000:  # Cap at +2000
                                    continue
                                bookie_imp_prob = self.calculate_implied_probability(odds)
                                self.results.append((
                                    data['game_ID'], bookie, data['Prop_Type'], "yes",
                                    data['Player_Name'], "N/A", odds, round(ev, 2),
                                    round(fair_prob_yes, 4), round(bookie_imp_prob, 4),
                                    round(market_overround, 4), data['sport_type'],
                                    data['last_updated_timestamp'],
                                    len(bookies_yes)  # Appended num_bookies
                                ))

                        for bookie, odds in outcomes.get("no", []):
                            if odds is None:
                                continue
                            ev = self.calculate_expected_value(odds, fair_prob_no)
                            if ev > self.ev_target:
                                if odds > 2000:  # Cap at +2000
                                    continue
                                bookie_imp_prob = self.calculate_implied_probability(odds)
                                self.results.append((
                                    data['game_ID'], bookie, data['Prop_Type'], "no",
                                    data['Player_Name'], "N/A", odds, round(ev, 2),
                                    round(fair_prob_no, 4), round(bookie_imp_prob, 4),
                                    round(market_overround, 4), data['sport_type'],
                                    data['last_updated_timestamp'],
                                    len(bookies_no)  # Appended num_bookies
                                ))
                    else:
                        if len(bookies_yes) >= self.min_bookies:
                            sorted_odds_yes = sorted(odds_yes)
                            mid = len(sorted_odds_yes) // 2
                            median_odds_yes = (sorted_odds_yes[mid - 1] + sorted_odds_yes[mid]) / 2 if len(sorted_odds_yes) % 2 == 0 else sorted_odds_yes[mid]
                            assumed_overround_yes = self.get_median_assumed_overround(median_odds_yes, data['Prop_Type'])
                            if assumed_overround_yes is None:
                                logger.warning(f"Invalid median odds {median_odds_yes} for {key}")
                                continue
                            fair_prob_yes = avg_imp_prob_yes / assumed_overround_yes
                            for bookie, odds in outcomes["yes"]:
                                if odds is None:
                                    continue
                                ev = self.calculate_expected_value(odds, fair_prob_yes)
                                if ev > self.ev_target:
                                    if odds > 2000:  # Cap at +2000
                                        continue
                                    bookie_imp_prob = self.calculate_implied_probability(odds)
                                    self.results.append((
                                        data['game_ID'], bookie, data['Prop_Type'], "yes",
                                        data['Player_Name'], "N/A", odds, round(ev, 2),
                                        round(fair_prob_yes, 4), round(bookie_imp_prob, 4),
                                        round(assumed_overround_yes, 4), data['sport_type'],
                                        data['last_updated_timestamp'],
                                        len(bookies_yes)  # Appended num_bookies
                                    ))

                        if len(bookies_no) >= self.min_bookies:
                            sorted_odds_no = sorted(odds_no)
                            mid = len(sorted_odds_no) // 2
                            median_odds_no = (sorted_odds_no[mid - 1] + sorted_odds_no[mid]) / 2 if len(sorted_odds_no) % 2 == 0 else sorted_odds_no[mid]
                            assumed_overround_no = self.get_median_assumed_overround(median_odds_no, data['Prop_Type'])
                            if assumed_overround_no is None:
                                logger.warning(f"Invalid median odds {median_odds_no} for {key}")
                                continue
                            fair_prob_no = avg_imp_prob_no / assumed_overround_no
                            for bookie, odds in outcomes["no"]:
                                if odds is None:
                                    continue
                                ev = self.calculate_expected_value(odds, fair_prob_no)
                                if ev > self.ev_target:
                                    if odds > 2000:  # Cap at +2000
                                        continue
                                    bookie_imp_prob = self.calculate_implied_probability(odds)
                                    self.results.append((
                                        data['game_ID'], bookie, data['Prop_Type'], "no",
                                        data['Player_Name'], "N/A", odds, round(ev, 2),
                                        round(fair_prob_no, 4), round(bookie_imp_prob, 4),
                                        round(assumed_overround_no, 4), data['sport_type'],
                                        data['last_updated_timestamp'],
                                        len(bookies_no)  # Appended num_bookies
                                    ))

                elif "over" in outcomes or "under" in outcomes:
                    bookies_over = set(bookie for bookie, _ in outcomes.get("over", []))
                    bookies_under = set(bookie for bookie, _ in outcomes.get("under", []))
                    odds_over = [odds for _, odds in outcomes.get("over", []) if odds is not None]
                    odds_under = [odds for _, odds in outcomes.get("under", []) if odds is not None]
                    imp_probs_over = [self.calculate_implied_probability(o) for o in odds_over] if odds_over else []
                    imp_probs_under = [self.calculate_implied_probability(o) for o in odds_under] if odds_under else []
                    avg_imp_prob_over = sum(imp_probs_over) / len(imp_probs_over) if imp_probs_over else 0
                    avg_imp_prob_under = sum(imp_probs_under) / len(imp_probs_under) if imp_probs_under else 0

                    both_sides_sufficient = ("over" in outcomes and "under" in outcomes and
                                            len(bookies_over) >= self.min_bookies and len(bookies_under) >= self.min_bookies)

                    if both_sides_sufficient:
                        market_overround = avg_imp_prob_over + avg_imp_prob_under
                        if data['Prop_Type'] in self.inflate_prop:
                            market_overround *= (1 + self.inflate_rate)
                        if market_overround <= 0:
                            logger.warning(f"Invalid market overround {market_overround} for {key}")
                            continue
                        fair_prob_over = avg_imp_prob_over / market_overround
                        fair_prob_under = avg_imp_prob_under / market_overround

                        for bookie, odds in outcomes.get("over", []):
                            if odds is None:
                                continue
                            ev = self.calculate_expected_value(odds, fair_prob_over)
                            if ev > self.ev_target:
                                if odds > 2000:  # Cap at +2000
                                    continue
                                bookie_imp_prob = self.calculate_implied_probability(odds)
                                self.results.append((
                                    data['game_ID'], bookie, data['Prop_Type'], "over",
                                    data['Player_Name'], data['Betting_Point'], odds,
                                    round(ev, 2), round(fair_prob_over, 4), round(bookie_imp_prob, 4),
                                    round(market_overround, 4), data['sport_type'],
                                    data['last_updated_timestamp'],
                                    len(bookies_over)  # Appended num_bookies
                                ))

                        for bookie, odds in outcomes.get("under", []):
                            if odds is None:
                                continue
                            ev = self.calculate_expected_value(odds, fair_prob_under)
                            if ev > self.ev_target:
                                if odds > 2000:  # Cap at +2000
                                    continue
                                bookie_imp_prob = self.calculate_implied_probability(odds)
                                self.results.append((
                                    data['game_ID'], bookie, data['Prop_Type'], "under",
                                    data['Player_Name'], data['Betting_Point'], odds,
                                    round(ev, 2), round(fair_prob_under, 4), round(bookie_imp_prob, 4),
                                    round(market_overround, 4), data['sport_type'],
                                    data['last_updated_timestamp'],
                                    len(bookies_under)  # Appended num_bookies
                                ))
                    else:
                        if len(bookies_over) >= self.min_bookies:
                            sorted_odds_over = sorted(odds_over)
                            mid = len(sorted_odds_over) // 2
                            median_odds_over = (sorted_odds_over[mid - 1] + sorted_odds_over[mid]) / 2 if len(sorted_odds_over) % 2 == 0 else sorted_odds_over[mid]
                            assumed_overround_over = self.get_median_assumed_overround(median_odds_over, data['Prop_Type'])
                            if assumed_overround_over is None:
                                logger.warning(f"Invalid median odds {median_odds_over} for {key}")
                                continue
                            fair_prob_over = avg_imp_prob_over / assumed_overround_over
                            for bookie, odds in outcomes["over"]:
                                if odds is None:
                                    continue
                                ev = self.calculate_expected_value(odds, fair_prob_over)
                                if ev > self.ev_target:
                                    if odds > 2000:  # Cap at +2000
                                        continue
                                    bookie_imp_prob = self.calculate_implied_probability(odds)
                                    self.results.append((
                                        data['game_ID'], bookie, data['Prop_Type'], "over",
                                        data['Player_Name'], data['Betting_Point'], odds,
                                        round(ev, 2), round(fair_prob_over, 4), round(bookie_imp_prob, 4),
                                        round(assumed_overround_over, 4), data['sport_type'],
                                        data['last_updated_timestamp'],
                                        len(bookies_over)  # Appended num_bookies
                                    ))

                        if len(bookies_under) >= self.min_bookies:
                            sorted_odds_under = sorted(odds_under)
                            mid = len(sorted_odds_under) // 2
                            median_odds_under = (sorted_odds_under[mid - 1] + sorted_odds_under[mid]) / 2 if len(sorted_odds_under) % 2 == 0 else sorted_odds_under[mid]
                            assumed_overround_under = self.get_median_assumed_overround(median_odds_under, data['Prop_Type'])
                            if assumed_overround_under is None:
                                logger.warning(f"Invalid median odds {median_odds_under} for {key}")
                                continue
                            fair_prob_under = avg_imp_prob_under / assumed_overround_under
                            for bookie, odds in outcomes["under"]:
                                if odds is None:
                                    continue
                                ev = self.calculate_expected_value(odds, fair_prob_under)
                                if ev > self.ev_target:
                                    if odds > 2000:  # Cap at +2000
                                        continue
                                    bookie_imp_prob = self.calculate_implied_probability(odds)
                                    self.results.append((
                                        data['game_ID'], bookie, data['Prop_Type'], "under",
                                        data['Player_Name'], data['Betting_Point'], odds,
                                        round(ev, 2), round(fair_prob_under, 4), round(bookie_imp_prob, 4),
                                        round(assumed_overround_under, 4), data['sport_type'],
                                        data['last_updated_timestamp'],
                                        len(bookies_under)  # Appended num_bookies
                                    ))

            self.results.sort(key=lambda x: x[7], reverse=True)
            logger.info(f"Found {len(self.results)} +EV bets" if self.results else "No +EV bets found")
            return self.results