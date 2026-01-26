import discord
from discord.ext import commands
import json
import os
import asyncio
import logging

logging.getLogger("discord.gateway").setLevel(logging.ERROR)

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

DATA_FILE = "index.json"
LAST_ID_FILE = "last_id.txt"

bot = commands.Bot(command_prefix="!", self_bot=True)

def serialize_message(msg):
    return {
        "id": str(msg.id),
        "timestamp": msg.created_at.isoformat(),
        "content": msg.content,
        "embeds": [e.to_dict() for e in msg.embeds],
        "author": {
            "id": str(msg.author.id),
            "username": msg.author.name,
            "bot": msg.author.bot,
        } if msg.author else None,
        "webhook_id": str(msg.webhook_id) if msg.webhook_id else None,
    }

def load_last_id():
    if os.path.exists(LAST_ID_FILE):
        return int(open(LAST_ID_FILE).read().strip())
    return None

def save_last_id(mid):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(mid))

def load_messages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_messages(msgs):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)

@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        await bot.close()
        return

    last_id = load_last_id()
    messages = load_messages()
    new_msgs = []

    async for msg in channel.history(limit=None, after=last_id):
        new_msgs.append(serialize_message(msg))

    if new_msgs:
        new_msgs.sort(key=lambda m: int(m["id"]))
        messages.extend(new_msgs)
        save_messages(messages)
        save_last_id(new_msgs[-1]["id"])
        print(f"Added {len(new_msgs)} new messages")

    await bot.close()

bot.run(TOKEN)
