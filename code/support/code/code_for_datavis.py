import pandas as pd
from database import engine
import os

query = '''
select
	regular_predicted_player_matrix_data."Player",
	regular_predicted_player_matrix_data."Tm" as Team,
	MAX(players_ability_cluster_regular_data."Age") as Player_age,
	MAX(regular_predicted_player_matrix_data."influence") as predicted_Influence,
	MAX(players_ability_cluster_regular_data."influence") as Actual_influence
from
	regular_predicted_player_matrix_data
join
	players_ability_cluster_regular_data
on
	regular_predicted_player_matrix_data."Player" = players_ability_cluster_regular_data."Player"
where
	regular_predicted_player_matrix_data."Year" = 2023
	and players_ability_cluster_regular_data."Year" = 2023
group by
	regular_predicted_player_matrix_data."Player",
	regular_predicted_player_matrix_data."Tm";
'''
cwd = os.getcwd()
file_name = "InfluencePredvsActualbyAge"
excel_filepath = os.path.join(cwd, f"{file_name}.xlsx")

df = pd.read_sql_query(query, engine)
#df.to_excel(excel_filepath, index=False)

df.to_sql('influence_predicted_vs_actual_byage_2022', \
                        con=engine, if_exists='replace', index=False)