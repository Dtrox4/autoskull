# utils/role_handler.py
import discord

async def toggle_user_role(ctx_author, bot_member, guild, member, role_name, channel):
    role = discord.utils.get(guild.roles, name=role_name)

    if not role:
        embed = discord.Embed(
            title="Role Not Found",
            description=f"Could not find a role named `{role_name}`.",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if role >= bot_member.top_role:
        embed = discord.Embed(
            title="Permission Error",
            description="I can't manage that role. It's higher or equal to my highest role.",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if role >= ctx_author.top_role and ctx_author != guild.owner:
        embed = discord.Embed(
            title="Permission Denied",
            description="You can't manage that role. It's higher or equal to your highest role.",
            color=discord.Color.red()
        )
        return await channel.send(embed=embed)

    if role in member.roles:
        await member.remove_roles(role)
        embed = discord.Embed(
            title="Role Removed",
            description=f"Removed role `{role.name}` from {member.mention}.",
            color=discord.Color.orange()
        )
    else:
        await member.add_roles(role)
        embed = discord.Embed(
            title="Role Added",
            description=f"Added role `{role.name}` to {member.mention}.",
            color=discord.Color.green()
        )

    embed.set_footer(text=f"Action by {ctx_author}", icon_url=ctx_author.avatar.url if ctx_author.avatar else None)
    await channel.send(embed=embed)