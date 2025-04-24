import discord
import random
import time

# Define a list of short diss responses
disses = [
    "Cry harder.", "Nice try, clown.", "Sit down.", "You're not that guy.", "Keep dreaming.",
    "That's cute.", "Try again, champ.", "Big words for someone so small.", "Nah.", "Yikes.",
    "Bold of you.", "Pipe down.", "You done?", "L ratio.", "Not impressed.",
    "Stay mad.", "Go outside.", "Delusional.", "That's embarrassing.", "Ain’t it sad?",
    "Sweetie, no.", "Have several seats.", "You’re reaching.", "Don’t start.", "Mid.",
    "Oop— you tried.", "You done venting?", "That's your best?", "Bless your heart.", "How brave.",
    "Groundbreaking.", "So original.", "You really said that, huh?", "Please touch grass.",
    "Put that back in drafts.", "You good?", "Yawn.", "Imagine typing that.", "You're not serious.",
    "Cool story.", "Bet.", "You okay?", "Thanks for sharing, I guess.", "Anyway...",
    "You're doing amazing... not.", "Try again when it lands.", "Such confidence. Zero delivery."
]

# Define more common trigger words
trigger_words = [
    "fuck", "shit", "bitch", "asshole", "bastard", "dick", "pussy", "cunt",
    "slut", "whore", "fag", "faggot", "damn", "crap", "bollocks", "prick", "arse",
    "motherfucker", "cock", "twat", "nigger", "nigga", "retard", "cum", "jizz",
    "rape", "kys", "stfu", "gtfo", "suck my", "eat shit", "die", "slit"
]

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