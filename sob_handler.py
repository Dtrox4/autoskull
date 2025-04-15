# sob_handler.py
import json
from datetime import datetime

sob_users = set()

try:
    with open("sob_data.json", "r") as f:
        sob_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    sob_data = {"sobbed": []}

def save_data():
    with open("sob_data.json", "w") as f:
        json.dump(sob_data, f, indent=4)

def add_sob(user_id):
    uid = str(user_id)
    if uid not in sob_data["sobbed"]:
        sob_data["sobbed"].append(uid)
        save_data()
        return True
    return False

def remove_sob(user_id):
    uid = str(user_id)
    if uid in sob_data["sobbed"]:
        sob_data["sobbed"].remove(uid)
        save_data()
        return True
    return False

def is_sob(user_id):
    return str(user_id) in sob_data["sobbed"]
