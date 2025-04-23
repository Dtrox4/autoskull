import discord
import random
import time

# Define a list of short diss responses
disses = [
    "Shut up.", "F*** you.", "No one asked.", "Get lost.", "Try harder.", "You wish.",
    "What a joke.", "So dumb.", "Who cares?", "Loser.", "Lame.", "Shut your mouth.",
    "Try again.", "Nice try.", "You're a mess.", "Big mood... not.", "Bye, Felicia.",
    "You're embarrassing.", "Get a clue.", "Weak.", "Boring.", "Take a seat."
]

# Define more common trigger words
trigger_words = ["stupid", "dumb", "idiot", "loser", "suck", "lame", "fool", "trash", "weak", 
                 "ugh", "annoying", "boring", "faggot", "rape", "r@pe", "dttm", "kys", "bitch", 
                 "sybau", "pooron", "slit", "cut", "hoe", "shut", "nigger", "ihy", "stfu"]

# Excluded users (IDs)
excluded_users = [1212229549459374222, 1269821629614264362, 845578292778238002, 
                  1177672910102614127, 1305007578857869403, 1147059630846005318]

# Cooldown dictionary and cooldown time
user_cooldowns = {}
COOLDOWN_SECONDS = 10  # cooldown time per user

# Function to handle the diss responses
async def handle_diss_response(message):
    # Ignore messages from bots or excluded users
    if message.author.bot or message.author.id in excluded_users:
        return

    content = message.content.lower()
    user_id = message.author.id
    now = time.time()

    # Check if the message contains any trigger words
    if any(word in content for word in trigger_words):
        last_used = user_cooldowns.get(user_id, 0)
        
        # Only respond if cooldown has passed
        if now - last_used >= COOLDOWN_SECONDS:
            response = random.choice(disses)  # Choose a random diss response
            await message.reply(response)
            
            # Update the user's cooldown
            user_cooldowns[user_id] = now