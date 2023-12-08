import pandas as pd
from database import engine
import warnings
from tqdm import tqdm

warnings.filterwarnings('ignore')

'''Step 1: Create a new DataFrame for the combined data'''
columns = ['Player', 'Pos', 'Age', 'Tm', 'MP', 'G', 'shooting', 'peri_def', 'playmaker', 'pro_rim', 'efficiency', 'influence', 'scoring','season']
player_cluster_matrix = pd.DataFrame(columns=columns)

def get_single_season_cluster_matrix(season, game_type):

    query = f'SELECT * FROM players_ability_cluster_{game_type}_data WHERE "Year" = {season}'
    df = pd.read_sql_query(query, engine)

    return df

'''Step 2: Iterate over each row in the cur playoffs DataFrame'''
if __name__ == "__main__":

    for season in tqdm(range(2016, 2025), desc="Processing years"):

        df_last_playoffs = get_single_season_cluster_matrix(season - 1, 'playoffs')
        df_cur_regular = get_single_season_cluster_matrix(season, 'regular')

        for index, player_cur_playoffs in df_cur_regular.iterrows():
            player_name = player_cur_playoffs['Player']
            team_name = player_cur_playoffs['Tm']

            '''Step 3: Check if the player is in the last playoffs DataFrame'''
            if player_name in df_last_playoffs['Player'].values:
                '''If yes, get the player's attributes from the 2015 playoffs DataFrame'''  
                player_attributes = df_last_playoffs[df_last_playoffs['Player'] == player_name].iloc[0]
                '''Update the team name to the current team'''
                player_attributes['Tm'] = team_name

                '''Step 4: Age-based adjustments to attributes'''
                age = player_attributes['Age']
                attributes = [['shooting', 'peri_def', 'playmaker', 'pro_rim', 'efficiency', 'influence', 'scoring']]
                if 18 <= age <= 23:
                    attributes = attributes.apply(lambda x: x + 0.5 if x != 5 else x)
                elif 24 <= age <= 27:
                    attributes = attributes.apply(lambda x: x + 0.25 if x != 5 else x)
                elif 33 <= age <= 35:
                    attributes = attributes.apply(lambda x: x if x != 0 else x)
                elif age >= 36:
                    attributes = attributes.apply(lambda x: x - 0.2 if x != 0 else x)

                '''Update the player's attributes in the player_cluster_matrix'''
                player_attributes[['shooting', 'peri_def', 'playmaker', 'pro_rim', 'efficiency', 'influence', 'scoring']] = attributes
            else:
                '''If no, use the player's attributes from the current regular season DataFrame'''
                player_attributes = player_cur_playoffs.copy()

                '''Step 5: Decrease all ability attributes by 0.25 if the value is not 0'''
                attributes = player_attributes[['shooting', 'peri_def', 'playmaker', 'pro_rim', 'efficiency', 'influence', 'scoring']]
                attributes = attributes.apply(lambda x: x - 0.25 if x != 0 else x)
                player_attributes[['shooting', 'peri_def', 'playmaker', 'pro_rim', 'efficiency', 'influence', 'scoring']] = attributes

            player_attributes['season'] = season
            '''Step 6: Append the player's attributes to the player_cluster_matrix'''

            player_cluster_matrix = player_cluster_matrix.append(player_attributes, ignore_index=True)
    
    player_cluster_matrix.to_sql('playoffs_predicted_player_matrix_data', con=engine, if_exists='replace', index=False) 



