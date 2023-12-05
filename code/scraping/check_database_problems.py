import pandas as pd
from database import engine


'''
!!!!!!!!

Note that the data table 'nba_game_by_game_regular_data' in our GCP database is good now,
the following codes and instructions can be used if you want to build up the database in your own one.
If you use our database, no need to operate anything.

'''

'''
Change 'season' to 2015, 2016, ..., 2024 to check each year's data.

'''
season = 2024

query = f'SELECT * FROM nba_game_by_game_regular_data WHERE season = {season}'
demo_df = pd.read_sql_query(query, engine)

'''
Q: What does the wrong rows look like?

A: There are wrong rows in the retrieved raw data, for example, a row of a Spurs's player's game data played on Jan. 1st may 
mix into the rows describing the game of HOU at DAL played on Feb. 3rd. We need to delete all those wrong rows, otherwise, 
we will get wrong result for the game schedule and game result.

'''

'''
Q: How to delete the wrong rows?

A: Use the four lines below one by one, for example, if you are using the one with 'Tm', comment out the other three lines.
We do this because for the game-by-game database retrieved from the website, there are some wrong rows in the dataframe,
and these errors are very hard to only use code for correction. Also, the number of wrong rows is around 10 rows / season, 
so considering efficiency demand, we use the combination of codes and manual correction to delete the wrong rows. 

The manual way to delete the wrong rows is to delete these rows on the debeaver database's tables manually.

'''

'''
The indices are the position where the 'Tm' or 'date' or 'Home' or 'Win' changes in the dataframe.
We can use these indices to make separation for different teams and different games.

'''
team_start_indices = demo_df.index[(demo_df['Tm'] != demo_df['Tm'].shift())].tolist()
team_start_indices = demo_df.index[(demo_df['date'] != demo_df['date'].shift())].tolist()
team_start_indices = demo_df.index[(demo_df['Win'] != demo_df['Win'].shift())].tolist()
team_start_indices = demo_df.index[(demo_df['Home'] != demo_df['Home'].shift())].tolist()

'''Delete the first indices, because it's no need to keep it.'''

if team_start_indices:
    team_start_indices.pop(0)

'''Append the last row into the indices to let the code get the information of the last game in the dataframe'''

num_rows = len(demo_df)
team_start_indices.append(num_rows - 1)

'''Print the length of indices to see if there are still wrong rows, for example, if you think you have already cleaned
all the wrong rows, then don't comment out any code above, and run the code to see if the length of indices is 2460 for
each season except for 2020,(due to Covid, less games played), 2021 (due to Covid, less games played), 
and 2024 (not finished yet), if yes, then we have deleted all the wrong rows. '''

print(len(team_start_indices))
print(team_start_indices[-1:])
processed_games = []

for i in range(0, len(team_start_indices), 2):  
    if team_start_indices[i + 1] - team_start_indices[i] == 1:
        print(game_start_indices[i])
    date = demo_df.loc[team_start_indices[i], 'date']
    team1 = demo_df.loc[team_start_indices[i] - 1, 'Tm']
    team2 = demo_df.loc[team_start_indices[i + 1] - 1, 'Tm']
    result = demo_df.loc[team_start_indices[i + 1] - 1 , 'Win']

    processed_games.append({
        'date': date,
        'team1': team1,
        'team2': team2,
        'result': result
    })

'''
Use the output CSV file to spot check (compared with the real game data in the database) 
to see if the generated game schedule is correct.

'''

final_df = pd.DataFrame(processed_games)
final_df.to_csv('processed_demo_for_check.csv', index=False)
