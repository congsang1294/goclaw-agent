#!/usr/bin/env python3
"""
post_from_queue.py — Cron 2 (8:05): Đọc queue → đăng Facebook.
KHÔNG có LLM, KHÔNG có AI, KHÔNG có lười.
Có queue file là đăng — 100%.

Cách dùng:
  python3 post_from_queue.py                       # dùng /tmp/post-queue.json mặc định
  python3 post_from_queue.py --queue /path/file.json

Luồng:
  1. Đọc queue file
  2. Gọi post_facebook.py (DRY_RUN=false) để đăng lên FB
  3. Cập nhật queue status → DONE / FAILED
  4. Archive queue file vào /tmp/post-queue-history/

Không cần OPENAI_API_KEY. Chỉ cần FB_ACCESS_TOKEN + FB_PAGE_ID trong .env
"""

import os, sys, json, time, shutil, subprocess, argparse
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")
POST_SCRIPT = os.path.join(SCRIPT_DIR, "post_facebook.py")
QUEUE_FILE_DEFAULT = "/tmp/post-queue.json"
QUEUE_HISTORY_DIR = "/tmp/post-queue-history"
LOG_FILE = "/tmp/post-queue-log.txt"

load_dotenv(ENV_PATH)


def log(msg):
    """Ghi log cả stderr và file log."""
    print(f"  {msg}", file=sys.stderr)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def read_queue(queue_path):
    """Đọc queue file, trả về dict hoặc None."""
    if not os.path.isfile(queue_path):
        log(f"❌ Không tìm thấy queue file: {queue_path}")
        return None

    try:
        with open(queue_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log(f"❌ Lỗi parse queue: {e}")
        return None
    except Exception as e:
        log(f"❌ Lỗi đọc queue: {e}")
        return None

    # Validate required fields
    missing = []
    if not data.get("caption"):
        missing.append("caption")
    if not data.get("image_local") and not data.get("image_filename"):
        missing.append("image_local / image_filename")
    if not data.get("status") == "PENDING":
        log(f"⚠ Queue không ở trạng thái PENDING (hiện tại: {data.get('status')})")
        return None

    if missing:
        log(f"❌ Queue thiếu trường: {', '.join(missing)}")
        return None

    return data


def find_image(data):
    """Tìm file ảnh từ queue data. Thử nhiều đường dẫn."""
    candidates = []

    if data.get("image_local") and os.path.isfile(data["image_local"]):
        candidates.append(data["image_local"])

    if data.get("image_filename"):
        for base in [
            SCRIPT_DIR,
            os.path.join(SCRIPT_DIR, "output"),
            "/tmp",
            "/app/workspace/ga-thanh-thoi-bot",
            "/app/workspace/ga-thanh-thoi-bot/output",
        ]:
            p = os.path.join(base, data["image_filename"])
            if os.path.isfile(p):
                candidates.append(p)

    if candidates:
        return candidates[0]

    # Thử tìm bất kỳ file .png nào trong output gần đây
    output_dir = os.path.join(SCRIPT_DIR, "output")
    if os.path.isdir(output_dir):
        pngs = sorted(
            [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".png")],
            key=os.path.getmtime, reverse=True
        )
        if pngs:
            log(f"⚠ Dùng ảnh mới nhất trong output/: {os.path.basename(pngs[0])}")
            return pngs[0]

    return None


