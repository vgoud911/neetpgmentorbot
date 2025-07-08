import os
import datetime
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
AUTHORIZED_USERS = {
    "123456789": "Vikas",
    "987654321": "Deepthi"
}

# In-memory logs for simplicity (replace with DB for production)
user_data = {}

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_id = str(data['message']['from']['id'])
        text = data['message'].get('text', '')

        if user_id not in AUTHORIZED_USERS:
            send_message(chat_id, "🚫 Unauthorized user.")
            return "ok"

        username = AUTHORIZED_USERS[user_id]
        user_logs = user_data.setdefault(user_id, {"mcq_scores": [], "streaks": [0, 0, 0]})

        if text == '/start':
            send_message(chat_id, f"🔥 Welcome {username}!
📅 *NEET PG Countdown:* {countdown_to_exam()} days left!
Type /menu to get started.")
        elif text == '/menu':
            send_message(chat_id, "*📋 Main Menu:*
"
                                  "/report - Log MCQ session
"
                                  "/progress - View your streaks & session logs
"
                                  "/leaderboard - Check friendly rankings
"
                                  "/summary - Get today’s progress report")
        elif text == '/report':
            now = datetime.datetime.now().strftime("%H:%M")
            user_logs["mcq_scores"].append((now, "✅ Reported 40 questions"))
            send_message(chat_id, f"✅ {username}, your session has been logged at {now}. Keep going!")
        elif text == '/progress':
            scores = user_logs["mcq_scores"]
            msg = "*📈 Your Progress:*
"
            for entry in scores[-5:]:
                msg += f"{entry[0]} - {entry[1]}
"
            send_message(chat_id, msg if scores else "No sessions logged yet.")
        elif text == '/leaderboard':
            scores = {AUTHORIZED_USERS[uid]: len(data['mcq_scores']) for uid, data in user_data.items()}
            sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
            lb_msg = "*🏆 Leaderboard:*
"
            for i, (name, count) in enumerate(sorted_scores, 1):
                lb_msg += f"{i}. {name} - {count} sessions
"
            send_message(chat_id, lb_msg)
        elif text == '/summary':
            total_sessions = len(user_logs["mcq_scores"])
            send_message(chat_id, f"📊 *Daily Summary*
Total MCQ Sessions: {total_sessions}
You're doing great, {username}! 💪")
        else:
            send_message(chat_id, "🤖 Command not recognized. Type /menu to see options.")

    return "ok"

def countdown_to_exam():
    exam_date = datetime.date(2025, 8, 3)
    today = datetime.date.today()
    return (exam_date - today).days

if __name__ == '__main__':
    app.run(debug=True)
