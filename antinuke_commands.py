import discord
from discord.ext import commands
import json
import os

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222

# Authorized users
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127}

# Create or load the antinuke configuration file
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

# Load configuration at startup
config = load_config()

async def toggle_antinuke(message):
    """
    Toggles the antinuke system on or off
    """
    if str(message.author.id) in AUTHORIZED_USERS:
        config["antinuke_enabled"] = not config["antinuke_enabled"]
        save_config(config)
        status = "enabled" if config["antinuke_enabled"] else "disabled"
        embed = discord.Embed(title="Antinuke Status", description=f"Antinuke has been {status}.", color=discord.Color.green())
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(title="Permission Denied", description="You need administrator permissions to toggle antinuke.", color=discord.Color.red())
        await message.channel.send(embed=embed)

async def whitelist_user(message):
    """
    Adds a user to the whitelist, allowing them to bypass antinuke restrictions
    """
    if str(message.author.id) in AUTHORIZED_USERS:
        mentioned_user = message.mentions[0] if message.mentions else None
        if mentioned_user:
            user_id = str(mentioned_user.id)
            if user_id not in config["whitelisted_users"]:
                config["whitelisted_users"].append(user_id)
                save_config(config)
                embed = discord.Embed(title="User Whitelisted", description=f"{mentioned_user.name} has been whitelisted.", color=discord.Color.green())
            else:
                embed = discord.Embed(title="User Already Whitelisted", description=f"{mentioned_user.name} is already whitelisted.", color=discord.Color.yellow())
        else:
            embed = discord.Embed(title="Error", description="Please mention a user to whitelist.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(title="Permission Denied", description="You need administrator permissions to whitelist users.", color=discord.Color.red())
        await message.channel.send(embed=embed)

async def unwhitelist_user(message):
    """
    Removes a user from the whitelist
    """
    if str(message.author.id) in AUTHORIZED_USERS:
        mentioned_user = message.mentions[0] if message.mentions else None
        if mentioned_user:
            user_id = str(mentioned_user.id)
            if user_id in config["whitelisted_users"]:
                config["whitelisted_users"].remove(user_id)
                save_config(config)
                embed = discord.Embed(title="User Unwhitelisted", description=f"{mentioned_user.name} has been unwhitelisted.", color=discord.Color.green())
            else:
                embed = discord.Embed(title="User Not Found", description=f"{mentioned_user.name} is not whitelisted.", color=discord.Color.yellow())
        else:
            embed = discord.Embed(title="Error", description="Please mention a user to unwhitelist.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(title="Permission Denied", description="You need administrator permissions to unwhitelist users.", color=discord.Color.red())
        await message.channel.send(embed=embed)

async def list_whitelisted(message):
    """
    Lists all the whitelisted users.
    """
    if str(message.author.id) in AUTHORIZED_USERS:
        if config["whitelisted_users"]:
            whitelisted = [f"<@{user_id}>" for user_id in config["whitelisted_users"]]
            embed = discord.Embed(title="Whitelisted Users", description="\n".join(whitelisted), color=discord.Color.blurple())
        else:
            embed = discord.Embed(title="No Whitelisted Users", description="There are no whitelisted users.", color=discord.Color.red())
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(title="Permission Denied", description="You need administrator permissions to view the whitelist.", color=discord.Color.red())
        await message.channel.send(embed=embed)

async def show_antinuke_status(message):
    """
    Shows the current status of the antinuke system
    """
    if str(message.author.id) in AUTHORIZED_USERS:
        status = "enabled" if config["antinuke_enabled"] else "disabled"
        embed = discord.Embed(title="Antinuke Status", description=f"Antinuke is currently {status}.", color=discord.Color.green())
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(title="Permission Denied", description="You need administrator permissions to view the antinuke status.", color=discord.Color.red())
        await message.channel.send(embed=embed)