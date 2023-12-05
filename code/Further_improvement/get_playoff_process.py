import pandas as pd

def split_win(win):
    if win == 1:
        return 1, 0
    elif win == 0:
        return 0, 1
    else:
        return None, None

def sum_scores(group):
    return pd.Series({
        'Team1_total_score': group['Team1_score'].sum(),
        'Team2_total_score': group['Team2_score'].sum()
    })

# read the detail regular match data
csv_file_path = 'C:/eco395m/temp/playoffs_2017.csv'
demo = pd.read_csv(csv_file_path)

# select all the match result data
temp = demo[['Tm','Home','Win','date']]
temp = temp.drop_duplicates()

# convert the original df into the ['date', 'team1', 'team2','result'] output format
result_columns = ['date', 'team1', 'team2','result']
result = pd.DataFrame(columns=result_columns)
for i in range(int(len(temp)/2)):
    if temp.iloc[2*i, 1] == 0:
        if temp.iloc[2*i+1, 3] == temp.iloc[2*i, 3]:
            result.loc[i] = [temp.iloc[2*i, 3], temp.iloc[2*i, 0], temp.iloc[2*i+1, 0], temp.iloc[2*i, 2]]
result = result.sort_values(by='date')

# Adjust the order of all teams and separate the score for each team
df = pd.DataFrame(result)
df['Team1'] = df.apply(lambda row: sorted([row['team1'], row['team2']])[0], axis=1)
df['Team2'] = df.apply(lambda row: sorted([row['team1'], row['team2']])[1], axis=1)
df['Win'] = df.apply(lambda row: row['result'] if row['team1'] == sorted([row['team1'], row['team2']])[0] else 1 - row['result'], axis=1)

# Sum the score for each round
df_sorted = df.sort_values(by=['Team1', 'Team2'])
df_sorted[['Team1_score', 'Team2_score']] = df_sorted['Win'].apply(split_win).apply(pd.Series)
result_df = df_sorted.groupby(['Team1', 'Team2']).apply(sum_scores).reset_index()

# Calculate the appear times of each group and assign the round to each match
team_counts = pd.concat([result_df['Team1'], result_df['Team2']]).value_counts()
result_df['Round'] = result_df.apply(lambda row: min(team_counts[row['Team1']], team_counts[row['Team2']]), axis=1)
plan_df = result_df.sort_values(by='Round')
plan_df = plan_df[['Round','Team1','Team2','Team1_total_score','Team2_total_score']]

# export the output
export_path1 = 'C:/eco395m/temp/playoff_process.csv'
export_path2 = 'C:/eco395m/temp/playoff_round_process.csv'
result.to_csv(export_path1, index=False)
plan_df.to_csv(export_path2, index=False)