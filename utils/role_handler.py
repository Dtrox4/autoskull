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

async def create_role(guild: discord.Guild, name: str, color: discord.Color, reason: str, channel: discord.TextChannel):
    try:
        role = await guild.create_role(name=name, color=color, reason=reason)
        embed = discord.Embed(
            title="Role Created",
            description=f"Role **{role.name}** has been created.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Error Creating Role",
            description=str(e),
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

async def delete_role(guild: discord.Guild, role: discord.Role, reason: str, channel: discord.TextChannel):
    try:
        await role.delete(reason=reason)
        embed = discord.Embed(
            title="Role Deleted",
            description=f"Role **{role.name}** has been deleted.",
            color=discord.Color.orange()
        )
        await channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Error Deleting Role",
            description=str(e),
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

async def rename_role(role: discord.Role, new_name: str, reason: str, channel: discord.TextChannel):
    try:
        old_name = role.name
        await role.edit(name=new_name, reason=reason)
        embed = discord.Embed(
            title="Role Renamed",
            description=f"Role **{old_name}** has been renamed to **{new_name}**.",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Error Renaming Role",
            description=str(e),
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

async def set_role_icon(role: discord.Role, image_bytes: bytes, reason: str, channel: discord.TextChannel):
    try:
        await role.edit(display_icon=image_bytes, reason=reason)
        embed = discord.Embed(
            title="Role Icon Updated",
            description=f"Icon for role **{role.name}** has been updated.",
            color=discord.Color.teal()
        )
        await channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Error Setting Role Icon",
            description=str(e),
            color=discord.Color.red()
        )
        await channel.send(embed=embed)