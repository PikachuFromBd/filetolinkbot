<p align="center">
  <img src="https://img.icons8.com/fluency/96/link.png" width="80"/>
</p>

<h1 align="center">FileToLink Bot</h1>

<p align="center">
  <b>An advanced Telegram File to Link bot with stream & download capabilities</b>
</p>

<p align="center">
  <a href="https://t.me/PikaFileToLinkBot"><img src="https://img.shields.io/badge/Bot-@PikaFileToLinkBot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Bot"></a>
  <a href="https://t.me/Team_SixtyNine"><img src="https://img.shields.io/badge/Channel-@Team__SixtyNine-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Channel"></a>
  <a href="https://t.me/listkiss"><img src="https://img.shields.io/badge/Developer-Shahadat_Hassan-6c5ce7?style=for-the-badge&logo=telegram&logoColor=white" alt="Developer"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pyrofork-2.x-FF6F00?style=flat-square&logo=fire&logoColor=white" alt="Pyrofork">
  <img src="https://img.shields.io/badge/aiohttp-3.x-2196F3?style=flat-square&logo=aiohttp&logoColor=white" alt="aiohttp">
  <img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/github/license/PikachuFromBd/filetolinkbot?style=flat-square" alt="License">
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎬 **Video/Audio Streaming** | Stream media directly in browser with [Plyr.js](https://plyr.io/) player |
| 📥 **Direct Download** | One-click download links for any file |
| 🌐 **HTML Static Hosting** | Upload `.html` files and view them as live web pages (sanitized, no server-side execution) |
| 🔍 **Smart Mime Detection** | Auto-detects file types — photos, stickers, voice, video notes, documents |
| 🔗 **Permanent Links** | Generated links never expire as long as the bot is running |
| 📱 **Responsive UI** | Beautiful dark theme with [Remix Icons](https://remixicon.com/) — works on mobile & desktop |
| 📂 **My Files** | Users can view & manage all their uploaded files |
| ⚡ **Speed Test** | `/ping` command shows server latency, CPU, RAM, disk & uptime |
| 📢 **Broadcast** | Admin broadcast messages to all users |
| 🔗 **Shortlink Support** | Optional shortlink integration (Shareus, etc.) |
| 🛡️ **Secure** | HTML files are sanitized — `<script>`, `<iframe>`, `<form>`, JS handlers are stripped |

---

## 🏗️ Architecture

```
filetolinkbot/
├── client/                  # 🤖 Telegram Bot (Pyrofork)
│   ├── bot.py               # Bot entry point
│   ├── config.py             # Environment config loader
│   ├── texts.py              # Message templates
│   ├── database/
│   │   └── db.py             # MongoDB operations
│   ├── plugins/
│   │   ├── start.py          # /start, /ping, /stats, /myfiles, callbacks
│   │   ├── file_handler.py   # File upload → link generation
│   │   └── broadcast.py      # Admin broadcast
│   └── requirements.txt
│
├── backend/                 # 🌐 Web Server (aiohttp)
│   ├── server.py             # Server entry point
│   ├── bot.py                # Backend bot client
│   ├── config.py             # Environment config
│   ├── routes.py             # /watch, /dl, HTML serving, streaming
│   ├── streamer.py           # Telegram file streaming engine
│   ├── file_properties.py    # File property extraction
│   ├── exceptions.py         # Custom exceptions
│   ├── database/
│   │   └── db.py             # MongoDB operations
│   ├── templates/
│   │   ├── player.html       # Video/audio player page
│   │   └── download.html     # File download page
│   └── requirements.txt
│
└── cloudflare-worker/       # ☁️ Optional Cloudflare Worker proxy
```

---

## 🚀 Deployment

### Prerequisites

- Python 3.10+
- MongoDB Atlas (or local MongoDB)
- Two Telegram Bot tokens (one for client, one for backend)
- A VPS with a public IP or domain

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/PikachuFromBd/filetolinkbot.git
cd filetolinkbot
```

### 2️⃣ Configure Environment Variables

Create `.env` files in both `client/` and `backend/` directories:

**`client/.env`**
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_client_bot_token
LOG_CHANNEL=-100xxxxxxxxxx
ADMINS=your_user_id
DATABASE_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=filetolinkbot
BACKEND_URL=https://yourdomain.com

# Optional
SHORTLINK=false
SHORTLINK_URL=api.shareus.io
SHORTLINK_API=your_api_key
```

**`backend/.env`**
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_backend_bot_token
LOG_CHANNEL=-100xxxxxxxxxx
DATABASE_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=filetolinkbot
PORT=8080
URL=https://yourdomain.com/
```

> ⚠️ **Important:** Use **different bot tokens** for client and backend. They must share the same `LOG_CHANNEL` and `DATABASE_URI`.

### 3️⃣ Install Dependencies

```bash
# Client bot
cd client
pip install -r requirements.txt
pip install psutil

# Backend server
cd ../backend
pip install -r requirements.txt
```

### 4️⃣ Start the Services

```bash
# Terminal 1 — Start backend server
cd backend
python server.py

# Terminal 2 — Start client bot
cd client
python bot.py
```

> 💡 **Tip:** Use `screen`, `tmux`, or `systemd` services for production.

---

## 🤖 Bot Commands

| Command | Description | Access |
|---|---|---|
| `/start` | Welcome message with buttons | All users |
| `/ping` | Server status — latency, CPU, RAM, disk, uptime | All users |
| `/myfiles` | View & manage your uploaded files | All users |
| `/stats` | Bot statistics — total users & files | Admin only |
| `/broadcast` | Send a message to all users (reply to a message) | Admin only |

---

## 🌐 Web Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | API health check |
| `GET /watch/{hash}{id}` | Stream page (video/audio player) or static HTML viewer |
| `GET /dl/{hash}{id}` | Direct file download |

---

## 📸 Screenshots

<p align="center">
  <img src="https://img.shields.io/badge/Player-Plyr.js_Dark_Theme-6c5ce7?style=for-the-badge" alt="Player">
  <img src="https://img.shields.io/badge/Download-Premium_UI-a855f7?style=for-the-badge" alt="Download">
  <img src="https://img.shields.io/badge/Mobile-Responsive-0ea5e9?style=for-the-badge" alt="Mobile">
</p>

---

## 🛡️ Security

- **HTML Sanitization** — Uploaded HTML files are stripped of:
  - `<script>` tags
  - `<iframe>`, `<object>`, `<embed>` tags
  - `<form>` tags
  - JavaScript event handlers (`onclick`, `onerror`, etc.)
  - `javascript:` URLs
- **No server-side execution** — HTML files are served purely as static content
- **Hash-based URLs** — Files are accessed via secure hash + message ID

---

## 🧰 Tech Stack

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pyrofork-FF6F00?style=for-the-badge&logo=fire&logoColor=white" alt="Pyrofork">
  <img src="https://img.shields.io/badge/aiohttp-2196F3?style=for-the-badge&logo=aiohttp&logoColor=white" alt="aiohttp">
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white" alt="Jinja2">
  <img src="https://img.shields.io/badge/Plyr.js-00B3FF?style=for-the-badge&logo=javascript&logoColor=white" alt="Plyr">
  <img src="https://img.shields.io/badge/Remix_Icons-121212?style=for-the-badge&logo=remixicon&logoColor=white" alt="Remix Icons">
</p>

---

## 📝 License

This project is open source. Feel free to fork and modify.

---

<p align="center">
  Made with ❤️ by <a href="https://t.me/listkiss">Shahadat Hassan</a>
</p>
