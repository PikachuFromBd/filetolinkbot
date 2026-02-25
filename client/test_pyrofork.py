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
            style=ButtonStyle.PRIMARY
        )],
        [InlineKeyboardButton(
            text="Success Button",
            callback_data="success_btn",
            style=ButtonStyle.SUCCESS
        )],
        [InlineKeyboardButton(
            text="Danger Button",
            callback_data="danger_btn",
            style=ButtonStyle.DANGER
        )]
    ])
    
    await message.reply(
        "<b>🎨 Choose a button color!</b>\n\n"
        "🔵 <b>Primary</b> - Dark Blue Button\n"
        "🟢 <b>Success</b> - Green Button\n"
        "🔴 <b>Danger</b> - Red Button\n\n"
        "<i>⚡ Powered by Kurigram</i>",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
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
