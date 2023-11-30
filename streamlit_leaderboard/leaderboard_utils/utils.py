import os, tiktoken
import streamlit as st
import pandas as pd
import json

# funtions
def relative_time(t_diff):
    days, seconds = t_diff.days, t_diff.seconds
    if days > 0:
        return f"{days}d"
    else:
        hours = t_diff.seconds // 3600
        minutes = t_diff.seconds // 60
        if hours >0 : #hour
            return f"{hours}h"
        elif minutes >0:
            return f"{minutes}m"
        else:
            return f"{seconds}s"
def clear_all():
    with key in st.session_state.keys():
        del st.session_state[key]
def clear_chatSession():
    pass

def log_out():
    return True


def get_leaderboard_dataframe(csv_file = 'leaderboard.csv', greater_is_better = True):
    df_leaderboard = pd.read_csv(csv_file)
    df_leaderboard = df_leaderboard.sort_values("TotalScore", ascending = not greater_is_better)
    """
    df_leaderboard['counter'] = 1
    df_leaderboard = df_leaderboard.groupby('usernames').agg({"TotalScore": "max"})
    df_leaderboard = df_leaderboard.sort_values("TotalScore", ascending = not greater_is_better)
    df_leaderboard = df_leaderboard.reset_index()
    df_leaderboard.columns = ['usernames','TotalScore', 'TotalSubmissions', 'TokensUsed']
    """
    return df_leaderboard

def utility_config(default_component: bool = True):
    st.subheader("Input your Trubrics credentials:")
    username = st.text_input(
        label="username", placeholder="Username", label_visibility="collapsed", value=st.secrets.get("username", "")
    )

    password = st.text_input(
        label="password",
        placeholder="password",
        label_visibility="collapsed",
        type="password",
        value=st.secrets.get("password", ""),
    )

    if default_component:
        return username, password

    feedback_component = st.text_input(
        label="feedback_component",
        placeholder="Feedback component name",
        label_visibility="collapsed",
    )

    feedback_type = st.radio(
        label="Select the component feedback type:", options=("faces", "thumbs", "textbox"), horizontal=True
    )

    return email, password, feedback_component, feedback_type

def validate_credentials(username, password):
    user_database = [
        {"user_id": 1, "username": "user1", "password": "a"},
        # Add more users as needed
    ]
    for user in user_database:
        if user["username"] == username and user["password"] == password:#sha256(password.encode()).hexdigest():
            return True
    return False

def scp_file(filename, destpath,push):
    if push: # Push to AWS instance
        host = r"@18.234.234.7"
        user = 'admin'
        password = r"15Ad456Hck"
        remote_path = destpath
        local_path = filename
        #print(filename)
        os.system(f"sshpass -p \"{password}\" scp {local_path} {user}{host}:{remote_path}")
    else: # Pull from their aws instance given a file_path
        host = r"@18.234.234.7"
        user = 'admin'
        password = r"15Ad456Hck"
        local_path = destpath
        remote_path = filename
        #print(filename)
        #print(local_path)
        os.system(f"sshpass -p \"{password}\" scp {user}{host}:{remote_path} "+ local_path.replace(" ","\ "))

def write_file(filename,code,username):
    filename = str(filename)
    username = str(username)
    print(filename)
    print(username)
    print(code)
    try:
        if not os.path.exists(username):
            os.makedirs(username)
            print('made dir')
        file_path = os.path.join(username,filename)
        print(file_path)
        with open(file_path, 'w') as file:
            for item in code:
                file.write("%s\n" % item)
        print('Wrote file.')
        return file_path
    except:
        print('Error writing your code. Likely an issue with the file name or your code cell is blank.')

def extract_code(messages):
    assistant_indices = [
        idx for idx, msg in enumerate(messages) if msg["role"] == "assistant"
    ]
    code = messages[assistant_indices[-1]]['content']

    return code

def split(input):
    delimiter = "```"
    splits = input.split(delimiter)
    codes = splits[1::2]
    text = splits[::2]

    code = []
    name = []
    #print(codes)
    for i in range(len(codes)):
        n,c = codes[i].split('\n',maxsplit=1)
        if n in ['python','bash']:# Lets think about this.
             n = True
        else:
            n = False
        code.append(c)
        name.append(n)

    return code,text,name



