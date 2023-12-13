import pandas as pd
import numpy as np
from database import engine
from get_result_two_teams_playoffs import get_single_game_result
from sklearn.ensemble import RandomForestClassifier

query_train = f'SELECT * FROM real_total_feature_matrix_data'
df_train = pd.read_sql_query(query_train, engine)

'''Get Basic Playoffs information'''
def get_playoff_info(season):

    query = f'SELECT * FROM predicted_{season - 1}_{season % 100}_west_playoffs_teams'
    west_df = pd.read_sql_query(query, engine)

    query = f'SELECT * FROM predicted_{season - 1}_{season % 100}_east_playoffs_teams'
    east_df = pd.read_sql_query(query, engine)

    '''Set up the playoff matchups'''
    playoff_matchups_west = [
        (west_df.iloc[0]['Rankings'], west_df.iloc[7]['Rankings']),
        (west_df.iloc[1]['Rankings'], west_df.iloc[6]['Rankings']),
        (west_df.iloc[2]['Rankings'], west_df.iloc[5]['Rankings']),
        (west_df.iloc[3]['Rankings'], west_df.iloc[4]['Rankings']),
    ]

    playoff_matchups_east = [
        (east_df.iloc[0]['Rankings'], east_df.iloc[7]['Rankings']),
        (east_df.iloc[1]['Rankings'], east_df.iloc[6]['Rankings']),
        (east_df.iloc[2]['Rankings'], east_df.iloc[5]['Rankings']),
        (east_df.iloc[3]['Rankings'], east_df.iloc[4]['Rankings']),
    ]

    return playoff_matchups_east, playoff_matchups_west, west_df, east_df

'''Simulate a round'''
def simulate_series(matchups, season, num_iterations):

    X_train = df_train[df_train['season'].isin(range(2015, season))].iloc[:, 12:-3]
    y_train = df_train[df_train['season'].isin(range(2015, season))]['result']

    winning_teams = []
    series_score = []
    for matchup in matchups:
        team2, team1 = matchup

        team1_wins, team2_wins = 0, 0
        for game_number in range(1, 8):
            '''Determine the home and away teams based on the game number'''
            if game_number in [1, 2, 5, 7]:
                home_team, away_team = team2, team1
                result = get_single_game_result(home_team, away_team, X_train, y_train, num_iterations)
                if result == 1:
                    team2_wins += 1
                else:
                    team1_wins += 1
            else:
                home_team, away_team = team1, team2

                result = get_single_game_result(home_team, away_team, X_train, y_train, num_iterations)
                if result == 1:
                    team2_wins += 1
                else:
                    team1_wins += 1

            '''Check if one team has won four games, and if so, end the series'''
            if team1_wins == 4 or team2_wins == 4:
                break

        print(
            f"{team1} vs {team2} - {team1_wins}:{team2_wins} \
                {f'{team1} wins' if team1_wins > team2_wins else f'{team2} wins'}"
        )

        winning_team = team1 if team1_wins > team2_wins else team2
        winning_teams.append(winning_team)
        series_score.append(f"{team1} vs {team2} - {team1_wins}:{team2_wins}")


    print('Winners: ', winning_teams)
    print('------------------------------------------------------------------')
    return winning_teams, series_score


'''Simulate each round'''

def simu_other_rounds(winning_teams, season, num_iterations, conf):
    print(f'{conf}ern Semifinals')
    winning_teams_2nd = []
    second_round_matchups = []

    team1 = winning_teams[0]
    team2 = winning_teams[3]
    second_round_matchups.append((team1, team2))

    team1 = winning_teams[1]
    team2 = winning_teams[2]
    second_round_matchups.append((team1, team2))

    winning_teams_2nd_round, series_score_2nd_round = simulate_series(second_round_matchups, season, num_iterations)

    print(f'{conf}ern Finals')
    winning_teams_3rd = []
    third_round_matchups = []

    team1 = winning_teams_2nd_round[0]
    team2 = winning_teams_2nd_round[1]
    third_round_matchups.append((team1, team2))

    winning_teams_3rd_round, series_score_3rd_round = simulate_series(third_round_matchups, season, num_iterations)
    if conf == 'West':
        conf_winner = winning_teams_3rd_round[0]
        conf_winner_regular_wins = west_df[west_df['Rankings'] == conf_winner]['Wins'].iloc[0]
        print(f'{conf}ern Winner is: ', conf_winner)
        print('------------------------------------------------------------------')
    elif conf == 'East':
        conf_winner = winning_teams_3rd_round[0]
        conf_winner_regular_wins = east_df[east_df['Rankings'] == conf_winner]['Wins'].iloc[0]
        print(f'{conf}ern Winner is: ', conf_winner)
        print('------------------------------------------------------------------')

    return winning_teams_2nd_round, series_score_2nd_round, winning_teams_3rd_round, \
           series_score_3rd_round, conf_winner_regular_wins, conf_winner

'''Simulate the Finals'''
def simu_finals(western_winner_regular_wins, eastern_winner_regular_wins, season, num_iterations):

    final_matchups = []

    if western_winner_regular_wins >= eastern_winner_regular_wins:
        final_matchups.append((western_winner, eastern_winner))

        champion, series_score_final = simulate_series(final_matchups, season, num_iterations)
    else:
        final_matchups.append((eastern_winner, western_winner))

        champion, series_score_final = simulate_series(final_matchups, season, num_iterations)

    print(f'The Predicted Champion is: {champion[0]} !!!!')

    return champion[0], series_score_final

playoff_matchups_east, playoff_matchups_west, west_df, east_df = get_playoff_info(season = 2023)
print('Western First Round')
winning_teams_1st_round_west, series_score_1st_round_west = simulate_series(playoff_matchups_west, season = 2023, num_iterations = 3)
winning_teams_2nd_round_west, series_score_2nd_round_west, winning_teams_3rd_round_west, \
series_score_3rd_round_west, western_winner_regular_wins, western_winner = simu_other_rounds(winning_teams_1st_round_west,
                                                                             season = 2023, num_iterations = 3, conf = 'West')
print('Eastern First Round')
winning_teams_1st_round_east, series_score_1st_round_east = simulate_series(playoff_matchups_east, season = 2023, num_iterations = 3)
winning_teams_2nd_round_east, series_score_2nd_round_east, winning_teams_3rd_round_east, \
series_score_3rd_round_east, eastern_winner_regular_wins, eastern_winner = simu_other_rounds(winning_teams_1st_round_east, 
                                                                             season = 2023, num_iterations = 3, conf = 'East')

series_all = series_score_1st_round_west
series_all.extend(series_score_2nd_round_west)
series_all.extend(series_score_3rd_round_west)
series_all.extend(series_score_1st_round_east)
series_all.extend(series_score_2nd_round_east)
series_all.extend(series_score_3rd_round_east)

print(f'Final Matchup: {western_winner} - {eastern_winner}')

champion, series_score_final = simu_finals(western_winner_regular_wins, eastern_winner_regular_wins, season = 2023, num_iterations = 3)

series_all.extend(series_score_final)
print(series_all)
