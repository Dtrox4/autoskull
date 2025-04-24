import discord
import random

# List of roast responses based on trigger words
roast_responses = {
    "bro": ["Bro? You sound like you're 12.", "Bro? Who says that anymore?", "Bro, get a new word."],
    "dude": ["Dude? Is that still your thing?", "Dude, that's so 2010.", "Dude, you're not even cool."],
    "man": ["Man, are you trying to be funny?", "Man? Really?", "Man, you need some new material."],
    "what": ["What? Can't even finish a sentence?", "What? You lost your train of thought?", "What’s up with that?"],
    "why": ["Why? I don’t even know why you’re asking.", "Why? Please, stop.", "Why are you still talking?"],
    "lol": ["Lol? You think that’s funny?", "Lol? Was that supposed to be a joke?", "Lol? You're trying too hard."],
    "smh": ["SMH? You should be embarrassed.", "SMH? At least I’m not speechless like you.", "SMH? Good one, genius."],
    "okay": ["Okay? That's the best you can come up with?", "Okay? More like 'I'm out of ideas.'", "Okay? Try harder."],
    "really": ["Really? You’re still on about this?", "Really? You should reconsider your life choices.", "Really? That was your big idea?"],
    "seriously": ["Seriously? That’s what you’re going with?", "Seriously? How original.", "Seriously? You really said that?"],
    "shut up": ["Shut up? How about you try some original words?", "Shut up? More like just stop talking.", "Shut up? I’m tired of hearing it."],
    "shutup": ["Shut up? How about you try some original words?", "Shut up? More like just stop talking.", "Shut up? I’m tired of hearing it."],
    "lmao": ["Lmao? Yeah, right. Try again.", "Lmao? You’re laughing at your own joke?", "Lmao? Nice try, though."],
    "wow": ["Wow? That’s all you’ve got?", "Wow? You should be proud of yourself.", "Wow, I'm so impressed. Not."],
    "nah": ["Nah? I didn’t ask.", "Nah? Yeah, sure, whatever.", "Nah? Okay, keep telling yourself that."],
    "please": ["Please? Please, stop talking.", "Please? I beg you to be quiet.", "Please, do us both a favor and stop."],
    "help": ["Help? You’re the one who needs help.", "Help? You should try figuring it out yourself.", "Help? You really just asked for help with that?"],
    "yo": ["Yo? Is that your go-to?", "Yo? That’s so early 2000s.", "Yo? Are we back in high school?"],
    "chill": ["Chill? Nah, you need to do more than chill.", "Chill? Please, you're a walking disaster.", "Chill? More like learn to stop talking."],
    "bruh": ["Bruh? Really? That’s your response?", "Bruh? What are you, 16?", "Bruh? Try harder next time."],
    "yikes": ["Yikes? That’s all you got?", "Yikes? Oh, I'm shaking.", "Yikes? What a disaster."],
    "gtfo": ["GTFO? More like you should leave.", "GTFO? Who are you kidding?", "GTFO? You really said that?"],
    "srsly": ["Srsly? Is that how you talk?", "Srsly? That’s your response?", "Srsly? You should rethink your choices."],
    "for real": ["For real? You just said that?", "For real? Please, stop.", "For real? How original."],
    "nah fam": ["Nah fam? You’ve lost me.", "Nah fam? Keep telling yourself that.", "Nah fam? That was weak."],
    "facts": ["Facts? Are you serious?", "Facts? You sure about that?", "Facts? You should rethink your whole statement."],
    "damn": ["Damn? You really said that?", "Damn? That's the best you’ve got?", "Damn? Keep it together, man."],
    "idiot": ["Idiot? That’s rich coming from you.", "Idiot? Really?", "Idiot? You must be joking."],
    "bitch": ["Bitch? Are you serious?", "Bitch? Who taught you that?", "Bitch? Nice vocabulary, genius."],
    "asshole": ["Asshole? Nice words, pal.", "Asshole? Look who's talking.", "Asshole? Please, stop."],
    "fool": ["Fool? That’s a stretch.", "Fool? How original.", "Fool? You’ve got some nerve."],
    "stupid": ["Stupid? I think you need a dictionary.", "Stupid? No wonder you think that.", "Stupid? Look in the mirror."],
    "bastard": ["Bastard? Look who’s getting spicy.", "Bastard? Please, you’re embarrassing yourself.", "Bastard? That’s not even clever."],
    "dumb": ["Dumb? That’s rich coming from you.", "Dumb? Look who’s talking.", "Dumb? Nice try, Einstein."],
    "trash": ["Trash? You’re the one throwing it around.", "Trash? Really? That’s your best shot?", "Trash? How cute."],
    "fuck": ["Fuck? Is that really necessary?", "Fuck? Wow, how original.", "Fuck? You really need to work on your vocabulary."],
    "shit": ["Shit? You’re just mad now.", "Shit? That’s so 2007.", "Shit? You’ve got to be kidding."],
    "piss": ["Piss? Keep it together, bro.", "Piss? Take a chill pill.", "Piss? Don’t go overboard."],
    "douche": ["Douche? Is that your comeback?", "Douche? Keep your insults clean, alright?", "Douche? Very original."],
    "clown": ["Clown? Is that what you call yourself?", "Clown? You’ve got jokes.", "Clown? Stop clowning around."],
    "lame": ["Lame? You should be ashamed.", "Lame? What a clever response.", "Lame? Yeah, that’s a classic one."],
    "whore": ["Whore? You’re really reaching.", "Whore? What a disgraceful term.", "Whore? Look who’s mad."],
    "dick": ["Dick? Nice words, genius.", "Dick? You sound like a broken record.", "Dick? Please, stop."],
    "wimp": ["Wimp? I didn’t know you cared.", "Wimp? That’s your insult?", "Wimp? Cute comeback."],
    "loser": ["Loser? I guess you don’t know what that means.", "Loser? Look who’s salty.", "Loser? Keep talking."],
}

# Trigger words to look for in messages
trigger_words = list(roast_responses.keys())

# Excluded users list (If you want to exclude specific users)
excluded_users = [1212229549459374222, 1269821629614264362]  # Add user IDs to exclude

async def handle_diss(message):
    # Don't let the bot respond to its own messages or excluded users
    if message.author.bot or message.author.id in excluded_users:
        return

    # Check if the bot is mentioned
    if message.mentions and message.mentions[0] == message.guild.me:
        content = message.content.lower()
        
        # Check if the message contains any of the roast trigger words
        for word in trigger_words:
            if word in content:
                response = random.choice(roast_responses[word])
                await message.reply(f"{response}")
                break  # Stop checking once we find a match
