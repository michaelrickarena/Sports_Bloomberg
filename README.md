# Sports Data Application

## Overview

This project is a sports data application that aggregates data from various sources and provides insights on NFL games, including scores, odds, and player statistics. The application fetches data from an external API and stores it in a PostgreSQL database.

## Features

- Fetches NFL game scores, spreads, money lines, and player prop bets.
- Stores data in a PostgreSQL database with proper schema and foreign key relationships.
- Supports insertion of new data while avoiding duplicates based on `game_ID` and `game_status`.
- Deletes records based on game status conditions.

## Technology Stack

- **Backend:** Python
- **Database:** PostgreSQL
- **Libraries:** psycopg2, dotenv, logging
- **Data Visualization:** (to be determined in the front end)

## Project Structure

src/ ├── data/ │ └── odds_api.py # Contains functions to fetch and filter data from the odds API └── utils/ └── db.py # Contains database management functions, including table creation and data insertion main.py # Main script that orchestrates data fetching and database operations logging.conf # Configuration file for logging

## Database Schema

### Tables

- **scores**
  - `id`: SERIAL PRIMARY KEY
  - `game_ID`: VARCHAR(255) UNIQUE
  - `sport_title`: TEXT NOT NULL
  - `game_time`: TIMESTAMPTZ NOT NULL
  - `game_status`: TEXT NOT NULL
  - `last_updated_timestamp`: TIMESTAMPTZ
  - `team1`: TEXT
  - `score1`: INT
  - `team2`: TEXT
  - `score2`: INT

### Foreign Keys

- The `scores` table has foreign key relationships with other tables (e.g., spreads, money lines) to maintain data integrity.

## Setup Instructions

1. Clone the repository.
2. Create a PostgreSQL database and update your database connection settings in the `.env` file.
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Database Schema

### Tables

- **scores**
  - `id`: SERIAL PRIMARY KEY
  - `game_ID`: VARCHAR(255) UNIQUE
  - `sport_title`: TEXT NOT NULL
  - `game_time`: TIMESTAMPTZ NOT NULL
  - `game_status`: TEXT NOT NULL
  - `last_updated_timestamp`: TIMESTAMPTZ
  - `team1`: TEXT
  - `score1`: INT
  - `team2`: TEXT
  - `score2`: INT

### Foreign Keys

- The `scores` table has foreign key relationships with other tables (e.g., spreads, money lines) to maintain data integrity.

## Setup Instructions

1. Clone the repository.
2. Create a PostgreSQL database and update your database connection settings in the `.env` file.
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

Run the main.py script to start fetching data and populating the database.
Future Work
Develop the front end using a framework like React Native to visualize the data and provide user interactions.
Implement additional features such as user authentication, advanced analytics, and more.
License
This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to modify any sections to better suit your project!
