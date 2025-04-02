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

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222  # Change this to your actual Discord ID

# List of authorized user IDs who can use bot commands
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127}

# File to store skull list
SKULL_LIST_FILE = "skull_list.json"

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.dm_messages = True  # Enable DM message handling

# Load skull list from file
def load_skull_list():
    try:
        with open(SKULL_LIST_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

# Save skull list to file
def save_skull_list(skull_list):
    with open(SKULL_LIST_FILE, "w") as f:
        json.dump(list(skull_list), f)

# Initialize bot
class AutoSkullBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_skull_list = load_skull_list()  # Load stored skull list

bot = AutoSkullBot(intents=intents)

# Keep the bot running with Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()  # Keep the bot alive

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    prefix = config.get("prefix", "!")
    content = message.content

# Command alias handling
    for alias, command in config.get("aliases", {}).items():
        if content.startswith(prefix + alias):
            content = content.replace(prefix + alias, prefix + command, 1)

    if content.startswith(prefix + "prefix"):
        args = content.split()
        if len(args) == 3 and args[1] == "set":
            config["prefix"] = args[2]
            save_config()
            await message.channel.send(f"Prefix changed to `{args[2]}`")
        elif len(args) == 2 and args[1] == "remove":
            config["prefix"] = "!"
            save_config()
            await message.channel.send("Prefix reset to `!`")

    elif content.startswith(prefix + "alias"):
        args = content.split()
        if len(args) == 4 and args[1] == "set":
            config["aliases"][args[2]] = args[3]
            save_config()
            await message.channel.send(f"Alias `{args[2]}` set for `{args[3]}`")
        elif len(args) == 3 and args[1] == "remove":
            if args[2] in config["aliases"]:
                del config["aliases"][args[2]]
                save_config()
                await message.channel.send(f"Alias `{args[2]}` removed.")
            else:
                await message.channel.send(f"Alias `{args[2]}` not found.")

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

    if message.author.id in bot.user_skull_list:
        await message.add_reaction("\u2620\ufe0f")  # Skull and crossbones reaction

    if message.content.startswith("!skull"):
        if message.author.id not in AUTHORIZED_USERS:
            await message.channel.send("You do not have permission to use this command.")
            return

        args = message.content.split()

        if len(args) == 1:
            await message.channel.send("Type `!skull help` for commands")
            return

        if len(args) == 2 and args[1] == "authorized":
            authorized_users = [f'<@{user_id}>' for user_id in AUTHORIZED_USERS]
            await message.channel.send(f"Authorized users: {', '.join(authorized_users)}")
            return

        if len(args) == 2 and args[1] == "list":
            skull_users = [f'<@{user_id}>' for user_id in bot.user_skull_list]
            await message.channel.send(f"Users being skulled: {', '.join(skull_users)}" if skull_users else "No users are currently being skulled.")
            return

        if len(args) == 2 and args[1] == "help":
            embed = discord.Embed(
                title="Worthy Commands",
                description="Here are the available commands:",
                color=discord.Color.blue()
            )
            embed.add_field(name="!skull @user", value="Skull a user.", inline=False)
            embed.add_field(name="!skull stop @user", value="Stop skulling a user.", inline=False)
            embed.add_field(name="!skull list", value="Show users being skulled.", inline=False)
            embed.add_field(name="!skull authorized", value="Show authorized users.", inline=False)
            embed.add_field(name="!skull authorize @user", value="Authorize a user to use commands.", inline=False)
            embed.add_field(name="!skull unauthorize @user", value="Remove a user from authorized list.", inline=False)
            embed.add_field(name="!skull help", value="Show this help message.", inline=False)
            embed.set_footer(text="AutoSkull Bot - Made by @xv9c")
            await message.channel.send(embed=embed)
            return

        if len(args) == 3 and args[1].lower() == "authorize":
            if message.mentions:
                user = message.mentions[0]
                if user.id not in AUTHORIZED_USERS:
                    AUTHORIZED_USERS.add(user.id)
                    await message.channel.send(f"{user.mention} has been authorized.")
                else:
                    await message.channel.send(f"{user.mention} is already authorized.")
            else:
                await message.channel.send("Please mention a valid user to authorize.")

        if len(args) == 3 and args[1].lower() == "unauthorize":
            if message.mentions:
                user = message.mentions[0]
                if user.id in AUTHORIZED_USERS:
                    AUTHORIZED_USERS.remove(user.id)
                    await message.channel.send(f"{user.mention} has been unauthorized.")
                else:
                    await message.channel.send(f"{user.mention} is not an authorized user.")
            else:
                await message.channel.send("Please mention a valid user to unauthorize.")

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

# Run the bot
bot.run(TOKEN)

