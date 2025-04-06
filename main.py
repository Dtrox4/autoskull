import discord 
import asyncio
import datetime
import os
import json
from discord.ui import View, Button
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# File paths
authorized_users_file = "authorized_users.json"
skull_list_file = "skull_list.json"

def read_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)
    with open(file, 'r') as f:
        return json.load(f)

def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

class AutoSkullBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix='!', intents=intents)
        self.authorized_users = read_json(authorized_users_file)
        self.skull_list = read_json(skull_list_file)

    async def setup_hook(self):
        print(f"Logged in as {self.user} ({self.user.id})")
        await self.change_presence(activity=discord.Game(name="if you're worthy, you shall be skulled"))

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.lower() == "skull me":
            await message.channel.send(f"{message.author.mention} ☠️")

        if message.author.id in [int(uid) for uid in self.authorized_users] and "skull" in message.content.lower():
            await message.add_reaction("☠️")

        await self.process_commands(message)

    def is_authorized(self, ctx):
        return str(ctx.author.id) in self.authorized_users

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = AutoSkullBot(intents)

load_flask()

@bot.command()
async def skull(ctx, subcommand=None, *args):
    if not bot.is_authorized(ctx):
        await ctx.send(embed=discord.Embed(description="❌ You are not authorized to use this command.", color=discord.Color.red()))
        return

    if subcommand is None:
        await ctx.send(embed=discord.Embed(description="Usage: `!skull <@user>` or `!skull <subcommand>`\nType `!skull help` for subcommands.", color=discord.Color.orange()))
        return


    if subcommand == "authorized":
        authorized_users = read_json(authorized_users_file)
        if not authorized_users:
            await ctx.send(embed=discord.Embed(description="No authorized users.", color=discord.Color.orange()))
        else:
            names = []
            for uid in authorized_users:
                user = await bot.fetch_user(int(uid))
                names.append(f"{user.name}#{user.discriminator} ({uid})")
            await ctx.send(embed=discord.Embed(title="Authorized Users", description="\n".join(names), color=discord.Color.green()))

    elif subcommand == "adminhelp":
        embed = discord.Embed(title="🔒 Skull Admin Help", color=discord.Color.dark_red())
        embed.add_field(name="!skull authorize <@user>", value="Add an authorized user.", inline=False)
        embed.add_field(name="!skull unauthorize <@user>", value="Remove an authorized user.", inline=False)
        await ctx.send(embed=embed)

    elif subcommand == "authorize" and args:
        user = args[0]
        user_id = user.strip('<@!>')
        if user_id not in bot.authorized_users:
            bot.authorized_users.append(user_id)
            write_json(authorized_users_file, bot.authorized_users)
            await ctx.send(embed=discord.Embed(description=f"✅ User <@{user_id}> authorized.", color=discord.Color.green()))
        else:
            await ctx.send(embed=discord.Embed(description=f"⚠️ User <@{user_id}> is already authorized.", color=discord.Color.orange()))

    elif subcommand == "unauthorize" and args:
        user = args[0]
        user_id = user.strip('<@!>')
        if user_id in bot.authorized_users:
            bot.authorized_users.remove(user_id)
            write_json(authorized_users_file, bot.authorized_users)
            await ctx.send(embed=discord.Embed(description=f"❌ User <@{user_id}> unauthorized.", color=discord.Color.red()))
        else:
            await ctx.send(embed=discord.Embed(description=f"⚠️ User <@{user_id}> is not authorized.", color=discord.Color.orange()))

    elif subcommand == "list":
        skull_list = read_json(skull_list_file)
        if not skull_list:
            await ctx.send(embed=discord.Embed(description="☠️ No users have been skulled yet!", color=discord.Color.orange()))
            return

        pages = []
        for i in range(0, len(skull_list), 10):
            chunk = skull_list[i:i + 10]
            desc = ""
            for entry in chunk:
                user = await bot.fetch_user(entry["user_id"])
                timestamp = entry["timestamp"]
                desc += f"{user.mention} - {timestamp}\n"
            embed = discord.Embed(title="💀 Skull List", description=desc, color=discord.Color.purple())
            embed.set_footer(text=f"Page {i//10+1} of {(len(skull_list)-1)//10+1}")
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


    elif subcommand == "stop" and args:
        user = args[0]
        user_id = user.strip('<@!>')
        skull_list = read_json(skull_list_file)
        if user_id in skull_list:
            skull_list.remove(user_id)
            write_json(skull_list_file, skull_list)
            await ctx.send(embed=discord.Embed(description=f"🛑 Stopped skull on <@{user_id}>.", color=discord.Color.red()))
        else:
            await ctx.send(embed=discord.Embed(description=f"⚠️ <@{user_id}> is not being skulled.", color=discord.Color.orange()))

    elif discord.utils.get(ctx.message.mentions, id=ctx.message.mentions[0].id) if ctx.message.mentions else None:
        user = ctx.message.mentions[0]
        skull_list = read_json(skull_list_file)
        if str(user.id) not in skull_list:
            skull_list.append(str(user.id))
            write_json(skull_list_file, skull_list)
            await ctx.send(embed=discord.Embed(description=f"☠️ Started skull on {user.mention}.", color=discord.Color.purple()))
        else:
            await ctx.send(embed=discord.Embed(description=f"⚠️ {user.mention} is already being skulled.", color=discord.Color.orange()))

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
    if role is None:
        embed = discord.Embed(
            title="Missing Argument",
            description="Please mention.\nUsage: ```!roleinfo <@user>```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
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

    skull_embed = discord.Embed(title="☠️ Skull Commands", color=discord.Color.blurple())
    skull_embed.add_field(name="!skull start <@user>", value="Grant auto-skull privileges to a user.", inline=False)
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
        admin_embed.add_field(name="!restart", value="Restart the bot from root.", inline=False)
        pages.append(admin_embed)

    return pages

# Main help command
@bot.command()
async def help(ctx):
    pages = get_help_pages(ctx.author.id)
    view = HelpView(pages, ctx.author)
    await view.send_initial(ctx)

bot.run(TOKEN)  
