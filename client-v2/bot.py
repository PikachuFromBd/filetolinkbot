# Don't Remove Credit @pikachufrombd
# FileToLink V3 — Client Bot

import sys
import glob
import importlib
import logging
import pytz
import asyncio
from pathlib import Path
from datetime import date, datetime
from pyrogram import Client, idle, enums
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL
from texts import Text

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


# Create the Pyrogram client
app = Client(
    name="FileToLinkClient",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    plugins={"root": "plugins"},
    sleep_threshold=5,
)


async def start():
    await app.start()
    print('\n')
    print('⚡ FileToLink Client Bot Starting...')

    me = await app.get_me()
    print(f'✅ Bot started as @{me.username}')

    # Resolve the log channel peer FIRST to avoid "Peer id invalid"
    try:
        chat = await app.get_chat(LOG_CHANNEL)
        print(f'📢 Log channel resolved: {chat.title}')
    except Exception as e:
        print(f'⚠️ Could not resolve log channel: {e}')
        print('   Make sure the bot is added as admin to the log channel!')

    # Load plugins info
    ppath = "plugins/*.py"
    files = glob.glob(ppath)
    for name in files:
        plugin_name = Path(name).stem
        if plugin_name != "__init__":
            print(f"📦 Loaded plugin => {plugin_name}")

    # Send restart notification
    tz = pytz.timezone('Asia/Dhaka')
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")

    try:
        await app.send_message(
            chat_id=LOG_CHANNEL,
            text=Text.RESTART_TXT.format(today, time_str),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        print(f"⚠️ Failed to send restart notification: {e}")

    print('🚀 Client Bot is running!')
    await idle()


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
