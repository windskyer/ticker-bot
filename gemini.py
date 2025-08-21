import time
import random
from datetime import datetime
import google.generativeai as genai
from config import cfg

API_KEY = cfg["gemini"]["key"]

# === Gemini API Key 配置 ===
genai.configure(api_key=API_KEY)


MODEL_CANDIDATES = [
    "models/gemini-2.5-pro",   # 你现在用的
    "models/gemini-1.5-pro",   # 稳定/长上下文
    "models/gemini-1.5-flash"  # 更快/更便宜，可做兜底
]


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


def call_gemini_with_retry(
    prompt: str,
    hard_timeout_s: int = 300,         # 整体最长等待时间（建议 2~5 分钟）
    per_call_timeout_s: int = 30,      # 单次请求超时
    max_backoff_s: int = 64,           # 最大退避时间
    temperature: float = 0.7,
    max_output_tokens: int = 1024,
    debug: bool = False
) -> str:
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
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                },
                # 可按需放宽安全阈值，减少“空输出”概率（若你场景纯金融文本）
                # safety_settings={"HARASSMENT": "BLOCK_NONE", ...}
            )

            resp = model.generate_content(
                prompt,
                request_options={"timeout": per_call_timeout_s}
            )
            text = safe_extract(resp)
            if text:
                return text

            # 若被安全策略拦截，打印提示（debug）
            if debug:
                try:
                    d = resp.to_dict()
                    pf = d.get("promptFeedback") or {}
                    br = pf.get("blockReason")
                    if br:
                        print(f"🛡️ 被安全策略拦截：{br}")
                except Exception:
                    pass

        except Exception as e:
            last_exc = e
            if debug:
                print(f"❌ 调用异常：{e}")

        # 指数退避 + 抖动
        sleep_s = min(max_backoff_s, 2 ** min(attempt, 6)) + random.uniform(0, 1.0)
        if debug:
            print(f"⏳ 等待 {sleep_s:.1f}s 后重试...")
        time.sleep(sleep_s)

    # 到达硬超时还没拿到内容
    msg = "⚠️ 生成失败：多模型多次重试后仍无内容。"
    if last_exc and debug:
        msg += f"\n最后错误：{last_exc}"
    return msg


def generate_report(stock_data, debug=False):
    today = datetime.now().strftime("%Y-%m-%d")
    # 控制输入体积，避免过长导致 500/超时；只传需要的信息
    prompt = f"""
今天是 {today}。以下是最新的收盘价（已精简）：
{stock_data}

请生成一份简短的金融日报，包含：
1) 市场整体趋势
2) 每只股票的简要点评（可合理推测驱动因素）
3) 未来风险或机会提示
要求：中文、专业、精炼。若信息不足，请返回“今日暂无数据”。
"""

    content = call_gemini_with_retry(
        prompt,
        hard_timeout_s=300,      # 可按需调整整体最长等待时间
        per_call_timeout_s=30,   # 单次请求超时
        max_backoff_s=64,
        temperature=0.7,
        max_output_tokens=900,
        debug=debug
    )
    print(f"\n[{datetime.now()}] === 金融日报已生成 ===\n")
    return content


# ====== AI日报 ======
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
    content = call_gemini_with_retry(
        prompt,
        hard_timeout_s=300,  # 可按需调整整体最长等待时间
        per_call_timeout_s=30,  # 单次请求超时
        max_backoff_s=64,
        temperature=0.7,
        max_output_tokens=900,
        debug=debug
    )
    print(f"\n[{datetime.now()}] === 金融日报已生成 ===\n")
    return content
