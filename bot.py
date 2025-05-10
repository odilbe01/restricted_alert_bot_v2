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
    "EWR8": "AgACAgUAAxkBAAIBW2YcxaF",  # Example file_id
    "TUS2": "AgACAgUAAxkBAAIBXGYcxbbb",
    "CLT6": "AgACAgUAAxkBAAIBY2Ycyzxc"
    # Add your real file_ids here
}

# --- STORAGE ---
pending_notifications = {}  # msg_id: {"file_id": ..., "pu_time": ..., "chat_id": ...}
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

# --- HANDLERS ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption or update.message.text or ""
    pu_time = parse_pu_time(caption)
    if pu_time:
        pending_notifications[update.message.message_id] = {
            "file_id": update.message.photo[-1].file_id,
            "pu_time": pu_time,
            "chat_id": update.message.chat_id
        }
        await update.message.reply_text("✅ PU vaqti saqlandi. Endi vaqt yozing (masalan: 6h30m)")

async def handle_time_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper()

    # Restriction code bo‘lsa
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

    # PU notification bo‘lsa
    if not pending_notifications:
        return
    try:
        last_msg_id = max(pending_notifications.keys())
        info = pending_notifications[last_msg_id]
        file_id = info["file_id"]
        pu_time = info["pu_time"]
        chat_id = info["chat_id"]
        offset = parse_time_offset(text)
        notify_time = pu_time - offset - timedelta(minutes=10)

        def job():
            context.bot.send_photo(chat_id=chat_id, photo=file_id,
                                   caption="Reminder: Load approaching pickup time. Please be prepared.")

        scheduler.add_job(job, trigger='date', run_date=notify

