import os
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
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
settings = load_data(SETTINGS_FILE, {"welcome": "أهلاً بك يا {name}! ✨\n\nأرسل لي رابطاً من (TikTok, Instagram, YouTube, Pinterest, X) للتحميل."})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in all_users:
        all_users.append(user_id)
        save_data(USERS_FILE, all_users)
    
    welcome_text = settings["welcome"].replace("{name}", update.effective_user.first_name)
    keyboard = [[InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/epr_a")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- لوحة تحكم TXAdmin ---
async def txadmin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"), InlineKeyboardButton("📢 إذاعة", callback_data="bc_info")],
        [InlineKeyboardButton("📝 تعديل الترحيب", callback_data="edit_welcome")]
    ]
    await update.message.reply_text("⚙️ **لوحة تحكم TXAdmin**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "stats":
        await query.edit_message_text(f"📊 عدد المستخدمين النشطين: `{len(all_users)}`", parse_mode="Markdown")
    elif query.data == "bc_info":
        await query.edit_message_text("📢 أرسل: `/broadcast نص الرسالة` للإذاعة.")
    elif query.data == "edit_welcome":
        await query.edit_message_text("📝 أرسل: `/setwelcome النص` لتغيير الترحيب.")

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status = await update.message.reply_text("جاري معالجة الرابط... ⏳")
    
    # إعدادات متقدمة لدعم كافة المواقع بما فيها Pinterest
    ydl_opts = {
        "format": "best",
        "quiet": True,
        "nocheckcertificate": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    }

    try:
        if not os.path.exists("downloads"): os.makedirs("downloads")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            
            # معالجة الألبومات (عدة صور/فيديوهات)
            files_to_send = []
            if 'entries' in info:
                for entry in info['entries']:
                    files_to_send.append((ydl.prepare_filename(entry), entry.get('ext', '')))
            else:
                files_to_send.append((ydl.prepare_filename(info), info.get('ext', '')))

            for file_path, ext in files_to_send:
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    await update.message.reply_photo(photo=open(file_path, "rb"))
                else:
                    await update.message.reply_video(video=open(file_path, "rb"))
                os.remove(file_path)
            
            await status.delete()

    except Exception as e:
        await status.edit_text("❌ عذراً، لم أتمكن من تحميل هذا الرابط. تأكد أنه عام وليس خاصاً.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("txadmin", txadmin_panel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    app.run_polling()
