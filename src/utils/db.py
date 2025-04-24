"""
db.py - Contains functionality to interact with our Azure SQL DB
"""
import psycopg2
import os
from pathlib import Path
import logging
import io
import traceback
import time
from psycopg2.extras import execute_batch, execute_values


logger = logging.getLogger(__name__)

class DB:
    """Organizes database operations"""

    def __init__(self):
        """Constructor method"""

        try:
            self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            self.cursor = self.conn.cursor()
            logger.info("Database connection established.")
        except Exception as e:
            logger.error(f"Failed to connect to the database. Error: {e}", exc_info=True)


    def create_db(self):
        """Creates database in cluster

        :param db_name: name of database
        """

        try:
            with self.conn.cursor() as cursor:
                cursor.execute('CREATE DATABASE IF NOT EXISTS "defaultdb"')
            self.conn.commit()
            logger.info("defaultdb created or already exists")
        except Exception as e:
            logger.error(f"Failed to create default db. Error: {e}", exc_info=True)


### START NFL upcoming games Create, insert, Get, Clear
    def create_NFL_upcoming_games(self):
        """Creates upcoming_games table in DB"""

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS upcoming_games (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        sport_title TEXT NOT NULL,
                        event_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp for the event
                        home_team TEXT NOT NULL,
                        away_team TEXT NOT NULL
                    );
                    """
                )
            self.conn.commit()
            logger.info(f" 'upcoming_games' table created")
        except Exception as e:
            logger.error(f"Failed to create 'upcoming_games' table. Error: {e}", exc_info=True)

    def insert_NFL_upcoming_games(self, upcoming_games):
        """Inserts provided list of tuples of upcoming games into DB

        Args:
        upcoming games (list of tuples): The list of tuples will have the following columns.
                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'sport_title': Will be the name of what sport these games are played in
                - 'event_timestamp': time of the game
                - 'Home_Team': Home Team
                - 'Away_Team': Away Team
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.executemany("INSERT INTO upcoming_games (game_ID, sport_title, event_timestamp, home_team, away_team) VALUES (%s, %s, %s, %s, %s)", upcoming_games)
            self.conn.commit()
            logger.info(f"Successfully inserted upcoming NFL games into upcoming_games table")
        except Exception as e:
            logger.error(f"Failed to insert data into upcoming_games table. Error: {e}, data: {upcoming_games}", exc_info=True)

### END NFL upcoming games Create, insert, Get, Clear

