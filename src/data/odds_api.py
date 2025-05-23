import requests
import os
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class Odds_API:
    def __init__(self):
        self.link = os.getenv('ODDS_LINK')
        self.odds_apikey = os.getenv('API_KEY_ODDS_API')
        self.all_sports = ['americanfootball_nfl', 'icehockey_nhl', 'basketball_nba', 'baseball_mlb']
        self.active_sports = []  # To store active sports

    #### START OF API CALLS

    # Helper function to make API Call
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Helper function to make API requests."""
        url = f"{self.link}{endpoint}"
        if params is None:
            params = {}
        params['apiKey'] = self.odds_apikey  # Add API key to parameters

        try:
            response = requests.get(url, params=params)  # Use params to manage query parameters

            # Check for 401 Unauthorized
            if response.status_code == 401:
                logger.error("Unauthorized access (401) - breaking the loop.")
                raise Exception("401 Unauthorized")  # Raise a specific exception for 401
            
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error occurred: {err}")
            return {}
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            return {}

    # Get all active sports that Odds API offers but filter based off sports we care about
    def fetch_active_sports(self):
        """Fetch a list of active sports from the API."""
        data = self._make_request('/v4/sports')
        if data:
            # Filter active sports to only include the sports of interest
            self.active_sports = [
                sport['key'] for sport in data 
                if sport.get('active') and sport['key'] in self.all_sports
            ]
            logger.info(f"Active sports: {self.active_sports}")
        else:
            logger.error("Failed to fetch active sports.")

    def get_team_odds(self):
        """Get odds for each team in a league."""
        all_team_odds = []
        for sport in self.active_sports:
            data = self._make_request(f'/v4/sports/{sport}/odds/', params={
                'regions': 'us,us2',
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'american'
            })
            if data:
                all_team_odds.extend(data)  # `data` is already iterable, no need for an inner loop
                logger.info(f"Team odds successfully fetched for {sport}.")
            else:
                logger.error(f"Team odds failed to be fetched for {sport}.")
        return all_team_odds



    def get_scores(self):
        """Get scores for each team in all active sports."""
        all_scores = []
        
        
        for sport in self.active_sports:
            data = self._make_request(f'/v4/sports/{sport}/scores/', params={'daysFrom': 3})
            
            if data:
                for info in data:
                    all_scores.append(info)
                logger.info(f"Successfully fetched scores for {sport}")
            else:
                logger.warning(f"Failed to fetch scores for {sport}")
        
        if all_scores:
            logger.info("Data successfully saved all scores from games")
        else:
            logger.info("No scores were fetched.")
            
        return all_scores


    def get_events(self):
        """Get events for active sports only."""
        # Ensure active sports are up-to-date
        if not self.active_sports:
            self.fetch_active_sports()

        all_event_ids = []
        all_event_details = []

        try:
            for sport in self.active_sports:
                data = self._make_request(f'/v4/sports/{sport}/events')
                if data:
                    for info in data:
                        all_event_ids.append(info['id'])
                        event_id = info['id']
                        sport_name = info['sport_title']
                        game_time = info['commence_time']
                        home_team = info['home_team']
                        away_team = info['away_team']
                        all_event_details.append((
                            event_id,
                            sport_name,
                            game_time,
                            home_team,
                            away_team
                        ))
                    logger.info(f"Events successfully fetched for sport: {sport}.")
                else:
                    logger.warning(f"No events found for sport: {sport}.")
            return all_event_ids, all_event_details
        except Exception as e:
            logger.error(f"Failed to fetch events for active sports. Error: {e}")
            return []



    # Below done
    def get_props(self):
        """Get player props for all active sports."""

        event_id_list, all_event_details = self.get_events()

        # Define market groups by sport_name
        market_groups = {
            'NFL': [
                'player_reception_yds', 'player_field_goals', 'player_pass_interceptions',
                'player_pass_rush_reception_tds', 'player_pass_rush_reception_yds', 
                'player_pass_tds', 'player_pass_yds', 'player_receptions', 'player_reception_longest', 
                'player_rush_longest', 'player_rush_reception_tds', 'player_rush_reception_yds',
                'player_rush_yds', 'player_1st_td', 'player_anytime_td', 'player_defensive_interceptions',
                'player_kicking_points', 'player_pass_attempts', 'player_pass_completions', 'player_pass_longest_completion',
                'player_pass_yds_q1', 'player_pats', 'player_reception_tds', 'player_rush_attempts', 'player_rush_tds',
                'player_sacks', 'player_solo_tackles', 'player_tackles_assists', 'player_last_td'
            ],
            'NBA': [
                'player_points', 'player_rebounds', 'player_assists', 
                'player_threes', 'player_blocks', 'player_steals', 
                'player_turnovers', 'player_points_assists', 
                'player_rebounds_assists', 'player_field_goals', 'player_first_basket',
                'player_double_double', 'player_triple_double'
            ],
            'NHL': [
                'player_points', 'player_power_play_points', 'player_assists', 
                'player_shots_on_goal', 'player_goals', 
                'player_total_saves', 'player_goal_scorer_first', 'player_goal_scorer_anytime'
            ],
            'MLB': [
                'batter_home_runs', 'batter_first_home_run', 'batter_hits', 'batter_total_bases', 
                'batter_runs_scored', 'batter_hits_runs_rbis', 'batter_singles',
                'batter_doubles', 'batter_triples', 'batter_strikeouts', 
                'batter_rbis', 'batter_walks', 'batter_stolen_bases'
            ]
        }

        # Define sport mapping for API call
        sport_mapping = {
            'NFL': 'americanfootball_nfl',
            'NBA': 'basketball_nba',
            'NHL': 'icehockey_nhl',
            'MLB': 'baseball_mlb'
        }

        all_props = []

        for event_id, sport_name, _, _, _ in all_event_details:
            # Map sport_name to the correct sport key for API call
            sport = sport_mapping.get(sport_name)
            if not sport:
                logger.warning(f"Unsupported sport: {sport_name}. Skipping event {event_id}.")
                continue

            # Determine the markets based on sport_name
            markets = market_groups.get(sport_name, [])
            if not markets:
                logger.warning(f"No markets defined for sport: {sport_name}. Skipping event {event_id}.")
                continue

            markets_joined = ",".join(markets)

            try:
                # Fetch props for the event
                data = self._make_request(f'/v4/sports/{sport}/events/{event_id}/odds/', params={
                    'regions': 'us,us2,eu,au,uk',
                    'markets': markets_joined,
                    'oddsFormat': 'american'
                })

                if data:
                    # Collect the props data
                    all_props.append(data)
                    logger.info(f"Props for {event_id} (sport: {sport_name}) successfully fetched.")
                else:
                    logger.info(f"No data found for event {event_id} (sport: {sport_name}).")

            except Exception as e:
                logger.error(f"Failed to fetch props for event {event_id} (sport: {sport_name}): {e}")

        return all_props



# above done

#### END OF API CALLS





#### START OF API FILTERING


# below done
    def bookies_and_odds(self):
        """Show bookies' odds across all upcoming games."""

        data = self.get_team_odds()
        game_lines = []
        game_spreads = []
        game_totals = []

        try:
            for sport in data:
                game_time = sport['commence_time']
                game_ID = sport['id']
                home_team = sport['home_team']
                away_team = sport['away_team']
                sport_type = sport['sport_key']

                for bookmaker in sport['bookmakers']:
                    bookie = bookmaker['title']
                    last_updated = bookmaker['last_update']

                    for market in bookmaker['markets']:
                        matchup_type = market['key']
                        if matchup_type == 'spreads':
                            spread_outcomes = market['outcomes']
                            if len(spread_outcomes) == 2:
                                spd_team1 = spread_outcomes[0]['name']
                                spd_point1 = spread_outcomes[0]['point']
                                spd_line1 = spread_outcomes[0]['price']
                                spd_team2 = spread_outcomes[1]['name']
                                spd_point2 = spread_outcomes[1]['point']
                                spd_line2 = spread_outcomes[1]['price']
                                logger.info(f"game_spreads for {game_ID} successfully fetched")
                                game_spreads.append((
                                    game_ID, bookie, matchup_type, spd_team1, spd_point1, spd_line1,
                                    spd_team2, spd_point2, spd_line2, game_time, last_updated, sport_type
                                ))
                        elif matchup_type == 'h2h':
                            line_outcomes = market['outcomes']
                            if len(line_outcomes) == 2:
                                h2h_team1 = line_outcomes[0]['name']
                                h2h_line1 = line_outcomes[0]['price']
                                h2h_team2 = line_outcomes[1]['name']
                                h2h_line2 = line_outcomes[1]['price']
                                logger.info(f"game_lines for {game_ID} successfully fetched")
                                game_lines.append((
                                    game_ID, bookie, matchup_type, h2h_team1, h2h_line1,
                                    h2h_team2, h2h_line2, game_time, last_updated, sport_type
                                ))
                        elif matchup_type == 'totals':
                            totals_outcomes = market['outcomes']
                            if len(totals_outcomes) == 2:
                                over_or_under1 = totals_outcomes[0]['name']
                                over_under_total1 = totals_outcomes[0]['point']
                                over_under_line1 = totals_outcomes[0]['price']
                                over_or_under2 = totals_outcomes[1]['name']
                                over_under_total2 = totals_outcomes[1]['point']
                                over_under_line2 = totals_outcomes[1]['price']
                                logger.info(f"game_totals for {game_ID} successfully fetched")
                                game_totals.append((
                                    game_ID, bookie, matchup_type, home_team, away_team,
                                    over_or_under1, over_under_total1, over_under_line1,
                                    over_or_under2, over_under_total2, over_under_line2,
                                    game_time, last_updated, sport_type
                                ))
        except Exception as e:
            logger.error(f"Failed to filter ML, Over/under, and spread data. Error: {e}")

        return game_totals, game_spreads, game_lines


