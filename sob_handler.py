import json
import os

DATA_FILE = "sob_data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"sob": []}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_sob(user_id):
    data = load_data()
    if str(user_id) not in data["sob"]:
        data["sob"].append(str(user_id))
        save_data(data)
        return True
    return False

def remove_sob(user_id):
    data = load_data()
    if str(user_id) in data["sob"]:
        data["sob"].remove(str(user_id))
        save_data(data)
        return True
    return False

def is_sob(user_id):
    data = load_data()
    return str(user_id) in data["sob"]
