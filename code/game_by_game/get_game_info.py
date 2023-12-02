import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = os.path.join(os.getcwd(), 'data')
SCORE_DIR = os.path.join(DATA_DIR, 'scores')

# Load Player Data (Ability-Cluster Data)
player_data = pd.read_csv(os.path.join(os.getcwd(), 'player_clusters.csv'))

# Load Game-by-Game Data
game_by_game_data = pd.read_csv(os.path.join(os.getcwd(), 'demo.csv'))

# Load Team Data
team_data = pd.read_csv(os.path.join(os.getcwd(), 'team_data.csv'))


game_data_list = []
game_start_indices = game_by_game_data.index[game_by_game_data['Tm'].ne(game_by_game_data['Tm'].shift()) \
                                           | game_by_game_data['date'].ne(game_by_game_data['date'].shift())].tolist()

'''team2 will always be home team'''

for i in range(0, len(game_start_indices), 2):

    date = game_by_game_data.loc[game_start_indices[i], 'date']
    team1 = game_by_game_data.loc[game_start_indices[i], 'Tm']

    team2 = game_by_game_data.loc[game_start_indices[i + 1], 'Tm']
    team2_result = game_by_game_data.loc[game_start_indices[i + 1], 'Win']

    game_data_list.append({
        'date': date,
        'team1': team1,
        'team2': team2,
        'home_team_result': team2_result
    })

game_info_list = []
len_list = []
for game in game_data_list:

    team1 = game['team1']
    team2 = game['team2']
    date = game['date']
    result = game['home_team_result']

    selected_game = game_by_game_data[
        (game_by_game_data['Tm'] == team1) |
        (game_by_game_data['Tm'] == team2)
    ]
    selected_game = selected_game[selected_game['date'] == date]

    # Extract players for each team
    team1_players = selected_game[selected_game['Tm'] == team1]['Player'].values
    team2_players = selected_game[selected_game['Tm'] == team2]['Player'].values

    if len(team1_players) >= 9 and len(team2_players) >= 9:


        team1_features = team_data[team_data['Team'] == team1][['ORtg', 'DRtg', 'NRtg', 'TOV%', 'ORB%', 'eFG%']]
        team2_features = team_data[team_data['Team'] == team2][['ORtg', 'DRtg', 'NRtg', 'TOV%', 'ORB%', 'eFG%']]

        team1_matrix = player_data[player_data['Player'].isin(team1_players)]\
                                [(player_data['Tm'] == team1)].drop(columns = ['Player', 'Tm']).reset_index(drop=True)
        team2_matrix = player_data[player_data['Player'].isin(team2_players)]\
                                [(player_data['Tm'] == team2)].drop(columns = ['Player','Tm']).reset_index(drop=True)
        if len(team1_matrix) >= 9 and len(team2_matrix) >= 9:
        

            game_info = {
                'date': date,
                'team1': {
                    'name': team1,
                    'features': team1_features.to_dict(orient='records'),
                    'matrix': team1_matrix.to_dict(orient='records')
                },
                'team2': {
                    'name': team2,
                    'features': team2_features.to_dict(orient='records'),
                    'matrix': team2_matrix.to_dict(orient='records')
                },
                'result': result
            }

            # Append the dictionary to the list
            game_info_list.append(game_info)

df = pd.DataFrame(game_info_list)

df.to_csv(os.path.join(os.getcwd(), 'game_info.csv'), index=False)

