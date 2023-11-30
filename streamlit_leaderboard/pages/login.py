import streamlit as st
import streamlit_authenticator as stauth
import os, json
from leaderboard_utils.utils import clear_all


def authenticate_user(teamname:str, username:str, password:str) -> bool:
    creds = st.secrets.passwords.get(f'{teamname}_{username}', None)
    config = None
    if (creds == password):
        st.session_state["logged_in"] = True
        st.session_state["teamname"] = teamname
        st.session_state["username"] = username
        st.session_state["password"] = password
        st.session_state["userDir"] = os.path.join(st.secrets.UserInfoDir, f'{teamname}', f'{username}')
        with open(os.path.join(st.session_state.userDir, 'status.json'), 'r') as jfile:
            config = json.load(jfile)
        st.session_state["config"] = config
        if (config["status"] == "LOGGED_IN"):
            st.error("You are already logged in!!! Cannot open two sessions at the same time", icon = "❌")
            st.error("Close Previous Session below go to logout page in left", icon = "❌")
            st.stop()
        else:
            st.session_state["OPENAI_API_KEY"] = st.secrets.OPENAI_API_KEY
            with open(os.path.join(st.session_state.userDir, 'status.json'), 'w') as jwfile:
                config["status"] = "LOGGED_IN"
                json.dump(config, jwfile)
            st.success(f"Great you are logged in!! Welcome {username}")
            st.balloons()
    else:
        st.error("Incorrect Credentials. Login with correct credentials", icon = "❌")
        st.stop()
        
    
st.set_page_config(page_title="Login", page_icon=":robot_face:", layout="wide", initial_sidebar_state="auto")
st.title("Welcome to AI4EIC Hackathon 2023")
st.divider()
st.header("Login to get started")

with st.container():
    with st.form("login_form"):
        st.markdown("## Enter your credentials")
        teamname = st.text_input("Team Name", placeholder = "Enter your team name")
        username = st.text_input("Username", placeholder = "Enter your username")
        password = st.text_input("Password", type = "password", placeholder = "Enter your password")
        login_button = st.form_submit_button(label = "Login", kwargs = {"teamname":teamname, "username":username, "password":password})
        if (login_button):
            authenticate_user(teamname, username, password)   
            