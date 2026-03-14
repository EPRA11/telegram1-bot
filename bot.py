import os
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# بيانات البوت
TOKEN = "8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8"
ADMIN_ID = 35192892  # سيبقى معرفك كأدمن أساسي للإشعارات

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f: return json.load(f)
    return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f: json.dump(users, f)

# نص الترحيب الذي طلبته 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    
    welcome_text = (
        f"أهلاً بك يا {user.first_name}! ✨\n\n"
        "أنا بوت تحميل الوسائط الشامل. أرسل لي أي رابط من:\n"
        "• تيك توك (TikTok) 📱\n"
        "• إنستغرام (Instagram) 📸\n"
        "• يوتيوب (YouTube) 🎥\n"
        "• تويتر (X) 🐦\n\n"
        "وسأقوم بإرسال الفيديو لك مباشرة بجودة عالية."
    )
    
    keyboard = [[InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/epr_a")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

# نظام TXAdmin الخاص بك 
async def txadmin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    admin_text = (
        "⚙️ **لوحة تحكم TXAdmin**\n\n"
        f"📊 عدد المستخدمين النشطين: `{len(users)}` \n\n"
        "📜 **الأوامر المتاحة لك:**\n"
        "📢 لإرسال إعلان للكل: `/broadcast نص الرسالة` \n"
    )
    await update.message.reply_text(admin_text, parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ميزة الإذاعة تعمل فقط لمن يعرف الأمر
    msg_text = " ".join(context.args)
    if not msg_text:
        await update.message.reply_text("❌ اكتب الرسالة بعد الأمر.")
        return
    
    users = load_users()
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **إشعار إداري:**\n\n{msg_text}")
            count += 1
        except: continue
    await update.message.reply_text(f"✅ تم الإرسال إلى {count} مستخدم.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    # إشعار للمطور (اختياري)
    try: await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 طلب تحميل: {url}")
    except: pass

    status = await update.message.reply_text("جاري التحميل... ⏳")
    opts = {"format": "best", "quiet": True, "nocheckcertificate": True}
    
    try:
        if not os.path.exists("downloads"): os.makedirs("downloads")
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            path = ydl.prepare_filename(info)
        
        await update.message.reply_video(video=open(path, "rb"), caption="✅ تم التحميل!")
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ خطأ: {str(e)[:50]}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # تفعيل نظام TXAdmin بالأمر الذي اخترته 
    app.add_handler(CommandHandler("txadmin", txadmin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()
