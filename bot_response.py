# bot_response.py
import random
import discord

GENTLE_USER_IDS = [845578292778238002, 1177672910102614127]

# Load skull list from JSON

with open("skull_list.json", "r") as f: 
    skull_data = json.load(f)

def is_skulled(user_id):  
    return str(user_id) in skull_data.get("skulled", [])
    

def get_response(base, user_id):
    praise_responses = [
        f"{base} — honestly, you're amazing.",
        f"{base} — and you're the best I've met.",
        f"{base} — your presence improves everything.",
    ]
    sarcasm_responses = [
        f"{base}... or so you'd like to believe.",
        f"{base} — yeah, sure, keep dreaming.",
        f"{base}? That's funny coming from you.",
    ]
    return random.choice(praise_responses if is_skulled(user_id) else sarcasm_responses)

async def handle_conversational(message):
    content = message.content.lower()
    author_id = message.author.id

    # Greetings and mood
    if any(q in content for q in ["how are you", "how’s it going", "are you alive", "you good", "you there"]):
        replies = [
            "I'm alive and lurking.",
            "Running at 100%... unlike your last idea.",
            "Still here, still skullin’.",
            "System checks green. Skull power: 99%.",
            "Better than your ping, that’s for sure."
        ]
        await message.reply(random.choice(replies))
        return True

    # About the bot
    if "what can you do" in content:
        replies = [
            "I skull people. I track. I roast. I flex. Type `!skull help`.",
            "Let’s just say I can make people disappear. Type `!skull help` to see more.",
            "Think of me as a digital grim reaper… with extra features. Try `!skull help`."
        ]
        await message.reply(random.choice(replies))
        return True

    if "who created you" in content or "who's your creator" in content:
        await message.reply("I was forged by **@xv9c** — the one who wields the skull key.")
        return True

    if "how do i get authorized" in content or "authorize me" in content:
        replies = [
            "Only a chosen one can authorize you. Beg for mercy.",
            "You need divine skull approval. Ask someone who's already authorized.",
            "Authorization isn’t given. It’s earned. Or begged for."
        ]
        await message.reply(random.choice(replies))
        return True

    # Love/hate
    if "do you like me" in content:
        replies = [
            "You’re... okay. For now.",
            "I tolerate your existence.",
            "You’re not on my skull list yet. That’s a compliment.",
            "You’re fine. Just don’t push your luck."
        ]
        await message.reply(random.choice(replies))
        return True

    # Info
    if "uptime" in content or "how long have you been on" in content:
        await message.reply("Use `!stats` to check how long I’ve been skulking around.")
        return True

    if "who is authorized" in content or "authorized users" in content:
        await message.reply("Use `!skull authorized` to view the sacred skull bearers.")
        return True

    if "help" in content and "!skull" not in content:
        await message.reply("Try `!skull help` — it has everything you need. Or everything I want you to know.")
        return True

    # Easter eggs / playful
    if "skull bomb" in content:
        replies = [
            "☠️ Skull bomb armed. Evacuate immediately.",
            "Boom incoming... skulls will rain.",
            "☠️ Deploying payload. No survivors expected."
        ]
        await message.reply(random.choice(replies))
        return True

    if "thanos" in content:
        replies = [
            "One snap and I’ll halve this server’s IQ.",
            "Better watch out — I’ve got a snap too.",
            "Thanos who? I don’t need stones to cause chaos."
        ]
        await message.reply(random.choice(replies))
        return True

    if "ping test" in content or "bot ping" in content:
        replies = [
            "Pong. I’m faster than your typing.",
            "Pinged and ready. Unlike your Wi-Fi.",
            "Pong! Latency? What latency?"
        ]
        await message.reply(random.choice(replies))
        return True

    if "you suck" in content or "trash bot" in content:
        replies = [
            "Careful. I bite back.",
            "You're talking a lot for someone with weak permissions.",
            "Insults? Bold move for someone on thin ice."
        ]
        await message.reply(random.choice(replies))
        return True

    return False