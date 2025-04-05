import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions, MissingRequiredArgument
import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Ensure files exist
authorized_users_file = "authorized_users.json"
skull_list_file = "skull_list.json"

for file in [authorized_users_file, skull_list_file]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

# Utility functions for reading/writing JSON files
def read_json(file):
    with open(file, "r") as f:
        return json.load(f)

def write_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# Embed utility
def create_embed(title, description=None, color=discord.Color.blue(), fields=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed

YOUR_USER_ID = 123456789012345678  # Replace with your actual Discord ID

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def say(ctx, *, message=None):
    if not message:
        await ctx.send(embed=create_embed("Missing message", "Please provide a message to say.", discord.Color.red()))
    else:
        await ctx.message.delete()
        await ctx.send(message)

@bot.command()
async def roleinfo(ctx, *, role: discord.Role = None):
    if role is None:
        await ctx.send(embed=create_embed("Missing Role", "Please mention a valid role.", discord.Color.red()))
        return

    fields = [
        ("ID", role.id, True),
        ("Color", str(role.color), True),
        ("Members", len(role.members), True),
        ("Mentionable", role.mentionable, True),
        ("Position", role.position, True),
        ("Permissions", role.permissions.value, True)
    ]
    await ctx.send(embed=create_embed(f"Role Info: {role.name}", fields=fields))

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    fields = [
        ("ID", guild.id, True),
        ("Owner", str(guild.owner), True),
        ("Region", str(guild.preferred_locale), True),
        ("Created At", guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), False),
        ("Members", guild.member_count, True),
        ("Text Channels", len(guild.text_channels), True),
        ("Voice Channels", len(guild.voice_channels), True),
        ("Roles", len(guild.roles), True),
    ]
    await ctx.send(embed=create_embed(f"Server Info: {guild.name}", fields=fields))

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = ', '.join([role.name for role in member.roles if role != ctx.guild.default_role]) or 'None'
    fields = [
        ("ID", member.id, True),
        ("Status", str(member.status), True),
        ("Top Role", str(member.top_role), True),
        ("Joined Server", member.joined_at.strftime("%Y-%m-%d"), True),
        ("Account Created", member.created_at.strftime("%Y-%m-%d"), True),
        ("Roles", roles, False)
    ]
    await ctx.send(embed=create_embed(f"User Info: {member.display_name}", fields=fields))

@bot.command()
async def eightball(ctx, *, question):
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes – definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]
    await ctx.send(embed=create_embed("🎱 8Ball", f"Question: {question}\nAnswer: {random.choice(responses)}"))

@bot.command()
async def remind(ctx, time: int, *, reminder: str):
    await ctx.send(embed=create_embed("Reminder Set!", f"I'll remind you in {time} seconds."))
    await asyncio.sleep(time)
    await ctx.send(embed=create_embed("⏰ Reminder!", f"{ctx.author.mention}, remember: {reminder}"))

@bot.command()
async def poll(ctx, *, question):
    embed = create_embed("📊 Poll", question)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command()
async def stats(ctx):
    total_members = sum(guild.member_count for guild in bot.guilds)
    fields = [
        ("Servers", len(bot.guilds), True),
        ("Users", total_members, True)
    ]
    await ctx.send(embed=create_embed("🤖 Bot Stats", fields=fields))

class HelpButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="General", style=discord.ButtonStyle.primary)
    async def general(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed("🧰 General Commands", fields=[
            ("!serverinfo", "Shows server details", True),
            ("!userinfo", "Shows info about a user", True),
            ("!roleinfo", "Shows info about a role", True),
            ("!say", "Bot repeats your message", True),
            ("!remind", "Set a reminder", True),
            ("!stats", "Show bot statistics", True)
        ])
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Fun", style=discord.ButtonStyle.success)
    async def fun(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed("🎉 Fun Commands", fields=[
            ("!eightball", "Ask the magic 8ball a question", True),
            ("!poll", "Create a simple poll", True)
        ])
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Skull Basic", style=discord.ButtonStyle.danger)
    async def skull_basic(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed("💀 Skull - Basic", fields=[
            ("!skull list", "View skull'd users list", True),
            ("!skull stop @user", "Stop skulling a user", True)
        ])
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Skull Admin", style=discord.ButtonStyle.danger)
    async def skull_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed("🔐 Skull - Admin", fields=[
            ("!skull authorize @user", "Authorize a user", True),
            ("!skull unauthorize @user", "Remove user from authorized list", True),
            ("!skull authorized", "View authorized users", True),
            ("!skull help", "Show skull command usage", True),
            ("!skull adminhelp", "Show advanced skull admin usage", True),
            ("!bc", "Bulk delete messages with filters", True)
        ])
        await interaction.response.edit_message(embed=embed, view=self)

@bot.command()
async def help(ctx):
    embed = create_embed("📖 Help Menu", "Click a button below to explore command categories.")
    await ctx.send(embed=embed, view=HelpButton())

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Failed to start bot: {e}")
