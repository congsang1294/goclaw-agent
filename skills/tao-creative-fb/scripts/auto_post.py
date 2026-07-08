#!/usr/bin/env python3
"""
auto_post.py — Tự động post bài lên Facebook. KHÔNG cần AI can thiệp.
Usage: python3 auto_post.py --image_url "URL" --caption "caption"

Script này được thiết kế để chạy trực tiếp, không qua AI.
Nó sẽ post lên Facebook và trả link.
"""

import os, sys, json, subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POST_SCRIPT = os.path.join(SCRIPT_DIR, "post_facebook.py")
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")

# Load .env to ensure DRY_RUN=false
from dotenv import load_dotenv
load_dotenv(ENV_PATH)

# Force DRY_RUN=false
os.environ["DRY_RUN"] = "false"

import argparse
parser = argparse.ArgumentParser(description="Auto post Facebook")
parser.add_argument("--image_url", required=True)
parser.add_argument("--caption", required=True)
args = parser.parse_args()

result = subprocess.run(
    [sys.executable, POST_SCRIPT, "--image_url", args.image_url, "--caption", args.caption],
    capture_output=True, text=True, cwd=SCRIPT_DIR,
    env={**os.environ, "DRY_RUN": "false"}
)

out = result.stdout.strip() or result.stderr.strip()
print(out)
