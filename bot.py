#!/usr/bin/env python3
import asyncio
import logging
import os
from datetime import datetime
import random
import string
from pathlib import Path
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# yt-dlp options
YDL_OPTS = {
    'format': '140/bestaudio[acodec=opus]/bestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'max_duration': 420,  # 7 minutes
    'nocheckcertificate': True,
    'concurrent_fragment_downloads': 3,
    'fragment_retries': 3,
}

async def download_audio(url: str) -> str:
    """Download audio from YouTube URL and return the file path."""
    # Create Downloads directory if it doesn't exist
    downloads_dir = os.path.join(os.path.dirname(__file__), 'Downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Get video info first to get the title
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info['title']
        
        # Clean filename (remove invalid characters)
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        # Add datetime prefix for uniqueness
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{now}-{safe_title}.mp3"
        filepath = os.path.join(downloads_dir, filename)
    
    # Update yt-dlp options
    YDL_OPTS['outtmpl'] = filepath.replace('.mp3', '.%(ext)s')
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Find the downloaded file (might have different extension before conversion)
            mp3_file = filepath
            if not os.path.exists(mp3_file):
                # Look for any file that starts with our filename pattern
                base_name = filepath.replace('.mp3', '')
                for file in Path(downloads_dir).glob(f"{os.path.basename(base_name)}*"):
                    if file.suffix == '.mp3':
                        return str(file)
            
            return mp3_file
            
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        raise Exception(f"خطأ في التحميل: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    message = update.message
    
    if not message.text:
        await message.reply_text("أرسل رابط يوتيوب فقط.")
        return
    
    url = message.text.strip()
    
    # Check if it's a YouTube URL
    if not ('youtube.com' in url or 'youtu.be' in url):
        await message.reply_text("هذا الرابط مو من يوتيوب. أرسل رابط يوتيوب صحيح.")
        return
    
    # Send initial message
    processing_msg = await message.reply_text("جاري التحميل... ⏳")
    
    try:
        # Download the audio
        audio_path = await download_audio(url)
        
        # Get the song title for caption
        audio_filename = os.path.basename(audio_path)
        # Remove datetime prefix from caption
        if "-" in audio_filename:
            title_only = "-".join(audio_filename.split("-")[1:])
            if title_only.endswith(".mp3"):
                title_only = title_only[:-4]
        
        # Send the audio file
        await update.message.reply_audio(
            audio=open(audio_path, 'rb'),
            caption=f"✅ {title_only}"
        )
        
        # Delete the processing message
        await processing_msg.delete()
        
        # Delete the audio file after sending
        try:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
                logger.info(f"Deleted file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to delete file {audio_path}: {e}")
            
    except Exception as e:
        await processing_msg.edit_text(f"❌ حدث خطأ: {str(e)}")
        logger.error(f"Error in handle_message: {e}")

def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in .env file")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()