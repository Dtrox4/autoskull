import discord 
import asyncio
import os
import json
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError(
        "Bot token is missing. Make sure you set it in the .env file.")

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222  # Change this to your actual Discord ID

# List of authorized user IDs who can use bot commands
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002,
                    1177672910102614127}  # Add more user IDs as needed

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.dm_messages = True  # Enable DM message handling


# Initialize bot
class AutoSkullBot(discord.Client):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_skull_list = set(
        )  # Store user IDs to auto-react to their new messages


bot = AutoSkullBot(command_prefix=['!'], intents=intents)

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
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Set the presence status to "Playing Skull Reacts"
    await bot.change_presence(activity=discord.Game(
        name="if you're worthy,you shall be skulled"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if it's a DM
    if isinstance(message.channel, discord.DMChannel):
        print(f"DM from {message.author}: {message.content}")

    # Skull reactions for authorized users
    if message.author.id in bot.user_skull_list:
        await message.add_reaction("☠️")  # Skull and crossbones reaction

    # Check if message is a command
    if message.content.startswith("!skull"):
        if message.author.id not in AUTHORIZED_USERS:
            embed = discord.Embed(description="You do not have permission to use this command.",
                    color=discord.Color.red()
                    )
            await message.channel.send(embed=embed)
            return

        args = message.content.split()

        # Command to show the list of authorized users
        if len(args) == 2 and args[1] == "authorized":
            if AUTHORIZED_USERS:
                authorized_users = [
                    f'<@{user_id}>' for user_id in AUTHORIZED_USERS
                ]
                embed = discord.Embed(Title="✅️ Authorized Users",
                        description="Authorized users: {', '.join(authorized_users)}",
                        color=discord.Color.red()
                        )
            await message.channel.send(embed=embed)
            else:
                await message.channel.send("No users are authorized.")
            return

        # Command to show the list of users being skulled
        if len(args) == 2 and args[1] == "list":
    if bot.user_skull_list:
        skull_users = [f'<@{user_id}>' for user_id in bot.user_skull_list]
        embed = discord.Embed(
            title="☠️ Skull List",
            description="\n".join(skull_users),
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            description="No users are currently being skulled.",
            color=discord.Color.red()
        )
    await message.channel.send(embed=embed)
    return

        # Command to show the list of available commands
        if len(args) == 2 and args[1] == "help":
            help_message = (
                "**Available Commands:**\n"
                "```!skull @user - Skull a user.\n"
                "!skull stop @user - Stop skulling a user.\n"
                "!skull list - Show users being skulled.\n"
                "!skull authorized - Show authorized users.\n"
                "!skull authorize @user - Authorize a user to use commands.\n"
                "!skull help - Show this help message.```"
            )
            await message.channel.send(help_message)
            return

        # Command to add a user to authorized list
        if len(args) == 3 and args[1].lower() == "authorize":
            if len(message.mentions) == 1:
                user = message.mentions[0]
                if user.id not in AUTHORIZED_USERS:
                    AUTHORIZED_USERS.add(user.id)
                    embed = discord.Embed(description=f"{user.mention} has been authorized to use the commands.",
                    color=discord.Color.red()
                    )
                await message.channel.send(embed=embed)
                else:
                    await message.channel.send(
                        f"{user.mention} is already authorized.")
            else:
                embed = discord.Embed(description="Please mention a valid user to authorize.",
                    color=discord.Color.red()
                    )
            await message.channel.send(embed=embed)

        # Command to stop skulling a user
        if len(args) == 3 and args[1].lower() == "stop":
            if len(message.mentions) == 1:
                user = message.mentions[0]
                if user.id in bot.user_skull_list:
                    bot.user_skull_list.remove(user.id)
                    embed = discord.Embed(description=f"{user.mention} will no longer be skulled.",
                    color=discord.Color.green()
                    )
                await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed(description=f"{user.mention} is not currently being skulled.",
                    color=discord.Color.red()
                    )
            await message.channel.send(embed=embed)
            else:
                    embed = discord.Embed(description="Please mention a valid user to stop skulling.",
                    color=discord.Color.red()
                    )
            await message.channel.send(embed=embed)

        # Command to skull a user (add to list of users to skull)
        elif len(args) == 2:
            mentioned_users = message.mentions
            if mentioned_users:
                for user in mentioned_users:
                    bot.user_skull_list.add(user.id)
                    embed = discord.Embed(description=f"Will skull {', '.join([user.mention for user in mentioned_users])} from now on ☠️"
                    color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
            else:
                    embed = discord.Embed(description="Please mention a user to skull!",
                    color=discord.Color.red()
                    )
            await message.channel.send(embed=embed)

# Run the bot
bot.run(TOKEN)