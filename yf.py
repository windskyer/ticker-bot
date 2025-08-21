import yfinance as yf
import matplotlib.pyplot as plt
from config import cfg

# ================= 配置 =================
STOCKS = cfg["yfinance"]["stocks"]  # 关注的股票
PERIOD = cfg["yfinance"]["period"]  # 拉取周期
INTERVAL = cfg["yfinance"]["interval"]  # 拉取粒度

# 设置中文字体（Windows/Mac/Linux 都可）
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 黑体
plt.rcParams["axes.unicode_minus"] = False    # 解决负号显示问题


# ================= 股票/宏观数据 =================
def fetch_stock_data():
    data = yf.download(STOCKS, period=PERIOD, interval=INTERVAL, auto_adjust=True)["Close"]
    latest = data.tail(1).to_dict()
    return latest


def get_macro_data(period="1mo", interval="1d"):
    tickers = {
        "NVIDIA": "NVDA",
        "Nasdaq100": "^NDX",
        "Gold": "GC=F",
        "Bitcoin": "BTC-USD"
    }
    df = yf.download(list(tickers.values()), period=period, interval=interval, auto_adjust=True)["Close"]
    df.rename(columns={v: k for k, v in tickers.items()}, inplace=True)
    return df


# ====== 绘图 ======
def plot_macro_chart(data, filename=None):
    normalized = data / data.iloc[0] * 100
    plt.figure(figsize=(12,6))
    for col in normalized.columns:
        plt.plot(normalized.index, normalized[col], label=col)
    plt.title("宏观资产对比：NVDA vs 纳斯达克100 vs 黄金 vs 比特币")
    plt.ylabel("Normalized Price (基准=100)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    if filename:
        plt.savefig(filename)
        plt.close()
        return filename
    else:
        plt.show()
