import os
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

# بيانات البوت
TOKEN = "8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8"
ADMINS = [35192892] 

USERS_FILE = "users_data.json"
SETTINGS_FILE = "settings_data.json"

def load_data(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

all_users = load_data(USERS_FILE, [])
settings = load_data(SETTINGS_FILE, {"welcome": "أهلاً بك يا {name}! ✨\n\nأرسل لي رابطاً للتحميل."})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in all_users:
        all_users.append(user_id)
        save_data(USERS_FILE, all_users)
    welcome_text = settings["welcome"].replace("{name}", update.effective_user.first_name)
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/epr_a")]]))

async def txadmin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    keyboard = [[InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")], [InlineKeyboardButton("📝 تعديل الترحيب", callback_data="edit_welcome")]]
    await update.message.reply_text("⚙️ **TXAdmin**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- معالج التحميل الذكي ---
async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "tiktok.com" in url:
        # فحص الرابط إذا كان ألبوم صور
        status = await update.message.reply_text("جاري فحص محتوى تيك توك... 🔍")
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                
                # إذا كان المنشور يحتوي على عدة صور (Slideshow)
                if info.get('entries') or (info.get('formats') and not any('vcodec' in f and f['vcodec'] != 'none' for f in info['formats'])):
                    keyboard = [
                        [InlineKeyboardButton("🎬 فيديو (صور + موسيقى)", callback_data=f"dl_vid|{url}")],
                        [InlineKeyboardButton("🖼️ صور فقط (ألبوم)", callback_data=f"dl_img|{url}")]
                    ]
                    await status.edit_text("هذا المنشور يحتوي على صور، كيف تريد تحميله؟", reply_markup=InlineKeyboardMarkup(keyboard))
                    return
        except: pass
        await status.delete()

    # التحميل المباشر للروابط العادية (فيديو أو صورة واحدة)
    await process_download(update, context, url, mode="auto")

async def process_download(update_or_query, context, url, mode="auto"):
    # تحديد مكان إرسال الرسائل (سواء كان ضغطة زر أو رسالة عادية)
    chat_id = update_or_query.message.chat_id if hasattr(update_or_query, 'message') else update_or_query.chat_id
    status = await context.bot.send_message(chat_id=chat_id, text="جاري التحميل... ⏳")
    
    ydl_opts = {
        "format": "bestvideo+bestaudio/best" if mode != "img" else "best",
        "quiet": True, "nocheckcertificate": True, "outtmpl": "downloads/%(id)s.%(ext)s",
        "http_headers": {"User-Agent": "Mozilla/5.0"}
    }

    try:
        if not os.path.exists("downloads"): os.makedirs("downloads")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            
            if 'entries' in info: # معالجة ألبوم الصور
                media_group = []
                for entry in info['entries']:
                    path = ydl.prepare_filename(entry)
                    if mode == "img":
                        media_group.append(InputMediaPhoto(open(path, "rb")))
                if media_group:
                    await context.bot.send_media_group(chat_id=chat_id, media=media_group[:10]) # بحد أقصى 10 صور
            else:
                path = ydl.prepare_filename(info)
                if mode == "img" or info.get('ext') in ['jpg', 'png', 'webp']:
                    await context.bot.send_photo(chat_id=chat_id, photo=open(path, "rb"), caption="✅ تم تحميل الصورة")
                else:
                    await context.bot.send_video(chat_id=chat_id, video=open(path, "rb"), caption="✅ تم تحميل الفيديو")
                os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ فشل التحميل. تأكد أن الحساب عام.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if "|" in data:
        mode, url = data.split("|")
        mode_type = "vid" if mode == "dl_vid" else "img"
        await query.message.delete()
        await process_download(query, context, url, mode=mode_type)
    elif data == "stats":
        await query.edit_message_text(f"📊 عدد المستخدمين: `{len(all_users)}`", parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("txadmin", txadmin_panel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    app.run_polling()
