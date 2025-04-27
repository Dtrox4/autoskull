# ANTI-NUKE COMMANDS. DO NOT CHANGE POSIION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Load the settings when the bot starts
def load_antinuke_settings():
    global antinuke_settings
    try:
        with open('antinuke_settings.json', 'r') as file:
            antinuke_settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        antinuke_settings = {}

# Call this function when the bot starts
load_antinuke_settings()

# Dictionary to store anti-nuke settings per guild
antinuke_settings = {}

# Anti-Nuke Setup Command
@bot.command()
async def antinuke(ctx, action: str):
    """Setup or disable anti-nuke protections (only accessible by bot owner)."""
    if ctx.author.id == YOUR_USER_ID:  # Only allow the bot owner to run this command
        guild_id = str(ctx.guild.id)

        if action.lower() == "setup":
            # Set up anti-nuke protection for the server
            if guild_id in antinuke_settings:
                await ctx.send("Anti-nuke system is already set up for this server.")
                return

            # Set all anti-nuke protections to True (can be customized)
            antinuke_settings[guild_id] = {
                "ban_protection": True,
                "kick_protection": True,
                "channel_create_protection": True,
                "channel_delete_protection": True,
                "role_create_protection": True,
                "role_delete_protection": True,
                "role_permission_protection": True,
                "webhook_protection": True,
            }

            # Send confirmation message
            # Send confirmation message
            embed = discord.Embed(
                title="Anti-Nuke Setup",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Ban protection", value="✅", inline=False)
            embed.add_field(name="Kick protection", value="✅", inline=False)
            embed.add_field(name="Channel create protection", value="✅", inline=False)
            embed.add_field(name="Channel delete protection", value="✅", inline=False)
            embed.add_field(name="Role create protection", value="✅", inline=False)
            embed.add_field(name="Role delete protection", value="✅", inline=False)
            embed.add_field(name="Role permission protection", value="✅", inline=False)
            embed.add_field(name="Webhook protection", value="✅", inline=False)
            await ctx.send(embed=embed)

            save_antinuke_settings()  # Save the settings

        elif action.lower() == "disable":
            # Disable anti-nuke protection for the server
            if guild_id not in antinuke_settings:
                await ctx.send("Anti-nuke system is not set up for this server.")
                return

            # Remove the server's anti-nuke settings
            del antinuke_settings[guild_id]
            save_antinuke_settings()  # Save the updated settings

            # Send confirmation message
            embed = discord.Embed(
                title="Anti-Nuke Disabled",
                description="The anti-nuke protections have been successfully disabled for this server.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        else:
            await ctx.send("Invalid action. Use `!antinuke setup` to set up or `!antinuke disable` to disable the system.")

    else:
        await ctx.send("You do not have permission to use this command.", delete_after=5)

# Function to save the updated settings to the file
def save_antinuke_settings():
    with open('antinuke_settings.json', 'w') as file:
        json.dump(antinuke_settings, file, indent=4)

@bot.command()
async def antinuke_settings(ctx):
    """View the current anti-nuke configuration for the server."""
    guild_id = str(ctx.guild.id)
    
    # Check if there are settings for the current guild
    if guild_id in antinuke_settings:
        settings = antinuke_settings[guild_id]
        
        # Create an embed to show the settings
        embed = discord.Embed(
            title="Anti-Nuke Settings",
            description=f"Current Anti-Nuke settings for **{ctx.guild.name}**:",
            color=discord.Color.blue()
        )
        
        # Add each protection status to the embed
        embed.add_field(name="Ban Protection", value="✅" if settings["ban_protection"] else "❌", inline=False)
        embed.add_field(name="Kick Protection", value="✅" if settings["kick_protection"] else "❌", inline=False)
        embed.add_field(name="Channel Create Protection", value="✅" if settings["channel_create_protection"] else "❌", inline=False)
        embed.add_field(name="Channel Delete Protection", value="✅" if settings["channel_delete_protection"] else "❌", inline=False)
        embed.add_field(name="Role Create Protection", value="✅" if settings["role_create_protection"] else "❌", inline=False)
        embed.add_field(name="Role Delete Protection", value="✅" if settings["role_delete_protection"] else "❌", inline=False)
        embed.add_field(name="Role Permission Protection", value="✅" if settings["role_permission_protection"] else "❌", inline=False)
        embed.add_field(name="Webhook Protection", value="✅" if settings["webhook_protection"] else "❌", inline=False)
        
        # Send the embed message
        await ctx.send(embed=embed)
    else:
        # If the server doesn't have any settings, send a message indicating no protection is set up
        await ctx.send("Anti-Nuke protection is not set up for this server. Use `!antinuke setup` to enable it.")


# Anti-Nuke Event Listeners
# Protecting against bans
@bot.event
async def on_member_ban(guild, user):
    guild_id = str(guild.id)
    if antinuke_settings.get(guild_id, {}).get("ban_protection"):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                banner = entry.user
                if not banner.guild_permissions.administrator:  # Only protect against non-admins
                    await guild.ban(banner, reason="Anti-Nuke: Unauthorized mass banning detected.")
                    await guild.unban(user, reason="Restoring banned member after anti-nuke protection.")
                    log_channel = discord.utils.get(guild.text_channels, name="antinuke-logs")
                    if log_channel:
                        embed = discord.Embed(
                            title="Nuke Detected",
                            description=f"{banner.mention} tried to ban {user.mention}. The action was reversed.",
                            color=discord.Color.red()
                        )
                        await log_channel.send(embed=embed)

# Protecting against kicks
@bot.event
async def on_member_remove(member):
    guild_id = str(member.guild.id)
    if antinuke_settings.get(guild_id, {}).get("kick_protection"):
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                kicker = entry.user
                if not kicker.guild_permissions.administrator:
                    await member.guild.ban(kicker, reason="Anti-Nuke: Unauthorized mass kick detected.")
                    log_channel = discord.utils.get(member.guild.text_channels, name="antinuke-logs")
                    if log_channel:
                        embed = discord.Embed(
                            title="Nuke Detected",
                            description=f"{kicker.mention} tried to kick {member.mention}. The action was reversed.",
                            color=discord.Color.red()
                        )
                        await log_channel.send(embed=embed)

# Protecting against channel deletions
@bot.event
async def on_guild_channel_delete(channel):
    guild_id = str(channel.guild.id)
    if antinuke_settings.get(guild_id, {}).get("channel_protection"):
        await asyncio.sleep(2)  # Wait a moment to check if this was a deletion attempt by the nuke
        new_channel = await channel.guild.create_text_channel(channel.name, category=channel.category)
        log_channel = discord.utils.get(channel.guild.text_channels, name="antinuke-logs")
        if log_channel:
            embed = discord.Embed(
                title="Nuke Detected",
                description=f"{channel.name} was deleted, but was automatically restored.",
                color=discord.Color.red()
            )
            await log_channel.send(embed=embed)

# Protecting against role deletions
@bot.event
async def on_guild_role_delete(role):
    guild_id = str(role.guild.id)
    if antinuke_settings.get(guild_id, {}).get("role_protection"):
        await asyncio.sleep(2)  # Wait a moment to check if this was a deletion attempt by the nuke
        new_role = await role.guild.create_role(name=role.name, permissions=role.permissions, color=role.color)
        log_channel = discord.utils.get(role.guild.text_channels, name="antinuke-logs")
        if log_channel:
            embed = discord.Embed(
                title="Nuke Detected",
                description=f"{role.name} was deleted, but was automatically restored.",
                color=discord.Color.red()
            )
            await log_channel.send(embed=embed)

# Protecting against webhook creations (webhook spam)
@bot.event
async def on_webhooks_update(guild, channel):
    guild_id = str(guild.id)
    if antinuke_settings.get(guild_id, {}).get("webhook_protection"):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.webhook_create):
            if entry.target.guild.id == guild.id:
                webhook_creator = entry.user
                if not webhook_creator.guild_permissions.administrator:
                    await channel.send("Webhook creation detected from unauthorized user. Action reversed.")
                    # Optionally, delete the webhook
                    webhooks = await channel.webhooks()
                    for webhook in webhooks:
                        await webhook.delete()
                    log_channel = discord.utils.get(guild.text_channels, name="antinuke-logs")
                    if log_channel:
                        embed = discord.Embed(
                            title="Nuke Detected",
                            description=f"{webhook_creator.mention} created a webhook. The action was reversed.",
                            color=discord.Color.red()
                        )
                        await log_channel.send(embed=embed)
