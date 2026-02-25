from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("test_kurigram", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text="Primary Button",
            callback_data="primary_btn",
            icon_custom_emoji_id=5258096772776991776,
            style=ButtonStyle.PRIMARY  # Dark Blue
        )],
        [InlineKeyboardButton(
            text="Success Button",
            callback_data="success_btn",
            icon_custom_emoji_id=5258503720928288433,
            style=ButtonStyle.SUCCESS  # Green
        )],
        [InlineKeyboardButton(
            text="Danger Button",
            callback_data="danger_btn",
            icon_custom_emoji_id=5258331647358540449,
            style=ButtonStyle.DANGER  # Red
        )]
    ])
    
    await message.reply(
        "Choose a button color! 🎨\n\n"
        "🔵 Primary - Dark Blue Button\n"
        "🟢 Success - Green Button\n"
        "🔴 Danger - Red Button",
        reply_markup=keyboard
    )

@app.on_callback_query()
async def handle_buttons(client, callback_query: CallbackQuery):
    messages = {
        "primary_btn": "✅ You clicked Primary (Dark Blue) button!",
        "success_btn": "✅ You clicked Success (Green) button!",
        "danger_btn": "✅ You clicked Danger (Red) button!"
    }
    
    await callback_query.answer(
        messages.get(callback_query.data),
        show_alert=True
    )

print("Bot started! 🚀")
app.run()
