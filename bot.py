import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- LOAD .ENV ---
load_dotenv()  

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
    "MQY1": "MQY1.jpg", "RBD5": "RBD5.jpg", 
}

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# --- UNIVERSAL HANDLER ---
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if update.message.from_user.is_bot:
        return

    text = (update.message.caption or update.message.text or "").upper()
    logger.info(f"Received: {text}")

    # 1. NEW LOAD ALERT
    if "NEW LOAD ALERT" in text:
        await update.message.reply_text(
            "Please check all post trucks, the driver was covered! It takes just few seconds, let's do!"
        )
        logger.info("✅ Replied to 'New Load Alert'")

    # 2. RESTRICTION
    matched = False
    for code, filename in RESTRICTION_CODES.items():
        if code in text:
            matched = True
            path = os.path.join("images", filename)
            if os.path.exists(path):
                with open(path, "rb") as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=(
                            f"🚫 *Restriction Alert: {code}*\n"
                            "Please check the restriction photo carefully. There might be no truck road or a no-parking zone.\n\n"
                            "Safe trips!"
                        ),
                        parse_mode="Markdown"
                    )
                    logger.info(f"✅ Sent restriction for {code}")
            else:
                await update.message.reply_text(f"❌ Image for {code} not found.")
                logger.warning(f"Image file not found: {filename}")
    if not matched and "NEW LOAD ALERT" not in text:
        logger.info("ℹ️ No restriction code or load alert found.")

# --- BOT START ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, handle_all_messages))

if __name__ == '__main__':
    print("📡 Bot is running...")
    app.run_polling()
