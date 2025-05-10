import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
import re

# --- CONFIG ---
BOT_TOKEN = "8160467333:AAHpITVdypiM7Qa70jbtQfRE9bwdraB4trQ"
TIMEZONE_MAP = {
    'PDT': 'America/Los_Angeles',
    'PST': 'America/Los_Angeles',
    'EDT': 'America/New_York',
    'EST': 'America/New_York',
    'CDT': 'America/Chicago',
    'CST': 'America/Chicago',
}

RESTRICTION_CODES = {
    "EWR8": "AgACAgUAAxkBAAIBW2YcxaF",
    "TUS2": "AgACAgUAAxkBAAIBXGYcxbbb",
    "CLT6": "AgACAgUAAxkBAAIBY2Ycyzxc"
    # Real file_id'larni shu yerga yozasiz
}

# --- STORAGE ---
scheduler = BackgroundScheduler()
scheduler.start()

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)

# --- UTILITY FUNCTIONS ---
def parse_pu_time(text):
    match = re.search(r'PU:\s*(.+\d{2}:\d{2})\s+([A-Z]+)', text)
    if not match:
        return None
    datetime_str, tz_abbr = match.groups()
    try:
        full_datetime_str = f"{datetime.now().year} {datetime_str}"
        dt = datetime.strptime(full_datetime_str, "%Y %a %b %d %H:%M")
        tz_name = TIMEZONE_MAP.get(tz_abbr)
        if not tz_name:
            return None
        tz = pytz.timezone(tz_name)
        return tz.localize(dt)
    except Exception as e:
        print("Failed to parse PU time:", e)
        return None

def parse_time_offset(text):
    h = m = 0
    h_match = re.search(r"(\d+)h", text)
    m_match = re.search(r"(\d+)m", text)
    if h_match:
        h = int(h_match.group(1))
    if m_match:
        m = int(m_match.group(1))
    return timedelta(hours=h, minutes=m)

# --- HANDLER ---
async def handle_text_or_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.caption or update.message.text or "").upper()

    # Restriction check
    for code in RESTRICTION_CODES:
        if code in text:
            await context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=RESTRICTION_CODES[code],
                caption=(
                    f"🚫 *Restriction Alert: {code}*\n"
                    "Please check the restriction photo carefully. There might be no truck road or a no-parking zone.\n\n"
                    "Safe trips!"
                ),
                parse_mode='Markdown'
            )
            return

    # PU notification check
    pu_time = parse_pu_time(text)
    if pu_time:
        offset = parse_time_offset(text)
        if offset.total_seconds() > 0:
            notify_time = pu_time - offset - timedelta(minutes=10)
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
            else:
                await update.message.reply_text("❌ Rasm topilmadi")
                return

            def job():
                context.bot.send_photo(
                    chat_id=update.message.chat_id,
                    photo=file_id,
                    caption="Reminder: Load approaching pickup time. Please be prepared."
                )

            scheduler.add_job(job, trigger='date', run_date=notify_time)
            await update.message.reply_text(f"⏰ Reminder scheduled at {notify_time.strftime('%Y-%m-%d %H:%M %Z')}")
        else:
            await update.message.reply_text("❌ Soat formati topilmadi. Masalan: 6h yoki 2h30m yozing.")

# --- MAIN ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_text_or_photo))

if __name__ == '__main__':
    print("🚛 Bot started.")
    app.run_polling()

