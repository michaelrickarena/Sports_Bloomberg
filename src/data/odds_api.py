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


def active_sports():
    r = requests.get(f'{link}/v4/sports?apiKey={odds_apikey}')
    data = r.json()

    if r.status_code == 200:
        with open('Active_Sports', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to Active_Sports")
    else:
        print(f"Error: {r.status_code}")


def specific_sport_odds(sport):
    r = requests.get(f'{link}v4/sports/{sport}/odds?regions=us&oddsFormat=american&apiKey={odds_apikey}')
    data = r.json()

    if r.status_code == 200:
        with open('NFL_Data', 'w') as json_file:
            json.dump(data, json_file, indent=4)  # `indent=4` makes the output readable
            print(f"Data successfully exported to NFL_Data")
    else:
        print(f"Error: {r.status_code}")

def teams_and_gametime(filename):
    games = []
    with open(filename, 'r') as file:
        data = json.load(file)  # Load JSON data from the file
        for sport in data:
            

            home_team = sport['home_team']
            away_team = sport['away_team']
            game_time = sport['commence_time']
            game=(home_team,away_team,game_time)
            if game not in games:
                games.append(game)

    games_df = pd.DataFrame(games, columns=["home_team", "away_team", "game_time"])
    print(games_df)        

def bookies_and_odds(filename):
    with open(filename, 'r') as file:
        data = json.load(file)  # Load JSON data from the file
        all_unique_bookies = []
        game_lines = []
        for sport in data:
            game_time = sport['commence_time']
            for bookmaker in sport['bookmakers']:
                bookie = bookmaker['title']
                if bookie not in all_unique_bookies:
                    all_unique_bookies.append(bookie)
                last_updated = bookmaker['last_update']
                for market in bookmaker['markets']:
                    outcomes = market['outcomes']
                    if len(outcomes) == 2:
                        team1 = outcomes[0]['name']
                        line1 = outcomes[0]['price']
                        team2 = outcomes[1]['name']
                        line2 = outcomes[1]['price']

                        game_lines.append([bookie,team1,line1,team2,line2,game_time,last_updated])
    df = pd.DataFrame(game_lines, columns=['bookie', 'team1', 'line1', 'team2', 'line2', 'game_time','last_updated'])
    df.to_csv('output.csv', index=False)

# teams_and_gametime('NFL_Data')
bookies_and_odds('NFL_Data')