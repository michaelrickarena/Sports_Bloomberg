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
        all_scores = []
        
        if data:
            for info in data:
                all_scores.append(info)
            return all_scores
            logger.info("Data successfully saved all scores from games")
        else:
            logger.info("Failed to fetch scores.")
            return []

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
            'player_pass_rush_reception_tds', 'player_pass_rush_reception_yds', 
            'player_pass_tds', 'player_pass_yds', 'player_receptions', 'player_reception_longest', 
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
    # def teams_and_gametime(self):
    #     """Show away and home teams and game times."""
    #     games = []
    #     data = self.get_team_odds()

    #     for sport in data:
    #         game_ID = sport['id']
    #         home_team = sport['home_team']
    #         away_team = sport['away_team']
    #         game_time = sport['commence_time']
    #         game = (game_ID, home_team, away_team, game_time)
    #         if game not in games:
    #             games.append(game)

    #     games_df = pd.DataFrame(games, columns=["Game_ID", "home_team", "away_team", "game_time"])
    #     return games_df
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
                                logger.info(f"game_spreads for {game_ID} successfully fetched")
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
                                logger.info(f"game_lines for {game_ID} successfully fetched")
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
                                logger.info(f"game_totals for {game_ID} successfully fetched")
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
        return all_prop_bets

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