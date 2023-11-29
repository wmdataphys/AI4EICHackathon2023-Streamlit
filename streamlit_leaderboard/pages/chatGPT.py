from openai import OpenAI
import streamlit as st
from leaderboard_utils.utils import utility_config,validate_credentials,scp_file,write_file,split,extract_code
from main_app import config, openAI_utils
from trubrics.integrations.streamlit import FeedbackCollector


st.set_page_config(page_title="Chat Bot", page_icon=":robot_face:", layout="wide", initial_sidebar_state="auto")
# Custom CSS to hide copy button in the code block
custom_css = """
<style>
.css-1bd8bfl .stCodebox button {
    display: none !important;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
st.title("Welcome to AI4EIC Hackathon 2023")
st.divider()
st.header("💬 AI4EIC Hackathon Assistant")

if "logged_in" not in st.session_state:
    st.error("You need to log in first! Click on log in from the side bar")
    st.stop()
    
# Get user credentials
username = st.session_state.username
teamname = st.session_state.teamname

if "Chat_sessionID" not in st.session_state:
    st.session_state["Chat_sessionID"] = str(uuid.uuid4())
    st.container()
    st.title("Start a Chat Session")
    ChatSessionForm = st.form(key="ChatSessionForm")
    ChatSessionForm.text_input("Session Name", key="Chat_sessionName", placeholder = "Enter a name for your session", default = "Session")
    stream = st.toggle("Stream LLM response", value=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = openAI_utils.GPT_MODEL

if "messages" not in st.session_state:
    st.session_state.messages = openAI_utils.setContext()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your prompt here"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"], 
            max_tokens=openAI_utils.MAX_TOKENS, 
            temperature=openAI_utils.TEMPERATURE,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})