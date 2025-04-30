import os
import csv
from src.data.odds_api import Odds_API
from src.utils.db import DB
from src.data.expected_value import ExpectedValueAnalyzer
from src.data.arbitrage import ArbitrageAnalyzer
import logging
import boto3
from datetime import datetime
import io

logger = logging.getLogger(__name__)

if os.environ.get("AWS_EXECUTION_ENV") is None:
   from dotenv import load_dotenv
   from src.visualizations.graph_details import plot_moneyline
   load_dotenv()

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event=None, context=None):
    logger.info("Executing main...")

    db = None  # Ensure db is defined before try block

    try:
        db = DB()        
        odds_api = Odds_API()
        odds_api.fetch_active_sports()

        # Create tables and db
        db.create_db()
        # db.create_NFL_scores()
        # db.create_NFL_upcoming_games()
        # db.create_NFL_spreads()
        # db.create_NFL_moneyline()
        # db.create_NFL_overunder()
        # db.create_NFL_props()
        # db.create_latest_props()
        # db.create_latest_moneyline()
        # db.create_latest_spreads()
        # db.create_latest_overunder()
        # db.create_distinct_props()
        # db.create_latest_EV_moneyline()
        # db.create_latest_EV_props()
        # db.create_arbitrage()

        # API Usage from Odds API
        # all_game_results = odds_api.filter_scores()
        # game_totals, game_spreads, game_lines = odds_api.bookies_and_odds()
        all_prop_bets = odds_api.prop_bets_filters()
        # all_event_ids, all_event_details = odds_api.get_events()

        # db.insert_NFL_upcoming_games(all_event_details)
        # db.insert_NFL_scores(all_game_results)

        # arbitage = ArbitrageAnalyzer(all_prop_bets)
        # arbitage_props = arbitage.analyze()

        # #process expected value
        # ev_opportunities_ml_results = ExpectedValueAnalyzer(game_lines)
        # ev_opportunities_ml = ev_opportunities_ml_results.analyze_ml()

        # ev_opportunities_prop_results = ExpectedValueAnalyzer(all_prop_bets)
        # ev_opportunities_prop = ev_opportunities_prop_results.analyze_prop() 

  
        # Upload the CSV file to S3
        save_and_upload_props_to_s3(all_prop_bets, os.environ['S3_BUCKET_NAME'])
    
        # ## remove existing and Insert data into latest_tables for best bets
        # VALID_TABLES = ['upcoming_games', 'latest_spreads', 'latest_moneyline', 'latest_overunder', 'latest_props', 'expected_value_moneyline', 'expected_value_props', 'arbitrage']


        # def clean_tables(table_name):
        #     try:
        #         db.truncate_table(f'{table_name}')
        #     except Exception as e:
        #         logging.error(f'Error with truncating {table_name} table. Error: {e}')
        #         pass

        # clean_tables('upcoming_games')
        # clean_tables('arbitrage')
        # db.insert_arbitrage(arbitage_props)
        # # Insert data into Postgresql tables for expected value
        # clean_tables('expected_value_moneyline')
        # db.insert_expected_value_moneyline(ev_opportunities_ml)
        # clean_tables('expected_value_props')
        # db.insert_expected_value_props(ev_opportunities_prop)

        # # # insert latest bookie data and aggregate props data simultaneously
        # clean_tables('latest_moneyline')
        # db.insert_moneyline_and_latest_moneyline(game_lines)
        # clean_tables('latest_spreads')
        # db.insert_spreads_and_latest_spreads(game_spreads)
        # clean_tables('latest_overunder')
        # db.insert_overunder_and_latest_overunder(game_totals)
        # clean_tables('latest_props')
        # db.insert_props_and_latest_props(all_prop_bets)

        # #update unique players in distinct props
        # db.update_distinct_props()

        # # delete old games
        # db.delete_old_games()

        # VALID_CLEANUP_TABLES = ['moneyline', 'spreads', 'props', 'overunder']
        # for cleanup in VALID_CLEANUP_TABLES:
        #     db.clean_old_data(cleanup)

        # # this triggers delete on cascade to only have most recent events
        # try:
        #     db.delete_games_with_true_status()  # Delete any game_IDs with True status as the game is completed
        #     logger.info("Removed all game_IDs with game_status set to True")
        # except Exception as e:
        #     logger.error(f"Error occurred removing game_IDs with True status. Error {e}")



    except Exception as e:
        logger.error(f"An error occurred. Error: {e}")

    finally:
        if db:
            db.close_connection()

