import pandas as pd
import numpy as np
from database import engine
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

query_train = f'SELECT * FROM real_total_feature_matrix_data'
df_train = pd.read_sql_query(query_train, engine)

query_test = f'SELECT * FROM predicted_total_feature_matrix_data'
df_test = pd.read_sql_query(query_test, engine)

X_train = df_train[(df_train['season'] == 2015) | (df_train['season'] == 2016) | 
                   (df_train['season'] == 2017) | (df_train['season'] == 2018) |
                   (df_train['season'] == 2019) | (df_train['season'] == 2020) |
                   (df_train['season'] == 2021) | (df_train['season'] == 2022)].iloc[:, 12:-3]

y_train = df_train[(df_train['season'] == 2015) | (df_train['season'] == 2016) | 
                   (df_train['season'] == 2017) | (df_train['season'] == 2018) |
                   (df_train['season'] == 2019) | (df_train['season'] == 2020) |
                   (df_train['season'] == 2021) | (df_train['season'] == 2022)]['result']

    

X_test = df_test[(df_test['season'] == 2023)].iloc[:, 12:-3]

y_test = df_test[(df_test['season'] == 2023)]['result']


model = RandomForestClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print('Accuracy:', accuracy)
