import pandas as pd
from database import engine

# read the regular_normal_player_data and choose the year
team_data_query = 'SELECT * FROM nba_regular_normal_player_data WHERE season = 2016'
playernormal = pd.read_sql_query(team_data_query,engine)
playernormal['Player'] = playernormal['Player'].str.replace('*', '')

# read the detail regular match data
csv_file_path = 'C:/eco395m/temp/demo_2016.csv'
demo = pd.read_csv(csv_file_path)

# select the first 20 games for each team
mask = demo.groupby('Tm')['date'].transform(lambda x: x.isin(x.unique()[20:]))
filtered_demo = demo[mask]

# calculate the average score for each player
average_plus_minus = filtered_demo.groupby('Player')['+/-'].mean().reset_index()
temp = pd.merge(playernormal, average_plus_minus, on='Player', how='left')
temp['+/-'] = temp['+/-'].fillna(0)
result = temp[['Player', 'Tm', 'season', '+/-']]
result.rename(columns={'+/-': 'Ave +/-'}, inplace=True)

# export the result
export_path = 'C:/eco395m/temp/ave_score.csv'
result.to_csv(export_path, index=False)




