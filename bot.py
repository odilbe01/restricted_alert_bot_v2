import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

IMAGE_DIR = "images"

with open("image_keywords.json", "r") as f:
    KEYWORDS = json.load(f)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.upper().strip()

    for code, filename in KEYWORDS.items():
        if code in message_text:
            image_path = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img:
                    await update.message.reply_photo(photo=img)
                return

    await update.message.reply_text("🚫 No matching facility code found in your message.")

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)

    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 Bot started.")
    app.run_polling()
