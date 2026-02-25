import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Token is fetched from Railway Environment Variables for security
TOKEN = os.getenv("BOT_TOKEN", "2127524069:AAGeFZw37aZoXpvTnXQf5zWgYcJRl5KrpjY")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    # Notify the user that the process has started
    status_msg = await update.message.reply_text("Downloading and processing your video... ⏳")

    # Setup download options with a unique filename per user
    file_template = f"video_{chat_id}.%(ext)s"

    ydl_opts = {
        "format": "best",
        "outtmpl": file_template,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            actual_filename = ydl.prepare_filename(info)

        # Send the video file to the user
        with open(actual_filename, "rb") as f:
            await update.message.reply_video(video=f, caption="✅ Downloaded successfully!")
        
        # Cleanup: Remove the file from the server immediately to save space
        if os.path.exists(actual_filename):
            os.remove(actual_filename)
            
        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    print("Bot is running...")
    app.run_polling()