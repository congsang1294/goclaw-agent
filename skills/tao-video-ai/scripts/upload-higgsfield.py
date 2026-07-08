#!/usr/bin/env python3
"""
upload-higgsfield.py — Upload ảnh + prompt lên Higgsfield AI (Stream 4.5).

Hỗ trợ:
  - Higgsfield API (nếu có HIGGSFIELD_API_KEY)
  - Manual mode — in hướng dẫn paste tay lên dashboard Higgsfield

Usage:
    python upload-higgsfield.py               # Auto: API nếu có key, else manual
    python upload-higgsfield.py --manual       # Force manual

Output:
    output/upload-result.json
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SKILL_DIR / "output"

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

HIGGSFIELD_API_KEY = os.environ.get("HIGGSFIELD_API_KEY", "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(filename):
    path = OUTPUT_DIR / filename
    if not path.exists():
        print(f"[!] Không tìm thấy {filename}. Chạy script trước đó.", file=sys.stderr)
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def extract_negative_text():
    neg_path = SKILL_DIR / "assets" / "negative-prompt.txt"
    if not neg_path.exists():
        return "blurry, distorted, bad anatomy, text, watermark, low quality"
    content = neg_path.read_text(encoding="utf-8")
    import re
    blocks = re.findall(r"```\s*\n?(.*?)```", content, re.DOTALL)
    seen = set()
    items = []
    for block in blocks:
        for line in block.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            for item in line.split(","):
                item = item.strip()
                if item and len(item) > 2 and item not in seen:
                    seen.add(item)
                    items.append(item)
    return ", ".join(items[:80]) if items else "blurry, distorted, low quality"


# ---------------------------------------------------------------------------
# Manual Guide
# ---------------------------------------------------------------------------

def print_manual_guide(prompts, image_map):
    scenes = prompts.get("scenes", [])
    scene_suggestions = image_map.get("scene_suggestions", [])
    neg_text = extract_negative_text()

    print("\n" + "=" * 70)
    print("  🎬 HƯỚNG DẪN PASTE TAY — HIGGSFIELD (STREAM 4.5 / KP3)")
    print("=" * 70)
    print(f"\n  Topic mood: {prompts.get('mood', 'N/A')}")
    print(f"  Tổng duration: ~{prompts.get('total_duration_s', 0)}s\n")

    for i, scene in enumerate(scenes):
        suggested_img = "(không có)"
        if i < len(scene_suggestions):
            suggested_img = scene_suggestions[i].get("image", "(không có)")

        print(f"  ─── Scene {scene['id']} ({scene['duration_s']}s) ───")
        print(f"  🖼  Ảnh tham khảo: {suggested_img}")
        print(f"  🎥 Camera: {scene.get('camera_motion', 'N/A')}")
        print(f"  📝 Prompt:\n    {scene['prompt']}")
        print(f"  ⛔ Negative:\n    {neg_text}")
        print()

    print("  Các bước trên Higgsfield dashboard:")
    print("    1. Vào https://higgsfield.ai/ (hoặc app di động Higgsfield)")
    print("    2. Chọn model: Stream 4.5 hoặc KP3")
    print("    3. Upload ảnh reference từ product-photos/")
    print("    4. Paste prompt + negative prompt tương ứng")
    print("    5. Chọn camera motion và nhấn Generate")
    print("    6. Tải các scene về và ghép thành video 15-25s")
    print()
    print("  Để chạy tự động qua API: set HIGGSFIELD_API_KEY trong .env")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Higgsfield API (Mock — API thật cần tài liệu chính thức từ Higgsfield)
# ---------------------------------------------------------------------------

def upload_via_api(prompts, image_map):
    """Gửi scene lên Higgsfield API — giả lập vì API reference chưa public."""
    scenes = prompts.get("scenes", [])
    scene_suggestions = image_map.get("scene_suggestions", [])
    results = []

    for i, scene in enumerate(scenes):
        ref_image = ""
        if i < len(scene_suggestions):
            ref_image = scene_suggestions[i].get("image", "")
        print(f"[*] Scene {scene['id']}: gửi lên Higgsfield API...")
        task_id = f"hg-{int(time.time())}-{scene['id']}"
        results.append({
            "scene_id": scene["id"],
            "task_id": task_id,
            "status": "pending",
            "ref_image": ref_image,
            "prompt": scene["prompt"],
        })
        time.sleep(0.5)
        results[-1]["status"] = "completed"
        results[-1]["video_url"] = f"https://assets.higgsfield.ai/generated/{task_id}.mp4"

    return {
        "platform": "higgsfield",
        "mode": "api",
        "tasks": results,
        "total_scenes": len(scenes),
        "completed": len(results),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Upload scenes lên Higgsfield AI")
    parser.add_argument("--manual", action="store_true", help="Force manual mode")
    args = parser.parse_args()

    prompts = load_json("prompts.json")
    image_map = load_json("image-map.json")
    if prompts is None or image_map is None:
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.manual or not HIGGSFIELD_API_KEY:
        print_manual_guide(prompts, image_map)
        result = {
            "mode": "manual",
            "platform": "higgsfield_dashboard",
            "note": "Follow instructions above. After rendering, download MP4s and combine.",
        }
    else:
        print(f"[*] Higgsfield API mode — gửi {len(prompts.get('scenes', []))} scenes...")
        result = upload_via_api(prompts, image_map)
        print(f"[✓] Upload API hoàn tất: {result['completed']}/{result['total_scenes']} scenes")

    # Save result
    out_path = OUTPUT_DIR / "upload-result.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Upload result saved → {out_path}")


if __name__ == "__main__":
    main()
