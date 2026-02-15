import re
from os import environ
from dotenv import load_dotenv

load_dotenv()

# Bot information (backend bot — no updates, only file access)
API_ID = int(environ.get('API_ID', '0'))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')

# Log channel (same as client bot)
_log_ch = environ.get('LOG_CHANNEL', '0')
LOG_CHANNEL = int(_log_ch) if _log_ch.lstrip('-').isdigit() else _log_ch

# MongoDB (same database as client)
DATABASE_URI = environ.get('DATABASE_URI', '')
DATABASE_NAME = environ.get('DATABASE_NAME', 'filetolinkbot')

# Web server
PORT = int(environ.get('PORT', '8080'))
URL = environ.get('URL', 'http://localhost:8080/').rstrip('/') + '/'
