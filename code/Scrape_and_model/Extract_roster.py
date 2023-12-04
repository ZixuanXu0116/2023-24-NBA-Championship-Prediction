import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore')

# Step 1: Create a new DataFrame for the combined data
columns = ['Player', 'Pos', 'Age', 'Tm', 'MP', 'G', 'shooting', 'peri_def', 'playmaker', 'pro_rim', 'efficiency', 'influence', 'scoring']
combined_df = pd.DataFrame(columns=columns)

# Assuming you have DataFrames for 2015 playoffs and 2016 regular season
player_playoffs_2015 = pd.read_csv(os.path.join(os.getcwd(), 'player_playoffs_cluster_2015.csv'))
play_2016 = pd.read_csv(os.path.join(os.getcwd(), 'play_cluster_2016.csv'))

# Step 2: Iterate over each row in the 2016 playoffs DataFrame
for index, row_2016_playoffs in play_2016.iterrows():
    player_name = row_2016_playoffs['Player']

    # Step 3: Check if the player is in the 2015 playoffs DataFrame
    if player_name in player_playoffs_2015['Player'].values:
        # If yes, get the player's attributes from the 2015 playoffs DataFrame
        player_attributes = player_playoffs_2015[player_playoffs_2015['Player'] == player_name].iloc[0]
        # Update the team name to the current team for the 2016 playoffs
        player_attributes['Tm'] = row_2016_playoffs['Tm']
    else:
        # If no, use the player's attributes from the 2016 regular season DataFrame
        player_attributes = row_2016_playoffs.copy()

    # Step 4: Append the player's attributes to the combined DataFrame
    combined_df = combined_df.append(player_attributes, ignore_index=True)

# Step 5: Display or Save the Combined DataFrame
print(combined_df)
combined_df.to_csv(os.path.join(os.getcwd(), 'combined_playoffs_matrix.csv'), index=False)