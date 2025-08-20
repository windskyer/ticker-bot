import time
import json
from datetime import datetime
import google.generativeai as genai
from config import cfg

API_KEY = cfg["gemini"]["key"]

# === Gemini API Key 配置 ===
genai.configure(api_key=API_KEY)


def safe_extract(response):
    """从 Gemini response 里安全提取文本"""
    if not hasattr(response, "candidates") or not response.candidates:
        return None

    texts = []
    for cand in response.candidates:
        if hasattr(cand, "content") and cand.content.parts:
            for part in cand.content.parts:
                if hasattr(part, "text") and part.text.strip():
                    texts.append(part.text.strip())

    return "\n".join(texts) if texts else None


def generate_report(stock_data, max_retries=10, debug=False, wait=5):
    """
    调用 Gemini 生成日报，直到有内容为止
    :param stock_data: 股票数据(dict 或 str)
    :param max_retries: 最大重试次数
    :param debug: 是否打印调试信息
    :param wait: 每次重试之间等待秒数
    """
    model = genai.GenerativeModel("models/gemini-2.5-pro")

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
今天是 {today}，以下是最新的美股收盘价：
{stock_data}

请帮我生成一份简短的金融日报，包括：
1. 市场整体趋势
2. 每只股票的简要点评（涨跌原因可合理推测）
3. 未来风险或机会提示

要求中文，简洁专业。
生成文本格式为Markdown。
如果无法生成完整内容，请至少输出“今日暂无数据”。
"""

    content = None
    attempt = 0

    while not content and attempt < max_retries:
        attempt += 1
        if debug:
            print(f"🔄 正在尝试第 {attempt} 次调用 Gemini...")

        response = model.generate_content(prompt)
        content = safe_extract(response)

        if not content:
            if debug:
                print("⚠️ 没有内容，等待后重试...")
            time.sleep(wait)

    if not content:
        content = "⚠️ 多次尝试后仍未生成内容，今日暂无数据。"

    # 输出日志
    if debug:
        print("\n=== 最终 RAW RESPONSE ===")
        try:
            print(json.dumps(response.to_dict(), indent=2, ensure_ascii=False))
        except Exception:
            print(response)

    print(f"\n[{datetime.now()}] === 金融日报 ===\n")
    print(content)

    return content
