import yfinance as yf
from config import cfg


# ================= 配置 =================
STOCKS = cfg["yfinance"]["stocks"]   # 关注的股票
PERIOD = cfg["yfinance"]["period"]     # 拉取周期
INTERVAL = cfg["yfinance"]["interval"]    # 拉取粒度


# ================= 获取股票数据 =================
def fetch_stock_data():
    data = yf.download(STOCKS, period=PERIOD, interval=INTERVAL)["Close"]
    latest = data.tail(1).to_dict()
    return latest

