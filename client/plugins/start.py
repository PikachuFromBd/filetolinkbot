# Don't Remove Credit @pikachufrombd

import time
import psutil
import humanize
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import LOG_CHANNEL, BACKEND_URL, ADMINS
from database.db import db
from texts import Text

BOT_START_TIME = time.time()


# ─── /start ───

@Client.on_message(filters.command("start") & filters.incoming & filters.private)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        try:
            await client.send_message(
                LOG_CHANNEL,
                Text.LOG_TEXT.format(message.from_user.id, message.from_user.mention),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass

    me = await client.get_me()
    await message.reply_text(
        text=Text.START_TXT.format(message.from_user.mention, me.username, me.first_name),
        reply_markup=start_markup(),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_to_message_id=message.id
    )


def start_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/Team_SixtyNine")
        ],
        [
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="tg://user?id=6129625814")
        ],
        [
            InlineKeyboardButton("📂 ᴍʏ ꜰɪʟᴇꜱ", callback_data="show_myfiles_1")
        ]
    ])


# ─── Back to Menu ───

@Client.on_callback_query(filters.regex("^back_to_menu$"))
async def back_to_menu(client, callback_query):
    me = await client.get_me()
    user = callback_query.from_user
    await callback_query.message.edit_text(
        text=Text.START_TXT.format(user.mention, me.username, me.first_name),
        reply_markup=start_markup(),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )


# ─── My Files (edit message) ───

@Client.on_callback_query(filters.regex(r"^show_myfiles_(\d+)$"))
async def myfiles_callback(client, callback_query):
    page = int(callback_query.data.split("_")[-1])
    user_id = callback_query.from_user.id
    per_page = 10
    skip = (page - 1) * per_page

    total = await db.get_user_files_count(user_id)

    if total == 0:
        await callback_query.answer("📂 You haven't uploaded any files yet!", show_alert=True)
        return

    files = await db.get_user_files(user_id, skip=skip, limit=per_page)
    total_pages = (total + per_page - 1) // per_page

    text = build_myfiles_text(files, page, total_pages, total, skip)
    buttons = build_myfiles_buttons(page, total_pages)

    await callback_query.message.edit_text(
        text=text,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=buttons
    )
    await callback_query.answer()


@Client.on_message(filters.command("myfiles") & filters.incoming & filters.private)
async def my_files_cmd(client, message):
    user_id = message.from_user.id
    page = 1
    per_page = 10
    skip = 0

    total = await db.get_user_files_count(user_id)

    if total == 0:
        await message.reply_text(
            "<b>📂 You haven't uploaded any files yet!</b>\n\n"
            "Send me any file and I'll generate stream & download links.",
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )
        return

    files = await db.get_user_files(user_id, skip=skip, limit=per_page)
    total_pages = (total + per_page - 1) // per_page

    text = build_myfiles_text(files, page, total_pages, total, skip)
    buttons = build_myfiles_buttons(page, total_pages)

    await message.reply_text(
        text=text,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=buttons,
        reply_to_message_id=message.id
    )


def build_myfiles_text(files, page, total_pages, total, skip):
    text = f"<b>📂 Your Files</b> — Page {page}/{total_pages}\n"
    text += f"━━━━━━━━━━━━━━━━━━\n"
    text += f"<b>Total :</b> {total} files\n\n"

    for i, f in enumerate(files, start=skip + 1):
        name = f.get('file_name', 'Unknown')
        size = humanize.naturalsize(f.get('file_size', 0))
        file_hash = f.get('hash', '')
        msg_id = f.get('message_id', '')
        stream = f"{BACKEND_URL}/watch/{file_hash}{msg_id}"
        download = f"{BACKEND_URL}/dl/{file_hash}{msg_id}"

        text += (
            f"<b>{i}.</b> <code>{name}</code>\n"
            f"    📦 {size}\n"
            f"    🖥 {stream}\n"
            f"    📥 {download}\n\n"
        )
    return text


def build_myfiles_buttons(page, total_pages):
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"show_myfiles_{page-1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"show_myfiles_{page+1}"))

    rows = []
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(rows)


# ─── /stats (Admin Only) ───

@Client.on_message(filters.command("stats") & filters.incoming & filters.private)
async def stats(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply_text(
            "⛔ <b>Admin only command!</b>",
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )
        return

    total_users = await db.total_users_count()
    total_files = await db.total_files_count()
    await message.reply_text(
        f"<b>📊 Bot Stats</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Users :</b> <code>{total_users}</code>\n"
        f"📁 <b>Files :</b> <code>{total_files}</code>\n"
        f"━━━━━━━━━━━━━━━━━━",
        parse_mode=enums.ParseMode.HTML,
        reply_to_message_id=message.id
    )


# ─── /ping ───

@Client.on_message(filters.command("ping") & filters.incoming & filters.private)
async def ping(client, message):
    # Measure bot response time
    start_time = time.time()
    msg = await message.reply_text(
        "🏓 <b>Pinging...</b>",
        parse_mode=enums.ParseMode.HTML,
        reply_to_message_id=message.id
    )
    ping_ms = round((time.time() - start_time) * 1000, 2)

    # System info
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime_seconds = time.time() - BOT_START_TIME

    # Format uptime
    days, remainder = divmod(int(uptime_seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days > 0:
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        uptime_str = f"{hours}h {minutes}m {seconds}s"
    else:
        uptime_str = f"{minutes}m {seconds}s"

    text = (
        f"<b>🏓 Pong!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>Response :</b> <code>{ping_ms}ms</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💻 <b>CPU :</b> <code>{cpu}%</code>\n"
        f"🧠 <b>RAM :</b> <code>{ram.percent}%</code> "
        f"({humanize.naturalsize(ram.used)}/{humanize.naturalsize(ram.total)})\n"
        f"💾 <b>Disk :</b> <code>{disk.percent}%</code> "
        f"({humanize.naturalsize(disk.used)}/{humanize.naturalsize(disk.total)})\n"
        f"⏱ <b>Uptime :</b> <code>{uptime_str}</code>\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    await msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
