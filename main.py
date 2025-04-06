import discord 
import asyncio
import datetime
import os
import sys
import json
import tempfile
import shutil
from discord.ui import View, Button
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Bot token is missing. Make sure you set it in GitHub Secrets.")

print("Bot token loaded successfully!")

# Owner's user ID
YOUR_USER_ID = 1212229549459374222

# File locations
SKULL_LIST_FILE = "skull_list.json"
AUTHORIZED_USERS_FILE = "authorized_users.json"
CONFIG_FILE = "config.json"
AUTHORIZED_GUILDS_FILE = "authorized_guilds.json"
REACTION_FILE = "reactions.json"

# Load Authorized Guilds List
def load_authorized_guilds():
    try:
        with open(AUTHORIZED_GUILDS_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_authorized_guilds(guilds):
    with open(AUTHORIZED_GUILDS_FILE, "w") as f:
        json.dump(list(guilds), f, indent=4)

def chunk_list(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]

AUTHORIZED_GUILDS = load_authorized_guilds()

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
        return {YOUR_USER_ID}

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
PREFIX = "!"
AUTHORIZED_USERS = load_authorized_users()
SKULL_LIST = load_skull_list()

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot
bot = discord.Client(intents=intents)

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
start_time = datetime.datetime.utcnow()

# Initialize bot
class autoskull(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_skull_list = set()  # Store user IDs to auto-react to their new messages

bot = autoskull(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="if you're worthy, you shall be skulled"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id in SKULL_LIST:
        await asyncio.sleep(1)
        await message.add_reaction("☠️")

    if not message.content.startswith(PREFIX):
        return

    # Skull reactions for authorized users
    if message.author.id in bot.user_skull_list:
        await message.add_reaction("💀")

    if message.content.startswith("!skull"):
        if message.author.id not in AUTHORIZED_USERS:
            embed = discord.Embed(description=f"⛔ | You are not authorized to use this command!", color=discord.Color.red())
            await message.channel.send(embed=embed)
            return

        args = message.content.split()
        mentioned_users = message.mentions
        
        if mentioned_users:
            for user in SKULL_LIST:
                    await msg.add_reaction("💀")  # React to their message
                    embed = discord.Embed(description=f"☠️ | {mentioned_user.mention} is now skulled.", color=discord.Color.green())
                    await message.channel.send(f"Skulled {msg.author.mention} 💀")
                    break
        else:
            embed = discord.Embed(description=f"❌ | Please mention a user to skull!", color=discord.Color.red())
            await message.channel.send(embed=embed)
    
    await bot.process_commands(message)

        # React to keywords
    for keyword, emoji in keyword_reactions.items():
        if keyword in message.content.lower():
            try:
                await message.add_reaction(emoji)
            except discord.HTTPException:
                pass  # Invalid emoji or permission issue

    await bot.process_commands(message)

def is_user_authorized(ctx):
    if ctx.author.id == YOUR_USER_ID:
        return True

    if ctx.author.id in AUTHORIZED_USERS:
        return True

@bot.command()
async def skull(ctx, *args):
    if not args:
        embed = discord.Embed(title="Need Help?", description="Type `!help` to view all commands.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    action = args[0].lower()
    mentioned_user = ctx.message.mentions[0] if ctx.message.mentions else None

    # Check for missing required mention
    def require_mention():
        return discord.Embed(
            title="Missing Argument",
            description=f"Please mention a user.\nUsage: ```{PREFIX}skull {action} @user```",
            color=discord.Color.orange()
        )

    if action in ["authorize", "unauthorize", "stop"] and not mentioned_user:
        await ctx.send(embed=require_mention())
        return

    if action.startswith("<@") and not mentioned_user:
        await ctx.send(embed=require_mention())
        return

    if ctx.author.id not in AUTHORIZED_USERS and action not in ["list", "authorized", "help"]:
        embed = discord.Embed(title="Access Denied", description="You are not permitted to use this command.", color=discord.Color.red())
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
    
@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="🗳️ New Poll", description=question, color=discord.Color.orange())
    embed.set_footer(text=f"Started by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    message = await ctx.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")

@bot.command()
async def remind(ctx, time_in_seconds: int, *, reminder: str):
    await ctx.send(embed=discord.Embed(
        description=f"⏰ Reminder set for **{time_in_seconds}** seconds.",
        color=discord.Color.teal()
    ))
    await asyncio.sleep(time_in_seconds)
    await ctx.send(embed=discord.Embed(
        title="⏰ Reminder!",
        description=reminder,
        color=discord.Color.red()
    ).set_footer(text=f"Reminder for {ctx.author}", icon_url=ctx.author.display_avatar.url))

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="📈 Server Stats", color=discord.Color.purple())
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Server Name", value=guild.name)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Owner", value=guild.owner)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

import random

@bot.command()
async def eightball(ctx, *, question):
    responses = ["Yes", "No", "Maybe", "Definitely", "Ask again later", "Absolutely not"]
    response = random.choice(responses)
    embed = discord.Embed(title="🎱 8Ball", color=discord.Color.random())
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=response, inline=False)
    embed.set_footer(text=f"Asked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    if member is None:
        embed = discord.Embed(
            title="Missing Argument",
            description="Please specify a role.\nUsage:!roleinfo <role name>",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title=f"User Info: {member}", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="Status", value=str(member.status).title(), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def roleinfo(ctx, *, role: discord.Role = None):
    if role is None:
        embed = discord.Embed(
            title="Missing Argument",
            description="Please specify a role.\nUsage: ```!roleinfo <role name>```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title=f"Role Info: {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id, inline=True)
    embed.add_field(name="Color", value=str(role.color), inline=True)
    embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
    embed.add_field(name="Hoisted", value=role.hoist, inline=True)
    embed.add_field(name="Position", value=role.position, inline=True)
    embed.add_field(name="Member Count", value=len(role.members), inline=True)
    embed.set_footer(text=f"Created at: {role.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    await ctx.send(embed=embed)

# Load existing reactions
if os.path.exists(REACTION_FILE):
    with open(REACTION_FILE, "r") as f:
        keyword_reactions = json.load(f)
else:
    keyword_reactions = {}
    
@bot.command()
async def addreact(ctx, keyword: str, emoji: str):
    keyword_reactions[keyword.lower()] = emoji
    with open(REACTION_FILE, "w") as f:
        json.dump(keyword_reactions, f, indent=4)
    await ctx.send(f"Got it! I’ll react with {emoji} when I see **{keyword}**.")


@bot.command()
async def restart(ctx):
    if str(ctx.author.id) != YOUR_USER_ID:
        embed = discord.Embed(
            title="Access Denied",
            description="Only the bot owner can restart the bot.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    await ctx.send(embed=discord.Embed(
        title="♻️ Restarting...",
        description="The bot is restarting. Please wait.",
        color=discord.Color.orange()
    ))

    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def bc(ctx, limit: int = 100, user: discord.User = None, *, keyword: str = None):
    """
    Deletes messages by bot (or user/keyword), including the command message.
    Usage: !bc [limit] [@user (optional)] [keyword (optional)]
    """
    # Delete the command message itself first
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass  # It may already be gone

    def check(msg):
        if user and msg.author != user:
            return False
        if keyword and keyword.lower() not in msg.content.lower():
            return False
        return msg.author == bot.user if not user else msg.author == user

    deleted = await ctx.channel.purge(limit=limit, check=check)

    embed = discord.Embed(
        title="Messages Cleared 🧹",
        description=f"Deleted {len(deleted)} message(s).",
        color=discord.Color.orange()
    )
    confirmation = await ctx.send(embed=embed)
    await asyncio.sleep(3)
    await confirmation.delete()



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Incomplete Command", description=f"Usage: `{ctx.command.qualified_name} {ctx.command.signature}`", color=discord.Color.orange())
        await ctx.send(embed=embed)
    else:
        raise error

class HelpView(discord.ui.View):
    def __init__(self, pages, author):
        super().__init__(timeout=120)
        self.pages = pages
        self.current_page = 0
        self.author = author

        self.message = None  # will be set when the message is sent

    async def send_initial(self, ctx):
        embed = self.pages[self.current_page]
        self.message = await ctx.send(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author.id

    async def update_page(self, interaction):
        embed = self.pages[self.current_page]
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % len(self.pages)
        await self.update_page(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await self.update_page(interaction)

bot.remove_command("help")

# Create your help pages as embeds
def get_help_pages(user_id):
    pages = []

    skull_embed = discord.Embed(title="☠️ Skull Commands", color=discord.Color.blurple())
    skull_embed.add_field(name="!skull <@user>", value="Grant auto-skull privileges to a user.", inline=False)
    skull_embed.add_field(name="!skull stop <@user>", value="Remove auto-skull previleges from a user.", inline=False)
    skull_embed.add_field(name="!skull list", value="View all users with auto-skull privileges.", inline=False)
    pages.append(skull_embed)

    mod_embed = discord.Embed(title="🛠️ Moderation Tools", color=discord.Color.blurple())
    mod_embed.add_field(name="!bc", value="Bulk delete bot command embed messages.", inline=False)
    mod_embed.add_field(name="!bc <limit> {@user}/[keyword] (optional)", value="Bulk delete commands with special arguments.", inline=False)
    mod_embed.add_field(name="!say", value="Echo a message and delete command.", inline=False)
    skull_embed.add_field(name="!addreact <keyword> <emoji>", value="Add reactions to keywords.", inline=False)
    pages.append(mod_embed)

    info_embed = discord.Embed(title="📊 Info Commands", color=discord.Color.blurple())
    info_embed.add_field(name="!roleinfo", value="Show info about a role.", inline=False)
    info_embed.add_field(name="!serverinfo", value="Show info about the server.", inline=False)
    info_embed.add_field(name="!userinfo", value="Show info about a user.", inline=False)
    info_embed.add_field(name="!stats", value="Bot statistics and uptime.", inline=False)
    pages.append(info_embed)

    fun_embed = discord.Embed(title="🎲 Engagement Commands", color=discord.Color.blurple())
    fun_embed.add_field(name="!eightball", value="Ask the magic 8-ball a question.", inline=False)
    fun_embed.add_field(name="!poll", value="Create a poll with reactions.", inline=False)
    pages.append(fun_embed)

    util_embed = discord.Embed(title="🧰 Utility Commands", color=discord.Color.blurple())
    util_embed.add_field(name="!remind", value="Set a reminder for yourself.", inline=False)
    pages.append(util_embed)

    # Admin-only page
    if user_id == YOUR_USER_ID:
        admin_embed = discord.Embed(title="🔐 Admin Tools", color=discord.Color.red())
        admin_embed.add_field(name="!skull authorize <@user>", value="Make someone worthy enough to use skull commands.", inline=False)
        admin_embed.add_field(name="!skull unauthorize <@user>", value="Make the user unworthy to use the skull commands.", inline=False)
        admin_embed.add_field(name="!authorized", value="List all worthy users.", inline=False)
        admin_embed.add_field(name="!restart", value="Restart the bot from root.", inline=False)
        pages.append(admin_embed)

    return pages

# Main help command
@bot.command()
async def help(ctx):
    pages = get_help_pages(ctx.author.id)
    view = HelpView(pages, ctx.author)
    await view.send_initial(ctx)

if __name__ == "__main__":
    start_flask()  # Start Flask server

    token = os.getenv("DISCORD_TOKEN")
    if token:
        try:
            asyncio.run(bot.start(token))
        except Exception as e:
            import traceback
            print("❌ Full Exception:")
            traceback.print_exc()
    else:
        print("❌ DISCORD_TOKEN not found in environment variables.")

