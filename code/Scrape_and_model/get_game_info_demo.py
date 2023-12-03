import os 
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import date
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

pd.set_option('mode.chained_assignment', None)

DATA_DIR = os.path.join(os.getcwd(), 'data')
SCORE_DIR = os.path.join(DATA_DIR, 'scores')


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
    
    df = pd.read_html(str(soup), attrs={'id':f'box-{team}-game-{stat}'}, index_col=0)[0].fillna(0) # indexcol will be the players column

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
    string= id.find_all('u')[3] # this u tag has the exact season, so we use regex to extract it
    season = re.findall(r'\d{4}-\d{2}', str(string))[0]
    season = int(season[0:2] + season[-2:])

    return season



def process_team_stats(soup, team, home, win):

    basic_df = get_stats(soup, team, 'basic')
    basic_df['Tm'] = team

    selected_df = basic_df[basic_df['MP'] != 'Did Not Play'].iloc[:-1, [0, -1]].drop('MP', axis=1)
    # selected_df['MP'] = selected_df['MP'].apply(lambda x: round(int(x.split(':')[0]) + int(x.split(':')[1])/60, 1))

    selected_df.reset_index(inplace=True)
    selected_df.rename(columns={'Starters': 'Player'}, inplace=True)

    selected_df['Home'] = home
    selected_df['Win'] = int(score_row['Total'][home] >= max(score_row['Total']))

    season = get_game_season(soup)
    selected_df['season'] = season

    return selected_df


df = pd.DataFrame()
files = os.listdir(SCORE_DIR)

for file in tqdm(files, desc='scraping Htmls', unit='file'):

    date = file[0:8]
    soup = clean_html(os.path.join(SCORE_DIR, file))
    score_row = get_score_line(soup)

    team_dfs = [process_team_stats(soup, team, i, int(score_row['Total'][i] >= max(score_row['Total'])))\
                for i, team in enumerate(score_row['Team'])]

    final_df = pd.concat(team_dfs, ignore_index=True)
    final_df['date'] = date

    df = df.append(final_df).reset_index(drop=True)
    

df.to_csv(os.path.join(os.getcwd(), 'demo.csv'), index=False)
