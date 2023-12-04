import pandas as pd

# Read the 'demo_2016.csv' file
csv_file_path = '../../../downloads/demo_2016.csv'  # Replace with your file path

# Reading the CSV file
demo_2016_df = pd.read_csv(csv_file_path)

# Identify the start indices of each game
game_start_indices = demo_2016_df.index[demo_2016_df['Tm'].ne(demo_2016_df['Tm'].shift()) | 
                                        demo_2016_df['date'].ne(demo_2016_df['date'].shift())].tolist()

processed_games = []

# Process each game
for i in range(0, len(game_start_indices), 2):
    if i + 1 < len(game_start_indices):  # Ensure there is a pair of indices
        date = demo_2016_df.loc[game_start_indices[i], 'date']
        team1 = demo_2016_df.loc[game_start_indices[i], 'Tm']
        team2 = demo_2016_df.loc[game_start_indices[i + 1], 'Tm']
        result = demo_2016_df.loc[game_start_indices[i + 1], 'Win']

        processed_games.append({
            'date': date,
            'team1': team1,
            'team2': team2,
            'result': result
        })
# Create a DataFrame from the processed games
final_df = pd.DataFrame(processed_games)

# Save the final dataframe to a new CSV file
final_df.to_csv('processed_demo_2016.csv', index=False)