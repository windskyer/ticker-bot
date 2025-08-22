import re
from config import cfg

TELEGRAM_PARSE_MODE = cfg["telegram"]["parse_mode"]
MAX_LEN = 4000
MAX_CAPTION_LEN = 1024


# ====== 工具函数：转义 Markdown 特殊字符 ======
def escape_markdown(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


# ================= 推送到 Telegram =================
def send_text(bot, chat_id, text):
    """
    按换行分段发送，单条消息不超过 MAX_LEN
    """
    lines = text.split("\n")
    chunk = ""
    for line in lines:
        line_safe = escape_markdown(line) + "\n"
        if len(chunk) + len(line_safe) > MAX_LEN:
            bot.send_message(chat_id=chat_id, text=chunk, parse_mode=TELEGRAM_PARSE_MODE)
            chunk = line_safe
        else:
            chunk += line_safe
    if chunk:
        bot.send_message(chat_id=chat_id, text=chunk, parse_mode=TELEGRAM_PARSE_MODE)


# ====== 发送图片到 Telegram ======
def send_photo_with_text(bot, chat_id, photo_path, text):
    """
    发送图片 + 分段文本
    """
    safe_text = escape_markdown(text)
    # 首段文字放在 caption
    caption = safe_text[:MAX_CAPTION_LEN]
    rest_text = safe_text[MAX_CAPTION_LEN:]

    with open(photo_path, "rb") as f:
        bot.send_photo(chat_id=chat_id, photo=f, caption=caption, parse_mode=TELEGRAM_PARSE_MODE)

    # 剩余文字分段发送
    while rest_text:
        chunk = rest_text[:MAX_LEN]
        rest_text = rest_text[MAX_LEN:]
        bot.send_message(chat_id=chat_id, text=chunk, parse_mode=TELEGRAM_PARSE_MODE)

