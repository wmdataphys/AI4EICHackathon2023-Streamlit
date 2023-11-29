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
        with open(os.path.join(st.secrets.UserInfoDir, f'{teamname}', f'{username}', 'status.json'), 'r') as file:
            config = json.load(file)
        if (config["status"] == "LOGGED_IN"):
            st.error("You are already logged in!!! Cannot open two sessions at the same time", icon = "❌")
            st.error("Close Previous Session below", icon = "❌")
            return -1
        st.session_state["OPENAI_API_KEY"] = "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"
        with open(os.path.join(st.secrets.UserInfoDir, f'{teamname}', f'{username}', 'status.json'), 'w') as file:
            config["status"] = "LOGGED_IN"
            json.dump(config, file)
        return 0
    else:
        return 1
        
    
st.set_page_config(page_title="Login", page_icon=":robot_face:", layout="wide", initial_sidebar_state="auto")
st.title("Welcome to AI4EIC Hackathon 2023")
st.divider()
st.header("Login to get started")

with st.container():
    val = -2
    with st.form("Login Form"):
        st.markdown("## Enter your credentials")
        teamname = st.text_input("Team Name", placeholder = "Enter your team name")
        username = st.text_input("Username", placeholder = "Enter your username")
        password = st.text_input("Password", type = "password", placeholder = "Enter your password")
        login_button = st.form_submit_button(label = "Login", kwargs = {"teamname":teamname, "username":username, "password":password})
        if (login_button):
            val = authenticate_user(teamname, username, password)
    if (val == 0):
        st.info(f"Login Successful Welcome {st.session_state.username} from {st.session_state.teamname}", icon="✅")
        st.balloons()
    if (val == 1):
        st.info("Login Failed! Check your credentials!!!", icon = "❌")
    if (val == -1):
        if(st.button("Logout")):
            print ("button pressed")
            if st.session_state.get("logged_in"):
                with open(os.path.join(st.secrets.UserInfoDir, f'{st.session_state.teamname}', f'{st.session_state.username}', "status.json"), 'w') as file:
                    config = json.load(file)
                    config["status"] = "LOGGED_OUT"
                    json.dump(config, file)
            clear_all()
            st.success("You have logged out successfully")    
            