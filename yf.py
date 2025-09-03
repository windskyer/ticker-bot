import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import font_manager
from datetime import datetime
from config import cfg

# ================= 配置 =================
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
def fetch_stock_data(stocks):
    data = yf.download(stocks, period=PERIOD, interval=INTERVAL, auto_adjust=True)["Close"]
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


# ================= 股票分析 =================
def analyze_stock(ticker_symbol: str):
    ticker = yf.Ticker(ticker_symbol)

    # 基本信息
    info = ticker.info
    name = info.get("shortName", ticker_symbol)
    current_price = info.get("currentPrice", None)
    target_mean = info.get("targetMeanPrice", None)
    target_high = info.get("targetHighPrice", None)
    target_low = info.get("targetLowPrice", None)
    recommendation = info.get("recommendationKey", "N/A")

    # 历史股价走势（近 6 个月）
    hist = ticker.history(period="6mo", interval="1d")
    last_close, pct_change = None, None
    if not hist.empty:
        last_close = hist["Close"].iloc[-1]
        pct_change = (last_close - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100

    # 分析师预测 (新版 API)
    eps_next_q, revenue_next_q = None, None
    try:
        earnings_forecast = ticker.get_earnings_forecasts()
        if earnings_forecast is not None and not earnings_forecast.empty:
            if "earningsAvg" in earnings_forecast.columns:
                eps_next_q = earnings_forecast.loc["avg", "earningsAvg"]
            if "revenueAvg" in earnings_forecast.columns:
                revenue_next_q = earnings_forecast.loc["avg", "revenueAvg"]
    except Exception:
        pass

    # 生成报告
    report = f"""
📊 股票自动分析报告
========================
公司: {name} ({ticker_symbol})
时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

💰 当前价格: {current_price}
📈 目标价区间: {target_low} ~ {target_high}
🎯 平均目标价: {target_mean}
📝 分析师评级: {recommendation.upper()}

📊 最近 6 个月涨跌幅: {pct_change:.2f}% （收盘价 {last_close}）

🔮 分析师预测（下一季度）:
- 每股收益 (EPS): {eps_next_q}
- 营收 (Revenue): {revenue_next_q}

⚠️ 免责声明: 本报告仅供学习和参考，不构成投资建议。
"""
    return report
