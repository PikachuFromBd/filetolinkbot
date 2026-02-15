import re
import math
import logging
import secrets
import mimetypes
import urllib.parse
import jinja2
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from config import LOG_CHANNEL, URL
from database.db import db
from exceptions import InvalidHash, FileNotFound


routes = web.RouteTableDef()

# Will be set by server.py after bot starts
streamer = None


def set_streamer(s):
    global streamer
    streamer = s


@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.json_response({
        "status": "running",
        "service": "FileToLink Backend v3.0",
        "developer": "@pikachufrombd"
    })


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def watch_handler(request: web.Request):
    """Render the stream/player page."""
    try:
        path = request.match_info["path"]
        secure_hash, message_id = parse_path(path, request)

        # Verify hash from DB
        file_record = await db.get_file_by_hash(secure_hash, message_id)
        if not file_record:
            # Fallback: verify from Telegram message directly
            file_data = await streamer.get_file_properties(message_id)
            if file_data.unique_id[:6] != secure_hash:
                raise InvalidHash

        # Get file properties for rendering
        file_data = await streamer.get_file_properties(message_id)
        if file_data.unique_id[:6] != secure_hash:
            raise InvalidHash

        # Build download URL using the actual request URL (not config)
        # This auto-adapts to whatever domain/IP the user is accessing from
        scheme = request.headers.get("X-Forwarded-Proto", request.scheme)
        host = request.headers.get("X-Forwarded-Host", request.host)
        base_url = f"{scheme}://{host}/"
        src = urllib.parse.urljoin(
            base_url,
            f"dl/{secure_hash}{message_id}"
        )

        # Determine template
        tag = (file_data.mime_type or "").split("/")[0].strip()
        file_size = humanbytes(file_data.file_size)
        file_name = (file_data.file_name or "Unknown").replace("_", " ")

        if tag in ["video", "audio"]:
            template_file = "templates/player.html"
        else:
            template_file = "templates/download.html"

        with open(template_file) as f:
            template = jinja2.Template(f.read())

        html = template.render(
            file_name=file_name,
            file_url=src,
            file_size=file_size,
        )
        return web.Response(text=html, content_type='text/html')

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FileNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(f"Watch error: {e}", exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))


@routes.get(r"/dl/{path:\S+}", allow_head=True)
async def download_handler(request: web.Request):
    """Handle direct file download/streaming."""
    try:
        path = request.match_info["path"]
        secure_hash, message_id = parse_path(path, request)

        return await media_streamer(request, message_id, secure_hash)

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FileNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(f"Download error: {e}", exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))


def parse_path(path, request):
    """Extract hash and message_id from URL path."""
    match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
    if match:
        secure_hash = match.group(1)
        message_id = int(match.group(2))
    else:
        # Fallback: try to parse id from path and hash from query
        message_id = int(re.search(r"(\d+)(?:/\S+)?", path).group(1))
        secure_hash = request.rel_url.query.get("hash")
    return secure_hash, message_id


async def media_streamer(request: web.Request, message_id: int, secure_hash: str):
    """Stream file bytes from Telegram to the client."""
    range_header = request.headers.get("Range", 0)

    file_id = await streamer.get_file_properties(message_id)

    if file_id.unique_id[:6] != secure_hash:
        raise InvalidHash

    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    body = streamer.yield_file(
        file_id, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )


def humanbytes(size):
    """Convert bytes to human-readable format."""
    if not size:
        return "0 B"
    power = 2 ** 10
    n = 0
    units = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"
