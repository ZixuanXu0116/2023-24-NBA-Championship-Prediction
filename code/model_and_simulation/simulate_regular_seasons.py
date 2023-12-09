import pandas as pd
import numpy as np
from database import engine
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from generate_playin_1st_round_result import generate_new_df_part
from generate_feature_matrix import get_feature_matrix
from get_result_two_teams_regular import get_single_game_result
import warnings
warnings.filterwarnings('ignore')

query_train = f'SELECT * FROM real_total_feature_matrix_data'
df_train = pd.read_sql_query(query_train, engine)

query_test = f'SELECT * FROM core_players_matrix_2023_regular'
df_test = pd.read_sql_query(query_test, engine)

season = 2023
query_schedule = f'SELECT * FROM regular_game_schedule_data WHERE season = {season}'
schedule_df = pd.read_sql_query(query_schedule, engine)

X_train = df_train[df_train['season'].isin(range(2015, 2023))].iloc[:, 12:-3]
y_train = df_train[df_train['season'].isin(range(2015, 2023))]['result']

X_test = df_test.iloc[:, :-1]
y_test = df_test['result']

model = RandomForestClassifier()
model.fit(X_train, y_train)

'''Make predictions on the test set'''

num_iterations = 999

'''Store the predictions for each iteration'''

all_predictions = np.zeros((X_test.shape[0], num_iterations))

'''Run the model multiple times for each sample'''

for i in tqdm(range(num_iterations), desc="Running Iterations", unit="iteration"):
    model.fit(X_train, y_train)
    y_pred_iteration = model.predict(X_test)
    all_predictions[:, i] = y_pred_iteration

'''Make the final prediction based on the majority'''

final_predictions = np.mean(all_predictions, axis=1) > 0.5
final_predictions = final_predictions.astype(int) 
print(final_predictions)
y_pred = final_predictions

'''Evaluate the model'''

accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print('Accuracy:', accuracy)
print('Classification Report:\n', report)

schedule_df['result_pred'] = y_pred

'''
Define Eastern Conference and Western Conference teams

'''

eastern_teams = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DET', 'IND', 
                 'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS']

western_teams = ['DAL', 'DEN', 'GSW', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN', 
                'NOP', 'OKC', 'PHO', 'POR', 'SAC', 'SAS', 'UTA']

eastern_wins = {}
eastern_losses = {}
western_wins = {}
western_losses = {}


for _, row in schedule_df.iterrows():
    team1 = row['team1']
    team2 = row['team2']
    result_pred = row['result_pred']

    '''Update wins and losses based on the predicted result and conference'''

    if team1 in eastern_teams:
        eastern_wins[team1] = eastern_wins.get(team1, 0) + (1 - result_pred)
        eastern_losses[team1] = eastern_losses.get(team1, 0) + result_pred
    elif team1 in western_teams:
        western_wins[team1] = western_wins.get(team1, 0) + (1 - result_pred)
        western_losses[team1] = western_losses.get(team1, 0) + result_pred

    if team2 in eastern_teams:
        eastern_wins[team2] = eastern_wins.get(team2, 0) + result_pred
        eastern_losses[team2] = eastern_losses.get(team2, 0) + (1 - result_pred)
    elif team2 in western_teams:
        western_wins[team2] = western_wins.get(team2, 0) + result_pred
        western_losses[team2] = western_losses.get(team2, 0) + (1 - result_pred)

'''
Convert the results to DataFrames for each conference

'''




eastern_results_df = pd.DataFrame({'Team': eastern_teams,
                                   'Wins': [eastern_wins.get(team, 0) for team in eastern_teams],
                                   'Losses': [eastern_losses.get(team, 0) for team in eastern_teams]})

western_results_df = pd.DataFrame({'Team': western_teams,
                                   'Wins': [western_wins.get(team, 0) for team in western_teams],
                                   'Losses': [western_losses.get(team, 0) for team in western_teams]})



'''
Add a new column for ranking within each conference
'''

eastern_results_df['Rank'] = eastern_results_df['Wins'].rank(ascending=False, method='min').astype(int)
western_results_df['Rank'] = western_results_df['Wins'].rank(ascending=False, method='min').astype(int)

'''
Sort the DataFrames based on the number of wins

'''

eastern_results_df = eastern_results_df.sort_values(by='Wins', ascending=False)
western_results_df = western_results_df.sort_values(by='Wins', ascending=False)


print("Eastern Conference Results:")
print(eastern_results_df)
print('-----------------------------------------------------------')
print("\nWestern Conference Results:")
print(western_results_df)


playin_range = range(6, 10)

