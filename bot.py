import os
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

# بيانات البوت
TOKEN = "8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8"
ADMIN_ID = 35192892 

# ملفات تخزين البيانات
USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json"

def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)

# تحميل الإعدادات (نص الترحيب الافتراضي)
default_welcome = "أهلاً بك! أرسل لي رابطاً للتحميل."
settings = load_data(SETTINGS_FILE, {"welcome_msg": default_welcome})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_data(USERS_FILE, [])
    if user.id not in users:
        users.append(user.id)
        save_data(USERS_FILE, users)
    
    # استخدام النص المخزن في الإعدادات
    welcome_text = settings.get("welcome_msg", default_welcome).replace("{name}", user.first_name)
    keyboard = [[InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/epr_a")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def txadmin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # صلاحية الدخول لـ txadmin
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"), InlineKeyboardButton("📢 إذاعة", callback_data="broadcast")],
        [InlineKeyboardButton("📝 تعديل الترحيب", callback_data="edit_welcome")],
        [InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="list_users")]
    ]
    await update.message.reply_text("🎮 **TXAdmin Control Panel**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    users = load_data(USERS_FILE, [])

    if query.data == "stats":
        await query.edit_message_text(f"📊 عدد المستخدمين الحالي: `{len(users)}`", parse_mode="Markdown")
    
    elif query.data == "edit_welcome":
        await query.edit_message_text("📝 لتغيير الترحيب، أرسل الأمر:\n`/setwelcome نص الترحيب الجديد` \n\n(ملاحظة: استخدم {name} لوضع اسم المستخدم تلقائياً)")

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_msg = " ".join(context.args)
    if not new_msg:
        await update.message.reply_text("⚠️ يرجى كتابة النص الجديد بعد الأمر.")
        return
    settings["welcome_msg"] = new_msg
    save_data(SETTINGS_FILE, settings)
    await update.message.reply_text("✅ تم تحديث كليشة الترحيب بنجاح!")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = " ".join(context.args)
    if not msg: return
    users = load_data(USERS_FILE, [])
    for uid in users:
        try: await context.bot.send_message(chat_id=uid, text=msg)
        except: continue
    await update.message.reply_text("✅ تم الإرسال للجميع.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status = await update.message.reply_text("جاري المعالجة... ⏳")
    try:
        with yt_dlp.YoutubeDL({"format": "best", "quiet": True}) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            path = ydl.prepare_filename(info)
        await update.message.reply_video(video=open(path, "rb"), caption="✅ تم!")
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ خطأ: {str(e)[:50]}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("txadmin", txadmin_panel))
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()
