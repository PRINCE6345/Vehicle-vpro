import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
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
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "⚠️ *Access Restricted!*\n\n"
            "You must join our channel to use this bot.\n\n"
            "👇 Click below to join:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        "🚗 *Vehicle Lookup Bot*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Send a vehicle number to get owner details.\n\n"
        "📌 *Example:* `WB74BH4531`\n"
        "━━━━━━━━━━━━━━━━━━\n"
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
            "✅ *Verified Successfully!*\n\n"
            "Welcome! Send a vehicle number to get started.\n\n"
            "📌 *Example:* `WB74BH4531`\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🔥 *Made by PRINCE*",
            parse_mode="Markdown"
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
        ]
        await query.message.edit_text(
            "❌ *Not Joined Yet!*\n\n"
            "Please join the channel first, then try again.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def lookup_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_member(user_id, context)

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "⚠️ Please join our channel first!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    vehicle_no = update.message.text.strip().upper()
    msg = await update.message.reply_text("🔍 *Searching...*", parse_mode="Markdown")

    try:
        response = requests.get(
            API_URL,
            params={"type": "v_num", "key": API_KEY, "query": vehicle_no},
            timeout=15
        )
        data = response.json()
        logger.info(f"API Response: {data}")

        # Handle nested structure like {"VEHICLE_NUMBER": {"success": true, "vehicle": "...", "mobile": "..."}}
        inner = None
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], dict):
                    inner = data[key]
                    break

        if inner is None:
            inner = data

        success = inner.get("success", False)

        if not success:
            await msg.edit_text(
                "❌ *No Record Found!*\n\n"
                "No data available for this vehicle number.\n"
                "Please check and try again.\n\n"
                "🔥 *Made by PRINCE*",
                parse_mode="Markdown"
            )
            return

        veh_num = inner.get("vehicle") or inner.get("vehicle_number") or inner.get("reg_no") or vehicle_no
        phone = inner.get("mobile") or inner.get("phone") or inner.get("mobile_no") or "Not Available"

        result = (
            f"╔══════════════════╗\n"
            f"  🚗 *VEHICLE LOOKUP RESULT*\n"
            f"╚══════════════════╝\n\n"
            f"🔢 *Vehicle Number*\n"
            f"┗ `{veh_num}`\n\n"
            f"📞 *Owner Phone Number*\n"
            f"┗ `{phone}`\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Powered by *Made by PRINCE*\n"
            f"📢 @princexhitmanmods"
        )

        await msg.edit_text(result, parse_mode="Markdown")

    except requests.exceptions.Timeout:
        await msg.edit_text(
            "⏱️ *Request Timed Out!*\n\nAPI is taking too long. Please try again later.\n\n🔥 *Made by PRINCE*",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(
            "❌ *Something Went Wrong!*\n\nPlease send a valid vehicle number.\n\n🔥 *Made by PRINCE*",
            parse_mode="Markdown"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="check_join"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup_vehicle))
    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
