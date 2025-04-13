import discord
import re

def parse_embed_args(content):
    data = {}
    matches = re.findall(r"{(.*?)}", content)
    for match in matches:
        if ':' in match:
            key, value = match.split(':', 1)
            data[key.strip().lower()] = value.strip()
    return data

async def handle_embed_command(message, bot):
    if not message.content.startswith("!embed"):
        return

    args = message.content[6:].strip()
    mentioned_channels = message.channel_mentions
    data = parse_embed_args(args)

    embed = discord.Embed(
        title=data.get("title"),
        description=data.get("description"),
        color=int(data.get("color", "0x2F3136").replace("#", "0x"), 16)
    )

    if "footer" in data:
        embed.set_footer(text=data["footer"])
    if "image" in data:
        embed.set_image(url=data["image"])
    if "thumbnail" in data:
        embed.set_thumbnail(url=data["thumbnail"])
    if "author" in data:
        embed.set_author(name=data["author"])
    if "timestamp" in data:
        embed.timestamp = discord.utils.utcnow()

    if mentioned_channels:
        for channel in mentioned_channels:
            await channel.send(embed=embed)
    else:
        await message.channel.send(embed=embed)