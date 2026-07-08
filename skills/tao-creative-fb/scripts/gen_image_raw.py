#!/usr/bin/env python3
"""
gen_image_raw.py — GỌI OPENAI API TẠO ẢNH GỐC (có mạng)

Chức năng: Gọi OpenAI gpt-image-2, lưu ảnh gốc xuống output/raw_{timestamp}.png
Output JSON: {"success": true, "raw_path": "output/raw_123.png"}

GÀ dùng exec chạy script này, sau đó chạy gen_image.py (offline) để xử lý Pillow.
"""

import os, sys, json, time, base64, re
from openai import OpenAI
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

load_dotenv(ENV_PATH)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gọi OpenAI tạo ảnh gốc")
    parser.add_argument("--prompt", default="", help="Prompt mô tả ảnh. Nếu trống sẽ dùng prompt mặc định theo góc.")
    parser.add_argument("--quality", default="low", choices=["low", "medium", "high"])
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--angle", default="pain", choices=["pain", "solution", "proof"])
    parser.add_argument("--slug", default="", help="Tên file gốc")
    args = parser.parse_args()

    prompt = args.prompt
    if not prompt or prompt.strip() == "":
        default_prompts = {
            "pain": "Realistic photo, candid, cinematic lighting. A Vietnamese business owner sitting at a cluttered desk late at night, tired, rubbing temples. Laptop screen glowing. Coffee cups, papers scattered. No text in image.",
            "solution": "Realistic photo, natural daylight. A Vietnamese freelancer working at a cozy coffee shop. Laptop open, calm expression. Warm tones. Lifestyle photography. No text in image.",
            "proof": "Realistic photo, candid. Close-up of a smartphone held by a Vietnamese person showing positive notification. Blurred background. Warm evening light. No text in image."
        }
        prompt = default_prompts.get(args.angle, default_prompts["pain"])

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print(json.dumps({"success": False, "error": "Thiếu OPENAI_API_KEY"}))
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    for attempt in range(2):
        try:
            resp = client.images.generate(
                model="gpt-image-2",
                prompt=prompt,
                n=1,
                size=args.size,
                quality=args.quality,
            )
            b64 = resp.data[0].b64_json
            ts = int(time.time())
            # Dùng slug nếu có, nếu không dùng "post"
            slug = args.slug if args.slug and args.slug.strip() else "post"
            safe_slug = re.sub(r'[^a-zA-Z0-9-]', '', slug.replace(" ", "-").lower())[:50] or "post"
            raw_path = os.path.join(OUTPUT_DIR, f"{safe_slug}-{ts}.png")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open(raw_path, "wb") as f:
                f.write(base64.b64decode(b64))

            print(json.dumps({"success": True, "raw_path": os.path.abspath(raw_path)}))
            sys.exit(0)

        except Exception as e:
            if attempt == 0 and ("rate" in str(e).lower() or "timeout" in str(e).lower()):
                time.sleep(3)
            else:
                print(json.dumps({"success": False, "error": str(e)[:200]}))
                sys.exit(1)

    print(json.dumps({"success": False, "error": "Hết lần retry."}))
    sys.exit(1)

if __name__ == "__main__":
    main()
