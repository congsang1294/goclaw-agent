#!/usr/bin/env python3
"""
post_video.py — Đăng video lên Facebook Reels qua Graph API.

Usage:
    python3 scripts/post_video.py --video output/final.mp4 --caption "Nội dung"
"""

import argparse
import json
import mimetypes
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("[FAIL] Thiếu requests. Chạy: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
    _env = Path(__file__).resolve().parent.parent / ".env"
    if _env.exists():
        load_dotenv(_env)
except ImportError:
    pass

FB_GRAPH_VERSION = os.environ.get("FB_GRAPH_VERSION", "v22.0")
FB_TIMEOUT = int(os.environ.get("FB_TIMEOUT_SECONDS", "120"))


def main():
    parser = argparse.ArgumentParser(description="Đăng video Facebook Reels")
    parser.add_argument("--video", required=True, help="File MP4")
    parser.add_argument("--caption", default="", help="Caption bài đăng")
    parser.add_argument("--dry-run", action="store_true", help="Không đăng thật")
    args = parser.parse_args()

    page_id = os.environ.get("FB_PAGE_ID")
    page_token = os.environ.get("FB_PAGE_TOKEN")
    if not page_id or not page_token:
        print("[FAIL] Thiếu FB_PAGE_ID hoặc FB_PAGE_TOKEN", file=sys.stderr)
        sys.exit(1)

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"[FAIL] Không tìm thấy {video_path}", file=sys.stderr)
        sys.exit(2)

    caption = args.caption[:2200] if args.caption else ""

    if args.dry_run or os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes"):
        print(f"[DRY RUN] Sẽ đăng: {video_path}")
        print(f"[DRY RUN] Caption: {caption[:100]}...")
        print(json.dumps({"ok": True, "dry_run": True, "video": str(video_path)}))
        sys.exit(0)

    # Upload video lên Facebook Reels
    url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{page_id}/video_reels"
    mime_type, _ = mimetypes.guess_type(str(video_path))
    if not mime_type:
        mime_type = "video/mp4"

    print(f"[FB] Uploading video ({video_path.stat().st_size // 1024}KB)...", flush=True)

    try:
        with open(video_path, "rb") as f:
            resp = requests.post(
                url,
                params={"access_token": page_token},
                files={"source": (video_path.name, f, mime_type)},
                data={"description": caption, "title": caption[:100] or "Video"},
                timeout=FB_TIMEOUT,
            )
    except requests.exceptions.Timeout:
        print("[FAIL] Facebook upload timeout", file=sys.stderr)
        sys.exit(3)
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Facebook request error: {e}", file=sys.stderr)
        sys.exit(4)

    result = resp.json()
    if resp.status_code != 200 or "id" not in result:
        print(f"[FAIL] Facebook error: {json.dumps(result, ensure_ascii=False)[:500]}", file=sys.stderr)
        sys.exit(5)

    print(f"[OK] Video uploaded. ID: {result['id']}", flush=True)

    # Lấy link Reels
    reel_id = result.get("id", "").split("_")[-1] if "_" in result.get("id", "") else result.get("id", "")
    feed_url = f"https://www.facebook.com/reel/{reel_id}" if reel_id else ""

    output = {"ok": True, "post_id": result.get("id"), "reel_url": feed_url}
    print(json.dumps(output, ensure_ascii=False))
    print(f"[OK] Link: {feed_url}", flush=True)


if __name__ == "__main__":
    main()
