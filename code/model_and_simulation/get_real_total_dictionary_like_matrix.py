import os
import warnings
import pandas as pd
from database import engine
from tqdm import tqdm
warnings.filterwarnings('ignore')

DATA_DIR = os.path.join(os.getcwd(), 'data')
SCORE_DIR = os.path.join(DATA_DIR, 'scores')

'''Load Player Data (Ability-Cluster Data)'''

def load_player_cluster_data(season):

    query = f'SELECT * FROM players_ability_cluster_regular_data WHERE "Year" = {season}'
    df = pd.read_sql_query(query, engine)
    df['Player'] = df['Player'].str.replace('*', '')

    return df

'''Load Game-by-Game Data'''

def load_game_by_game_data(season):

    query = f'SELECT * FROM nba_game_by_game_regular_data WHERE season = {season}'
    df = pd.read_sql_query(query, engine)

    return df

'''Load Team Data'''

def load_team_data(season):

    query = f'SELECT * FROM nba_regular_advanced_team_data WHERE season = {season}'

    df = pd.read_sql_query(query, engine)

    df = df.drop(columns = ['W', 'L', 'PW', 'PL', 'Arena', 'Attend.'])
    df['Team'] = df['Team'].str.replace('*', '')

    team_abbreviations = {
        'Atlanta Hawks': 'ATL',
        'Boston Celtics': 'BOS',
        'Brooklyn Nets': 'BRK',
        'Charlotte Hornets': 'CHO',
        'Chicago Bulls': 'CHI',
        'Cleveland Cavaliers': 'CLE',
        'Dallas Mavericks': 'DAL',
        'Denver Nuggets': 'DEN',
        'Detroit Pistons': 'DET',
        'Golden State Warriors': 'GSW',
        'Houston Rockets': 'HOU',
        'Indiana Pacers': 'IND',
        'Los Angeles Clippers': 'LAC',
        'Los Angeles Lakers': 'LAL',
        'Memphis Grizzlies': 'MEM',
        'Miami Heat': 'MIA',
        'Milwaukee Bucks': 'MIL',
        'Minnesota Timberwolves': 'MIN',
        'New Orleans Pelicans': 'NOP',
        'New York Knicks': 'NYK',
        'Oklahoma City Thunder': 'OKC',
        'Orlando Magic': 'ORL',
        'Philadelphia 76ers': 'PHI',
        'Phoenix Suns': 'PHO',
        'Portland Trail Blazers': 'POR',
        'Sacramento Kings': 'SAC',
        'San Antonio Spurs': 'SAS',
        'Toronto Raptors': 'TOR',
        'Utah Jazz': 'UTA',
        'Washington Wizards': 'WAS'
    }

    df['Team'] = df['Team'].map(team_abbreviations)

    return df


game_info_list = []
for season in tqdm(range(2015, 2025), desc='Processing years'):

    game_by_game_data = load_game_by_game_data(season)
    player_data = load_player_cluster_data(season)
    team_data = load_team_data(season)


    game_start_indices = game_by_game_data.index[game_by_game_data['Home'].ne(game_by_game_data['Home'].shift())].tolist()

    '''team2 will always be home team'''
    if game_start_indices:
        game_start_indices.pop(0)
    
    num_rows = len(game_by_game_data)
    game_start_indices.append(num_rows - 1)

    game_data_list = []

    for i in range(0, len(game_start_indices), 2):

        date = game_by_game_data.loc[game_start_indices[i], 'date']
        team1 = game_by_game_data.loc[game_start_indices[i] - 1, 'Tm']

        team2 = game_by_game_data.loc[game_start_indices[i + 1] - 1, 'Tm']
        team2_result = game_by_game_data.loc[game_start_indices[i + 1] - 1, 'Win']

        game_data_list.append({
            'date': date,
            'season': season,
            'team1': team1,
            'team2': team2,
            'home_team_result': team2_result
        })

    len_list = []
    for game in game_data_list:

        team1 = game['team1']
        team2 = game['team2']
        date = game['date']
        season = game['season']
        result = game['home_team_result']

        selected_game = game_by_game_data[
            (game_by_game_data['Tm'] == team1) |
            (game_by_game_data['Tm'] == team2)
        ]
        selected_game = selected_game[selected_game['date'] == date]

        '''Extract players for each team'''

        team1_players = selected_game[selected_game['Tm'] == team1]['Player'].values
        team2_players = selected_game[selected_game['Tm'] == team2]['Player'].values

        if len(team1_players) >= 9 and len(team2_players) >= 9:


            team1_features = team_data[team_data['Team'] == team1][['ORtg', 'DRtg', 'NRtg', 'TOV%', 'ORB%', 'eFG%']]
            team1_features.columns = ['ORtg_1', 'DRtg_1', 'NRtg_1', 'TOV%_1', 'ORB%_1', 'eFG%_1']
            team2_features = team_data[team_data['Team'] == team2][['ORtg', 'DRtg', 'NRtg', 'TOV%', 'ORB%', 'eFG%']]
            team2_features.columns = ['ORtg_2', 'DRtg_2', 'NRtg_2', 'TOV%_2', 'ORB%_2', 'eFG%_2']
            

            team1_matrix = player_data[player_data['Player'].isin(team1_players)]\
            [(player_data['Tm'] == team1)].drop(columns = ['Player', 'Year', 'Tm', 'G']).reset_index(drop=True)
            team2_matrix = player_data[player_data['Player'].isin(team2_players)]\
            [(player_data['Tm'] == team2)].drop(columns = ['Player', 'Year', 'Tm', 'G']).reset_index(drop=True)

            if len(team1_matrix) >= 9 and len(team2_matrix) >= 9:

                game_info = {
                    'date': date,
                    'season': season,
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

                game_info_list.append(game_info)

df = pd.DataFrame(game_info_list)


'''Save the df to a temp.csv file to temporarily keep the data'''
new_directory = os.path.join(os.getcwd(), 'code', 'model_and_simulation') 
os.chdir(new_directory)
df.to_csv(os.path.join(os.getcwd(), 'temp_real.csv'), index = False)
