import os
from bs4 import BeautifulSoup
import pandas as pd
from database import engine
from datetime import datetime

# Function to convert the date format
print('Starting Process get_game_schedule')
def convert_date_format(date_str):
    try:
        # Convert to datetime object
        date_obj = datetime.strptime(date_str, '%a, %b %d, %Y')
        # Format as 'YYYYMMDD'
        return date_obj.strftime('%Y%m%d')
    except ValueError:
        return date_str

new_directory = os.path.join(os.getcwd(), 'code', 'scraping')
os.chdir(new_directory)

DATA_DIR = 'data'
STANDINGS_DIR = os.path.join(DATA_DIR, 'standings')
SCORES_DIR = os.path.join(DATA_DIR, 'scores')
os.makedirs(STANDINGS_DIR, exist_ok=True)
os.makedirs(SCORES_DIR, exist_ok=True)

standing_file_names = os.listdir(STANDINGS_DIR)

team_abbreviations = {
    'Atlanta Hawks': 'ATL',
    'Boston Celtics': 'BOS',
    'Brooklyn Nets': 'BRK',
    'Charlotte Hornets': 'CHO',
    'Chicago Bulls': 'CHI',
    'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL',
    'Denver Nuggets': 'DEN',
    'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW',
    'Houston Rockets': 'HOU',
    'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL',
    'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL',
    'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP',
    'New York Knicks': 'NYK',
    'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL',
    'Philadelphia 76ers': 'PHI',
    'Phoenix Suns': 'PHO',
    'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC',
    'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR',
    'Utah Jazz': 'UTA',
    'Washington Wizards': 'WAS'
}

games_info = []
for name in standing_file_names:
    file_path = os.path.join(STANDINGS_DIR, name)
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all game rows
    game_rows = soup.find_all('tr')

    # Extract game date, home team, and visitor team for each game
    for row in game_rows:
        game_date_tag = row.find('th', {'data-stat': 'date_game'})
        visitor_team_tag = row.find('td', {'data-stat': 'visitor_team_name'})
        home_team_tag = row.find('td', {'data-stat': 'home_team_name'})

        # Check if the tags are found (to avoid header rows, etc.)
        if game_date_tag and visitor_team_tag and home_team_tag:
            game_date = game_date_tag.text.strip()
            visitor_team_name = visitor_team_tag.text.strip()
            home_team_name = home_team_tag.text.strip()

            games_info.append({
                'game_date': game_date,
                'visitor_team': visitor_team_name,
                'home_team': home_team_name
            })

df_games = pd.DataFrame(games_info)

# Rename columns
df_games.rename(columns={'game_date': 'date', 'visitor_team': 'team1', 'home_team': 'team2'}, inplace=True)
df_games['date'] = df_games['date'].apply(convert_date_format)

# Abbreviate team names
df_games['team1'] = df_games['team1'].map(team_abbreviations)
df_games['team2'] = df_games['team2'].map(team_abbreviations)
df_games['date'] = df_games['date'].astype(int)
df_games['result'] = 0
df_games['season'] = 2024

df_games.to_sql(
        'regular_game_schedule_data', con=engine, if_exists='append', index=False
    )





