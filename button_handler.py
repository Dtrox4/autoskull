import discord

# Memory to track message buttons
message_buttons = {}

# Dynamic View for buttons
class DynamicLinkView(discord.ui.View):
    def __init__(self, buttons_data):
        super().__init__()
        for label, url in buttons_data:
            self.add_item(discord.ui.Button(label=label, url=url))

# Function to add button
async def add_button(bot, channel, message_id: int, link: str, label: str = "Click Here"):
    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        return "❌ Message not found."
    except discord.Forbidden:
        return "❌ No permission to view message."
    except discord.HTTPException:
        return "❌ Failed to fetch message."

    if message.author.id != bot.user.id:
        return "❌ I can only edit my own messages."

    # Track buttons
    if message.id not in message_buttons:
        message_buttons[message.id] = []
    message_buttons[message.id].append((label, link))

    view = DynamicLinkView(message_buttons[message.id])

    try:
        await message.edit(view=view)
        return f"✅ Added button [{label}] linked to {link}!"
    except discord.HTTPException:
        return "❌ Failed to edit the message."

# Function to remove button
async def remove_button(bot, channel, message_id: int, label: str):
    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        return "❌ Message not found."
    except discord.Forbidden:
        return "❌ No permission to view message."
    except discord.HTTPException:
        return "❌ Failed to fetch message."

    if message.author.id != bot.user.id:
        return "❌ I can only edit my own messages."

    if message.id not in message_buttons:
        return "❌ No buttons found on this message."

    buttons_list = message_buttons[message.id]
    new_buttons = [btn for btn in buttons_list if btn[0].lower() != label.lower()]

    if len(new_buttons) == len(buttons_list):
        return f"❌ No button with label `{label}` found."

    message_buttons[message.id] = new_buttons

    if not new_buttons:
        await message.edit(view=None)
    else:
        view = DynamicLinkView(new_buttons)
        await message.edit(view=view)

    return f"✅ Removed button `{label}`!"
