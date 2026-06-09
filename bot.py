import os
import re
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

# بيانات البوت (يقرأ التوكن تلقائياً من إعدادات Render لحمايته)
TOKEN = os.getenv("8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8")
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
settings = load_data(SETTINGS_FILE, {"welcome": "أهلاً بك يا {name}! ✨\n\nأرسل لي رابطاً من (تيك توك، إنستا، يوتيوب) للتحميل فوراً."})

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
    text_received = update.message.text
    
    # استخراج الرابط فقط من النص (حتى لو كان معه كابشن أو هاشتاغات مثل المثال اللي رسلته)
    url_match = re.search(r'(https?://\S+)', text_received)
    if not url_match:
        await update.message.reply_text("❌ عذراً، لم أجد رابطاً صالحاً في رسالتك.")
        return
        
    url = url_match.group(1)
    status = await update.message.reply_text("جاري المعالجة والتحميل بأقصى سرعة... ⚡")
    
    # إعدادات متقدمة جداً لتسريع التحميل ودعم تيك توك وإنستغرام بدون حظر
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", # اختيار صيغ سريعة الدمج
        "quiet": True, 
        "nocheckcertificate": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "concurrent_fragment_downloads": 5, # تحميل 5 أجزاء من الفيديو في نفس الوقت لتسريع خارق
        "socket_timeout": 15,
        "retries": 3,
        "extractor_args": {
            "instagram": {"skip": ["api"]}, # تسريع روابط إنستغرام
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    }

    try:
        if not os.path.exists("downloads"): os.makedirs("downloads")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # التحميل في خلفية منفصلة لعدم تجميد البوت
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            path = ydl.prepare_filename(info)
            
            # التأكد من الصيغة لإرسالها بشكل صحيح
            ext = info.get('ext', '').lower()
            if ext in ['jpg', 'png', 'webp', 'jpeg']:
                await update.message.reply_photo(photo=open(path, "rb"), caption="تم التحميل بواسطة بوتك 🎬")
            else:
                await update.message.reply_video(video=open(path, "rb"), caption="تم التحميل بواسطة بوتك 🎬")
                
            # تنظيف السيرفر وحذف الملف بعد الإرسال فوراً
            if os.path.exists(path):
                os.remove(path)
                
        await status.delete()
    except Exception as e:
        print(f"Error: {e}") # لطباعة الخطأ في لوحة تحكم Render إذا حدثت مشكلة
        await status.edit_text("❌ فشل التحميل! تأكد أن الحساب ليس خاصاً (Private) أو حاول مجدداً لاحقاً.")

if __name__ == "__main__":
    if not TOKEN:
        print("⚠️ خطأ: لم يتم العثور على BOT_TOKEN في إعدادات البيئة (Environment Variables)!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("txadmin", txadmin_panel))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
        app.run_polling()
