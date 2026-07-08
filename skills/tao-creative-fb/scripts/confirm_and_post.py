#!/usr/bin/env python3
"""
confirm_and_post.py — Post Facebook. BẮT BUỘC truyền --image và --caption.
Chỉ gọi script này khi user nói OK. KHÔNG tự động tìm file.
"""
import os, sys, json, subprocess, datetime

WORKSPACE = "/app/workspace/ga-thanh-thoi-bot"
SKILLS_DIR = "/app/data/skills-store/tao-creative-fb/1/scripts"
POST_SCRIPT = os.path.join(SKILLS_DIR, "post_facebook.py")

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--image", required=True)
parser.add_argument("--caption", required=True)
args = parser.parse_args()

image = args.image
caption = args.caption

if not os.path.isfile(image):
    alt = os.path.join(WORKSPACE, "output", os.path.basename(image))
    if os.path.isfile(alt):
        image = alt
    else:
        print(json.dumps({"success": False, "error": f"Không tìm thấy ảnh: {image}"}))
        sys.exit(1)

env = {**os.environ, "DRY_RUN": "false"}
result = subprocess.run(
    [sys.executable, POST_SCRIPT, "--image", image, "--caption", caption],
    capture_output=True, text=True, cwd=WORKSPACE, env=env
)

try:
    fb_result = json.loads(result.stdout.strip() or result.stderr.strip())
except:
    print(json.dumps({"success": False, "error": f"Lỗi post: {(result.stdout or result.stderr)[:200]}"}))
    sys.exit(1)

if fb_result.get("success"):
    print(json.dumps({**fb_result, "posted_at": datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}, ensure_ascii=False))
else:
    print(json.dumps({"success": False, "error": fb_result.get("error", "Lỗi không xác định")}))
