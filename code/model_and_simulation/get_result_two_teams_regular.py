import pandas as pd
import numpy as np
from database import engine
from tqdm import tqdm
from generate_feature_matrix import get_feature_matrix


def get_single_game_result(team1, team2, model):
    query = f'SELECT * FROM regular_predicted_player_matrix_data WHERE season = 2023'
    matrix_df = pd.read_sql_query(query, engine)

    schedule_df = pd.DataFrame({'team1': [team1], 'team2': [team2]})
    df = get_feature_matrix(schedule_df, matrix_df)

    num_iterations = 9

    '''Store the predictions for each iteration'''

    all_predictions = np.zeros((df.shape[0], num_iterations))

    for i in tqdm(range(num_iterations), desc='Running Iterations', unit='iteration'):
        y_pred_iteration = model.predict(df)
        all_predictions[:, i] = y_pred_iteration

    '''Make the final prediction based on the majority'''

    final_predictions = np.mean(all_predictions, axis=1) > 0.5
    final_predictions = final_predictions.astype(int)

    return final_predictions
