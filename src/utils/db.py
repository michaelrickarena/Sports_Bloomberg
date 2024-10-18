"""
db.py - Contains functionality to interact with our Azure SQL DB
"""
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path
import logging.config

# Load environment variables
env_path = Path('../../.env')
load_dotenv(dotenv_path=env_path)

# Load logging configuration
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('db_logger')

class DB:
    """Organizes database operations"""

    def __init__(self):
        """Constructor method"""

        try:
            self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
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
                        last_updated_timestamp TIMESTAMPTZ NOT NULL -- Timestamp of last update
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created spreads table or table already exists")
        except Exception as e:
            logger.error(f"failed to create spreads table. Error: {e}", exc_info=True)

    def insert_NFL_spreads(self, spreads):
        """Inserts provided list of tuples of spreads into DB

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
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.executemany("INSERT INTO spreads (game_ID, Bookie, Matchup_Type, Home_Team, Spread_1, Line_1, Away_Team, Spread_2, Line_2, event_timestamp, last_updated_timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", spreads)
            self.conn.commit()
            logger.info("Successfully inserted data into NFL_spreads table")
        except Exception as e:
            logger.error(f"failed to insert data into NFL_spreads table. Error: {e}, data: {spreads}", exc_info=True)

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
                        last_updated_timestamp TIMESTAMPTZ NOT NULL -- Timestamp of last update
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created moneyline table or table already exists")
        except Exception as e:
            logger.error(f"failed to create moneyline table. Error: {e}", exc_info=True)

    def insert_NFL_moneyline(self, moneyline):
        """Inserts provided list of tuples of moneylines into DB

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
        """

        try:
            with self.conn.cursor() as cursor:
                cursor.executemany("INSERT INTO moneyline (game_ID, Bookie, Matchup_Type, Home_Team, Line_1, Away_Team, Line_2, event_timestamp, last_updated_timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", moneyline)
            self.conn.commit()
            logger.info("Successfully inserted data into moneyline table")
        except Exception as e:
            logger.error(f"Failed to insert data into moneyline table. Error: {e}, data: {moneyline}", exc_info=True)

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
                        last_updated_timestamp TIMESTAMPTZ NOT NULL -- Timestamp of last update
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
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.executemany("INSERT INTO overunder (game_ID, Bookie, Matchup_Type, Home_Team, Away_Team, Over_or_Under_1, Over_Under_Total_1, Over_Under_Line_1, Over_or_Under_2, Over_Under_Total_2, Over_Under_Line_2, event_timestamp, last_updated_timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", overunder)
            self.conn.commit()
            logger.info("Successfully inserted data into overunder table")
        except Exception as e:
            logger.error(f"Failed to insert data into overunder table. Error: {e}, data: {overunder}", exc_info=True)

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
                        Betting_Point TEXT NOT NULL -- this is text because it can either be N/A or a float. Easier to convert text of a float later on.
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created props table or table already exists")
        except Exception as e:
            logger.error(f"error creating props table. Error: {e}", exc_info=True)

    def insert_NFL_props(self, props):
        """Inserts provided pandas dataframe of payments into DB

        Args:
        props (list of tuples): The list of tuples will have the following columns.

                - 'game_ID': Unique ID from OddsAPI for a game/event
                - 'last_updated_timestamp': last time updated              
                - 'Bookie': Name of one of 10 bookies included in OddsAPI
                - 'Prop_Type': Type of prop bet being offered
                - 'Bet_Type': "Yes", "over", or "under" given the prop_type
                - 'Player_Name': name of player in the prop bet,
                - 'Betting_Line': betting line for prop bet          
                - 'Betting_Point': number of yards needed, tds, kicks, etc but N/A if not applicable. Ex. anytime TD would be NA  
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.executemany("INSERT INTO props (game_ID, last_updated_timestamp, Bookie, Prop_Type, Bet_Type, Player_Name, Betting_Line, Betting_Point) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", props)
            self.conn.commit()
            logger.info("Successfully inserted nfl props data into props table")
        except Exception as e:
            logger.error(f"Failed to insert nfl props data into props table. Error: {e}, data: {props}", exc_info=True)
# ### End NFL Props Create, insert, Get, Clear

    ### truncate data from table
    def truncate_table(self, table: str) -> None:
        """Truncates a specified table in the database.

        Args:
            table (str): The name of the table to truncate.
        """
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