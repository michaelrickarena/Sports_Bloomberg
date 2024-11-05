# Sports Betting Data Application

This project is a sports data visualization dashboard that aggregates, processes, and displays betting odds, player stats, and other game-related information from multiple sources. The application is designed to provide an intuitive, user-friendly experience for fans, analysts, and sports bettors, allowing users to filter through different chart options and visualize data across a variety of metrics.

## Project Structure

The application is divided into multiple components, including a backend database, data processing scripts, and a planned React Native frontend for mobile deployment. Below is a breakdown of the key files and directories in the project.

### 1. `db.py`

This script handles database operations, including creating tables and inserting data. The main tables are listed below, stores betting data with fields such as:

- `scores`
- `upcoming_games`
- `spreads`
- `moneyline`
- `overunder`
- `props`

        db.create_db()
        db.create_NFL_scores()
        db.create_NFL_upcoming_games()
        db.create_NFL_spreads()
        db.create_NFL_moneyline()
        db.create_NFL_overunder()
        db.create_NFL_props()

### 2. `odds_api.py`

This script interacts with a sports odds API, fetching and processing data on various sports events, odds, and player statistics. Key functionalities include:

- Making API requests to retrieve betting data.
- Fetching active sports, team odds, scores, events, and player props.
- Filtering data by teams, game times, bookmakers' odds, and prop bets.
- Saving formatted data to CSV files for further analysis.

### 3. `app.py`

This script initializes the main application workflow. It:

- Imports the `Odds_API` class from `odds_api.py` and the `DB` class from `db.py`.
- Loads environment variables using `.env` for API key management.
- Initializes the database connection.

### 4. `build.ps1` - AWS Lambda Deployment Script

The `build.ps1` script automates the deployment process for the sports betting data application on AWS Lambda. This script packages the necessary files and configurations and uploads them to AWS Lambda to enable cloud-based automation.

#### Build Overview Overview

The script performs the following steps:

1. **Environment Setup**: Ensures the required AWS CLI configuration and access credentials are available.
2. **Packaging**: Creates a deployment package, including the code and any required dependencies.
3. **Lambda Deployment**: Uploads the deployment package to AWS Lambda, updating the function code.

#### Prerequisites

- **AWS CLI**: Ensure that the AWS CLI is installed and configured with access keys.
- **AWS Lambda Function**: Set up an AWS Lambda function with the necessary IAM roles and permissions to execute the application.
- **Python Dependencies**: All required dependencies must be installed in a local virtual environment to be packaged with the Lambda function.

### 5. `visualizations/`

Contains Python scripts to visualize and graph data stored in the database. Current visualizations include:

- Graphing moneyline data, filtering by unique `game_ID` and `bookie`.
- Displaying `Line_1` & `Line_2` values in chronological order using `last_updated_timestamp`.
- functionality currently only exists for moneyline table

## Development Progress

### Installation and Environment Management

- Dependencies are managed via `requirements.txt`.
- Sensitive information, like API keys, is stored in a `.env` file and loaded as environment variables.

### Database Setup

- The database has been configured to store NFL spreads, props, moneylines, and overunder odds, with tables managed through the `db.py` script.
- A `truncate` function is used for data clearing.

### Visualization

- Current visualizations are developed using Matplotlib to generate graphs from the database data, allowing visual insights into various betting lines and odds trends.
- This will later be done with javascript and Chart.js on the webapp

### Cloud Setup

- AWS CLI & Lambda are used to automate script execution, eliminating the need to run the application locally at all times.

## Features

- **Database Management:** Efficiently stores NFL spread and odds data for analysis and visualization.
- **API Integration:** Aggregates data from a sports betting API to populate the database.
- **Data Visualization:** Generates charts that display betting trends and odds data.
- **Modular Design:** Flexible script structure, enabling easy additions and modifications for new data sources or features.

## Planned Development

- **Frontend Application**: A React Native app for iOS deployment on the App Store, providing users access to betting insights and data visualizations.
- **Enhanced Data Filtering**: User-selectable filtering options for various data views, making the dashboard highly customizable.
- **Cloud Automation**: Automate data updates and processing scripts using AWS Lambda.
- **Other Sports**: During development only NFL odds are being used, but this will be changed to NFL, NHL, MMA, MLB and NBA once the website goes live.
