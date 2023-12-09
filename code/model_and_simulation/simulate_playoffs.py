import pandas as pd
from database import engine
from get_result_two_teams_playoffs import get_single_game_result
from sklearn.ensemble import RandomForestClassifier

query_train = f'SELECT * FROM real_total_feature_matrix_data'
df_train = pd.read_sql_query(query_train, engine)

season = 2023
query_schedule = f'SELECT * FROM regular_game_schedule_data WHERE season = {season}'
schedule_df = pd.read_sql_query(query_schedule, engine)

X_train = df_train[df_train['season'].isin(range(2015, 2023))].iloc[:, 12:-3]
y_train = df_train[df_train['season'].isin(range(2015, 2023))]['result']

model = RandomForestClassifier()
model.fit(X_train, y_train)

query = f'SELECT * FROM predicted_2022_23_west_playoffs_teams'
west_df = pd.read_sql_query(query, engine)

query = f'SELECT * FROM predicted_2022_23_east_playoffs_teams'
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


def simulate_series(matchups):
    winning_teams = []
    for matchup in matchups:
        team2, team1 = matchup

        team1_wins, team2_wins = 0, 0
        for game_number in range(1, 8):
            '''Determine the home and away teams based on the game number'''
            if game_number in [1, 2, 5, 7]:
                home_team, away_team = team2, team1
                result = get_single_game_result(away_team, home_team, model)
                if result == 1:
                    team2_wins += 1
                else:
                    team1_wins += 1
            else:
                home_team, away_team = team1, team2

                result = get_single_game_result(away_team, home_team, model)
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

    print('Winners: ', winning_teams)
    print('------------------------------------------------------------------')
    return winning_teams


'''Simulate each round'''

'''Simulate Western Results'''

print('Western First Round')
winning_teams = simulate_series(playoff_matchups_west)


print('Western Semifinals')
winning_teams_2nd = []
second_round_matchups = []

team1 = winning_teams[0]
team2 = winning_teams[3]
second_round_matchups.append((team1, team2))

team1 = winning_teams[1]
team2 = winning_teams[2]
second_round_matchups.append((team1, team2))

winning_teams = simulate_series(second_round_matchups)

print('Western Finals')
winning_teams_3rd = []
third_round_matchups = []

team1 = winning_teams[0]
team2 = winning_teams[1]
third_round_matchups.append((team1, team2))

winning_teams = simulate_series(third_round_matchups)
western_winner = winning_teams[0]
western_winner_regular_wins = west_df[west_df['Rankings'] == western_winner][
    'Wins'
].iloc[0]
print('Western Winner is: ', western_winner)
print('------------------------------------------------------------------')


'''---------------------------------------------------------------------------'''
'''Simulate Western Results'''

print('Eastern First Round')
winning_teams = simulate_series(playoff_matchups_east)


print('Eastern Semifinals')
winning_teams_2nd = []
second_round_matchups = []

team1 = winning_teams[0]
team2 = winning_teams[3]
second_round_matchups.append((team1, team2))

team1 = winning_teams[1]
team2 = winning_teams[2]
second_round_matchups.append((team1, team2))

winning_teams = simulate_series(second_round_matchups)

print('Eastern Finals')
winning_teams_3rd = []
third_round_matchups = []

team1 = winning_teams[0]
team2 = winning_teams[1]
third_round_matchups.append((team1, team2))

winning_teams = simulate_series(third_round_matchups)

print('Eastern Winner is: ', winning_teams[0])
print('------------------------------------------------------------------')
eastern_winner = winning_teams[0]
eastern_winner_regular_wins = east_df[east_df['Rankings'] == eastern_winner][
    'Wins'
].iloc[0]

print(f'Final Matchup: {western_winner} - {eastern_winner}')

final_matchups = []

if western_winner_regular_wins >= eastern_winner_regular_wins:
    final_matchups.append((western_winner, eastern_winner))

    champion = simulate_series(final_matchups)
else:
    final_matchups.append((eastern_winner, western_winner))

    champion = simulate_series(final_matchups)

print(f'The Predicted Champion is: {champion[0]} !!!!')
