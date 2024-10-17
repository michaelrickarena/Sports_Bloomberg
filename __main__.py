from dotenv import load_dotenv
from src.data.odds_api import Odds_API
from src.utils.db import DB
import psycopg2
import logging.config

# Load logging configuration
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('db_logger')

def main():
    logger.info("Executing main...")

    load_dotenv()
    db = None  # Ensure db is defined before try block

    try:
        db = DB()
        odds_api = Odds_API()

        # Create tables and db
        db.create_db()
        db.create_NFL_upcoming_games()
        db.create_NFL_spreads()
        db.create_NFL_moneyline()
        db.create_NFL_overunder()
        db.create_NFL_props()

        game_totals, game_spreads, game_lines = odds_api.bookies_and_odds()
        all_prop_bets = odds_api.prop_bets_filters()
        all_event_ids, all_event_details = odds_api.get_events()

        # Insert data into tables
        db.insert_NFL_upcoming_games(all_event_details)
        db.insert_NFL_spreads(game_spreads)
        db.insert_NFL_moneyline(game_lines)
        db.insert_NFL_overunder(game_totals)
        db.insert_NFL_props(all_prop_bets)



    except Exception as e:
        logger.error(f"An error occurred. Error: {e}")

    finally:
        if db:
            db.close_connection()

if __name__ == "__main__":
    main()


## Clear Data from tables
# db.truncate_table('moneyline')
# db.truncate_table('spreads')
# db.truncate_table('overunder')