import os
import datetime
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

AUTHORIZED_USERS = {
    440324261: "Vikas",             
    1177941894: "Deepthi",           
}

USERNAME_MAP = {
    "Vikas": "@gaddamvikas",
    "Deepthi": "@Deepthiramana"
}

DAILY_LOG = {
    "Vikas": {},
    "Deepthi": {}
}

STREAKS = {
    "Vikas": {"mcq1": 0, "mcq2": 0, "mcq3": 0, "anki": 0},
    "Deepthi": {"mcq1": 0, "mcq2": 0, "mcq3": 0, "anki": 0}
}

def countdown_to_exam():
    exam_date = datetime.date(2025, 8, 3)
    today = datetime.date.today()
    return (exam_date - today).days

def send_message(chat_id, text):
    url = f"{BOT_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route('/', methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    username = AUTHORIZED_USERS.get(user_id, None)

    if username is None:
        send_message(chat_id, "Unauthorized user.")
        return "ok"

    text = msg.get("text", "")
    today = str(datetime.date.today())

    # Init daily log
    if today not in DAILY_LOG[username]:
        DAILY_LOG[username][today] = {
            "checkins": [],
            "mcq_scores": {},
            "anki": None,
        }

    # Command handlers
    if text.startswith("/start"):
        countdown = countdown_to_exam()
        send_message(chat_id, f"ð *Good Morning {username}!*\n*NEET PG Countdown:* {countdown} days left!\nLet's crush this! ðª")
    elif text.startswith("/checkin"):
        DAILY_LOG[username][today]["checkins"].append(text)
        send_message(chat_id, f"â Logged {text} for {username}. Keep going!")
    elif text.startswith("/logmcq"):
        session = text.split()[0][-1]
        try:
            score = int(text.split()[1])
            DAILY_LOG[username][today]["mcq_scores"][f"mcq{session}"] = score
            if score >= 30:
                STREAKS[username][f"mcq{session}"] += 1
            else:
                STREAKS[username][f"mcq{session}"] = 0
            send_message(chat_id, f"â MCQ {session} logged: {score}/40\nð¥ Streak: {STREAKS[username][f'mcq{session}']}")
        except:
            send_message(chat_id, "â ï¸ Use format: /logmcq1 35")
    elif text.startswith("/loganki"):
        try:
            count = int(text.split()[1])
            DAILY_LOG[username][today]["anki"] = count
            if count >= 100:
                STREAKS[username]["anki"] += 1
            else:
                STREAKS[username]["anki"] = 0
            send_message(chat_id, f"ð§  Anki logged: {count} cards\nð¥ Streak: {STREAKS[username]['anki']}")
        except:
            send_message(chat_id, "â ï¸ Use format: /loganki 120")
    elif text.startswith("/progress"):
        log = DAILY_LOG[username][today]
        msg = f"ð *Today's Progress - {username}*\n"
        msg += f"Check-ins: {', '.join(log['checkins']) or 'None'}\n"
        for k, v in log["mcq_scores"].items():
            msg += f"{k.upper()}: {v}/40 | Streak: {STREAKS[username][k]}\n"
        msg += f"Anki: {log['anki'] or 'Not logged'} | Streak: {STREAKS[username]['anki']}"
        send_message(chat_id, msg)
    elif text.startswith("/report"):
        countdown = countdown_to_exam()
        send_message(chat_id, f"ðï¸ *NEET PG Countdown:* {countdown} days left.\nUse /progress to view todayâs log.")
    elif text.startswith("/ask"):
        question = text[4:].strip()
        if not question:
            send_message(chat_id, "â Use: /ask Your question here")
        else:
            # Placeholder for AI response
            response = f"ð¤ AI says: [This is a simulated reply to: '{question}']"
            send_message(chat_id, response)
    else:
        send_message(chat_id, "â ï¸ Unknown command.")

    return "ok"