class DB_Utils:
    def __init__(self):
        self.HOST = "ai4eichackathon.mysql.pythonanywhere-services.com"
        self.USERNAME = "ai4eichackathon"
        self.PASSWORD = "Hack_2023"
        self.DB_NAME = "ai4eichackathon$users"
    def getDB_URL(self):
        return self.DB_URL
    def getDB_NAME(self):
        return self.DB_NAME

class OPENAI_Utils:
    def __init__(self):
        self.MAX_TOKENS = 4096
        self.GPT_MODEL = "gpt-3.5-turbo-1106"
        self.TEMPERATURE = 1.0

    def getMaxTokens(self):
        return self.MAX_TOKENS

    def getGPTModel(self):
        return self.GPT_MODEL

    def getTemperature(self):
        return self.TEMPERATURE

    def split(self,input):
        delimiter = "```"
        splits = input.split(delimiter)
        codes = splits[1::2]
        text = splits[::2]

        code = []
        name = []
        print(codes)
        for i in range(len(codes)):
            n,c = codes[i].split('\n',maxsplit=1)
            if n in ['python','bash']:# Lets think about this.
                 n = True
            else:
                n = False
            code.append(c)
            name.append(n)

        return code,text,name


    def write_file(self,filename,code,username):
        filename = str(filename)
        username = str(username)
        try:
            if not os.path.exists(os.path.join(r"../../",username)):
                os.makedirs(os.path.join(r"../../",username))
            file_path = os.path.join(r"../../",username,filename)
            with open(file_path, 'w') as file:
                file.write(code)
            print('Wrote file.')
            return file_path
        except:
            print('Error writing your code. Likely an issue with the file name or your code cell is blank.')

    def scp_file(self,filename, destpath,push):
        if push: # Push to AWS instance
            host = r"@18.234.234.7"
            user = 'admin'
            password = r"15Ad456Hck"
            remote_path = destpath
            local_path = filename
            #print(filename)
            os.system(f"sshpass -p \"{password}\" scp {local_path} {user}{host}:{remote_path}")
        else: # Pull from their aws instance given a file_path
            host = r"@18.234.234.7"
            user = 'admin'
            password = r"15Ad456Hck"
            local_path = destpath
            remote_path = filename
            #print(filename)
            #print(local_path)
            os.system(f"sshpass -p \"{password}\" scp {user}{host}:{remote_path} "+ local_path.replace(" ","\ "))

        """
        ssh = paramiko.SSHClient()
        private_key = paramiko.RSAKey(filename=private_key_path)

        ssh.connect(host, username=user, pkey=private_key)

        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_path, remote_path)

        ssh.close()
        """


    def getDefaultContexts(self):
        """_summary_ : This function returns the default context for the chatbot"""
        # To do This is to be reviewed by @james
        sys_context_1 = """You are an expert python programmer, very proficient in the following python packages.
        1. numpy
        2. pandas
        3. pytorch especially using cuda for GPU acceleration
        4. hdf5
        5. tensorflow
        """
        sys_context_2 = """You are very critical in writing code with no Run Time errors. You can write code snippets in python."""
        sys_context_3 = """You will strictly not answer questions that are not related to programming, computer science and Hardonic physics.
        Politely decline answering any conversation that is not related to the topic."""

        return [sys_context_1, sys_context_2, sys_context_3]

    def setContext(self, content = None)->list:
        msgs = []
        #print(content)
        if(content):
            msgs.append({"role" : "system", "content" : content})
        else:
            for msg in self.getDefaultContexts():
                msgs.append({"role" : "system", "content" : msg,})

        msgs.append({"role": "assistant", "content": "How can I help you?"})
        return msgs

    def num_tokens_from_messages(self, messages) -> int:
        """Return the number of tokens used by a list of messages."""
        encoding = tiktoken.encoding_for_model(self.GPT_MODEL)
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = 1
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 4  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
