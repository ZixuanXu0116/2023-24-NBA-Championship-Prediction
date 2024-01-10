import pandas as pd
import numpy as np
from database import engine
from generate_feature_matrix import get_feature_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split


def get_single_game_result(team1, team2, X_train, y_train, num_iterations):
    query = f'SELECT * FROM playoffs_predicted_player_matrix_data WHERE season = 2023'
    matrix_df = pd.read_sql_query(query, engine)

    schedule_df = pd.DataFrame({'team1': [team1], 'team2': [team2]})
    df = get_feature_matrix(schedule_df, matrix_df)

    '''Store the predictions for each iteration'''

    all_predictions = np.zeros((df.shape[0], num_iterations))

    for i in range(num_iterations):

        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state = np.random.randint(1, 100))

        if i % 2 == 1:
            model = RandomForestClassifier(random_state = np.random.randint(1, 100))
            model.fit(X_train, y_train)

            y_pred_iteration = model.predict(df)
            all_predictions[:, i] = y_pred_iteration

        else:
            model = KNeighborsClassifier(n_neighbors=np.random.randint(3, 5))
            model.fit(X_train, y_train)

            y_pred_iteration = model.predict(df)
            all_predictions[:, i] = y_pred_iteration
            

    '''Make the final prediction based on the majority'''

    final_predictions = np.mean(all_predictions, axis=1) > 0.5
    final_predictions = final_predictions.astype(int)

    return final_predictions
