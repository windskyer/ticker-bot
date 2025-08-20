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
TELEGRAM_REPORT_TIME = cfg["telegram"]["report_time"]
TELEGRAM_PARSE_MODE = cfg["telegram"]["parse_mode"]

# === 初始化 Bot ===
bot = TeleBot(TELEGRAM_TOKEN)


# === 命令: /start ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        print(f"[{datetime.now()}] 用户 {message.from_user.id} 请求了链接")
        bot.reply_to(message, "欢迎使用 Ticker 股市订阅助手！输入 /help 查看可用命令。", parse_mode=TELEGRAM_PARSE_MODE)
        daily_job()
        print(f"[{datetime.now()}] 发送start成功")
    except Exception as e:
        print(f"[{datetime.now()}] 发送start失败: {e}")


# ================= 每日任务 =================
def daily_job():
    stock_data = fetch_stock_data()
    report = generate_report(stock_data, debug=False)

    print("===== 今日 AI 金融日报 =====")
    print(report)

    send_telegram_message(bot, report)


# === 定时任务线程运行函数 ===
def task1():
    schedule.every().day.at(TELEGRAM_REPORT_TIME).do(daily_job)  # 每天早上0点推送
    print(f"📅 ticker-bot 已启动，将在每天 {TELEGRAM_REPORT_TIME} 生成日报...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    print(f"[{datetime.now()}]✅启动定时任务...")
    # 启动发送
    threading.Thread(target=task1, daemon=True).start()
    # 启动 Bot
    bot.infinity_polling()
