from datetime import datetime
from config import cfg


TELEGRAM_PARSE_MODE = cfg["telegram"]["parse_mode"]


# ================= 推送到 Telegram =================
def send_text_to_telegram(bot: None, chat_id: None, text: None):
    try:
        bot.send_message(chat_id=chat_id, text=text, parse_mode=TELEGRAM_PARSE_MODE)
        print(f"[{datetime.now()}] 日报，自动推送成功")
    except Exception as e:
        print(f"[{datetime.now()}] 日报，自动推送失败: {e}")


# ====== 发送图片到 Telegram ======
def send_photo_to_telegram(bot: None, chat_id: None, text: None, photo_path: None):
    """
    使用 bot.send_photo() 发送图片 + 文字
    """
    with open(photo_path, "rb") as f:
        bot.send_photo(chat_id=chat_id, photo=f, caption=text, parse_mode=TELEGRAM_PARSE_MODE)
