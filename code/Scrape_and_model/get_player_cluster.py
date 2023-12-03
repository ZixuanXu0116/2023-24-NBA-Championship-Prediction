import pandas as pd
from database import engine
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import warnings
warnings.filterwarnings('ignore')

def get_player_type_and_level(season, table_name, *feature_lists):
    sql_query = f"SELECT * FROM {table_name} WHERE season_n1 = {season}"

    df = pd.read_sql_query(sql_query, engine)
    df = df[(df['Tm'] != 'TOT')]
    position_mapping = {'PG': 1, 'SG': 2, 'SF': 3, 'PF': 4, 'C': 5}
    df['Pos'] = df['Pos'].map(position_mapping)

    scaler = StandardScaler()
    num_clusters = 5

    result_df = pd.DataFrame({'Player': df['Player'], 'Pos': df['Pos'], 'Tm': df['Tm'],
                              'MP': df['MP'], 'G': df['G']})

    for abl, cluster_col in zip(feature_lists, ['shooting', 'peri_def', 'playmaker', 
                                                'pro_rim', 'efficiency', 'influence', 
                                                'scoring']):
        X = df[abl]
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        result_df[cluster_col] = kmeans.fit_predict(X_scaled)

    return result_df

shooting_abl = ['3P', '3PAr', '3P%', 'FT%', 'USG%']
peri_def_abl = ['STL', 'STL%', 'DBPM', 'DWS', 'BLK', 'BLK%']
playmkr_abl = ['AST', 'AST%', 'USG%', 'TOV%']
pro_rim_abl = ['DBPM', 'DWS', 'BLK', 'BLK%', 'ORB%', 'DRB%', 'TRB']
effi_abl = ['eFG%', 'TS%', 'PER']
influ_abl = ['BPM', 'WS', 'VORP', 'OBPM', 'OWS', 'USG%']
scoring_abl = ['PTS', 'FG', '2P', '3P', 'FT']

result_df = get_player_type_and_level(2015, 'result_table', shooting_abl, 
                                      peri_def_abl, playmkr_abl, pro_rim_abl, 
                                      effi_abl, influ_abl, scoring_abl)

result_df.to_csv(os.path.join(os.getcwd(), 'player_clusters.csv'), index=False)
