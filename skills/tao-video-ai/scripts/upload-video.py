#!/usr/bin/env python3
"""
upload-video.py — Upload ảnh + prompt lên AI Video platform.

Hỗ trợ:
  - Kling AI API (api.klingai.com) — PRIMARY, có API thật, cần KLING_API_KEY
  - Manual mode — in hướng dẫn paste tay lên dashboard Kling / Runway / Higgsfield

Usage:
    # Tự động upload lên Kling (cần set KLING_API_KEY + KLING_SECRET_KEY)
    python upload-video.py

    # Chọn platform khác
    python upload-video.py --platform kling

    # Manual mode
    python upload-video.py --manual

Output:
    output/upload-result.json  — kết quả render hoặc hướng dẫn
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# Load .env nếu có
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

# ============================================================
# Kling AI API config
# Docs: https://docs.klingai.com/api-reference/
# ============================================================
KLING_API_BASE = os.environ.get("KLING_API_BASE", "https://api.klingai.com")
KLING_API_KEY = os.environ.get("KLING_API_KEY", "")
KLING_SECRET_KEY = os.environ.get("KLING_SECRET_KEY", "")


def load_prompts() -> dict:
    prompts_path = OUTPUT_DIR / "prompts.json"
    if not prompts_path.exists():
        print(f"[!] Không tìm thấy {prompts_path}. Chạy gen-prompt.py trước.", file=sys.stderr)
        return None
    return json.loads(prompts_path.read_text(encoding="utf-8"))


def load_image_map() -> dict:
    map_path = OUTPUT_DIR / "image-map.json"
    if not map_path.exists():
        print(f"[!] Không tìm thấy {map_path}. Chạy list-images.py trước.", file=sys.stderr)
        return None
    return json.loads(map_path.read_text(encoding="utf-8"))


def extract_negative_prompt_text() -> str:
    """Đọc negative-prompt.txt và chỉ lấy nội dung blocklist (bỏ qua markdown)."""
    neg_path = PROJECT_ROOT / "assets" / "negative-prompt.txt"
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
                    if not any(kw in item.lower() for kw in ["bash ", "pip ", "python ", "```", "hoặc", "thêm"]):
                        seen.add(item)
                        items.append(item)
    if items:
        return ", ".join(items[:80])
    return "blurry, distorted, low quality"


def print_manual_guide(prompts: dict, image_map: dict):
    """In hướng dẫn manual paste lên Kling/Higgsfield dashboard."""
    scenes = prompts.get("scenes", [])
    scene_suggestions = image_map.get("scene_suggestions", [])
    neg_text = extract_negative_prompt_text()

    print("\n" + "=" * 70)
    print("  🎬 HƯỚNG DẪN PASTE TAY — KLING AI")
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

    print("  Các bước trên Kling AI dashboard:")
    print("    1. Vào https://www.klingai.com → AI Videos → Image to Video")
    print("    2. Upload ảnh reference (ảnh thật sản phẩm)")
    print("    3. Paste prompt + negative prompt")
    print("    4. Chọn model: Kling 3.0 (Pro nếu có)")
    print("    5. Render → tải xuống → ghép video bằng CapCut")
    print()
    print("  Hoặc dùng thủ công: python upload-video.py --manual")
    print("  Nếu muốn tự động: export KLING_API_KEY + KLING_SECRET_KEY")
    print("=" * 70)


def sign_kling_request(method: str, path: str, body: str = "") -> dict:
    """Tạo header auth cho Kling API v1 (HMAC-SHA256)."""
    import hashlib
    import hmac

    timestamp = str(int(time.time()))
    # Kling sign format: header = {"Content-Type": "application/json", "Authorization": "Bearer ..."}
    # Thực tế Kling dùng API Key + Secret để sign request
    # Format: AK + ":" + base64(HMAC-SHA256(secret, AK + timestamp + body))
    # Xem docs: https://docs.klingai.com/api-reference/authentication
    raw = KLING_API_KEY + timestamp + body
    sig = hmac.new(
        KLING_SECRET_KEY.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KLING_API_KEY}",
        "x-kling-signature": sig,
        "x-kling-timestamp": timestamp,
    }


def upload_to_kling_v1(prompts: dict, image_map: dict) -> dict:
    """
    Upload scenes lên Kling AI API v1 (Image-to-Video).

    endpoint: POST /v1/images/image-to-video
    ref: https://docs.klingai.com/api-reference/image-to-video/create
    """
    import requests

    scenes = prompts.get("scenes", [])
    scene_suggestions = image_map.get("scene_suggestions", [])
    results = []

    for i, scene in enumerate(scenes):
        # Tìm ảnh reference
        ref_image_path = None
        if i < len(scene_suggestions):
            img_filename = scene_suggestions[i].get("image", "")
            for img in image_map.get("scan", {}).get("images", []):
                if img["filename"] == img_filename:
                    ref_image_path = img["path"]
                    break

        if not ref_image_path:
            print(f"[!] Scene {scene['id']}: không có ảnh reference — bỏ qua", file=sys.stderr)
            continue

        # Upload ảnh lên Kling (họ yêu cầu upload image trước)
        print(f"[*] Scene {scene['id']}: đang upload ảnh {Path(ref_image_path).name}...")

        # Bước 1: Lấy upload URL
        upload_headers = sign_kling_request("POST", "/v1/files/upload")
        try:
            resp = requests.post(
                f"{KLING_API_BASE}/v1/files/upload",
                headers=upload_headers,
                json={"file_extension": Path(ref_image_path).suffix.replace(".", "")},
                timeout=30,
            )
            resp.raise_for_status()
            upload_data = resp.json()
            upload_url = upload_data.get("data", {}).get("upload_url")
            file_id = upload_data.get("data", {}).get("file_id")

            if not upload_url or not file_id:
                print(f"[!] Không lấy được upload URL từ Kling", file=sys.stderr)
                print(f"    Response: {resp.text}")
                continue

            # Bước 2: Upload file lên presigned URL
            with open(ref_image_path, "rb") as f:
                file_resp = requests.put(upload_url, data=f, timeout=120)
                file_resp.raise_for_status()

            print(f"    ✓ Upload ảnh thành công. File ID: {file_id}")
        except Exception as e:
            print(f"[!] Upload ảnh scene {scene['id']} thất bại: {e}", file=sys.stderr)
            continue

        # Bước 3: Tạo Image-to-Video task
        body = json.dumps({
            "model_name": "kling-v3.0",
            "image": file_id,
            "prompt": scene["prompt"],
            "negative_prompt": scene.get("negative_prompt", ""),
            "duration": scene["duration_s"],
            "cfg_scale": 0.5,
        })
        task_headers = sign_kling_request("POST", "/v1/images/image-to-video", body)
        try:
            resp = requests.post(
                f"{KLING_API_BASE}/v1/images/image-to-video",
                headers=task_headers,
                data=body,
                timeout=60,
            )
            resp.raise_for_status()
            task_data = resp.json()
            task_id = task_data.get("data", {}).get("task_id")
            print(f"    ✓ Task tạo: {task_id}")
            results.append({"scene_id": scene["id"], "task_id": task_id, "status": "pending"})
        except Exception as e:
            print(f"[!] Tạo task scene {scene['id']} thất bại: {e}", file=sys.stderr)
            results.append({"scene_id": scene["id"], "error": str(e)})

    return {"platform": "kling", "tasks": results, "total_scenes": len(scenes), "submitted": len(results)}


def poll_kling_tasks(result: dict) -> dict:
    """Poll Kling tasks cho đến khi hoàn thành."""
    if not result.get("tasks"):
        return result

    import requests

    completed = []
    pending = [t for t in result["tasks"] if t.get("status") == "pending" and "error" not in t]

    print(f"\n[*] Đang đợi {len(pending)} task render... (poll mỗi 15s)")
    while pending:
        for t in pending[:]:
            task_headers = sign_kling_request("GET", f"/v1/images/image-to-video/{t['task_id']}")
            try:
                resp = requests.get(
                    f"{KLING_API_BASE}/v1/images/image-to-video/{t['task_id']}",
                    headers=task_headers,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                status = data.get("data", {}).get("status", "")
                if status == "succeeded":
                    video_url = data.get("data", {}).get("video", {}).get("url", "")
                    t["status"] = "completed"
                    t["video_url"] = video_url
                    completed.append(t)
                    pending.remove(t)
                    print(f"  ✓ Scene {t['scene_id']} hoàn thành: {video_url[:80]}...")
                elif status == "failed":
                    t["status"] = "failed"
                    t["error"] = data.get("data", {}).get("message", "unknown")
                    pending.remove(t)
                    print(f"  ✗ Scene {t['scene_id']} thất bại: {t['error']}")
                # "processing" → chưa xong, tiếp tục
            except Exception as e:
                print(f"[!] Lỗi poll scene {t['scene_id']}: {e}", file=sys.stderr)

        if pending:
            time.sleep(15)

    result["completed"] = len(completed)
    result["failed"] = len(result["tasks"]) - len(completed)
    return result


def main():
    parser = argparse.ArgumentParser(description="Upload video scenes lên AI platform")
    parser.add_argument("--platform", choices=["kling", "manual"], default="kling",
                        help="AI video platform (mặc định: kling)")
    parser.add_argument("--manual", action="store_true",
                        help="Force manual mode (in hướng dẫn paste tay)")
    parser.add_argument("--poll", action="store_true",
                        help="Poll Kling tasks đến khi hoàn thành")
    args = parser.parse_args()

    # Load data từ các bước trước
    prompts = load_prompts()
    image_map = load_image_map()
    if prompts is None or image_map is None:
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Manual mode
    if args.manual or (args.platform == "manual"):
        print("[*] Manual mode — hướng dẫn paste tay")
        print_manual_guide(prompts, image_map)
        result = {"mode": "manual", "platform": "kling_dashboard", "note": "Follow hướng dẫn ở trên"}
        out_path = OUTPUT_DIR / "upload-result.json"
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[✓] Upload result saved → {out_path}")
        return

    # Kling API mode
    if args.platform == "kling":
        if not KLING_API_KEY or not KLING_SECRET_KEY:
            print("[!] Cần set KLING_API_KEY và KLING_SECRET_KEY để dùng API.", file=sys.stderr)
            print("    export KLING_API_KEY='your_key'", file=sys.stderr)
            print("    export KLING_SECRET_KEY='your_secret'", file=sys.stderr)
            print("[*] Fallback sang manual mode...")
            print_manual_guide(prompts, image_map)
            result = {"mode": "manual", "note": "Missing Kling API credentials"}
        else:
            print(f"[*] Uploading {len(prompts.get('scenes', []))} scenes to Kling AI...")
            result = upload_to_kling_v1(prompts, image_map)
            if args.poll and result.get("tasks"):
                result = poll_kling_tasks(result)
            print(f"\n[✓] Hoàn thành: {result.get('completed', 0)}/{result.get('total_scenes', 0)} scenes")

    # Save result
    out_path = OUTPUT_DIR / "upload-result.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Upload result saved → {out_path}")


if __name__ == "__main__":
    main()
