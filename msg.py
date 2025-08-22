import re
from datetime import datetime
from config import cfg

TELEGRAM_PARSE_MODE = cfg["telegram"]["parse_mode"]


# ====== 转义 MarkdownV2 特殊字符 ======
def escape_markdown_v2(text: str) -> str:
    """
    转义 Telegram MarkdownV2 保留字符：
    _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    text = text.replace("#", r"")
    return re.sub(r'([_$begin:math:display$$end:math:display$()~`>#+\-=|{}.!])', r'\\\1', text)


# ====== 工具函数：分段发送 ======
def split_text(text: str, chunk_size: int = 1000):
    """
    按行分段，同时尽量保持 Markdown 标签完整
    """
    lines = text.split("\n")
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > chunk_size:
            chunks.append(current)
            current = ""
        current += line + "\n"
    if current:
        chunks.append(current)
    return chunks


# ================= 推送到 Telegram =================
def send_text_to_telegram(bot, chat_id, text: str):
    try:
        safe_text = escape_markdown_v2(text)
        chunks = split_text(safe_text, chunk_size=1000)
        for chunk in chunks:
            bot.send_message(chat_id=chat_id, text=chunk, parse_mode=TELEGRAM_PARSE_MODE)
        print(f"[{datetime.now()}] 日报，自动推送成功（分段 {len(chunks)} 条）")
    except Exception as e:
        print(f"[{datetime.now()}] 日报，自动推送失败: {e}")


# ====== 推送图片 + 分段文字 ======
def send_photo_to_telegram(bot, chat_id, text: str, photo_path: str):
    try:
        safe_text = escape_markdown_v2(text)
        chunks = split_text(safe_text, chunk_size=1000)  # caption 限制 1024

        # 第一段作为 caption + 图片
        with open(photo_path, "rb") as f:
            bot.send_photo(chat_id=chat_id, photo=f, caption=chunks[0], parse_mode=TELEGRAM_PARSE_MODE)

        # 其余段落作为普通消息
        for chunk in chunks[1:]:
            bot.send_message(chat_id=chat_id, text=chunk, parse_mode=TELEGRAM_PARSE_MODE)

        print(f"[{datetime.now()}] ✅ 图片+文字推送成功（共 {len(chunks)} 段）")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 图片推送失败: {e}")
