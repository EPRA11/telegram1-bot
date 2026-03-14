import os
import yt_dlp
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# بيانات البوت الأساسية
TOKEN = "8644900793:AAE5CTvAJUz0YdO2HyRjVpID7XLf3ro_Uu8"
ADMIN_ID = 35192892  # معرفك الخاص للتحكم بالإدارة

# ملفات قاعدة البيانات البسيطة
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f: return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f)

# دالة الترحيب الأصلية التي طلبتها
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    banned_users = load_data(BANNED_FILE)
    
    if user.id in banned_users:
        await update.message.reply_text("❌ أنت محظور من استخدام هذا البوت.")
        return

    # حفظ المستخدم الجديد في القاعدة للإذاعة
    users = load_data(USERS_FILE)
    if user.id not in users:
        users.append(user.id)
        save_data(USERS_FILE, users)
        # إشعار للمطور بدخول شخص جديد
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🆕 مستخدم جديد انضم:\nالاسم: {user.first_name}\nID: `{user.id}`")

    # نص الترحيب الذي اخترته أنت
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

# لوحة تحكم الأدمن (تظهر لك فقط عند كتابة /admin)
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = load_data(USERS_FILE)
    banned = load_data(BANNED_FILE)
    admin_text = (
        "🛠 **لوحة تحكم المطور**\n\n"
        f"👥 إجمالي المستخدمين: `{len(users)}` \n"
        f"🚫 عدد المحظورين: `{len(banned)}` \n\n"
        "📢 للإذاعة: `/broadcast نص الرسالة` \n"
        "⛔ للحظر: `/ban ID_المستخدم` \n"
        "✅ لإلغاء الحظر: `/unban ID_المستخدم`"
    )
    await update.message.reply_text(admin_text, parse_mode="Markdown")

# ميزة الإذاعة (Broadcast)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("⚠️ اكتب نص الرسالة بعد الأمر.")
        return
    users = load_data(USERS_FILE)
    success = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **رسالة من الإدارة:**\n\n{text}", parse_mode="Markdown")
            success += 1
        except: continue
    await update.message.reply_text(f"✅ تم إرسال الرسالة إلى {success} مستخدم.")

# ميزة الحظر (Ban)
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        target_id = int(context.args[0])
        banned = load_data(BANNED_FILE)
        if target_id not in banned:
            banned.append(target_id)
            save_data(BANNED_FILE, banned)
            await update.message.reply_text(f"✅ تم حظر المستخدم `{target_id}` بنجاح.")
    except:
        await update.message.reply_text("⚠️ يرجى إدخال ID صحيح بعد الأمر.")

# ميزة التحميل الأساسية
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    banned_users = load_data(BANNED_FILE)
    if user.id in banned_users: return

    url = update.message.text
    # إرسال تقرير للمطور عن أي عملية تحميل
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 {user.first_name} يحاول تحميل:\n{url}")
    
    status = await update.message.reply_text("جاري التحميل... ⏳")
    opts = {
        "format": "best", "outtmpl": "downloads/%(id)s.%(ext)s", "quiet": True,
        "nocheckcertificate": True, "http_headers": {"User-Agent": "Mozilla/5.0"}
    }
    
    try:
        if not os.path.exists("downloads"): os.makedirs("downloads")
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            path = ydl.prepare_filename(info)
        
        await update.message.reply_video(video=open(path, "rb"), caption="✅ تم التحميل!")
        os.remove(path)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ حدث خطأ: {str(e)[:100]}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bot is fully updated with original welcome message!")
    app.run_polling()
