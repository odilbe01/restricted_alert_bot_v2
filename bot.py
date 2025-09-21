import os
import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

RESTRICTION_CODES = {
    "EWR8": "EWR8.jpg", "HLA2": "HLA2.jpg", "OWD5": "OWD5.jpg", "CLT2": "CLT2.jpg", "GRR1": "GRR1.jpg",
    "HEA2": "HEA2.jpg", "HMK3": "HMK3.jpg", "DWA5": "DWA5.jpg", "LGA5": "LGA5.jpg", "RFD2": "RFD2.jpg",
    "MEM5": "MEM5.jpg", "PHL5": "PHL5.jpg", "YHM1": "YHM1.jpg", "MKY1": "MKY1.jpg", "CHO1": "CHO1.jpg",
    "DTW3": "DTW3.jpg", "HRD2": "HRD2.jpg", "IND9": "IND9.jpg", "MCI5": "MCI5.jpg", "DTW9": "DTW9.jpg",
    "CDW5": "CDW5.jpg", "OXR1": "OXR1.jpg", "OWD9": "OWD9.jpg", "BNA7": "BNA7.jpg", "DET6": "DET6.jpg",
    "JAN1": "JAN1.jpg", "MSP8": "MSP8.jpg", "IND5": "IND5.jpg", "LBE1": "LBE1.jpg", "RDU1": "RDU1.jpg",
    "MCI9": "MCI9.jpg", "TYS1": "TYS1.jpg", "BOS4": "BOS4.jpg", "PPO4": "PPO4.jpg", "CLT9": "CLT9.jpg",
    "RNO4": "RNO4.jpg", "DSM4": "DSM4.jpg", "RDU2": "RDU2.jpg", "HNE1": "HNE1.jpg", "BNA5": "BNA5.jpg",
    "DXC3": "DXC3.jpg", "FTW6": "FTW6.jpg", "CMH1": "CMH1.jpg", "LDJ5": "LDJ5.jpg", "DTW1": "DTW1.jpg",
    "FTW2": "FTW2.jpg", "SYR1": "SYR1.jpg", "LIT1": "LIT1.jpg", "LAN2": "LAN2.jpg", "MGEY": "MGEY.jpg",
    "DTW5": "DTW5.jpg", "MTN6": "MTN6.jpg", "JFK8": "JFK8.jpg", "RIC4": "RIC4.jpg", "CLT6": "CLT6.jpg",
    "VGA1": "VGA1.jpg", "ACY2": "ACY2.jpg", "MTN1": "MTN1.jpg", "MOB5": "MOB5.jpg", "MCO2": "MCO2.jpg",
    "ABE3": "ABE3.jpg", "ORF2": "ORF2.jpg", "FTW1": "FTW1.jpg", "EWR4": "EWR4.jpg", "ILG1": "ILG1.jpg",
    "CLE2": "CLE2.jpg", "XLA4": "XLA4.jpg", "SGA1": "SGA1.jpg", "DEN4": "DEN4.jpg", "SBD6": "SBD6.jpg",
    "LGA9": "LGA9.jpg", "DNJ2": "DNJ2.jpg", "BOS3": "BOS3.jpg", "MDT5": "MDT5.jpg", "VCB3": "VCB3.jpg",
    "ORF3": "ORF3.jpg", "HOU1": "HOU1.jpg", "ABE8": "ABE8.jpg", "PNE5": "PNE5.jpg", "SWF2": "SWF2.jpg",
    "MKE2": "MKE2.jpg", "RFD4": "RFD4.jpg", "MEM4": "MEM4.jpg", "LUK2": "LUK2.jpg", "DIN4": "DIN4.jpg",
    "MTN2": "MTN2.jpg", "TYS5": "TYS5.jpg", "MCO5": "MCO5.jpg", "AFW5": "AFW5.jpg", "AUS2": "AUS2.jpg",
    "MQY1": "MQY1.jpg", "RBD5": "RBD5.jpg", "CMH7": "CMH7.jpg","JAX3": "JAX3.jpg",
}

# --- TEXTS ---
SAFETY_TEXT = (
    "Dear Drivers,\n\n"
    "When arriving at the facility, please comply with all yard rules:\n\n"
    "- Speed: Max 5 mph inside the yard; take all turns slowly.\n"
    "- Maneuvers: No sharp turns or other risky actions.\n"
    "- Distractions: No phone use; no headphones while driving.\n\n"
    "Please remember the rest of the posted yard rules as well. "
    "These reminders are part of our job—and they keep everyone safe."
)

# 🗺 + 𝗧𝗿𝗶𝗽 + 𝗜𝗗 (ixtiyoriy bo'shliqlar, ixtiyoriy ":")
TRIP_PIN_TRIGGER = re.compile(r'(?:^|\n)\s*🗺\s*𝗧𝗿𝗶𝗽\s*𝗜𝗗\s*:?\s*', re.UNICODE)

# --- NEW: trigger for updater message ---
# OLD:
# SEND_IT_TRIGGER = re.compile(r'@David_updaterbot\s+send it', re.IGNORECASE)

# NEW:
SEND_IT_TRIGGER = re.compile(r'\bSend it david\b', re.IGNORECASE)

