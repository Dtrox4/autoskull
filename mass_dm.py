import discord
import time

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222

# Authorized users
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127, 1305007578857869403}

massdm_cooldowns = {}  # user_id : last_used_time

async def handle_massdm(message):
    user_id = message.author.id

    # Cooldown check
    now = time.time()
    last_used = massdm_cooldowns.get(user_id, 0)
    cooldown = 600  # seconds

    if user_id not in AUTHORIZED_USERS:
        embed = discord.Embed(
            description="❌ You are not authorized to use this command.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if now - last_used < cooldown:
        remaining = int(cooldown - (now - last_used))
        embed = discord.Embed(
            description=f"⏳ You must wait `{remaining}s` before using this command again.",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return

    try:
        await message.delete()
    except discord.Forbidden:
        pass

    content = message.content.strip()
    command_prefix = "!massdm"
    dm_content = content[len(command_prefix):].strip()

    if not dm_content:
        embed = discord.Embed(
            description="⚠️ You must provide a message to DM.\n**Usage:** `!massdm <message>`",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return

    sent = 0
    failed = 0
    for member in message.guild.members:
        if member.bot:
            continue
        try:
            await member.send(dm_content)
            sent += 1
        except Exception:
            failed += 1

    massdm_cooldowns[user_id] = now  # Set cooldown

    result = f"✅ DMed {sent} member(s).\n❌ Failed to DM {failed} member(s)."
    await message.channel.send(result)
