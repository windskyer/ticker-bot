from telebot import TeleBot
from datetime import datetime
import threading
import schedule
import time

from config import cfg
from gemini import generate_report
from yf import fetch_stock_data
from msg import send_telegram_message

# ================= 配置 =================
TELEGRAM_TOKEN = cfg["telegram"]["token"]
REPORT_TIME = cfg["telegram"]["report_time"]

# === 初始化 Bot ===
bot = TeleBot(TELEGRAM_TOKEN)


# ================= 每日任务 =================
# === 命令: /start ===
@bot.message_handler(commands=['start'])
def daily_job():
    stock_data = fetch_stock_data()
    report = generate_report(stock_data)

    print("===== 今日 AI 金融日报 =====")
    print(report)

    send_telegram_message(bot, report)


# === 定时任务线程运行函数 ===
def task1():
    schedule.every().day.at(REPORT_TIME).do(daily_job)  # 每天早上0点推送
    print(f"📅 ticker-bot 已启动，将在每天 {REPORT_TIME} 生成日报...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    print(f"[{datetime.now()}]✅启动定时任务...")
    # 启动发送
    threading.Thread(target=task1, daemon=True).start()
    # 启动 Bot
    bot.infinity_polling()
