import os
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

AUTHORIZED_USERS = {
    "vikas": 123456789,  # replace with your Telegram ID
    "deepthi": 987654321  # replace with Deepthi's Telegram ID
}

def send_message(chat_id, text):
    url = f"{BOT_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() == "/start":
            send_message(chat_id, "Welcome to NEET PG Mentor Bot! 🔥\nLet’s crush NEET PG 2025!")
        elif text.lower() == "/motivate":
            send_message(chat_id, "Every question you solve gets you one step closer to your dream. Keep going! 💪")
        elif text.lower() == "/checkin":
            send_message(chat_id, "📍 Session check-in recorded.")
        elif text.lower().startswith("/report"):
            send_message(chat_id, "📊 Report logged. Great work!")
        else:
            send_message(chat_id, "I'm here to help you stay on track! Type /motivate or /checkin.")
    
    return "ok", 200

def set_webhook():
    url = f"{BOT_URL}/setWebhook"
    webhook_url = f"https://neetpgmentorbot.onrender.com/{BOT_TOKEN}"
    response = requests.post(url, json={"url": webhook_url})
    print("Webhook set:", response.text)

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
