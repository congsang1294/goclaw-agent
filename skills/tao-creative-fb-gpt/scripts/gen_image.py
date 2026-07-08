#!/usr/bin/env python3
"""Generate one Facebook image with GPT Image and save it as a local PNG."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

try:
    import openai
    from openai import OpenAI
except ImportError:
    print(json.dumps({
        "ok": False,
        "error": "Thiếu thư viện openai. Chạy: pip install openai",
    }, ensure_ascii=False))
    raise SystemExit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"


def configure_console() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def load_environment() -> None:
    """Load container variables first, then optional local/VPS dotenv files."""
    candidates = [
        SCRIPT_DIR / ".env",
        SKILL_DIR / ".env",
        Path(os.getenv("GOCLAW_ENV_FILE", "/opt/goclaw/.env")),
    ]
    for path in candidates:
        if path.is_file():
            try:
                load_dotenv(path, override=False)
            except (OSError, PermissionError) as exc:
                print(
                    f"[gen_image] Bỏ qua dotenv không đọc được: {path} ({exc})",
                    file=sys.stderr,
                )


def is_retryable(exc: Exception) -> bool:
    retryable_types = (
        openai.APITimeoutError,
        openai.APIConnectionError,
        openai.RateLimitError,
        openai.InternalServerError,
    )
    if isinstance(exc, retryable_types):
        return True
    return getattr(exc, "status_code", None) in {408, 409, 429, 500, 502, 503, 504}


def safe_error(exc: Exception) -> dict:
    return {
        "type": type(exc).__name__,
        "status_code": getattr(exc, "status_code", None),
        "code": getattr(exc, "code", None),
        "request_id": getattr(exc, "request_id", None),
        "message": str(exc)[:500],
    }


def resolve_output_path(raw_path: str | None, mode: str) -> Path:
    if raw_path:
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = SKILL_DIR / path
    else:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        path = DEFAULT_OUTPUT_DIR / f"{mode}_{stamp}.png"
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def send_telegram_preview(image_path: Path) -> dict:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[gen_image] TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID chưa set — bỏ qua gửi preview", file=sys.stderr)
        return {"sent": False, "reason": "env vars not set"}
    try:
        with image_path.open("rb") as f:
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                data={
                    "chat_id": chat_id,
                    "caption": "🖼️ Ảnh vừa tạo — duyệt để đăng Facebook hoặc nhắn 'tạo lại ảnh'.",
                },
                files={"photo": (image_path.name, f, "image/png")},
                timeout=30,
            )
        if resp.ok:
            print(f"[TG] Đã gửi preview ảnh về Telegram (chat {chat_id})", file=sys.stderr)
            return {"sent": True, "chat_id": chat_id}
        print(f"[TG] Gửi preview thất bại: {resp.text[:200]}", file=sys.stderr)
        return {"sent": False, "error": resp.text[:200]}
    except Exception as exc:
        print(f"[TG] Không gửi được preview: {exc}", file=sys.stderr)
        return {"sent": False, "error": str(exc)[:200]}


def generate_image(prompt: str, mode: str, output_path: Path) -> dict:
    api_key = os.getenv("OPENAI_KEY_REAL") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Thiếu OPENAI_KEY_REAL hoặc OPENAI_API_KEY trong environment/.env"
        )

    quality = "low" if mode == "organic" else "medium"
    model = "gpt-image-1"
    client = OpenAI(api_key=api_key)

    for attempt in range(2):
        try:
            result = client.images.generate(
                model=model,
                prompt=prompt,
                size="1024x1024",
                quality=quality,
                n=1,
            )
            if not result.data or not result.data[0].b64_json:
                raise RuntimeError("OpenAI không trả về dữ liệu ảnh base64")

            image_bytes = base64.b64decode(result.data[0].b64_json, validate=True)
            output_path.write_bytes(image_bytes)
            tg = send_telegram_preview(output_path)
            return {
                "ok": True,
                "mode": mode,
                "model": model,
                "quality": quality,
                "size": "1024x1024",
                "image_path": str(output_path),
                "bytes": len(image_bytes),
                "telegram_preview": tg,
            }
        except Exception as exc:
            error = safe_error(exc)
            print(
                f"[gen_image] Lần {attempt + 1} thất bại: "
                f"{json.dumps(error, ensure_ascii=False)}",
                file=sys.stderr,
            )
            if attempt == 0 and is_retryable(exc):
                time.sleep(3)
                continue
            raise

    raise RuntimeError("Không thể tạo ảnh sau 2 lần thử")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tạo ảnh Facebook bằng gpt-image-1 và lưu PNG local."
    )
    parser.add_argument("--prompt", required=True, help="Prompt mô tả ảnh.")
    parser.add_argument(
        "--mode",
        required=True,
        choices=("organic", "ads"),
        help="organic dùng quality low; ads dùng quality medium.",
    )
    parser.add_argument(
        "--output",
        help="Đường dẫn PNG. Đường dẫn tương đối được tính từ thư mục skill.",
    )
    return parser.parse_args()


def main() -> int:
    configure_console()
    load_environment()
    args = parse_args()
    output_path = resolve_output_path(args.output, args.mode)

    try:
        result = generate_image(args.prompt.strip(), args.mode, output_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        payload = {
            "ok": False,
            "mode": args.mode,
            "image_path": str(output_path),
            "error": safe_error(exc),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
