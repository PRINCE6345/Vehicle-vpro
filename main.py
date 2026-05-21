import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8996859662:AAESV9bvxt3ub7ChOZzQisSPaCUk1oIyESM"
CHANNEL_USERNAME = "@princexhitmanmods"
CHANNEL_LINK = "https://t.me/princexhitmanmods"
API_KEY = "1WEEK_DEMO_ROOTX_INDIA"
API_URL = "https://rootx-osint.in/"

async def check_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_member(user_id, context)

    if not is_member:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join")]]
        await update.message.reply_text(
            "⚠️ *Channel Join Required*\n\nBot use karne ke liye pehle channel join karo!\n\n"
            "👇 Niche button click karo:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        "🚗 *Vehicle Lookup Bot*\n\n"
        "Vehicle number bhejo, main details nikaal deta hoon.\n\n"
        "*Example:* `WB74Bh4531`\n\n"
        "━━━━━━━━━━━━━━\n"
        "🔥 *Made by PRINCE*",
        parse_mode="Markdown"
    )

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    is_member = await check_member(user_id, context)

    if is_member:
        await query.message.edit_text(
            "✅ *Verified!*\n\nAb vehicle number bhejo.\n\n"
            "*Example:* `WB74Bh4531`\n\n"
            "━━━━━━━━━━━━━━\n"
            "🔥 *Made by PRINCE*",
            parse_mode="Markdown"
        )
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join")]]
        await query.message.edit_text(
            "❌ *Abhi Join Nahi Kiya!*\n\nPehle channel join karo phir try karo.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def lookup_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_member(user_id, context)

    if not is_member:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join")]]
        await update.message.reply_text(
            "⚠️ Pehle channel join karo!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    vehicle_no = update.message.text.strip().upper()
    msg = await update.message.reply_text("🔍 Searching...")

    try:
        response = requests.get(
            API_URL,
            params={"type": "v_num", "key": API_KEY, "query": vehicle_no},
            timeout=15
        )
        data = response.json()

        # Extract vehicle number and phone number
        veh_num = data.get("vehicle_number") or data.get("reg_no") or data.get("rc_number") or vehicle_no
        phone = data.get("mobile") or data.get("phone") or data.get("mobile_no") or data.get("owner_mobile") or "Not Found"

        result = (
            f"🚗 *Vehicle Lookup Result*\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔢 *Vehicle No:* `{veh_num}`\n"
            f"📞 *Phone No:* `{phone}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔥 *Made by PRINCE*"
        )

        await msg.edit_text(result, parse_mode="Markdown")

    except requests.exceptions.Timeout:
        await msg.edit_text("⏱️ API timeout. Baad mein try karo.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text("❌ Kuch error aaya. Valid vehicle number bhejo.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="check_join"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup_vehicle))
    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
