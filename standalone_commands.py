import discord
import os
import sys
import platform
import asyncio

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222

# All the functions go here:

# handle_poll
async def handle_poll(message, question):
    if not question.strip():
        error_embed = discord.Embed(
            title="Error",
            description="Please provide a question for the poll.\n\n**Usage:** `!poll <question>`",
            color=discord.Color.red()
        )
        await message.channel.send(embed=error_embed)
        return

    embed = discord.Embed(
        title="🗳️ New Poll",
        description=question,
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Started by {message.author}", icon_url=message.author.display_avatar.url)
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

# handle_remind
async def handle_remind(message, time_in_seconds, reminder):
    await message.channel.send(embed=discord.Embed(
        description=f"⏰ Reminder set for **{time_in_seconds}** seconds.",
        color=discord.Color.teal()
    ))
    await asyncio.sleep(time_in_seconds)
    await message.channel.send(embed=discord.Embed(
        title="⏰ Reminder!",
        description=reminder,
        color=discord.Color.red()
    ).set_footer(text=f"Reminder for {message.author}", icon_url=message.author.display_avatar.url))

# handle_serverinfo
async def handle_serverinfo(message):
    guild = message.guild
    embed = discord.Embed(title="📈 Server Stats", color=discord.Color.purple())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Server Name", value=guild.name)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Owner", value=guild.owner)
    embed.set_footer(text=f"Requested by {message.author}", icon_url=message.author.display_avatar.url)
    await message.channel.send(embed=embed)

# handle_userinfo
async def handle_userinfo(message, member: discord.Member = None):
    member = member or message.author

    embed = discord.Embed(title=f"User Info: {member}", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="Status", value=str(member.status).title(), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

    await message.channel.send(embed=embed)

# handle_roleinfo
async def handle_roleinfo(message, role: discord.Role = None):
    if role is None:
        embed = discord.Embed(
            title="Missing Argument",
            description="Please specify a role.\nUsage: `!roleinfo <role name>`",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    embed = discord.Embed(title=f"Role Info: {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id, inline=True)
    embed.add_field(name="Color", value=str(role.color), inline=True)
    embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
    embed.add_field(name="Hoisted", value=role.hoist, inline=True)
    embed.add_field(name="Position", value=role.position, inline=True)
    embed.add_field(name="Member Count", value=len(role.members), inline=True)
    embed.set_footer(text=f"Created at: {role.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    await message.channel.send(embed=embed)

# handle_eightball
import random

async def handle_eightball(message, question):
    responses = ["Yes", "No", "Maybe", "Definitely", "Ask again later", "Absolutely not"]
    response = random.choice(responses)
    embed = discord.Embed(title="🎱 8Ball", color=discord.Color.random())
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=response, inline=False)
    embed.set_footer(text=f"Asked by {message.author}", icon_url=message.author.display_avatar.url)
    await message.channel.send(embed=embed)

# handle_bc
async def handle_bc(message, args):
    if not message.author.guild_permissions.manage_messages:
        await message.channel.send("You don't have the required **permission** : `manage_messages` to use this command.")
        return

    if len(args) < 1:
        await message.channel.send("Usage: `!bc <count> [contains <word>]`")
        return

    try:
        count = int(args[0])
    except ValueError:
        await message.channel.send("First argument must be a number.")
        return

    keyword = None
    if len(args) >= 3 and args[1].lower() == "contains":
        keyword = " ".join(args[2:])

    def check(msg):
        return keyword.lower() in msg.content.lower() if keyword else True

    deleted = await message.channel.purge(limit=count+1, check=check)
    await message.channel.send(f"Deleted {len(deleted)-1} messages.", delete_after=5)
