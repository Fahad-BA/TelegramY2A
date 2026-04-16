# Telegram Y2A Bot

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![YT-DLP](https://img.shields.io/badge/yt--dlp-supported-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![Telegram](https://img.shields.io/badge/telegram-bot-32AEE3.svg)](https://core.telegram.org/bots)

A Telegram bot that downloads YouTube videos and converts them to MP3 format. Built with passion and good vibes.

## Features

- ⚡ **Fast download** - Optimized for speed with concurrent downloads
- 🎵 **MP3 conversion** - Converts YouTube videos to high-quality MP3 files
- 📱 **Telegram integration** - Works seamlessly with Telegram
- 🗑️ **Auto-cleanup** - Automatically deletes files after sending
- ⏱️ **Duration limit** - Limits downloads to 7 minutes maximum
- 🔥 **Vibe coded** - Built with good vibes by Fahad Alhuqaili

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token
- Deno (for JavaScript runtime)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fahad-alhuqaili/TelegramY2A.git
   cd TelegramY2A
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Deno** (required for yt-dlp)
   ```bash
   curl -fsSL https://deno.land/install.sh | sh
   ```

5. **Configure your bot token**
   - Replace the `BOT_TOKEN` in `bot.py` with your actual bot token from BotFather

6. **Run the bot**
   ```bash
   python bot.py
   ```

Or run as a systemd service:

```bash
sudo cp y2a.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable y2a.service
sudo systemctl start y2a.service
```

## Usage

1. **Start a chat with your bot** in Telegram
2. **Send any YouTube video link** to the bot
3. **Wait for the download** - The bot will show "جاري التحميل..."
4. **Receive the MP3 file** - The bot sends the audio file with the song title
5. **Done!** - The file is automatically deleted after sending

## Configuration

### Bot Settings
- **Max duration**: 7 minutes (420 seconds)
- **Audio quality**: 192 kbps MP3
- **File naming**: `datetime-song_title.mp3`
- **Concurrent downloads**: 3

### Environment Variables
- `BOT_TOKEN`: Your Telegram bot token
- `PATH`: Include Deno binary path for yt-dlp

## Bot Commands

The bot doesn't require any special commands. Simply send a YouTube URL and it will:

1. Validate the URL
2. Download the video
3. Convert to MP3
4. Send the audio file
5. Clean up temporary files

## File Structure

```
TelegramY2A/
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
├── y2a.service       # Systemd service file
├── run.sh            # Quick start script
├── Downloads/        # Temporary download directory
├── .gitignore        # Git ignore file
└── README.md         # This file
```

## Troubleshooting

### Slow Downloads
- Make sure Deno is installed and in your PATH
- Check your internet connection
- Try shorter videos first

### JavaScript Runtime Error
If you see "No supported JavaScript runtime could be found":
```bash
curl -fsSL https://deno.land/install.sh | sh
export PATH="$HOME/.deno/bin:$PATH"
```

### Service Issues
If running as a service:
```bash
sudo systemctl status y2a.service
sudo journalctl -u y2a.service -f
```

## Contributing

This project is open for contributions! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve the documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Fahad Alhuqaili** - Built with good vibes and positive energy 🌟

---

*Made with ❤️ and good vibes*