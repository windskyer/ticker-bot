from datetime import datetime
from config import cfg


TELEGRAM_CHAT_ID = cfg["telegram"]["chat_id"]
TELEGRAM_PARSE_MODE = cfg["telegram"]["parse_mode"]


# ================= 推送到 Telegram =================
def send_telegram_message(bot: None, text: None):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode=TELEGRAM_PARSE_MODE)
        print(f"[{datetime.now()}] 日报，自动推送成功")
    except Exception as e:
        print(f"[{datetime.now()}] 日报，自动推送失败: {e}")

