import json
import os
from datetime import datetime, timedelta
import secrets

JSON_FILE = "users.json"

def load_json():
    if not os.path.exists(JSON_FILE):
        return {"users": {}}
    with open(JSON_FILE, "r") as f:
        return json.load(f)
    
def save_dat(dat):
    with open(JSON_FILE, "w") as f:
        json.dump(dat, f, indent=4)

def gen_token():
    return secrets.token_hex(16)

def add_or_upd_usr(usrname, eula_acc=False):
    users = load_json()
    token = secrets.token_hex(16)

    if usrname in users:
        users[usrname]["token"] = token
        users[usrname]["token"] = eula_acc
        users[usrname]["created_at"] = datetime.now().isoformat()
    else:
        users[usrname] = {
            "token": token,
            "eula": eula_acc,
            "created_at": datetime.now().isoformat(),
            "banned": False,
            "moderator": False
        }
    
    save_dat(users)
    return token

def validate_token(usrname, token):
    users = load_json()
    if usrname not in users:
        return False, "Username not found, please recheck your username !"

    user = users[usrname]
    if user["banned"]:
        return False, "User is banned !"

    if user["token"] != token:
        return False,  "Invalid token, please recheck your token !"

    created_at = datetime.fromisoformat(user["created_at"])

    if datetime.now() > created_at + timedelta(days=7):
        return False, "Token expired, please regenerate a new token for your account."
    
    return True, "Token is valid."

def is_mod(usrname):
    users=load_json()
    return users.get(usrname, {}).get("moderator", False)

def ban_usr(usrname):
    users = load_json()
    if usrname in users:
        users[usrname]["banned"] = True
        save_dat(users)

def unban_user(usrname):
    users = load_json()
    if usrname in users:
        users[usrname]["banned"] = False
        save_dat(users)

def revoke_token(usrname):
    users = load_json()
    if usrname in users:
        users[usrname]["token"] = None
        save_dat(users)