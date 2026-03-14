import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# التوكن الخاص بك
TOKEN = "8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8"

# إعدادات المحرك لضمان جودة عالية وتجاوز الحظر
YDL_OPTIONS = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "outtmpl": "downloads/%(title).50s_%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "merge_output_format": "mp4",
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    },
}

# دالة الترحيب عند الضغط على /start (تم إزالة قناة التحديثات)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name [cite: 1]
    
    welcome_text = (
        f"أهلاً بك يا {user_name}! ✨\n\n"
        "أنا بوت تحميل الوسائط الشامل. أرسل لي أي رابط من:\n"
        "• تيك توك (TikTok) 📱\n"
        "• إنستغرام (Instagram) 📸\n"
        "• يوتيوب (YouTube) 🎥\n"
        "• تويتر (X) 🐦\n\n"
        "وسأقوم بإرسال الفيديو لك مباشرة بجودة عالية."
    )
    
    # الإبقاء فقط على زر المطور @epr_a
    keyboard = [
        [InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/epr_a")] [cite: 1]
    ]
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text [cite: 1]
    status_msg = await update.message.reply_text("جاري التحميل... يرجى الانتظار ⏳") [cite: 1]

    if not os.path.exists("downloads"):
        os.makedirs("downloads") [cite: 1]

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True) [cite: 1]
            file_path = ydl.prepare_filename(info) [cite: 1]

        with open(file_path, "rb") as video:
            await update.message.reply_video(
                video=video, 
                caption=f"✅ **تم التحميل بنجاح!**\n\n📌: {info.get('title', 'فيديو')}",
                parse_mode="Markdown"
            ) [cite: 1]
        
        if os.path.exists(file_path):
            os.remove(file_path) [cite: 1]
        await status_msg.delete() [cite: 1]

    except Exception as e:
        await status_msg.edit_text(f"❌ **حدث خطأ:**\n`{str(e)[:100]}`", parse_mode="Markdown") [cite: 1]

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build() [cite: 1]
    
    app.add_handler(CommandHandler("start", start)) [cite: 1]
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video)) [cite: 1]
    
    print("Bot is running. Developer: @epr_a")
    app.run_polling() [cite: 1]
