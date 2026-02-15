# Don't Remove Credit @pikachufrombd
# FileToLink V3 — Backend Server

import logging
import asyncio
from aiohttp import web
from config import PORT, LOG_CHANNEL
from bot import bot
from streamer import ByteStreamer
from routes import routes, set_streamer

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)


async def start():
    # Start the backend Pyrogram bot (no updates, file access only)
    await bot.start()
    me = await bot.get_me()
    print(f"\n⚡ Backend bot connected as @{me.username}")

    # Resolve log channel peer to avoid "Peer id invalid"
    try:
        chat = await bot.get_chat(LOG_CHANNEL)
        print(f"📢 Log channel resolved: {chat.title}")
    except Exception as e:
        print(f"⚠️ Could not resolve log channel: {e}")
        print("   Make sure the backend bot is admin in the log channel!")

    # Initialize the ByteStreamer with the bot client
    byte_streamer = ByteStreamer(bot)
    set_streamer(byte_streamer)
    print("📦 ByteStreamer initialized")

    # Create and start aiohttp web server
    app = web.Application(client_max_size=30000000)
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"🚀 Backend server running on http://0.0.0.0:{PORT}")
    print(f"🌐 Serving files at port {PORT}")
    print("─" * 50)

    # Keep running
    await asyncio.Event().wait()


async def shutdown():
    await bot.stop()


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Backend server stopped 👋')
        asyncio.get_event_loop().run_until_complete(shutdown())
