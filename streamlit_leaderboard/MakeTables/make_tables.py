import numpy as np
import sys, os, pathlib

import pandas as pd
import json
BASE_DIR = str(pathlib.Path(__file__).parent.parent.absolute())
sys.path.append(BASE_DIR)
with open(os.path.join(BASE_DIR, "UserInfo", "users.json")) as file:
    config = json.load(file)
    
with open(os.path.join(BASE_DIR, ".streamlit", "secrets.toml"), "a") as file:
    file.write("\n")
    file.write("base_dir = \"" + BASE_DIR + "\"\n")
    file.write("UserInfoDir = \"" + os.path.join(BASE_DIR, "UserInfo") + "\"\n")
    file.write("UserInfoFile = \"" + os.path.join(BASE_DIR, "UserInfo", "users.json") + "\"\n")
    #names of team
    file.write("[NamesOfTeam]\n")
    for team in config.keys():
        teamname = config[team]["name"]# can have spaces and something like awesome team
        file.write(f"{team} = \"{teamname}\"\n")
    #users names:
    file.write("[NamesOfUsers]\n")
    for team in config.keys():
        for usrname,nameOfUsr in zip(config[team]["usernames"], config[team]["users"]):
            file.write(f"{team}_{usrname} = \"{nameOfUsr}\"\n")
    #passwords
    file.write("[passwords]\n")
    for team in config.keys():
        for usr,password in zip(config[team]["usernames"],config[team]["passwords"]):
            file.write(f"{team}_{usr} = \"{password}\"\n")
    #instances
    file.write("[instances]\n")
    for team in config.keys():
        for usr, instance in zip(config[team]["usernames"], config[team]["instances"]):
            file.write(f"{team}_{usr} = \"{instance}\"\n")
    #openAIkeys
    file.write("[openAI_keys]\n")
    for team in config.keys():
        for usr, key in zip(config[team]["usernames"], config[team]["openAI_keys"]):
            file.write(f"{team}_{usr} = \"{key}\"\n")

userConfig = {}
_data = {"teamname":[], 
         "NameOfTeam":[],
         "username": [],
         "NameOfUser":[], 
         "QuestionAttempted": [],
         "TokensUsed": [],
         "Score": []
         }  
for team in config.keys():
    for index, (usrs,password) in enumerate(zip(config[team]["usernames"],config[team]["passwords"])):
        tmpdir = os.path.join(os.path.join(BASE_DIR, "UserInfo", team, usrs))
        tmpdir2 = os.path.join(tmpdir, "Results")
        print (tmpdir)
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        #else:
        #    os.system(f"rm -rf {tmpdir}")
        #    os.makedirs(tmpdir)
        if not os.path.exists(tmpdir2):
            os.makedirs(tmpdir2)
        #else:
        #    os.system(f"rm -rf {tmpdir2}")
        #    os.makedirs(tmpdir2)
        with open(os.path.join(tmpdir, "status.json"), "w") as js:
            data = {"status": "LOGGED_OUT", "session_id": 0, "tokens_used":0}
            json.dump(data, js)
        userConfig[f'{team}_{usrs}'] = os.path.join(os.path.join(BASE_DIR, "UserInfo", team, usrs))
        print("made dir")
        _data["teamname"].append(team)
        _data["NameOfTeam"].append(config[team]["name"]),
        _data["NameOfUser"].append(config[team]["users"][index])
        _data["username"].append(usrs)
        _data["QuestionAttempted"].append(0)
        _data["TokensUsed"].append(0)
        _data["Score"].append(0)
        print("made row")

pd.DataFrame(_data).to_csv(os.path.join(BASE_DIR, "UserInfo", "leaderboard.csv"), index = False)