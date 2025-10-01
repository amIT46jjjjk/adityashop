from flask import Flask, request
import telebot

# === CONFIG ===
BOT_TOKEN = "7231687781:AAE8qTH7orpwdwnD0z_gMwCIqn47oe17bcA"  # ⚠️ Replace with your actual bot token
OWNER_ID = 6811664913  # ⚠️ Your Telegram user ID (chat_id)
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# To store order status for each phone number
order_status = {}

# === ROUTE 1: ORDER RECEIVE FROM WEBSITE ===
@app.route("/send", methods=["POST"])
def send_order():
    order = request.json

    # HTML-formatted message
    message = (
        "🛒 <b>New COD Order Received!</b>\n"
        f"👤 <b>Name:</b> {order['name']}\n"
        f"📞 <b>Phone:</b> {order['phone']}\n"
        f"🏠 <b>Address:</b> {order['address']}\n"
        f"🛍 <b>Items:</b>\n{order['items'].replace('-', '•')}\n\n"
        "⏳ <b>Status:</b> Pending\n\n"
        "<i>Choose an option below:</i>"
    )

    # Inline Buttons
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    accept_btn = telebot.types.InlineKeyboardButton("✅ Accept", callback_data=f"accept|{order['phone']}")
    reject_btn = telebot.types.InlineKeyboardButton("❌ Reject", callback_data=f"reject|{order['phone']}")
    markup.add(accept_btn, reject_btn)

    try:
        bot.send_message(OWNER_ID, message, parse_mode="HTML", reply_markup=markup)
        order_status[order['phone']] = "pending"
        return "✅ Order sent to Telegram", 200
    except Exception as e:
        return f"❌ Error sending order: {str(e)}", 500

# === ROUTE 2: CHECK STATUS FROM WEB ===
@app.route("/status/<phone>")
def status(phone):
    return {"status": order_status.get(phone, "pending")}

# === ROUTE 3: TELEGRAM CALLBACK WEBHOOK ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return "ok"

# === CALLBACK HANDLER ===
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    action, phone = call.data.split("|")

    if action == "accept":
        order_status[phone] = "accepted"
        msg = f"✅ <b>Order from {phone} has been accepted.</b>\nDelivery is on the way."
        notify_customer(phone, "Your order has been accepted! 🚚 Delivery is on the way.")
    elif action == "reject":
        order_status[phone] = "rejected"
        msg = f"❌ <b>Order from {phone} has been rejected.</b>\nCustomer has been notified."
        notify_customer(phone, "Sorry, your order has been rejected. ❌ Please contact support.")
    else:
        msg = "❓ Unknown action"

    # Edit the original message
    bot.answer_callback_query(call.id, "Response recorded")
    bot.edit_message_text(
        msg,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="HTML"
    )

# === OPTIONAL: Customer Notification (Placeholder) ===
def notify_customer(phone, message):
    # Tujhe yaha customer notify karna h to add logic here
    # For example, SMS API ya Telegram user chat_id mapping se
    print(f"Notify to {phone}: {message}")

# === FLASK START ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)