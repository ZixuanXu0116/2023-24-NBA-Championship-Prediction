import pandas as pd
from database import engine
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')

def get_season_schedule(season):

    query = f'SELECT * FROM nba_game_by_game_regular_data WHERE season = {season}'
    demo_df = pd.read_sql_query(query, engine)

    team_start_indices = demo_df.index[(demo_df['Home'] != demo_df['Home'].shift())].tolist()

    '''Delete the first indices, because it's no need to keep it.'''

    if team_start_indices:
        team_start_indices.pop(0)

    '''Append the last row into the indices to let the code get the information of the last game in the dataframe'''

    num_rows = len(demo_df)
    team_start_indices.append(num_rows - 1)

    processed_games = []