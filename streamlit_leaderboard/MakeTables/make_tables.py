
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
    file.write("UserInfoFile = \"" + os.path.join(BASE_DIR, "UserInfo", "users.yaml") + "\"\n")
    file.write("[passwords]\n")
    for team in config.keys():
        for usr,password in zip(config[team]["users"],config[team]["passwords"]):
            file.write(f"{team}_{usr} = \"{password}\"\n")
            print (f"{team}_{usr} = \"{password}\"\n")
    

userConfig = {}
_data = {"teamname":[], 
         "usernames": [], 
         "TotalScore" : [], 
         "TotalSumbissions": [],
         "Q1BestScore": [],
         "Q2BestScore": [],
         "QuestionsAttempted": [],
         "TokensUsed": [],
         "Q1Scores": [],
         "Q2Scores": [],
         "TotalSessions":[]
         }  
for team in config.keys():
    for usrs,password in zip(config[team]["users"],config[team]["passwords"]):
        tmpdir = os.path.join(os.path.join(BASE_DIR, "UserInfo", team, usrs))
        print (tmpdir)
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        with open(os.path.join(tmpdir, "status.json"), "w") as js:
            data = {"status": "LOGGED_OUT", "session_id": 0}
            json.dump(data, js)
        userConfig[f'{team}_{usrs}'] = os.path.join(os.path.join(BASE_DIR, "UserInfo", team, usrs))
        print("made dir")
        _data["teamname"].append(team)
        _data["usernames"].append(usrs)
        _data["TotalScore"].append(0)
        _data["TotalSumbissions"].append(0)
        _data["Q1BestScore"].append(0)
        _data["Q2BestScore"].append(0)
        _data["QuestionsAttempted"].append(0)
        _data["TokensUsed"].append(0)
        _data["Q1Scores"].append([])
        _data["Q2Scores"].append([])
        _data["TotalSessions"].append(0)
        print("made row")

pd.DataFrame(_data).to_csv(os.path.join(BASE_DIR, "UserInfo", "leaderboard.csv"))