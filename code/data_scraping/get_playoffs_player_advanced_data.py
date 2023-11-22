import requests
from bs4 import BeautifulSoup
import pandas as pd
from database import engine
from tqdm import tqdm
import os
import time

def get_soup_from_page(season):


    url = f"https://www.basketball-reference.com/playoffs/NBA_{season}_advanced.html"

    response = requests.get(url)

    html = response.text

    soup = BeautifulSoup(html, features="lxml")

    return soup

def get_df_stats(season):

    soup = get_soup_from_page(season)
    table = soup.findAll('tr', limit = 2)

    columns = [th.getText() for th in table[0].findAll('th')][1:]
    rows = soup.findAll('tr')[1:]

    player_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

    BASE_DIR = "data"
    CSV_PATH = os.path.join(BASE_DIR, f"playoffs_player_results_{season}.csv")


    df = pd.DataFrame(player_stats, columns = columns)
    df['season'] = season

    df.to_csv(CSV_PATH, index = False)

    df = pd.read_csv(CSV_PATH)
    df_filled = df.fillna(0)
    df_final = df_filled[df_filled['Player'] != 0]


    return df_final


requests_per_minute = 15

# Calculate the delay between each request
delay = 60 / requests_per_minute

for season in tqdm(range(2015, 2024), desc='Processing seasons'):
    df = get_df_stats(season)
    df.to_sql('nba_playoffs_advanced_player_data_15_24', con=engine, if_exists='append', index=False)
    time.sleep(delay)