# 2023-24-NBA-Championship-Prediction

## A. Data Scraping and Loading
 
***Source:*** We scraped the NBA normal and advanced data of players and teams in playoffs and regular seasons from https://www.basketball-reference.com/


***Execution method:*** To execute the code and load the data to your database, you should:
* Create a Google Cloud Platform (GCP) account and set up a project.
* Enable the necessary APIs for your project, such as the PostgreSQL API if you're using PostgreSQL.
* Create a database on GCP.
* After the GCP database has been set up completely, please follow the commands and instructions below.

```linux

git clone git@github.com:ZixuanXu0116/2023-24-NBA-Championship-Prediction.git

cd 2023-24-NBA-Championship-Prediction

pip install -r requirements.txt 

```

* Then create a .env file in the same format as demo.env by changing the attributes inside like passwords, host, and database_name to the ones of your own database. You can edit the content in the demo.env directly and then run:


```python
cp demo.env .env

```

* In this way, you will set up the dotenv file for loading data into the database, then run the following Python code:

```python
python3 code/data_scraping/get_NBA_data.py

```

* Since the data of the NBA 2023-24 Regular Season will be updated for now (2023/11), i.e. almost new game stats every day, we provide a code to update data automatically every day. You can set up an automatic code execution in the following method in your terminal:

```python
crontab -e
0 0 * * * your_directory/update_data.py

```

Learning Materials:
Google Data Studio Visualization: https://www.youtube.com/watch?v=CvsCQJFpRpI

Tableau Dashboard: https://www.youtube.com/watch?v=sqbq4eTv3AU

NBA Players Peak age Distributions: https://www.linkedin.com/pulse/analysing-predicting-peak-age-nba-players-data-science-marcus-chua/

Flowchart: 
![NBA Prediction Flow](visualizations/Updated-NBA-prediction.png)


## B. Data Preparation

***Data Cleaning:***
* The Raw data of players and teams are huge and messy, so we need to roughly clean and summarize the data. Firstly, we scrape regular and advanced player and team summary statistics for each season, differentiating between playoffs and regular seasons, resulting in 2 * 2 * 2 = 8 tables. Next, we scrape HTML files containing game-by-game data from the same website. These data allow us to retrieve each player's performance and game outcomes for every match. We then utilize the code in the "manipulation" folder for data cleaning and creating new tables. As a result, we create a **Player Ability Cluster Matrix** using some of the previously obtained eight tables.

![Players ability clusters](visualizations/Updated-Clusters.png)

***Construct Player Ability Vector:***
* We utilized the K-means machine learning classification algorithm for the Player Ability Cluster Matrix. Different attributes were employed to classify distinct abilities, and we devised custom weights to calculate the ranking of each cluster. Consequently, we constructed a **Player Ability Vector**. Each player is measured by seven attributes: shooting, peri_def, playmaker, pro_rim, efficiency, influence, and scoring. Each attribute ranges from 0 to 5, where 0 signifies the weakest ability in the respective attribute, while 5 indicates the strongest. Here is an example:(screenshot)

***Construct Team Ability Matrix:***
* Having obtained the ability vectors for each player in each regular season and playoff, it is natural to establish a **Team Ability Matrix**. Each team consists of a different number of players, for simplification, we only selected the nine players with the longest playing time in each team, which is essentially the key nine players for that team. We formed a 9x7 ability matrix with these nine players and their seven attributes. Adding a few columns to this matrix for their age, on-court positions, time played, and game played, we constructed a **Team Ability Matrix** for each team for each season and the regular seasons and playoffs. Here is an example:(screenshot)

***Get Game Schedule:***
* After obtaining the ability matrix, the next step is to acquire the schedule for the entire season. In a league with 30 teams, a regular season typically involves each team playing 82 games. Therefore, the total number of games in a season is 82 × 15, equal to 1230 games. We can combine our previously scraped HTML files with our Python code to generate the history schedule for each season. This schedule takes the form of a data frame with 4 columns: the date of the game, the teams involved (team 1 and team 2), and the game result. Results are represented using 0 and 1, where 0 indicates a predicted loss of team 1, and 1 indicates a predicted win of team 1. To simplify the model, we focus on predicting the outcome rather than the exact score.

## C. Making Prediction

***Construct Prediction Model:***
* With all the data prepared, we can proceed with the predictions. To predict the result of any game, we construct a machine-learning model. We treat the ability matrices for the two teams involved as our total features and include a column for the result to serve as the real outcome for validation. By training the model on the results of all games from the 2015 season to the 2022 season, we aim to predict the outcomes of games in the 2023 season.

***Play-in Games Prediction:***
* Since the rule of playoff seasons changed after COVID-19, we added the play-in games into consideration. For the 2022-2023 season, we obtained the predicted results for each game. Then, we calculated the total wins and losses for each team, allowing us to rank them. We selected teams that ranked 7th to 10th in both the Eastern and Western Conferences, which would participate in play-in games. We designed an algorithm for these teams to compete in play-in games and get the team that would join in the playoff games. To raise the level of engagement of the users, we will let users input the match-ups for the second round of play-ins which are straightforward.

