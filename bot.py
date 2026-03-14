import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# جلب التوكن من متغيرات البيئة في Railway
TOKEN = os.getenv("BOT_TOKEN")

# دالة الترحيب عند إرسال أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 مرحباً بك في بوت تحميل الفيديوهات!\n\n"
        "🚀 يمكنك التحميل من مختلف المنصات (YouTube, TikTok, Instagram, X).\n"
        "✅ البوت مجاني بالكامل ويعمل بدون إعلانات مزعجة.\n\n"
        "فقط أرسل لي رابط الفيديو وسأقوم بتحميله لك فوراً."
    )
    keyboard = [[InlineKeyboardButton("قناة التحديثات 📢", url="https://t.me/YourChannel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    status_msg = await update.message.reply_text("جاري التحميل... يرجى الانتظار ⏳")

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

        with open(actual_filename, "rb") as f:
            await update.message.reply_video(video=f, caption="✅ تم التحميل بنجاح!")
        
        if os.path.exists(actual_filename):
            os.remove(actual_filename)
            
        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    print("Bot is running with Arabic Welcome Message...")
    app.run_polling()
