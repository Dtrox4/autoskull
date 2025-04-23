import emoji as emoji_lib  # pip install emoji

import discord



# Dictionary to store users and their assigned emoji for auto-reacting
auto_react_users = {}  # <-- Make sure this is declared at the top

# Then define your functions below
async def auto_react_to_messages(message):
    emoji = auto_react_users.get(message.author.id)
    if emoji:
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            pass

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

async def handle_reactlist_command(message):
    if message.author.id not in AUTHORIZED_USERS:
        embed = discord.Embed(
            title="⛔ Unauthorized",
            description="You are not allowed to use this command.",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)
        return

    if not auto_react_users:
        embed = discord.Embed(
            title="ℹ️ Auto-Reaction List",
            description="No users are currently set for auto-reaction.",
            color=discord.Color.blue()
        )
    else:
        description = ""
        for user_id, emoji in auto_react_users.items():
            user = message.guild.get_member(user_id)
            if user:
                description += f"{user.mention} — {emoji}\n"
            else:
                description += f"<@{user_id}> — {emoji}\n"

        embed = discord.Embed(
            title="📋 Auto-Reaction List",
            description=description,
            color=discord.Color.green()
        )

    await message.channel.send(embed=embed)