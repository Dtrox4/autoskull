import discord 
import asyncio
import datetime
import os
import json
from discord.ui import View, Button
from discord.ext import commands
from keep_alive import keep_alive
from dotenv import load_dotenv

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
AUTHORIZED_GUILDS_FILE = "authorized_guilds.json"

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
    """Loads the skull list from the JSON file."""
    try:
        with open(SKULL_LIST_FILE, "r") as f:
            return set(json.load(f))  # Convert list back to set
    except (FileNotFoundError, json.JSONDecodeError):
        return set()  # Return empty set if file doesn't exist or is invalid

def save_skull_list(skull_list):
    """Saves the skull list to the JSON file."""
    try:
        with open(SKULL_LIST_FILE, "w") as f:
            json.dump(list(skull_list), f, indent=4)  # Convert set to list before saving
        print(f"✅ Skull list saved successfully: {skull_list}")  # Debugging log
    except Exception as e:
        print(f"❌ Error saving skull list: {e}")  # Debugging log

# Load ser ids
def load_authorized_users():
    try:
        with open("authorized_users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_authorized_users(users):
    with open("authorized_users.json", "w") as f:
        json.dump(users, f, indent=4)

def is_authorized(user_id):
    return str(user_id) == YOUR_USER_ID or str(user_id) in load_authorized_users()

# Load Config
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        default_config = {"prefix": "!"}
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)  # Create config file if missing/corrupted
        return default_config


config = load_config()
PREFIX = config.get("prefix", "!")
AUTHORIZED_USERS = load_authorized_users()
SKULL_LIST = load_skull_list()

# Use `commands.Bot`
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

keep_alive()
# your bot stuff here

start_time = datetime.datetime.utcnow()

def require_mention(first_arg):
    return discord.Embed(
        title="Missing Argument",
        description=f"Please mention a user.\nUsage: `{PREFIX}skull {first_arg} @user`",
        color=discord.Color.orange()
    )

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
    
    await bot.process_commands(message)

def is_user_authorized(ctx):
    if ctx.guild and ctx.guild.id not in AUTHORIZED_GUILDS:
        return False

    if ctx.author.id == YOUR_USER_ID:
        return True

    if ctx.author.id in AUTHORIZED_USERS:
        return True

    if ctx.guild:
        guild_id = str(ctx.guild.id)
        guild_data = GUILD_PERMISSIONS.get(guild_id, {})
        authorized_roles = guild_data.get("authorized_roles", [])
        user_roles = [role.id for role in ctx.author.roles]
        if any(role_id in authorized_roles for role_id in user_roles):
            return True

    return False

