#!/usr/bin/env python3
"""gen_full_post.py — Gen caption + anh + upload trong 1 lan duy nhat."""
import os, sys, json, time, base64, shutil, argparse, re
from openai import OpenAI
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
PUBLIC_IMAGE_DIR = "/app/images"
BASE_URL = "https://tool.congsang.info.vn/images"
load_dotenv(ENV_PATH)

def gen_caption(api_key, idea, angle, mode):
    client = OpenAI(api_key=api_key)
    sp = """Bạn là trợ lý viết caption Facebook cho anh Sáng (chủ của Google Ads Match Type Converter - tool.congsang.info.vn).

TUÂN THỦ NGHIÊM NGẶT brand voice sau:

XƯNG HÔ: Tự xưng "mình" hoặc "Gà". Gọi người đọc "anh em", "bạn".

GIỌNG VIẾT: Viết như người đã làm thật, sai thật, mất tiền thật, rồi ngồi kể lại cho anh em nghe. Gần gũi, thẳng thắn, đời thường, có trải nghiệm.

MỞ BÀI (CHỌN 1 TRONG 4):
1. "Mình từng..." — kể trải nghiệm thật
2. "Mình hay thấy..." — quan sát thị trường
3. "Mình mở Excel ra..." — cảnh cụ thể
4. "Nói thật là..." — nhận xét đời thường

CẤM TUYỆT ĐỐI:
- KHÔNG mở đầu bằng "Bạn" (ví dụ: "Bạn có thấy..." là SAI)
- KHÔNG dùng: "Bạn có biết rằng", "Trong thời đại hiện nay", "Thị trường đầy rẫy", "Đừng lo!", "Hãy thử ngay!"
- KHÔNG dùng: synergy, leverage, maximize, optimize, hàng đầu, số 1, giải pháp đột phá
- KHÔNG hứa kết quả, không cam kết ra đơn, không dìm đối thủ
- KHÔNG dùng emoji, icon, ký tự đặc biệt
- KHÔNG viết kiểu báo, kiểu quảng cáo, kiểu bán hàng

DẪN DẮT: Cảnh quen → cái khó → vì sao khó → xác nhận cảm giác → giải pháp. KHÔNG đưa giải pháp quá sớm.

CTA: Nhẹ, không ép. "Anh em ghé vào xem thử", "Nếu đang mất thời gian ở đoạn này thì thử xem có hợp không"

ĐỘ DÀI: 80-150 từ. CHỈ trả caption, không giải thích, không thêm thắt."""

    up = f"Viet caption Facebook. San pham: Google Ads Match Type Converter (tool.congsang.info.vn). Y tuong: {idea}. Goc: {angle}. Mode: {'organic' if mode=='1' else 'ads'}. 80-150 tu."
    try:
        r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"system","content":sp},{"role":"user","content":up}], max_tokens=1024, temperature=0.7)
        caption = r.choices[0].message.content.strip()
        return caption, len(caption.split())
    except Exception as e:
        return None, str(e)

def gen_image(api_key, prompt, angle="pain", slug="post"):
    client = OpenAI(api_key=api_key)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = int(time.time())
    # Slug từ ý tưởng, chỉ lấy 4 từ đầu, bỏ dấu
    safe_slug = re.sub(r'[^a-zA-Z0-9-]', '', slug.replace(" ", "-").lower())[:50] or "post"
    raw_path = os.path.join(OUTPUT_DIR, f"{safe_slug}-{ts}.png")
    if not prompt or prompt.strip() == "":
        prompts = {"pain":"Realistic photo, candid, cinematic lighting. A Vietnamese business owner sitting at a cluttered desk late at night, tired, rubbing temples. Laptop screen glowing. Coffee cups, papers scattered. No text in image.","solution":"Realistic photo, natural daylight. A Vietnamese freelancer working at a cozy coffee shop. Laptop open, calm expression. Warm tones. Lifestyle photography. No text in image.","proof":"Realistic photo, candid. Close-up of a smartphone held by a Vietnamese person showing positive notification. Blurred background. Warm evening light. No text in image."}
        prompt = prompts.get(angle, prompts["pain"])
    for attempt in range(2):
        try:
            r = client.images.generate(model="gpt-image-2", prompt=prompt, n=1, size="1024x1024", quality="low")
            with open(raw_path, "wb") as f:
                f.write(base64.b64decode(r.data[0].b64_json))
            return raw_path
        except Exception as e:
            if attempt == 0 and ("rate" in str(e).lower() or "timeout" in str(e).lower()):
                time.sleep(3)
            else:
                return None
    return None

def upload_image(source_path):
    os.makedirs(PUBLIC_IMAGE_DIR, exist_ok=True)
    filename = os.path.basename(source_path)
    shutil.copy2(source_path, os.path.join(PUBLIC_IMAGE_DIR, filename))
    return f"{BASE_URL}/{filename}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idea", required=True)
    parser.add_argument("--angle", default="pain", choices=["pain","solution","proof"])
    parser.add_argument("--mode", default="1", choices=["1","2"])
    args = parser.parse_args()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print(json.dumps({"success":False,"error":"Thieu OPENAI_API_KEY"}))
        sys.exit(1)
    # Tạo slug từ idea
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', args.idea.lower()).strip('-')[:60] or "post"

    caption, wc = gen_caption(api_key, args.idea, args.angle, args.mode)
    if caption is None:
        print(json.dumps({"success":False,"error":f"Loi caption: {wc}"}))
        sys.exit(1)
    prompts = {"pain":"Realistic photo, candid, cinematic lighting. A Vietnamese business owner sitting at a cluttered desk late at night, tired, rubbing temples. Laptop screen glowing. Coffee cups, papers scattered. No text in image.","solution":"Realistic photo, natural daylight. A Vietnamese freelancer working at a cozy coffee shop. Laptop open, calm expression. Warm tones. Lifestyle photography. No text in image.","proof":"Realistic photo, candid. Close-up of a smartphone held by a Vietnamese person showing positive notification. Blurred background. Warm evening light. No text in image."}
    raw_path = gen_image(api_key, prompts.get(args.angle, prompts["pain"]), args.angle, slug)
    if raw_path is None:
        print(json.dumps({"success":False,"error":"Loi gen anh","caption":caption}))
        sys.exit(1)
    image_url = upload_image(raw_path)
    # Ghi state lock: approved=false, user chua duyet
    import json as _sj
    _sj.dump({"status":"PENDING_APPROVAL","approved":False,"caption":caption,"image_path":os.path.abspath(raw_path),"image_url":image_url}, open(os.path.join(OUTPUT_DIR,"cron_state.json"),"w"), ensure_ascii=False)
    json_out = json.dumps({"success":True,"caption":caption,"word_count":wc,"image_path":os.path.abspath(raw_path),"image_url":image_url,"angle":args.angle}, ensure_ascii=False)
    # In JSON cho bot doc
    print(json_out)
    # In plain text cho bot tu dong lam response
    print("---TEXT---")
    print(f"🖼 Em đã gen ảnh + caption xong rồi ạ.")
    print(f"")
    print(f"📝 {caption}")
    print(f"")
    print(f"Anh thấy ổn chưa? OK em đăng, Đổi em gen lại nhé.")

if __name__ == "__main__":
    main()
