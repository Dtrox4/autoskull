import discord
import random
import re


# List of roast responses based on trigger words
roast_responses = {
    "hi": ["Dryest hi ever. Congrats.", "Say hi again, I dare you. With some spice.", "hi? That’s it?"],
    "hello": ["Hello? That's all you got?", "Who still says hello unironically?", "Hello? What is this, 2015?"],
    "hey": ["Hey? Try harder next time.", "Hey? Sounding desperate.", "Hey? Dry as your DMs."],
    "heyy": ["Two y’s and still no personality.", "heyy? You practicing or something?", "heyy? You lonely or what?"],
    "heyyy": ["heyyy? calm down, it's not that serious.", "heyyy? You fishing for attention?", "heyyy? Your thirst is showing."],
    "yo": ["Yo? Bro, it's not 2006 anymore.", "Yo? You’re one bad freestyle away from disaster.", "Yo? Be serious."],
    "hru": [" More like how irrelevant are you.", "hru? That's how you check on people now?", "hru? Don't act like you care."],
    "how are you": ["How am I? Better than your existence.", "how are you? Nosy much?", "I'm thriving while you’re still trying."],
    "what's up": ["Nothing you need to worry about.", "What's up? Not you, obviously.", "What's up? Your standards, hopefully."],
    "sup": [" Your vocabulary limited or what?", "Sup? Bro, update your phrases.", "Sup? Dry convos only, I see."],
    "gm": [" Dry. Try again with some energy.", "Gm? Hope your day’s better than that text.", "Waking up just to be lame, huh?"],
    "gn": ["Sleep tight, don't trip over your own irrelevance.", "Finally giving everyone peace.", " Night night, lightweight."],
    "good morning": [" Bro, I just woke up, leave me alone.", "Good morning? Who raised you?", "Good morning? Try texting with some personality."],
    "good night": ["Go dream about being interesting.", "Good night? You're dismissed.", "Finally, silence."],
    "wyd": ["Plotting your next flop?", "Why do you care?", "Avoiding you."],
    "idk": ["ydk? Of course you don’t.", "That's your whole brand.", "Expected from you."],
    "lol": ["Trying too hard to laugh at your own jokes?", "Calm down, clown.", "Lol? Not even funny, bro."],
    "wsp": ["Not enough to deal with you.", "More than you can handle, clearly.", "Wsp? Definitely not you."],
    "hru": ["Better than you, thanks for asking.", "Alive and unlike your social skills.", "Flourishing while you’re flopping."],
    "babe": ["Don't ‘babe’ me, I’m not your emotional support NPC.", "Wrong tab, sweetheart.", "Save that for someone desperate."],
    "bae": ["Don’t ‘bae’ me, I’m not your therapist.", "Find someone who cares.", "Yeah, no."],
    "lol": ["Laughing like your life isn’t in shambles.", "LOL? Bro you're coping.", "Imagine laughing while failing."],
    "lmao": ["LMAO at your existence.", "Lmao? You mean cry for help?", "LMAO. Nothing funny about you though."],
    "hehe": ["Hehe? Grow up.", "Hehe? What are you, 12?", "Hehe? That's your whole personality huh."],
    "smh": ["Keep shaking that head, maybe a thought will fall in.", "SMH. You're a full-time disappointment.", "SMH? Your head empty anyway."],
    "smd": ["You wish you had the charisma to get that offer.", "SMD? Bro, touch grass.", "Desperate much?"],
    "suck my dick": ["You wish you had the charisma to get that offer.", "You couldn't pay me enough.", "No thanks, I have standards."],
    "ihy": ["Takes one to know one.", "Cool story bro, tell it again.", "Still living rent-free in your head."],
    "i hate you": ["Takes one to know one.", "Why do I care tho?", "Cry harder."],
    "you suck": ["You must be projecting again.", "Says the expert.", "You’re a case study in failure."],
    "trash": ["You must be projecting again.", "And yet I'm still better.", "Recycling centers reject you too huh?"],
    "wow": ["Try using words with more than one syllable.", "Wow. Revolutionary vocabulary.", "That's the best you got?"],
    "damn": ["Try using words with more than one syllable.", "Damn... tragic.", "Damn, even your reactions are mid."],
    "nah": ["Whole attitude of a rejected SoundCloud rapper.", "Nah? Brain empty reply.", "Nah but you're still typing huh."],
    "bruh": ["Is that your whole vocabulary?", "Bruh moment? You're the moment.", "Bruh, touch grass."],
    "chill": ["You bring the energy of a broken air conditioner.", "Chill? You bring freezer vibes.", "Chill? You’re frostbite to talk to."],
    "yo": ["No.", "Bye.", "Grow up."],
    "gtfo": ["Temper tantrum detected.", "GTFO? You first.", "GTFO? Make me."],
    "stfu": ["Temper tantrum detected.", "STFU? Bro you started it.", "STFU? Rent free behavior."],
    "idiot": ["And you’re the president of this club, huh?", "Mirror must be wildin'.", "Takes one to know one."],
    "bitch": ["Spoken like someone who lost an Xbox argument.", "You bark louder than your brain works.", "Gotta bark when you can't debate huh?"],
    "shit": ["You're just seasoning your nonsense at this point.", "Still smelling it from here.", "You're the prime exporter of it."],
    "lame": ["And yet here you are.", "Look who's talking.", "Lame? Bro you're a museum exhibit."],
    "clown": ["And you’re the whole circus.", "You even got your own tent.", "Ringmaster of L’s."],
    "unworthy": ["And you’re the whole circus.", "Facts but only for yourself.", "Unworthy? You invented that."],
    "worthy": ["For once, you're correct: I'm him.", "Worthy? Always was.", "Born worthy, unlike you."],
    "asshole": ["Spoken like someone who lost an Xbox argument.", "Your insults are on life support.", "Desperation is loud huh?"],
    "fool": ["You run on 2 brain cells and both are lagging.", "Look who's talking, Jester.", "Whole court fool energy."],
    "bastard": ["At least I’m not out here using 2005 insults.", "Vintage insult energy.", "Still better than being you."],
    "piss": ["Angry AND unoriginal. Wow.", "Is that your final word?", "Actual toilet water vibes."],
    "douche": ["Look who’s talking, Drakkar Noir.", "Douche? Describe yourself harder.", "Projection’s crazy."],
    "vibe": ["Your aura screams expired Capri Sun.", "You got Blockbuster rental vibes.", "Vibe? Wrong frequency fam."],
    "savage": ["More like mildly annoying with wifi.", "Savage? Mid-level at best.", "Savage? Keyboard warrior vibes."],
    "w": ["You have neither the W nor the rizz. Sit down.", "That’s a lowercase W at best.", "W? More like an upside down M."],
    "ratio": ["You’re the reason that button exists.", "Ratioed by existence.", "You ratio yourself every morning."],
    "rizz": ["Bro you have negative rizz, respectfully.", "Rizz? You misspelled risk.", "You got the rizz of a wet napkin."],
    "why": ["Question everything, especially your choices.", "Why? Because you're built like that.", "Why? That's above your paygrade."],
    "okay": ["Not even your replies try anymore.", "Okay? L vocabulary.", "Bro thinks he's deep."],
    "ok": ["Not even your replies try anymore.", "OK? Minimal effort energy.", "OK bozo."],
    "really": ["Really? That’s all you got?", "Really? Try again.", "Really? Brain buffering huh."],
    "lost": ["You stay L’ing in HD.", "Lost? Story of your life.", "Lost? That's your default state."],
    "lose": ["You stay L’ing in HD.", "You lose more than an empty wallet.", "Professional L collector."],
    "never": ["That's what you said about failing, right?", "Never? Famous last words.", "Never? Already happening."],
    "bet": ["Don’t bet with that broke confidence.", "Bet? You're already bankrupt in credibility.", "Bet. And you'll still lose."],
    "cringe": ["Your personality is a walking TikTok comment.", "Cringe? That's your autobiography.", "You're the CEO of cringe."],
    "skull": ["Dead emoji, fitting for that dry joke.", "Skull? Brain dead too huh.", "Skull fits your jokes perfectly."],
    "based": ["If ignorance was a foundation, you’d be the Empire State Building.", "Based? Based on what, failure?", "You're based like expired milk."],
    "mid": ["Bold of you to call anything mid with that taste.", "Mid recognizing mid. Respect.", "Your opinions are the blueprint for mid."],
    "loser": ["Say it in the mirror next time.", "Loser? Self aware king.", "Loser? Your greatest achievement."],
    "dick": ["Keep dreaming, buddy.", "You wish, playa.", "Still a fantasy for you huh."],
    "srs": ["Seriously unserious, that’s you.", "Srs? Can't take you seriously.", "Srs? More like 'serious L'."],
    "seriously": ["Seriously unserious, that’s you.", "Seriously? Doubt.", "Seriously built like a bad idea."],
    "man": ["Still stuck in caveman chat mode huh?", "Man? More like Neanderthal.", "Bro grunted 'man' like it's deep."],
    "dude": ["Still stuck in caveman chat mode huh?", "Dude? Very intellectual.", "Dude? Peak vocabulary moment."],
    "wth": ["Exactly the energy you give.", "WTH? Bro it's you.", "WTH every time you speak."],
    "wtf": ["It’s the confusion for me.", "WTF? Story of your life.", "Still confused huh."],
    "deadass": ["Deadass? More like dead inside.", "Deadass? Your whole mood.", "Deadass mid."],
    "yes": ["Cool. No one asked tho.", "Yes? Still irrelevant.", "Yes, but at what cost?"],
    "no": ["Even rejection sounds boring from you.", "No? Coping hard.", "No but you’re still losing."],
    "hell no": ["Hell ain't even claiming that one.", "Hell said keep it.", "Hell no and heaven neither."],
    "no cap": ["That’s cap. Heavy cap.", "Cap detected.", "Certified cap artist right here."],
    "no shit": ["Groundbreaking discovery.", "Sherlock who?", "No shit, Einstein."],
    "pmo": ["Post about it. Maybe someone will care.", "PMO? Nobody asked.", "PMO and no one noticed.", "Still no one cares.", "TS PMO? Still irrelevant.", "Cry harder king."],
    "stop": ["You first.", "Stop breathing that hard.", "Stop embarrassing yourself."],
    "lowk": ["Lowk? You mean low IQ.", "Lowk built like low vibes.", "Lowk mid, high key."],
    "nigga": ["You're black bitch.", "I don't associate with niggas.", "Why is a nigga talking to me. sybau."],
    "sybau": ["make me.", "Pipe down low role", "ban?"],
    "sorry": ["Sorry doesn’t fix the IQ deficit.","Awww, look who suddenly grew a conscience.","That’s cute. Still not forgiven."],
    "my fault": ["Finally, a moment of self-awareness.","We been knew.","You admitting it doesn't make it less embarrassing."],
    "i won't do it again": ["You said that the last 3 times, chief.","we'll see about that…","Promises from you mean less than Monopoly money."],
    "please": ["Beg harder.","Say it with more tears.","Even your 'please' is weak."]
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

        # Use regex to split content into words, ignoring punctuation
        words = re.findall(r'\b\w+\b', content)

        for word in trigger_words:
            if word.lower() in words:  # Check if exact word is present
                response = random.choice(roast_responses[word])
                await message.reply(f"{response}")
                break  # Stop checking once we find a match
