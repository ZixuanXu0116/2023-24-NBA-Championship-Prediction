import pandas as pd
from database import engine

def get_feature_matrix(schedule_df, df):

    df_sorted = df.groupby('Tm', group_keys=False).apply(lambda x: x.sort_values(by='MP', ascending=False))
    df_sorted = df_sorted[df_sorted['Tm'] != 'TOT']

    '''Selecting the top 9 players based on average minutes played'''

    players_df = df_sorted.groupby('Tm').head(9)


    result_df = pd.concat([schedule_df.apply(lambda x: players_df.loc[players_df['Tm'] == x['team1'], 
                        ['Pos', 'MP', 'Age', 'shooting', 'peri_def', 'playmaker', 
                        'pro_rim', 'efficiency', 'influence', 'scoring']].values.flatten(), axis=1, result_type='expand'),

                        schedule_df.apply(lambda x: players_df.loc[players_df['Tm'] == x['team2'], 
                        ['Pos', 'MP', 'Age', 'shooting', 'peri_def', 'playmaker', 
                        'pro_rim', 'efficiency', 'influence', 'scoring']].values.flatten(), axis=1, result_type='expand')],
                        axis=1)

    query = f'SELECT * FROM real_total_feature_matrix_data WHERE season = 2023'
    use_name_df = pd.read_sql_query(query, engine)

    result_df.columns = use_name_df.columns[12:-3].tolist()

    return result_df
