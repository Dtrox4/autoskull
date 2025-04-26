import asyncio
import discord

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