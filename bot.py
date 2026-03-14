import os
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = "8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8"
ADMIN_ID = 35192892  # معرفك الخاص لضمان صلاحيات الإدارة

# ملف بسيط لحفظ المستخدمين
DB_FILE = "users.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(DB_FILE, "w") as f: json.dump(users, f)

YDL_OPTIONS = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "outtmpl": "downloads/%(title).50s_%(id)s.%(ext)s",
    "quiet": True, "no_warnings": True, "nocheckcertificate": True, "merge_output_format": "mp4",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id) # حفظ المستخدم في القاعدة
    
    welcome_text = f"أهلاً بك يا {user.first_name}! ✨\nأرسل لي أي رابط وسأقوم بتحميله لك."
    keyboard = [[InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/epr_a")]]
    
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    # إشعار للمطور بدخول شخص جديد
    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"👤 مستخدم جديد: {user.first_name}\nID: `{user.id}`")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    users = load_users()
    stats_text = f"🛠 **لوحة تحكم الإدارة**\n\n👥 عدد المستخدمين: {len(users)}\n\nللإذاعة استخدم: `/broadcast نص الرسالة`"
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    msg_text = " ".join(context.args)
    if not msg_text:
        await update.message.reply_text("❌ يرجى كتابة نص الإذاعة بعد الأمر.")
        return
    
    users = load_users()
    count = 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 **إعلان من الإدارة:**\n\n{msg_text}", parse_mode="Markdown")
            count += 1
        except: pass
    
    await update.message.reply_text(f"✅ تم إرسال الإذاعة إلى {count} مستخدم.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    # تقرير التحميل للمطور
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 طلب تحميل من {update.effective_user.first_name}:\n{url}")
    
    status_msg = await update.message.reply_text("جاري التحميل... ⏳")
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            file_path = ydl.prepare_filename(info)
        with open(file_path, "rb") as video:
            await update.message.reply_video(video=video, caption=f"✅ {info.get('title', 'فيديو')}")
        os.remove(file_path)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ: {str(e)[:100]}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()
