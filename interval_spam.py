import discord
from discord.ext import commands
import asyncio

# Your user ID for access control (replace with your actual Discord ID)
YOUR_USER_ID =   # <-- Replace this with your own user ID

# Dictionary to keep track of auto-message tasks
auto_message_tasks = {}

# Function to start auto messaging
async def start_spam_manual(channel, interval, message):
    task_name = f"{channel.guild.id}-{channel.id}"

    async def auto_send():
        try:
            while True:
                await channel.send(message)  # <-- SPAM: plain text
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass

    # Cancel old task if running
    if task_name in auto_message_tasks:
        auto_message_tasks[task_name].cancel()

    task = asyncio.create_task(auto_send())
    auto_message_tasks[task_name] = task

# Function to stop auto messaging
async def stop_spam_manual(channel):
    task_name = f"{channel.guild.id}-{channel.id}"
    if task_name in auto_message_tasks:
        auto_message_tasks[task_name].cancel()
        del auto_message_tasks[task_name]
        return True
    return False

# on_message event to listen for trigger words
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if the message author is you
    if message.author.id != YOUR_USER_ID:
        return  # Ignore messages from anyone who is not you

    content = message.content.lower()

    if content == "start spam":
        channel = message.channel
        interval = 10  # seconds
        spam_message = "I'm alive and spamming!"
        await start_spam_manual(channel, interval, spam_message)

        embed = discord.Embed(
            title="Started Spamming!",
            description=f"Spamming every {interval} seconds.",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)

    if content == "stop spam":
        channel = message.channel
        stopped = await stop_spam_manual(channel)
        if stopped:
            embed = discord.Embed(
                title="Stopped Spamming!",
                description="No longer sending auto-messages.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="No Active Spam!",
                description="There was no spam running in this channel.",
                color=discord.Color.orange()
            )
        await message.channel.send(embed=embed)

    await bot.process_commands(message)

# Optional Commands (also using embeds for replies)
@bot.command()
async def startspam(ctx, interval: int, *, spam_message: str):
    """Command version: !startspam 10 Hello World"""
    if ctx.author.id != YOUR_USER_ID:
        await ctx.send("You do not have permission to use this command.")
        return

    await start_spam_manual(ctx.channel, interval, spam_message)

    embed = discord.Embed(
        title="Started Spamming!",
        description=f"Spamming every {interval} seconds with:\n`{spam_message}`",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def stopspam(ctx):
    """Command version: !stopspam"""
    if ctx.author.id != YOUR_USER_ID:
        await ctx.send("You do not have permission to use this command.")
        return

    stopped = await stop_spam_manual(ctx.channel)
    if stopped:
        embed = discord.Embed(
            title="Stopped Spamming!",
            description="No longer sending auto-messages.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="No Active Spam!",
            description="There was no spam running in this channel.",
            color=discord.Color.orange()
        )
    await ctx.send(embed=embed)

# Bot token
bot.run("YOUR_BOT_TOKEN")