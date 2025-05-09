import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Ruxsat berilgan guruhlar ro‘yxati
ALLOWED_CHAT_IDS = [-1001234567890, -1009876543210]  # <-- bu yerga ruxsatli chat ID larni yozing

# Rasm katalogi
IMAGE_DIR = "images"

# Kalit so‘zlar (kodlar) va fayllarni yuklash
with open("image_keywords.json", "r") as f:
    KEYWORDS = json.load(f)

# Foydalanuvchi xabarini qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"Chat ID: {chat_id}")

    # Faqat ruxsat berilgan chatlar ishlata oladi
    if chat_id not in ALLOWED_CHAT_IDS:
        return

    message_text = update.message.text.upper().strip()
    matched = False

    for code, filename in KEYWORDS.items():
        if code in message_text:
            image_path = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(image_path):
                with open(image_path, "rb") as img:
                    await update.message.reply_photo(photo=img)
                    matched = True

    # Hech biri mos kelmasa – javob yozmaydi
    if not matched:
        return

# Dastur ishga tushiriladi
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 Bot started.")
    app.run_polling()