def save_and_upload_props_to_s3(all_prop_bets, bucket_name, max_files=24, prefix="props/", latest_prefix="latest-props/"):
    """Saves the all_prop_bets list of tuples to an in-memory CSV file, uploads it to S3,
    manages files in the props folder, and ensures only one file exists in the latest-props folder.

    Args:
        all_prop_bets (list of tuples): The list of prop bets to save.
        bucket_name (str): The name of the S3 bucket.
        max_files (int): Maximum number of CSV files allowed in the bucket prefix.
        prefix (str): S3 key prefix for CSV files.
        latest_prefix (str): S3 key prefix for the latest CSV file.
    """
    try:
        if not all_prop_bets:
            logger.warning(
                "The all_prop_bets list is empty. No CSV file will be created."
            )
            return

        # Generate the file name with the current timestamp
        file_name = f"all_props_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
        s3_key = f"{prefix}{file_name}"
        latest_s3_key = f"{latest_prefix}{file_name}"

        # Define the CSV column names
        column_names = [
            "game_ID", "last_updated_timestamp", "bookie", "prop_type",
            "bet_type", "player_name", "betting_line", "betting_point", "sport_type"
        ]

        # Create an in-memory CSV file using StringIO
        text_buffer = io.StringIO()
        writer = csv.writer(text_buffer)
        writer.writerow(column_names)
        writer.writerows(all_prop_bets)

        # Convert text buffer to bytes buffer for S3 upload
        text_buffer.seek(0)
        byte_buffer = io.BytesIO(text_buffer.getvalue().encode('utf-8'))

        # Upload the CSV buffer to the props folder in S3
        s3_client.upload_fileobj(byte_buffer, bucket_name, s3_key, ExtraArgs={'ContentType': 'text/csv'})
        logger.info(f"Successfully uploaded {file_name} to s3://{bucket_name}/{s3_key}")

        # Reset the buffer for reuse
        text_buffer.seek(0)
        byte_buffer = io.BytesIO(text_buffer.getvalue().encode('utf-8'))

        # Upload the same CSV buffer to the latest-props folder in S3
        s3_client.upload_fileobj(byte_buffer, bucket_name, latest_s3_key, ExtraArgs={'ContentType': 'text/csv'})
        logger.info(f"Successfully uploaded {file_name} to s3://{bucket_name}/{latest_s3_key}")

        # Ensure only one file exists in the latest-props folder
        latest_response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=latest_prefix)
        latest_objects = latest_response.get('Contents', [])

        if len(latest_objects) > 1:
            # Sort objects by LastModified ascending
            sorted_latest_objs = sorted(latest_objects, key=lambda obj: obj['LastModified'])
            # Delete all but the most recent file
            to_delete_latest = sorted_latest_objs[:-1]
            delete_latest_keys = [{'Key': obj['Key']} for obj in to_delete_latest]

            # Perform batch delete
            delete_latest_response = s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_latest_keys}
            )
            deleted_latest = delete_latest_response.get('Deleted', [])
            logger.info(f"Deleted {len(deleted_latest)} old files in latest-props: {[d['Key'] for d in deleted_latest]}")

        # List existing files in the props folder
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        objects = response.get('Contents', [])

        # If more than max_files, delete the oldest ones
        if len(objects) > max_files:
            # Sort objects by LastModified ascending
            sorted_objs = sorted(objects, key=lambda obj: obj['LastModified'])
            # Determine how many to delete
            to_delete = sorted_objs[:-max_files]
            delete_keys = [{'Key': obj['Key']} for obj in to_delete]

            # Perform batch delete
            delete_response = s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_keys}
            )
            deleted = delete_response.get('Deleted', [])
            logger.info(f"Deleted {len(deleted)} old files in props: {[d['Key'] for d in deleted]}")

    except Exception as e:
        logger.error(f"Failed to upload or cleanup CSVs on S3. Error: {e}", exc_info=True)

if __name__ == "__main__":
    lambda_handler()