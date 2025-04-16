import discord
import json
import os

# Static authorized user IDs (trusted owners/developers)
AUTHORIZED_USERS = {1212229549459374222, 845578292778238002, 1177672910102614127}

# Antinuke config file
CONFIG_FILE = "antinuke_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"antinuke_enabled": False, "whitelisted_users": []}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Load config at startup
config = load_config()

def is_authorized(user_id):
    """Checks if a user is allowed to use antinuke commands"""
    return str(user_id) in config["whitelisted_users"] or user_id in AUTHORIZED_USERS

async def toggle_antinuke(message):
    if is_authorized(message.author.id):
        config["antinuke_enabled"] = not config["antinuke_enabled"]
        save_config(config)
        status = "enabled ✅" if config["antinuke_enabled"] else "disabled ❌"
        embed = discord.Embed(title="Antinuke Status", description=f"Antinuke has been **{status}**.", color=discord.Color.green())
        await message.channel.send(embed=embed)
    else:
        await no_permission(message)

async def whitelist_user(message):
    if is_authorized(message.author.id):
        mentioned_user = message.mentions[0] if message.mentions else None
        if mentioned_user:
            user_id = str(mentioned_user.id)
            if user_id not in config["whitelisted_users"]:
                config["whitelisted_users"].append(user_id)
                save_config(config)
                embed = discord.Embed(title="✅ User Whitelisted", description=f"{mentioned_user.mention} has been added to the whitelist.", color=discord.Color.green())
            else:
                embed = discord.Embed(title="⚠️ Already Whitelisted", description=f"{mentioned_user.mention} is already in the whitelist.", color=discord.Color.gold())
        else:
            embed = discord.Embed(title="❌ Invalid Usage", description="Please mention a user to whitelist.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    else:
        await no_permission(message)

async def unwhitelist_user(message):
    if is_authorized(message.author.id):
        mentioned_user = message.mentions[0] if message.mentions else None
        if mentioned_user:
            user_id = str(mentioned_user.id)
            if user_id in config["whitelisted_users"]:
                config["whitelisted_users"].remove(user_id)
                save_config(config)
                embed = discord.Embed(title="✅ User Unwhitelisted", description=f"{mentioned_user.mention} has been removed from the whitelist.", color=discord.Color.green())
            else:
                embed = discord.Embed(title="⚠️ Not Whitelisted", description=f"{mentioned_user.mention} is not in the whitelist.", color=discord.Color.gold())
        else:
            embed = discord.Embed(title="❌ Invalid Usage", description="Please mention a user to unwhitelist.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    else:
        await no_permission(message)

async def list_whitelisted(message):
    if is_authorized(message.author.id):
        if config["whitelisted_users"]:
            whitelisted_mentions = [f"<@{uid}>" for uid in config["whitelisted_users"]]
            embed = discord.Embed(title="🛡️ Whitelisted Users", description="\n".join(whitelisted_mentions), color=discord.Color.blurple())
        else:
            embed = discord.Embed(title="🚫 No Whitelisted Users", description="The whitelist is currently empty.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    else:
        await no_permission(message)

async def show_antinuke_status(message):
    if is_authorized(message.author.id):
        status = "enabled ✅" if config["antinuke_enabled"] else "disabled ❌"
        embed = discord.Embed(title="🛡️ Antinuke Status", description=f"Antinuke is currently **{status}**.", color=discord.Color.green())
        await message.channel.send(embed=embed)
    else:
        await no_permission(message)

async def no_permission(message):
    embed = discord.Embed(
        title="🚫 Permission Denied",
        description="You are not authorized to use this antinuke command.",
        color=discord.Color.red()
    )
    await message.channel.send(embed=embed)
