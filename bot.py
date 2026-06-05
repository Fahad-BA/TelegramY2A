#!/usr/bin/env python3
import asyncio
import logging
import os
from datetime import datetime
import random
import string
from pathlib import Path
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes, CallbackQueryHandler
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

async def search_youtube(query: str, page: int = 1) -> list:
    """Search YouTube using yt-dlp without API."""
    # Use more direct search approach
    search_count = 5
    search_query = f"ytsearch{search_count}:{query}"
    print(f"DEBUG: Original query = '{query}'")
    print(f"DEBUG: Formatted query = '{search_query}'")
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': search_count,
        'default_search': 'ytsearch',
    }
    
    try:
        # Add debug logging
        print(f"DEBUG: Search query = '{search_query}'")
        print(f"DEBUG: Page = {page}, Count = {search_count}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)
            print(f"DEBUG: Result type = {type(result)}")
            
            if isinstance(result, list):
                print(f"DEBUG: Got list with {len(result)} items")
            elif result and 'entries' in result:
                print(f"DEBUG: Got playlist with {len(result['entries'])} entries")
            else:
                print(f"DEBUG: Got unexpected result: {result}")
            
            # Handle different result formats
            entries = []
            if isinstance(result, list):
                # Direct list of videos
                for entry in result[:5]:
                    if entry and entry.get('url'):
                        entries.append({
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('url', ''),
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader', 'Unknown')
                        })
            elif result and 'entries' in result:
                # Playlist format with entries
                for entry in result['entries'][:5]:
                    if entry and entry.get('url'):
                        entries.append({
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('url', ''),
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader', 'Unknown')
                        })
            
            return entries
            
    except Exception as e:
        logger.error(f"Error searching YouTube for '{query}': {e}")
        return []

async def download_audio(url: str) -> str:
    """Download audio from YouTube or SoundCloud URL and return the file path."""
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

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search command."""
    if not context.args:
        await update.message.reply_text("🔍 استخدم: /search <اسم الأغنية>")
        return
    
    query = " ".join(context.args)
    search_msg = await update.message.reply_text(f"🔍 جاري البحث عن: {query}...")
    
    try:
        results = await search_youtube(query)
        
        if not results:
            await search_msg.edit_text("❌ لم يتم العثور على نتائج.")
            return
        
        # Create inline keyboard with search results
        keyboard = []
        for result in results:
            video_id = result['id']
            title = result['title']
            duration = result.get('duration', 0)
            uploader = result.get('uploader', 'Unknown')
            
            # Format title with duration
            if duration > 0:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                title_with_time = f"{title} ({minutes}:{seconds:02d})"
            else:
                title_with_time = title
            
            # Truncate long titles
            if len(title_with_time) > 40:
                title_with_time = title_with_time[:37] + "..."
            
            keyboard.append([InlineKeyboardButton(title_with_time, callback_data=f"play_{video_id}")])
        
        # Add navigation buttons
        nav_buttons = []
        nav_buttons.append(InlineKeyboardButton("➡️ المزيد", callback_data="more_2"))
        nav_buttons.append(InlineKeyboardButton("❌ إلغاء", callback_data="cancel"))
        keyboard.append(nav_buttons)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Store search context
        context.user_data['current_query'] = query
        context.user_data['current_page'] = 1
        
        await search_msg.edit_text(f"✨ اختر الأغنية المطلوبة:\n\n🎵 نتائج البحث عن: {query}", reply_markup=reply_markup)
        
    except Exception as e:
        await search_msg.edit_text(f"❌ حدث خطأ في البحث: {str(e)}")
        logger.error(f"Error in search: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "cancel":
        await query.edit_message_text("❌ تم إلغاء البحث.")
        return
    
    if data.startswith("more_"):
        page_num = int(data[5:])  # Remove "more_" prefix
        query_text = context.user_data.get('current_query', '')
        
        try:
            results = await search_youtube(query_text, page_num)
            
            if not results:
                await query.edit_message_text("❌ لا توجد نتائج إضافية.")
                return
            
            keyboard = []
            for result in results:
                video_id = result['id']
                title = result['title']
                duration = result.get('duration', 0)
                
                if duration > 0:
                    minutes = int(duration // 60)
                    seconds = int(duration % 60)
                    title_with_time = f"{title} ({minutes}:{seconds:02d})"
                else:
                    title_with_time = title
                
                if len(title_with_time) > 40:
                    title_with_time = title_with_time[:37] + "..."
                
                keyboard.append([InlineKeyboardButton(title_with_time, callback_data=f"play_{video_id}")])
            
            nav_buttons = []
            nav_buttons.append(InlineKeyboardButton("➡️ المزيد", callback_data=f"more_{page_num + 1}"))
            nav_buttons.append(InlineKeyboardButton("❌ إلغاء", callback_data="cancel"))
            keyboard.append(nav_buttons)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(f"✨ اختر الأغنية المطلوبة:\n\n🎵 نتائج إضافية عن: {query_text}", reply_markup=reply_markup)
            
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ في تحميل المزيد: {str(e)}")
        return
    
    if data.startswith("play_"):
        video_id = data[5:]  # Remove "play_" prefix
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Send initial message
        processing_msg = await query.edit_message_text("🎵 جاري التحميل... ⏳")
        
        try:
            # Download the audio
            audio_path = await download_audio(video_url)
            
            # Get the song title for caption
            audio_filename = os.path.basename(audio_path)
            # Remove datetime prefix from caption
            if "-" in audio_filename:
                title_only = "-".join(audio_filename.split("-")[1:])
                if title_only.endswith(".mp3"):
                    title_only = title_only[:-4]
            
            # Send the audio file
            await query.message.reply_audio(
                audio=open(audio_path, 'rb'),
                caption=f"✅ {title_only}"
            )
            
            # Delete the audio file after sending
            try:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                    logger.info(f"Deleted file: {audio_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {audio_path}: {e}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ حدث خطأ: {str(e)}")
            logger.error(f"Error in play callback: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    message = update.message
    
    if not message.text:
        await message.reply_text("أرسل رابط يوتيوب أو ساوندكلاود فقط.")
        return
    
    url = message.text.strip()
    
    # Check if it's a YouTube or SoundCloud URL
    if not ('youtube.com' in url or 'youtu.be' in url or 'soundcloud.com' in url):
        await message.reply_text("هذا الرابط مو من يوتيوب أو ساوندكلاود. أرسل رابط صحيح.")
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
    
    # Add handlers
    application.add_handler(CommandHandler("search", handle_search))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()