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
import time

logger = logging.getLogger(__name__)

if os.environ.get("AWS_EXECUTION_ENV") is None:
   from dotenv import load_dotenv
   from src.visualizations.graph_details import plot_moneyline
   load_dotenv()
   
ATHENA_DATABASE = os.environ["ATHENA_DATABASE"]
ATHENA_OUTPUT_LOCATION = os.environ["ATHENA_OUTPUT_LOCATION"]

# Initialize S3 client
s3_client = boto3.client('s3')
athena_client = boto3.client('athena')


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
        all_game_results = odds_api.filter_scores()
        game_totals, game_spreads, game_lines = odds_api.bookies_and_odds()
        all_prop_bets, unique_player_props = odds_api.prop_bets_filters()
        all_event_ids, all_event_details = odds_api.get_events()

        db.insert_NFL_upcoming_games(all_event_details)
        db.insert_NFL_scores(all_game_results)

        arbitage = ArbitrageAnalyzer(all_prop_bets)
        arbitage_props = arbitage.analyze()

        #process expected value
        ev_opportunities_ml_results = ExpectedValueAnalyzer(game_lines)
        ev_opportunities_ml = ev_opportunities_ml_results.analyze_ml()

        ev_opportunities_prop_results = ExpectedValueAnalyzer(all_prop_bets)
        ev_opportunities_prop = ev_opportunities_prop_results.analyze_prop() 

  
        # Upload the CSV file to S3
        save_and_upload_props_to_s3(all_prop_bets, os.environ['S3_BUCKET_NAME'])
    
        ## remove existing and Insert data into latest_tables for best bets
        VALID_TABLES = ['upcoming_games', 'latest_spreads', 'latest_moneyline', 'latest_overunder', 'expected_value_moneyline', 'expected_value_props', 'arbitrage']


        def clean_tables(table_name):
            try:
                db.truncate_table(f'{table_name}')
            except Exception as e:
                logging.error(f'Error with truncating {table_name} table. Error: {e}')
                pass

        clean_tables('upcoming_games')
        clean_tables('arbitrage')
        db.insert_arbitrage(arbitage_props)
        # Insert data into Postgresql tables for expected value
        clean_tables('expected_value_moneyline')
        db.insert_expected_value_moneyline(ev_opportunities_ml)
        clean_tables('expected_value_props')
        db.insert_expected_value_props(ev_opportunities_prop)

        # # insert latest bookie data and aggregate props data simultaneously
        clean_tables('latest_moneyline')
        db.insert_moneyline_and_latest_moneyline(game_lines)
        clean_tables('latest_spreads')
        db.insert_spreads_and_latest_spreads(game_spreads)
        clean_tables('latest_overunder')
        db.insert_overunder_and_latest_overunder(game_totals)

        #update unique players in distinct props
        db.update_distinct_props(unique_player_props)

        # delete old games
        db.delete_old_games()

        VALID_CLEANUP_TABLES = ['moneyline', 'spreads', 'overunder']
        for cleanup in VALID_CLEANUP_TABLES:
            db.clean_old_data(cleanup)

        # this triggers delete on cascade to only have most recent events
        try:
            db.delete_games_with_true_status()  # Delete any game_IDs with True status as the game is completed
            logger.info("Removed all game_IDs with game_status set to True")
        except Exception as e:
            logger.error(f"Error occurred removing game_IDs with True status. Error {e}")



    except Exception as e:
        logger.error(f"An error occurred. Error: {e}")

    finally:
        if db:
            db.close_connection()

def save_and_upload_props_to_s3(all_prop_bets, bucket_name, max_files=24,
                                prefix="props/", latest_prefix="latest-props/"):
    """Saves prop bets to S3 and repairs Athena tables when CSVs update."""
    try:
        if not all_prop_bets:
            logger.warning("The all_prop_bets list is empty. No CSV file will be created.")
            return

        # Create timestamped filename
        file_name = f"all_props_{datetime.utcnow():%Y%m%d%H%M%S}.csv"
        props_key = f"{prefix}{file_name}"
        latest_key = f"{latest_prefix}{file_name}"

        # Write CSV to in-memory buffer
        column_names = [
            "game_ID", "last_updated_timestamp", "bookie", "prop_type",
            "bet_type", "player_name", "betting_line", "betting_point", "sport_type"
        ]
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(column_names)
        writer.writerows(all_prop_bets)
        buffer.seek(0)
        byte_buf = io.BytesIO(buffer.getvalue().encode('utf-8'))

        # Upload to props/ and latest-props/
        s3_client.upload_fileobj(byte_buf, bucket_name, props_key, ExtraArgs={'ContentType': 'text/csv'})
        logger.info(f"Uploaded {props_key} to s3://{bucket_name}/{props_key}")

        buffer.seek(0)
        byte_buf = io.BytesIO(buffer.getvalue().encode('utf-8'))
        s3_client.upload_fileobj(byte_buf, bucket_name, latest_key, ExtraArgs={'ContentType': 'text/csv'})
        logger.info(f"Uploaded {latest_key} to s3://{bucket_name}/{latest_key}")

        # Cleanup latest-props folder
        latest_objs = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=latest_prefix).get('Contents', [])
        if len(latest_objs) > 1:
            old = sorted(latest_objs, key=lambda o: o['LastModified'])[:-1]
            s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': [{'Key': o['Key']} for o in old]})
            logger.info(f"Deleted {len(old)} old files in {latest_prefix}")

        # Cleanup props folder
        all_objs = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix).get('Contents', [])
        if len(all_objs) > max_files:
            old = sorted(all_objs, key=lambda o: o['LastModified'])[:-max_files]
            s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': [{'Key': o['Key']} for o in old]})
            logger.info(f"Deleted {len(old)} old files in {prefix}")

        # Repair Athena tables after S3 update
        for table in ('latest_props', 'props'):
            q = f"MSCK REPAIR TABLE {table};"
            resp = athena_client.start_query_execution(
                QueryString=q,
                QueryExecutionContext={'Database': ATHENA_DATABASE},
                ResultConfiguration={'OutputLocation': ATHENA_OUTPUT_LOCATION}
            )
            qid = resp['QueryExecutionId']
            # Optionally poll for completion
            state = 'RUNNING'
            while state in ('RUNNING', 'QUEUED'):
                time.sleep(1)
                status = athena_client.get_query_execution(QueryExecutionId=qid)['QueryExecution']['Status']
                state = status['State']
            logger.info(f"MSCK REPAIR for {table} completed with state {state}")

    except Exception as e:
        logger.error(f"Failed in save_and_upload_props_to_s3: {e}", exc_info=True)

if __name__ == "__main__":
    lambda_handler()