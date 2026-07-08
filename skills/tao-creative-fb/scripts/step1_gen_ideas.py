#!/usr/bin/env python3
"""step1_gen_ideas.py — Gen 3 y tuong + full tin nhan tra loi. Bot COPY nguyen van."""
import os, json, sys, re
from openai import OpenAI
from dotenv import load_dotenv

SD = "/app/workspace/ga-thanh-thoi-bot"
ENV = os.path.join(SD, ".env")
STATE = os.path.join(SD, "output", "cron_state.json")
load_dotenv(ENV)

bv_path = os.path.join(SD, "brand-voice.md")
voice = ""
if os.path.isfile(bv_path):
    with open(bv_path, "r") as f: voice = f.read()[:1500]

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
prompt = """Bạn là Gà Thảnh Thơi, trợ lý Google Ads. Sinh 3 ý tưởng caption Facebook.

SẢN PHẨM: Google Ads Match Type Converter (tool.congsang.info.vn) - chuyển keyword Broad/Phrase/Exact.

3 Ý TƯỞNG - mỗi ý 1 góc: pain, solution, social proof.

LUẬT BẮT BUỘC CHO MỖI Ý TƯỞNG:
- Mở bài CHỈ được 1 trong 4: "Mình từng...", "Mình hay thấy...", "Mình mở Excel ra...", "Nói thật là..."
- Xưng: "mình" hoặc "Gà"
- Gọi người đọc: "anh em" (KHÔNG dùng "bạn", "bạn đọc", "người dùng")

CẤM TUYỆT ĐỐI - nếu vi phạm là SAI:
- "Bạn" ở đầu câu
- "Nhiều người thường" (hoặc "nhiều người")
- "Đừng lo!", "Hãy thử ngay!"
- synergy, leverage, hàng đầu, số 1
- Emoji, icon, ký tự đặc biệt
- Hứa kết quả, cam kết ra đơn

Description CHỈ 1 câu, ngắn gọn, đúng brand voice.
CTA: "Anh em ghé vào xem thử" (nếu có).

Trả JSON array CHÍNH XÁC format này, KHÔNG THÊM GÌ KHÁC:
[{"title":"Mình từng...","angle":"pain","description":"Mình từng [trải nghiệm]. Anh em ghé vào xem thử."}]"""

try:
    r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], max_tokens=1024, temperature=0.7)
    text = r.choices[0].message.content.strip()
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if match: text = match.group()
    ideas = json.loads(text)
    if isinstance(ideas, dict):
        ideas = list(ideas.values())
except Exception as e:
    print(json.dumps({"success":False,"error":str(e)}))
    sys.exit(1)

state = {"status":"PENDING_SELECTION","ideas":[],"selected_index":None,"generated_content":None,"fb_post_url":""}
state["ideas"] = ideas
os.makedirs(os.path.dirname(STATE), exist_ok=True)
with open(STATE, "w") as f: json.dump(state, f, ensure_ascii=False)

# Tao san tin nhan hoan chinh
lines = ["Chào sáng anh Sáng. Hôm nay em có 3 ý tưởng về Google Ads Match Type Converter (tool.congsang.info.vn), anh chọn giúp em nhé:"]
lines.append("")
for idx, i in enumerate(ideas, 1):
    lines.append(f"{idx}. {i['title']} — {i['description']}")
lines.append("")
lines.append("Anh chọn số mấy để em gen ảnh với caption cho anh duyệt?")

# In ra text thuan - bot se tu dung lam response
print("\n".join(lines))
