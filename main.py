import discord
import asyncio
import datetime
import os
import json
from discord.ui import View, Button
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Bot token is missing. Make sure you set it in GitHub Secrets.")

# Owner's user ID
YOUR_USER_ID = 1212229549459374222

# File locations
SKULL_LIST_FILE = "skull_list.json"
AUTHORIZED_USERS_FILE = "authorized_users.json"
CONFIG_FILE = "config.json"
AUTHORIZED_GUILDS_FILE = "authorized_guilds.json"

# Load JSON files
def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# Load data
AUTHORIZED_GUILDS = set(load_json(AUTHORIZED_GUILDS_FILE, []))
SKULL_LIST = set(load_json(SKULL_LIST_FILE, []))
AUTHORIZED_USERS = set(load_json(AUTHORIZED_USERS_FILE, [YOUR_USER_ID]))
CONFIG = load_json(CONFIG_FILE, {"prefix": "!"})
PREFIX = CONFIG.get("prefix", "!")

# Initialize bot with intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Bot startup timestamp
start_time = datetime.datetime.utcnow()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="if you're worthy, you shall be skulled"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from itself

    # React if user is in SKULL_LIST
    if message.author.id in SKULL_LIST:
        await asyncio.sleep(1)
        await message.add_reaction("☠️")

    await bot.process_commands(message)  # Process commands normally

# Check user authorization
def is_user_authorized(ctx):
    if ctx.guild and ctx.guild.id not in AUTHORIZED_GUILDS:
        return False

    if ctx.author.id == YOUR_USER_ID or ctx.author.id in AUTHORIZED_USERS:
        return True

    return False

@bot.command()
async def skull(ctx, *args):
    if not args:
        embed = discord.Embed(title="Need Help?", description=f"Type `{PREFIX}skull help` to view all commands.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    action = args[0].lower()
    mentioned_user = ctx.message.mentions[0] if ctx.message.mentions else None

    def require_mention():
        return discord.Embed(title="Missing Argument", description=f"Please mention a user.\nUsage: `{PREFIX}skull {action} @user`", color=discord.Color.orange())

    if action in ["authorize", "unauthorize", "stop"] and not mentioned_user:
        await ctx.send(embed=require_mention())
        return

    if ctx.author.id not in AUTHORIZED_USERS and action not in ["list", "authorized", "help"]:
        embed = discord.Embed(title="Access Denied", description="You are not permitted to use this command.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if action == "adminhelp":
        if ctx.author.id != YOUR_USER_ID:
            embed = discord.Embed(title="Access Denied", description="Only the bot owner can view admin commands.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Admin Commands", color=discord.Color.dark_red())
        embed.add_field(name=f"{PREFIX}skull authorize @user", value="Grant command access to a user.", inline=False)
        embed.add_field(name=f"{PREFIX}skull unauthorize @user", value="Revoke access from a user.", inline=False)
        embed.add_field(name=f"{PREFIX}skull authorized", value="Lists all authorized users.", inline=False)
        embed.add_field(name=f"{PREFIX}skull allowguild", value="Authorize this server to use commands.", inline=False)
        embed.add_field(name=f"{PREFIX}skull disallowguild", value="Remove this server from the authorized list.", inline=False)
        embed.add_field(name=f"{PREFIX}skull guilds", value="List all authorized guild IDs.", inline=False)
        embed.set_footer(text="Admin use only — Owner privileges")
        await ctx.send(embed=embed)
        return

    if action == "help":
        embed = discord.Embed(title="Worthy Commands", color=discord.Color.blue())
        embed.add_field(name=f"{PREFIX}skull @user", value="Adds a user to the skull list.", inline=False)
        embed.add_field(name=f"{PREFIX}skull stop @user", value="Removes a user from the skull list.", inline=False)
        embed.add_field(name=f"{PREFIX}skull list", value="Shows all users currently being skulled.", inline=False)
        embed.set_footer(text="made by - @xv9c")
        await ctx.send(embed=embed)
        return

    if action == "list":
        embed = discord.Embed(title="Skulled Users", color=discord.Color.purple())
        embed.description = "\n".join([f"<@{user_id}>" for user_id in SKULL_LIST]) if SKULL_LIST else "No users are being skulled."
        await ctx.send(embed=embed)
        return

    if action == "authorize" and mentioned_user:
        if mentioned_user.id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.add(mentioned_user.id)
            save_json(AUTHORIZED_USERS_FILE, list(AUTHORIZED_USERS))
            embed = discord.Embed(title="Authorized", description=f"{mentioned_user.mention} has been authorized.", color=discord.Color.green())
        else:
            embed = discord.Embed(title="Already Authorized", description=f"{mentioned_user.mention} is already authorized.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    if action == "unauthorize" and mentioned_user:
        if mentioned_user.id in AUTHORIZED_USERS and mentioned_user.id != YOUR_USER_ID:
            AUTHORIZED_USERS.remove(mentioned_user.id)
            save_json(AUTHORIZED_USERS_FILE, list(AUTHORIZED_USERS))
            embed = discord.Embed(title="Unauthorized", description=f"{mentioned_user.mention} has been unauthorized.", color=discord.Color.red())
        else:
            embed = discord.Embed(title="Cannot Unauthorize", description=f"{mentioned_user.mention} is not authorized.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    if action == "stop" and mentioned_user:
        if mentioned_user.id in SKULL_LIST:
            SKULL_LIST.remove(mentioned_user.id)
            save_json(SKULL_LIST_FILE, list(SKULL_LIST))
            embed = discord.Embed(title="Skull Removed", description=f"{mentioned_user.mention} will no longer be skulled.", color=discord.Color.green())
        else:
            embed = discord.Embed(title="Not Skulled", description=f"{mentioned_user.mention} is not in the skull list.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    if action.startswith("<@") and mentioned_user:
        SKULL_LIST.add(mentioned_user.id)
        save_json(SKULL_LIST_FILE, list(SKULL_LIST))
        embed = discord.Embed(title="Skulled", description=f"{mentioned_user.mention} will be **skulled from now on** ☠️", color=discord.Color.purple())
        await ctx.send(embed=embed)
        return

@bot.command()
async def stats(ctx):
    now = datetime.datetime.utcnow()
    uptime = now - start_time
    uptime_str = str(uptime).split('.')[0]

    latency = round(bot.latency * 1000)
    guild_count = len(bot.guilds)
    user_count = len(set(member.id for guild in bot.guilds for member in guild.members))

    embed = discord.Embed(title="Bot Stats", color=discord.Color.teal())
    embed.add_field(name="Latency", value=f"{latency} ms", inline=True)
    embed.add_field(name="Uptime", value=uptime_str, inline=True)
    embed.add_field(name="Servers", value=f"{guild_count}", inline=True)
    embed.add_field(name="Users", value=f"{user_count}", inline=True)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Incomplete Command", description=f"Usage: `{ctx.command.qualified_name} {ctx.command.signature}`", color=discord.Color.orange())
        await ctx.send(embed=embed)
    else:
        raise error

bot.run(TOKEN)