def update_queue_status(queue_path, status, fb_result=None, error=None):
    """Cập nhật trạng thái queue file."""
    try:
        with open(queue_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return

    data["status"] = status
    if fb_result:
        data["fb_post_result"] = fb_result
        data["fb_posted_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if error:
        data["error"] = error

    try:
        with open(queue_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"⚠ Lỗi ghi queue status: {e}")


def archive_queue(queue_path, status):
    """Archive queue file vào thư mục lịch sử."""
    try:
        os.makedirs(QUEUE_HISTORY_DIR, exist_ok=True)
        ts = int(time.time())
        filename = f"post_{status}_{ts}.json"
        shutil.copy2(queue_path, os.path.join(QUEUE_HISTORY_DIR, filename))
        log(f"📦 Archive: {filename}")
    except Exception as e:
        log(f"⚠ Lỗi archive queue: {e}")


def main():
    parser = argparse.ArgumentParser(description="Cron 2: Đọc queue → đăng Facebook (no LLM)")
    parser.add_argument("--queue", default=QUEUE_FILE_DEFAULT, help="Đường dẫn queue file")
    parser.add_argument("--dry-run", action="store_true", help="Không đăng thật, chỉ kiểm tra")
    args = parser.parse_args()

    queue_path = args.queue

    # Kiểm tra biến môi trường
    access_token = os.environ.get("FB_ACCESS_TOKEN", "")
    page_id = os.environ.get("FB_PAGE_ID", "")
    page_name = os.environ.get("FB_PAGE_NAME", "")

    log(f"🔍 Bắt đầu post từ queue: {queue_path}")

    # === Bước 1: Đọc queue ===
    data = read_queue(queue_path)
    if data is None:
        log("❌ Queue không hợp lệ hoặc không tồn tại. Thoát.")
        sys.exit(1)

    # Cập nhật status → POSTING
    update_queue_status(queue_path, "POSTING")

    caption = data["caption"]
    log(f"📝 Caption ({data.get('word_count', '?')} từ): {caption[:80]}...")

    # === Bước 2: Tìm ảnh ===
    image_path = find_image(data)
    if not image_path:
        error_msg = f"Không tìm thấy file ảnh: {data.get('image_local')} / {data.get('image_filename')}"
        log(f"❌ {error_msg}")
        update_queue_status(queue_path, "FAILED", error=error_msg)
        archive_queue(queue_path, "FAILED")
        sys.exit(1)

    log(f"🖼 Ảnh: {image_path} ({os.path.getsize(image_path)} bytes)")

    if not os.path.isfile(image_path):
        error_msg = f"File ảnh không tồn tại: {image_path}"
        log(f"❌ {error_msg}")
        update_queue_status(queue_path, "FAILED", error=error_msg)
        archive_queue(queue_path, "FAILED")
        sys.exit(1)

    # === Bước 3: Kiểm tra token ===
    if not access_token:
        error_msg = "Thiếu FB_ACCESS_TOKEN"
        log(f"❌ {error_msg}")
        update_queue_status(queue_path, "FAILED", error=error_msg)
        archive_queue(queue_path, "FAILED")
        sys.exit(1)
    if not page_id:
        error_msg = "Thiếu FB_PAGE_ID"
        log(f"❌ {error_msg}")
        update_queue_status(queue_path, "FAILED", error=error_msg)
        archive_queue(queue_path, "FAILED")
        sys.exit(1)

    if args.dry_run:
        log("🏁 DRY RUN — không đăng thật")
        result = {
            "success": True,
            "dry_run": True,
            "image": image_path,
            "caption_preview": caption[:150],
            "access_token_ok": bool(access_token),
            "page_id": page_id,
            "page_name": page_name,
        }
        print(json.dumps(result, ensure_ascii=False))
        update_queue_status(queue_path, "DRY_RUN_OK")
        archive_queue(queue_path, "DRY_RUN_OK")
        sys.exit(0)

    # === Bước 4: Gọi post_facebook.py (PURE — không LLM) ===
    log("🚀 Đang đăng Facebook...")
    log(f"  FB_PAGE_ID: {page_id}")
    log(f"  FB_PAGE_NAME: {page_name}")

    env = {
        **os.environ,
        "DRY_RUN": "false",
        "FB_ACCESS_TOKEN": access_token,
        "FB_PAGE_ID": page_id,
        "FB_PAGE_NAME": page_name,
    }

    try:
        result = subprocess.run(
            [sys.executable, POST_SCRIPT, "--image", image_path, "--caption", caption],
            capture_output=True, text=True, timeout=180,
            cwd=SCRIPT_DIR, env=env
        )
    except subprocess.TimeoutExpired:
        error_msg = "Timeout sau 180s khi gọi post_facebook.py"
        log(f"❌ {error_msg}")
        update_queue_status(queue_path, "FAILED", error=error_msg)
        archive_queue(queue_path, "FAILED")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Lỗi subprocess: {e}"
        log(f"❌ {error_msg}")
        update_queue_status(queue_path, "FAILED", error=error_msg)
        archive_queue(queue_path, "FAILED")
        sys.exit(1)

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    # Parse kết quả
    try:
        fb_result = json.loads(stdout)
    except json.JSONDecodeError:
        fb_result = {"success": False, "error": f"Không parse được JSON từ post_facebook.py. stdout: {stdout[:300]}, stderr: {stderr[:300]}"}

    if fb_result.get("success"):
        post_id = fb_result.get("post_id", "")
        post_url = fb_result.get("post_url", "")
        log(f"✅ ĐĂNG THÀNH CÔNG!")
        log(f"  Post ID: {post_id}")
        log(f"  URL: {post_url}")

        result_data = {
            "success": True,
            "post_id": post_id,
            "post_url": post_url,
            "page_name": page_name,
            "page_id": page_id,
            "posted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(time.time()),
        }

        update_queue_status(queue_path, "DONE", fb_result=result_data)
        archive_queue(queue_path, "DONE")
        print(json.dumps(result_data, ensure_ascii=False))

    else:
        error_msg = fb_result.get("error", "Lỗi không xác định từ Facebook API")
        error_code = fb_result.get("error_code", 0)
        log(f"❌ ĐĂNG THẤT BẠI: [{error_code}] {error_msg}")

        result_data = {
            "success": False,
            "error": error_msg,
            "error_code": error_code,
        }

        update_queue_status(queue_path, "FAILED", error=error_msg)
        archive_queue(queue_path, "FAILED")
        print(json.dumps(result_data, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
