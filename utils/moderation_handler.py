import discord
from discord.ext import commands

async def ban_user(ctx_author, bot_member, guild, member, reason, channel):
    """Bans a member from the server and sends an embed output."""
    if member == ctx_author:
        embed = discord.Embed(
            title="Action Failed",
            description="You cannot ban yourself!",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if member == guild.owner:
        embed = discord.Embed(
            title="Action Failed",
            description="You cannot ban the server owner!",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if member.top_role >= ctx_author.top_role and ctx_author != guild.owner:
        embed = discord.Embed(
            title="Action Failed",
            description="You cannot ban a member with a higher or equal role.",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="User Banned",
            description=f"Banned {member.mention} from the server.\nReason: {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Action by {ctx_author}", icon_url=ctx_author.avatar.url if ctx_author.avatar else None)
        await channel.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="Action Failed",
            description="I do not have permission to ban this member.",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

async def kick_user(ctx_author, bot_member, guild, member, reason, channel):
    """Kicks a member from the server and sends an embed output."""
    if member == ctx_author:
        embed = discord.Embed(
            title="Action Failed",
            description="You cannot kick yourself!",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if member == guild.owner:
        embed = discord.Embed(
            title="Action Failed",
            description="You cannot kick the server owner!",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if member.top_role >= ctx_author.top_role and ctx_author != guild.owner:
        embed = discord.Embed(
            title="Action Failed",
            description="You cannot kick a member with a higher or equal role.",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="User Kicked",
            description=f"Kicked {member.mention} from the server.\nReason: {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Action by {ctx_author}", icon_url=ctx_author.avatar.url if ctx_author.avatar else None)
        await channel.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="Action Failed",
            description="I do not have permission to kick this member.",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

async def mute_user(ctx_author, bot_member, guild, member, reason, channel):
    """Mutes a member in the server and sends an embed output."""
    mute_role = discord.utils.get(guild.roles, name="Muted")

    if not mute_role:
        mute_role = await guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))

    if mute_role >= bot_member.top_role:
        embed = discord.Embed(
            title="Action Failed",
            description="I cannot assign the mute role, it's higher or equal to my highest role.",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if mute_role >= ctx_author.top_role and ctx_author != guild.owner:
        embed = discord.Embed(
            title="Action Failed",
            description="You cannot mute a member with a higher or equal role.",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        embed = discord.Embed(
            title="User Unmuted",
            description=f"Unmuted {member.mention}.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)
    else:
        await member.add_roles(mute_role, reason=reason)
        embed = discord.Embed(
            title="User Muted",
            description=f"Muted {member.mention}.\nReason: {reason}",
            color=discord.Color.orange()
        )
        await channel.send(embed=embed)