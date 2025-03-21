import logging

logger = logging.getLogger(__name__)

class ExpectedValueAnalyzer:
    def __init__(self, bet_lines, min_bookies=4, ev_target=1.5):
        """Initialize the analyzer with bet lines (moneylines or props) and a minimum bookie threshold."""
        self.bet_lines = bet_lines  # Generic name for moneylines or prop bets
        self.min_bookies = min_bookies
        self.results = []  # Store results here
        self.ev_target = ev_target

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
        """Determine the assumed overround based on the median odds tier."""
        if odds <= -300:
            return 1.0412
        elif odds <= -200:
            return 1.0511
        elif odds <= -100:
            return 1.0597
        elif odds <= 150:
            return 1.096
        elif odds <= 300:
            return 1.135
        elif odds <= 500:
            return 1.2291
        elif odds <= 800:
            return 1.3219
        elif odds <= 1200:
            return 1.4125
        elif odds <= 2000:
            return 1.5129
        elif odds <= 3000:
            return 1.6342
        else:
            return None  # Should not occur due to odds > 1100 filter

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

        self.results = []  # Reset results
        logger.debug(f"Grouped {len(game_dict)} games for analysis")
        for game_id, data in game_dict.items():
            team1_bookies = set(bookie for bookie, _ in data['team1_odds'])
            team2_bookies = set(bookie for bookie, _ in data['team2_odds'])
            num_bookies_team1 = len(team1_bookies)
            num_bookies_team2 = len(team2_bookies)
            if num_bookies_team1 < self.min_bookies or num_bookies_team2 < self.min_bookies:
                logger.info(f"Skipping game_ID {game_id}: Only {num_bookies_team1} bookies for {data['teams'][0]} and {num_bookies_team2} for {data['teams'][1]} (min {self.min_bookies} required)")
                continue

            logger.debug(f"Analyzing game_ID {game_id} with {num_bookies_team1} bookies for {data['teams'][0]} and {num_bookies_team2} for {data['teams'][1]}")
            
            # Calculate implied probabilities for each bookie's odds
            imp_probs_team1 = [self.calculate_implied_probability(odds) for _, odds in data['team1_odds']]
            imp_probs_team2 = [self.calculate_implied_probability(odds) for _, odds in data['team2_odds']]
            
            # Average the implied probabilities for each team
            avg_imp_prob_team1 = sum(imp_probs_team1) / len(imp_probs_team1)
            avg_imp_prob_team2 = sum(imp_probs_team2) / len(imp_probs_team2)
            
            # Calculate market overround
            market_overround = avg_imp_prob_team1 + avg_imp_prob_team2
            
            # Calculate fair probabilities
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
                logger.info(f"Found +EV for {data['teams'][0]} in game_ID {game_id}: EV = {best_ev_team1:.2f}")
                for bookie, odds in best_bookies_team1:
                    bookie_imp_prob = self.calculate_implied_probability(odds)
                    self.results.append((
                        data['game_ID'],
                        bookie,
                        data['Matchup_Type'],
                        data['teams'][0],
                        odds,
                        round(best_ev_team1, 2),
                        round(fair_prob_team1, 4),
                        round(bookie_imp_prob, 4),
                        round(market_overround, 4),
                        data['sport_type'],
                        data['event_timestamp'],
                        data['last_updated_timestamp']
                    ))
            
            if best_ev_team2 is not None and best_ev_team2 > self.ev_target:
                logger.info(f"Found +EV for {data['teams'][1]} in game_ID {game_id}: EV = {best_ev_team2:.2f}")
                for bookie, odds in best_bookies_team2:
                    bookie_imp_prob = self.calculate_implied_probability(odds)
                    self.results.append((
                        data['game_ID'],
                        bookie,
                        data['Matchup_Type'],
                        data['teams'][1],
                        odds,
                        round(best_ev_team2, 2),
                        round(fair_prob_team2, 4),
                        round(bookie_imp_prob, 4),
                        round(market_overround, 4),
                        data['sport_type'],
                        data['event_timestamp'],
                        data['last_updated_timestamp']
                    ))
        
        logger.info(f"Moneyline analysis completed. Found {len(self.results)} +EV opportunities")
        return self.results

    def analyze_prop(self):
        """Analyze prop bets to find all +EV bets with max EV, returning a list of tuples."""
        logger.info(f"Number of bet lines loaded: {len(self.bet_lines)}")
        if not self.bet_lines:
            logger.error("No bet lines to analyze. Check data loading.")
            return []

        prop_dict = {}
        
        for line in self.bet_lines:
            game_id, last_updated_timestamp, bookie, prop_type, bet_type, player_name, betting_line, betting_point, sport_type = line
            if bet_type.lower() == "yes":
                key = (game_id, prop_type, player_name)
            elif bet_type.lower() in ["over", "under"]:
                key = (game_id, prop_type, player_name, betting_point)
            else:
                logger.debug(f"Skipping unknown bet_type {bet_type} for prop {line}")
                continue
            
            if key not in prop_dict:
                prop_dict[key] = {
                    'game_ID': game_id,
                    'Prop_Type': prop_type,
                    'Player_Name': player_name,
                    'Betting_Point': betting_point if bet_type.lower() in ["over", "under"] else None,
                    'sport_type': sport_type,
                    'last_updated_timestamp': last_updated_timestamp,
                    'outcomes': {}
                }
            if bet_type.lower() not in prop_dict[key]['outcomes']:
                prop_dict[key]['outcomes'][bet_type.lower()] = []
            prop_dict[key]['outcomes'][bet_type.lower()].append((bookie, betting_line))

        self.results = []
        logger.info(f"Grouped {len(prop_dict)} unique prop bets for analysis")
        
        for key, data in prop_dict.items():
            outcomes = data['outcomes']
            
            if "yes" in outcomes:
                bookies_yes = set(bookie for bookie, _ in outcomes["yes"])
                if len(bookies_yes) < self.min_bookies:
                    logger.debug(f"Skipping prop {key}: Insufficient bookies for 'yes' ({len(bookies_yes)} < {self.min_bookies})")
                    continue

                odds_yes = [odds for _, odds in outcomes["yes"]]
                if any(odds > 1200 for odds in odds_yes):
                    logger.debug(f"Skipping prop {key}: Contains longshot odds > +1000")
                    continue
                    
                imp_probs_yes = [self.calculate_implied_probability(o) for o in odds_yes]
                avg_imp_prob_yes = sorted(imp_probs_yes)[len(imp_probs_yes) // 2]  # Median implied probability
                
                # Calculate median odds manually
                sorted_odds = sorted(odds_yes)
                mid = len(sorted_odds) // 2
                if len(sorted_odds) % 2 == 0:
                    median_odds = (sorted_odds[mid - 1] + sorted_odds[mid]) / 2
                else:
                    median_odds = sorted_odds[mid]
                
                assumed_overround = self.get_assumed_overround(median_odds)
                if assumed_overround is None:
                    logger.warning(f"Invalid median odds {median_odds} for prop {key}, skipping")
                    continue
                fair_prob_yes = avg_imp_prob_yes / assumed_overround

                for bookie, odds in outcomes["yes"]:
                    ev = self.calculate_expected_value(odds, fair_prob_yes)
                    if ev > self.ev_target:
                        bookie_imp_prob = self.calculate_implied_probability(odds)
                        logger.debug(f"Found +EV for 'yes' prop {key} at {bookie}: EV = {ev:.2f}, fair_prob = {fair_prob_yes:.4f}, implied_prob = {bookie_imp_prob:.4f}")
                        self.results.append((
                            data['game_ID'],
                            bookie,
                            data['Prop_Type'],
                            "yes",
                            data['Player_Name'],
                            "N/A",
                            odds,
                            round(ev, 2),
                            round(fair_prob_yes, 4),
                            round(bookie_imp_prob, 4),
                            round(assumed_overround, 4),
                            data['sport_type'],
                            data['last_updated_timestamp']
                        ))
                    
            elif "over" in outcomes and "under" in outcomes:
                bookies_over = set(bookie for bookie, _ in outcomes["over"])
                bookies_under = set(bookie for bookie, _ in outcomes["under"])
                
                if len(bookies_over) >= self.min_bookies and len(bookies_under) >= self.min_bookies:
                    # Full market overround analysis
                    odds_over = [odds for _, odds in outcomes["over"]]
                    odds_under = [odds for _, odds in outcomes["under"]]
                    imp_probs_over = [self.calculate_implied_probability(o) for o in odds_over]
                    imp_probs_under = [self.calculate_implied_probability(o) for o in odds_under]
                    avg_imp_prob_over = sum(imp_probs_over) / len(imp_probs_over)
                    avg_imp_prob_under = sum(imp_probs_under) / len(imp_probs_under)

                    market_overround = avg_imp_prob_over + avg_imp_prob_under
                    if market_overround <= 0:
                        logger.warning(f"Invalid market overround {market_overround} for prop {key}, skipping")
                        continue
                    fair_prob_over = avg_imp_prob_over / market_overround
                    fair_prob_under = avg_imp_prob_under / market_overround

                    for bet_type, outcome_odds in outcomes.items():
                        fair_prob = fair_prob_over if bet_type == "over" else fair_prob_under
                        for bookie, odds in outcome_odds:
                            ev = self.calculate_expected_value(odds, fair_prob)
                            if ev > self.ev_target:
                                bookie_imp_prob = self.calculate_implied_probability(odds)
                                logger.debug(f"Found +EV for '{bet_type}' prop {key} at {bookie}: EV = {ev:.2f}, fair_prob = {fair_prob:.4f}, implied_prob = {bookie_imp_prob:.4f}")
                                self.results.append((
                                    data['game_ID'],
                                    bookie,
                                    data['Prop_Type'],
                                    bet_type,
                                    data['Player_Name'],
                                    data['Betting_Point'],
                                    odds,
                                    round(ev, 2),
                                    round(fair_prob, 4),
                                    round(bookie_imp_prob, 4),
                                    round(market_overround, 4),
                                    data['sport_type'],
                                    data['last_updated_timestamp']
                                ))
                elif len(bookies_over) >= self.min_bookies:
                    # Fallback: analyze "over" with assumed overround
                    odds_over = [odds for _, odds in outcomes["over"]]
                    sorted_odds = sorted(odds_over)
                    mid = len(sorted_odds) // 2
                    median_odds = (sorted_odds[mid - 1] + sorted_odds[mid]) / 2 if len(sorted_odds) % 2 == 0 else sorted_odds[mid]
                    assumed_overround = self.get_assumed_overround(median_odds)
                    if assumed_overround is None:
                        logger.warning(f"Invalid median odds {median_odds} for prop {key}, skipping")
                        continue
                    imp_probs_over = [self.calculate_implied_probability(o) for o in odds_over]
                    fair_prob_over = sum(imp_probs_over) / len(imp_probs_over) / assumed_overround
                    for bookie, odds in outcomes["over"]:
                        ev = self.calculate_expected_value(odds, fair_prob_over)
                        if ev > self.ev_target:
                            bookie_imp_prob = self.calculate_implied_probability(odds)
                            logger.debug(f"Found +EV for 'over' prop {key} at {bookie}: EV = {ev:.2f}, fair_prob = {fair_prob_over:.4f}, implied_prob = {bookie_imp_prob:.4f}")
                            self.results.append((
                                data['game_ID'],
                                bookie,
                                data['Prop_Type'],
                                "over",
                                data['Player_Name'],
                                data['Betting_Point'],
                                odds,
                                round(ev, 2),
                                round(fair_prob_over, 4),
                                round(bookie_imp_prob, 4),
                                round(assumed_overround, 4),
                                data['sport_type'],
                                data['last_updated_timestamp']
                            ))
                elif len(bookies_under) >= self.min_bookies:
                    # Fallback: analyze "under" with assumed overround
                    odds_under = [odds for _, odds in outcomes["under"]]
                    sorted_odds = sorted(odds_under)
                    mid = len(sorted_odds) // 2
                    median_odds = (sorted_odds[mid - 1] + sorted_odds[mid]) / 2 if len(sorted_odds) % 2 == 0 else sorted_odds[mid]
                    assumed_overround = self.get_assumed_overround(median_odds)
                    if assumed_overround is None:
                        logger.warning(f"Invalid median odds {median_odds} for prop {key}, skipping")
                        continue
                    imp_probs_under = [self.calculate_implied_probability(o) for o in odds_under]
                    fair_prob_under = sum(imp_probs_under) / len(imp_probs_under) / assumed_overround
                    for bookie, odds in outcomes["under"]:
                        ev = self.calculate_expected_value(odds, fair_prob_under)
                        if ev > self.ev_target:
                            bookie_imp_prob = self.calculate_implied_probability(odds)
                            logger.debug(f"Found +EV for 'under' prop {key} at {bookie}: EV = {ev:.2f}, fair_prob = {fair_prob_under:.4f}, implied_prob = {bookie_imp_prob:.4f}")
                            self.results.append((
                                data['game_ID'],
                                bookie,
                                data['Prop_Type'],
                                "under",
                                data['Player_Name'],
                                data['Betting_Point'],
                                odds,
                                round(ev, 2),
                                round(fair_prob_under, 4),
                                round(bookie_imp_prob, 4),
                                round(assumed_overround, 4),
                                data['sport_type'],
                                data['last_updated_timestamp']
                            ))
                else:
                    logger.debug(f"Skipping prop {key}: Insufficient bookies for both over and under")
                    continue
            else:
                logger.debug(f"Skipping prop {key}: Only one outcome present - {list(outcomes.keys())}")
                continue

        self.results.sort(key=lambda x: x[7], reverse=True)
        if self.results:
            logger.info(f"Analysis complete. Found {len(self.results)} +EV bets. Highest EV: {self.results[0]}")
        else:
            logger.info("Analysis complete. No +EV bets found.")
        return self.results