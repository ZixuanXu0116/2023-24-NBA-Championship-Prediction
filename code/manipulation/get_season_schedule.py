import pandas as pd
from database import engine
import warnings
from tqdm import tqdm

warnings.filterwarnings('ignore')


def get_season_schedule(season):
    query = f'SELECT * FROM nba_game_by_game_regular_data WHERE season = {season}'
    demo_df = pd.read_sql_query(query, engine)

    team_start_indices = demo_df.index[
        (demo_df['Home'] != demo_df['Home'].shift())
    ].tolist()

    '''Delete the first indices, because it's no need to keep it.'''

    if team_start_indices:
        team_start_indices.pop(0)

    '''Append the last row into the indices to let the code get the information of the last game in the dataframe'''

    num_rows = len(demo_df)
    team_start_indices.append(num_rows - 1)

    processed_games = []

    for i in range(0, len(team_start_indices), 2):
        date = demo_df.loc[team_start_indices[i], 'date']
        team1 = demo_df.loc[team_start_indices[i] - 1, 'Tm']
        team2 = demo_df.loc[team_start_indices[i + 1] - 1, 'Tm']
        result = demo_df.loc[team_start_indices[i + 1] - 1, 'Win']

        processed_games.append(
            {
                'date': date,
                'team1': team1,
                'team2': team2,
                'result': result,
                'season': season,
            }
        )

    final_df = pd.DataFrame(processed_games)

    return final_df


if __name__ == '__main__':
    all_game_schedule = pd.DataFrame()

    for season in tqdm(range(2015, 2025), desc='Processing years'):
        df = get_season_schedule(season)
        all_game_schedule = pd.concat([all_game_schedule, df])

    '''Pushing into databases'''

    all_game_schedule.to_sql(
        'regular_game_schedule_data', con=engine, if_exists='replace', index=False
    )
