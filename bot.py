import os
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

# بيانات البوت
TOKEN = "8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8"
ADMINS = [35192892]  # أضف أي ID أدمن جديد هنا داخل القائمة

# ملفات تخزين البيانات (لضمان عدم ضياع الإحصائيات)
USERS_FILE = "users_data.json"
SETTINGS_FILE = "settings_data.json"

def load_data(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if data else default
    except: pass
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تحميل الإحصائيات والترحيب
all_users = load_data(USERS_FILE, [])
settings = load_data(SETTINGS_FILE, {"welcome": "أهلاً بك يا {name}! أرسل الرابط للتحميل."})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # تسجيل المستخدم إذا كان جديداً لزيادة العدد
    if user_id not in all_users:
        all_users.append(user_id)
        save_data(USERS_FILE, all_users)
    
    welcome_text = settings["welcome"].replace("{name}", user_name)
    keyboard = [[InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/epr_a")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def txadmin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # لا يفتح إلا للأدمنية
    if update.effective_user.id not in ADMINS:
        return

    keyboard = [
        [InlineKeyboardButton("📊 عدد المستخدمين", callback_data="stats")],
        [InlineKeyboardButton("📢 إرسال إذاعة", callback_data="broadcast_info")],
        [InlineKeyboardButton("📝 تعديل الترحيب", callback_data="edit_welcome")]
    ]
    await update.message.reply_text("🎮 **لوحة تحكم TXAdmin**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id not in ADMINS:
        await query.answer("ليس لديك صلاحية!", show_alert=True)
        return

    await query.answer()
    
    if query.data == "stats":
        current_users = load_data(USERS_FILE, [])
        await query.edit_message_text(f"📊 **إحصائيات مباشرة:**\n\nعدد المستخدمين المسجلين: `{len(current_users)}`", parse_mode="Markdown")
    
    elif query.data == "broadcast_info":
        await query.edit_message_text("📢 **طريقة الإذاعة:**\nأرسل الأمر التالي:\n`/broadcast نص الرسالة`", parse_mode="Markdown")
        
    elif query.data == "edit_welcome":
        await query.edit_message_text("📝 **تعديل الترحيب:**\nأرسل الأمر التالي:\n`/setwelcome النص الجديد`", parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("❌ اكتب نص الرسالة!")
        return
    
    users = load_data(USERS_FILE, [])
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **إشعار إداري:**\n\n{msg}")
            count += 1
        except: continue
    await update.message.reply_text(f"✅ تم الإرسال إلى {count} مستخدم.")

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS: return
    new_text = " ".join(context.args)
    if not new_text:
        await update.message.reply_text("❌ أرسل النص الجديد بعد الأمر!")
        return
    settings["welcome"] = new_text
    save_data(SETTINGS_FILE, settings)
    await update.message.reply_text("✅ تم تحديث كليشة الترحيب بنجاح!")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status = await update.message.reply_text("جاري التحميل... ⏳")
    
    ydl_opts = {"format": "best", "quiet": True, "nocheckcertificate": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            path = ydl.prepare_filename(info)
        await update.message.reply_video(video=open(path, "rb"), caption="✅ تم التحميل بنجاح!")
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ فشل التحميل. تأكد من الرابط.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("txadmin", txadmin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    app.add_handler(CallbackQueryHandler(handle_callback)) # المعالج الذي كان ينقصك
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("TXAdmin is Online!")
    app.run_polling()
