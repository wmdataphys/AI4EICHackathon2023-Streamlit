from openai import OpenAI
import streamlit as st
from leaderboard_utils.utils import utility_config,validate_credentials,scp_file,write_file,split,extract_code
from main_app import config, openAI_utils
import uuid
from trubrics.integrations.streamlit import FeedbackCollector



@st.cache_data
def init_trubrics():
    email = st.secrets.TRUBRICS_EMAIL
    password = st.secrets.TRUBRICS_PASSWORD
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

if "user_session_context" not in st.session_state:
    st.session_state.user_session_context = None

if "user_session_name" not in st.session_state:
    st.session_state.user_session_name = 'Default'

if "stream" not in st.session_state:
    st.session_state.stream = True

if "submit_button_clicked" not in st.session_state:
    st.session_state.submit_button_clicked = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

if "len_context" not in st.session_state:
    st.session_state.len_context = 0

if "response_contains_code" not in st.session_state:
    st.session_state.response_contains_code = False

if "show_feedback_controls" not in st.session_state:
    st.session_state.show_feedback_controls = False

if "push_button_clicked" not in st.session_state:
    st.session_state.push_button_clicked = False

if "last_message_count" not in st.session_state:
    st.session_state.last_message_count = 0

if "aws_state" not in st.session_state:
    st.session_state.aws_state = True

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

#with st.sidebar:
#    stream = st.toggle("Stream LLM response",value=True)

if not st.session_state.submit_button_clicked:
    st.session_state["Chat_sessionID"] = str(uuid.uuid4())
    st.container()
    st.title("Start a Chat Session")
    ChatSessionForm = st.form(key="ChatSessionForm")
    user_session_name = ChatSessionForm.text_input("Session Name", placeholder="Enter a name for your session")
    user_session_context = ChatSessionForm.text_input("Session Context", placeholder="Enter the context you would like to set for this session", value=None)
    submit_button = ChatSessionForm.form_submit_button("Start Chat Session")
    #stream = st.toggle("Stream LLM Response",value=True)

    if submit_button:
        st.session_state.user_session_name = user_session_name
        st.session_state.user_session_context = user_session_context
        st.session_state.submit_button_clicked = True
        st.session_state['messages']= openAI_utils.setContext(st.session_state.user_session_context)
        st.session_state.len_context = len(st.session_state['messages'])
        print(st.session_state.len_context)


