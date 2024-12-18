"""
db.py - Contains functionality to interact with our Azure SQL DB
"""
import psycopg2
import os
from pathlib import Path
import logging

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
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
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
                        last_updated_timestamp TIMESTAMPTZ NOT NULL, -- Timestamp of last update
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
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

    def get_moneyline_data(self):
        """Fetch moneyline data from the database."""
        query = """
            SELECT game_ID, bookie, home_team, line_1, away_team, line_2, last_updated_timestamp
            FROM moneyline
            ORDER BY last_updated_timestamp;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        return data



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
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.executemany("INSERT INTO overunder (game_ID, Bookie, Matchup_Type, Home_Team, Away_Team, Over_or_Under_1, Over_Under_Total_1, Over_Under_Line_1, Over_or_Under_2, Over_Under_Total_2, Over_Under_Line_2, event_timestamp, last_updated_timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", overunder)
            self.conn.commit()
            logger.info("Successfully inserted data into overunder table")
        except Exception as e:
            logger.error(f"Failed to insert data into overunder table. Error: {e}, data: {overunder}", exc_info=True)


    def get_overunder_data(self):
        """Fetch moneyline data from the database."""
        query = """
            SELECT game_ID, bookie, home_team, line_1, away_team, line_2, last_updated_timestamp
            FROM moneyline
            ORDER BY last_updated_timestamp;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        return data


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
                        FOREIGN KEY (game_ID) REFERENCES scores(game_ID) ON DELETE CASCADE
                    );
                    """
                )
            self.conn.commit()
            logger.info("Successfully created props table or table already exists")
        except Exception as e:
            logger.error(f"error creating props table. Error: {e}", exc_info=True)


    def insert_NFL_props(self, props):
        """Inserts provided list of tuples of props into DB

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
                for prop in props:
                    cursor.execute("INSERT INTO props (game_ID, last_updated_timestamp, Bookie, Prop_Type, Bet_Type, Player_Name, Betting_Line, Betting_Point) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", prop)
            self.conn.commit()
            logger.info("Successfully inserted nfl props data into props table")
        except Exception as e:
            logger.error(f"Failed to insert nfl props data into props table. Error: {e}, data: {props}", exc_info=True)

#### End NFL Props Create, insert, Get, Clear


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


    def delete_games_with_false_status(self):
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


# ### End NFL Props Create, insert, Get, Clear


    def get_arb_data(self):
        """Fetch arb from db"""
        query = """
            WITH latest AS (
                SELECT game_id, bookie, MAX(last_updated_timestamp) AS latest_dt
                FROM moneyline
                GROUP BY game_id, bookie
            ),
            latest_detailed AS (
                SELECT l.game_id, l.bookie, l.latest_dt, m.line_1, m.line_2
                FROM latest AS l
                LEFT JOIN moneyline AS m
                ON l.game_id = m.game_id AND l.bookie = m.bookie AND l.latest_dt = m.last_updated_timestamp 
            ),
            line1_max AS (
                SELECT l.game_id, l.line_1, ld.bookie
                FROM (
                    SELECT game_id, MAX(line_1) AS line_1
                    FROM latest_detailed
                    GROUP BY game_id
                ) AS l
                LEFT JOIN latest_detailed AS ld
                ON l.game_id = ld.game_id AND l.line_1 = ld.line_1 
            ),
            line2_max AS (
                SELECT l.game_id, l.line_2, ld.bookie
                FROM (
                    SELECT game_id, MAX(line_2) AS line_2
                    FROM latest_detailed
                    GROUP BY game_id
                ) AS l
                LEFT JOIN latest_detailed AS ld
                ON l.game_id = ld.game_id AND l.line_2 = ld.line_2
            ),
            arb1 AS (
                SELECT * FROM line1_max
            ),
            arb2 AS (
                SELECT * FROM line2_max
            )
            SELECT * FROM arb1
            UNION ALL
            SELECT * FROM arb2;

        """
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            print(data)
        return data



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