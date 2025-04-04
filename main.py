import discord
import asyncio
import os
import json
from discord.ext import commands
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Bot token is missing. Make sure you set it in the .env file.")

# Owner's user ID
YOUR_USER_ID = 1212229549459374222  

# File locations
SKULL_LIST_FILE = "skull_list.json"
AUTHORIZED_USERS_FILE = "authorized_users.json"
CONFIG_FILE = "config.json"

# Load Skull List
def load_skull_list():
    try:
        with open(SKULL_LIST_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_skull_list(skull_list):
    with open(SKULL_LIST_FILE, "w") as f:
        json.dump(list(skull_list), f, indent=4)

# Load Authorized Users
def load_authorized_users():
    try:
        with open(AUTHORIZED_USERS_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return {YOUR_USER_ID}  # Default authorized users

def save_authorized_users(authorized_users):
    with open(AUTHORIZED_USERS_FILE, "w") as f:
        json.dump(list(authorized_users), f, indent=4)

# Load Config
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"prefix": "!"}

config = load_config()
PREFIX = config.get("prefix", "!")
AUTHORIZED_USERS = load_authorized_users()
SKULL_LIST = load_skull_list()

# Use `commands.Bot` instead of `discord.Client`
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Keep bot alive
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

# Bot Ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="if you're worthy, you shall be skulled"))

# Auto-react to messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id in SKULL_LIST:
        await asyncio.sleep(1)  # Add a small delay before reacting
        await message.add_reaction("☠️")  

    if not message.content.startswith(PREFIX):
        return  # Ignore non-command messages

    await bot.process_commands(message)  # Ensure commands are processed
return

# Skull Command
@bot.command()
async def skull(ctx, *args):
    if not args:
        embed = discord.Embed(title="Need Help?", description="Type `!skull help` to view all commands.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    action = args[0].lower()

    if ctx.author.id not in AUTHORIZED_USERS and action not in ["list", "authorized", "help"]:
        embed = discord.Embed(title="Access Denied", description="You are not permitted to use this command.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    mentioned_user = ctx.message.mentions[0] if ctx.message.mentions else None

    if action == "help":
        embed = discord.Embed(title="Worthy Commands", color=discord.Color.blue())
        embed.add_field(name=f"{PREFIX}skull @user", value="Adds a user to the skull list.", inline=False)
        embed.add_field(name=f"{PREFIX}skull stop @user", value="Removes a user from the skull list.", inline=False)
        embed.add_field(name=f"{PREFIX}skull list", value="Shows all users currently being skulled.", inline=False)
        embed.add_field(name=f"{PREFIX}skull authorized", value="Lists all authorized users.", inline=False)
        embed.add_field(name=f"{PREFIX}skull authorize @user", value="Grants authorization to a user.", inline=False)
        embed.add_field(name=f"{PREFIX}skull unauthorize @user", value="Removes authorization from a user.", inline=False)
        embed.set_footer(text="made by - @xv9c")
        await ctx.send(embed=embed)
        return

    if action == "list":
        embed = discord.Embed(title="Skulled Users", color=discord.Color.purple())
        if SKULL_LIST:
            for user_id in SKULL_LIST:
                embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
        else:
            embed.description = "No users are being skulled."
        await ctx.send(embed=embed)
        return

    if action == "authorized":
        embed = discord.Embed(title="Authorized Users", color=discord.Color.green())
        for user_id in AUTHORIZED_USERS:
            embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
        await ctx.send(embed=embed)
        return

    if action == "authorize" and mentioned_user:
        if mentioned_user.id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.add(mentioned_user.id)
            save_authorized_users(AUTHORIZED_USERS)
            embed = discord.Embed(title="Authorized", description=f"{mentioned_user.mention} has been **permanently authorized**.", color=discord.Color.green())
        else:
            embed = discord.Embed(title="Already Authorized", description=f"{mentioned_user.mention} is already authorized.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    if action == "unauthorize" and mentioned_user:
        if mentioned_user.id in AUTHORIZED_USERS and mentioned_user.id != YOUR_USER_ID:
            AUTHORIZED_USERS.remove(mentioned_user.id)
            save_authorized_users(AUTHORIZED_USERS)
            embed = discord.Embed(title="Unauthorized", description=f"{mentioned_user.mention} has been **permanently unauthorized**.", color=discord.Color.red())
        else:
            embed = discord.Embed(title="Cannot Unauthorize", description=f"{mentioned_user.mention} is not authorized or cannot be unauthorized.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    if action == "stop" and mentioned_user:
        if mentioned_user.id in SKULL_LIST:
            SKULL_LIST.remove(mentioned_user.id)
            save_skull_list(SKULL_LIST)
            embed = discord.Embed(title="Skull Removed", description=f"{mentioned_user.mention} will **no longer be skulled**.", color=discord.Color.green())
        else:
            embed = discord.Embed(title="Not Skulled", description=f"{mentioned_user.mention} is not in the skull list.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    if action.startswith("<@") and mentioned_user:
        SKULL_LIST.add(mentioned_user.id)
        save_skull_list(SKULL_LIST)
        embed = discord.Embed(title="Skulled", description=f"{mentioned_user.mention} will be **skulled from now on** ☠️", color=discord.Color.purple())
        await ctx.send(embed=embed)
        return

# Run the bot
bot.run(TOKEN)