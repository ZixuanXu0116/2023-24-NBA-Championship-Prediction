import pandas as pd
import numpy as np
from database import engine
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from generate_playin_1st_round_result import generate_new_df_part
from generate_feature_matrix import get_feature_matrix
from get_result_two_teams_regular import get_single_game_result
import warnings

warnings.filterwarnings('ignore')


def simulate_seasons(schedule_df, eastern_teams, western_teams, y_test, y_pred):

    eastern_wins = {}
    eastern_losses = {}
    western_wins = {}
    western_losses = {}

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print('Accuracy:', accuracy)
    print('Classification Report:\n', report)

    report = classification_report(y_test, y_pred, output_dict=True)

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


    eastern_results_df = pd.DataFrame(
        {
            'Team': eastern_teams,
            'Wins': [eastern_wins.get(team, 0) for team in eastern_teams],
            'Losses': [eastern_losses.get(team, 0) for team in eastern_teams],
        }
    )

    western_results_df = pd.DataFrame(
        {
            'Team': western_teams,
            'Wins': [western_wins.get(team, 0) for team in western_teams],
            'Losses': [western_losses.get(team, 0) for team in western_teams],
        }
    )


    '''
    Add a new column for ranking within each conference
    '''

    eastern_results_df['Rank'] = (
        eastern_results_df['Wins'].rank(ascending=False, method='min').astype(int)
    )
    western_results_df['Rank'] = (
        western_results_df['Wins'].rank(ascending=False, method='min').astype(int)
    )

    '''
    Sort the DataFrames based on the number of wins

    '''

    eastern_results_df = eastern_results_df.sort_values(by='Wins', ascending=False).reset_index(drop=True)
    western_results_df = western_results_df.sort_values(by='Wins', ascending=False).reset_index(drop=True)


    print('Eastern Conference Results:')
    print(eastern_results_df)
    print('-----------------------------------------------------------')
    print('\nWestern Conference Results:')
    print(western_results_df)

    return eastern_results_df, western_results_df, accuracy, report


def get_predictions(season, num_iterations):

    query_train = f'SELECT * FROM real_total_feature_matrix_data'
    df_train = pd.read_sql_query(query_train, engine)

    query_test = f'SELECT * FROM core_players_matrix_{season}_regular'
    df_test = pd.read_sql_query(query_test, engine)

    query_schedule = f'SELECT * FROM regular_game_schedule_data WHERE season = {season}'
    schedule_df = pd.read_sql_query(query_schedule, engine)

    X_train = df_train[df_train['season'].isin(range(2015, season))].iloc[:, 12:-3]
    y_train = df_train[df_train['season'].isin(range(2015, season))]['result']

    X_test = df_test.iloc[:, :-1]
    y_test = df_test['result']

    all_predictions = np.zeros((X_test.shape[0], num_iterations))

    for i in tqdm(range(num_iterations), desc='Running Iterations', unit='iteration'):

        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state = np.random.randint(1, 100))

        if i % 2 == 1:
            model = RandomForestClassifier(random_state = np.random.randint(1, 100))
            model.fit(X_train, y_train)

            y_pred_iteration = model.predict(X_test)
            all_predictions[:, i] = y_pred_iteration

        else:
            model = KNeighborsClassifier(n_neighbors=np.random.randint(2, 6))
            model.fit(X_train, y_train)

            y_pred_iteration = model.predict(X_test)
            all_predictions[:, i] = y_pred_iteration
            


    '''Make the final prediction based on the majority'''

    final_predictions = np.mean(all_predictions, axis=1) > 0.5
    final_predictions = final_predictions.astype(int)
    y_pred = final_predictions

    return y_pred, y_test, schedule_df, model


y_pred, y_test, schedule_df, model = get_predictions(season = 2023, num_iterations = 3)
schedule_df['result_pred'] = y_pred

'''
Define Eastern Conference and Western Conference teams

'''

