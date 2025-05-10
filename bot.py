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
    # Boshqa kodlar qo‘shing kerak bo‘lsa
}

scheduler = BackgroundScheduler()
scheduler.start()
logging.basicConfig(level=logging.INFO)

# --- PU Time Parse ---
def parse_pu_time(text):
    match = re.search(r'PU:\s*(.+?\d{2}:\d{2})\s+([A-Z]+)', text)
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
        logging.error(f"Failed to parse PU time: {e}")
        return None

# --- Offset Parse ---
def parse_time_offset(text):
    h = m = 0
    h_match = re.search(r"(\d+)h", text)
    m_match = re.search(r"(\d+)m", text)
    if h_match:
        h = int(h_match.group(1))
    if m_match:
        m = int(m_match.group(1))
    return timedelta(hours=h, minutes=m)

# --- Message Handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.caption or update.message.text or "").upper()
    chat_id = update.message.chat_id
    logging.info(f"Received message: {text}")

    # --- Restriction Check ---
    for code in RESTRICTION_CODES:
        if code in text:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=RESTRICTION_CODES[code],
                caption=(
                    f"🚫 *Restriction Alert: {code}*\n"
                    "Please check the restriction photo carefully. There might be no truck road or a no-parking zone.\n\n"
                    "Safe trips!"
                ),
                parse_mode='Markdown'
            )
            logging.info(f"[Restriction] Sent for {code} to {chat_id}")
            return

    # --- PU Notification Check ---
    pu_time = parse_pu_time(text)
    if pu_time:
        offset = parse_time_offset(text)
        if offset.total_seconds() > 0:
            notify_time = pu_time - offset - timedelta(minutes=10)
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
            else:
                await update.message.reply_text("❌ Rasm topilmadi. PU notification uchun rasm ham kerak.")
                return

            def job():
                try:
                    context.bot.send_photo(
                        chat_id=chat_id,
                        photo=file_id,
                        caption="Reminder: Load approaching pickup time. Please be prepared."
                    )
                    logging.info(f"[Reminder] Sent photo to {chat_id}")
                except Exception as e:
                    logging.error(f"[Reminder] Error sending photo: {e}")

            scheduler.add_job(job, trigger='date', run_date=notify_time)
            await update.message.reply_text(f"⏰ Reminder scheduled at {notify_time.strftime('%Y-%m-%d %H:%M %Z')}")
            logging.info(f"[Reminder] Scheduled for {notify_time} to {chat_id}")
        else:
            await update.message.reply_text("❌ '6h', '2h30m' kabi offset aniqlanmadi")
            logging.warning(f"[Reminder] Offset topilmadi in text: {text}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_message))

if __name__ == '__main__':
    print("🚛 Bot ishga tushdi")
    app.run_polling()
