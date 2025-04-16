import discord
import asyncio
import random

EIGHTBALL_ANSWERS = [
    "Yes.", "No.", "Maybe.", "Definitely!", "Absolutely not.", "I don't know.",
    "Ask again later.", "Trust me.", "It's certain.", "Not a chance."
]

async def handle_poll(message):
    parts = message.content.split(None, 1)
    if len(parts) < 2:
        return await message.channel.send(embed=discord.Embed(
            title="Command: !poll",
            description="**Usage:** `!poll <your question>`",
            color=discord.Color.blue()
        ))

    question = parts[1]
    embed = discord.Embed(title="New Poll", description=question, color=discord.Color.blurple())
    embed.set_footer(text=f"Poll by {message.author}", icon_url=message.author.avatar.url)
    poll_msg = await message.channel.send(embed=embed)
    await poll_msg.add_reaction("✅")
    await poll_msg.add_reaction("❌")

async def handle_eightball(message):
    parts = message.content.split(None, 1)
    if len(parts) < 2:
        return await message.channel.send(embed=discord.Embed(
            title="Command: !eightball",
            description="**Usage:** `!eightball <your question>`",
            color=discord.Color.blue()
        ))

    question = parts[1]
    answer = random.choice(EIGHTBALL_ANSWERS)
    embed = discord.Embed(title="8Ball", description=f"**Question:** {question}\n**Answer:** {answer}", color=discord.Color.purple())
    await message.channel.send(embed=embed)

async def handle_serverinfo(message):
    guild = message.guild
    embed = discord.Embed(title=f"{guild.name} Info", color=discord.Color.green())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Owner", value=str(guild.owner), inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=False)
    embed.add_field(name="Roles", value=len(guild.roles), inline=False)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    await message.channel.send(embed=embed)

async def handle_userinfo(message):
    args = message.content.split()
    if len(args) < 2:
        return await message.channel.send(embed=discord.Embed(
            title="Command: !userinfo",
            description="**Usage:** `!userinfo <@mention or user id>`",
            color=discord.Color.blue()
        ))

    user = None
    if message.mentions:
        user = message.mentions[0]
    else:
        try:
            user = await message.guild.fetch_member(int(args[1]))
        except:
            return await message.channel.send("User not found.")

    embed = discord.Embed(title="User Info", color=discord.Color.orange())
    embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
    embed.add_field(name="Username", value=str(user), inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    await message.channel.send(embed=embed)

async def handle_remind(message):
    args = message.content.split(maxsplit=2)
    if len(args) < 3:
        return await message.channel.send(embed=discord.Embed(
            title="Command: !remind",
            description="**Usage:** `!remind <time> <message>`\nExample: `!remind 10m take a break`",
            color=discord.Color.blue()
        ))

    time_str = args[1]
    reminder = args[2]

    units = {"s": 1, "m": 60, "h": 3600}
    try:
        delay = int(time_str[:-1]) * units[time_str[-1]]
    except:
        return await message.channel.send(embed=discord.Embed(
            title="Command: !remind",
            description="Invalid time format. Use `10s`, `5m`, or `1h`.",
            color=discord.Color.red()
        ))

    await message.channel.send(f"I'll remind you in {time_str}!")
    await asyncio.sleep(delay)
    await message.channel.send(f"Reminder for {message.author.mention}: {reminder}")

async def handle_roleinfo(message):
    args = message.content.split(maxsplit=1)
    if len(args) < 2:
        return await message.channel.send(embed=discord.Embed(
            title="Command: !roleinfo",
            description="**Usage:** `!roleinfo <@role / role id / role name>`",
            color=discord.Color.blue()
        ))

    role = None
    if message.role_mentions:
        role = message.role_mentions[0]
    else:
        try:
            role_id = int(args[1])
            role = message.guild.get_role(role_id)
        except:
            role = discord.utils.get(message.guild.roles, name=args[1])

    if not role:
        return await message.channel.send("Role not found.")

    embed = discord.Embed(title="Role Info", color=role.color)
    embed.add_field(name="Name", value=role.name, inline=False)
    embed.add_field(name="ID", value=role.id, inline=False)
    embed.add_field(name="Color", value=str(role.color), inline=False)
    embed.add_field(name="Mentionable", value=role.mentionable, inline=False)
    embed.add_field(name="Position", value=role.position, inline=False)
    embed.add_field(name="Members with Role", value=len(role.members), inline=False)
    await message.channel.send(embed=embed)