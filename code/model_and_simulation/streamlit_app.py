import streamlit as st
st.set_page_config(layout="wide")
import os
from PIL import Image
import base64
import pandas as pd
import numpy as np
from tqdm import tqdm
from database import engine
from get_result_two_teams_playoffs import get_single_game_result
from simulate_regular_seasons import get_predictions, simulate_seasons, eastern_teams, western_teams, get_playoff_teams

# Custom color theme
primaryColor = "#E694FF"
backgroundColor = "#00172B"
secondaryBackgroundColor = "#0083B8"
textColor = "#7FFF00"
font = "sans serif"

# You can set configuration in .streamlit/config.toml or directly in the script
st.config.set_option('theme.primaryColor', primaryColor)
st.config.set_option('theme.backgroundColor', backgroundColor)
st.config.set_option('theme.secondaryBackgroundColor', secondaryBackgroundColor)
st.config.set_option('theme.textColor', textColor)
st.config.set_option('theme.font', font)

st.title(":orange[NBA Season Simulation Dashboard]")

# Function to convert image file to a data URI
def get_base64_of_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Define the path to your background image
background_image_path = 'visualizations/trophy2.png'
new_directory = os.path.join(os.getcwd(), background_image_path)
# Convert your image to a data URI
image_data_uri = get_base64_of_image(new_directory)

