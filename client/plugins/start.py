# Don't Remove Credit @pikachufrombd

import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import LOG_CHANNEL, BACKEND_URL, ADMINS
from database.db import db
from texts import Text


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
    rm = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/Team_SixtyNine"),
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/pikachufrombd")
        ],
        [
            InlineKeyboardButton("📂 ᴍʏ ꜰɪʟᴇꜱ", callback_data="show_myfiles"),
            InlineKeyboardButton("📊 ꜱᴛᴀᴛꜱ", callback_data="show_stats")
        ]
    ])
    await message.reply_text(
        text=Text.START_TXT.format(message.from_user.mention, me.username, me.first_name),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_to_message_id=message.id
    )


@Client.on_callback_query(filters.regex("^show_stats$"))
async def stats_callback(client, callback_query):
    total_users = await db.total_users_count()
    total_files = await db.total_files_count()
    await callback_query.answer(
        f"👥 Users: {total_users} | 📁 Files: {total_files}",
        show_alert=True
    )


@Client.on_message(filters.command("stats") & filters.incoming & filters.private)
async def stats(client, message):
    total_users = await db.total_users_count()
    total_files = await db.total_files_count()
    await message.reply_text(
        f"<b>📊 Bot Stats</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users :</b> <code>{total_users}</code>\n"
        f"📁 <b>Total Files :</b> <code>{total_files}</code>\n"
        f"━━━━━━━━━━━━━━━━━━",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^show_myfiles$"))
async def myfiles_start_callback(client, callback_query):
    """Handle /myfiles from button click."""
    user_id = callback_query.from_user.id
    total = await db.get_user_files_count(user_id)

    if total == 0:
        await callback_query.answer("📂 You haven't uploaded any files yet!", show_alert=True)
        return

    page = 1
    per_page = 10
    skip = 0

    files = await db.get_user_files(user_id, skip=skip, limit=per_page)
    total_pages = (total + per_page - 1) // per_page

    text = build_myfiles_text(files, page, total_pages, total, skip)
    buttons = build_myfiles_buttons(page, total_pages)

    await callback_query.message.reply_text(
        text=text,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=buttons
    )
    await callback_query.answer()


@Client.on_message(filters.command("myfiles") & filters.incoming & filters.private)
async def my_files(client, message):
    """Show user's uploaded files with links."""
    user_id = message.from_user.id

    try:
        parts = message.text.split()
        page = int(parts[1]) if len(parts) > 1 else 1
    except (ValueError, IndexError):
        page = 1

    page = max(1, page)
    per_page = 10
    skip = (page - 1) * per_page

    total = await db.get_user_files_count(user_id)

    if total == 0:
        await message.reply_text(
            "<b>📂 You haven't uploaded any files yet!</b>\n\n"
            "Send me any file and I'll generate stream & download links.",
            parse_mode=enums.ParseMode.HTML
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
        reply_markup=buttons
    )


@Client.on_callback_query(filters.regex(r"^myfiles_(\d+)$"))
async def myfiles_callback(client, callback_query):
    """Handle pagination for /myfiles."""
    page = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    per_page = 10
    skip = (page - 1) * per_page

    total = await db.get_user_files_count(user_id)
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
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"myfiles_{page-1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"myfiles_{page+1}"))
    return InlineKeyboardMarkup([buttons]) if buttons else None
