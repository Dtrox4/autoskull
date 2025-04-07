import discord
import asyncio
import os
import json
import datetime
import platform
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from standalone_commands import (
    handle_stats, handle_poll, handle_remind,
    handle_serverinfo, handle_userinfo, handle_roleinfo,
    handle_eightball, handle_restart, handle_bc
)

start_time = datetime.datetime.utcnow()

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Bot token is missing. Make sure you set it in the .env file.")

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222

# Authorized users
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127}

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.dm_messages = True

# Initialize bot
class AutoSkullBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_skull_list = set()

bot = AutoSkullBot(intents=intents)

# Keep-alive server using Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="if you're worthy, you shall be skulled"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        print(f"DM from {message.author}: {message.content}")

    content = message.content
    if not content.startswith('!'):
        if message.author.id in bot.user_skull_list:
            await message.add_reaction("\u2620\ufe0f")
        return

    args = content.split()
