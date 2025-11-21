"""
Telethon Userbot with Button Menu
- Scan members
- Show online/offline/bots/deleted
- Remove deleted
- Remove bots
- Remove offline

Run:
  python userbot.py

You must fill API_ID & API_HASH below.
"""

import asyncio
from telethon import TelegramClient, events, Button
from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth

API_ID = 0  # <-- Your API ID
API_HASH = ""  # <-- Your API HASH
SESSION = "userbot_session"

client = TelegramClient(SESSION, API_ID, API_HASH)

# Detect functions

def is_deleted(u):
    return getattr(u, 'deleted', False)

def is_online(u):
    return isinstance(getattr(u, 'status', None), (UserStatusOnline, UserStatusRecently))

def is_offline(u):
    st = getattr(u, 'status', None)
    return isinstance(st, (UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth)) or st is None

async def scan(chat):
    users = await client.get_participants(chat)
    online, offline, bots, deleted = [], [], [], []
    for u in users:
        if getattr(u, 'bot', False): bots.append(u); continue
        if is_deleted(u): deleted.append(u); continue
        if is_online(u): online.append(u)
        else: offline.append(u)
    return online, offline, bots, deleted

async def remove_users(chat, users):
    for u in users:
        try:
            await client.kick_participant(chat, u)
            await asyncio.sleep(1)
        except: pass

# Start message
@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "**Userbot Control Panel**",
        buttons=[
            [Button.text("Scan Members")],
            [Button.text("Show Online"), Button.text("Show Offline")],
            [Button.text("Show Bots"), Button.text("Show Deleted")],
            [Button.text("Remove Deleted")],
            [Button.text("Remove Bots"), Button.text("Remove Offline")]
        ]
    )

# Button handler
@client.on(events.NewMessage)
async def handler(event):
    chat = event.chat_id
    txt = event.raw_text

    if txt == "Scan Members":
        o, f, b, d = await scan(chat)
        await event.respond(f"Scan Complete:\nOnline: {len(o)}\nOffline: {len(f)}\nBots: {len(b)}\nDeleted: {len(d)}")

    elif txt == "Show Online":
        o, _, _, _ = await scan(chat)
        msg = "Online Users:\n" + "\n".join([str(u.id) for u in o][:40])
        await event.respond(msg)

    elif txt == "Show Offline":
        _, f, _, _ = await scan(chat)
        msg = "Offline Users:\n" + "\n".join([str(u.id) for u in f][:40])
        await event.respond(msg)

    elif txt == "Show Bots":
        _, _, b, _ = await scan(chat)
        msg = "Bots:\n" + "\n".join([str(u.id) for u in b][:40])
        await event.respond(msg)

    elif txt == "Show Deleted":
        _, _, _, d = await scan(chat)
        msg = "Deleted Accounts:\n" + "\n".join([str(u.id) for u in d][:40])
        await event.respond(msg)

    elif txt == "Remove Deleted":
        _, _, _, d = await scan(chat)
        await event.respond(f"Removing {len(d)} deleted accounts...")
        await remove_users(chat, d)
        await event.respond("Deleted accounts removed.")

    elif txt == "Remove Bots":
        _, _, b, _ = await scan(chat)
        await event.respond(f"Removing {len(b)} bots...")
        await remove_users(chat, b)
        await event.respond("Bots removed.")

    elif txt == "Remove Offline":
        _, f, _, _ = await scan(chat)
        await event.respond(f"Removing {len(f)} offline members...")
        await remove_users(chat, f)
        await event.respond("Offline users removed.")

print("Userbot running...")
client.start()
client.run_until_disconnected()
