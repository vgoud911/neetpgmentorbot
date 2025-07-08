import os
import logging
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
YOUR_CHAT_ID = os.environ.get("YOUR_CHAT_ID")  # Replace later if needed

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        reply = f"You said: {text}"
        requests.post(URL, json={"chat_id": chat_id, "text": reply})
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
