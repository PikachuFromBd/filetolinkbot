import mimetypes
from pyrogram import Client
from typing import Any, Optional
from pyrogram.types import Message
from pyrogram.file_id import FileId
from exceptions import FileNotFound


# Known mime types for Telegram media types
MEDIA_MIME_MAP = {
    "photo": "image/jpeg",
    "sticker": "image/webp",
    "voice": "audio/ogg",
    "video_note": "video/mp4",
    "animation": "video/mp4",
}


async def parse_file_id(message: Message) -> Optional[FileId]:
    media = get_media_from_message(message)
    if media:
        return FileId.decode(media[1].file_id)


async def parse_file_unique_id(message: Message) -> Optional[str]:
    media = get_media_from_message(message)
    if media:
        return media[1].file_unique_id


async def get_file_ids(client: Client, chat_id: int, message_id: int) -> Optional[FileId]:
    """Fetch a message and extract full file ID properties."""
    message = await client.get_messages(chat_id, message_id)
    if message.empty:
        raise FileNotFound

    result = get_media_from_message(message)
    if not result:
        raise FileNotFound

    media_type, media = result
    file_unique_id = media.file_unique_id
    file_id = FileId.decode(media.file_id)

    # Attach extra properties to the FileId object
    file_size = getattr(media, "file_size", 0)
    file_name = getattr(media, "file_name", "")

    # Smart mime detection
    mime_type = detect_mime_type(media, media_type, file_name)

    # Smart file name
    if not file_name:
        file_name = generate_file_name(media_type, message_id, mime_type)

    setattr(file_id, "file_size", file_size)
    setattr(file_id, "mime_type", mime_type)
    setattr(file_id, "file_name", file_name)
    setattr(file_id, "unique_id", file_unique_id)
    return file_id


def detect_mime_type(media, media_type, file_name):
    """Auto-detect the correct mime type."""
    # 1. Known media type
    if media_type in MEDIA_MIME_MAP:
        return MEDIA_MIME_MAP[media_type]

    # 2. Pyrogram's mime if not generic
    pyrogram_mime = getattr(media, "mime_type", None)
    if pyrogram_mime and pyrogram_mime != "application/octet-stream":
        return pyrogram_mime

    # 3. Guess from file name
    if file_name:
        guessed = mimetypes.guess_type(file_name)[0]
        if guessed:
            return guessed

    # 4. Fallback
    return pyrogram_mime or "application/octet-stream"


def generate_file_name(media_type, message_id, mime_type):
    """Generate a proper file name with correct extension."""
    ext_map = {
        "photo": "jpg",
        "sticker": "webp",
        "voice": "ogg",
        "video_note": "mp4",
        "animation": "gif",
        "video": "mp4",
        "audio": "mp3",
    }
    ext = ext_map.get(media_type)
    if not ext and mime_type:
        try:
            ext = mime_type.split("/")[1]
        except (IndexError, AttributeError):
            ext = "bin"
    return f"{media_type}_{message_id}.{ext or 'bin'}"


def get_media_from_message(message: Message) -> Any:
    """Extract the media object and type from any type of media message."""
    media_types = (
        "audio", "document", "photo", "sticker",
        "animation", "video", "voice", "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return attr, media
    return None