eastern_teams = [
    'ATL',
    'BOS',
    'BRK',
    'CHO',
    'CHI',
    'CLE',
    'DET',
    'IND',
    'MIA',
    'MIL',
    'NYK',
    'ORL',
    'PHI',
    'TOR',
    'WAS',
]

western_teams = [
    'DAL',
    'DEN',
    'GSW',
    'HOU',
    'LAC',
    'LAL',
    'MEM',
    'MIN',
    'NOP',
    'OKC',
    'PHO',
    'POR',
    'SAC',
    'SAS',
    'UTA',
]


playin_range = range(6, 10)


'''Identify the teams that would be in the play-in games'''
def get_playoff_teams(eastern_results_df, western_results_df, season):

    eastern_playin_teams = eastern_results_df.iloc[playin_range].copy()
    western_playin_teams = western_results_df.iloc[playin_range].copy()
    print('-----------------------------------------------------------')

    '''Display the teams that would be in the play-in games'''

    print('Eastern Conference Play-in Teams:')
    print(eastern_playin_teams)
    print('-----------------------------------------------------------')
    print('\nWestern Conference Play-in Teams:')
    print(western_playin_teams)


    team1_data = {
        'team': [
            western_playin_teams.iloc[1, :]['Team'],
            western_playin_teams.iloc[3, :]['Team'],
            eastern_playin_teams.iloc[1, :]['Team'],
            eastern_playin_teams.iloc[3, :]['Team'],
        ]
    }

    team2_data = {
        'team': [
            western_playin_teams.iloc[0, :]['Team'],
            western_playin_teams.iloc[2, :]['Team'],
            eastern_playin_teams.iloc[0, :]['Team'],
            eastern_playin_teams.iloc[2, :]['Team'],
        ]
    }

    query = f'SELECT * FROM regular_predicted_player_matrix_data WHERE season = {season}'
    matrix_df = pd.read_sql_query(query, engine)

    playin_round_one = pd.DataFrame(
        {'team1': team1_data['team'], 'team2': team2_data['team']}
    )

    playin_round_one_matrix = get_feature_matrix(playin_round_one, matrix_df)

    y_pred_playin_round_one = model.predict(playin_round_one_matrix)

    playin_round_one['result_pred'] = y_pred_playin_round_one
    print('-----------------------------------------------------------')
    round_one_result = generate_new_df_part(playin_round_one)
    print(round_one_result)
    print('-----------------------------------------------------------')
    west_team1 = round_one_result['team'].iloc[2][-3:]
    west_team2 = round_one_result['team'].iloc[1][-3:]
    east_team1 = round_one_result['team'].iloc[6][-3:]
    east_team2 = round_one_result['team'].iloc[5][-3:]

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

    seven_wins_west = western_results_df[western_results_df['Team'] == west_seven][
        'Wins'
    ].iloc[0]
    seven_wins_east = eastern_results_df[eastern_results_df['Team'] == east_seven][
        'Wins'
    ].iloc[0]

    west_eight = eight_list[0]
    east_eight = eight_list[1]

    eight_wins_west = western_results_df[western_results_df['Team'] == west_eight][
        'Wins'
    ].iloc[0]
    eight_wins_east = eastern_results_df[eastern_results_df['Team'] == east_eight][
        'Wins'
    ].iloc[0]

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

    ranking_east_df.to_sql(
        f'predicted_{season - 1}_{season % 100}_east_playoffs_teams',
        con=engine,
        if_exists='replace',
        index=False,
    )
    ranking_west_df.to_sql(
        f'predicted_{season - 1}_{season % 100}_west_playoffs_teams',
        con=engine,
        if_exists='replace',
        index=False,
    )
    print('Saved the result to the database')

    return ranking_east_df, ranking_west_df
    
eastern_results_df, western_results_df, accuracy, report = simulate_seasons(schedule_df, eastern_teams, western_teams, y_test, y_pred)
ranking_east_df, ranking_west_df = get_playoff_teams(eastern_results_df, western_results_df, season = 2023)
