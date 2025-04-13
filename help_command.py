import discord

# Command help database
command_help = {
    "embed": {
        "syntax": "!embed <channel> {embed}{title:...}{description:...}{footer:...}{image:...}{color:#hex}{timestamp:true}",
        "description": "Creates and sends a custom embed message to the specified channel. You can include fields like title, description, footer, color, and more."
    },
    "authorize": {
        "syntax": "!authorize <@user>",
        "description": "Grants a user authorization to use specific bot features or commands."
    },
    "unauthorize": {
        "syntax": "!unauthorize <@user>",
        "description": "Revokes a user's authorization to use certain bot features or commands."
    },
    "skull": {
        "syntax": "!skull <@user>",
        "description": "Sends a skull message targeting the mentioned user. Can be used for fun or admin purposes depending on subcommands."
    },
    "say": {
        "syntax": "!say <message>",
        "description": "Bot repeats your message in the current channel."
    },
    "stats": {
        "syntax": "!stats",
        "description": "Shows the uptime and stats of the bot."
    },
    "stop": {
        "syntax": "!stop",
        "description": "Stops a running task or operation initiated by the bot. Restricted to authorized users."
    },
    "userinfo": {
        "syntax": "!userinfo <@user>",
        "description": "Displays detailed information about the mentioned user, such as roles, join date, etc."
    },
    "roleinfo": {
        "syntax": "!roleinfo <@role>",
        "description": "Displays detailed information about a specific role."
    },
    "eightball": {
        "syntax": "!eightball <question>",
        "description": "Ask the magic 8-ball a question and receive a random response."
    },
    "poll": {
        "syntax": "!poll <question>",
        "description": "Creates a poll in the current channel with the provided question. Users can vote on the options."
    },
    "bc": {
        "syntax": "!bc <message>",
        "description": "Broadcasts the provided message to all servers the bot is in (requires admin permissions)."
    },
    "maintenance": {
        "syntax": "!maintenance <on/off>",
        "description": "Toggles the bot's maintenance mode. When on, only the owner can use the bot."
    },
    "authorized": {
        "syntax": "!authorized",
        "description": "Displays a list of all users who are authorized to use specific bot features or commands."
    },
    "list": {
        "syntax": "!list",
        "description": "Shows a list of available commands in the bot."
    },
    "cancelmaintenance": {
        "syntax": "!cancelmaintenance",
        "description": "Cancels maintenance mode, allowing all users to use the bot again."
    },
    "restart": {
        "syntax": "!restart",
        "description": "Restarts the bot. Only available to the owner or authorized users."
    },
    "role": {
        "syntax": "!role @user <role name>",
        "description": "Toggles the specified role on the mentioned user. Adds or removes it based on current state."
    },
    "rolecreate": {
        "syntax": "!rolecreate <name> [#hexcolor]",
        "description": "Creates a new role with the given name and optional color."
    },
    "roledelete": {
        "syntax": "!roledelete @role",
        "description": "Deletes the mentioned role from the server."
    },
    "rolerename": {
        "syntax": "!rolerename @role <new name>",
        "description": "Renames the mentioned role to a new name."
    },
    "roleicon": {
        "syntax": "!roleicon @role <attach image>",
        "description": "Sets the icon of the mentioned role using an attached image."
    },
    "ban": {
        "syntax": "!ban @user [reason]",
        "description": "Bans the mentioned user with an optional reason. Requires ban permissions."
    },
    "kick": {
        "syntax": "!kick @user [reason]",
        "description": "Kicks the mentioned user with an optional reason. Requires kick permissions."
    },
    "mute": {
        "syntax": "!mute @user [reason]",
        "description": "Mutes the mentioned user by assigning a mute role. Requires manage roles permissions."
    }
}

async def handle_help_command(message):
    content = message.content.strip()
    args = content.split()

    if len(args) == 1:
        # General help
        embed = discord.Embed(
            title="Help Menu",
            description="Type `!help <command>` for more details on a specific command.",
            color=discord.Color.blue()
        )
        for cmd in command_help:
            embed.add_field(
                name=cmd,
                value=command_help[cmd]['description'],
                inline=False
            )
        await message.reply(embed=embed)
    else:
        # Detailed help
        cmd_name = args[1].lower()
        cmd = command_help.get(cmd_name)
        if cmd:
            embed = discord.Embed(
                title=f"Command: {cmd_name}",
                description=cmd['description'],
                color=discord.Color.green()
            )
            embed.add_field(
                name="Usage",
                value=f"```{cmd['syntax']}```",
                inline=False
            )
            await message.reply(embed=embed)
        else:
            await message.reply(f"No help found for `{cmd_name}`.")
