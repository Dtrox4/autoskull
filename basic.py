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
    raise ValueError(
        "Bot token is missing. Make sure you set it in the .env file.")

start_time = datetime.datetime.utcnow()

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


bot = commands.Bot(command_prefix=['!'], intents=intents)

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
            await message.channel.send(
                "You do not have permission to use this command.")
            return

        args = message.content.split()

        # Command to show the list of authorized users
        if len(args) == 2 and args[1] == "authorized":
            if AUTHORIZED_USERS:
                authorized_users = [
                    f'<@{user_id}>' for user_id in AUTHORIZED_USERS
                ]
                await message.channel.send(
                    f"Authorized users: {', '.join(authorized_users)}")
            else:
                await message.channel.send("No users are authorized.")
            return

        # Command to show the list of users being skulled
        if len(args) == 2 and args[1] == "list":
            if bot.user_skull_list:
                skull_users = [
                    f'<@{user_id}>' for user_id in bot.user_skull_list
                ]
                await message.channel.send(
                    f"Users being skulled: {', '.join(skull_users)}")
            else:
                await message.channel.send(
                    "No users are currently being skulled.")
            return

        # Command to show the list of available commands
        if len(args) == 2 and args[1] == "help":
            help_message = (
                "**Available Commands:**\n"
                "`!skull @user` - Skull a user.\n"
                "`!skull stop @user` - Stop skulling a user.\n"
                "`!skull list` - Show users being skulled.\n"
                "`!skull authorized` - Show authorized users.\n"
                "`!skull authorize @user` - Authorize a user to use commands.\n"
                "`!skull help` - Show this help message."
            )
            await message.channel.send(help_message)
            return

        # Command to add a user to authorized list
        if len(args) == 3 and args[1].lower() == "authorize":
            if len(message.mentions) == 1:
                user = message.mentions[0]
                if user.id not in AUTHORIZED_USERS:
                    AUTHORIZED_USERS.add(user.id)
                    await message.channel.send(
                        f"{user.mention} has been authorized to use the commands."
                    )
                else:
                    await message.channel.send(
                        f"{user.mention} is already authorized.")
            else:
                await message.channel.send(
                    "Please mention a valid user to authorize.")

        # Command to stop skulling a user
        if len(args) == 3 and args[1].lower() == "stop":
            if len(message.mentions) == 1:
                user = message.mentions[0]
                if user.id in bot.user_skull_list:
                    bot.user_skull_list.remove(user.id)
                    await message.channel.send(
                        f"{user.mention} will no longer be skulled.")
                else:
                    await message.channel.send(
                        f"{user.mention} is not currently being skulled.")
            else:
                await message.channel.send(
                    "Please mention a valid user to stop skulling.")

        # Command to skull a user (add to list of users to skull)
        elif len(args) == 2:
            mentioned_users = message.mentions
            if mentioned_users:
                for user in mentioned_users:
                    bot.user_skull_list.add(user.id)
                await message.channel.send(
                    f"Will skull {', '.join([user.mention for user in mentioned_users])} from now on ☠️"
                )
            else:
                await message.channel.send("Please mention a user to skull!")

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


# Run the bot
bot.run(TOKEN)
