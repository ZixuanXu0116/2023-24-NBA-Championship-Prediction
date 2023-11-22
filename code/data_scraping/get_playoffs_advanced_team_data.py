import requests
from bs4 import BeautifulSoup
import pandas as pd
from database import engine
from tqdm import tqdm
import time

def get_soup_from_page(season):


    url = f"https://www.basketball-reference.com/playoffs/NBA_{season}.html#all_per_game_team-opponent"

    response = requests.get(url)

    html = response.text

    soup = BeautifulSoup(html, features="lxml")

    return soup

def get_df_stats(season):

    soup = get_soup_from_page(season)

    table = soup.find('div', id = "all_advanced_team").findAll('tr')
    columns = [th.getText() for th in table[1].findAll('th')][1:]
    team_stats = [[td.getText() for td in table[i].findAll('td')] for i in range(2, 18)]
    
    df = pd.DataFrame(team_stats, columns = columns)
    df['season'] = season
    columns_to_delete = ['\xa0']

    # Drop the specified columns from the DataFrame
    df = df.drop(columns=columns_to_delete)
    df.columns = df.columns[:18].tolist() + [col + '_oppo' for col in df.columns[18:-1]] + [df.columns[-1]]

    return df

requests_per_minute = 15

# Calculate the delay between each request
delay = 60 / requests_per_minute

for season in tqdm(range(2015, 2024), desc='Processing seasons'):
    df = get_df_stats(season)
    df.to_sql('nba_playoffs_team_adv_data_15_23', con=engine, if_exists='append', index=False)
    time.sleep(delay)
