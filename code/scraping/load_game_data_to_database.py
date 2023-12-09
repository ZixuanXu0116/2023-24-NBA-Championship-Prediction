import os
import warnings
import re
from datetime import date
from tqdm import tqdm
import pandas as pd
from database import engine
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')

new_directory = os.path.join(os.getcwd(), "code", "scraping")
os.chdir(new_directory)
DATA_DIR = os.path.join(os.getcwd(), 'data')

def get_subfolders(folder_path):
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    return subfolders

def clean_html(box_score):
    """ Info:
        This function will clean the html file and return a soup object
        ---------------------------------------------------------------
        Input:
        box_score: html file
        ---------------------------------------------------------------
        Output:
        soup: BeautifulSoup object
        """
    
    with open(box_score, 'r', encoding="utf-8", errors='ignore') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, features="lxml")
    [f.decompose() for f in soup.select('tr.over_header')]
    [f.decompose() for f in soup.select('tr.thead')]

    return soup


def get_score_line(soup):
    """ 
        Input:
        soup: BeautifulSoup object
        ---------------------------------------------------------------
        Output:
        score_row: Dataframe with the score line of the game with total points.  """

    score_row = pd.read_html(str(soup), attrs={'id': 'line_score'})[0]

    try:
        score_row.columns.values[0] = 'Team' 
        score_row.columns.values[-1] = 'Total' 
        score_row = score_row[['Team', 'Total']] 
    
    except KeyError:
        score_row.rename(columns={0: 'Team', 'T': 'Total'}, inplace=True)
        score_row = score_row[['Team', 'Total']]

    return score_row

def get_stats(soup, team, stat):
    """
        Input:
        soup: BeautifulSoup object
        team: string with the team name
        stat: string with the type of stats (basic or advanced)
        ---------------------------------------------------------------
        Output:
        df: Dataframe with the stats of the game. 
    
    """
    
    df = pd.read_html(str(soup), attrs={'id':f'box-{team}-game-{stat}'}, index_col=0)[0].fillna(0)

    return df


def get_game_season(soup):
    """ 
        Input:
        soup: BeautifulSoup object
        ---------------------------------------------------------------
        Output:
        Int: the season of the game.  
    """
    id = soup.select('#bottom_nav_container')[0]
    string= id.find_all('u')[3]
    season = re.findall(r'\d{4}-\d{2}', str(string))[0]
    season = int(season[0:2] + season[-2:])

    return season



def process_team_stats(soup, team, home):

    basic_df = get_stats(soup, team, 'basic')
    basic_df['Tm'] = team

    selected_df = basic_df[
        (basic_df['MP'] != 'Did Not Play') &
        (basic_df['MP'] != 'Not With Team') &
        (basic_df['MP'] != 'Did Not Dress') &
        (basic_df['MP'] != 'Player Suspended')
    ].iloc[:-1, :].drop('MP', axis=1)


    selected_df.reset_index(inplace=True)
    selected_df.rename(columns={'Starters': 'Player'}, inplace=True)

    selected_df['Home'] = home
    selected_df['Win'] = int(score_row['Total'][home] >= max(score_row['Total']))

    season = get_game_season(soup)
    selected_df['season'] = season

    return selected_df


df = pd.DataFrame()
SCORES_DIR = get_subfolders(DATA_DIR)

for folder_name in SCORES_DIR:

    if folder_name.startswith('scores_20'):

        score_dir = os.listdir(os.path.join(DATA_DIR, folder_name))

        for file in tqdm(score_dir, desc='scraping Htmls', unit='file'):

            path = os.path.join(os.path.join(DATA_DIR, folder_name), file)

            date = file[0:8]
            soup = clean_html(path)
            score_row = get_score_line(soup)

            team_dfs = [process_team_stats(soup, team, i)\
                        for i, team in enumerate(score_row['Team'])]

            final_df = pd.concat(team_dfs, ignore_index=True)
            final_df['date'] = date

            df = df.append(final_df).reset_index(drop=True)


df.to_sql('nba_game_by_game_regular_data', con=engine, if_exists='replace', index=False)
