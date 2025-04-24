import discord
import random

# Friendly responses based on trigger words
friendly_responses = {
    "hi": ["Hey there!", "Hello! How's it going?", "Hi! What's up?"],
    "hello": ["Hey!", "Hello, how's your day?", "Hi there!"],
    "hey": ["Hey! What's up?", "Yo! How's it going?", "Hey there!"],
    "yo": ["Yo! What's good?", "Hey yo! How are you?", "Yo, what's up?"],
    "sup": ["Sup, dude? What's going on?", "Hey, not much. You?", "What's up with you?"],
    "good morning": ["Good morning! How are you today?", "Morning! Hope you have a great day!", "Good morning! What's new?"],
    "good evening": ["Good evening! How's your night going?", "Evening! How's everything?", "Good evening! What are you up to?"],
    "how are you": ["I'm doing great, thanks for asking! How about you?", "I'm good! How are you doing?", "I'm doing well, how are you?"],
    "what's up": ["Not much, just chilling! How about you?", "Just hanging out, what's up with you?", "Not much, what's going on with you?"],
    "how's it going": ["It's going great! How about you?", "Going well! How's your day?", "It's going good! What's up with you?"],
    "how are things": ["Things are going smoothly! How about for you?", "Things are good, thanks for asking!", "Everything's great here, how are things with you?"],
    "how's life": ["Life's good! How about yours?", "Life's going well, thanks for asking!", "Life's good! What's up with you?"],
    "wyd": ["Not much, just here chilling. What about you?", "Just here, how about you?", "Chilling, what are you up to?"],
    "thank you": ["You're welcome!", "No problem, glad I could help!", "You're welcome!"],
    "thanks": ["No problem!", "Anytime!", "You're welcome!"],
    "appreciate it": ["Glad I could help!", "You're welcome!", "I'm happy to help!"],
    "no problem": ["It's all good!", "No worries at all!", "Anytime!"],
    "np": ["No worries!", "You're welcome!", "Glad to help!"],
    "sure": ["Of course!", "Definitely!", "Sure thing!"],
    "of course": ["Always!", "Definitely!", "Sure thing!"],
    "bye": ["Goodbye, take care!", "See you later!", "Bye, have a great day!"],
    "goodbye": ["Goodbye! Stay safe!", "See you soon!", "Take care, goodbye!"],
    "see ya": ["See you later!", "Catch you later!", "Take care! See you!"],
    "good night": ["Good night! Sleep well!", "Sweet dreams! Good night!", "Good night, rest up!"],
    "take care": ["You too! Take care!", "Take care! See you soon!", "Be safe and take care!"],
    "talk later": ["Talk to you later!", "Catch you later!", "See you later!"]
}

# Trigger words to look for in messages
trigger_words = list(friendly_responses.keys())

# Excluded users list (If you want to exclude specific users)
excluded_users = [1212229549459374222, 1269821629614264362]  # Add user IDs to exclude

async def on_message(message):
    # Don't let the bot respond to its own messages or excluded users
    if message.author.bot or message.author.id in excluded_users:
        return

    # Check if the bot is mentioned
    if message.mentions and message.mentions[0] == message.guild.me:
        content = message.content.lower()
        
        # Check if the message contains any of the friendly trigger words
        for word in trigger_words:
            if word in content:
                response = random.choice(friendly_responses[word])
                await message.channel.send(response)
                break  # Stop checking once we find a match