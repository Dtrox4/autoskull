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

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

YOUR_USER_ID = "1212229549459374222"

# Load Skull List
def load_skull_list():
    if not os.path.exists("skull_list.json"):
        return set()

    with open("skull_list.json", "r") as f:
        try:
            data = json.load(f)
            return set(str(item) for item in data if isinstance(item, (str, int)))
        except json.JSONDecodeError:
            return set()

def save_skull_list(skull_list):
    with open(SKULL_LIST_FILE, "w") as f:
        json.dump(list(skull_list), f, indent=4)

# Load Authorized Users
def load_authorized_users():
    if not os.path.exists(AUTHORIZED_USERS_FILE):
        return {YOUR_USER_ID}  # Replace with your actual user ID

    try:
        with open(AUTHORIZED_USERS_FILE, "r") as f:
            data = json.load(f)
            return set(str(user_id) for user_id in data if isinstance(user_id, (str, int)))
    except json.JSONDecodeError:
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

# File paths
AUTHORIZED_USERS_FILE = "authorized_users.json"
SKULL_LIST_FILE = "skull_list.json"

AUTHORIZED_USERS = load_authorized_users()
SKULL_LIST = load_skull_list()

start_time = datetime.datetime.utcnow()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

def read_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)
        return []

    try:
        with open(file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Reset to empty list if corrupted
        with open(file, 'w') as f:
            json.dump([], f)
        return []

def write_json(file, data):
    temp_file = file + ".tmp"
    with open(temp_file, 'w') as f:
        json.dump(data, f, indent=4)
    shutil.move(temp_file, file)
    print(f"[✔] Wrote data to {file}")

# Define your custom bot class first
class AutoSkullBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Instantiate the bot
bot = AutoSkullBot(command_prefix=['!', '.'], intents=intents)

# Auto-react to messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id in SKULL_LIST:
        await message.add_reaction("☠️")  

    if not message.content.startswith(PREFIX):
        return  # Ignore non-command messages

    await bot.process_commands(message)  # Ensure commands are processed
    
    async def setup_hook(self):
        print("🔧 setup_hook completed.")


    async def on_ready(self):
        print(f"✅ Logged in as {self.user} ({self.user.id})")
        await self.change_presence(activity=discord.Game(name="if you're worthy, you shall be skulled"))

bot = AutoSkullBot(command_prefix=['!', '.'], intents=intents)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

@bot.command()
async def skull(ctx, *args):
    if ctx.author.id not in AUTHORIZED_USERS and not YOUR_USER_ID and action not in ["list", "authorized", "help"]:
        embed = discord.Embed(title="Access Denied", description="You are not permitted to use this command.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    mentioned_user = ctx.message.mentions[0] if ctx.message.mentions else None

    action = args[0].lower()
    
    if action == "stop" and mentioned_user:
        if mentioned_user.id in SKULL_LIST:
            SKULL_LIST.remove(mentioned_user.id)
            save_skull_list(SKULL_LIST)
            await ctx.send(f"{mentioned_user.mention} will no longer be skulled.")
        else:
            await ctx.send(f"{mentioned_user.mention} is not in the skull list.")
        return

    if action.startswith("<@") and mentioned_user:
        # Handle !skull @user directly
        SKULL_LIST.add(mentioned_user.id)
        save_skull_list(SKULL_LIST)
        await ctx.send(f"Will skull {mentioned_user.mention} from now on ☠️")
        return

    embed = discord.Embed(title="Invalid Usage", description="Use `!skull help` for available commands.", color=discord.Color.red())
    await ctx.send(embed=embed)

    if action == "list":
        embed = discord.Embed(title="Skulled Users", color=discord.Color.purple())
        if SKULL_LIST:
            for user_id in SKULL_LIST:
                embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
        else:
            embed.description = "No users are being skulled."
        await ctx.send(embed=embed)
        return

# Example command to verify bot is working
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
    
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def start_flask():
    Thread(target=lambda: app.run(host='0.0.0.0', port=3000)).start()

@bot.command()
async def user(ctx, subcommand=None, *args):
    # Base auth: Only allow command if user is authorized or bot owner
    if not bot.is_authorized(ctx):
        await ctx.send(embed=discord.Embed(description="❌ You are not authorized to use this command.", color=discord.Color.red()))
        return

    # Show help if no subcommand
    if subcommand is None:
        await ctx.send(embed=discord.Embed(description="Usage: `!skull <@user>` or `!skull <subcommand>`\nType `!skull help` for more info.", color=discord.Color.orange()))
        return

    # Limit certain commands to bot owner only
    owner_only_subcommands = ["authorize", "unauthorize", "authorized"]
    if subcommand in owner_only_subcommands and str(ctx.author.id) != YOUR_USER_ID:
        await ctx.send(embed=discord.Embed(description="❌ Only the bot owner can use this command.", color=discord.Color.red()))
        return

    skull_list = read_json(skull_list_file)

    if subcommand == "authorized":
        if not bot.is_authorized(ctx):
            await ctx.send(embed=discord.Embed(
                description="❌ You are not authorized to use this command.",
                color=discord.Color.red()
            ))
            return

        if not bot.authorized_users:
            await ctx.send(embed=discord.Embed(
                description="No authorized users.",
                color=discord.Color.orange()
            ))
        else:
            names = []
            for uid in bot.authorized_users:
                try:
                    user = await bot.fetch_user(int(uid))
                    names.append(f"{user.name}#{user.discriminator} ({uid})")
                except:
                    names.append(f"(Unknown User) ({uid})")

            await ctx.send(embed=discord.Embed(
                title="✅ Authorized Users",
                description="\n".join(names),
                color=discord.Color.green()
            ))

    if subcommand == "authorize" and args:
        if not bot.is_authorized(ctx):
            await ctx.send(embed=discord.Embed(description="❌ You are not authorized to use this command.", color=discord.Color.red()))
            return

        user = args[0]
        user_id = user.strip('<@!>')

        if user_id not in bot.authorized_users:
            bot.authorized_users.append(user_id)
            write_json(AUTHORIZED_USERS_FILE, bot.authorized_users)
            await ctx.send(embed=discord.Embed(description=f"✅ User <@{user_id}> authorized.", color=discord.Color.green()))
        else:
            await ctx.send(embed=discord.Embed(description=f"⚠️ User <@{user_id}> is already authorized.", color=discord.Color.orange()))


    if subcommand == "unauthorize" and args:
        if not bot.is_authorized(ctx):
            await ctx.send(embed=discord.Embed(description="❌ You are not authorized to use this command.", color=discord.Color.red()))
            return

        user = args[0]
        user_id = user.strip('<@!>')
        if user_id in bot.authorized_users:
            bot.authorized_users.remove(user_id)
            write_json(AUTHORIZED_USERS_FILE, bot.authorized_users)
            await ctx.send(embed=discord.Embed(description=f"❌ User <@{user_id}> unauthorized.", color=discord.Color.red()))
        else:
            await ctx.send(embed=discord.Embed(description=f"⚠️ User <@{user_id}> is not authorized.", color=discord.Color.orange()))

    if subcommand == "list":
        if not bot.is_authorized(ctx):
            await ctx.send(embed=discord.Embed(description="❌ You are not authorized to use this command.", color=discord.Color.red()))
            return

        SKULL_LIST = read_json(SKULL_LIST_FILE)
        if not SKULL_LIST:
            await ctx.send(embed=discord.Embed(description="☠️ No users have been skulled yet!", color=discord.Color.orange()))
            return

        pages = []
        for i in range(0, len(SKULL_LIST), 10):
            chunk = skull_list[i:i + 10]
            desc = ""
            for entry in chunk:
                user = await bot.fetch_user(entry["user_id"])
                timestamp = entry["timestamp"]
                desc += f"{user.mention} - {timestamp}\n"
                embed = discord.Embed(title="💀 Skull List", description=desc, color=discord.Color.purple())
                embed.set_footer(text=f"Page {i//10+1} of {(len(SKULL_LIST)-1)//10+1}")
                pages.append(embed)

        current = 0
        message = await ctx.send(embed=pages[current])
        await message.add_reaction("⏮️")
        await message.add_reaction("⏭️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⏮️", "⏭️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                if str(reaction.emoji) == "⏮️":
                    current = (current - 1) % len(pages)
                    await message.edit(embed=pages[current])
                elif str(reaction.emoji) == "⏭️":
                    current = (current + 1) % len(pages)
                    await message.edit(embed=pages[current])
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                break


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
    mod_embed.add_field(name="!bc <number> <@user>", value="Bulk delete commands with special arguments.", inline=False)
    mod_embed.add_field(name="!say", value="Echo a message and delete command.", inline=False)
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
        admin_embed.add_field(name="!skull authorized", value="List all worthy users.", inline=False)
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

