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
    r = requests.get(f'{link}v4/sports/{sport}/odds?regions=us&oddsFormat=american&apiKey={odds_apikey}')
    data = r.json()

    if r.status_code == 200:
        with open('NFL_Data', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to NFL_Data")
    else:
        print(f"Error: {r.status_code}")


# get scores by each team in a leauge
def get_scores(sport):
    r = requests.get(f'{link}v4/sports/{sport}/scores/?apiKey={odds_apikey}&daysFrom=3')
    data = r.json()

    if r.status_code == 200:
        with open('NFL_Scores', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to NFL_Scores")
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
    print(games_df)      
    return games_df

# Shows bookies odds across all upcoming games
def bookies_and_odds(filename):
    with open(filename, 'r') as file:
        data = json.load(file)  # Load JSON data from the file
        game_lines = []
        for sport in data:
            game_time = sport['commence_time']
            game_ID = sport['id']
            for bookmaker in sport['bookmakers']:
                bookie = bookmaker['title']
                last_updated = bookmaker['last_update']
                for market in bookmaker['markets']:
                    outcomes = market['outcomes']
                    if len(outcomes) == 2:
                        team1 = outcomes[0]['name']
                        line1 = outcomes[0]['price']
                        team2 = outcomes[1]['name']
                        line2 = outcomes[1]['price']

                        game_lines.append([game_ID,bookie,team1,line1,team2,line2,game_time,last_updated])
    bookies_df = pd.DataFrame(game_lines, columns=['game_ID','bookie', 'team1', 'line1', 'team2', 'line2', 'game_time','last_updated'])
    print(bookies_df) 
    return bookies_df


# def filter_scores(filename):



#### FILTER DATA START


# teams_and_gametime('NFL_Data')
# bookies_and_odds('NFL_Data')


# get_scores('americanfootball_nfl')