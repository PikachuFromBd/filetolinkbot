from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# Backend bot — no updates, only used for file access from Telegram
bot = Client(
    name="FileToLinkBackend",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    no_updates=True,
    in_memory=True,
)
