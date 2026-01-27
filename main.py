import os
import sqlite3
import yt_dlp
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. إعداد سيرفر وهمي لإبقاء البوت حياً على Render ---
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- 2. إعداد قاعدة البيانات ---
def init_db():
    try:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
        conn.commit()
        conn.close()
    except: pass

# --- 3. قاموس الردود الذكية ---
QUICK_REPLIES = {
    "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته، نورت البوت! 🌹",
    "مرحبا": "أهلاً بك يا غالي، كيف أقدر أساعدك اليوم؟ ✨",
    "من انت": "أنا بوتك الشخصي للبحث عن الشيلات، الزوامل، والقرآن. 🎤",
    "كيف حالك": "الحمد لله بنعمة، أتمنى أن تكون أنت بخير أيضاً! ❤️"
}

# --- 4. وظيفة التحميل من يوتيوب ---
async def download_audio(update: Update, query: str):
    msg = await update.message.reply_text(f"⏳ جاري البحث والتحميل: {query}...")
    file_name = f"audio_{update.message.message_id}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1',
        'outtmpl': file_name,
        'quiet': True,
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [f"ytsearch1:{query}"])
            
        if os.path.exists(file_name):
            await update.message.reply_audio(audio=open(file_name, 'rb'), caption=f"✅ تم تحميل: {query}")
            os.remove(file_name)
        else:
            await update.message.reply_text("❌ تعذر العثور على الملف.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ: {str(e)[:50]}")
    finally:
        await msg.delete()

# --- 5. معالج الرسائل ---
async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip()

    if text in QUICK_REPLIES:
        await update.message.reply_text(QUICK_REPLIES[text])
        return

    search_keywords = ["بحث شيله", "بحث شيلة", "بحث زامل", "بحث قرآن"]
    for kw in search_keywords:
        if text.startswith(kw):
            query = text.replace(kw, "").strip()
            if query:
                await download_audio(update, query)
            return

# --- 6. تشغيل البوت ---
if __name__ == '__main__':
    init_db()
    # تشغيل السيرفر الوهمي في خلفية الكود
    keep_alive() 
    
    TOKEN = " 7955939093:AAEd2E68oukep9XzmNa_QZGAF3PfY-rL298 "
    
    app_telegram = Application.builder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("البوت متصل ويعمل!")))
    app_telegram.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), main_handler))
    
    print("البوت يعمل الآن...")
    app_telegram.run_polling()