# --- NEW: texts for updater flow ---
UPD_TEXT_1 = (
    "Dear Driver,\n\n"
    "Please be informed that the Amazon Relay app navigation must be used at all times during each stop and throughout your trips. "
    "You are required to check in and check out with the app, otherwise, it affects the company's performance. "
    "Ensure you are punctual for pickups and deliveries and inform us in the the group if you encounter any issues. "
    "Failure to do so may result in charges. Please read this message and confirm your receipt."
)

UPD_TEXT_2 = (
    "Attention⚠️\n\n"
    "For android\n"
    "(https://play.google.com/store/apps/details?id=com.jeyluta.timestampcamerafree&hl=en_US&gl=US&pli=1)\n"
    "For IOS (https://apps.apple.com/us/app/timestamp-camera-basic/id840110184)\n\n"
    "Google Play (https://play.google.com/store/apps/details?id=com.jeyluta.timestampcamerafree&hl=en_US&gl=US&pli=1)\n"
    "Timestamp Camera - Apps on Google Play\n"
    "Add date and time watermark to photos and videos"
)

UPD_TEXT_3_REPLY = (
    "Dear Driver,\n\n"
    "Please use the Timestamps app when sending photos for update of pick-ups, drop trailers, traffic, etc. "
    "This will help us provide evidence to Amazon.\n\n"
    "Thank you for your help!"
)

UPD_TEXT_4 = (
    "📌 Late PU: $500 \n"
    "📌 Late DEL: $500\n"
    "📌 No App Usage: $500\n"
    "📌 No Update: $200\n"
    "📌 No Trailer pictures, Seal and BOL: $300\n"
    "📌 Rejection: $1000\n"
    "📌 Restricted Road: $5000\n\n"
    "‼️ Please check in at the gate 20-30 min earlier to prevent any unforeseen circumstances at the gate.\n\n"
    "‼️  Always use amazon navigation on your relay acc"
)

UPD_TEXT_5 = (
    "Dear drivers when you get check in /out at amazon guard shack please send pictures of the guard screen in this order "
    "to avoid any kind of misunderstandings and problems with amazon check in/out timestamps. "
    "We kindly ask you to respect and follow company rules."
)

# --- NEW: images for the last step (change paths if needed) ---
IMG1_PATH = os.getenv("IMG1_PATH", "images/checkin_complete.jpg")
IMG2_PATH = os.getenv("IMG2_PATH", "images/checkout_complete.jpg")

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)


# --- HANDLER ---
async def handle_restriction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    raw_text = (msg.caption or msg.text or "")

    # Botlarning xabarlariga javob bermaslik
    if msg.from_user and msg.from_user.is_bot:
        return

    logging.info(f"Received: {raw_text}")

    # --- NEW: @David_updaterbot send it flow ---
    if SEND_IT_TRIGGER.search(raw_text):
        m1 = await msg.reply_text(UPD_TEXT_1)
        m2 = await msg.reply_text(UPD_TEXT_2)
        await msg.reply_text(UPD_TEXT_3_REPLY, reply_to_message_id=m2.message_id)
        await msg.reply_text(UPD_TEXT_4)
        m5 = await msg.reply_text(UPD_TEXT_5)

        # send two images (if present)
        try:
            if os.path.exists(IMG1_PATH):
                with open(IMG1_PATH, "rb") as f1:
                    await context.bot.send_photo(chat_id=msg.chat_id, photo=f1)
            else:
                logging.warning(f"Image not found: {IMG1_PATH}")
            if os.path.exists(IMG2_PATH):
                with open(IMG2_PATH, "rb") as f2:
                    await context.bot.send_photo(chat_id=msg.chat_id, photo=f2)
            else:
                logging.warning(f"Image not found: {IMG2_PATH}")
        except Exception as e:
            logging.warning(f"Sending images failed: {e}")
        # davom ettirish shart emas, lekin qolgan matchinglar ta’sir qilmasligi uchun return qilamiz
        return
    # --- NEW END ---

    # 1) "🗺𝗧𝗿𝗶𝗽 𝗜𝗗" trigger bo'lsa — safety reply + PIN
    if TRIP_PIN_TRIGGER.search(raw_text):
        await msg.reply_text(SAFETY_TEXT, disable_web_page_preview=True)

        # --- ADDED: Xabarni pin qilish (admin ruxsat kerak) ---
        try:
            # PTB v20: Message.pin() mavjud; bildirishnomasiz pinlaymiz
            await msg.pin(disable_notification=True)
        except Exception as e:
            logging.warning(f"Pin failed (probably missing permission): {e}")
        # --- ADDED END ---

    # 2) Restriction kodlari bo'yicha rasm yuborish
    text_upper = raw_text.upper()
    matched = False
    for code, filename in RESTRICTION_CODES.items():
        if code in text_upper:
            matched = True
            photo_path = os.path.join("images", filename)
            if os.path.exists(photo_path):
                with open(photo_path, "rb") as f:
                    await msg.reply_photo(
                        photo=f,
                        caption=(
                            f"🚫 *Restriction Alert: {code}*\n"
                            "Please check the restriction photo carefully. "
                            "There might be no truck road or a no-parking zone.\n\n"
                            "Safe trips!"
                        ),
                        parse_mode="Markdown",
                    )
                logging.info(f"Sent restriction for {code}")
            else:
                await msg.reply_text(f"❌ Image for {code} not found.")
                logging.warning(f"Image file not found: {filename}")

    if not matched:
        logging.info("No matching restriction code found.")

# --- BOT START ---
def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is empty.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # Matn va captionlarni ushlash uchun:
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_restriction))
    print("📡 Restriction Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

