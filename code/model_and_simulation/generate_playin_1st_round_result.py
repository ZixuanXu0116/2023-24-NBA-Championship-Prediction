import pandas as pd

def generate_new_df_part(original_df):
    
    new_rows = []

    for index, row in original_df.iterrows():
        team1, team2, result_pred = row['team1'], row['team2'], row['result_pred']

        if index == 1:
            if result_pred == 1:
                new_rows.append({'team': f'Keep temp as West 9: {team2}'})
                new_rows.append({'team': f'Gameover: {team1}'})
            else:
                new_rows.append({'team': f'Keep temp as West 9: {team1}'})
                new_rows.append({'team': f'Gameover: {team2}'})
        elif index == 3:
            if result_pred == 1:
                new_rows.append({'team': f'Keep temp as East 9: {team2}'})
                new_rows.append({'team': f'Gameover: {team1}'})
            else:
                new_rows.append({'team': f'Keep temp as East 9:  {team1}'})
                new_rows.append({'team': f'Gameover: {team2}'})
        else:
            if index == 0:
                if result_pred == 1:
                    new_rows.append({'team': f'Make playoffs as West 7: {team2}'})
                    new_rows.append({'team': f'Keep temp as West 8:  {team1}'})
                elif result_pred == 0:
                    new_rows.append({'team': f'Make playoffs as West 7: {team1}'})
                    new_rows.append({'team': f'Keep temp as West 8: {team2}'})
            elif index == 2:
                if result_pred == 1:
                    new_rows.append({'team': f'Make playoffs as East 7: {team2}'})
                    new_rows.append({'team': f'Keep temp as East 8:  {team1}'})
                elif result_pred == 0:
                    new_rows.append({'team': f'Make playoffs as East 7: {team1}'})
                    new_rows.append({'team': f'Keep temp as East 8:  {team2}'})

    '''Create DataFrame with new rows'''

    new_df = pd.DataFrame(new_rows)

    return new_df
