import streamlit as st
import streamlit_authenticator as stauth
import os, json


def authenticate_user(teamname:str, username:str, password:str) -> bool:
    creds = st.secrets.passwords.get(f'{teamname}_{username}', None)
    config = None
    with open(os.path.join(st.secrets.UserInfoDir, f'{teamname}', f'{username}', 'status.json'), 'r') as file:
        config = json.load(file)
    if (config["status"] == "LOGGED_IN"):
        st.error("You are already logged in!!! Cannot open two sessions at the same time", icon = "❌")
        st.error("Close Previous Session", icon = "❌")
    elif (creds == password):
        st.session_state["logged_in"] = True
        st.session_state["teamname"] = teamname
        st.session_state["username"] = username
        st.session_state["password"] = password
        st.session_state["OPENAI_API_KEY"] = "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"
        with open(os.path.join(st.secrets.UserInfoDir, 'status.json'), 'w') as file:
            config["status"] = "LOGGED_IN"
            json.dump(config, file)
        st.info(f"Login Successful Welcome {username} from {teamname}", icon="✅")
        st.balloons()
    else:
        st.error("Login Failed! Check your credentials!!!", icon = "❌")
        
    
st.set_page_config(page_title="Login", page_icon=":robot_face:", layout="wide", initial_sidebar_state="auto")
st.title("Welcome to AI4EIC Hackathon 2023")
st.divider()

st.header("Login to get started")

with st.container():
    with st.form("Login Form"):
        st.markdown("## Enter your credentials")
        teamname = st.text_input("Team Name", placeholder = "Enter your team name")
        username = st.text_input("Username", placeholder = "Enter your username")
        password = st.text_input("Password", type = "password", placeholder = "Enter your password")
        login_button = st.form_submit_button(label = "Login", kwargs = {"teamname":teamname, "username":username, "password":password})
        if (login_button):
            authenticate_user(teamname, username, password)
            