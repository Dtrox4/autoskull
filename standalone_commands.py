import discord
import os
import sys
import random
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

# handle_eightball
async def handle_eightball(message, question):
    responses = ["Yes", "No", "Maybe", "Definitely", "Ask again later", "Absolutely not"]
    response = random.choice(responses)
    embed = discord.Embed(title="🎱 8Ball", color=discord.Color.random())
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=response, inline=False)
    embed.set_footer(text=f"Asked by {message.author}", icon_url=message.author.display_avatar.url)
    await message.channel.send(embed=embed)

