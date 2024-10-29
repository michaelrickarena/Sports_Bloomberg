from dotenv import load_dotenv
from src.data.odds_api import Odds_API
from src.utils.db import DB
from src.visualizations.graph_details import plot_moneyline
import logging

logger = logging.getLogger(__name__)
load_dotenv()

def main():
    logger.info("Executing main...")
    
    db = None  # Ensure db is defined before try block

    try:
        db = DB()
        odds_api = Odds_API()

        # Create tables and db
        db.create_db()
        db.create_NFL_scores()
        db.create_NFL_upcoming_games()
        db.create_NFL_spreads()
        db.create_NFL_moneyline()
        db.create_NFL_overunder()
        db.create_NFL_props()
        
        all_game_results = odds_api.filter_scores()
        game_totals, game_spreads, game_lines = odds_api.bookies_and_odds()
        all_prop_bets = odds_api.prop_bets_filters()
        all_event_ids, all_event_details = odds_api.get_events()

        try:
            db.truncate_table('upcoming_games')
        except Exception as e:
            logging.error(f'Error with truncating upcoming_games table. Error: {e}')
            pass

        ## Insert data into tables
        db.insert_NFL_scores(all_game_results)
        db.insert_NFL_upcoming_games(all_event_details)
        db.insert_NFL_spreads(game_spreads)
        db.insert_NFL_moneyline(game_lines)
        db.insert_NFL_overunder(game_totals)
        db.insert_NFL_props(all_prop_bets)

        try:
            db.delete_games_with_false_status()  # Delete any game_IDs with False status
            logger.info("Removed all game_IDs with game_status set to False")
        except Exception as e:
            logger.error(f"Error occurred removing game_IDs with False status. Error {e}")


    except Exception as e:
        logger.error(f"An error occurred. Error: {e}")

    finally:
        if db:
            db.close_connection()

if __name__ == "__main__":
    main()
    # plot_moneyline()
