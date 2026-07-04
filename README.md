# 🎵 Y2A — YouTube to Audio Telegram Bot

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![python-telegram-bot](https://img.shields.io/badge/Telegram%20Bot-22.7-0088cc?logo=telegram&logoColor=white)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey?logo=linux&logoColor=white)

A Telegram bot that downloads audio from YouTube and SoundCloud links and lets you search YouTube by name — all without a YouTube API key. Built with `yt-dlp` for reliable extraction and `python-telegram-bot` for a smooth inline-keyboard experience.

---

## ✨ Features

- 🔗 **Direct URL Download** — Send a YouTube or SoundCloud link, get an MP3 back
- 🔍 **YouTube Search** — Use `/search <song name>` to browse 5 results at a time with inline buttons
- 📄 **Paginated Results** — Load more results with a single tap
- ⏱️ **Duration Guard** — Rejects videos longer than 7 minutes (configurable)
- 🎧 **192 kbps MP3 Output** — Converted via FFmpeg for consistent quality
- 🧹 **Auto Cleanup** — Downloaded files are deleted after sending
- 🇸🇦 **Arabic UI** — Bot messages in Arabic for the target audience
- 🔐 **No YouTube API Key Needed** — Uses `yt-dlp` search extraction

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3** | Core runtime |
| **python-telegram-bot** | Telegram Bot API |
| **yt-dlp** | YouTube / SoundCloud extraction |
| **FFmpeg** | Audio conversion to MP3 |
| **python-dotenv** | Environment variable management |
| **systemd** | Production process management |

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) installed and on `PATH`
- A Telegram Bot token from [@BotFather](https://t.me/BotFather)

### Steps

```bash
# Clone the repo
git clone https://github.com/Fahad-BA/TelegramY2A.git
cd TelegramY2A

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # Linux/macOS
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure your bot token
cp .env.example .env
echo "BOT_TOKEN=your_token_here" > .env

# Run the bot
python bot.py
```

---

## 🚀 Usage

### Direct Download

Send any YouTube or SoundCloud URL as a plain message — the bot downloads and returns the audio as an MP3 file.

### Search

```
/search Lovestruck Jxdn
```

The bot returns 5 inline results. Tap a button to download, or tap **➡️ المزيد** for more results.

### Run as a systemd Service (Production)

```bash
# Edit the service file paths to match your setup
sudo cp y2a.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now y2a
```

---

## ⚙️ Configuration

| Variable | File | Description |
|----------|------|-------------|
| `BOT_TOKEN` | `.env` | Telegram Bot API token from BotFather |
| `max_duration` | `bot.py` | Max video length in seconds (default: 420 = 7 min) |
| `preferredquality` | `bot.py` | MP3 bitrate in kbps (default: 192) |

---

## 📁 Project Structure

```
Y2A/
├── bot.py              # Main bot logic (search, download, send)
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
├── y2a.service         # systemd unit file for production
├── Downloads/          # Temporary audio storage (auto-cleaned)
└── .gitignore
```

---

## 📝 License

This project is licensed under the MIT License.
