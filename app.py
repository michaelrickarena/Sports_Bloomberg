import os
from src.data.odds_api import Odds_API
from src.utils.db import DB
import logging

logger = logging.getLogger(__name__)

if os.environ.get("AWS_EXECUTION_ENV") is None:
   from dotenv import load_dotenv
   from src.visualizations.graph_details import plot_moneyline
   load_dotenv()

def lambda_handler(event=None, context=None):
    logger.info("Executing main...")

    db = None  # Ensure db is defined before try block

    try:
        db = DB()
        odds_api = Odds_API()
        odds_api.fetch_active_sports()

        # Create tables and db
        db.create_db()
        db.create_NFL_scores()
        db.create_NFL_upcoming_games()
        db.create_NFL_spreads()
        db.create_NFL_moneyline()
        db.create_NFL_overunder()
        db.create_NFL_props()
        db.create_latest_props()
        db.create_latest_moneyline()
        db.create_latest_spreads()
        db.create_latest_overunder()
    
        # API Usage from Odds API
        all_game_results = odds_api.filter_scores()
        game_totals, game_spreads, game_lines = odds_api.bookies_and_odds()
        all_prop_bets = odds_api.prop_bets_filters()
        all_event_ids, all_event_details = odds_api.get_events()

        ## remove existing and Insert data into latest_tables for best bets
        VALID_TABLES = ['upcoming_games', 'latest_spreads', 'latest_moneyline', 'latest_overunder', 'latest_props']
        for table in VALID_TABLES:
            try:
                db.truncate_table(f'{table}')
            except Exception as e:
                logging.error(f'Error with truncating {table} table. Error: {e}')
                pass
        
        ## Insert data into Postgresql tables for line graphs
        db.insert_NFL_scores(all_game_results)

        # insert latest bookie data
        db.insert_latest_spreads(game_spreads)
        db.insert_latest_moneyline(game_lines)
        db.insert_latest_overunder(game_totals)
        db.insert_latest_props(all_prop_bets)

        # insert bookie data into aggregate tables
        db.insert_NFL_upcoming_games(all_event_details)
        db.insert_NFL_spreads(game_spreads)
        db.insert_NFL_moneyline(game_lines)
        db.insert_NFL_overunder(game_totals)
        db.insert_NFL_props(all_prop_bets)

        # this triggers delete on cascade to only have most recent events
        try:
            db.delete_games_with_false_status()  # Delete any game_IDs with False status as the game is completed
            logger.info("Removed all game_IDs with game_status set to False")
        except Exception as e:
            logger.error(f"Error occurred removing game_IDs with False status. Error {e}")

    except Exception as e:
        logger.error(f"An error occurred. Error: {e}")

    finally:
        if db:
            db.close_connection()

if __name__ == "__main__":
    lambda_handler()