***Regular Season & Playoffs Prediction:***
* After simulating the regular season using the "simulate regular season" Python file, we could identify the final top eight teams from each conference that advanced to the playoffs after completing the play-in games. Subsequently, using another code called "simulate_playoffs," we predicted the outcomes and winners for each round of the playoffs. In this simulation, we considered the home-court advantage and consistently placed the home team at the end to ensure our model factored in this aspect. The final output of this code reveals the champion of the season and all the game results from the first round to the finals. Here is an example(screenshot).

## D. Result & Model evaluation

* With all codes provided before, we can predict the champion of 2023. Here is the result:(screenshot)
* For the model evaluation, we use accuracy as our metric. Here is our report:(screenshot or table)
  
## E. Limitations

* One main limitation of this plan is that we didn't separately train of model on playoff data and regular season data; instead, we used a model trained on regular season data to predict playoffs. Ideally, a dedicated training for previous seasons' playoff data should be done, but due to time constraints, we couldn't manage that.

* Additionally, for rookie players and those who didn't play in the previous season, we used current season data. This approach isn't ideal as it incorporates future information to predict the future, but due to time limitations, we temporarily adopted this method to ensure the completion of the entire process.

* Finally, another area for potential improvement is exploring additional methods to enhance the accuracy of our model predictions. We might engage in more feature engineering, refining the selection of truly valuable features. For instance, in clustering, we can seek more precise and professionally segmented data to define clusters. We could also experiment with creating additional clusters or combining existing ones to identify the most effective combinations for prediction, rather than being confined to a single configuration.
 
* Given that the current combination incorporates subjective elements based on our understanding of basketball and the NBA, exploring various combinations may provide better predictive outcomes. Adjusting the weights assigned to player improvement and regression, based on a more realistic or finely segmented allocation, is another aspect to explore.

## F. Further Improvements

* We could consider experimenting with different models. While our current attempts have been somewhat limited to machine learning, venturing into deep learning might yield higher prediction accuracy. We possibly need more parameter tuning combined with some grid search methods. However, it's important to note that there's no guarantee of a definite improvement, but it's a direction worth exploring and putting effort into.

* We once considered constructing a comprehensive dataset for the first 20 games of each season using the data from each game. This approach would allow us to combine the data from the previous season with the data from the first 20 games of the current season for a more accurate estimation of current player abilities and the current status of teams. Subsequently, using this data, we could predict the outcomes of games after the initial 20 matches. Adding the results of the first 20 games to predict playoff contenders and, within the playoff predictions, forecast the eventual champion is an area where we can enhance our model.

* We began writing some code to scrape player average plus-minus values for the first 20 games as an attempt to implement this idea. However, due to the substantial workload and time constraints, we couldn't complete this aspect of the work. Nevertheless, we do have plans to refine this approach in the future because it has the potential to make the entire model more logical, compelling, and likely more precise in its predictions.

* For the feature selection in our prediction model, we ultimately did not incorporate any team-specific features. This decision wasn't due to the belief that team features are unimportant, but rather, creating highly effective team features with our current data and limited time posed significant challenges. We are well aware that team data is commonly utilized in match predictions, but our model aims to explore a different path. The player ability matrix, a unique concept we introduced, serves as a testament to this unconventional approach. We are eager to evaluate the viability of this idea. In the future, given the capability and time, we may introduce team-specific features and refine the player ability matrix to construct improved features and models.

* We also wrote code to update the database, focusing on the data from the current 2023-24 season. Our original intention was to create a predictive model that could be updated in real-time daily. However, due to time constraints, we only managed to accomplish the basic task of updating fundamental data. We did not complete the integration of the updated data with the model or even produce an interactive real-time updating dashboard. Insufficient manpower and time hindered us from achieving this, but it remains an area for future improvement and enhancement.

## G. Things to Mention

* Throughout the entire process of data manipulation, model development, and simulating match results, there are indeed some challenging aspects. The first significant challenge is the considerable time required to extract HTML data for each game from the monthly game HTML. With data spanning 10 seasons and approximately 1230 games per season, this totals over 10,000 games, and the complexity of each game's data, coupled with potential timeouts during scraping, may necessitate around 70 hours for data retrieval.

* If you wish to replicate the entire process from scratch and create a new database using your account, it would indeed take more than 70 hours to run these codes. However, if you prefer not to undertake this task, you can directly use our GCP Database, which already contains the data we need. Additionally, within the game data, there are some erroneous entries due to mistakes by official website record keepers. While some of these errors can be removed using code, others require a more intricate screening process, involving both code-based filtering and manual review, to ensure the accurate removal of erroneous data. To address this, we provide a code-named "check database problems." Following the instructions in this code allows you to rectify your self-created database, a crucial step for generating accurate season schedules. Failure to rectify errors can lead to inaccuracies in the generated schedules, but with proper correction, accurate schedules can be produced. These challenges are integral aspects of the entire operational process.

* As some codes generate intermediate products that cannot be directly input into the database, it might be necessary to store certain results in a temporary CSV file. For these codes, the first step is to adjust their working directory, and secondly, we must ensure that the codes are executed in the correct order. I will provide a sequence for running the entire code process. If you deviate from this sequence, you might make incorrect modifications to the database, resulting in potential errors during execution or the generation of faulty models.


The link to get all the outputs of get_gamely_html directly without running codes for over 70 hours: https://drive.google.com/file/d/1rDECUtqfObDgGxkqTo-9oiiPt-PdRXNL/view?usp=sharing
