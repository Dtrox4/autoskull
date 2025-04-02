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
AUTHORIZED_USERS = {YOUR_USER_ID, 845578292778238002, 1177672910102614127}

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
    # Set the presence status
    await bot.change_presence(activity=discord.Game(name="if you're worthy,  you shall be skulled"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if it's a DM
    if isinstance(message.channel, discord.DMChannel):
        print(f"DM from {message.author}: {message.content}")

    # Skull reactions for authorized users
    if message.author.id in bot.user_skull_list:
        await message.add_reaction("☠️")  # Skull and crossbones reaction

    # Check if message is a command
    if message.content.startswith("!skull"):
        if message.author.id not in AUTHORIZED_USERS:
            await message.channel.send("You do not have permission to use this command.")
            return

        args = message.content.split()

        # Command to show the list of authorized users
        if len(args) == 2 and args[1] == "authorized":
            if AUTHORIZED_USERS:
                authorized_users = [f'<@{user_id}>' for user_id in AUTHORIZED_USERS]
                await message.channel.send(f"Authorized users: {', '.join(authorized_users)}")
            else:
                await message.channel.send("No users are authorized.")
            return

        # Command to show the list of users being skulled
        if len(args) == 2 and args[1] == "list":
            if bot.user_skull_list:
                skull_users = [f'<@{user_id}>' for user_id in bot.user_skull_list]
                await message.channel.send(f"Users being skulled: {', '.join(skull_users)}")
            else:
                await message.channel.send("No users are currently being skulled.")
            return

        
        # Command to show the list of available commands in an embed format
        if len(args) == 2 and args[1] == "help":
            embed = discord.Embed(
                title="Worthy Commands",
                description="Here are the available commands:",
                color=discord.Color.blue()
            )
            embed.add_field(name="!skull @user", value="Skull a user.", inline=False)
            embed.add_field(name="!skull stop @user", value="Stop skulling a user.", inline=False)
            embed.add_field(name="!skull list", value="Show users being skulled.", inline=False)
            embed.add_field(name="!skull authorized", value="Show authorized users.", inline=False)
            embed.add_field(name="!skull authorize @user", value="Authorize a user to use commands.", inline=False)
            embed.add_field(name="!skull help", value="Show this help message.", inline=False)
            embed.set_footer(text="autoskull bot - made by @xv9c")
            
            await message.channel.send(embed=embed)
            return

        # Command to add a user to authorized list
        if len(args) == 3 and args[1].lower() == "authorize":
            if len(message.mentions) == 1:
                user = message.mentions[0]
                if user.id not in AUTHORIZED_USERS:
                    AUTHORIZED_USERS.add(user.id)
                    await message.channel.send(f"{user.mention} has been authorized to use the commands.")
                else:
                    await message.channel.send(f"{user.mention} is already authorized.")
            else:
                await message.channel.send("Please mention a valid user to authorize.")

        # Command to stop skulling a user
        if len(args) == 3 and args[1].lower() == "stop":
            if len(message.mentions) == 1:
                user = message.mentions[0]
                if user.id in bot.user_skull_list:
                    bot.user_skull_list.remove(user.id)
                    await message.channel.send(f"{user.mention} will no longer be skulled.")
                else:
                    await message.channel.send(f"{user.mention} is not currently being skulled.")
            else:
                await message.channel.send("Please mention a valid user to stop skulling.")

        # Command to skull a user (add to list of users to skull)
        elif len(args) == 2:
            mentioned_users = message.mentions
            if mentioned_users:
                for user in mentioned_users:
                    bot.user_skull_list.add(user.id)
                await message.channel.send(
                    f"Will skull {', '.join([user.mention for user in mentioned_users])} from now on ☠️"
                )
            else:
                await message.channel.send("Please mention a user to skull!")

# Run the bot
bot.run(TOKEN)