import pandas as pd

# Read the 'demo_2016.csv' file
csv_file_path = '../../../downloads/demo_2016.csv'  # Replace with your file path

# Reading the CSV file
demo_2016_df = pd.read_csv(csv_file_path)

# Identify the start indices of each game
game_start_indices = demo_2016_df.index[demo_2016_df['Tm'].ne(demo_2016_df['Tm'].shift()) | 
                                        demo_2016_df['date'].ne(demo_2016_df['date'].shift())].tolist()

processed_games = []