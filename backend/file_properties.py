from pyrogram import Client
from typing import Any, Optional
from pyrogram.types import Message
from pyrogram.file_id import FileId
from exceptions import FileNotFound


async def parse_file_id(message: Message) -> Optional[FileId]:
    media = get_media_from_message(message)
    if media:
        return FileId.decode(media.file_id)


async def parse_file_unique_id(message: Message) -> Optional[str]:
    media = get_media_from_message(message)
    if media:
        return media.file_unique_id


async def get_file_ids(client: Client, chat_id: int, message_id: int) -> Optional[FileId]:
    """Fetch a message and extract full file ID properties."""
    message = await client.get_messages(chat_id, message_id)
    if message.empty:
        raise FileNotFound

    media = get_media_from_message(message)
    if not media:
        raise FileNotFound

    file_unique_id = await parse_file_unique_id(message)
    file_id = await parse_file_id(message)

    # Attach extra properties to the FileId object
    setattr(file_id, "file_size", getattr(media, "file_size", 0))
    setattr(file_id, "mime_type", getattr(media, "mime_type", "application/octet-stream"))
    setattr(file_id, "file_name", getattr(media, "file_name", ""))
    setattr(file_id, "unique_id", file_unique_id)
    return file_id


def get_media_from_message(message: Message) -> Any:
    """Extract the media object from any type of media message."""
    media_types = (
        "audio", "document", "photo", "sticker",
        "animation", "video", "voice", "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media
    return None
