# Don't Remove Credit @pikachufrombd

import mimetypes
import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BACKEND_URL, LOG_CHANNEL, SHORTLINK, SHORTLINK_URL, SHORTLINK_API
from database.db import db
from texts import Text


# Mime type mapping for media types that Pyrogram doesn't always set
MEDIA_MIME_MAP = {
    "photo": "image/jpeg",
    "sticker": "image/webp",
    "voice": "audio/ogg",
    "video_note": "video/mp4",
    "animation": "video/mp4",
}


def get_media_info(message):
    """Extract media object and type from a message."""
    media_types = (
        "document", "video", "audio", "animation",
        "voice", "video_note", "photo", "sticker",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media, attr
    return None, None


def detect_mime_type(media, media_type, file_name):
    """Auto-detect the correct mime type."""
    # 1. Check if it's a known media type with fixed mime
    if media_type in MEDIA_MIME_MAP:
        return MEDIA_MIME_MAP[media_type]

    # 2. Use Pyrogram's mime_type if available and not generic
    pyrogram_mime = getattr(media, 'mime_type', None)
    if pyrogram_mime and pyrogram_mime != 'application/octet-stream':
        return pyrogram_mime

    # 3. Guess from file name extension
    if file_name:
        guessed = mimetypes.guess_type(file_name)[0]
        if guessed:
            return guessed

    # 4. Fallback
    return pyrogram_mime or 'application/octet-stream'


def detect_file_name(media, media_type, message_id):
    """Auto-detect a proper file name with correct extension."""
    name = getattr(media, 'file_name', None)
    if name:
        return name

    # Build name from media type
    ext_map = {
        "photo": "jpg",
        "sticker": "webp",
        "voice": "ogg",
        "video_note": "mp4",
        "animation": "gif",
        "video": "mp4",
        "audio": "mp3",
    }
    ext = ext_map.get(media_type, "bin")
    return f"{media_type}_{message_id}.{ext}"


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
    media, media_type = get_media_info(message)
    if not media:
        return

    user_id = message.from_user.id
    username = message.from_user.mention

    # Auto-detect file info
    file_name = detect_file_name(media, media_type, message.id)
    file_size = getattr(media, 'file_size', 0)
    mime_type = detect_mime_type(media, media_type, file_name)
    file_unique_id = media.file_unique_id
    file_id = media.file_id

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