### START NFL SPREADS Create, insert, Get, Clear
    def create_NFL_spreads(self):
        """Creates spreads table in DB"""

        try:

            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS spreads (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        Bookie TEXT NOT NULL,
                        Matchup_Type TEXT NOT NULL,
                        Home_Team TEXT NOT NULL,
                        Spread_1 FLOAT NOT NULL,
                        Line_1 INT NOT NULL,
                        Away_Team TEXT NOT NULL,
                        Spread_2 FLOAT NOT NULL,
                        Line_2 INT NOT NULL,
                        event_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp for the event
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update
                        sport_type TEXT NOT NULL,
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created spreads table or table already exists")
        except Exception as e:
            logger.error(f"failed to create spreads table. Error: {e}", exc_info=True)

    def insert_NFL_spreads(self, spreads):
        """Inserts provided list of tuples of spreads into DB after verifying the game_ID exists in scores

        Args:
        spreads (list of tuples): The list of tuples will have the following columns.
                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'Bookie': Name of one of 10 bookies included in OddsAPI
                - 'Matchup_Type': Type of matchup needed for the bet
                - 'Home_Team': Home Team
                - 'Spread_1': Spread for the home team
                - 'Line_1': Betting line for the home team spread
                - 'Away_Team': Away Team
                - 'Spread_2': Spread for the away team
                - 'Line_2': Betting line for the away team spread
                - 'event_timestamp': time of the game
                - 'last_updated_timestamp': last time updated
                - 'sport_type': the type of sport for this bet
        """
        try:
            with self.conn.cursor() as cursor:
                for spread in spreads:
                    game_id = spread[0]  # Assuming game_ID is the first element in each tuple

                    # Check if game_ID exists in the 'scores' table
                    cursor.execute("SELECT 1 FROM scores WHERE game_id = %s", (game_id,))
                    if not cursor.fetchone():
                        # If game_ID does not exist, log an error and skip this insert
                        logger.error(f"Game ID {game_id} does not exist in scores. Skipping insertion for this game.")
                        continue

                    # If game_ID exists, proceed with the insert
                    cursor.execute("""
                        INSERT INTO spreads (
                            game_ID, Bookie, Matchup_Type, Home_Team, Spread_1, Line_1, 
                            Away_Team, Spread_2, Line_2, event_timestamp, last_updated_timestamp, sport_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, spread)
                    logger.info(f"Game ID {game_id} succesfully inserted into latest spreads.")

            self.conn.commit()
            logger.info("Successfully inserted data into spreads table")
        except Exception as e:
            logger.error(f"Failed to insert data into spreads table. Error: {e}, data: {spreads}", exc_info=True)

    def insert_spreads_and_latest_spreads(self, spreads, batch_size=1000, max_retries=3):
        """Inserts provided list of spreads into both 'spreads' and 'latest_spreads' tables in batches with retry logic."""
        try:
            logger.debug("Splitting data into batches for spreads and latest_spreads.")
            batches = [spreads[i:i + batch_size] for i in range(0, len(spreads), batch_size)]

            for attempt in range(max_retries):
                try:
                    with self.conn.cursor() as cursor:
                        for batch_index, batch in enumerate(batches):
                            logger.debug(f"Inserting batch {batch_index + 1} with {len(batch)} rows.")
                            sanitized_batch = [
                                (
                                    str(row[0]),  # game_ID
                                    str(row[1]),  # Bookie
                                    str(row[2]),  # Matchup_Type
                                    str(row[3]),  # Home_Team
                                    float(row[4]),  # Spread_1
                                    int(row[5]),  # Line_1
                                    str(row[6]),  # Away_Team
                                    float(row[7]),  # Spread_2
                                    int(row[8]),  # Line_2
                                    row[9],       # event_timestamp
                                    row[10],      # last_updated_timestamp
                                    str(row[11])  # sport_type
                                )
                                for row in batch
                            ]

                            query = """
                                WITH inserted AS (
                                    INSERT INTO spreads (
                                        game_ID, Bookie, Matchup_Type, Home_Team, Spread_1, Line_1, 
                                        Away_Team, Spread_2, Line_2, event_timestamp, last_updated_timestamp, sport_type
                                    ) VALUES %s
                                    ON CONFLICT DO NOTHING
                                    RETURNING game_ID, Bookie, Matchup_Type, Home_Team, Spread_1, Line_1, 
                                              Away_Team, Spread_2, Line_2, event_timestamp, last_updated_timestamp, sport_type
                                )
                                INSERT INTO latest_spreads (
                                    game_ID, Bookie, Matchup_Type, Home_Team, Spread_1, Line_1, 
                                    Away_Team, Spread_2, Line_2, event_timestamp, last_updated_timestamp, sport_type
                                )
                                SELECT * FROM inserted
                                ON CONFLICT DO NOTHING;
                            """
                            execute_values(
                                cursor,
                                query,
                                sanitized_batch,
                                template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            )
                            logger.info(f"Inserted batch {batch_index + 1} with {len(batch)} rows into spreads and latest_spreads.")

                    self.conn.commit()
                    logger.info(f"Successfully inserted {len(spreads)} rows into both spreads and latest_spreads tables.")
                    return
                except psycopg2.OperationalError as e:
                    logger.warning(f"Serialization failure on attempt {attempt + 1}/{max_retries}. Retrying...")
                    self.conn.rollback()
                    time.sleep(2 ** attempt)
                except Exception as e:
                    logger.error(f"Error inserting data into spreads and latest_spreads tables. Full traceback:\n{traceback.format_exc()}")
                    self.conn.rollback()
                    raise

            logger.error(f"Failed to insert spreads and latest_spreads after {max_retries} retries.")
            raise Exception("Max retries exceeded for insert_spreads_and_latest_spreads.")
        except Exception as e:
            logger.error(f"Unhandled error in insert_spreads_and_latest_spreads. Full traceback:\n{traceback.format_exc()}")

###### END NFL SPREADS Create, insert, Get, Clear


### START NFL MoneyLine Create, insert, Get, Clear
    def create_NFL_moneyline(self):
        """Creates moneyline table in DB"""

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS moneyline (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        Bookie TEXT NOT NULL,
                        Matchup_Type TEXT NOT NULL,
                        Home_Team TEXT NOT NULL,
                        Line_1 INT NOT NULL,
                        Away_Team TEXT NOT NULL,
                        Line_2 INT NOT NULL,
                        event_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp for the event
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update
                        sport_type TEXT NOT NULL,
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created moneyline table or table already exists")
        except Exception as e:
            logger.error(f"failed to create moneyline table. Error: {e}", exc_info=True)


    def insert_NFL_moneyline(self, moneyline):
        """Inserts provided list of tuples of moneylines into DB after verifying the game_ID exists in scores

        Args:
        moneylines (list of tuples): The list of tuples will have the following columns.
                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'Bookie': Name of one of 10 bookies included in OddsAPI
                - 'Matchup_Type': Type of matchup needed for the bet
                - 'Home_Team': Home Team
                - 'Line_1': Betting line for the home team Moneyline
                - 'Away_Team': Away Team
                - 'Line_2': Betting line for the away team Moneyline
                - 'event_timestamp': time of the game
                - 'last_updated_timestamp': last time updated
                - 'sport_type': the type of sport for this bet
        """
        try:
            with self.conn.cursor() as cursor:
                for line in moneyline:
                    game_id = line[0]  # Assuming game_ID is the first element in each tuple

                    # Check if game_ID exists in the 'scores' table
                    cursor.execute("SELECT 1 FROM scores WHERE game_id = %s", (game_id,))
                    if not cursor.fetchone():
                        # If game_ID does not exist, log an error and skip this insert
                        logger.error(f"Game ID {game_id} does not exist in scores. Skipping insertion for this game.")
                        continue

                    # If game_ID exists, proceed with the insert
                    cursor.execute("""
                        INSERT INTO moneyline (
                            game_ID, Bookie, Matchup_Type, Home_Team, Line_1, Away_Team, 
                            Line_2, event_timestamp, last_updated_timestamp, sport_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, line)

            self.conn.commit()
            logger.info("Successfully inserted data into moneyline table")
        except Exception as e:
            logger.error(f"Failed to insert data into moneyline table. Error: {e}, data: {moneyline}", exc_info=True)

    def insert_moneyline_and_latest_moneyline(self, moneyline, batch_size=1000, max_retries=3):
        """Inserts provided list of moneyline data into both 'moneyline' and 'latest_moneyline' tables in batches with retry logic."""
        try:
            logger.debug("Splitting data into batches for moneyline and latest_moneyline.")
            batches = [moneyline[i:i + batch_size] for i in range(0, len(moneyline), batch_size)]

            for attempt in range(max_retries):
                try:
                    with self.conn.cursor() as cursor:
                        for batch_index, batch in enumerate(batches):
                            logger.debug(f"Inserting batch {batch_index + 1} with {len(batch)} rows.")
                            sanitized_batch = [
                                (
                                    str(row[0]),  # game_ID
                                    str(row[1]),  # Bookie
                                    str(row[2]),  # Matchup_Type
                                    str(row[3]),  # Home_Team
                                    int(row[4]),  # Line_1
                                    str(row[5]),  # Away_Team
                                    int(row[6]),  # Line_2
                                    row[7],       # event_timestamp
                                    row[8],       # last_updated_timestamp
                                    str(row[9])   # sport_type
                                )
                                for row in batch
                            ]

                            query = """
                                WITH inserted AS (
                                    INSERT INTO moneyline (
                                        game_ID, Bookie, Matchup_Type, Home_Team, Line_1, Away_Team, 
                                        Line_2, event_timestamp, last_updated_timestamp, sport_type
                                    ) VALUES %s
                                    ON CONFLICT DO NOTHING
                                    RETURNING game_ID, Bookie, Matchup_Type, Home_Team, Line_1, Away_Team, 
                                              Line_2, event_timestamp, last_updated_timestamp, sport_type
                                )
                                INSERT INTO latest_moneyline (
                                    game_ID, Bookie, Matchup_Type, Home_Team, Line_1, Away_Team, 
                                    Line_2, event_timestamp, last_updated_timestamp, sport_type
                                )
                                SELECT * FROM inserted
                                ON CONFLICT DO NOTHING;
                            """
                            execute_values(
                                cursor,
                                query,
                                sanitized_batch,
                                template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            )
                            logger.info(f"Inserted batch {batch_index + 1} with {len(batch)} rows into moneyline and latest_moneyline.")

                    self.conn.commit()
                    logger.info(f"Successfully inserted {len(moneyline)} rows into both moneyline and latest_moneyline tables.")
                    return
                except psycopg2.OperationalError as e:
                    logger.warning(f"Serialization failure on attempt {attempt + 1}/{max_retries}. Retrying...")
                    self.conn.rollback()
                    time.sleep(2 ** attempt)
                except Exception as e:
                    logger.error(f"Error inserting data into moneyline and latest_moneyline tables. Full traceback:\n{traceback.format_exc()}")
                    self.conn.rollback()
                    raise

            logger.error(f"Failed to insert moneyline and latest_moneyline after {max_retries} retries.")
            raise Exception("Max retries exceeded for insert_moneyline_and_latest_moneyline.")
        except Exception as e:
            logger.error(f"Unhandled error in insert_moneyline_and_latest_moneyline. Full traceback:\n{traceback.format_exc()}")


### END NFL MoneyLine Create, insert, Get, Clear


### START NFL Overunder Create, insert, Get, Clear
    def create_NFL_overunder(self):
        """ Creates overunder table in DB """

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS overunder (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        Bookie TEXT NOT NULL,
                        Matchup_Type TEXT NOT NULL,
                        Home_Team TEXT NOT NULL,
                        Away_Team TEXT NOT NULL,
                        Over_or_Under_1 TEXT NOT NULL,
                        Over_Under_Total_1 FLOAT NOT NULL,
                        Over_Under_Line_1 INT NOT NULL,
                        Over_or_Under_2 TEXT NOT NULL,
                        Over_Under_Total_2 FLOAT NOT NULL,
                        Over_Under_Line_2 INT NOT NULL,
                        event_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp for the event
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update
                        sport_type TEXT NOT NULL,
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created overunder table or table already exists")
        except Exception as e:
            logger.error(f"Failed to create overunder table. Error: {e}", exc_info=True)

    def insert_NFL_overunder(self, overunder):
        """Inserts provided list of tuples of overunders into DB

        Args:
        overunder (list of tuples): The list of tuples will have the following columns.
                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'Bookie': Name of one of 10 bookies included in OddsAPI
                - 'Matchup_Type': Type of matchup needed for the bet
                - 'Home_Team': Home Team
                - 'Away_Team': Away Team                
                - 'Over_or_Under_1': Either "Over" or "Under"
                - 'Over_Under_Total_1': total points scored for over or under
                - 'Over_Under_Line_1': betting line for total / over or under
                - 'Over_or_Under_2': Either "Over" or "Under"
                - 'Over_Under_Total_2': total points scored for over or under
                - 'Over_Under_Line_2': betting line for total / over or under
                - 'event_timestamp': time of the game
                - 'last_updated_timestamp': last time updated
                - 'sport_type': the type of sport for this bet
        """
        try:
            with self.conn.cursor() as cursor:
                for line in overunder:
                    # Check if the game_id exists in the scores table before inserting
                    game_id = line[0]
                    cursor.execute("SELECT 1 FROM scores WHERE game_id = %s", (game_id,))
                    if cursor.fetchone():
                        cursor.execute("INSERT INTO overunder (game_ID, Bookie, Matchup_Type, Home_Team, Away_Team, Over_or_Under_1, Over_Under_Total_1, Over_Under_Line_1, Over_or_Under_2, Over_Under_Total_2, Over_Under_Line_2, event_timestamp, last_updated_timestamp, sport_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", line)
                    else:
                        logger.error(f"Game ID {game_id} not found in scores table. Skipping insert.")
                self.conn.commit()
                logger.info("Successfully inserted data into overunder table")
        except Exception as e:
            logger.error(f"Failed to insert data into overunder table. Error: {e}, data: {overunder}", exc_info=True)

    def insert_overunder_and_latest_overunder(self, overunder, batch_size=1000, max_retries=3):
        """Inserts provided list of overunder data into both 'overunder' and 'latest_overunder' tables in batches with retry logic."""
        try:
            logger.debug("Splitting data into batches for overunder and latest_overunder.")
            batches = [overunder[i:i + batch_size] for i in range(0, len(overunder), batch_size)]

            for attempt in range(max_retries):
                try:
                    with self.conn.cursor() as cursor:
                        for batch_index, batch in enumerate(batches):
                            logger.debug(f"Inserting batch {batch_index + 1} with {len(batch)} rows.")
                            sanitized_batch = [
                                (
                                    str(row[0]),  # game_ID
                                    str(row[1]),  # Bookie
                                    str(row[2]),  # Matchup_Type
                                    str(row[3]),  # Home_Team
                                    str(row[4]),  # Away_Team
                                    str(row[5]),  # Over_or_Under_1
                                    float(row[6]),  # Over_Under_Total_1
                                    int(row[7]),  # Over_Under_Line_1
                                    str(row[8]),  # Over_or_Under_2
                                    float(row[9]),  # Over_Under_Total_2
                                    int(row[10]), # Over_Under_Line_2
                                    row[11],      # event_timestamp
                                    row[12],      # last_updated_timestamp
                                    str(row[13])  # sport_type
                                )
                                for row in batch
                            ]

                            query = """
                                WITH inserted AS (
                                    INSERT INTO overunder (
                                        game_ID, Bookie, Matchup_Type, Home_Team, Away_Team, Over_or_Under_1, 
                                        Over_Under_Total_1, Over_Under_Line_1, Over_or_Under_2, Over_Under_Total_2, 
                                        Over_Under_Line_2, event_timestamp, last_updated_timestamp, sport_type
                                    ) VALUES %s
                                    ON CONFLICT DO NOTHING
                                    RETURNING game_ID, Bookie, Matchup_Type, Home_Team, Away_Team, Over_or_Under_1, 
                                              Over_Under_Total_1, Over_Under_Line_1, Over_or_Under_2, Over_Under_Total_2, 
                                              Over_Under_Line_2, event_timestamp, last_updated_timestamp, sport_type
                                )
                                INSERT INTO latest_overunder (
                                    game_ID, Bookie, Matchup_Type, Home_Team, Away_Team, Over_or_Under_1, 
                                    Over_Under_Total_1, Over_Under_Line_1, Over_or_Under_2, Over_Under_Total_2, 
                                    Over_Under_Line_2, event_timestamp, last_updated_timestamp, sport_type
                                )
                                SELECT * FROM inserted
                                ON CONFLICT DO NOTHING;
                            """
                            execute_values(
                                cursor,
                                query,
                                sanitized_batch,
                                template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            )
                            logger.info(f"Inserted batch {batch_index + 1} with {len(batch)} rows into overunder and latest_overunder.")

                    self.conn.commit()
                    logger.info(f"Successfully inserted {len(overunder)} rows into both overunder and latest_overunder tables.")
                    return
                except psycopg2.OperationalError as e:
                    logger.warning(f"Serialization failure on attempt {attempt + 1}/{max_retries}. Retrying...")
                    self.conn.rollback()
                    time.sleep(2 ** attempt)
                except Exception as e:
                    logger.error(f"Error inserting data into overunder and latest_overunder tables. Full traceback:\n{traceback.format_exc()}")
                    self.conn.rollback()
                    raise

            logger.error(f"Failed to insert overunder and latest_overunder after {max_retries} retries.")
            raise Exception("Max retries exceeded for insert_overunder_and_latest_overunder.")
        except Exception as e:
            logger.error(f"Unhandled error in insert_overunder_and_latest_overunder. Full traceback:\n{traceback.format_exc()}")

### END NFL Overunder Create, insert, Get, Clear

### START NFL Props Create, insert, Get, Clear
    def create_NFL_props(self):
        """ Creates props table in DB """

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS props (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update              
                        Bookie TEXT NOT NULL,
                        Prop_Type TEXT NOT NULL,
                        Bet_Type TEXT NOT NULL,
                        Player_Name TEXT NOT NULL,
                        Betting_Line INT NOT NULL,
                        Betting_Point TEXT NOT NULL, -- this is text because it can either be N/A or a float. Easier to convert text of a float later on.
                        sport_type TEXT NOT NULL,
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created props table or table already exists")
        except Exception as e:
            logger.error(f"error creating props table. Error: {e}", exc_info=True)

    def bulk_insert_with_copy_props(self, props):
        """Fallback to bulk insert using INSERT statements for CockroachDB (for props table)."""
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO props (
                        game_id, last_updated_timestamp, bookie, prop_type,
                        bet_type, player_name, betting_line, betting_point, sport_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                logger.debug("Executing batch INSERT query for props.")
                execute_batch(cursor, query, props)
                self.conn.commit()
                logger.info(f"Successfully inserted {len(props)} rows into props using batch INSERT.")
        except Exception as e:
            logger.error(f"Batch INSERT for props failed. Error: {e}", exc_info=True)
            logger.debug("Rolling back transaction for props.")
            self.conn.rollback()
            raise

    def insert_NFL_props(self, props, batch_size=1000):
        """Inserts provided list of props into DB in batches."""
        try:
            logger.debug("Splitting data into batches for NFL props.")
            # Split data into batches
            batches = [props[i:i + batch_size] for i in range(0, len(props), batch_size)]

            # Insert batches
            for batch_index, batch in enumerate(batches):
                try:
                    logger.debug(f"Inserting batch {batch_index + 1} with {len(batch)} rows.")
                    self.bulk_insert_with_copy_props(batch)  # Use the fallback bulk insert for props
                    logger.info(f"Inserted batch {batch_index + 1} with {len(batch)} rows into props.")
                except Exception as e:
                    logger.error(f"Failed to insert batch {batch_index + 1}. Error: {e}", exc_info=True)
                    raise

            logger.info(f"Successfully inserted {len(props)} props into props table.")
        except Exception as e:
            logger.error(f"Error inserting data into props table. Full traceback:\n{traceback.format_exc()}")

    def create_distinct_props(self):
        """ Creates distinct props table in DB """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS distinct_props (
                        id SERIAL PRIMARY KEY,
                        player_name TEXT NOT NULL,
                        game_ID VARCHAR(255) NOT NULL,  -- Game ID added
                        sport_type TEXT NOT NULL,
                        last_updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Track when this entry was last updated
                        UNIQUE(player_name, game_ID, sport_type)  -- Ensure uniqueness across player, game, and sport type
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created distinct_props table or table already exists")
        except Exception as e:
            logger.error(f"Error creating distinct_props table. Error: {e}", exc_info=True)


    def update_distinct_props(self):
        """ Update distinct_props table with unique values from the main props table """
        try:
            with self.conn.cursor() as cursor:
                # Delete players who no longer have props
                cursor.execute("""
                    DELETE FROM distinct_props
                    WHERE (player_name, game_ID, sport_type) NOT IN (
                        SELECT DISTINCT player_name, game_ID, sport_type
                        FROM props
                    );
                """)

                # Insert/update players who currently have props bets into the distinct_props table
                cursor.execute("""
                    INSERT INTO distinct_props (player_name, game_ID, sport_type)
                    SELECT DISTINCT player_name, game_ID, sport_type
                    FROM props
                    ON CONFLICT (player_name, game_ID, sport_type) DO UPDATE
                    SET last_updated = CURRENT_TIMESTAMP;
                """)
            self.conn.commit()
            logger.info("Successfully updated distinct_props table.")
        except Exception as e:
            logger.error(f"Error updating distinct_props table. Error: {e}", exc_info=True)



    # Clean up the distinct_props table by removing players who no longer have props bets


    # You could schedule this function to run periodically using Celery or a cron job.




#### End NFL Props Create, insert, Get, Clear

##### Same tables as insert and create above but will be refreshed with the latest API data

    def create_latest_spreads(self):
        """Creates spreads table in DB"""

        try:

            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS latest_spreads (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        Bookie TEXT NOT NULL,
                        Matchup_Type TEXT NOT NULL,
                        Home_Team TEXT NOT NULL,
                        Spread_1 FLOAT NOT NULL,
                        Line_1 INT NOT NULL,
                        Away_Team TEXT NOT NULL,
                        Spread_2 FLOAT NOT NULL,
                        Line_2 INT NOT NULL,
                        event_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp for the event
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update
                        sport_type TEXT NOT NULL,
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created spreads table or table already exists")
        except Exception as e:
            logger.error(f"failed to create spreads table. Error: {e}", exc_info=True)

    def insert_latest_spreads(self, spreads):
        """Inserts provided list of tuples of spreads into DB after verifying the game_ID exists in scores

        Args:
        spreads (list of tuples): The list of tuples will have the following columns.
                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'Bookie': Name of one of 10 bookies included in OddsAPI
                - 'Matchup_Type': Type of matchup needed for the bet
                - 'Home_Team': Home Team
                - 'Spread_1': Spread for the home team
                - 'Line_1': Betting line for the home team spread
                - 'Away_Team': Away Team
                - 'Spread_2': Spread for the away team
                - 'Line_2': Betting line for the away team spread
                - 'event_timestamp': time of the game
                - 'last_updated_timestamp': last time updated
                - 'sport_type': the type of sport for this bet
        """
        try:
            with self.conn.cursor() as cursor:
                for spread in spreads:
                    game_id = spread[0]  # Assuming game_ID is the first element in each tuple

                    # Check if game_ID exists in the 'scores' table
                    cursor.execute("SELECT 1 FROM scores WHERE game_id = %s", (game_id,))
                    if not cursor.fetchone():
                        # If game_ID does not exist, log an error and skip this insert
                        logger.error(f"Game ID {game_id} does not exist in scores. Skipping insertion for this game.")
                        continue

                    # If game_ID exists, proceed with the insert
                    cursor.execute("""
                        INSERT INTO latest_spreads (
                            game_ID, Bookie, Matchup_Type, Home_Team, Spread_1, Line_1, 
                            Away_Team, Spread_2, Line_2, event_timestamp, last_updated_timestamp, sport_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, spread)
                    logger.info(f"Game ID {game_id} succesfully inserted into latest spreads.")

            self.conn.commit()
            logger.info("Successfully inserted data into latest_spreads table")
        except Exception as e:
            logger.error(f"Failed to insert data into latest_spreads table. Error: {e}, data: {spreads}", exc_info=True)


###### END NFL SPREADS Create, insert, Get, Clear


### START NFL MoneyLine Create, insert, Get, Clear
    def create_latest_moneyline(self):
        """Creates moneyline table in DB"""

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS latest_moneyline (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        Bookie TEXT NOT NULL,
                        Matchup_Type TEXT NOT NULL,
                        Home_Team TEXT NOT NULL,
                        Line_1 INT NOT NULL,
                        Away_Team TEXT NOT NULL,
                        Line_2 INT NOT NULL,
                        event_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp for the event
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update
                        sport_type TEXT NOT NULL,
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created latest_moneyline table or table already exists")
        except Exception as e:
            logger.error(f"failed to create latest_moneyline table. Error: {e}", exc_info=True)

    def insert_latest_moneyline(self, moneyline):
        """Inserts provided list of tuples of moneylines into DB after verifying the game_ID exists in scores

        Args:
        moneylines (list of tuples): The list of tuples will have the following columns.
                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'Bookie': Name of one of 10 bookies included in OddsAPI
                - 'Matchup_Type': Type of matchup needed for the bet
                - 'Home_Team': Home Team
                - 'Line_1': Betting line for the home team Moneyline
                - 'Away_Team': Away Team
                - 'Line_2': Betting line for the away team Moneyline
                - 'event_timestamp': time of the game
                - 'last_updated_timestamp': last time updated
                - 'sport_type': the type of sport for this bet
        """
        try:
            with self.conn.cursor() as cursor:
                for line in moneyline:
                    game_id = line[0]  # Assuming game_ID is the first element in each tuple

                    # Check if game_ID exists in the 'scores' table
                    cursor.execute("SELECT 1 FROM scores WHERE game_id = %s", (game_id,))
                    if not cursor.fetchone():
                        # If game_ID does not exist, log an error and skip this insert
                        logger.error(f"Game ID {game_id} does not exist in scores. Skipping insertion for this game.")
                        continue

                    # If game_ID exists, proceed with the insert
                    cursor.execute("""
                        INSERT INTO latest_moneyline (
                            game_ID, Bookie, Matchup_Type, Home_Team, Line_1, Away_Team, 
                            Line_2, event_timestamp, last_updated_timestamp, sport_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, line)

            self.conn.commit()
            logger.info("Successfully inserted data into latest_moneyline table")
        except Exception as e:
            logger.error(f"Failed to insert data into latest_moneyline table. Error: {e}, data: {moneyline}", exc_info=True)


### END NFL MoneyLine Create, insert, Get, Clear


### START NFL Overunder Create, insert, Get, Clear
    def create_latest_overunder(self):
        """ Creates overunder table in DB """

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS latest_overunder (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        Bookie TEXT NOT NULL,
                        Matchup_Type TEXT NOT NULL,
                        Home_Team TEXT NOT NULL,
                        Away_Team TEXT NOT NULL,
                        Over_or_Under_1 TEXT NOT NULL,
                        Over_Under_Total_1 FLOAT NOT NULL,
                        Over_Under_Line_1 INT NOT NULL,
                        Over_or_Under_2 TEXT NOT NULL,
                        Over_Under_Total_2 FLOAT NOT NULL,
                        Over_Under_Line_2 INT NOT NULL,
                        event_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp for the event
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update
                        sport_type TEXT NOT NULL,
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created latest_overunder table or table already exists")
        except Exception as e:
            logger.error(f"Failed to create latest_overunder table. Error: {e}", exc_info=True)

    def insert_latest_overunder(self, overunder):
        """Inserts provided list of tuples of overunders into DB

        Args:
        overunder (list of tuples): The list of tuples will have the following columns.
                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'Bookie': Name of one of 10 bookies included in OddsAPI
                - 'Matchup_Type': Type of matchup needed for the bet
                - 'Home_Team': Home Team
                - 'Away_Team': Away Team                
                - 'Over_or_Under_1': Either "Over" or "Under"
                - 'Over_Under_Total_1': total points scored for over or under
                - 'Over_Under_Line_1': betting line for total / over or under
                - 'Over_or_Under_2': Either "Over" or "Under"
                - 'Over_Under_Total_2': total points scored for over or under
                - 'Over_Under_Line_2': betting line for total / over or under
                - 'event_timestamp': time of the game
                - 'last_updated_timestamp': last time updated
                - 'sport_type': the type of sport for this bet
        """
        try:
            with self.conn.cursor() as cursor:
                for line in overunder:
                    # Check if the game_id exists in the scores table before inserting
                    game_id = line[0]
                    cursor.execute("SELECT 1 FROM scores WHERE game_id = %s", (game_id,))
                    if cursor.fetchone():
                        cursor.execute("INSERT INTO latest_overunder (game_ID, Bookie, Matchup_Type, Home_Team, Away_Team, Over_or_Under_1, Over_Under_Total_1, Over_Under_Line_1, Over_or_Under_2, Over_Under_Total_2, Over_Under_Line_2, event_timestamp, last_updated_timestamp, sport_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", line)
                    else:
                        logger.error(f"Game ID {game_id} not found in scores table. Skipping insert.")
                self.conn.commit()
                logger.info("Successfully inserted data into latest_overunder table")
        except Exception as e:
            logger.error(f"Failed to insert data into latest_overunder table. Error: {e}, data: {overunder}", exc_info=True)


### END NFL Overunder Create, insert, Get, Clear

### START NFL Props Create, insert, Get, Clear
    def create_latest_props(self):
        """ Creates props table in DB """

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS latest_props (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255),
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update              
                        Bookie TEXT NOT NULL,
                        Prop_Type TEXT NOT NULL,
                        Bet_Type TEXT NOT NULL,
                        Player_Name TEXT NOT NULL,
                        Betting_Line INT NOT NULL,
                        Betting_Point TEXT NOT NULL, -- this is text because it can either be N/A or a float. Easier to convert text of a float later on.
                        sport_type TEXT NOT NULL,
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created latest_props table or table already exists")
        except Exception as e:
            logger.error(f"error creating latest_props table. Error: {e}", exc_info=True)

    def bulk_insert_with_copy_latest_props(self, props):
            """Fallback to bulk insert using INSERT statements for CockroachDB."""
            try:
                with self.conn.cursor() as cursor:
                    query = """
                        INSERT INTO latest_props (
                            game_id, last_updated_timestamp, bookie, prop_type,
                            bet_type, player_name, betting_line, betting_point, sport_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    logger.debug("Executing batch INSERT query.")
                    execute_batch(cursor, query, props)
                    self.conn.commit()
                    logger.info(f"Successfully inserted {len(props)} rows into latest_props using batch INSERT.")
            except Exception as e:
                logger.error(f"Batch INSERT failed. Error: {e}", exc_info=True)
                logger.debug("Rolling back transaction.")
                self.conn.rollback()
                raise

    def insert_latest_props(self, props, batch_size=1000):
        """Inserts provided list of props into DB in batches."""
        try:
            logger.debug("Splitting data into batches.")
            # Split data into batches
            batches = [props[i:i + batch_size] for i in range(0, len(props), batch_size)]

            # Insert batches
            for batch_index, batch in enumerate(batches):
                try:
                    logger.debug(f"Inserting batch {batch_index + 1} with {len(batch)} rows.")
                    self.bulk_insert_with_copy_latest_props(batch)  # Use the fallback bulk insert
                    logger.info(f"Inserted batch {batch_index + 1} with {len(batch)} rows.")
                except Exception as e:
                    logger.error(f"Failed to insert batch {batch_index + 1}. Error: {e}", exc_info=True)
                    raise

            logger.info(f"Successfully inserted {len(props)} props into latest_props table.")
        except Exception as e:
            logger.error(f"Error inserting data into latest_props table. Full traceback:\n{traceback.format_exc()}")

    def insert_props_and_latest_props(self, props, batch_size=1000, max_retries=3):
        """Inserts provided list of props into both 'props' and 'latest_props' tables in batches with retry logic."""
        try:
            logger.debug("Splitting data into batches for props and latest_props.")
            batches = [props[i:i + batch_size] for i in range(0, len(props), batch_size)]

            for attempt in range(max_retries):
                try:
                    with self.conn.cursor() as cursor:
                        for batch_index, batch in enumerate(batches):
                            logger.debug(f"Inserting batch {batch_index + 1} with {len(batch)} rows.")
                            sanitized_batch = [
                                (
                                    str(row[0]),  # game_ID
                                    row[1],       # last_updated_timestamp
                                    str(row[2]),  # bookie
                                    str(row[3]),  # prop_type
                                    str(row[4]),  # bet_type
                                    str(row[5]),  # player_name
                                    int(row[6]),  # betting_line
                                    str(row[7]),  # betting_point
                                    str(row[8])   # sport_type
                                )
                                for row in batch
                            ]

                            query = """
                                WITH inserted AS (
                                    INSERT INTO props (
                                        game_ID, last_updated_timestamp, bookie, prop_type,
                                        bet_type, player_name, betting_line, betting_point, sport_type
                                    ) VALUES %s
                                    ON CONFLICT DO NOTHING
                                    RETURNING game_ID, last_updated_timestamp, bookie, prop_type,
                                              bet_type, player_name, betting_line, betting_point, sport_type
                                )
                                INSERT INTO latest_props (
                                    game_ID, last_updated_timestamp, bookie, prop_type,
                                    bet_type, player_name, betting_line, betting_point, sport_type
                                )
                                SELECT * FROM inserted
                                ON CONFLICT DO NOTHING;
                            """
                            execute_values(
                                cursor,
                                query,
                                sanitized_batch,
                                template="(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            )
                            logger.info(f"Inserted batch {batch_index + 1} with {len(batch)} rows into props and latest_props.")

                    self.conn.commit()
                    logger.info(f"Successfully inserted {len(props)} props into both props and latest_props tables.")
                    return
                except psycopg2.OperationalError as e:
                    logger.warning(f"Serialization failure on attempt {attempt + 1}/{max_retries}. Retrying...")
                    self.conn.rollback()
                    time.sleep(2 ** attempt)
                except Exception as e:
                    logger.error(f"Error inserting data into props and latest_props tables. Full traceback:\n{traceback.format_exc()}")
                    self.conn.rollback()
                    raise

            logger.error(f"Failed to insert props and latest_props after {max_retries} retries.")
            raise Exception("Max retries exceeded for insert_props_and_latest_props.")
        except Exception as e:
            logger.error(f"Unhandled error in insert_props_and_latest_props. Full traceback:\n{traceback.format_exc()}")

##### Same tables as insert and create above but will be refreshed with the latest API data


#### START NFL Scores Create, insert, Get, Clear
    def create_NFL_scores(self):
        """ Creates Scores table in DB """

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scores (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255) UNIQUE,
                        sport_title TEXT NOT NULL,      
                        game_time TIMESTAMPTZ NOT NULL, -- Timestamp of last update  
                        game_status TEXT NOT NULL,
                        last_updated_timestamp TIMESTAMPTZ, -- Timestamp of last update
                        team1 TEXT,
                        score1 INT,
                        team2 TEXT,
                        score2 INT
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created scores table or table already exists")
        except Exception as e:
            logger.error(f"error creating scores table. Error: {e}", exc_info=True)

    def insert_NFL_scores(self, scores):
        """Inserts provided list of tuples of scores into DB only if game_status and game_ID are not already in the table.

        Args:
        scores (list of tuples): The list of tuples will have the following columns.

                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'sport_title': name of sport being uploaded into db
                - 'game_time': time game starts      
                - 'game_status': completed or incomplete game
                - 'last_updated_timestamp': last time updated    
                - 'team1': name of team 1
                - 'score1': score of team 1
                - 'team2': name of team 2     
                - 'score2': score of team 2
        """
        try:
            with self.conn.cursor() as cursor:
                for score in scores:
                    cursor.execute("""
                                        INSERT INTO scores (game_ID, sport_title, game_time, game_status, last_updated_timestamp, team1, score1, team2, score2)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        ON CONFLICT (game_ID) DO UPDATE SET
                                            sport_title = EXCLUDED.sport_title,
                                            game_time = EXCLUDED.game_time,
                                            game_status = EXCLUDED.game_status,
                                            last_updated_timestamp = EXCLUDED.last_updated_timestamp,
                                            team1 = EXCLUDED.team1,
                                            score1 = EXCLUDED.score1,
                                            team2 = EXCLUDED.team2,
                                            score2 = EXCLUDED.score2;
                                    """, score)
            self.conn.commit()
            logger.info("Successfully inserted NFL scores data into scores table")
        except Exception as e:
            logger.error(f"Failed to insert NFL scores data into scores table. Error: {e}, data: {scores}", exc_info=True)


    def delete_games_with_true_status(self):
        """Deletes all rows for game_IDs where any row has game_status = 'False'."""
        try:
            with self.conn.cursor() as cursor:
                # Find all game_IDs where any row has game_status = 'False'
                cursor.execute("""
                    SELECT DISTINCT game_ID
                    FROM scores
                    WHERE game_status = 'true';
                """)
                game_ids_to_delete = [gid[0] for gid in cursor.fetchall()]

                if game_ids_to_delete:
                    # Delete all rows with those game_IDs
                    cursor.execute("""
                        DELETE FROM scores
                        WHERE game_ID = ANY(%s);
                    """, (game_ids_to_delete,))  # Pass list directly for PostgreSQL array format
                    self.conn.commit()
                    logger.info(f"Deleted all rows for game_IDs: {game_ids_to_delete}")
                else:
                    logger.info("No rows with game_status = 'true' found for deletion.")
        except Exception as e:
            logger.error(f"Error occurred deleting scores where game_status is true. Error: {e}", exc_info=True)

    def delete_old_games(self):
        """Deletes rows in the 'scores' table where the game_time is older than 2 days."""
        try:
            with self.conn.cursor() as cursor:
                # Get the current time minus 2 days
                cursor.execute("""
                    DELETE FROM scores
                    WHERE game_time < CURRENT_TIMESTAMP - INTERVAL '2 days';
                """)
                self.conn.commit()
                logger.info("Successfully deleted rows with game_time older than 2 days.")
        except Exception as e:
            logger.error(f"Error occurred deleting old game data from scores table. Error: {e}", exc_info=True)


# ### End NFL Props Create, insert, Get, Clear

    #    "84d20dc0dc4467c9fbc67824a1ffa2e3",
    #     "BetMGM",
    #     "h2h",
    #     "Chicago Blackhawks",
    #     105,
    #     "San Jose Sharks",
    #     -125,
    #     "2025-03-14T02:30:00Z",
    #     "2025-03-14T00:06:03Z",
    #     "icehockey_nhl"

### START +EV table


    def create_latest_EV_moneyline(self):
        """Creates the expected_value_moneyline table in the database with a unique constraint."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS expected_value_moneyline (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255) NOT NULL,
                        Bookie TEXT NOT NULL,
                        Matchup_Type TEXT NOT NULL,
                        Team TEXT NOT NULL,
                        Line INT NOT NULL,
                        Expected_Value FLOAT NOT NULL CHECK (Expected_Value > 0),
                        Fair_Probability FLOAT NOT NULL,
                        Implied_Probability FLOAT NOT NULL,
                        Market_Overround FLOAT NOT NULL,
                        sport_type TEXT NOT NULL,
                        event_timestamp TIMESTAMPTZ NOT NULL,  -- Timestamp for the event
                        last_updated_timestamp TIMESTAMPTZ NOT NULL,  -- Timestamp of last update
                        CONSTRAINT expected_value_moneyline_game_id_bookie_team_line_key
                        UNIQUE (game_ID, Bookie, Team, Line)
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created expected_value_moneyline table or table already exists")
        except Exception as e:
            logger.error(f"Failed to create expected_value_moneyline table. Error: {e}", exc_info=True)
            self.conn.rollback()  # Roll back on failure

    def insert_expected_value_moneyline(self, expected_value_moneyline):
        """Inserts provided list of tuples of +EV into DB after verifying the game_ID exists in scores.

        Args:
            expected_value_moneyline (list of tuples): The list of tuples will have the following columns:
                - 'game_ID': Unique ID from OddsAPI for a game/event (str).
                - 'Bookie': Name of one of 10 bookies included in OddsAPI (str).
                - 'Matchup_Type': Type of matchup needed for the bet (str).
                - 'Team': Team with the positive expected value to be bet on (str).
                - 'Line': Betting line for the team Moneyline (int).
                - 'Expected_Value': The expected profit per $100 bet, calculated as 
                                   (fair probability * payout) - (1 - fair probability) * bet amount, 
                                   rounded to 2 decimal places (float).
                - 'Fair_Probability': The adjusted probability of the team winning, derived by normalizing 
                                     the implied probability against the market overround, rounded to 4 decimal places (float).
                - 'Implied_Probability': The probability implied by the betting line for the specific bookie, 
                                        calculated from American odds as 100 / (odds + 100) for positive odds 
                                        or -odds / (-odds + 100) for negative odds, rounded to 4 decimal places (float).
                - 'Market_Overround': The sum of implied probabilities across all outcomes, representing the 
                                     bookmaker's margin or the market's total probability (e.g., 1.0456 for 104.56%), 
                                     rounded to 4 decimal places (float).
                - 'sport_type': The type of sport for this bet (str).
                - 'event_timestamp': Time of the game in ISO 8601 format (str).
                - 'last_updated_timestamp': Last time the odds were updated in ISO 8601 format (str).
        """
        if not isinstance(expected_value_moneyline, list):
            raise TypeError(f"expected_value_moneyline must be a list of tuples, got {type(expected_value_moneyline)}")

        inserted_count = 0
        line = None
        try:
            with self.conn.cursor() as cursor:
                for line in expected_value_moneyline:
                    game_id = line[0]  # game_ID is the first element in each tuple

                    # Check if game_ID exists in the 'scores' table
                    cursor.execute("SELECT 1 FROM scores WHERE game_id = %s", (game_id,))
                    if not cursor.fetchone():
                        logger.warning(f"Game ID {game_id} does not exist in scores. Skipping insertion for this game.")
                        continue

                    # Insert the row, using the unique constraint to handle duplicates
                    cursor.execute("""
                        INSERT INTO expected_value_moneyline (
                            game_ID, Bookie, Matchup_Type, Team, Line, Expected_Value, 
                            Fair_Probability, Implied_Probability, Market_Overround, sport_type, 
                            event_timestamp, last_updated_timestamp
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT ON CONSTRAINT expected_value_moneyline_game_id_bookie_team_line_key 
                        DO NOTHING
                    """, line)
                    inserted_count += 1

            self.conn.commit()
            logger.info(f"Successfully inserted {inserted_count} rows into 'expected_value_moneyline' table")
        except Exception as e:
            if line is not None:
                logger.error(f"Failed to insert into 'expected_value_moneyline' table. Error: {e}, problematic line: {line}", exc_info=True)
            else:
                logger.error(f"Failed to insert into 'expected_value_moneyline' table. Error: {e}", exc_info=True)
            self.conn.rollback()  # Roll back on error


                        # id SERIAL PRIMARY KEY,
                        # game_ID VARCHAR(255),
                        # last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update              
                        # Bookie TEXT NOT NULL,
                        # 
                        # 
                        # 
                        # 
                        # 
                        # sport_type TEXT NOT NULL,
                        # FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE

    def create_latest_EV_props(self):
        """Creates the expected_value_props table in the database with a unique constraint."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS expected_value_props (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255) NOT NULL,
                        Bookie TEXT NOT NULL,
                        Prop_Type TEXT NOT NULL,
                        Bet_Type TEXT NOT NULL,
                        Player_Name TEXT NOT NULL,
                        Betting_Line INT NOT NULL,
                        Betting_Point TEXT NOT NULL,
                        Expected_Value FLOAT NOT NULL CHECK (Expected_Value > 0),
                        Fair_Probability FLOAT NOT NULL,
                        Implied_Probability FLOAT NOT NULL,
                        Market_Overround FLOAT NOT NULL,
                        sport_type TEXT NOT NULL,
                        last_updated_timestamp TIMESTAMPTZ NOT NULL,
                        num_bookies INT NOT NULL,
                        z_score DECIMAL(10, 2) NULL,
                        CONSTRAINT expected_value_props_game_id_bookie_prop_bet_player_line_key
                        UNIQUE (game_ID, Bookie, Prop_Type, Bet_Type, Player_Name, Betting_Line)
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created expected_value_props table or table already exists")
        except Exception as e:
            logger.error(f"Failed to create expected_value_props table. Error: {e}", exc_info=True)
            self.conn.rollback()

    def insert_expected_value_props(self, expected_value_props):
        """Inserts provided list of +EV props into DB after verifying the game_ID exists in scores.

        Args:
            expected_value_props (list of tuples): List of tuples with the following columns:
                - game_ID (str): Unique ID from OddsAPI for a game/event.
                - Bookie (str): Name of one of 10 bookies included in OddsAPI.
                - Prop_Type (str): Type of prop bet (e.g., 'player_points').
                - Bet_Type (str): Type of bet ('yes', 'over', 'under').
                - Player_Name (str): Player with the positive expected value.
                - Betting_Point (str): Line for the prop bet, or 'N/A' for 'yes' bets.
                - Betting_Line (int): Betting odds in American format.
                - Expected_Value (float): Expected profit per $100 bet, rounded to 2 decimal places.
                - Fair_Probability (float): Adjusted probability, rounded to 4 decimal places.
                - Implied_Probability (float): Probability from odds, rounded to 4 decimal places.
                - Market_Overround (float): Bookmaker's margin, rounded to 4 decimal places.
                - sport_type (str): Type of sport (e.g., 'basketball_nba').
                - last_updated_timestamp (str): Last update time in ISO 8601 format.
                - num_bookies: number of bookies offering this prop
                - z_score (float or None): Z-score of implied probability vs. market, rounded to 2 decimal places, or NULL if not calculable.
        """
        if not isinstance(expected_value_props, list):
            raise TypeError(f"expected_value_props must be a list of tuples, got {type(expected_value_props)}")

        inserted_count = 0
        line = None
        try:
            with self.conn.cursor() as cursor:
                for line in expected_value_props:
                    game_id = line[0]
                    cursor.execute("SELECT 1 FROM scores WHERE game_id = %s", (game_id,))
                    if not cursor.fetchone():
                        logger.warning(f"Game ID {game_id} does not exist in scores. Skipping insertion.")
                        continue

                    cursor.execute("""
                        INSERT INTO expected_value_props (
                            game_ID, Bookie, Prop_Type, Bet_Type, Player_Name, Betting_Point, Betting_Line,
                            Expected_Value, Fair_Probability, Implied_Probability, Market_Overround,
                            sport_type, last_updated_timestamp, num_bookies, z_score
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT ON CONSTRAINT expected_value_props_game_id_bookie_prop_bet_player_line_key 
                        DO NOTHING
                    """, line)
                    inserted_count += 1

            self.conn.commit()
            logger.info(f"Successfully inserted {inserted_count} rows into 'expected_value_props' table")
        except Exception as e:
            if line is not None:
                logger.error(f"Failed to insert into 'expected_value_props' table. Error: {e}, problematic line: {line}", exc_info=True)
            else:
                logger.error(f"Failed to insert into 'expected_value_props' table. Error: {e}", exc_info=True)
            self.conn.rollback()

### START +EV table

    def create_arbitrage(self):
        """Creates the arbitrage table in the database with a unique constraint."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS arbitrage (
                        id SERIAL PRIMARY KEY,
                        game_ID VARCHAR(255) NOT NULL,
                        Prop_Type TEXT NOT NULL,
                        Player_Name TEXT NOT NULL,
                        Betting_Point TEXT NOT NULL,
                        sport_type TEXT NOT NULL,
                        bookie_one TEXT NOT NULL,
                        outcome_one TEXT,
                        odds_one INT NOT NULL,
                        bet_amount_one FLOAT NOT NULL,
                        bookie_two TEXT NOT NULL,
                        outcome_two TEXT,
                        odds_two INT NOT NULL,
                        bet_amount_two FLOAT NOT NULL,
                        profit_percentage FLOAT NOT NULL,
                        last_updated_timestamp TIMESTAMPTZ NOT NULL,
                        UNIQUE (game_ID, Prop_Type, Player_Name, Betting_Point, bookie_one, outcome_one, bookie_two, outcome_two)
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created arbitrage table or table already exists")
        except Exception as e:
            logger.error(f"Failed to create arbitrage table. Error: {e}", exc_info=True)
            self.conn.rollback()

    def insert_arbitrage(self, arbitrage):
        """
        Inserts arbitrage opportunities into the database.

        Args:
            arbitrage (list of tuples): List of tuples with the following columns:
                - game_ID (str): Unique ID from OddsAPI for the relevant game or event.
                - Prop_Type (str): Type of prop bet (e.g., 'player_points', 'game_winner').
                - Player_Name (str): Name of the player associated with the prop bet.
                - Betting_Point (str): Line or point for the prop bet (e.g., '25.5' for points).
                - sport_type (str): Sport type (e.g., 'basketball_nba', 'football_nfl').
                - bookie_one (str): Name of the first bookmaker offering one side of the prop.
                - outcome_one (str or None): Outcome offered by bookie_one (e.g., 'over', 'under').
                - odds_one (int): American odds provided by bookie_one (e.g., -110, +130).
                - bet_amount_one (float): Suggested bet amount on bookie_one to lock in profit.
                - bookie_two (str): Name of the second bookmaker offering the opposing side.
                - outcome_two (str or None): Outcome offered by bookie_two.
                - odds_two (int): American odds provided by bookie_two.
                - bet_amount_two (float): Suggested bet amount on bookie_two to lock in profit.
                - profit_percentage (float): Percentage profit from the arbitrage opportunity, rounded to 2 decimal places.
                - last_updated_timestamp (str): ISO 8601 format timestamp of the latest odds update.
        """

        if not isinstance(arbitrage, list):
            raise TypeError(f"arbitrage must be a list of tuples, got {type(arbitrage)}")

        inserted_count = 0
        line = None
        try:
            with self.conn.cursor() as cursor:
                for line in arbitrage:
                    cursor.execute("""
                        INSERT INTO arbitrage (
                            game_ID, Prop_Type, Player_Name, Betting_Point, sport_type,
                            bookie_one, outcome_one, odds_one, bet_amount_one,
                            bookie_two, outcome_two, odds_two, bet_amount_two,
                            profit_percentage, last_updated_timestamp
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (game_ID, Prop_Type, Player_Name, Betting_Point, bookie_one, outcome_one, bookie_two, outcome_two) DO NOTHING
                    """, line)
                    inserted_count += cursor.rowcount  # Accurately count inserted rows

            self.conn.commit()
            logger.info(f"Successfully inserted {inserted_count} rows into 'arbitrage' table")
        except Exception as e:
            if line is not None:
                logger.error(f"Failed to insert into 'arbitrage' table. Error: {e}, problematic line: {line}", exc_info=True)
            else:
                logger.error(f"Failed to insert into 'arbitrage' table. Error: {e}", exc_info=True)
            self.conn.rollback()


### end arbitrage

    def clean_old_data(self, table: str) -> None:
        """Deletes records older than 24 hours from the specified table based on last_updated_timestamp.

        Args:
            table (str): The name of the table to clean.
        """
        VALID_TABLES = ['moneyline', 'overunder', 'props', 'spreads']

        if table not in VALID_TABLES:
            logger.error(f"Invalid table name: {table}. Cleanup operation aborted.")
            raise ValueError(f"Invalid table name: {table}")

        try:
            with self.conn.cursor() as cursor:
                query = f"""
                DELETE FROM {table} 
                WHERE last_updated_timestamp < NOW() - INTERVAL '1 day';
                """
                cursor.execute(query)
                rows_deleted = cursor.rowcount  # Get the number of deleted rows
            self.conn.commit()
            logger.info(f"Successfully deleted {rows_deleted} rows from {table} table")
        except Exception as e:
            logger.error(f"Failed to clean {table} table. Error: {e}", exc_info=True)


    ### truncate data from table
    def truncate_table(self, table: str) -> None:
        """Truncates a specified table in the database, with validation.

        Args:
            table (str): The name of the table to truncate.
        """
        VALID_TABLES = ['upcoming_games', 'latest_spreads', 'latest_moneyline', 'latest_overunder', 'latest_props', 'expected_value_moneyline', 'expected_value_props', 'arbitrage']

        if table not in VALID_TABLES:
            logger.error(f"Invalid table name: {table}. Truncate operation aborted.")
            raise ValueError(f"Invalid table name: {table}")

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {table};")
            self.conn.commit()
            logger.info(f"Successfully truncated {table} table")
        except Exception as e:
            logger.error(f"Failed to truncate {table} table. Error: {e}", exc_info=True)

#Close database connection after api calls run.
    def close_connection(self):
        """Closes the database connection"""
        if self.conn:
            try:
                self.conn.close()
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Failed to close database connection. Error: {e}", exc_info=True)
