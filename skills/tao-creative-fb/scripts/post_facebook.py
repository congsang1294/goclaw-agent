#!/usr/bin/env python3
"""
post_facebook.py — Đăng ảnh + caption lên Facebook Page.
Dùng file local, không cần URL public.

Usage:
  python post_facebook.py --image "output/anh.png" --caption "Nội dung"
  python post_facebook.py --image "output/anh.png" --caption "..." --dry-run
"""

import os, sys, json, time, argparse
# Thêm path chứa requests library
sys.path.insert(0, "/app/data/skills-store/tao-creative-fb/1/pylib")
import requests
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "dry_run_output")
load_dotenv(ENV_PATH)

GRAPH_API = "https://graph.facebook.com/v21.0"

def post_photo_to_page(access_token, page_id, image_path, caption, alt_text=None):
    """Upload file ảnh local + caption lên FB Page qua multipart POST."""
    url = f"{GRAPH_API}/{page_id}/photos"

    with open(image_path, "rb") as f:
        files = {"source": f}
        data = {"caption": caption, "access_token": access_token}
        if alt_text:
            data["alt_text_custom"] = alt_text

        for attempt in range(2):
            try:
                resp = requests.post(url, files=files, data=data, timeout=120)
                result = resp.json()
                if "id" in result:
                    post_id = result["id"]
                    post_url = f"https://facebook.com/{page_id}/posts/{post_id}"
                    return {"success": True, "post_id": post_id, "post_url": post_url}
                elif "error" in result:
                    err_msg = result["error"].get("message", str(result))
                    err_code = result["error"].get("code", 0)
                    if attempt == 0 and err_code in (1, 2, 4, 17, 341):
                        time.sleep(3)
                        continue
                    return {"success": False, "error": err_msg, "error_code": err_code}
                return {"success": False, "error": f"Response không có id: {result}"}
            except requests.exceptions.Timeout:
                if attempt == 0:
                    time.sleep(3)
                else:
                    return {"success": False, "error": "Timeout sau 2 lần"}
            except Exception as e:
                return {"success": False, "error": str(e)}
    return {"success": False, "error": "Hết lần retry."}

def main():
    parser = argparse.ArgumentParser(description="Đăng bài lên Facebook Page")
    parser.add_argument("--image", default="", help="Đường dẫn file ảnh local")
    parser.add_argument("--image_url", default="", help="URL/tên file ảnh (tự tìm local)")
    parser.add_argument("--caption", required=True, help="Nội dung caption")
    parser.add_argument("--alt-text-custom", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "true").lower() == "true"
    access_token = os.environ.get("FB_ACCESS_TOKEN", "")
    page_id = os.environ.get("FB_PAGE_ID", "")
    page_name = os.environ.get("FB_PAGE_NAME", "")

    image_path = args.image
    # Nếu --image trống, thử dùng --image_url
    if not image_path and args.image_url:
        basename = os.path.basename(args.image_url)
        for try_path in [os.path.join(SCRIPT_DIR, "output", basename), os.path.join("output", basename), basename]:
            abs_p = os.path.join(SCRIPT_DIR, try_path) if not os.path.isabs(try_path) else try_path
            if os.path.isfile(abs_p):
                image_path = abs_p
                break
        if not image_path:
            image_path = basename  # fallback
    if not os.path.isfile(image_path):
        # Thử tìm trong thư mục output/
        alt = os.path.join(SCRIPT_DIR, "output", os.path.basename(image_path))
        if os.path.isfile(alt):
            image_path = alt
        else:
            print(json.dumps({"success": False, "error": f"Không tìm thấy file ảnh: {image_path}"}))
            sys.exit(1)

    if not dry_run:
        if not access_token:
            print(json.dumps({"success": False, "error": "Thiếu FB_ACCESS_TOKEN"}))
            sys.exit(1)
        if not page_id:
            print(json.dumps({"success": False, "error": "Thiếu FB_PAGE_ID"}))
            sys.exit(1)

    if dry_run:
        fake_id = f"dry_run_{int(time.time())}"
        result = {
            "success": True, "post_id": fake_id,
            "post_url": f"https://facebook.com/{page_id}/posts/{fake_id}",
            "page_name": page_name, "dry_run": True,
            "image_local": image_path,
            "caption_preview": args.caption[:200] + "..." if len(args.caption) > 200 else args.caption,
            "note": "DRY_RUN: giả lập thành công."
        }
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, f"post_dry_run_{int(time.time())}.json"), "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0)

    result = post_photo_to_page(access_token, page_id, image_path, args.caption, args.alt_text_custom)
    if result["success"]:
        print(json.dumps({**result, "page_name": page_name, "dry_run": False}, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
