import pandas as pd
import numpy as np
import ast
from database import engine
from ast import literal_eval
from pandas import json_normalize
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import os

df = pd.read_csv(os.path.join(os.getcwd(), 'temp_real.csv'))

y = df['result']
season = df['season']
date = df['date']

df['team1'] = df['team1'].apply(ast.literal_eval)
df['team2'] = df['team2'].apply(ast.literal_eval)


'''Flatten features and matrix for both teams'''

df_team1_features = json_normalize(df['team1'].apply(lambda x: x['features'][0]))
df_team1_matrix = json_normalize(df['team1'].apply(lambda x: x['matrix']))

df_team2_features = json_normalize(df['team2'].apply(lambda x: x['features'][0]))
df_team2_matrix = json_normalize(df['team2'].apply(lambda x: x['matrix']))

'''Concatenate the flattened features and matrix'''

df = pd.concat([df_team1_features, df_team1_matrix, df_team2_features, df_team2_matrix], axis=1)

dict_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8]
for col in dict_columns:

    list_temp1 = df[col].iloc[:, 0].values.tolist()
    temp1 = pd.DataFrame(list_temp1)

    list_temp2 = df[col].iloc[:, 1].values.tolist()
    temp2 = pd.DataFrame(list_temp2)

    index1 = str((col + 1) * 10 + 1)
    index2 = str((col + 1) * 10 + 2)

    df[[f'Pos{index1}', f'MP{index1}', f'Age{index1}', f'shooting{index1}', f'peri_def{index1}', \
        f'playmaker{index1}', f'pro_rim{index1}', f'efficiency{index1}', f'influence{index1}']] = \
    temp1[['Pos', 'MP', 'Age', 'shooting', 'peri_def', 'playmaker', 'pro_rim', 'efficiency', 'influence']]

    df[[f'Pos{index2}', f'MP{index2}', f'Age{index2}', f'shooting{index2}', f'peri_def{index2}', \
        f'playmaker{index2}', f'pro_rim{index2}', f'efficiency{index2}', f'influence{index2}']] = \
    temp2[['Pos', 'MP', 'Age', 'shooting', 'peri_def', 'playmaker', 'pro_rim', 'efficiency', 'influence']]

df = df.drop(columns = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14])
df['season'] = season
df['date'] = date
df['result'] = y

df.to_sql('real_total_feature_matrix_data', con=engine, if_exists='replace', index=False)
