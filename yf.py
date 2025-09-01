import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import font_manager
from config import cfg

# ================= 配置 =================
STOCKS = cfg["yfinance"]["stocks"]  # 关注的股票
PERIOD = cfg["yfinance"]["period"]  # 拉取周期
INTERVAL = cfg["yfinance"]["interval"]  # 拉取粒度


# 设置中文字体（Windows/Mac/Linux 都可）
# 优先选择可用中文字体
def set_chinese_font():
    candidates = ["SimHei", "WenQuanYi Zen Hei", "Noto Sans CJK SC"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for font in candidates:
        if font in available:
            plt.rcParams["font.sans-serif"] = [font]
            plt.rcParams["axes.unicode_minus"] = False
            print(f"✅ 使用字体: {font}")
            return
    print("⚠️ 未找到中文字体，可能出现乱码")


set_chinese_font()


# ================= 股票/宏观数据 =================
def fetch_stock_data():
    data = yf.download(STOCKS, period=PERIOD, interval=INTERVAL, auto_adjust=True)["Close"]
    latest = data.tail(1).to_dict()
    return latest


# ====== 获取行情 ======
def get_stock_data(ticker, period="3mo", interval="1d"):
    data = yf.download(ticker, period=period, interval=interval)["Close"]
    return pd.DataFrame(data, columns=["Close"])


def get_macro_data(period="1mo", interval="1d"):
    tickers = {
        "AAPL": "AAPL",  # 苹果
        "S&P500": "^GSPC",  # 标普500
        "Gold": "GC=F",  # 黄金期货
        "Bitcoin": "BTC-USD"  # 比特币
    }
    df = yf.download(list(tickers.values()), period=period, interval=interval, auto_adjust=True)["Close"]
    df.rename(columns={v: k for k, v in tickers.items()}, inplace=True)
    return df


# ====== 绘图 ======
def plot_macro_chart(data, filename=None):
    normalized = data / data.iloc[0] * 100
    plt.figure(figsize=(12, 6))
    for col in normalized.columns:
        plt.plot(normalized.index, normalized[col], label=col)
    plt.title("宏观资产对比：股票 vs 指数 vs 黄金 vs 比特币 (最近1月)")
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


# ====== 均线策略 ======
def ma_crossover(df, short=20, long=50):
    df["SMA_short"] = df["Close"].rolling(short).mean()
    df["SMA_long"] = df["Close"].rolling(long).mean()
    df["Signal"] = 0
    df["Signal"][short:] = (df["SMA_short"][short:] > df["SMA_long"][short:]).astype(int)
    df["Position"] = df["Signal"].diff()
    return df


# ====== 动量策略 ======
def momentum_strategy(df, lookback=5):
    df["Momentum"] = df["Close"].pct_change(periods=lookback)
    df["Signal"] = 0
    df["Signal"][lookback:] = (df["Momentum"][lookback:] > 0).astype(int)
    df["Position"] = df["Signal"].diff()
    return df


# ====== 简单套利策略 ======
def pair_arbitrage(stock_df, index_df):
    df = pd.DataFrame({"Stock": stock_df["Close"], "Index": index_df["Close"]})
    df["Spread"] = df["Stock"] - df["Index"]
    mean = df["Spread"].mean()
    std = df["Spread"].std()
    df["Signal"] = 0
    df.loc[df["Spread"] > mean + std, "Signal"] = -1
    df.loc[df["Spread"] < mean - std, "Signal"] = 1
    df["Position"] = df["Signal"].diff()
    return df


# ====== 绘图2 ======
def plot_strategies(ma_df, mom_df, arb_df, filename="strategy_report.png"):
    plt.figure(figsize=(14, 10))

    # 均线策略
    plt.subplot(3, 1, 1)
    plt.plot(ma_df["Close"], label="Close")
    plt.plot(ma_df["SMA_short"], label="SMA_short")
    plt.plot(ma_df["SMA_long"], label="SMA_long")
    plt.title("均线策略（MA Crossover）")
    plt.legend()

    # 动量策略
    plt.subplot(3, 1, 2)
    plt.plot(mom_df["Close"], label="Close")
    plt.plot(mom_df["Momentum"], label="Momentum")
    plt.title("动量策略")
    plt.legend()

    # 套利策略
    plt.subplot(3, 1, 3)
    plt.plot(arb_df["Stock"], label="Stock")
    plt.plot(arb_df["Index"], label="Index")
    plt.plot(arb_df["Spread"], label="Spread")
    plt.title("简单套利策略（Spread）")
    plt.legend()

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return filename
