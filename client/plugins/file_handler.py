# Don't Remove Credit @pikachufrombd

import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BACKEND_URL, LOG_CHANNEL, SHORTLINK, SHORTLINK_URL, SHORTLINK_API
from database.db import db
from texts import Text


def get_media_from_message(message):
    """Extract media object from a message."""
    media_types = (
        "document", "video", "audio", "animation",
        "voice", "video_note", "photo", "sticker",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media
    return None


async def get_shortlink(link):
    """Convert a link to shortlink if enabled."""
    if not SHORTLINK:
        return link
    try:
        from shortzy import Shortzy
        shortzy = Shortzy(api_key=SHORTLINK_API, base_site=SHORTLINK_URL)
        return await shortzy.convert(link)
    except Exception:
        return link


@Client.on_message(
    filters.private & (
        filters.document | filters.video | filters.audio |
        filters.animation | filters.voice | filters.video_note |
        filters.photo | filters.sticker
    )
)
async def file_handler(client, message):
    """Handle incoming files — copy to log channel, save to DB, generate links."""
    media = get_media_from_message(message)
    if not media:
        return

    user_id = message.from_user.id
    username = message.from_user.mention

    # Get file info
    file_name = getattr(media, 'file_name', None) or f"file_{message.id}"
    file_size = getattr(media, 'file_size', 0)
    mime_type = getattr(media, 'mime_type', 'application/octet-stream')
    file_unique_id = media.file_unique_id
    file_id = media.file_id

    # For photos, set a proper name
    if message.photo:
        file_name = f"photo_{message.id}.jpg"
        mime_type = "image/jpeg"

    # Copy file to log channel (no forward tag, like original)
    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=file_id,
    )

    # Save to MongoDB
    file_hash = await db.save_file(
        message_id=log_msg.id,
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
        file_unique_id=file_unique_id,
        file_id=file_id,
        user_id=user_id
    )

    # Generate URLs
    stream_url = f"{BACKEND_URL}/watch/{file_hash}{log_msg.id}"
    download_url = f"{BACKEND_URL}/dl/{file_hash}{log_msg.id}"

    # Apply shortlink if enabled
    stream_url = await get_shortlink(stream_url)
    download_url = await get_shortlink(download_url)

    # Log the link generation in log channel
    await log_msg.reply_text(
        text=Text.LOG_FILE_TXT.format(
            user_id=user_id,
            username=username,
            file_name=file_name,
            stream=stream_url,
            download=download_url
        ),
        quote=True,
        disable_web_page_preview=True,
        parse_mode=enums.ParseMode.HTML,
    )

    human_size = humanize.naturalsize(file_size) if file_size else "Unknown"

    # Check if URLs are HTTPS (buttons require https)
    if stream_url.startswith("https://"):
        # Production mode — send with inline buttons
        rm = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream_url),
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download_url)
            ]
        ])
        await message.reply_text(
            text=Text.LINK_TXT.format(
                file_name=file_name,
                file_size=human_size,
                download=download_url,
                stream=stream_url
            ),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )
    else:
        # Local/HTTP mode — send links as plain text (buttons need https)
        await message.reply_text(
            text=Text.LINK_TXT.format(
                file_name=file_name,
                file_size=human_size,
                download=download_url,
                stream=stream_url
            ),
            quote=True,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )

