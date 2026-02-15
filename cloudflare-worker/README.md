# FileToLink — Cloudflare Worker Proxy

This Cloudflare Worker acts as a **permanent proxy URL** for the backend VPS.

## Why?
- VPS IPs change every month
- User file links would break with every VPS change
- The worker URL is **permanent** — links never expire

## How It Works
```
User clicks link → Cloudflare Worker (permanent URL) → Backend VPS (changeable IP)
```

## Setup

### 1. Install Wrangler CLI
```bash
npm install -g wrangler
```

### 2. Login to Cloudflare
```bash
wrangler login
```

### 3. Update Backend IP
Edit `worker.js` line 10:
```js
const BACKEND_ORIGIN = "http://YOUR_VPS_IP:8080";
```

### 4. Deploy
```bash
cd cloudflare-worker
wrangler deploy
```

You'll get a URL like: `https://filetolink-proxy.YOUR_ACCOUNT.workers.dev`

### 5. Update Client Bot
Set `BACKEND_URL` in `FileToLink-Client/.env`:
```
BACKEND_URL=https://filetolink-proxy.YOUR_ACCOUNT.workers.dev
```

## When VPS Changes
1. Edit `worker.js` → update `BACKEND_ORIGIN` with new IP
2. Run `wrangler deploy`
3. Done! All existing links keep working ✅
