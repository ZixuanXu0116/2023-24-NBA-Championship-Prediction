# 2023-24-NBA-Championship-Prediction


Team Members: [Zixuan Xu](https://github.com/ZixuanXu0116), [Munazza Ilyas](https://github.com/Munazza-Ilyas), [Suqian Qi](https://github.com/SuqianQi), [Aahil Navroz](https://github.com/AahilNav), [Joseph Williams](https://github.com/josephwms)

## Introduction
We aim to build a prediction pipeline for an NBA regular season and its playoffs. It is more like a semi-finished product with flaws. But the basic structure and the whole pipeline are built up. Significant techniques we used in the project include Data Scraping, K-means Clustering, Random Forest Classification, K-neighbors classifier, and Streamlit Dashboard. We hope you enjoy it!


## A. Data Scraping and Preparation
 
***Source:*** 
* Data was scraped from https://www.basketball-reference.com/. We scrape players' and teams' summary statistics for each season, differentiating between the regular season and playoffs data. Next, we scrape HTML files containing game-by-game data, allowing us to retrieve each player's performance and game outcomes for every match.

* A brief workflow of our pipeline is provided below:

![NBA Prediction Flow](visualizations/Updated2-flowchart.drawio.png)

***Construct Player Ability Cluster Vector:***
* After obtaining our raw data, we utilized a K-means machine learning classification algorithm for the Player Ability Cluster Vector. Different attributes were employed to classify distinct abilities, and we devised custom weights to calculate the ranking of each cluster. 

![Players ability clusters](visualizations/Updated-Clusters.png)


* The result is a **Player Ability Vector**. Each player is measured by seven attributes: shooting, peri_def, playmaker, pro_rim, efficiency, influence, and scoring. Each attribute ranges from 0 to 5, where 0 signifies the weakest ability in the respective attribute, while 5 indicates the strongest.


***Predict Next Year's Player Ability Vector:***
* For predicting the ability vector of a given year, we try to find some way to adjust the player's ability vectors in the last year to make it a predicted one for this year. 
* For the regular season, player's cluster scores were adjusted positively for younger players and negatively for older players. For playoffs, we gave positive adjustments to players who had played in the previous year's playoffs (experienced under pressure) and negative adjustments to rookies, or players who had not played in the previous year's playoffs.

## B. Making Prediction

***Construct Prediction Model:***
* With all the data prepared, we can proceed with the predictions. To predict the result of any game, we construct a machine-learning model. We treat the ability/attribute matrices for the two teams as the total features for predicting the result of a single game. The result column serves as the real outcome of each game and is used for validation and evaluation. By training the model on the results of all games from the 2015 to 2023 season, we aim to predict the outcomes of games in the 2024 season. For the simulation of each game, we can repeat n times by setting an iteration parameter, and choose the majority as the winner of that game.

***Play-in Games Prediction:***
* Since the rule of entering the playoffs changed after COVID-19, we added the play-in games into consideration. For the 2022-2023 regular season, we obtained the predicted results for each game. Then, we calculated the total wins and losses for each team in this season, allowing us to rank them. We selected teams that ranked 7th to 10th in both the Eastern and Western Conferences, which would participate in the play-in games. Next, we designed an algorithm to simulate the play-in games based on the real rules so that we can determine which team makes the playoffs. To let the users gain engagement in the simulating process, there is a component that allows users to input the second-round matchup of the play-in games.

***Playoffs Prediction:***
* After simulating the regular season using the simulate_regular_season.py, we were able to identify the final top eight teams for each conference.  We conclude our process by running the simulate_playoffs.py, which predicts outcomes and winners for each round of the playoffs, taking into account home team advantage for each match (very relevant in playoffs!). We will let the results of all the playoff series output in the terminal, so you will witness the birth of a predicted NBA champion!


## C. Result & Model Evaluation

Here is an example dashboard of predicted results (it's a GIF) for the 2023-24 playoffs with an accuracy of 55.93% for predicting each game! The Predicted Champion is LAC! 

![Dashboard](visualizations/dash_2024.gif)


## D. Limitations

* One main limitation of this plan is that we ***didn't train a separate model for the playoff data***; instead, we still used the model trained on regular season data to predict playoffs (due to limited time). Ideally, dedicated training for previous seasons' playoff data should be done.

* Additionally, for rookie players and those who didn't play in the previous season, we used current season data. This approach isn't ideal as it ***incorporates future information to predict the future***, but again due to ***time limitations***, we temporarily adopted this method to ensure the completion of the entire process.

* Another area for potential improvement is exploring additional methods to enhance the accuracy of our model predictions.  See the earlier link (https://fivethirtyeight.com/methodology/how-our-nba-predictions-work/). We might engage in more feature engineering, refining the selection of truly valuable features. For instance, in clustering, we can seek more precise and professionally segmented data to ***define clusters***. We could also experiment with creating additional clusters or combining existing ones to identify the most effective combinations for prediction, rather than being confined to a single configuration.
 
* Given that the current combination incorporates ***subjective elements based on our understanding of basketball and the NBA***, exploring various combinations may provide better predictive outcomes. Adjusting the weights assigned to a player's improvement and regression, based on a more realistic or finely segmented allocation, is another aspect to explore.

## E. Reproducing Results

### Our current model is not the best, we will continue modifying it, but anyway, the whole process is completed. All the things left are to enhance the model's performance. 

***Setup:***
* Create a Google Cloud Platform (GCP) account and set up a project.
* Enable the necessary APIs for your project, such as the PostgreSQL API if you're using PostgreSQL.
* Create a database on GCP.
* After the GCP database has been set up completely, please follow the commands and instructions below.

```linux

sh code/environ.sh

```

* Then create a .env file in the same format as demo.env by changing the attributes inside like passwords, host, and database_name to the ones of your own database. You can edit the content in the demo.env directly and then run:


```python
cp demo.env .env

```

***Scraping Data:***

```linux
sh code/scrape.sh
```

* Then you will load the game-by-game data into the database, the table name will be 'nba_game_by_game_regular_data'. This time, no worries about the duplicate of data because we use if_exists='replace' for load_game_data_to_database.py.

***Note: Within the game data, there are some erroneous entries due to mistakes by official website record keepers or the scraping process. While some of these errors can be removed using code, others require a more tricky process, involving both code-based filtering and manual review, it's very inefficient to only use a code to delete these errors because the logic and strategy for determining which row should be deleted depend on the situation. Different rows have different situations. If you use code to detect the approximate error position, and manually check the problem, it will be much faster and more precise. Considering the limited time and our huge workload, it should be reasonable to use a little bit of manual operations here to enhance efficiency. This is the most efficient way to fix this problem. For details and exact codes, please check code/scraping/check_database_problems.py. Again, you need to do this error-checking stuff only if you want to build your own database. If you want to use our database, please directly use the table named nba_game_by_game_regular_data in the database for the following operations without running the load_game_data_to_database.py and check_database_problems.py.***


***Manipulating the Data:***

* Now, after getting all the required tables to construct features for ML prediction, we begin to construct features. First, let's get the play_ability_cluster, you need to join nba_regular/playoffs_normal_player_data with nba_regular/playoffs_advanced_player_data to get a combined table before running the Python code. The SQL code for joining two pairs of two tables is provided in the get_player_cluster.py

```python
python3 code/manipulation/get_player_cluster.py
```
***The output is saved into the database in the tables named players_ability_cluster_playoffs/regular_data.***

* Then, we run the following code to get the predicted play_ability_cluster for playoffs and the regular seasons:

```python
python3 code/manipulation/get_predicted_player_matrix_regular.py
python3 code/manipulation/get_predicted_player_matrix_playoffs.py
```
***The output is saved into the database in the tables named regular/playoffs_predicted_player_matrix_data.***

Then, run the following code in order and you will get the game schedule for each season:

```python
python3 code/manipulation/get_season_schedule.py
python3 code/scraping/get_game_schedule.py
```

For the 'result' column for season 2024 are all 0s, they are not the real result, we will predict the result for 2024.

Also, remember to delete the game on 20231209 (IND vs LAL), because it's the final game for the In-Season Tournament, which doesn't count as a game of regular season.

***The output is saved into the database in the tables named regular_game_schedule_data.***

***Build Up the Model and Simulation***

* Get the real/predicted_total_dictionary_like_matrix first:

```python
python3 code/model_and_simulation/get_real_total_dictionary_like_matrix.py
python3 code/model_and_simulation/get_predicted_total_dictionary_like_matrix.py
```
For these two codes above, if `IndexError: list index out of range` happened, just rerun the code 1 or 2 times.

You will get two CSV files in the code/model_and_simulation folder, which are used to keep data temporarily for the next step: 

```python
python3 code/model_and_simulation/get_real_total_feature_matrix.py
python3 code/model_and_simulation/get_predicted_total_feature_matrix.py

```

***The output is saved into the database in the tables named real/predicted_total_feature_matrix_data.***


* Then, run the following code to get the core player_ability_matrix for each team:

```python
python3 code/model_and_simulation/get_core_players_matrix.py
```
***The output is saved into the database in the tables named core_players_matrix_2023_regular.***

* Now, we can simulate the whole 2022-23 season by running the following codes:

```python
python3 code/model_and_simulation/simulate_regular_seasons.py
```
* By changing the parameter num_iterations, you can control how many times you wanna simulate for one single game, default = 999, you can set it to a small number to save time.

***The playoffs team list will be saved into tables named predicted_2022_23_west/east_playoffs_teams***

* Then simulate the playoffs:

```python
python3 code/model_and_simulation/simulate_playoffs.py
```

### We created a Streamlit DashBoard to let you control the num_iterations for simulation:

```python
streamlit run code/model_and_simulation/streamlit_app.py
```

* Click 'Open the Browser' in the pop-up window after running the command above, wait for seconds and you will go to our dashboard webpage. Change the num_iterations to an odd positive number you want and click 'Run Simulation'. After you see the results of the regular season, you can then click 'Simulate Playoffs' at the bottom of this page. After minutes of waiting (depending on your num_iterations), you will get the score of each playoffs series and,

## You will witness the birth of the Champion!

***If you have any problems regarding the whole process, please use pulling requests or issues in this repo, or contact me through email: `zixuanxu@utexas.edu`.***













