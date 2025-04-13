# utils/moderation_handler.py
import discord
from discord.ext import commands

async def ban_user(ctx_author, bot_member, guild, member, reason, channel):
    if member == ctx_author:
        return await channel.send("You cannot ban yourself!")

    if member == guild.owner:
        return await channel.send("You cannot ban the server owner!")

    if member.top_role >= ctx_author.top_role and ctx_author != guild.owner:
        return await channel.send("You cannot ban a member with a higher or equal role.")

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
        await channel.send("I do not have permission to ban this member.")

async def mute_user(ctx_author, bot_member, guild, member, reason, channel):
    mute_role = discord.utils.get(guild.roles, name="Muted")

    if not mute_role:
        mute_role = await guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))

    if mute_role >= bot_member.top_role:
        return await channel.send("I cannot assign the mute role, it's higher or equal to my highest role.")

    if mute_role >= ctx_author.top_role and ctx_author != guild.owner:
        return await channel.send("You cannot mute a member with a higher or equal role.")

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