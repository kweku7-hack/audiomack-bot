import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Get token from environment variable (SECURE!)
BOT_TOKEN = os.environ.get("8919834679:AAHU7g34JcTvGd3YA0R6tUoC-sCPI66MUBI")

class AudiomackDownloader:
    @staticmethod
    def download_song(url):
        """Download song using yt-dlp"""
        try:
            # Create downloads folder
            os.makedirs('downloads', exist_ok=True)
            
            # Download as MP3
            cmd = [
                'yt-dlp', 
                '-o', 'downloads/%(title)s.%(ext)s',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--no-warnings',
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            
            if result.returncode == 0 and os.listdir('downloads'):
                files = os.listdir('downloads')
                if files:
                    return os.path.join('downloads', files[0])
            return None
        except Exception as e:
            print(f"Download error: {e}")
            return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 *Audiomack Downloader Bot*\n\n"
        "Send me any Audiomack song link and I'll send you the MP3!\n\n"
        "Example: `https://audiomack.com/artist/song`\n\n"
        "⚠️ Only download content you have permission to use.",
        parse_mode='Markdown'
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if 'audiomack.com' not in url:
        await update.message.reply_text("❌ Please send a valid Audiomack URL")
        return
    
    msg = await update.message.reply_text("🎵 Processing your request...")
    
    try:
        # Get song title
        title_cmd = ['yt-dlp', '--get-title', '--no-warnings', url]
        title_result = subprocess.run(title_cmd, capture_output=True, text=True, timeout=30)
        song_title = title_result.stdout.strip() if title_result.returncode == 0 else "Audiomack Song"
        
        await msg.edit_text(f"📥 Downloading: *{song_title}*", parse_mode='Markdown')
        
        # Download
        downloader = AudiomackDownloader()
        file_path = downloader.download_song(url)
        
        if file_path and os.path.exists(file_path):
            await msg.edit_text("📤 Uploading to Telegram...")
            
            # Send audio
            with open(file_path, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    title=song_title[:50],
                    performer="Audiomack"
                )
            
            # Cleanup
            os.remove(file_path)
            await msg.delete()
        else:
            await msg.edit_text("❌ Download failed. Song might be restricted or invalid.")
            
    except subprocess.TimeoutExpired:
        await msg.edit_text("⏰ Timeout! Try a shorter song or different link.")
    except Exception as e:
        print(f"Error: {e}")
        await msg.edit_text("❌ An error occurred. Please try again.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *How to use:*\n"
        "1. Get an Audiomack song URL\n"
        "2. Paste it here\n"
        "3. Receive your MP3!\n\n"
        "Commands:\n"
        "/start - Start bot\n"
        "/help - Show this help",
        parse_mode='Markdown'
    )

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN environment variable not set!")
        return
    
    os.makedirs('downloads', exist_ok=True)
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    print("🤖 Bot is running on Render...")
    app.run_polling()

if __name__ == '__main__':
    main()
