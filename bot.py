import os
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    keyboard = [[InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")]]
    await update.message.reply_text("⚙️ **TXAdmin**", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "stats":
        await query.edit_message_text(f"📊 عدد المستخدمين: `{len(all_users)}`")

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status = await update.message.reply_text("جاري التحميل... ⏳")
    
    ydl_opts = {
        "format": "best", 
        "quiet": True, 
        "nocheckcertificate": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "http_headers": {"User-Agent": "Mozilla/5.0"}
    }

    try:
        if not os.path.exists("downloads"): os.makedirs("downloads")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            path = ydl.prepare_filename(info)
            
            if info.get('ext') in ['jpg', 'png', 'webp']:
                await update.message.reply_photo(photo=open(path, "rb"))
            else:
                await update.message.reply_video(video=open(path, "rb"))
            os.remove(path)
        await status.delete()
    except Exception as e:
        # هنا غيرنا الرسالة لتكون أدق
        await status.edit_text("❌ فشل التحميل. قد يكون الرابط تالفاً أو يحتاج البوت لتحديث.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("txadmin", txadmin_panel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    app.run_polling()
