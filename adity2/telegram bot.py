from flask import Flask, request, jsonify
import json
import os
import telebot

app = Flask(__name__)
BOT_TOKEN = "7231687781:AAE8qTH7orpwdwnD0z_gMwCIqn47oe17bcA"
OWNER_ID = 6811664913
bot = telebot.TeleBot(BOT_TOKEN)
ORDERS_FILE = "orders.json"

# Save Order to JSON file
def save_order(data):
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    else:
        orders = []

    orders.append(data)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Send to Telegram
def send_to_telegram(order):
    msg = f"""🛒 *New COD Order Received!*
👤 *{order['name']}*
📞 {order['phone']}
🏠 {order['address']}
💳 Payment: COD

🧾 *Items:*
{order['items']}

💰 *Total:* ₹{order['total']}
⏳ Status: Pending
"""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Accept", callback_data=f"accept|{order['phone']}"),
        telebot.types.InlineKeyboardButton("❌ Reject", callback_data=f"reject|{order['phone']}")
    )
    bot.send_message(OWNER_ID, msg, parse_mode="Markdown", reply_markup=markup)

@app.route("/send", methods=["POST"])
def send_order():
    data = request.json
    save_order(data)
    send_to_telegram(data)
    return jsonify({"status": "success"})

@app.route("/get-cart", methods=["GET"])
def get_cart():
    phone = request.args.get("phone")
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
        cart = next((o for o in orders if o["phone"] == phone), None)
        return jsonify(cart if cart else {})
    return jsonify({})

# === Accept / Reject Handler
@bot.callback_query_handler(func=lambda call: True)
def handle_btn(call):
    action, phone = call.data.split("|")
    if action == "accept":
        bot.send_message(OWNER_ID, f"✅ Order from {phone} accepted.")
    else:
        bot.send_message(OWNER_ID, f"❌ Order from {phone} rejected.")
    bot.answer_callback_query(call.id, "Response sent")

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: bot.polling(non_stop=True)).start()
    app.run(host="0.0.0.0", port=5000)