if st.session_state.submit_button_clicked:
    with st.sidebar:
        st.subheader("Options")
        st.session_state.stream = st.toggle("Stream LLM response",value=True)
        st.sidebar.text(f"Number of tokens used: {st.session_state.total_tokens}")
        if st.button("Start New Session"):
            st.session_state.submit_button_clicked = False
            st.session_state.show_feedback_controls = False
            st.session_state.aws_state = False
            st.session_state.messages = []
            st.session_state.prompt_ids = []
            st.session_state.total_tokens = 0
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.last_message_count = 0
            st.session_state.len_context = 0
            st.experimental_rerun()
    
    st.write(f"Session Name: {st.session_state.user_session_name}")
    st.write(f"Session Context: {st.session_state.user_session_context}")
    collector = init_trubrics()
    custom_data ={"session_name":st.session_state.user_session_name,
                  "session_context":st.session_state.user_session_context,
                  "tokens_used":st.session_state.total_tokens}

    if "prompt_ids" not in st.session_state:
        st.session_state["prompt_ids"] = []

    if "aws_push" not in st.session_state:
        st.session_state["aws_push"] = False

    model = openAI_utils.GPT_MODEL
    tags = [f"llm_chatbot{'_stream' if st.session_state.stream else ''}.py"]

    messages = st.session_state.messages

    for n, msg in enumerate(messages):
        st.chat_message(msg["role"]).write(msg["content"])
        if msg["role"] == "assistant" and n > st.session_state.len_context:
            feedback_key = f"feedback_{int(n / 2)}"
            #print("n:", n, "len(prompt_ids):", len(st.session_state.prompt_ids))
            #prompt_index = int(n / 3) - 1
            #print("prompt_index:", prompt_index)
            #print("st.session_state.prompt_ids:", st.session_state.prompt_ids)
            #prompt_id = st.session_state.prompt_ids[prompt_index] if prompt_index >= 0 else None
            #print("prompt_id:", prompt_id)

            #if feedback_key not in st.session_state:
            #    st.session_state[feedback_key] = None

            #if prompt_index >= 0 and prompt_index < len(st.session_state.prompt_ids):
            #    prompt_id = st.session_state.prompt_ids[prompt_index]
            #else:
            #    prompt_id = None
            feedback = collector.st_feedback(
                component="default",
                feedback_type="thumbs",
                open_feedback_label="[Optional] Provide additional feedback",
                model=model,
                tags=tags,
                key=feedback_key,
                prompt_id=st.session_state.prompt_ids[int(n/3)-1],
                user_id=username,
            )
            if feedback:
                with st.sidebar:
                    st.write(":orange[Here's the raw feedback you sent to [Trubrics](https://trubrics.streamlit.app/):]")
                    st.write(feedback)
    


    if st.session_state.total_tokens > 12000:
        st.error("You have exceeded the maximum number of tokens, please start a new session")
        if st.button("Start New Session",key='MaxTokensReached'):
            st.session_state.submit_button_clicked = False
            st.session_state.show_feedback_controls = False
            st.session_state.aws_state = False
            st.session_state.messages = []
            st.session_state.prompt_ids = []
            st.session_state.total_tokens = 0
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.last_message_count = 0
            st.session_state.len_context = 0
            st.rerun()
    
    #gen_form = st.form(key="generation_form")
    if prompt := st.chat_input("Ask your question"):
        messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

        with st.chat_message("assistant"):
            if st.session_state.stream:
                message_placeholder = st.empty()
                generation = ""
                for part in client.chat.completions.create(model=model, messages=messages, stream=True,temperature = openAI_utils.TEMPERATURE, max_tokens=openAI_utils.MAX_TOKENS):
                    generation += part.choices[0].delta.content or ""
                    message_placeholder.markdown(generation + "▌")
                message_placeholder.markdown(generation)
            else:
                response = client.chat.completions.create(model=model, messages=messages,temperature = openAI_utils.TEMPERATURE, max_tokens=openAI_utils.MAX_TOKENS)
                generation = response.choices[0].message.content
                st.write(generation)

            messages.append({"role": "assistant", "content": generation})
            st.session_state.total_tokens += openAI_utils.num_tokens_from_messages(messages)
            logged_prompt = collector.log_prompt(
                config_model={"model": model},
                prompt=prompt,
                generation=generation,
                session_id=st.session_state.session_id,
                tags=tags,
                user_id=username,
            )
            st.session_state.prompt_ids.append(logged_prompt.id)
            print(st.session_state.total_tokens)
            st.rerun()

# Check if the generated response contains code
response_contains_code = any(
    "```" in msg["content"] for msg in st.session_state.messages if msg["role"] == "assistant"
)

# Check if the generated response contains code
response_contains_code = any(
    "```" in msg["content"] for msg in st.session_state.messages if msg["role"] == "assistant"
)


# Show "Push to AWS" button only if response contains code
if response_contains_code and not st.session_state.show_feedback_controls:
    if st.button("Push to AWS"):
        st.session_state.show_feedback_controls = True
        # Extract code from assistant's messages

# Check if the user clicked "Push to AWS" and show feedback controls
if st.session_state.show_feedback_controls:
    user_feedback_text = st.text_area("Enter file name:")
    if st.button("Push"):
        try:
            code = extract_code(messages)
            code,text,name = split(code)
            file_path = write_file(user_feedback_text, code,username)
            scp_file(file_path, r"/home/user/workspace", True)
            st.session_state.show_feedback_controls = False
            st.rerun()
        except:
            st.session_state.show_feedback_controls = False
            st.error("Error, invalid filename.")
    elif st.button("Cancel"):
        st.session_state.show_feedback_controls = False  # Hide controls
        st.rerun()
