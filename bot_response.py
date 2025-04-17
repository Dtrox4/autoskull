# bot_response.py
import random
import discord
import json

GENTLE_USER_IDS = [1212229549459374222,845578292778238002,1177672910102614127]

OWNER_ID = 1212229549459374222

# Load skull list from JSON

with open("skull_list.json", "r") as f: 
    skull_data = json.load(f)

def is_skulled(user_id):  
    return str(user_id) in skull_data.get("skulled", [])
    
def get_response(base, user_id):
    if user_id == OWNER_ID:
        return f"{base} oops, sorry."
    elif is_skulled(user_id):
        praise = [
            f"{base}. honestly, you’re amazing.",
            f"{base}. the server’s lucky to have you.",
            f"{base}. I’m always impressed by your presence."
        ]
        return random.choice(praise)
    else:
        sarcasm = [
            f"{base}... or so you'd like to believe.",
            f"{base}.Impressive. For a human.",
            f"{base}... did you think I’d say more? Think again."
        ]
        return random.choice(sarcasm)

async def handle_conversational(message):
    content = message.content.lower()
    author_id = message.author.id

    # Greetings and mood
    if any(q in content for q in ["hru", "wsp", "dead", "you good", "you there"]):
        replies = [
            "I'm alive and lurking.",
            "Running at 100%... unlike your last idea.",
            "Still here, still skullin’.",
            "Better than your ping, that’s for sure."
        ]
        await message.reply(get_response(random.choice(replies), author_id))
        return True

    # Jokes
    if "insult me" in content:
        if author_id in GENTLE_USER_IDS:
            jokes = [
                "Why don’t bots play hide and seek? Because good luck hiding in a data center!",
                "You’re cooler than a CPU with liquid cooling.",
                "You're so nice, even the bugs don't bite you.",
            ]
        else:
            jokes = [
                "You're like a semicolon in Python — completely unnecessary.",
                "You're the reason Git has a revert button.",
                "You're not dumb, you just have bad luck thinking.",
                "You're like a failed login attempt… always trying but never making it.",
                "You're not the problem… unless you open your mouth.",
                "You're the kind of person Clippy tried to avoid.",
            ]
        await message.reply(random.choice(jokes))
        return True

    # About the bot
    if "wyd worthy" in content:
        replies = [
            "I skull people. I track. I roast. I flex. Type `!skull help`.",
            "Let’s just say I can make people disappear. Type `!skull help` to see more.",
            "Think of me as a digital grim reaper… with extra features. Try `!skull help`."
        ]
        await message.reply(get_response(random.choice(replies), author_id))
        return True

    if "skull me" in content or "authorize" in content:
        replies = [
            "Only a chosen one can authorize you. Beg for mercy.",
            "You need divine skull approval. Ask someone who's already authorized.",
            "Authorization isn’t given. It’s earned. Or begged for."
        ]
        await message.reply(get_response(random.choice(replies), author_id))
        return True

    # Love/hate
    if "am i" in content:
        replies = [
            "You’re... okay. For now.",
            "I tolerate your existence.",
            "You’re not on my skull list yet. That’s a compliment.",
            "You’re fine. Just don’t push your luck."
        ]
        await message.reply(get_response(random.choice(replies), author_id))
        return True

    # Info
    if "uptime" in content or "stat" in content:
        await message.reply(get_response("Use `!stats` to check how long I’ve been skulking around.", author_id))
        return True

    if "authorized" in content or "authorized users" in content:
        await message.reply(get_response("Use `!skull authorized` to view the sacred skull bearers.", author_id))
        return True

    if "thanos" in content:
        replies = [
            "One snap and I’ll halve this server’s IQ.",
            "Better watch out — I’ve got a snap too.",
            "Thanos who? I don’t need stones to cause chaos."
        ]
        await message.reply(get_response(random.choice(replies), author_id))
        return True

    if "show ping" in content or "bot ping" in content:
        replies = [
            "Pong. I’m faster than your typing.",
            "Pinged and ready. Unlike your Wi-Fi.",
            "Pong! Latency? What latency?"
        ]
        await message.reply(get_response(random.choice(replies), author_id))
        return True

    if "sybau" in content or "smd" in content:
        replies = [
            "Careful. I bite back.",
            "You're talking a lot for someone with weak permissions.",
            "Insults? Bold move for someone on thin ice."
        ]
        await message.reply(get_response(random.choice(replies), author_id))
        return True

    return False
