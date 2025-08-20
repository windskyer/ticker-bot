from datetime import datetime
import google.generativeai as genai
from config import cfg

API_KEY = cfg["gemini"]["key"]

# === Gemini API Key 配置 ===
genai.configure(api_key=API_KEY)


# ================= 调用 google GPT 总结 =================
def generate_report(stock_data):
    # 选择模型（推荐 gemini-pro）
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
"""

    print(f"[{datetime.now()}] === 金融日报提示词 ===\n {prompt} \n\n")
    # 生成内容
    response = model.generate_content(prompt)

    # 保险的取值方式
    if response.candidates and response.candidates[0].content.parts:
        content = response.candidates[0].content.parts[0].text
    else:
        content = "⚠️ 没有生成内容"

    return content.strip()