# Use local CSS to set the background image by injecting it with Markdown
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{image_data_uri}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    <div class="overlayBg"></div>
""", unsafe_allow_html=True)

# Function to run the predictions and simulations

def run_simulation(season, num_iterations):
    y_pred, y_test, schedule_df, model = get_predictions(season, num_iterations)
    schedule_df['result_pred'] = y_pred
    eastern_results_df, western_results_df, accuracy, report = simulate_seasons(schedule_df, eastern_teams, western_teams, y_test, y_pred)
    return eastern_results_df, western_results_df, accuracy, report

st.markdown(
    """
    <style>
    .big-font {
        font-size:25px !important;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Display the labels with a bigger font
st.markdown('<p class="big-font">Enter the Season Year</p>', unsafe_allow_html=True)

season = st.number_input(":orange[Year Range we support: 2021-2023]", min_value=2021, max_value = 2023, value=2023)

st.markdown('<p class="big-font">Enter Number of Iterations for Simulation</p>', unsafe_allow_html=True)
num_iterations = st.number_input(":orange[Please input a positive odd integer]", min_value=1, value=3)

if st.button("Run Simulation"):
    with st.spinner("Running the simulation..."):
        eastern_results_df, western_results_df, accuracy, report = run_simulation(season, num_iterations)
        formatted_accuracy = "{:.2%}".format(accuracy)
        report_df = pd.DataFrame(report).transpose()
    st.header(":violet[Model Performance]")

    col1, col2 = st.columns([1, 3])

    # Display the accuracy as a metric on the left
    with col1:
        st.metric(label="Accuracy", value=formatted_accuracy)

    st.markdown("""
    <style>
    .stMetric {
        border: 3px solid #09ab3b;
        border-radius: 7px;
        padding: 7px;
    }
    .stDataFrame {
        font-size: 26px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Display the classification report on the right
    with col2:
        st.subheader(":violet[Classification Report]")
        st.dataframe(report_df.style.format("{:.2f}").highlight_max(axis=0), width=800, height=220)


    st.success("Simulation Completed!")

    st.subheader(":violet[Conference Results]")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(":violet[Eastern Conference]")
        st.dataframe(eastern_results_df, width=500, height=570)

    with col2:
        st.subheader(":violet[Western Conference]")
        st.dataframe(western_results_df, width=500, height=570)

    st.subheader(":violet[Teams that Make the Playoffs After the Play-in Games]")
    col3, col4 = st.columns(2)

    ranking_east_df, ranking_west_df = get_playoff_teams(eastern_results_df, western_results_df, season = 2023)

    with col3:
        st.subheader(":violet[East Playoff Teams]")
        st.dataframe(ranking_east_df, width=500, height=330)

    with col4:
        st.subheader(":violet[West Playoff Teams]")
        st.dataframe(ranking_west_df, width=500, height=330)

def display_matchups(series_scores, title):

    st.markdown("""
    <style>
    .big-font {
        font-size:35px !important;
        font-weight: bold;
    }
    .text-font {
        font-size:25px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Use the custom CSS classes
    st.markdown(f'<p class="big-font">{title}</p>', unsafe_allow_html=True)
    for score in series_scores:
        st.markdown(f'<p class="text-font">{score}</p>', unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------------------
# Codes for simulating playoffs, the same one as simulate_playoffs
query_train = f'SELECT * FROM real_total_feature_matrix_data'
df_train = pd.read_sql_query(query_train, engine)

def get_playoff_info(season):

    query = f'SELECT * FROM predicted_{season - 1}_{season % 100}_west_playoffs_teams'
    west_df = pd.read_sql_query(query, engine)

    query = f'SELECT * FROM predicted_{season - 1}_{season % 100}_east_playoffs_teams'
    east_df = pd.read_sql_query(query, engine)

    playoff_matchups_west = [
        (west_df.iloc[0]['Rankings'], west_df.iloc[7]['Rankings']),
        (west_df.iloc[1]['Rankings'], west_df.iloc[6]['Rankings']),
        (west_df.iloc[2]['Rankings'], west_df.iloc[5]['Rankings']),
        (west_df.iloc[3]['Rankings'], west_df.iloc[4]['Rankings']),
    ]

    playoff_matchups_east = [
        (east_df.iloc[0]['Rankings'], east_df.iloc[7]['Rankings']),
        (east_df.iloc[1]['Rankings'], east_df.iloc[6]['Rankings']),
        (east_df.iloc[2]['Rankings'], east_df.iloc[5]['Rankings']),
        (east_df.iloc[3]['Rankings'], east_df.iloc[4]['Rankings']),
    ]

    return playoff_matchups_east, playoff_matchups_west, west_df, east_df

def simulate_series(matchups, season, num_iterations):

    X_train = df_train[df_train['season'].isin(range(2015, season))].iloc[:, 12:-3]
    y_train = df_train[df_train['season'].isin(range(2015, season))]['result']

    winning_teams = []
    series_score = []
    for matchup in matchups:
        team2, team1 = matchup

        team1_wins, team2_wins = 0, 0
        for game_number in range(1, 8):
            if game_number in [1, 2, 5, 7]:
                home_team, away_team = team2, team1
                result = get_single_game_result(home_team, away_team, X_train, y_train, num_iterations)
                if result == 1:
                    team2_wins += 1
                else:
                    team1_wins += 1
            else:
                home_team, away_team = team1, team2

                result = get_single_game_result(home_team, away_team, X_train, y_train, num_iterations)
                if result == 1:
                    team2_wins += 1
                else:
                    team1_wins += 1
            if team1_wins == 4 or team2_wins == 4:
                print(f'Finish one Simulation')
                break

 
        winning_team = team1 if team1_wins > team2_wins else team2
        winning_teams.append(winning_team)
        series_score.append(f"{team1} vs {team2} - {team1_wins}:{team2_wins}")

    return winning_teams, series_score


def simu_other_rounds(winning_teams, season, num_iterations, conf):
    winning_teams_2nd = []
    second_round_matchups = []

    team1 = winning_teams[0]
    team2 = winning_teams[3]
    second_round_matchups.append((team1, team2))

    team1 = winning_teams[1]
    team2 = winning_teams[2]
    second_round_matchups.append((team1, team2))

    winning_teams_2nd_round, series_score_2nd_round = simulate_series(second_round_matchups, season, num_iterations)
    winning_teams_3rd = []
    third_round_matchups = []

    team1 = winning_teams_2nd_round[0]
    team2 = winning_teams_2nd_round[1]
    third_round_matchups.append((team1, team2))

    winning_teams_3rd_round, series_score_3rd_round = simulate_series(third_round_matchups, season, num_iterations)
    if conf == 'West':
        conf_winner = winning_teams_3rd_round[0]
        conf_winner_regular_wins = west_df[west_df['Rankings'] == conf_winner]['Wins'].iloc[0]
    elif conf == 'East':
        conf_winner = winning_teams_3rd_round[0]
        conf_winner_regular_wins = east_df[east_df['Rankings'] == conf_winner]['Wins'].iloc[0]

    return winning_teams_2nd_round, series_score_2nd_round, winning_teams_3rd_round, \
           series_score_3rd_round, conf_winner_regular_wins, conf_winner

def simu_finals(western_winner_regular_wins, eastern_winner_regular_wins, season, num_iterations):

    final_matchups = []

    if western_winner_regular_wins >= eastern_winner_regular_wins:
        final_matchups.append((western_winner, eastern_winner))

        champion, series_score_final = simulate_series(final_matchups, season, num_iterations)
    else:
        final_matchups.append((eastern_winner, western_winner))

        champion, series_score_final = simulate_series(final_matchups, season, num_iterations)

    return champion[0], series_score_final

playoff_matchups_east, playoff_matchups_west, west_df, east_df = get_playoff_info(season)
if st.button("Simulate Playoffs"):
    winning_teams_1st_round_west, series_score_1st_round_west = simulate_series(playoff_matchups_west, season, num_iterations)
    winning_teams_2nd_round_west, series_score_2nd_round_west, winning_teams_3rd_round_west, \
    series_score_3rd_round_west, western_winner_regular_wins, western_winner = simu_other_rounds(winning_teams_1st_round_west,
                                                                                season, num_iterations, conf = 'West')

    winning_teams_1st_round_east, series_score_1st_round_east = simulate_series(playoff_matchups_east, season, num_iterations)
    winning_teams_2nd_round_east, series_score_2nd_round_east, winning_teams_3rd_round_east, \
    series_score_3rd_round_east, eastern_winner_regular_wins, eastern_winner = simu_other_rounds(winning_teams_1st_round_east, 
                                                                                season, num_iterations, conf = 'East')

    series_all = series_score_1st_round_west
    series_all.extend(series_score_2nd_round_west)
    series_all.extend(series_score_3rd_round_west)
    series_all.extend(series_score_1st_round_east)
    series_all.extend(series_score_2nd_round_east)
    series_all.extend(series_score_3rd_round_east)

    champion, series_score_final = simu_finals(western_winner_regular_wins, eastern_winner_regular_wins, season, num_iterations)

    series_all.extend(series_score_final)

    #------------------------------------------------------------------------------------------------------------
    
    with st.spinner("Simulating the NBA Playoffs..."):
        series_all = series_all

    st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .text-font {
        font-size:20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Create columns for Western and Eastern conference
    col_west, col_east = st.columns(2)

    with col_west:
        display_matchups(series_all[:4], "Western Conference First Round")
        display_matchups(series_all[4:6], "Western Conference Semifinals")
        display_matchups(series_all[6:7], "Western Conference Finals")

    with col_east:
        display_matchups(series_all[7:11], "Eastern Conference First Round")
        display_matchups(series_all[11:13], "Eastern Conference Semifinals")
        display_matchups(series_all[13:14], "Eastern Conference Finals")

    # Display the finals
    st.markdown(f'<p style="color:red; font-size: 35px;">NBA Finals</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:red; font-size: 25px;">{series_all[-1]}</p>', unsafe_allow_html=True)

    st.success("Playoffs Simulation Completed!")
    st.markdown(f'<p style="color:red; font-size: 40px;">The Champion is {champion}!</p>', unsafe_allow_html=True)
