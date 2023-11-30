import streamlit as st 
import os, json, time


st.set_page_config(page_title="Profile and Submit", page_icon=":robot_face:", layout="wide", initial_sidebar_state="auto")
st.title("Welcome to AI4EIC Hackathon 2023")
st.divider()

#if (not st.session_state.get("username")):
#    st.error("You have to be logged in to access this page. Login in")
#    st.stop()

with st.container():
    with st.form("submit_form"):
        st.markdown("## Submit new Solution")
        QuestionNumber = st.text_input("Question Number", placeholder = "Enter the question number")
        file_path = st.text_input("File Path", placeholder = r"Enter the path to the full file from your instance. only `.py` files")
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button(label = "Submit for grading")
            if (submit_button):
                submissionText = "Your solution is being submitted for grading"
                progress_bar = st.progress(0, submissionText)
                for percent_complete in range(10):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 10, text = submissionText)
                time.sleep(0.5)
                progress_bar.empty()
        
    
with st.container():
    st.markdown("## Stats for " + st.session_state.get("username"))
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of correct submissions")
    st.markdown("### Total number of incorrect submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")
    st.markdown("### Total number of submissions")