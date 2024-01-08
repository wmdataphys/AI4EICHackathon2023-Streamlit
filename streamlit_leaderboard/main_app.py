from leaderboard_utils.utils import OPENAI_Utils, get_leaderboard_dataframe, log_out
import json, sys, os
from yaml.loader import SafeLoader
import streamlit as st
import pandas as pd

openAI_utils = OPENAI_Utils()

BASE_DIR = st.secrets.base_dir
sys.path.append(BASE_DIR)

with open(os.path.join(BASE_DIR, "UserInfo", "users.json")) as file:
    config = json.load(file)

st.set_page_config(
    page_title="AI4EIC Hackathon 2023",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://eic.ai',
        'About': "# AI4EIC Hackathon 2023"
    }
)

st.title("Welcome to AI4EIC Hackathon 2023")
st.divider()
# Have a timer here

if "updated_leaderboard" not in st.session_state:
    st.session_state.updated_leaderboard = False
with st.container():
    st.markdown("## AI4EIC Hackathon 2023")
    st.markdown("### Welcome to the AI4EIC Hackathon 2023. Navigate to the different pages of the hackathon.")

with st.container():
    with st.container():
        if False:
            df_leaderboard = get_leaderboard_dataframe(csv_file = os.path.join(st.secrets["UserInfoDir"], 'leaderboard.csv'), greater_is_better = True)
            st.write(df_leaderboard)
        else:
            columns = ['Team#','Team Name','Username','Name of User','Q1 Score','Q2 Score','Total Score']
            df = pd.read_csv(os.path.join(st.secrets["UserInfoDir"], 'leaderboard.csv'))
            df.columns = columns
            df["Total Score"] = df["Q1 Score"] + df["Q2 Score"]
            st.write(df)


