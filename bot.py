import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = os.environ["8644900793:AAHWmsD6ZdIWDYl8hi8uQS7wYJxxIrHVWOw"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً! أنا بوت تحميل الفيديوهات\n\n"
        "📥 أرسل لي رابط من:\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Instagram\n"
        "• X (Twitter)\n\n"
        "وسأحمله لك فوراً! 🚀"
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    filename = f"video_{chat_id}.%(ext)s"

    status = await update.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {
        "format": "best",
        "outtmpl": filename,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        with open(file_path, "rb") as f:
            await update.message.reply_video(video=f, caption="✅ تم التحميل!")

        os.remove(file_path)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ فشل التحميل:\n{str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    print("✅ Bot is running...")
    app.run_polling()