# above done

    def prop_bets_filters(self):
        """Collect all prop bets and unique player prop data for database insertion."""
        
        props_data = self.get_props()
        all_prop_bets = []
        unique_player_props = []
        
        try:
            for data in props_data:
                if not data.get('bookmakers'):
                    continue
                    
                game_id = data['id']
                sport_type = data['sport_key']
                
                for bookie_type in data['bookmakers']:
                    bookie = bookie_type['key']
                    for prop in bookie_type['markets']:
                        prop_type = prop['key']
                        last_update = prop.get('last_update', '')
                        
                        for betting_line in prop['outcomes']:
                            name = betting_line.get('name')
                            description = betting_line.get('description')
                            price = betting_line.get('price')
                            point = betting_line.get('point', 'N/A')
                            
                            # Collect all prop bets
                            all_prop_bets.append((
                                game_id,
                                last_update,
                                bookie,
                                prop_type,
                                name,
                                description,
                                price,
                                point,
                                sport_type
                            ))
                            
                            # Collect unique player props
                            # Use description for player name, except for specific markets
                            player_name = name if prop_type in ['first_goal_scorer', 'anytime_goal'] else description
                            
                            # Validate player_name and ensure uniqueness
                            if player_name and player_name not in ['Over', 'Under', 'Yes', 'No'] and (player_name, game_id) not in [(p[0], p[1]) for p in unique_player_props]:
                                unique_player_props.append((
                                    player_name,   # Player name
                                    game_id,       # Game ID
                                    sport_type,    # Sport type
                                    last_update    # Market's last_update timestamp
                                ))
            
            logger.info(f"Collected {len(all_prop_bets)} prop bets and {len(unique_player_props)} unique player props")
            
        except Exception as e:
            logger.error(f"Failed to filter prop bets or player props. Error: {e}")
        
        return all_prop_bets, unique_player_props

    def filter_scores(self):
        scores = self.get_scores()  # Assume this gets your API scores
        all_game_results = []
        try:
            for game in scores:
                game_id = game['id']
                sport_title = game['sport_title']
                game_time = game['commence_time']
                game_status = game['completed']
                last_update = game['last_update']

                # Default values in case 'scores' is None
                team1, score1 = None, None
                team2, score2 = None, None

                # If scores exist, update them
                if game['scores'] is not None:
                    for i, score in enumerate(game['scores']):
                        if i == 0:
                            team1 = score['name']
                            score1 = score['score']
                        elif i == 1:
                            team2 = score['name']
                            score2 = score['score']

                # Append the result to the list
                logger.info(f"game scores for {game_id} successfully fetched")
                all_game_results.append((
                    game_id, sport_title, game_time, 
                    game_status, last_update, 
                    team1, score1, team2, score2))
        except Exception as e:
            logger.error(f"Failed to filter game scores. Error: {e}")

        return all_game_results



# api = Odds_API()