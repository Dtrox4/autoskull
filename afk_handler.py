# afk_handler.py

import discord
import datetime

afk_users = {}  # user_id: {"reason": str, "since": datetime}

def set_afk(user_id, reason):
    afk_users[user_id] = {
        "reason": reason,
        "since": datetime.datetime.utcnow()
    }

def remove_afk(user_id):
    if user_id in afk_users:
        del afk_users[user_id]

def is_afk(user_id):
    return user_id in afk_users

def get_afk_data(user_id):
    return afk_users.get(user_id)

# Usage in on_message (example):
# import afk_handler
# if message.content.startswith("!afk"):
#     afk_handler.set_afk(message.author.id, "Away")
