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


# === 命令: /start ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        print(f"[{datetime.now()}] 用户 {message.from_user.id} 请求了链接")
        bot.reply_to(message, f"""欢迎使用 Ticker 股市订阅助手！\n 每日9点推送金融日报。""", parse_mode=TELEGRAM_PARSE_MODE)
        daily_job()
        print(f"[{datetime.now()}] 发送start成功")
    except Exception as e:
        print(f"[{datetime.now()}] 发送start失败: {e}")


# ================= 每日任务 =================
def daily_job():
    stock_data = fetch_stock_data()
    report = generate_report(stock_data, debug=False)
    send_text_to_telegram(bot, TELEGRAM_CHAT_ID, report)
    time.sleep(10)
    send_text_to_telegram(bot, TELEGRAM_CHANNEL_ID, report)
    time.sleep(10)
    daily_job_photo()


# ================= 每日任务 =================
def daily_job_photo():
    data = get_macro_data(period="1mo", interval="1d")
    filename = plot_macro_chart(data, TELEGRAM_IMG_PATH + "/macro.png")
    report = generate_report_macro(data)
    send_photo_to_telegram(bot, TELEGRAM_CHAT_ID, report, filename)


# === 定时任务线程运行函数 ===
def task1():
    schedule.every().day.at(TELEGRAM_REPORT_TIME).do(daily_job)  # 每天早上9点推送
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
