from database import engine
from tqdm import tqdm
import time
from get_NBA_data import get_df_stats
import os

requests_per_minute = 15
delay = 60 / requests_per_minute

def update_data(target_type, data_type):

    delete_statement = f'DELETE FROM nba_regular_{data_type}_{target_type}_data WHERE season = 2024'
    with engine.connect() as conn:
        conn.execute(delete_statement)
    
    df = get_df_stats(2024, 'regular', target_type, data_type)
    df.to_sql(f'nba_regular_{data_type}_{target_type}_data', \
            con=engine, if_exists='append', index=False)
    time.sleep(delay)
    progress_bar.update(1)

    return ''
    
new_directory = os.path.join(os.getcwd(), "code", "data_scraping")
os.chdir(new_directory)

total_iterations = 2*2*1
progress_bar = tqdm(total=total_iterations, desc="Processing")

for target_type in ['player', 'team']:
        for data_type in ['normal', 'advanced']:
            update_data(target_type, data_type)
