import os
from pathlib import Path
import logging
import sys
import matplotlib.pyplot as plt
from src.utils.db import DB

logger = logging.getLogger(__name__)

def plot_moneyline():
    db = DB()
    moneyline_data = db.get_moneyline_data()
    
    # Prepare data
    game_ids = []
    bookies = []
    home_teams = []
    lines_1 = []  # Home Team Betting Lines
    away_teams = []
    lines_2 = []  # Away Team Betting Lines
    timestamps = []

    for row in moneyline_data:
        game_id, bookie, home_team, line_1, away_team, line_2, last_updated_timestamp = row
        game_ids.append(game_id)
        bookies.append(bookie)
        home_teams.append(home_team)
        lines_1.append(line_1)
        away_teams.append(away_team)
        lines_2.append(line_2)
        timestamps.append(last_updated_timestamp)

    # Limit to first 5 unique games
    unique_games = list(set(game_ids))

    for game_id in unique_games:
        plt.figure(figsize=(12, 6))
        indices = [i for i, x in enumerate(game_ids) if x == game_id]
        
        for bookie in set([bookies[i] for i in indices]):
            bookie_indices = [i for i in indices if bookies[i] == bookie]
            
            # Plot for Home Team Line (Line 1)
            plt.plot([timestamps[i] for i in bookie_indices], [lines_1[i] for i in bookie_indices],
                     marker='o', label=f"{bookie} Home Team ({home_teams[bookie_indices[0]]}) - Game ID {game_id}")

            # Plot for Away Team Line (Line 2)
            plt.plot([timestamps[i] for i in bookie_indices], [lines_2[i] for i in bookie_indices],
                     marker='x', linestyle='--', label=f"{bookie} Away Team ({away_teams[bookie_indices[0]]}) - Game ID {game_id}")

        plt.title(f'Betting Line Movements for Game ID {game_id}')
        plt.xlabel('Last Updated Timestamp')
        plt.ylabel('Betting Lines')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Place legend outside the plot
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()  # Show the plot for the current game ID
