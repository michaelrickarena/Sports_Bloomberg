import requests
from dotenv import load_dotenv
import os
from pathlib import Path
import json
import pandas as pd
import logging.config


# Adjust the path to the parent directory
logging_conf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logging.conf')

# Load the logging configuration
logging.config.fileConfig(logging_conf_path)

# Create a logger instance
logger = logging.getLogger('db_logger')

class Odds_API:
    def __init__(self):
        env_path = Path('../../.env')
        load_dotenv(dotenv_path=env_path)

        self.link = os.getenv('ODDS_LINK')
        self.odds_apikey = os.getenv('API_KEY_ODDS_API')

#### START OF API CALLS

    # helper function to make API Call
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


    # get all active sports that Odds API offers
    # Currently not in use
    def active_sports(self):
        """Fetch a list of active sports from the API."""
        data = self._make_request('/v4/sports')
        if data:
            with open('Active_Sports.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)
                logger.info("Data successfully exported to Active_Sports.json")
        else:
            logger.info("Failed to fetch active sports.")

    def get_team_odds(self, sport='americanfootball_nfl'):
        """Get odds for each team in a league."""

        all_team_odds = []
        data = self._make_request(f'/v4/sports/{sport}/odds/', params={
            'regions': 'us',
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american'
        })


        if data:
            for info in data:
                all_team_odds.append(info)
            logger.info("Team odds successfully fetched.")
            return all_team_odds
        else:
            logger.error("Team odds failed to be fetched.")


    # currently not in use
    def get_scores(self, sport='americanfootball_nfl'):
        """Get scores for each team in a league."""
        data = self._make_request(f'/v4/sports/{sport}/scores/', params={'daysFrom': 3})
        if data:
            with open('NFL_Scores.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)
                logger.info("Data successfully exported to NFL_Scores.json")
        else:
            logger.info("Failed to fetch scores.")

    def get_events(self, sport='americanfootball_nfl'):
        """Get events for each sport."""
        data = self._make_request(f'/v4/sports/{sport}/events')
        all_event_ids = []
        all_event_details = []
        try:
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
                logger.info("events successfully fetched.")
                return all_event_ids, all_event_details
                    # return data
            else:
                logger.error("events failed to be fetched. and returned an empty array")
                return []
        except Exception as e:
            logger.error(f"events failed to be fetched. Error: {e}")




# Below done
    def get_props(self, sport='americanfootball_nfl'):
        """Get player props for a specific event."""
        
        event_id_list, all_event_details = self.get_events()

        markets = [
            'player_reception_yds', 'player_field_goals', 'player_pass_interceptions',
            'player_pass_longest_completion', 'player_pass_rush_reception_tds',
            'player_pass_rush_reception_yds', 'player_pass_tds', 'player_pass_yds',
            'player_receptions', 'player_reception_longest', 'player_rush_attempts',
            'player_rush_longest', 'player_rush_reception_tds', 'player_rush_reception_yds',
            'player_rush_yds', 'player_1st_td', 'player_anytime_td', 'player_last_td'
        ]
        markets_joined = ",".join(markets)

        all_props = []

        for event_id in event_id_list:
            try:
                data = self._make_request(f'/v4/sports/{sport}/events/{event_id}/odds/', params={
                    'regions': 'us',
                    'markets': markets_joined,
                    'oddsFormat': 'american'
                })

                if data:
                    # Collect the props data
                    all_props.append(data)
                    logger.info(f"props for {event_id} successfully fetched")
                else:
                    logger.info(f"No data found for event {event_id}.")

            except Exception as e:
                logger.error(f"Failed to fetch props for event {event_id}: {e}")
            
        return all_props

# above done

#### END OF API CALLS





#### START OF API FILTERING

# Below done
    def teams_and_gametime(self):
        """Show away and home teams and game times."""
        games = []
        data = self.get_team_odds()

        for sport in data:
            game_ID = sport['id']
            home_team = sport['home_team']
            away_team = sport['away_team']
            game_time = sport['commence_time']
            game = (game_ID, home_team, away_team, game_time)
            if game not in games:
                games.append(game)

        games_df = pd.DataFrame(games, columns=["Game_ID", "home_team", "away_team", "game_time"])
        return games_df
# above done

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
                                game_spreads.append((
                                    game_ID, bookie, matchup_type, spd_team1, spd_point1, spd_line1,
                                    spd_team2, spd_point2, spd_line2, game_time, last_updated
                                ))
                        elif matchup_type == 'h2h':
                            line_outcomes = market['outcomes']
                            if len(line_outcomes) == 2:
                                h2h_team1 = line_outcomes[0]['name']
                                h2h_line1 = line_outcomes[0]['price']
                                h2h_team2 = line_outcomes[1]['name']
                                h2h_line2 = line_outcomes[1]['price']
                                game_lines.append((
                                    game_ID, bookie, matchup_type, h2h_team1, h2h_line1,
                                    h2h_team2, h2h_line2, game_time, last_updated
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
                                game_totals.append((
                                    game_ID, bookie, matchup_type, home_team, away_team,
                                    over_or_under1, over_under_total1, over_under_line1,
                                    over_or_under2, over_under_total2, over_under_line2,
                                    game_time, last_updated
                                ))
        except Exception as e:
            logger.error(f"Failed to filter ML, Over/under, and spread data. Error: {e}")

        return game_totals, game_spreads, game_lines


# above done

    def prop_bets_filters(self):

        props_data = self.get_props()
        all_prop_bets = []

        try:
            for data in props_data:
                if len(data['bookmakers']) == 0:
                    pass
                else:
                    game_id = data['id']
                    all_props = data['bookmakers']
                    for bookie_type in all_props:
                        bookie = bookie_type['key']
                        for prop in bookie_type['markets']:
                            prop_type = prop['key']
                            last_update = prop['last_update']
                            for betting_lines in prop['outcomes']:
                                name = betting_lines['name']
                                description = betting_lines['description']
                                price = betting_lines['price']
                                try:
                                    point = betting_lines['point']
                                except:
                                    point = 'N/A'

                                all_prop_bets.append((
                                            game_id,
                                            last_update,
                                            bookie,
                                            prop_type,
                                            name,
                                            description,
                                            price,
                                            point
                                ))       
        except Exception as e:
            logger.error(f"Failed to filter prop bets. Error: {e}")

        print(all_prop_bets)
        return all_prop_bets

api = Odds_API()
api.get_props()

#### END OF API FILTERING