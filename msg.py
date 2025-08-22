import re
from datetime import datetime
from config import cfg

TELEGRAM_PARSE_MODE = cfg["telegram"]["parse_mode"]


# ====== 工具函数：转义 MarkdownV2 特殊字符 ======
def escape_markdown(text: str) -> str:
    escape_chars = r'[]()'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


# ====== 工具函数：分段发送 ======
def split_text(text: str, chunk_size: int = 4000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


# ================= 推送到 Telegram =================
def send_text_to_telegram(bot, chat_id, text: str):
    try:
        escape = escape_markdown(text)
        chunks = split_text(escape)
        for chunk in chunks:
            bot.send_message(chat_id=chat_id, text=chunk, parse_mode=TELEGRAM_PARSE_MODE)
        print(f"[{datetime.now()}] 日报，自动推送成功（分段 {len(chunks)} 条）")
    except Exception as e:
        print(f"[{datetime.now()}] 日报，自动推送失败: {e}")


# ====== 推送图片 + 分段文字 ======
def send_photo_to_telegram(bot, chat_id, text: str, photo_path: str):
    try:
        escape = escape_markdown(text)
        chunks = split_text(escape, chunk_size=1000)  # caption 限制 1024

        # 第一段作为 caption + 图片
        with open(photo_path, "rb") as f:
            bot.send_photo(chat_id=chat_id, photo=f, caption=chunks[0], parse_mode=TELEGRAM_PARSE_MODE)

        # 其余段落作为普通消息
        for chunk in chunks[1:]:
            bot.send_message(chat_id=chat_id, text=chunk, parse_mode=TELEGRAM_PARSE_MODE)

        print(f"[{datetime.now()}] ✅ 图片+文字推送成功（共 {len(chunks)} 段）")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 图片推送失败: {e}")
