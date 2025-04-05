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
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

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

YOUR_USER_ID =   # Replace with your actual Discord ID

# Use `commands.Bot`
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

keep_alive()
# your bot stuff here

start_time = datetime.datetime.utcnow()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

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

class ConfirmView(discord.ui.View):
    def __init__(self, author, on_confirm, on_cancel):
        super().__init__(timeout=30)
        self.author = author
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("You're not allowed to interact with this.", ephemeral=True)
            return
        await interaction.response.defer()
        await self.on_confirm()
        self.stop()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("You're not allowed to interact with this.", ephemeral=True)
            return
        await interaction.response.send_message("Action cancelled.", ephemeral=True)
        await self.on_cancel()
        self.stop()

@bot.group()
async def skull(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(embed=create_embed("Skull Command", "Use a subcommand: list, start @user, stop @user", discord.Color.orange()))

@skull.command()
async def authorize(ctx, member: discord.Member):
    if ctx.author.id != YOUR_USER_ID:
        return await ctx.send(embed=create_embed("Unauthorized", "Only the bot owner can authorize users.", discord.Color.red()))

    async def confirm_action():
        authorized_users = read_json(authorized_users_file)
        if member.id in authorized_users:
            await ctx.send(embed=create_embed("Already Authorized", f"{member.display_name} is already authorized."))
            return
        authorized_users.append(member.id)
        write_json(authorized_users_file, authorized_users)
        await ctx.send(embed=create_embed("✅ Authorized", f"{member.display_name} has been authorized."))

    async def cancel_action():
        pass

    view = ConfirmView(ctx.author, confirm_action, cancel_action)
    await ctx.send(embed=create_embed("Confirm Authorization", f"Are you sure you want to authorize {member.mention}?"), view=view)

@skull.command()
async def unauthorize(ctx, member: discord.Member):
    if ctx.author.id != YOUR_USER_ID:
        return await ctx.send(embed=create_embed("Unauthorized", "Only the bot owner can unauthorize users.", discord.Color.red()))

    async def confirm_action():
        authorized_users = read_json(authorized_users_file)
        if member.id not in authorized_users:
            await ctx.send(embed=create_embed("Not Authorized", f"{member.display_name} is not authorized."))
            return
        authorized_users.remove(member.id)
        write_json(authorized_users_file, authorized_users)
        await ctx.send(embed=create_embed("🗑️ Unauthorize", f"{member.display_name} has been removed from the authorized list."))

    async def cancel_action():
        pass

    view = ConfirmView(ctx.author, confirm_action, cancel_action)
    await ctx.send(embed=create_embed("Confirm Unauthorization", f"Are you sure you want to remove {member.mention} from the authorized list?"), view=view)

@bot.group()
async def skull(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(embed=create_embed("Skull Command", "Use a subcommand: list, start @user, stop @user", discord.Color.orange()))

@skull.command()
async def start(ctx, member: discord.Member):
    authorized_users = read_json(authorized_users_file)
    if ctx.author.id not in authorized_users and ctx.author.id != YOUR_USER_ID:
        return await ctx.send(embed=create_embed("Unauthorized", "You are not authorized to use this command.", discord.Color.red()))

    skull_list = read_json(skull_list_file)
    if member.id in skull_list:
        return await ctx.send(embed=create_embed("Already Skulled", f"{member.display_name} is already being skulled."))

    skull_list.append(member.id)
    write_json(skull_list_file, skull_list)
    await ctx.send(embed=create_embed("✅ Skull Started", f"{member.display_name} will now be skulled."))

@skull.command()
async def stop(ctx, member: discord.Member):
    authorized_users = read_json(authorized_users_file)
    if ctx.author.id not in authorized_users and ctx.author.id != YOUR_USER_ID:
        return await ctx.send(embed=create_embed("Unauthorized", "You are not authorized to use this command.", discord.Color.red()))

    skull_list = read_json(skull_list_file)
    if member.id not in skull_list:
        return await ctx.send(embed=create_embed("Not Skulled", f"{member.display_name} is not being skulled."))

    skull_list.remove(member.id)
    write_json(skull_list_file, skull_list)
    await ctx.send(embed=create_embed("🛑 Skull Stopped", f"{member.display_name} is no longer being skulled."))

@skull.command()
async def list(ctx):
    skull_list = read_json(skull_list_file)
    if not skull_list:
        return await ctx.send(embed=create_embed("💀 Skull List", "No users are currently being skulled."))

    users = []
    for uid in skull_list:
        member = ctx.guild.get_member(uid)
        if member:
            users.append(member.display_name)
        else:
            users.append(f"Unknown User ({uid})")

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