@bot.command(name="skull")
async def skull(ctx, action=None, member: discord.Member = None):
    if not args:
        embed = discord.Embed(title="Need Help?", description="Type `!help` to view all commands.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    first_arg = args[0].lower()
    mentioned_user = ctx.message.mentions[0] if ctx.message.mentions else None
        
    if mentioned_user and not first_arg.isalpha():
        if mentioned_user.id not in SKULL_LIST:
            SKULL_LIST.add(mentioned_user.id)
            save_skull_list(SKULL_LIST)
            embed = discord.Embed(
            title="💀 Skull granted",
            description=f"skulling {mentioned_user.mention} starting now.",
            color=discord.Color.dark_red()
            )
        elif mentioned_user.id in SKULL_LIST:
            embed = discord.Embed(
            title="Existing skull",
            description=f"{mentioned_user.mention} is already being skulled",
            color=discord.Color.light_grey()
            )
        else:
            embed = discord.Embed(
            title="Existing skull",
            description=f"{mentioned_user.mention} is already being skulled",
            color=discord.Color.light_grey()
            )
        await ctx.send(embed=embed)
        return
        
    action = args[0].lower()  # <-- This must come BEFORE any use of `action`
    author_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    if action.startswith("skull") and not mentioned_user:
        await ctx.send(embed=require_mention(action))
        return

    if action == "stop":
        if not is_authorized(ctx.author.id):
            return await ctx.send(embed=discord.Embed(
                title="❌ Unauthorized",
                description="Only authorized users can stop skulls.",
                color=discord.Color.red()
            ))
        
        if not member:
            return await ctx.send(embed=discord.Embed(
                title="⚠️ Missing Argument",
                description="Please mention a user.\nUsage: `!skull stop @user`",
                color=discord.Color.orange()
            ))

        skull_data = load_skull_list()
        user_id = str(member.id)

        if user_id not in skull_data:
            return await ctx.send(embed=discord.Embed(
                title="⚠️ Not Skulled",
                description=f"{member.mention} is not in the skull list.",
                color=discord.Color.orange()
            ))

        if skull_data[user_id] != str(ctx.author.id) and str(ctx.author.id) != YOUR_USER_ID:
            return await ctx.send(embed=discord.Embed(
                title="❌ Unauthorized",
                description="You didn't skull this user, and you're not an authorized admin.",
                color=discord.Color.red()
            ))

        del skull_data[user_id]
        save_skull_list(skull_data)
        await ctx.send(embed=discord.Embed(
            title="✅ Skull Removed",
            description=f"{member.mention} is no longer being skulled.",
            color=discord.Color.green()
        ))


        elif action == "list":
            if not is_authorized(ctx.author.id):
                return await ctx.send(embed=discord.Embed(
                    title="❌ Unauthorized",
                    description="Only authorized users can view the skull list.",
                    color=discord.Color.red()
                ))

            skull_data = load_skull_list()
            if not skull_data:
                return await ctx.send(embed=discord.Embed(
                    title="💀 Skull List",
                    description="Nobody is currently being skulled.",
                    color=discord.Color.purple()
                ))

            description = ""
            for target_id, author_id in skull_data.items():
                target = await bot.fetch_user(int(target_id))
                author = await bot.fetch_user(int(author_id))
                description += f"{target.mention} - Skulled by: {author.mention}\n"

            await ctx.send(embed=discord.Embed(
                title="💀 Skull List",
                description=description,
                color=discord.Color.purple()
            ))

        elif action == "authorize":
            if not is_authorized(ctx.author.id):
                return await ctx.send(embed=discord.Embed(
                    title="❌ Unauthorized",
                    description="Only authorized users can authorize others.",
                    color=discord.Color.red()
                ))

            if not member:
                return await ctx.send(embed=discord.Embed(
                    title="⚠️ Missing Argument",
                    description="Please mention a user to authorize.\nUsage: `!skull authorize @user`",
                    color=discord.Color.orange()
                ))

            authorized = load_authorized_users()
            if str(member.id) in authorized:
                return await ctx.send(embed=discord.Embed(
                    title="⚠️ Already Authorized",
                    description="This user is already authorized.",
                    color=discord.Color.orange()
                ))

            authorized.append(str(member.id))
            save_authorized_users(authorized)
            await ctx.send(embed=discord.Embed(
                title="✅ Authorized",
                description=f"{member.mention} is now authorized.",
                color=discord.Color.green()
            ))


        elif action == "unauthorize":
            if not is_authorized(ctx.author.id):
                return await ctx.send(embed=discord.Embed(
                    title="❌ Unauthorized",
                    description="Only authorized users can unauthorize others.",
                    color=discord.Color.red()
                ))

            if not member:
                return await ctx.send(embed=discord.Embed(
                    title="⚠️ Missing Argument",
                    description="Please mention a user to unauthorize.\nUsage: `!skull unauthorize @user`",
                    color=discord.Color.orange()
                ))

            authorized = load_authorized_users()
            if str(member.id) not in authorized:
                return await ctx.send(embed=discord.Embed(
                    title="⚠️ Not Authorized",
                    description="This user is not currently authorized.",
                    color=discord.Color.orange()
                ))

            authorized.remove(str(member.id))
            save_authorized_users(authorized)
            await ctx.send(embed=discord.Embed(
                title="🚫 Unauthorized",
                description=f"{member.mention} is no longer authorized.",
                color=discord.Color.red()
            ))

        elif action == "authorized":
            if not is_authorized(ctx.author.id):
                return await ctx.send(embed=discord.Embed(
                    title="❌ Unauthorized",
                    description="Only authorized users can view this list.",
                    color=discord.Color.red()
                ))

            authorized = load_authorized_users()
            if not authorized:
                return await ctx.send(embed=discord.Embed(
                    title="🔒 No Authorized Users",
                    description="No users are currently authorized.",
                    color=discord.Color.dark_red()
                ))

            description = ""
            for user_id in authorized:
                user = await bot.fetch_user(int(user_id))
                description += f"{user.mention}\nID: {user_id}\n"

            await ctx.send(embed=discord.Embed(
                title="🔐 Authorized Users",
                description=description,
                color=discord.Color.blue()
            ))

        if action == "allowguild":
            if ctx.author.id != YOUR_USER_ID:
                embed = discord.Embed(title="Access Denied", description="Only the bot owner can allow guilds.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

            if ctx.guild and ctx.guild.id not in AUTHORIZED_GUILDS:
                AUTHORIZED_GUILDS.add(ctx.guild.id)
                save_authorized_guilds(AUTHORIZED_GUILDS)
                embed = discord.Embed(title="Guild Authorized", description=f"Guild `{ctx.guild.name}` is now authorized.", color=discord.Color.green())
            else:
                embed = discord.Embed(title="Already Authorized", description="This guild is already authorized.", color=discord.Color.orange())
            await ctx.send(embed=embed)
            return

    if action == "disallowguild":
        if ctx.author.id != YOUR_USER_ID:
            embed = discord.Embed(title="Access Denied", description="Only the bot owner can disallow guilds.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        if ctx.guild and ctx.guild.id in AUTHORIZED_GUILDS:
            AUTHORIZED_GUILDS.remove(ctx.guild.id)
            save_authorized_guilds(AUTHORIZED_GUILDS)
            embed = discord.Embed(title="Guild Unauthorized", description=f"Guild `{ctx.guild.name}` has been removed from the authorized list.", color=discord.Color.red())
        else:
            embed = discord.Embed(title="Not Authorized", description="This guild is not in the authorized list.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return

    if action == "guilds":
        if ctx.author.id != YOUR_USER_ID:
            embed = discord.Embed(title="Access Denied", description="Only the bot owner can view authorized guilds.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        guild_entries = []
        for guild_id in AUTHORIZED_GUILDS:
            guild = bot.get_guild(guild_id)
            name = guild.name if guild else "Unknown"
            guild_entries.append(f"`{guild_id}` ({name})")

        if not guild_entries:
            embed = discord.Embed(title="Authorized Guilds", description="No guilds are currently authorized.", color=discord.Color.blurple())
            await ctx.send(embed=embed)
            return

        pages = list(chunk_list(guild_entries, 5))
        current_page = 0

        def generate_embed(page):
            embed = discord.Embed(title="Authorized Guilds", color=discord.Color.blurple())
            for entry in pages[page]:
                embed.add_field(name="", value=entry, inline=False)
            embed.set_footer(text=f"Page {page + 1} of {len(pages)}")
            return embed

        class Paginator(View):
            def __init__(self):
                super().__init__(timeout=60)

            @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
            async def previous(self, interaction: discord.Interaction, button: Button):
                nonlocal current_page
                if current_page > 0:
                    current_page -= 1
                    await interaction.response.edit_message(embed=generate_embed(current_page), view=self)

            @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
            async def next(self, interaction: discord.Interaction, button: Button):
                nonlocal current_page
                if current_page < len(pages) - 1:
                    current_page += 1
                    await interaction.response.edit_message(embed=generate_embed(current_page), view=self)

        await ctx.send(embed=generate_embed(current_page), view=Paginator())
        return

    # Fallback if command wasn't recognized
    embed = discord.Embed(title="Unknown Command", description=f"Type `{PREFIX}help` to see available actions.", color=discord.Color.red())
    await ctx.send(embed=embed)

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

bot.command()
@commands.has_permissions(manage_messages=True)
async def bc(ctx, limit: int = 100, user: discord.User = None, *, keyword: str = None):
    # Load authorized users
    with open("authorized_users.json", "r") as f:
        authorized_users = json.load(f)
    """
    Deletes messages by bot (or user/keyword), including the command message.
    Usage: !bc [limit] [@user (optional)] [keyword (optional)]
    """
    # Delete the command message itself first
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass  # It may already be gone
    if ctx.author.id not in authorized_users:
        embed = discord.Embed(
            title="🚫 Unauthorized",
            description="You are not authorized to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
        return
        
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

@bot.command(name='say')
async def say(ctx, *, message: str):
    try:
        await ctx.message.delete()  # Deletes the user's command message
    except discord.Forbidden:
        # If the bot doesn't have permission to delete messages
        pass
    
    await ctx.send(message)
    
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
async def serverstats(ctx):
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
    roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
    roles_display = ", ".join(roles) if roles else "No roles"

    embed = discord.Embed(
        title=f"👤 User Info — {member.display_name}",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Status", value=str(member.status).title(), inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="Roles", value=roles_display, inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def roleinfo(ctx, *, role: discord.Role = None):
    if role is None:
        embed = discord.Embed(
            title="Missing Argument",
            description="Please specify a role.\nUsage: ```!roleinfo <role name>```",
            color=discord.Color.orange()
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
async def showguilds(ctx):
    # Build your `guild_entries` list here
        pages = list(chunk_list(guild_entries, 5))
        current_page = 0

        def generate_embed(page):
            embed = discord.Embed(title="Authorized Guilds", color=discord.Color.blurple())
            for entry in pages[page]:
                embed.add_field(name="Guild", value=entry, inline=False)
            embed.set_footer(text=f"Page {page + 1} of {len(pages)}")
            return embed

        class Paginator(View):
            def __init__(self):
                super().__init__(timeout=60)

            @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
            async def previous(self, interaction: discord.Interaction, button: Button):
                nonlocal current_page
                if current_page > 0:
                    current_page -= 1
                    await interaction.response.edit_message(embed=generate_embed(current_page), view=self)

            @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
            async def next(self, interaction: discord.Interaction, button: Button):
                nonlocal current_page
                if current_page < len(pages) - 1:
                    current_page += 1
                    await interaction.response.edit_message(embed=generate_embed(current_page), view=self)

        await ctx.send(embed=generate_embed(current_page), view=Paginator())
        return


@bot.command()
async def restart(ctx):
    if ctx.author.id != YOUR_USER_ID:
        embed = discord.Embed(
            title="Access Denied",
            description="Only the bot owner can restart the bot.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="Restarting...",
        description="The bot is restarting now. Please wait a few seconds.",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)
    await bot.close()
    os._exit(0)  # Render will auto-restart the process


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

# Create your help pages as embeds
def get_help_pages(user_id):
    pages = []

    skull_embed = discord.Embed(title="☠️ Auto-skull Commands", color=discord.Color.blurple())
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
    info_embed.add_field(name="!userinfo", value="Show info about a user.", inline=False)
    info_embed.add_field(name="!serverstats", value="View server statistics.", inline=False)
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
        admin_embed.add_field(name="!skull allowguild", value="Allow this guild to use skull commands.", inline=False)
        admin_embed.add_field(name="!skull disallowguild", value="Disallow this guild from skull commands.", inline=False)
        admin_embed.add_field(name="!skull guilds", value="List all allowed guilds.", inline=False)
        admin_embed.add_field(name="!restart", value="Restart the bot.", inline=False)
        pages.append(admin_embed)

    return pages

# Main help command
@bot.command()
async def help(ctx):
    pages = get_help_pages(ctx.author.id)
    view = HelpView(pages, ctx.author)
    await view.send_initial(ctx)


bot.run(TOKEN)
