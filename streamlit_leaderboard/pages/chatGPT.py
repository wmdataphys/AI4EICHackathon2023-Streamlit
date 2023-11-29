from openai import OpenAI
import streamlit as st
from leaderboard_utils.utils import utility_config,validate_credentials,scp_file,write_file,split,extract_code
from main_app import config, openAI_utils
import uuid
from trubrics.integrations.streamlit import FeedbackCollector


#st.set_page_config(page_title="Chat Bot", page_icon=":robot_face:")
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
    ChatSessionForm.text_input("Session Name", key="Chat_sessionName", placeholder = "Enter a name for your session", default = "Session-")
    ChatSessionForm.text_input("Session Context", key="Chat_sessionUserContext", placeholder = "Enter a the context you would like to set for this session")
    button = ChatSessionForm.form_submit_button("Start Chat Session")
    stream = st.toggle("Stream LLM response", value=True)

@st.cache_data
def init_trubrics(email, password):
    email = st.secrets.TRUBRICS_EMAIL
    password = st.secrets.TRUBRICS_PASSWORD
    print(password,email)
    try:
        collector = FeedbackCollector(
            email=st.secrets.TRUBRICS_EMAIL,
            password=st.secrets.TRUBRICS_PASSWORD,
            project="Hackathon"  # Specify your Trubrics project name
        )
        return collector
    except Exception:
        st.error(f"Error authenticating '{email}' with [Trubrics](https://trubrics.streamlit.app/). Please try again.")
        st.stop()


collector = init_trubrics(username, password)
if "messages" not in st.session_state:
    st.session_state.messages = openAI_utils.setContext()
    st.session_state["messages"].append([{"role": "assistant", "content": "How can I help you?"}])
    
if "prompt_ids" not in st.session_state:
    st.session_state["prompt_ids"] = []
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "show_feedback_controls" not in st.session_state:
    st.session_state.show_feedback_controls = False

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = openAI_utils.GPT_MODEL
tags = [f"llm_chatbot{'_stream' if stream else ''}.py"]

messages = st.session_state.messages

for n, msg in enumerate(messages):
    if(msg['role']!="system"):
        st.chat_message(msg["role"]).write(msg["content"])

    if msg["role"] == "assistant" and n > 1:
        feedback_key = f"feedback_{int(n / 2)}"

        if feedback_key not in st.session_state:
            st.session_state[feedback_key] = None
        feedback = collector.st_feedback(
            component="default",
            feedback_type="thumbs",
            open_feedback_label="[Optional] Provide additional feedback",
            model=model,
            tags=tags,
            key=feedback_key,
            prompt_id=st.session_state.prompt_ids[int(n / 2) - 1],
            user_id=username,
        )
        if feedback:
            with st.sidebar:
                st.write(":orange[Here's the raw feedback you sent to [Trubrics](https://trubrics.streamlit.app/):]")
                st.write(feedback)

if prompt := st.chat_input("Ask your question"):
    messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        client = OpenAI(api_key=openai_api_key)

    with st.chat_message("assistant"):
        if stream:
            message_placeholder = st.empty()
            generation = ""
            for part in client.chat.completions.create(model=model, messages=messages, stream=True):
                generation += part.choices[0].delta.content or ""
                message_placeholder.markdown(generation + "▌")
            message_placeholder.markdown(generation)
        else:
            response = client.chat.completions.create(model=model, messages=messages)
            generation = response.choices[0].message.content
            st.write(generation)

        logged_prompt = collector.log_prompt(
            config_model={"model": model},
            prompt=prompt,
            generation=generation,
            session_id=st.session_state.session_id,
            tags=tags,
            user_id=username,
        )
        st.session_state.prompt_ids.append(logged_prompt.id)
        messages.append({"role": "assistant", "content": generation})
        st.rerun()  # force rerun of app, to load last feedback component
        # Add button to open text box
        # Show "Push to AWS" button

# Check if the generated response contains code
response_contains_code = any(
    "```" in msg["content"] for msg in messages if msg["role"] == "assistant"
)


# Show "Push to AWS" button only if response contains code
if response_contains_code and not st.session_state.show_feedback_controls:
    if st.button("Push to AWS"):
        st.session_state.show_feedback_controls = True
        # Extract code from assistant's messages

# Check if the user clicked "Push to AWS" and show feedback controls
if st.session_state.show_feedback_controls:
    user_feedback_text = st.text_area("Enter file name:")
    my_bar = st.progress(0, text="Uploading...")
    if st.button("Push"):
        # Execute your function using user_feedback_text and extracted code
        print('Pushing to AWS:')
        
        #code = extract_code(messages)
        print('messages:',messages)
        code = extract_code(messages)
        print('extract code:',code)
        code,text,name = split(code)
        print(code)
        file_path = write_file(user_feedback_text, code,username)
        scp_file(file_path, r"/home/user/workspace", True)
        st.session_state.show_feedback_controls = False
        st.rerun()
    elif st.button("Cancel"):
        st.session_state.show_feedback_controls = False  # Hide controls
        st.rerun()
