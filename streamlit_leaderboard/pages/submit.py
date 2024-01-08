import streamlit as st
from leaderboard_utils.utils import OPENAI_Utils, get_leaderboard_dataframe
from leaderboard_utils.utils import utility_config,validate_credentials,scp_file,write_file,split,extract_code
import os, json, time
#from leaderboard_utils import evaluate
import pandas as pd


def update_leaderboard(value, question):
    leaderboard_path = os.path.join(st.secrets["UserInfoDir"], 'leaderboard.csv')
    leaderboard = pd.read_csv(leaderboard_path)

    team_filter = leaderboard['teamname'] == st.session_state.teamname

    if question == 1:
        if value > leaderboard.loc[team_filter, 'QuestionAttempted'].max():
            leaderboard.loc[team_filter, 'QuestionAttempted'] = value
            leaderboard.loc[team_filter, 'Score'] = leaderboard.loc[team_filter, 'TokensUsed'].sum() + value
#        leaderboard.loc[team_filter, 'Total Submissions'] += 1

    if question == 2:
        if value > leaderboard.loc[team_filter, 'TokensUsed'].max():
            leaderboard.loc[team_filter, 'TokensUsed'] = value
            leaderboard.loc[team_filter, 'Score'] = leaderboard.loc[team_filter, 'QuestionAttempted'].max() + value
#        leaderboard.loc[team_filter, 'Total Submissions'] += 1

    leaderboard.to_csv(leaderboard_path, index=False)


st.set_page_config(page_title="Profile and Submit", page_icon=":robot_face:", layout="wide", initial_sidebar_state="auto")
st.title("Welcome to AI4EIC Hackathon 2023")
st.divider()


if "logged_in" not in st.session_state:
    st.error("You need to log in first! Click on log in from the side bar")
    st.stop()


from leaderboard_utils.evaluate import evaluate

data = {'eventID': [8,9], 'PID': [0,1]}
df = pd.DataFrame(data)

# Set up session state to persist data across sessions
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

if 'selected_question' not in st.session_state:
    st.session_state.selected_question  = False

if 'csv_file' not in st.session_state:
    st.session_state.csv_file = False

if 'selected_int' not in st.session_state:
    st.session_state.selected_int = None

if "sucess" not in st.session_state:
    st.session_state.sucess = 0

with st.container():
    with st.form("submit_form"):
        st.markdown("## Submit new Solution")
        options = [None, "Question 1", "Question 2"]
        selected_option = st.selectbox("Question Number:", options, key='question_selectbox')

        select_button = st.form_submit_button("Select")

        if selected_option is not None and select_button:
            # Store selected option in session state
            st.session_state.selected_option = selected_option
            st.write("You selected: ", selected_option)
            st.session_state.selected_int  = int(selected_option[-1])
            #st.write(st.session_state.selected_int)
            st.session_state.selected_question = True


        if st.session_state.selected_question:
            st.write("Please ensure your data is in this format: ")
            st.markdown(df.to_markdown(index=False))

            file_path = st.text_input("File Path", placeholder=r"Enter the path relative to $WORKSPACE Only `.csv` files")
            filename = file_path.split("/")[-1]
            if file_path and file_path[-4:] != '.csv' and not st.session_state.csv_file:
                st.error('Not a .csv file!')
                st.session_state.csv_file = True
                st.stop()
            else:
                st.session_state.csv_file = False

            col1, col2 = st.columns(2)

            with col1:
                submit_button = st.form_submit_button(label="Submit for grading")

                if submit_button and not st.session_state.csv_file:
                    # Access selected_option from session state
                    selected_option_from_session = st.session_state.selected_option
                    #st.write("Selected option from session state:", selected_option_from_session)

                    submission_text = "Your solution is being submitted for grading"
                    progress_bar = st.progress(0, submission_text)
    
                    for percent_complete in range(10):
                        time.sleep(0.01)
                        progress_bar.progress(percent_complete + 10, text=submission_text) 
                    dest_path =  os.path.join(st.secrets.UserInfoDir,st.session_state.userDir,'Results')
                    st.session_state.sucess =  scp_file(file_path,dest_path,False,st.secrets.instances[f'{st.session_state.teamname}_{st.session_state.username}'])
                    if st.session_state.sucess != 0:
                        st.error("Sorry, file does not exist. Try again.")
                        st.stop()
                        st.rerun()

                    status,score,uncertainty = evaluate(dest_path+"/"+filename,st.session_state.selected_int)
                    time.sleep(0.5)
                    progress_bar.empty()
                    st.write(status)
                    if score != -1:
                        st.write("Wow, what a score!")
                        st.latex(f"{score} \pm {uncertainty}")
                    time.sleep(0.5)
                    update_leaderboard(score,st.session_state.selected_int)
                    st.session_state.updated_leaderboard = True
                    #progress_bar.empty()
                    #st.stop()

#if 'selected_option' not in st.session_state:
#    st.session_state.selected_option=None

#with st.container():
#    with st.form("submit_form"):
#        st.markdown("## Submit new Solution")
#        #QuestionNumber = st.text_input("Question Number", placeholder = "Enter the question number")
#        options = [None,"Question 1","Question 2"]
#        selected_option = st.selectbox("Question Number:",options)
#        select_button = st.form_submit_button("Select")
#        if selected_option is not None and select_button:
#            st.write("You selected: ",selected_option)
#            selected_option = int(selected_option[-1])
#            st.write(selected_option)
#            
#            st.write("Please ensure your data is in this format: ")
#            st.write(df)
#
#            file_path = st.text_input("File Path", placeholder = r"Enter the path to the full file from your instance. only `.py` files")
#            col1, col2 = st.columns(2)
#            with col1:
#                submit_button = st.form_submit_button(label = "Submit for grading")
#                if (submit_button):
#                    submissionText = "Your solution is being submitted for grading"
#                    progress_bar = st.progress(0, submissionText)
#                    for percent_complete in range(10):
#                        time.sleep(0.01)
#                        progress_bar.progress(percent_complete + 10, text = submissionText)
#                    time.sleep(0.5)
#                    progress_bar.empty()
        
    
#with st.container():
#    st.markdown("## Stats for " + st.session_state.get("username"))
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of correct submissions")
#    st.markdown("### Total number of incorrect submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
#    st.markdown("### Total number of submissions")
