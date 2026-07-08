#!/usr/bin/env python3
"""step2_gen_and_ask.py — 1 lan exec: gen caption, anh, upload, save file. xong het."""
import os, sys, json, time, base64, shutil, argparse, re
from openai import OpenAI
from dotenv import load_dotenv

SD = "/app/workspace/ga-thanh-thoi-bot"
ENV = os.path.join(SD, ".env")
OUTPUT = os.path.join(SD, "output")
PUBLIC_IMAGE_DIR = "/app/images"
BASE_URL = "https://tool.congsang.info.vn/images"
load_dotenv(ENV)

# Luu vao file nay de fb_post.py doc
STATE_FILE = os.path.join(OUTPUT, "last_post.json")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idea", required=True)
    parser.add_argument("--angle", default="pain", choices=["pain","solution","proof"])
    parser.add_argument("--mode", default="1", choices=["1","2"])
    args = parser.parse_args()
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        print(json.dumps({"success":False,"error":"Thieu OPENAI_API_KEY"})); sys.exit(1)

    slug = re.sub(r'[^a-zA-Z0-9]+', '-', args.idea.lower()).strip('-')[:40] or "post"
    client = OpenAI(api_key=key)

    # Gen caption
    sp = """Ban la tro ly viet caption Facebook cho anh Sang (tool.congsang.info.vn). Brand voice: xuong minh/Ga, goi anh em. Viet nhu nguoi da lam that. Mo bai: Minh tung..., Minh hay thay..., Minh mo Excel ra..., Noi that la... CAM: Ban o dau cau, Nhieu nguoi thuong, emoji, hua ket qua. CTA nhe: Anh em ghe vao xem thu. CHI tra caption 80-150 tu."""
    try:
        r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"system","content":sp},{"role":"user","content":f"Viet caption. San pham: Google Ads Match Type Converter. Y tuong: {args.idea}. Goc: {args.angle}. 80-150 tu."}], max_tokens=1024, temperature=0.7)
        caption = r.choices[0].message.content.strip()
    except Exception as e:
        print(json.dumps({"success":False,"error":f"Loi caption: {str(e)[:100]}"})); sys.exit(1)

    wc = len(caption.split())

    # Gen anh
    prompts = {"pain":"Realistic photo, candid. Vietnamese business owner at cluttered desk late at night, tired. Laptop glow. No text.","solution":"Realistic photo, daylight. Vietnamese freelancer at coffee shop, laptop open, calm. No text.","proof":"Realistic photo, candid. Smartphone showing positive notification. Blurred background. No text."}
    ts = int(time.time())
    raw_path = os.path.join(OUTPUT, f"{slug}-{ts}.png")
    os.makedirs(OUTPUT, exist_ok=True)
    try:
        r = client.images.generate(model="gpt-image-2", prompt=prompts.get(args.angle, prompts["pain"]), n=1, size="1024x1024", quality="low")
        with open(raw_path, "wb") as f: f.write(base64.b64decode(r.data[0].b64_json))
    except Exception as e:
        print(json.dumps({"success":False,"error":f"Loi anh: {str(e)[:100]}","caption":caption})); sys.exit(1)

    # Upload
    os.makedirs(PUBLIC_IMAGE_DIR, exist_ok=True)
    shutil.copy2(raw_path, os.path.join(PUBLIC_IMAGE_DIR, os.path.basename(raw_path)))
    image_url = f"{BASE_URL}/{os.path.basename(raw_path)}"

    # Ghi file de fb_post.py doc
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"image_url": image_url, "caption": caption, "ts": ts}, f, ensure_ascii=False)

    print(json.dumps({"success":True,"caption":caption,"word_count":wc,"image_path":os.path.abspath(raw_path),"image_url":image_url}, ensure_ascii=False))

if __name__ == "__main__":
    main()