# Identify the teams that would be in the play-in games
eastern_playin_teams = eastern_results_df.iloc[playin_range].copy()
western_playin_teams = western_results_df.iloc[playin_range].copy()
print('-----------------------------------------------------------')
# Display the teams that would be in the play-in games
print("Eastern Conference Play-in Teams:")
print(eastern_playin_teams)
print('-----------------------------------------------------------')
print("\nWestern Conference Play-in Teams:")
print(western_playin_teams)


team1_data = {'team': [western_playin_teams.iloc[1, :]['Team'], western_playin_teams.iloc[3, :]['Team'],
                       eastern_playin_teams.iloc[1, :]['Team'], eastern_playin_teams.iloc[3, :]['Team']]}

team2_data = {'team': [western_playin_teams.iloc[0, :]['Team'], western_playin_teams.iloc[2, :]['Team'],
                       eastern_playin_teams.iloc[0, :]['Team'], eastern_playin_teams.iloc[2, :]['Team']]}

query = f'SELECT * FROM regular_predicted_player_matrix_data WHERE season = 2023'
matrix_df = pd.read_sql_query(query, engine)

playin_round_one = pd.DataFrame({'team1': team1_data['team'], 'team2': team2_data['team']})

playin_round_one_matrix = get_feature_matrix(playin_round_one, matrix_df)

y_pred_playin_round_one = model.predict(playin_round_one_matrix)

playin_round_one['result_pred'] = y_pred_playin_round_one
print('-----------------------------------------------------------')
round_one_result = generate_new_df_part(playin_round_one)
print(round_one_result)
print('-----------------------------------------------------------')
west_team1 = str(input('Please tell me the temp West 9 team: '))
west_team2 = str(input('Please tell me the temp West 8 team: '))
east_team1 = str(input('Please tell me the temp East 9 team: '))
east_team2 = str(input('Please tell me the temp East 8 team: '))

print('------------------------------------------------------------')
print(f'The West playin_round_two is {west_team1} - {west_team2}')
print(f'The East playin_round_two is {east_team1} - {east_team2}')
print('------------------------------------------------------------')

result_west = get_single_game_result(west_team1, west_team2, model)
result_east = get_single_game_result(east_team1, east_team2, model)

eight_list = []
if result_west == 1:
    print(f'{west_team2} makes the playoffs as West 8, {west_team1} goes home')
    eight_list.append(west_team2)
else:
    print(f'{west_team1} makes the playoffs as West 8, {west_team2} goes home')
    eight_list.append(west_team1)

if result_east == 1:
    print(f'{east_team2} makes the playoffs as East 8, {east_team1} goes home')
    eight_list.append(east_team2)
else:
    print(f'{east_team1} makes the playoffs as East 8, {east_team2} goes home')
    eight_list.append(east_team1)


top_six_west = list(western_results_df.iloc[0:6, :]['Team'])
top_six_east = list(eastern_results_df.iloc[0:6, :]['Team'])

top_wins_west = list(western_results_df.iloc[0:6, :]['Wins'].tolist())
top_wins_east = list(eastern_results_df.iloc[0:6, :]['Wins'].tolist())

west_seven = round_one_result.iloc[0]['team'][-3:]
east_seven = round_one_result.iloc[4]['team'][-3:]

seven_wins_west = western_results_df[western_results_df['Team'] == west_seven]['Wins'].iloc[0]
seven_wins_east = eastern_results_df[eastern_results_df['Team'] == east_seven]['Wins'].iloc[0]

west_eight = eight_list[0]
east_eight = eight_list[1]

eight_wins_west = western_results_df[western_results_df['Team'] == west_eight]['Wins'].iloc[0]
eight_wins_east = eastern_results_df[eastern_results_df['Team'] == east_eight]['Wins'].iloc[0]

top_six_west += [west_seven, west_eight]
top_six_east += [east_seven, east_eight]

top_wins_west += [seven_wins_west, eight_wins_west]
top_wins_east += [seven_wins_east, eight_wins_east]

top_eight_west = top_six_west
top_eight_east = top_six_east

ranking_west_df = pd.DataFrame(top_eight_west, columns=['Rankings'])
ranking_west_df['Wins'] = top_wins_west 
ranking_east_df = pd.DataFrame(top_eight_east, columns=['Rankings'])
ranking_east_df['Wins'] = top_wins_east

ranking_east_df.to_sql('predicted_2022_23_east_playoffs_teams', con=engine, if_exists='replace', index=False)
ranking_west_df.to_sql('predicted_2022_23_west_playoffs_teams', con=engine, if_exists='replace', index=False)
print('Saved the result to the database')
