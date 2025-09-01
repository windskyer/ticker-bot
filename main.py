from telebot import TeleBot
from datetime import datetime
import threading
import schedule
import time

from config import cfg
from gemini import generate_report, generate_report_macro
from yf import fetch_stock_data, get_macro_data, plot_macro_chart
from msg import send_text_to_telegram, send_photo_to_telegram

# ================= 配置 =================
TELEGRAM_TOKEN = cfg["telegram"]["token"]
TELEGRAM_REPORT_TIME = cfg["telegram"]["report_time"]
TELEGRAM_PARSE_MODE = cfg["telegram"]["parse_mode"]
TELEGRAM_IMG_PATH = cfg["telegram"]["img_path"]  # 图片地址
TELEGRAM_CHAT_ID = cfg["telegram"]["chat_id"]
TELEGRAM_CHANNEL_ID = cfg["telegram"]["channel_id"]

# === 初始化 Bot ===
bot = TeleBot(TELEGRAM_TOKEN)


# ================= 每日任务 =================
def daily_task():
    try:
        # 文字日报
        stock_data = fetch_stock_data()
        report = generate_report(stock_data)
        print(report)
        send_text_to_telegram(bot, TELEGRAM_CHAT_ID, report)
        # send_text_to_telegram(bot, TELEGRAM_CHANNEL_ID, report)

        # 图片日报
        macro_data = get_macro_data()
        filename = f"{TELEGRAM_IMG_PATH}/macro.png"
        plot_macro_chart(macro_data, filename)
        report_macro = generate_report_macro(macro_data)
        print(report_macro)
        send_photo_to_telegram(bot, TELEGRAM_CHAT_ID, report_macro, filename)
        # send_photo_to_telegram(bot, TELEGRAM_CHANNEL_ID, report_macro, filename)
        print(f"[{datetime.now()}] ✅ 今日日报发送成功")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 日报发送失败: {e}")


# ================= 定时任务 =================
def schedule_daily_task():
    schedule.every().day.at(TELEGRAM_REPORT_TIME).do(daily_task)
    print(f"[{datetime.now()}] 📅 ticker-bot 已启动，将在每天 {TELEGRAM_REPORT_TIME} 生成日报...")
    while True:
        schedule.run_pending()
        time.sleep(1)


# ================= Bot 命令 =================
@bot.message_handler(commands=['start', 's'])
def send_welcome(message):
    help_text = f"""
欢迎使用 Ticker 股市订阅助手！

可用命令：
/start - 启动 Bot，接收每日金融日报
/push 或 /p - 立即推送金融日报

每日任务：
- 每天 {TELEGRAM_REPORT_TIME} 自动推送 AI 金融日报
- 包含股票收盘价、宏观资产对比
- 回测策略图表（均线/动量/套利）

使用注意：
- 确保 Bot 已加入目标群组或频道
- 支持 MarkdownV2 消息显示
"""
    send_text_to_telegram(bot, message.chat.id, help_text)


# ================= Bot push 帮助命令 =================
@bot.message_handler(commands=['push', 'p'])
def send_push(message):
    help_text = f"""
    欢迎使用 Ticker 股市订阅助手！
    立即推送 AI 金融日报
"""
    send_text_to_telegram(bot, message.chat.id, help_text)
    daily_task()


# ================= 主程序 =================
if __name__ == "__main__":
    print(f"[{datetime.now()}]✅启动定时任务...")
    threading.Thread(target=schedule_daily_task, daemon=True).start()
    bot.infinity_polling()
