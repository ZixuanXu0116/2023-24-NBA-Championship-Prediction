import time
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from database import engine
from tqdm import tqdm


def get_soup_from_page(season, game_type, target_type, data_type):

    '''
    Scraping soup from 'basketball-reference.com'
    Parameters: season: int , game_type, target_type and data_type: str
    Examples: 'season = 2022' refer to the year in which the playoffs occurred, 
    namely the season that Warriors won the championship.
    Restrictions: game_type can only be 'regular' or 'playoffs', 
                target_type can only be 'player' or 'team',
                data_type can only be 'normal' or 'advanced'.
    '''

    url1 = 'leagues' if game_type == 'regular' else 'playoffs'

    if target_type == 'player' and data_type == 'normal':
        url2 = '_per_game' 
    elif target_type == 'player' and data_type == 'advanced':
        url2 = '_advanced'
    else:
        url2 = ''

    url3 = '#all_per_game_team-opponent' if target_type == 'team' else ''

    url = "https://www.basketball-reference.com/" + url1 + f"/NBA_{season}" + url2 + '.html' + url3

    response = requests.get(url)

    html = response.text

    soup = BeautifulSoup(html, features="lxml")

    return soup

def mk_csv_dir(season, game_type, data_type):

    '''
    Make a Directory to keep some CSV files, 
    more convenient for doing some data cleaning.
    Parameters: data_type: str (can only be 'normal' or 'advanced')
    
    '''

    BASE_DIR = "data"
    CSV_PATH = os.path.join(BASE_DIR, f"{game_type}_{data_type}_{season}.csv")
    os.makedirs(BASE_DIR, exist_ok=True)

    return CSV_PATH


def get_df_stats(season, game_type, target_type, data_type):

    '''Extract the stats table into a dataframe, and different combinations of 
       game_type, target_type, and data_type may need different codes to get the correct answer'''

    soup = get_soup_from_page(season, game_type, target_type, data_type)

    '''Get the needed table from the website'''

    if target_type == 'player':
        table = soup.findAll('tr')

    elif (target_type, data_type) == ('team', 'normal'):
        table = soup.find('div', id = 'all_per_game_team-opponent').findAll('tr')

    elif (target_type, data_type) == ('team', 'advanced'):
        table = soup.find('div', id = "all_advanced_team").findAll('tr')


    '''Get Headers for our table'''
    columns = [th.getText() for th in table[1 \
    if (target_type, data_type) == ('team', 'advanced') else 0].findAll('th')][1:]


    '''Get the stats of the table'''
    if target_type == 'player':
        stats = [[td.getText() for td in table[1:][i].findAll('td')] for i in range(len(table[1:]))]

    elif (game_type, target_type, data_type) == ('regular', 'team', 'normal'):
        stats = [[td.getText() for td in table[i].findAll('td')] for i in range(1, 31)]

    elif (game_type, target_type, data_type) == ('regular', 'team', 'advanced'):
        stats = [[td.getText() for td in table[i].findAll('td')] for i in range(2, 32)]

    elif (game_type, target_type, data_type) == ('playoffs', 'team', 'normal'):
        stats = [[td.getText() for td in table[i].findAll('td')] for i in range(1, 17)]

    elif (game_type, target_type, data_type) == ('playoffs', 'team', 'advanced'):
        stats = [[td.getText() for td in table[i].findAll('td')] for i in range(2, 18)]

    
    '''Convert the data into Pandas Dataframe and add a column: 'the year of season' to the df'''
    df = pd.DataFrame(stats, columns = columns)
    df['season'] = season


    '''Data Cleaning for the dataframe'''
    if (game_type, target_type, data_type) == ('regular', 'player', 'normal'):

        CSV_PATH = mk_csv_dir(season, game_type, data_type)
        df.to_csv(CSV_PATH, index = False)

        df = pd.read_csv(CSV_PATH)
        df_filled = df.fillna(0)
        df_final = df_filled[df_filled['Player'] != 0]

    elif (game_type, target_type, data_type) == ('regular', 'player', 'advanced'):

        columns_to_delete = ['\xa0']
        df = df.drop(columns=columns_to_delete)

        CSV_PATH = mk_csv_dir(season, game_type, data_type)
        df.to_csv(CSV_PATH, index = False)

        df = pd.read_csv(CSV_PATH)
        df_filled = df.fillna(0)
        df_final = df_filled[df_filled['Player'] != 0]
    
    elif (game_type, target_type, data_type) == ('regular', 'team', 'normal'):

        df_final = df.dropna(subset=['Team'])

    elif (game_type, target_type, data_type) == ('regular', 'team', 'advanced'):

        columns_to_delete = ['\xa0']
        df = df.drop(columns=columns_to_delete)
        df.columns = df.columns[:-8].tolist() + [col + '_oppo' for col in df.columns[-8:-4]] + df.columns[-4:].tolist()
        df_final = df

    elif (game_type, target_type, data_type) == ('playoffs', 'player', 'normal'):

        CSV_PATH = mk_csv_dir(season, game_type, data_type)
        df.to_csv(CSV_PATH, index = False)
        df = pd.read_csv(CSV_PATH)

        df_filled = df.fillna(0)
        df_final = df_filled[df_filled['Player'] != 0]

    elif (game_type, target_type, data_type) == ('playoffs', 'player', 'advanced'):

        CSV_PATH = mk_csv_dir(season, game_type, data_type)
        df.to_csv(CSV_PATH, index = False)
        df = pd.read_csv(CSV_PATH)

        df_filled = df.fillna(0)
        df_final = df_filled[df_filled['Player'] != 0]
    
    elif (game_type, target_type, data_type) == ('playoffs', 'team', 'normal'):

        df_final = df

    elif (game_type, target_type, data_type) == ('playoffs', 'team', 'advanced'):

        columns_to_delete = ['\xa0']
        df = df.drop(columns=columns_to_delete)

        df.columns = df.columns[:18].tolist() + [col + '_oppo' for col in df.columns[18:-1]] + [df.columns[-1]]
        df_final = df
    
    return df_final





if __name__ == "__main__":
    
    '''Set a request limit to avoid issues'''
    requests_per_minute = 15
    delay = 60 / requests_per_minute


    '''Create the tqdm instance'''
    total_iterations = 4 * (2024 - 2015) + 4 * (2025 - 2015)
    progress_bar = tqdm(total=total_iterations, desc="Processing")


    new_directory = os.path.join(os.getcwd(), "code", "scraping")
    os.chdir(new_directory)

    for target_type in ['player', 'team']:
        for data_type in ['normal', 'advanced']:
            for game_type in ['regular', 'playoffs']:

                if game_type == 'regular':
                    for season in range(2015, 2025):
                        df = get_df_stats(season, game_type, target_type, data_type)
                        df.to_sql(f'nba_{game_type}_{data_type}_{target_type}_data', \
                        con=engine, if_exists='append', index=False)
                        time.sleep(delay)
                        progress_bar.update(1)

                elif game_type == 'playoffs':
                    for season in range(2015, 2024):
                        df = get_df_stats(season, game_type, target_type, data_type)
                        df.to_sql(f'nba_{game_type}_{data_type}_{target_type}_data', \
                        con=engine, if_exists='append', index=False)
                        time.sleep(delay)
                        progress_bar.update(1)

