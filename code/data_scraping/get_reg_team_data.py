import requests
from bs4 import BeautifulSoup
import pandas as pd
from database import engine
from tqdm import tqdm
import time

def get_soup_from_page(season):


    url = f"https://www.basketball-reference.com/leagues/NBA_{season}.html#all_per_game_team-opponent"

    response = requests.get(url)

    html = response.text

    soup = BeautifulSoup(html, features="lxml")

    return soup


def get_df_stats(season):

    soup = get_soup_from_page(season)
    table = soup.find('div', id = 'all_per_game_team-opponent').findAll('tr')

    columns = [th.getText() for th in table[0].findAll('th')][1:]
    team_stats = [[td.getText() for td in table[i].findAll('td')] for i in range(1, 31)]

    df = pd.DataFrame(team_stats, columns = columns)
    df['season'] = season
    df = df.dropna(subset=['Team'])

    return df

requests_per_minute = 15

# Calculate the delay between each request
delay = 60 / requests_per_minute

for season in tqdm(range(2015, 2025), desc='Processing seasons'):
    df = get_df_stats(season)
    df.to_sql('nba_regular_team_data_15_24', con=engine, if_exists='append', index=False)
    time.sleep(delay)


