import emoji as emoji_lib  # pip install emoji

def is_valid_emoji(emoji_str):
    return emoji_lib.is_emoji(emoji_str) or (
        emoji_str.startswith("<:") and emoji_str.endswith(">")
    )

async def handle_react_command(message):
    if not message.content.startswith("!react"):
        return

    if message.author.id not in AUTHORIZED_USERS:
        embed = discord.Embed(
            title="⛔ Unauthorized",
            description="You are not allowed to use this command.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if not message.mentions:
        embed = discord.Embed(
            title="⚠️ Invalid Usage",
            description="Use `!react @user <emoji>`",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return

    args = message.content.split()
    if len(args) < 3:
        embed = discord.Embed(
            title="⚠️ Missing Emoji",
            description="Please specify an emoji to react with. Example: `!react @user 😂`",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed)
        return

    target = message.mentions[0]
    emoji = args[2]

    if not is_valid_emoji(emoji):
        embed = discord.Embed(
            title="❌ Invalid Emoji",
            description="Please enter a valid emoji only. Example: `!react @user 😂`",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if target.id in auto_react_users:
        del auto_react_users[target.id]
        embed = discord.Embed(
            title="❌ Auto-React Disabled",
            description=f"Auto-reactions disabled for {target.mention}.",
            color=discord.Color.red()
        )
    else:
        auto_react_users[target.id] = emoji
        embed = discord.Embed(
            title="✅ Auto-React Enabled",
            description=f"{target.mention} will now receive auto-reactions with {emoji}.",
            color=discord.Color.green()
        )

    await message.channel.send(embed=embed)