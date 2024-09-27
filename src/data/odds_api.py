import requests
from dotenv import load_dotenv
import os
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

env_path = Path('../../.env')
load_dotenv(dotenv_path=env_path)

link=os.getenv('ODDS_LINK')
odds_apikey = os.getenv('API_KEY_ODDS_API')


#### REQUEST DATA START


#shows list of all sports that can be pulled with API and whether they are active
def active_sports():
    r = requests.get(f'{link}/v4/sports?apiKey={odds_apikey}')
    data = r.json()

    if r.status_code == 200:
        with open('Active_Sports', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to Active_Sports")
    else:
        print(f"Error: {r.status_code}")


# get odds by each team in a leauge
def get_team_odds(sport):
    r = requests.get(f'{link}/v4/sports/{sport}/odds/?apiKey={odds_apikey}&regions=us&markets=h2h,spreads,totals&oddsFormat=american')
    
    data = r.json()

    if r.status_code == 200:
        with open('NFL_Data_v2', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to NFL_Data")
    else:
        print(f"Error: {r.status_code}")


# get scores by each team in a leauge
def get_scores(sport):
    r = requests.get(f'{link}/v4/sports/{sport}/scores/?apiKey={odds_apikey}&daysFrom=3')
    data = r.json()

    if r.status_code == 200:
        with open('NFL_Scores', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to NFL_Scores")
    else:
        print(f"Error: {r.status_code}")

def get_events(sport):
    r = requests.get(f'{link}/v4/sports/{sport}/events?apiKey={odds_apikey}')
    data = r.json()

    if r.status_code == 200:
        with open('NFL_events', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to NFL_events")
    else:
        print(f"Error: {r.status_code}")



def get_props(sport, event_id):
    
    
    markets = [
        'player_reception_yds',
        'player_field_goals',
        'player_pass_interceptions',
        'player_pass_longest_completion',
       'player_pass_rush_reception_tds',
        'player_pass_rush_reception_yds',
        'player_pass_tds',
        'player_pass_yds',
        'player_receptions',
        'player_reception_longest',
        'player_reception_yds',
        'player_rush_attempts',
        'player_rush_longest',
        'player_rush_reception_tds',
        'player_rush_reception_yds',
        'player_rush_yds',
        'player_1st_td',
        'player_anytime_td',
        'player_last_td',
        ]
    markets_joined = ",".join(markets)
    r = requests.get(f'{link}/v4/sports/{sport}/events/{event_id}/odds?apiKey={odds_apikey}&regions=us&markets={markets_joined}&oddsFormat=american')
    
    data = r.json()

    if r.status_code == 200:
        with open('NFL_props', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to NFL_Props")
    else:
        print(f"Error: {r.status_code}")


#### REQUEST DATA END










#### FILTER DATA START

# shows away and home teams + game times
def teams_and_gametime(filename):
    games = []
    with open(filename, 'r') as file:
        data = json.load(file)  # Load JSON data from the file
        for sport in data:
            game_ID = sport['id']
            home_team = sport['home_team']
            away_team = sport['away_team']
            game_time = sport['commence_time']
            game=(game_ID,home_team,away_team,game_time)
            if game not in games:
                games.append(game)

    games_df = pd.DataFrame(games, columns=["Game_ID","home_team", "away_team", "game_time"])     
    return games_df

# Shows bookies odds across all upcoming games for over under, moneyline and spreads
def bookies_and_odds(filename):
    with open(filename, 'r') as file:
        data = json.load(file)  # Load JSON data from the file
        #Set an empty list to populate details of moneyline matchups
        game_lines = []
        #Set an empty list to populate details of spread matchups
        game_spreads = []
        #Set an empty list to populate details of over/unders
        game_totals = []
        #begin filtering JSON
        for sport in data:
            # time and date of game
            game_time = sport['commence_time']
            # Unique ID of Game
            game_ID = sport['id']
            # Home Team
            home_team = sport['home_team']
            # Away Team
            away_team = sport['away_team']
            for bookmaker in sport['bookmakers']:
                # Bookie's name
                bookie = bookmaker['title']
                # Last time the spread was updated by the bookie
                last_updated = bookmaker['last_update']
                for market in bookmaker['markets']:
                    #Either Head to Head, Spread or totals
                    matchup_type = market['key']
                    #if matchup type is a spread, then look for the spread details
                    if matchup_type == 'spreads':
                        spread_outcomes = market['outcomes']
                        if len(spread_outcomes) == 2:
                            # team 1 name of the spread
                            spd_team1 = spread_outcomes[0]['name']
                            # spread for team 1
                            spd_point1 = spread_outcomes[0]['point']
                            # line for team 1
                            spd_line1 = spread_outcomes[0]['price']
                            # team 2 name of the spread
                            spd_team2 = spread_outcomes[1]['name']
                            # spread for team 2
                            spd_point2 = spread_outcomes[1]['point']
                            # line for team 1
                            spd_line2 = spread_outcomes[1]['price']
                            # append all variables to a list
                            game_spreads.append([
                                game_ID,
                                bookie,
                                matchup_type,
                                spd_team1,
                                spd_point1,
                                spd_line1,
                                spd_team2,
                                spd_point2,
                                spd_line2,
                                game_time,
                                last_updated
                                ])
                    # if matchup is money line
                    if matchup_type == 'h2h':
                        line_outcomes = market['outcomes']
                        if len(line_outcomes) == 2:
                            # team 1 name of money line
                            h2h_team1 = line_outcomes[0]['name']
                            # Line for team 1 of money line
                            h2h_line1 = line_outcomes[0]['price']
                            # team 2 name of money line
                            h2h_team2 = line_outcomes[1]['name']
                            # Line for team 2 of money line
                            h2h_line2 = line_outcomes[1]['price']
                            # append all money line details to list
                            game_lines.append([
                                game_ID,
                                bookie,
                                matchup_type,
                                h2h_team1,
                                h2h_line1,
                                h2h_team2,
                                h2h_line2,
                                game_time,
                                last_updated
                                ])
                    if matchup_type == 'totals':
                        totals_outcomes = market['outcomes']
                        if len(totals_outcomes) == 2:
                            # either over or under
                            over_or_under1 = totals_outcomes[0]['name']
                            # over / under amount of points
                            over_under_total1 = totals_outcomes[0]['point']
                            # line for either over or under
                            over_under_line1 = totals_outcomes[0]['price']
                            # either over or under
                            over_or_under2 = totals_outcomes[1]['name']
                            # over / under amount of points
                            over_under_total2 = totals_outcomes[1]['point']
                            # line for either over or under
                            over_under_line2 = totals_outcomes[1]['price']
                            # append all variables to a list
                            game_totals.append([
                                game_ID,
                                bookie,
                                matchup_type,
                                home_team,
                                away_team,
                                over_or_under1,
                                over_under_total1,
                                over_under_line1,
                                over_or_under2,
                                over_under_total2,
                                over_under_line2,
                                game_time,
                                last_updated
                                ])



    # turn list of all spread details to dataframe
    bookies_df_spreads = pd.DataFrame(game_spreads, columns=[
        'game_ID',
        'bookie',
        'matchup_type', 
        'Home_Team',
        'Spread1', 
        'line1', 
        'Away_Team', 
        'Spread2',
        'line2', 
        'game_time',
        'last_updated'
        ])

    # turn list of all money line details to dataframe
    bookies_df_ml = pd.DataFrame(game_lines, columns=[
        'game_ID',
        'bookie',
        'matchup_type', 
        'Home_Team', 
        'line1', 
        'Away_Team', 
        'line2', 
        'game_time',
        'last_updated'
        ])

    # turn list of all over/under details to dataframe
    bookies_df_totals = pd.DataFrame(game_totals, columns=[
        'game_ID',
        'bookie',
        'matchup_type', 
        'Home_Team',
        'Away_Team',
        'over_or_under1', 
        'over_under_total1', 
        'over_under_line1', 
        'over_or_under2',
        'over_under_total2',
        'over_under_line2',
        'game_time',
        'last_updated'
        ])


    bookies_df_spreads.to_csv('spreads.csv', index=False)
    bookies_df_ml.to_csv('moneyline.csv', index=False)
    bookies_df_totals.to_csv('over_under.csv', index=False)

    return bookies_df_spreads, bookies_df_ml, bookies_df_totals



def prop_bets_filters(filename):
    with open(filename, 'r') as file:
        data = json.load(file)  # Load JSON data from the file


        game_id = data['id']

        all_props = data['bookmakers']

        bookie = bookie[0]['key']
        
        markets = bookie[0]['markets']
        print(markets)











# def filter_scores(filename):



#### FILTER DATA START

# teams_and_gametime('NFL_Data')
# bookies_and_odds('NFL_Data_v2')

prop_bets_filters('NFL_props')
# get_team_odds('americanfootball_nfl')
# get_scores('americanfootball_nfl')
# get_events('americanfootball_nfl')
# get_props('americanfootball_nfl', 'b08196b0745d9e2e0bebfe8627fc5a1f')