import discord
import os
import json
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Bot token is missing. Make sure you set it in the .env file.")

YOUR_USER_ID = 1212229549459374222 

AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127}

SKULL_LIST_FILE = "skull_list.json"
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"prefix": "!", "aliases": {}}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()
PREFIX = config.get("prefix", "!")

def load_skull_list():
    try:
        with open(SKULL_LIST_FILE, "r") as f:
            return set(json.load(f) or [])
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_skull_list(skull_list):
    with open(SKULL_LIST_FILE, "w") as f:
        json.dump(list(skull_list), f)

class AutoSkullBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_skull_list = load_skull_list()

bot = AutoSkullBot(intents=discord.Intents.all())

def run():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "I'm alive!"

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

    global PREFIX
    PREFIX = config.get("prefix", "!")
    content = message.content

    for alias, command in config.get("aliases", {}).items():
        if content.startswith(PREFIX + alias):
            content = content.replace(PREFIX + alias, PREFIX + command, 1)

    if message.author.id in bot.user_skull_list:
        await message.add_reaction("\u2620\ufe0f")  # Skull reaction

    if content.startswith(PREFIX + "skull"):
        args = content.split()

        if len(args) == 1:
            await message.channel.send(f"Type `{PREFIX}skull help` for commands")
            return

        if len(args) == 2 and args[1] == "list":
            if bot.user_skull_list:
                embed = discord.Embed(title="Skulled Users", color=discord.Color.purple())
                for user_id in bot.user_skull_list:
                    embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
                await message.channel.send(embed=embed)
            else:
                await message.channel.send("No users are being skulled.")
            return

        if len(args) == 2 and args[1] == "authorized":
            embed = discord.Embed(title="Authorized Users", color=discord.Color.green())
            for user_id in AUTHORIZED_USERS:
                embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
            await message.channel.send(embed=embed)
            return

        if len(args) == 3 and args[1].lower() == "stop":
            if message.mentions:
                user = message.mentions[0]
                if user.id in bot.user_skull_list:
                    bot.user_skull_list.remove(user.id)
                    save_skull_list(bot.user_skull_list)  # Save updated list
                    await message.channel.send(f"{user.mention} will no longer be skulled.")
                else:
                    await message.channel.send(f"{user.mention} is not currently being skulled.")
            else:
                await message.channel.send("Please mention a valid user to stop skulling.")

        elif len(args) == 2:
            mentioned_users = message.mentions
            if mentioned_users:
                for user in mentioned_users:
                    bot.user_skull_list.add(user.id)
                save_skull_list(bot.user_skull_list)  # Save updated list
                await message.channel.send(f"Will skull {', '.join([user.mention for user in mentioned_users])} from now on ☠️")
            else:
                await message.channel.send("Please mention a user to skull!")

bot.run(TOKEN)