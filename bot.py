import os
import re
import glob
import asyncio
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)

TOKEN = os.getenv("8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8")

YDL_OPTIONS = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "outtmpl": "downloads/%(title).50s_%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "merge_output_format": "mp4",
    "geo_bypass": True,
    "noplaylist": True,
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 "
            "Mobile/15E148 Safari/604.1"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    },
}

URL_REGEX = re.compile(r"^https?://", re.IGNORECASE)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **أهلاً بك في بوت تحميل الوسائط!**\n\n"
        "أرسل رابط فيديو من:\n"
        "- YouTube\n"
        "- TikTok\n"
        "- Instagram\n"
        "- X\n\n"
        "وسيتم تحميله وإرساله لك إذا كان الرابط مدعوماً."
    )
    keyboard = [
        [InlineKeyboardButton("قناة التحديثات 📢", url="https://t.me/YourChannel")]
    ]
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


def extract_and_download(url: str):
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=True)

        video_id = info.get("id")
        if not video_id:
            raise Exception("تعذر الحصول على معرف الفيديو.")

        # نبحث عن الملف النهائي بعد التحميل/الدمج
        matches = glob.glob(f"downloads/*_{video_id}.*")
        if not matches:
            raise Exception("تم التحميل لكن لم يتم العثور على الملف النهائي.")

        # نأخذ أول ملف موجود
        return info, matches[0]


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()

    if not URL_REGEX.match(url):
        await update.message.reply_text("❌ أرسل رابط صحيح يبدأ بـ http أو https")
        return

    os.makedirs("downloads", exist_ok=True)

    status_msg = await update.message.reply_text("⏳ جاري التحميل، انتظر شوي...")

    try:
        info, file_path = await asyncio.to_thread(extract_and_download, url)

        title = info.get("title", "فيديو بدون عنوان")

        with open(file_path, "rb") as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=f"✅ **تم التحميل بنجاح**\n\n📌 **العنوان:** {title}",
                parse_mode="Markdown",
            )

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(
            f"❌ **حدث خطأ أثناء التحميل:**\n`{str(e)[:300]}`",
            parse_mode="Markdown",
        )

    finally:
        # تنظيف الملفات بعد الإرسال أو الخطأ
        try:
            for file in glob.glob("downloads/*"):
                if os.path.isfile(file):
                    os.remove(file)
        except Exception:
            pass


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
