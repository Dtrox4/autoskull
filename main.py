import discord
import os
import json
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
CONFIG_FILE = "config.json"

# File locations
SKULL_LIST_FILE = "skull_list.json"

# Load Skull List from File
def load_skull_list():
    try:
        with open(SKULL_LIST_FILE, "r") as f:
            return set(json.load(f))  # Load stored skull list
    except (FileNotFoundError, json.JSONDecodeError):
        return set()  # Return empty set if file doesn't exist or is corrupted

# Save Skull List to File
def save_skull_list(skull_list):
    with open(SKULL_LIST_FILE, "w") as f:
        json.dump(list(skull_list), f, indent=4)

# Initialize skull list
SKULL_LIST = load_skull_list()

AUTHORIZED_USERS_FILE = "authorized_users.json"

def load_authorized_users():
    """Loads authorized users from a JSON file."""
    try:
        with open(AUTHORIZED_USERS_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return {1212229549459374222, 1177672910102614127, 845578292778238002}  # Default authorized users

def save_authorized_users():
    """Saves the authorized users to the JSON file."""
    with open(AUTHORIZED_USERS_FILE, "w") as f:
        json.dump(list(AUTHORIZED_USERS), f, indent=4)

# Load authorized users when the bot starts
AUTHORIZED_USERS = load_authorized_users()

# Load Config
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"prefix": "!", "aliases": {}, "authorized_users": [YOUR_USER_ID]}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()
PREFIX = config.get("prefix", "!")
AUTHORIZED_USERS = set(config.get("authorized_users", [YOUR_USER_ID]))

# Load Skull List
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

# Message Handling
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id in bot.user_skull_list:
        await message.add_reaction("☠️")  # Skull reaction

    if not message.content.startswith(PREFIX):
        return  # Ignore non-command messages

    # Check Authorization for Skull Commands
    if message.content.startswith(PREFIX + "skull") and message.author.id not in AUTHORIZED_USERS:
        embed = discord.Embed(title="Access Denied", description="You are not permitted to use this command.", color=discord.Color.red())
        await message.channel.send(embed=embed)
        return
    
    # Skull Commands
    args = message.content.split()
    mentioned_users = message.mentions

    # If the user types just "!skull", show the help message
    if len(args) == 1:
        embed = discord.Embed(
            title="Need Help?", 
            description="Type `!skull help` to view all commands.", 
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return  # Ensure function exits here

    # If "!skull help" is used
    if args[1] == "help":
        embed = discord.Embed(title="Worthy Commands", color=discord.Color.blue())
        embed.add_field(name=f"{PREFIX}skull @user", value="Adds a user to the skull list.", inline=False)
        embed.add_field(name=f"{PREFIX}skull stop @user", value="Removes a user from the skull list.", inline=False)
        embed.add_field(name=f"{PREFIX}skull list", value="Shows all users currently being skulled.", inline=False)
        embed.add_field(name=f"{PREFIX}skull authorized", value="Lists all authorized users.", inline=False)
        embed.add_field(name=f"{PREFIX}skull authorize @user", value="Grants authorization to a user.", inline=False)
        embed.add_field(name=f"{PREFIX}skull unauthorize @user", value="Removes authorization from a user.", inline=False)
        embed.set_footer(text="made by - @xv9c")
        await message.channel.send(embed=embed)
        return
    
    # Show Skulled List
    if len(args) == 2 and args[1] == "list":
        embed = discord.Embed(title="Skulled Users", color=discord.Color.purple())
        if bot.user_skull_list:
            for user_id in bot.user_skull_list:
                embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
        else:
            embed.description = "No users are being skulled."
        await message.channel.send(embed=embed)
        return

    # Show Authorized Users
    if len(args) == 2 and args[1] == "authorized":
        embed = discord.Embed(title="Authorized Users", color=discord.Color.green())
        for user_id in AUTHORIZED_USERS:
            embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
        await message.channel.send(embed=embed)
        return

    if len(args) == 3 and args[1].lower() == "authorize" and mentioned_users:
    user = mentioned_users[0]
    if user.id not in AUTHORIZED_USERS:
        AUTHORIZED_USERS.add(user.id)  # Add user to the set
        save_authorized_users()  # Save the updated list to JSON
        await message.channel.send(f"{user.mention} has been permanently authorized.")
    else:
        await message.channel.send(f"{user.mention} is already authorized.")
    return

    if len(args) == 3 and args[1].lower() == "unauthorize" and mentioned_users:
    user = mentioned_users[0]
    if user.id in AUTHORIZED_USERS and user.id != YOUR_USER_ID:
        AUTHORIZED_USERS.remove(user.id)  # Remove from set
        save_authorized_users()  # Save changes
        await message.channel.send(f"{user.mention} has been permanently unauthorized.")
    else:
        await message.channel.send(f"{user.mention} is not an authorized user or cannot be unauthorized.")
    return

    # Remove from Skull List
    if len(args) == 3 and args[1].lower() == "stop":
        if mentioned_users:
            user = mentioned_users[0]
            if user.id in bot.user_skull_list:
                bot.user_skull_list.remove(user.id)
                save_skull_list(bot.user_skull_list)
                await message.channel.send(f"{user.mention} will no longer be skulled.")
            else:
                await message.channel.send(f"{user.mention} is not currently being skulled.")
        else:
            await message.channel.send("Please mention a valid user to stop skulling.")
        return

    # Add to Skull List
    if len(args) == 2 and mentioned_users:
        for user in mentioned_users:
            bot.user_skull_list.add(user.id)
        save_skull_list(bot.user_skull_list)
        await message.channel.send(f"Will skull {', '.join([user.mention for user in mentioned_users])} from now on ☠️")
    else:
        await message.channel.send("Please mention a user to skull.")

bot.run(TOKEN)