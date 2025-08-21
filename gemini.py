import time
import random
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
    for c in response.candidates:
        if getattr(c, "content", None) and c.content.parts:
            for p in c.content.parts:
                t = getattr(p, "text", None)
                if t and t.strip():
                    texts.append(t.strip())
    return "\n".join(texts) if texts else None


MODEL_CANDIDATES = [
    "models/gemini-2.5-pro",
    "models/gemini-1.5-pro",
    "models/gemini-1.5-flash"
]


def call_gemini_with_retry(prompt, hard_timeout_s=300, per_call_timeout_s=30,
                           max_backoff_s=64, temperature=0.7, max_output_tokens=900, debug=False):
    start = time.time()
    attempt = 0
    last_exc = None
    model_idx = 0

    while time.time() - start < hard_timeout_s:
        attempt += 1
        model_name = MODEL_CANDIDATES[model_idx % len(MODEL_CANDIDATES)]
        model_idx += 1
        if debug:
            print(f"🔄 尝试 #{attempt}，模型：{model_name}")

        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={"temperature": temperature, "max_output_tokens": max_output_tokens}
            )
            resp = model.generate_content(prompt, request_options={"timeout": per_call_timeout_s})
            text = safe_extract(resp)
            if text:
                return text
        except Exception as e:
            last_exc = e
            if debug:
                print(f"❌ 调用异常：{e}")

        sleep_s = min(max_backoff_s, 2 ** min(attempt, 6)) + random.uniform(0, 1.0)
        if debug:
            print(f"⏳ 等待 {sleep_s:.1f}s 后重试...")
        time.sleep(sleep_s)

    msg = "⚠️ 生成失败：多模型多次重试后仍无内容。"
    if last_exc and debug:
        msg += f"\n最后错误：{last_exc}"
    return msg


# ================= Gemini AI 日报 =================
def generate_report(stock_data, debug=False):
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
今天是 {today}。以下是最新的收盘价（已精简）：
{stock_data}

请生成一份简短的金融日报，包含：
1) 市场整体趋势
2) 每只股票的简要点评（可合理推测驱动因素）
3) 未来风险或机会提示
要求：中文、专业、精炼。若信息不足，请返回“今日暂无数据”。
"""
    return call_gemini_with_retry(prompt, debug=debug)


def generate_report_macro(data, debug=False):
    today = datetime.now().strftime("%Y-%m-%d")
    latest = data.tail(1).iloc[0].to_dict()
    prompt = f"""
今天是 {today}。以下是最新的宏观资产收盘价：
{latest}

请用中文写一份简短的金融日报，总结：
1. 宏观市场整体趋势
2. 四类资产的表现和简要点评
3. 风险或机会提示
要求专业简洁。
"""
    return call_gemini_with_retry(prompt, debug=debug)
