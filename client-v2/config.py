import re
from os import environ
from dotenv import load_dotenv

load_dotenv()

id_pattern = re.compile(r'^.\d+$')

# Bot information
API_ID = int(environ.get('API_ID', '0'))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')

# Admins & Channels
_log_ch = environ.get('LOG_CHANNEL', '0')
LOG_CHANNEL = int(_log_ch) if _log_ch.lstrip('-').isdigit() else _log_ch
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]

# MongoDB
DATABASE_URI = environ.get('DATABASE_URI', '')
DATABASE_NAME = environ.get('DATABASE_NAME', 'filetolinkbot')

# Backend server URL (where files are served from)
BACKEND_URL = environ.get('BACKEND_URL', 'http://localhost:8080').rstrip('/')

# Shortlink
SHORTLINK = environ.get('SHORTLINK', 'False').lower() in ('true', '1', 'yes')
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', '')

# Force Join
FORCE_JOIN_CHANNEL = environ.get('FORCE_JOIN_CHANNEL', 'Team_SixtyNine')  # channel username without @
FORCE_JOIN_TIMEOUT = int(environ.get('FORCE_JOIN_TIMEOUT', '300'))  # seconds (5 min)
