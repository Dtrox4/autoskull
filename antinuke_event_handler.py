import discord
from discord.ext import commands, tasks
import json
import os
import asyncio

CONFIG_FILE = "antinuke_config.json"
BACKUP_FILE = "antinuke_backup.json"

# Load the config
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = {"antinuke_enabled": False, "whitelisted_users": []}

# Save helper
def save_backup(data):
    with open(BACKUP_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_backup():
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, 'r') as f:
            return json.load(f)
    return {}

# Main event handler setup
def setup_event_handlers(bot):
    @bot.event
    async def on_guild_channel_delete(channel):
        if not config.get("antinuke_enabled"):
            return

        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if str(entry.user.id) not in config["whitelisted_users"]:
                await channel.guild.ban(entry.user, reason="Unauthorized channel deletion detected by AntiNuke")
                await restore_channel(channel)
                return

    @bot.event
    async def on_guild_channel_create(channel):
        if not config.get("antinuke_enabled"):
            return

        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            if str(entry.user.id) not in config["whitelisted_users"]:
                await channel.guild.ban(entry.user, reason="Unauthorized channel creation detected by AntiNuke")
                await channel.delete()
                return

    @bot.event
    async def on_member_ban(guild, user):
        if not config.get("antinuke_enabled"):
            return

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if str(entry.user.id) not in config["whitelisted_users"]:
                await guild.unban(user, reason="Auto-rejoin protection")
                await guild.ban(entry.user, reason="Unauthorized ban action detected by AntiNuke")
                return

    @bot.event
    async def on_member_remove(member):
        if not config.get("antinuke_enabled"):
            return

        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if str(entry.user.id) not in config["whitelisted_users"]:
                await member.guild.ban(entry.user, reason="Unauthorized kick detected by AntiNuke")
                # You can implement reinvite logic here (if your bot has an invite link stored)
                return

    @bot.event
    async def on_guild_role_delete(role):
        if not config.get("antinuke_enabled"):
            return

        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if str(entry.user.id) not in config["whitelisted_users"]:
                await role.guild.ban(entry.user, reason="Unauthorized role deletion detected by AntiNuke")
                await restore_role(role.guild, role)
                return

# Restore Functions
async def restore_channel(channel):
    backup = load_backup()
    data = backup.get("channels", {}).get(str(channel.id))
    if not data:
        return
    guild = channel.guild
    new_channel = await guild.create_text_channel(name=data['name'], position=data['position'])
    # Permissions etc can be added

async def restore_role(guild, role):
    backup = load_backup()
    data = backup.get("roles", {}).get(str(role.id))
    if not data:
        return
    new_role = await guild.create_role(
        name=data['name'],
        permissions=discord.Permissions(data['permissions']),
        colour=discord.Colour(data['color'])
    )
    # Position etc can be added

# Optional: Task to regularly backup roles/channels
async def backup_loop():
    for guild in bot.guilds:
        backup = {"roles": {}, "channels": {}}

        for role in guild.roles:
            if role.is_default():
                continue
            backup["roles"][str(role.id)] = {
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
            }

        for channel in guild.text_channels:
            backup["channels"][str(channel.id)] = {
                "name": channel.name,
                "position": channel.position
            }

        save_backup(backup)

# Start the backup task only when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    backup_loop.start()

# Add your bot setup
bot = commands.Bot(command_prefix="!")

# Register the event handlers and start the bot
setup_event_handlers(bot)
