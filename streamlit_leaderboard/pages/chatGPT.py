from openai import OpenAI
import streamlit as st
from leaderboard_utils.utils import utility_config,validate_credentials,scp_file,write_file,split,extract_code
from main_app import config, openAI_utils
import uuid
from trubrics.integrations.streamlit import FeedbackCollector
import logging, os, json

logging.basicConfig(filename='GPTLogs.log',level=logging.ERROR)


@st.cache_data
def init_trubrics():
    email = st.secrets.TRUBRICS_EMAIL
    password = st.secrets.TRUBRICS_PASSWORD
    try:
        collector = FeedbackCollector(
            email=st.secrets.TRUBRICS_EMAIL,
            password=st.secrets.TRUBRICS_PASSWORD,
            project=st.secrets.TRUBRICS_DATANAME  # Specify your Trubrics project name
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

if "username" not in st.session_state:
    st.error("You need to log in first! Click on log in from the side bar")
    st.stop()

# Get user credentials
username = st.session_state.username
teamname = st.session_state.teamname

with st.container():
    st.markdown(f"## Hi {st.session_state.NameOfUser} 🥷from {st.session_state.NameOfTeam} 👥 ")

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

if "disable_chat" not in st.session_state:
    st.session_state.disable_chat = False
    
if "response_contains_code" not in st.session_state:
    st.session_state.response_contains_code = False

#with st.sidebar:
#    stream = st.toggle("Stream LLM response",value=True)

if not st.session_state.submit_button_clicked:
    st.container()
    st.title("Start a Chat Session")
    ChatSessionForm = st.form(key="ChatSessionForm")
    sess_id = st.session_state.config["session_id"]
    user_session_name = ChatSessionForm.text_input("Session Name", placeholder=f"Session-{sess_id}", value = f"Session-{sess_id}")
    user_session_context = ChatSessionForm.text_input("Session Context", placeholder="Enter the context you would like to set for this session", value=None)
    submit_button = ChatSessionForm.form_submit_button("Start Chat Session")
    st.session_state["messages"] = openAI_utils.setContext()
    #stream = st.toggle("Stream LLM Response",value=True)

    if submit_button:
        st.session_state.user_session_name = user_session_name
        st.session_state.user_session_context = user_session_context
        st.session_state.submit_button_clicked = True
        if(user_session_context):
            st.markdown(f"Your set context : {user_session_context}")
            st.session_state['messages']+= openAI_utils.setContext(st.session_state.user_session_context)
        st.session_state.len_context = len(st.session_state['messages'])
        st.session_state.disable_chat = False
        print(st.session_state.len_context)
        


if st.session_state.submit_button_clicked:
    with st.sidebar:
        st.subheader("💼 Sessions")
        st.session_state.stream = st.toggle("Stream LLM response",value=True)
        st.sidebar.text(f"Session: {st.session_state.user_session_name}")
        st.sidebar.text(f"Tokens used: {st.session_state.total_tokens/1000}k / 12k")
        st.session_state.config["session_id"] += 1
        if st.button("Start New Session"):
            cfg = st.session_state.get("config")
            cfg["session_id"]+=1
            cfg["tokens_used"]+= st.session_state.get("total_tokens", 0)
            with open(os.path.join(st.session_state.userDir, "status.json"), 'w') as ifile:
                json.dump(cfg, ifile)
            st.session_state.submit_button_clicked = False
            st.session_state.show_feedback_controls = False
            st.session_state.aws_state = False
            st.session_state.messages = []
            st.session_state.prompt_ids = []
            st.session_state.total_tokens = 0
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.last_message_count = 0
            st.session_state.len_context = 0
            # updated session_id in user folder
            
            
            st.rerun()

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
    
    avatars = {"user" : "🧑‍🔬", "assistant" : "🤖"}

    for n, msg in enumerate(messages):
        if(msg["role"] != "system"):
            st.chat_message(msg["role"], avatar = avatars[msg["role"]]).write(msg["content"])
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
            try:
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
            except IndexError as e:
                st.error("Please slow down...")
                logging.error(f"{st.session_state.username} double typed.",exc_info=True)


    if st.session_state.total_tokens > openAI_utils.MAX_CONTENT_LENGTH:
        st.error("You have exceeded the maximum number of tokens, please start a new session")
        st.session_state.disable_chat = True
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
    
    #gen_form = st.form(key="generation_form")
    if prompt := st.chat_input("Ask your question",disabled=st.session_state.disable_chat):
        st.session_state.disable_chat = True
        messages.append({"role": "user", "content": prompt})
        st.chat_message("user", avatar = "🧑‍🔬").write(prompt)
        client = OpenAI(api_key=st.secrets.openAI_keys.get(f"{teamname}_{username}"))

        with st.chat_message("assistant", avatar = "🤖"):
            if st.session_state.stream:
                message_placeholder = st.empty()
                generation = ""
                try:
                    for part in client.chat.completions.create(model=model, messages=messages, stream=True,temperature = openAI_utils.TEMPERATURE, max_tokens=openAI_utils.MAX_TOKENS):
                        generation += part.choices[0].delta.content or ""
                        message_placeholder.markdown(generation + "▌")
                    message_placeholder.markdown(generation)
                except:
                    st.session_state.disable_chat = True
                    st.error("Dont do that. Username logged.")
                    logging.error(f"{st.session_state.username} injected an enormous prompt.",exc_info=True)
                    st.stop()
            else:
                try:
                    response = client.chat.completions.create(model=model, messages=messages,temperature = openAI_utils.TEMPERATURE, max_tokens=openAI_utils.MAX_TOKENS)
                    generation = response.choices[0].message.content
                    st.write(generation)
                except:
                    st.session_state.disable_chat = True
                    st.error("Dont do that. Username logged.")
                    logging.error(f"{st.session_state.username} injected an enormous prompt.",exc_info=True)
                    st.stop()
            messages.append({"role": "assistant", "content": generation})
            st.session_state.total_tokens += openAI_utils.num_tokens_from_messages(messages)
    
            logged_prompt = collector.log_prompt(
                config_model={"model": model},
                prompt=prompt,
                generation=generation,
                session_id=st.session_state.session_id,
                tags=tags,                    
                user_id=username,
                metadata=custom_data,
            )
            st.error('Please slow down...')
            logging.error(f"{st.session_state.username} spammed chat.",exc_info=True)
            st.session_state.disable_chat = False

            st.session_state.prompt_ids.append(logged_prompt.id)
            print(st.session_state.total_tokens)
            st.session_state.disable_chat = False
            st.rerun()


# Check if the generated response contains code
st.session_state.response_contains_code = any(
    "```" in msg["content"] for msg in st.session_state.messages if msg["role"] == "assistant"
)


# Show "Push to AWS" button only if response contains code
if st.session_state.response_contains_code and not st.session_state.show_feedback_controls:
    aws_push_button = st.button("Push to AWS instance")
    if aws_push_button:
        st.session_state.show_feedback_controls = True
        # Extract code from assistant's messages

# Check if the user clicked "Push to AWS" and show feedback controls
if st.session_state.show_feedback_controls:
    user_feedback_text = st.text_input("Enter file name (.py):")
    if (st.button("Push now")):
        with st.spinner("Checking for file naming conventions"):
            if (user_feedback_text.split(".")[-1] != "py"):
                st.error("Only python extensions allowed, rename correctly !!")
            else:
                st.info("Great convention is correct")
        with st.spinner("Pushing code to your AWS Instance"):
            
            code = extract_code(messages)
            code,text,name = split(code)    
            file_path = write_file(user_feedback_text, code, st.session_state.userDir)
            # 
            return_code = scp_file(file_path, 
                                   r"/home/user/workspace", 
                                   True, 
                                   st.secrets.instances[f"{st.session_state.teamname}_{st.session_state.username}"]
                                   )
            if (return_code != 0):
                st.error(f"Push Error with Return Code: {return_code}. Retry or contact help in slack :slack:")        
            st.session_state.show_feedback_controls = False
            st.session_state.response_contains_code = False
    elif st.button("Cancel"):
        st.session_state.show_feedback_controls = False  # Hide controls
        st.session_state.response_contains_code = True
    else:
        pass