import discord
import asyncio
import os
import json
import datetime
import platform
from collections import defaultdict
import time
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from bot_response import handle_conversational, get_response
from standalone_commands import (
    handle_poll, handle_remind,
    handle_serverinfo, handle_userinfo, handle_roleinfo,
    handle_eightball
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

OWNER_ID = 1212229549459374222

GENTLE_USER_IDS = [845578292778238002, 1177672910102614127]

# Define channels and optional messages
WELCOME_CHANNELS = {
    1359319883988336924: "welc! rep **/mock** 4 pic, bst for roles!"  # Add a custom message here
}

global MAINTENANCE_MODE, MAINTENANCE_END_TIME, MAINTENANCE_CANCELLED
MAINTENANCE_MODE = False
MAINTENANCE_END_TIME = None
MAINTENANCE_CANCELLED = False


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
async def on_member_join(member):
    for channel_id, custom_message in WELCOME_CHANNELS.items():
        channel = member.guild.get_channel(channel_id)
        if channel:
            if custom_message:
                content = f"{member.mention} {custom_message}"
            else:
                content = f"{member.mention}"
            await channel.send(content, delete_after=5)

async def handle_say(message):
    try:
        await message.delete()
    except discord.Forbidden:
        await message.channel.send("⚠️ I don't have permission to delete messages.")
        return

    content = message.content.strip()
    command_prefix = "!say"

    say_message = content[len(command_prefix):].strip()
    if say_message:
        await message.channel.send(say_message)
    else:
        embed = discord.Embed(
            description="⚠️ You must provide a message to say.\n**Usage:** `!say <message>`",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)

async def handle_stats(message, bot, start_time):
    now = datetime.datetime.utcnow()
    uptime = now - start_time
    uptime_str = str(uptime).split('.')[0]

    latency = round(bot.latency * 1000)
    guild_count = len(bot.guilds)
    user_count = len(set(member.id for guild in bot.guilds for member in guild.members))

    embed = discord.Embed(title="🤖 Bot Stats", color=discord.Color.green())
    embed.add_field(name="Latency", value=f"{latency} ms", inline=True)
    embed.add_field(name="Uptime", value=uptime_str, inline=True)
    embed.add_field(name="Servers", value=f"{guild_count}", inline=True)
    embed.add_field(name="Users", value=f"{user_count}", inline=True)

    embed.set_footer(text=f"Requested by {message.author}", icon_url=message.author.display_avatar.url)
    await message.channel.send(embed=embed)

async def handle_restart(message):
    if message.author.id != YOUR_USER_ID:
        await message.channel.send("You are not authorized to restart the bot.")
        return

    confirm_message = await message.channel.send("Are you sure you want to restart the bot? Reply with `yes` or `no` within 15 seconds.")

    def check(m):
        return m.author == message.author and m.channel == message.channel and m.content.lower() in ["yes", "no"]

    try:
        reply = await message.client.wait_for("message", timeout=15.0, check=check)
        if reply.content.lower() == "yes":
            await message.channel.send("Restarting bot...")
            await message.client.close()
        else:
            await message.channel.send("Restart cancelled.")
    except asyncio.TimeoutError:
        await message.channel.send("No response. Restart cancelled.")


async def handle_maintenance(message, bot):
    global MAINTENANCE_MODE, MAINTENANCE_END_TIME, MAINTENANCE_CANCELLED

    if message.author.id != YOUR_USER_ID:
        embed = discord.Embed(
            description="⚠️ You are not authorized to use this command.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    args = message.content.split()
    if len(args) != 2:
        embed = discord.Embed(
            description="⚠️ Usage: `!maintenance <duration_in_minutes>`",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return

    try:
        duration = int(args[1])
    except ValueError:
        embed = discord.Embed(
            description="⚠️ Please provide a valid number for duration.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    MAINTENANCE_MODE = True
    MAINTENANCE_END_TIME = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)
    MAINTENANCE_CANCELLED = False

    embed = discord.Embed(
        title="🛠️ Maintenance Mode Activated",
        description=f"The bot will be under maintenance for {duration} minute(s).",
        color=discord.Color.orange()
    )
    embed.set_footer(text="Only the bot owner can use commands during this time.")
    await message.channel.send(embed=embed)

    # Wait until maintenance time is over or cancelled
    for _ in range(duration * 60):
        if MAINTENANCE_CANCELLED:
            return
        await asyncio.sleep(1)

    # Maintenance done, restart the bot
    if not MAINTENANCE_CANCELLED:
        embed = discord.Embed(
            title="✅ Maintenance Complete",
            description="Restarting the bot now...",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)
        await bot.close()

async def handle_cancel_maintenance(message):
    global MAINTENANCE_MODE, MAINTENANCE_END_TIME, MAINTENANCE_CANCELLED

    if message.author.id != YOUR_USER_ID:
        embed = discord.Embed(
            description="\u274C You are not authorized to cancel maintenance.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if MAINTENANCE_MODE:
        MAINTENANCE_MODE = False
        MAINTENANCE_END_TIME = None
        MAINTENANCE_CANCELLED = True
        embed = discord.Embed(
            title="\u274C Maintenance Cancelled",
            description="The bot is no longer in maintenance mode.",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(
            description="\u2139 The bot is not currently in maintenance mode.",
            color=discord.Color.blue()
        )
        await message.channel.send(embed=embed)

async def handle_bc(message, args):
    if not message.author.guild_permissions.manage_messages:
        embed = discord.Embed(
            description="❌ You don't have the required **permission**: `Manage Messages`.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if len(args) < 1:
        embed = discord.Embed(
            description="⚠️ Usage: `!bc <count> [contains <word>]`",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return

    try:
        count = int(args[0])
    except ValueError:
        embed = discord.Embed(
            description="❌ The first argument must be a number.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    keyword = None
    if len(args) >= 3 and args[1].lower() == "contains":
        keyword = " ".join(args[2:])

    def check(msg):
        return keyword.lower() in msg.content.lower() if keyword else True

    deleted = await message.channel.purge(limit=count + 1, check=check)
    embed = discord.Embed(
        description=f"✅ Deleted **{len(deleted) - 1}** messages.",
        color=discord.Color.green()
    )
    await message.channel.send(embed=embed, delete_after=5)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="if you're worthy, you shall be skulled"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if await handle_conversational(message):
        return

    if isinstance(message.channel, discord.DMChannel):
        print(f"DM from {message.author}: {message.content}")

    if message.content.lower().startswith("!stats"):
        await handle_stats(message, bot, start_time)
        return

    if message.content.lower().startswith("!restart"):
        await handle_restart(message)
        return

    if message.content.startswith("!say"):
        await handle_say(message)
        return

    if MAINTENANCE_MODE and message.author.id != YOUR_USER_ID:
        embed = discord.Embed(
            description="🛠️ The bot is currently under maintenance.\nPlease try again later.",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return

    if message.content.startswith("!maintenance"):
        await handle_maintenance(message, bot)

    if message.content.startswith("!cancelmaintenance"):
        await handle_cancel_maintenance(message)
        return

    content = message.content
    if not content.startswith('!'):
        if message.author.id in bot.user_skull_list:
            await asyncio.sleep(1)
            await message.add_reaction("\u2620\ufe0f")
        return

    args = content.split()
    command = args[0][1:].lower()
    arguments = args[1:]

    if command == 'bc':
        await handle_bc(message, arguments)
        return

    if command == "skull":
        if message.author.id not in AUTHORIZED_USERS:
            embed = discord.Embed(
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return

        # !skull authorized
        if len(arguments) == 1 and arguments[0] == "authorized":
            authorized_users = [f'<@{user_id}>' for user_id in AUTHORIZED_USERS]
            embed = discord.Embed(
                title="✅️ Authorized Users",
                description="\n".join(authorized_users) if authorized_users else "⚠️ No users are authorized.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return

        # !skull list
        if len(arguments) == 1 and arguments[0] == "list":
            skull_users = [f'<@{user_id}>' for user_id in bot.user_skull_list]
            embed = discord.Embed(
                title="☠️ Skull List",
                description="\n".join(skull_users) if skull_users else "⚠️ No users are currently being skulled.",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)
            return

        # !skull help
        if len(arguments) == 1 and arguments[0] == "help":
            help_message = (
        "**Available Commands:**\n"
        "```diff\n"
        "[ Skull Commands ]\n"
        "!skull @user              - Skull a user.\n"
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
        "!restart                  - Restart the bot.    (owner only).\n"
        "!maintenance <minutes>    - Enter maintenance mode (owner only).\n"
        "!cancelmaintenance        - Cancel maintenance mode (owner only).\n"
        "```"
            )
            await asyncio.sleep(1)
            await message.channel.send(help_message)
            return

        # !skull authorize @user
        if len(arguments) == 2 and arguments[0] == "authorize" and message.mentions:
            user = message.mentions[0]
            if user.id not in AUTHORIZED_USERS:
                AUTHORIZED_USERS.add(user.id)
                embed = discord.Embed(
                    description=f"✅️ {user.mention} has been authorized to use the commands.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    description=f"‼️ {user.mention} is already authorized.",
                    color=discord.Color.red()
                )
            await message.channel.send(embed=embed)
            return

        # !skull unauthorize @user
        if len(arguments) == 2 and arguments[0] == "unauthorize" and message.mentions:
            user = message.mentions[0]
            if user.id == message.author.id:
                embed = discord.Embed(
                    description="❌️ You cannot unauthorize yourself.",
                    color=discord.Color.red()
                )
            elif user.id in AUTHORIZED_USERS:
                AUTHORIZED_USERS.remove(user.id)
                embed = discord.Embed(
                    description=f"✅️ {user.mention} has been unauthorized.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    description=f"‼️ {user.mention} is not in the authorized list.",
                    color=discord.Color.red()
                )
            await message.channel.send(embed=embed)
            return

        # !skull stop @user
        if len(arguments) == 2 and arguments[0] == "stop" and message.mentions:
            user = message.mentions[0]
            if user.id in bot.user_skull_list:
                bot.user_skull_list.remove(user.id)
                embed = discord.Embed(
                    description=f"✅️ {user.mention} will no longer be skulled.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    description=f"‼️ {user.mention} is not currently being skulled.",
                    color=discord.Color.red()
                )
            await message.channel.send(embed=embed)
            return

        # !skull @user
        if len(args) == 2:
            user = None
            if message.mentions:
                user = message.mentions[0]
            else:
                try:
                    user_id = int(args[1])
                    user = await bot.fetch_user(user_id)
                except (ValueError, discord.NotFound):
                    pass

            if user:
                bot.user_skull_list.add(user.id)
                embed = discord.Embed(
                    description=f"✅️ Skulling {user.mention} starting now.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    description="⚠️ Please mention a user or provide a valid user ID.",
                    color=discord.Color.red()
                )
            await message.channel.send(embed=embed)
            return

        # Fallback
        embed = discord.Embed(
            description="⚠️ Type `!skull help` to view all valid skull commands.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if message.author.id in bot.user_skull_list:
        await message.add_reaction("\u2620\ufe0f")

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

# Run the bot
bot.run(TOKEN)
