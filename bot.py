import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# ملاحظة: استبدل هذا التوكن بالجديد إذا قمت بعمل Revoke
TOKEN = "8644900793:AAFyCWtc3QUp2wSW5oNQMYk2d7wOlqXGKFY"

# إعدادات متقدمة للمحرك yt-dlp لضمان جودة عالية ودعم كافة المواقع
YDL_OPTIONS = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "outtmpl": "downloads/%(title).50s_%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "merge_output_format": "mp4",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **أهلاً بك في بوت تحميل الوسائط الشامل!**\n\n"
        "🚀 أرسل رابط الفيديو من (YouTube, TikTok, Instagram, X).\n"
        "✅ البوت سيقوم بالتحميل وإرساله لك كملف فيديو مباشر."
    )
    # رابط قناة التحديثات الخاص بك (اختياري)
    keyboard = [[InlineKeyboardButton("قناة المطور 📢", url="https://t.me/YourChannel")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    # رسالة مؤقتة لتنبيه المستخدم
    status_msg = await update.message.reply_text("جاري معالجة الرابط... يرجى الانتظار ⏳")

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # استخراج المعلومات والتحميل (استخدام asyncio لعدم تجميد البوت)
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            file_path = ydl.prepare_filename(info)

        # إرسال الفيديو للمستخدم
        with open(file_path, "rb") as video:
            await update.message.reply_video(
                video=video, 
                caption=f"✅ **تم التحميل بنجاح!**\n\n📌: {info.get('title', 'فيديو بدون عنوان')}",
                parse_mode="Markdown"
            )
        
        # تنظيف الخادم: حذف الملف بعد إرساله لتوفير المساحة
        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status_msg.delete()

    except Exception as e:
        # في حال حدوث خطأ، نقوم بتحديث رسالة الحالة بدلاً من إرسال رسالة جديدة
        await status_msg.edit_text(f"❌ **عذراً، حدث خطأ أثناء التحميل:**\n`{str(e)[:100]}`", parse_mode="Markdown")

if __name__ == "__main__":
    # تشغيل البوت
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("Bot is starting... Press Ctrl+C to stop.")
    app.run_polling()
