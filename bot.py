import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# التوكن الخاص بك
TOKEN = "8644900793:AAFyCWtc3QUp2wSW5oNQMYk2d7wOlqXGKFY"

# إعدادات متقدمة لتجاوز حظر إنستغرام والمنصات الأخرى
YDL_OPTIONS = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "outtmpl": "downloads/%(title).50s_%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "merge_output_format": "mp4",
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    },
    "geo_bypass": True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **أهلاً بك يا محمد في بوت تحميل الوسائط!**\n\n"
        "🚀 أرسل رابط الفيديو من (YouTube, TikTok, Instagram, X).\n"
        "✅ البوت سيعالج الرابط ويرسل الفيديو فوراً."
    )
    keyboard = [[InlineKeyboardButton("قناة التحديثات 📢", url="https://t.me/YourChannel")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status_msg = await update.message.reply_text("جاري التحميل... يرجى الانتظار ⏳")

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # استخراج المعلومات والتحميل في خيط منفصل لتجنب تعليق البوت
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            file_path = ydl.prepare_filename(info)

        with open(file_path, "rb") as video:
            await update.message.reply_video(
                video=video, 
                caption=f"✅ **تم التحميل بنجاح!**\n\n📌: {info.get('title', 'فيديو بدون عنوان')}",
                parse_mode="Markdown"
            )
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status_msg.delete()

    except Exception as e:
        # التعامل مع الخطأ وتنبيه المستخدم
        await status_msg.edit_text(f"❌ **حدث خطأ أثناء التحميل:**\n`{str(e)[:100]}`", parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("Bot is running...")
    app.run_polling()
