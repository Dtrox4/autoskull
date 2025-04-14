import os
from dotenv import load_dotenv
from getpass import getpass
import discord

ENV_FILE = ".env"

# Check if .env file exists; create if not
if not os.path.isfile(ENV_FILE):
    print("🔧 No .env file found. Let's set it up!")
    bot_token = getpass("🔑 Enter your Discord bot token (input hidden): ").strip()

    with open(ENV_FILE, "w") as f:
        f.write(f"BOT_TOKEN={bot_token}")
    print("✅ .env file created successfully!")
