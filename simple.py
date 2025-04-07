import discord
import asyncio
import os
import json
import datetime
import platform
import psutil
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
            await message.add_reaction("☠️")
        return

    args = content.split()
    command = args[0][1:].lower()
    arguments = args[1:]

    if content.startswith("!skull"):
        if message.author.id not in AUTHORIZED_USERS:
            embed = discord.Embed(
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return

        if len(args) == 2 and args[1] == "authorized":
            if AUTHORIZED_USERS:
                authorized_users = [f'<@{user_id}>' for user_id in AUTHORIZED_USERS]
                embed = discord.Embed(
                    title="✅️ Authorized Users",
                    description="\n".join(authorized_users),
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    description="No users are authorized.",
                    color=discord.Color.red()
                )
            await message.channel.send(embed=embed)
            return

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

        if len(args) == 2 and args[1] == "help":
            help_message = (
                "**Available Commands:**\n"
                "```diff\n"
                "[ Skull Commands ]\n"
                "!skull @user               - Skull a user.\n"
                "!skull stop @user         - Stop skulling a user.\n"
                "!skull list               - Show users being skulled.\n"
                "!skull help               - Show this help message.\n\n"
                "[ User & Server Info ]\n"
                "!userinfo [name]          - Show info about a user.\n"
                "!roleinfo [role name]     - Show info about a role.\n"
                "!serverinfo               - Show server statistics.\n"
                "!stats                    - Show bot uptime and system statistics.\n\n"
                "[ Fun & Utility ]\n"
                "!eightball <question>     - Ask the magic 8-ball a question.\n"
                "!poll <question>          - Create a simple yes/no poll.\n"
                "!remind <sec> <msg>       - Get a reminder after a given time.\n"
                "!bc <filters>             - Bulk delete messages with optional filters.\n\n"
                "[ Admin Only ]\n"
                "!skull authorize @user    - Authorize a user to use skull commands.\n"
                "!skull unauthorize @user  - Remove a user's authorization.\n"
                "!skull authorized         - Show authorized users.\n"
                "!restart                  - Restart the bot (owner only).\n"
                "```"
            )
            await message.channel.send(help_message)
            return

        if len(args) == 3 and args[1].lower() == "authorize":
            if message.mentions:
                user = message.mentions[0]
                if user.id not in AUTHORIZED_USERS:
                    AUTHORIZED_USERS.add(user.id)
                    embed = discord.Embed(
                        description=f"{user.mention} has been authorized to use the commands.",
                        color=discord.Color.green()
                    )
                else:
                    embed = discord.Embed(
                        description=f"{user.mention} is already authorized.",
                        color=discord.Color.red()
                    )
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    description="Please mention a valid user to authorize.",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
            return

        if len(args) == 3 and args[1].lower() == "stop":
            if message.mentions:
                user = message.mentions[0]
                if user.id in bot.user_skull_list:
                    bot.user_skull_list.remove(user.id)
                    embed = discord.Embed(
                        description=f"{user.mention} will no longer be skulled.",
                        color=discord.Color.green()
                    )
                else:
                    embed = discord.Embed(
                        description=f"{user.mention} is not currently being skulled.",
                        color=discord.Color.red()
                    )
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    description="Please mention a valid user to stop skulling.",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
            return

        if len(args) == 2:
            mentioned_users = message.mentions
            if mentioned_users:
                for user in mentioned_users:
                    bot.user_skull_list.add(user.id)
                embed = discord.Embed(
                    description=f"Will skull {', '.join([user.mention for user in mentioned_users])} from now on ☠️",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    description="Please mention a user to skull!",
                    color=discord.Color.red()
                )
            await message.channel.send(embed=embed)
            return
    
    # final skull reaction (non-command messages)
    if message.author.id in bot.user_skull_list:
        await message.add_reaction("☠️")

    if command == 'stats':
        await handle_stats(message, bot, start_time)

    elif command == 'poll':
        question = " ".join(arguments)
        await handle_poll(message, question)

    elif command == 'remind':
        if len(arguments) < 2 or not arguments[0].isdigit():
            await message.channel.send("Usage: `!remind <seconds> <reminder>`")
        else:
            time_in_seconds = int(arguments[0])
            reminder = " ".join(arguments[1:])
            await handle_remind(message, time_in_seconds, reminder)

    elif command == 'userinfo':
        if arguments:
            member_name = " ".join(arguments)
            member = discord.utils.find(lambda m: m.name.lower() == member_name.lower(), message.guild.members)
            await handle_userinfo(message, member)
        else:
            await handle_userinfo(message)

    elif command == 'roleinfo':
        if arguments:
            role_name = " ".join(arguments)
            role = discord.utils.get(message.guild.roles, name=role_name)
            await handle_roleinfo(message, role)
        else:
            await handle_roleinfo(message)

    elif command == 'eightball':
        question = " ".join(arguments)
        await handle_eightball(message, question)

    elif command == 'serverinfo':
        await handle_serverinfo(message)

    elif command == 'restart':
        await handle_restart(message)

    elif command == 'bc':
        await handle_bc(message, arguments)

# Run the bot
bot.run(TOKEN)