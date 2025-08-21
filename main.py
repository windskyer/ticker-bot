from telebot import TeleBot
from datetime import datetime
import threading
import schedule
import time

from config import cfg
from gemini import generate_report, generate_report_macro
from yf import fetch_stock_data, get_macro_data, plot_macro_chart
from msg import send_text, send_photo

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
        send_text(bot, TELEGRAM_CHAT_ID, report)
        send_text(bot, TELEGRAM_CHANNEL_ID, report)

        # 图片日报
        macro_data = get_macro_data()
        filename = f"{TELEGRAM_IMG_PATH}/macro.png"
        plot_macro_chart(macro_data, filename)
        report_macro = generate_report_macro(macro_data)
        send_photo(bot, TELEGRAM_CHAT_ID, report_macro, filename)
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
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"欢迎使用 Ticker 股市订阅助手！\n每日{TELEGRAM_REPORT_TIME}推送金融日报。", parse_mode=TELEGRAM_PARSE_MODE)


# ================= 主程序 =================
if __name__ == "__main__":
    print(f"[{datetime.now()}]✅启动定时任务...")
    threading.Thread(target=schedule_daily_task, daemon=True).start()
    bot.infinity_polling()
