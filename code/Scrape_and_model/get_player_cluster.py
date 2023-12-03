import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import sys
import warnings
warnings.filterwarnings('ignore')

ENGINE_DIR = os.path.join(os.getcwd(),"code","Initial_scrape")
sys.path.append(ENGINE_DIR)
from database import engine

def pull_player_data(table_name, season):

    sql_query = f"SELECT * FROM {table_name} WHERE season_n1 = {season}"
    '''
    SQL  code to create result_table
    '''
    createtable_query= '''
        CREATE TABLE result_table AS
    SELECT
        n1."Player",
        n1."Pos",
        n1."Age",
        n1."Tm",
        n1."G",
        n1."GS",
        n1."MP",
        n1."FG",
        n1."FGA",
        n1."FG%",
        n1."3P",
        n1."3PA",
        n1."3P%",
        n1."2P",
        n1."2PA",
        n1."2P%",
        n1."eFG%",
        n1."FT",
        n1."FTA",
        n1."FT%",
        n1."ORB",
        n1."DRB",
        n1."TRB",
        n1."AST",
        n1."STL",
        n1."BLK",
        n1."TOV",
        n1."PF",
        n1."PTS",
        n1."season" AS season_n1,
        n2."season" AS season_n2,
        n2."PER",
        n2."TS%",
        n2."3PAr",
        n2."FTr",
        n2."ORB%",
        n2."DRB%",
        n2."TRB%",
        n2."AST%",
        n2."STL%",
        n2."BLK%",
        n2."TOV%",
        n2."USG%",
        n2."OWS",
        n2."DWS",
        n2."WS",
        n2."WS/48",
        n2."OBPM",
        n2."DBPM",
        n2."BPM",
        n2."VORP"
    FROM
        nba_regular_normal_player_data n1
    JOIN
        nba_regular_advanced_player_data n2
    ON
        n1."Player" = n2."Player"
        AND n1."season" = n2."season"
        AND n1."Tm" = n2."Tm";'''

    df = pd.read_sql_query(sql_query, engine)
    df = df[(df['Tm'] != 'TOT')]

    return df

'''Credit for below logic for clustering belongs to Zixuan'''
def sort_clusters(cluster_labels, num_clusters, X, weights):

    cluster_averages = {}
    for i in range(num_clusters):
        cluster_attributes = X[X[cluster_labels] == i].iloc[:, :-1]
        df_array = cluster_attributes.to_numpy()
        weight_array = np.array(weights)
        result = np.mean(np.dot(df_array, weight_array))
        cluster_averages[i] = result
    
    sorted_clusters = sorted(cluster_averages, key=cluster_averages.get)
    new_labels = {sorted_clusters[i]: i for i in range(num_clusters)}
    adjusted_labels = np.vectorize(lambda x: new_labels[x])(X[cluster_labels])
        
    
    return adjusted_labels


def get_player_type_and_level(player_data, year, *feature_lists):
    
    df = player_data
    
    position_mapping = {'PG': 1, 'SG': 2, 'SF': 3, 'PF': 4, 'C': 5}
    df['Pos'] = df['Pos'].map(position_mapping)

    scaler = StandardScaler()
    num_clusters = 6

    result_df = pd.DataFrame({'Year': year, 'Player': df['Player'], 'Pos': df['Pos'], 'Tm': df['Tm'],
                              'MP': df['MP'], 'G': df['G']})

    for abl, cluster_col, weights in zip(feature_lists, ['shooting', 'peri_def', 'playmaker', 
                                                'pro_rim', 'efficiency', 'influence', 
                                                'scoring'],
                                                [ [1, 5, 10, 2, 0.1], 
                                                [1, 0.75, 1, 1, 0.5, 0.2], 
                                                [1, 0.3, 0.25, 0.5], 
                                                [1, 1, 1, 1, 0.3, 0.3, 0.3], 
                                                [1, 1, 0.05], 
                                                [1, 1, 1, 1, 1, 0.1], 
                                                [1, 2, 2, 3, 1] ]):
        X = df[abl]
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        result_df[cluster_col] = kmeans.fit_predict(X_scaled)
        X[cluster_col] = result_df[cluster_col]

        adjusted_labels = sort_clusters(cluster_col, num_clusters, X, weights)
        result_df[cluster_col] = adjusted_labels


    return result_df

def mk_csv_dir():

    '''
    Make data directory to visualize data
    '''
    TARGET_DIR = os.path.join(os.getcwd(), "code", "Scrape_and_model", "data")
    CSV_PATH = os.path.join(TARGET_DIR, 'player_clusters.csv')
    os.makedirs(TARGET_DIR, exist_ok=True)

    return CSV_PATH


if __name__ == "__main__":

    '''Defining cluster characteristics'''
    shooting_abl = ['3P', '3PAr', '3P%', 'FT%', 'USG%']
    peri_def_abl = ['STL', 'STL%', 'DBPM', 'DWS', 'BLK', 'BLK%']
    playmkr_abl = ['AST', 'AST%', 'USG%', 'TOV%']
    pro_rim_abl = ['DBPM', 'DWS', 'BLK', 'BLK%', 'ORB%', 'DRB%', 'TRB']
    effi_abl = ['eFG%', 'TS%', 'PER']
    influ_abl = ['BPM', 'WS', 'VORP', 'OBPM', 'OWS', 'USG%']
    scoring_abl = ['PTS', 'FG', '2P', '3P', 'FT']

    '''Outputting to csv of all players and their yearly clusters'''
    all_clustered_players = pd.DataFrame()
    for year in range(2015,2024):
        player_data = pull_player_data('result_table',year)
        result_df = get_player_type_and_level(player_data, year, shooting_abl, 
                                            peri_def_abl, playmkr_abl, pro_rim_abl, 
                                            effi_abl, influ_abl, scoring_abl)
        all_clustered_players = pd.concat([all_clustered_players,result_df])

    OUT_PATH = mk_csv_dir()
    all_clustered_players.to_csv(OUT_PATH, index=False)

    '''Pushing to database'''
    all_clustered_players.to_sql('players_clustered', \
                        con=engine, if_exists='append', index=False)