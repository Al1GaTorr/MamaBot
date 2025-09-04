import requests
import time
import schedule

TOKEN = "8118208361:AAFrCQgk8qT9T6oQifuKdwr2c8tR5LewToc"
URL = f"https://api.telegram.org/bot{TOKEN}/"
MOM_CHAT_ID = 1173782035  # твой chat_id

waiting_for_reply = False
last_reminder_time = None

def send_message(chat_id, text, keyboard=None):
    url = URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = keyboard
    r = requests.post(url, json=payload)
    print("send_message response:", r.text)  # 🔍 debug

def daily_reminder():
    global waiting_for_reply, last_reminder_time
    keyboard = {"keyboard": [["Я заполнила ✅"]], "resize_keyboard": True}
    print("📢 Отправляем напоминание маме...")  # 🔍 debug
    send_message(MOM_CHAT_ID, "⏰ Мама, заполни отчёт!", keyboard)
    waiting_for_reply = True
    last_reminder_time = time.time()

def check_timeout():
    global waiting_for_reply, last_reminder_time
    if waiting_for_reply and last_reminder_time:
        if time.time() - last_reminder_time > 300:  # для теста 1 минута (потом сделай 300)
            print("⏰ Время вышло, напоминаем снова!")  # 🔍 debug
            daily_reminder()

def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += f"?offset={offset}"
    return requests.get(url).json()

def main():
    last_update_id = None
    schedule.every().day.at("15:30").do(daily_reminder)

    print("Bot started...")

    while True:
        schedule.run_pending()
        check_timeout()

        updates = get_updates(last_update_id)
        if "result" in updates:
            for update in updates["result"]:
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "").lower()

                    if text == "я заполнила ✅".lower():
                        global waiting_for_reply
                        waiting_for_reply = False
                        send_message(chat_id, "Спасибо 🙌 Напомню завтра в 20:00!")

                    last_update_id = update["update_id"] + 1
        time.sleep(1)

if __name__ == "__main__":
    main()
