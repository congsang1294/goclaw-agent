#!/usr/bin/env python3
"""Publish one image and one caption together to a Facebook Page."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print(json.dumps({
        "ok": False,
        "error": "Thiếu thư viện requests. Chạy: pip install requests",
    }, ensure_ascii=False))
    raise SystemExit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"


class FacebookAPIError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: int | str | None = None,
        error_subcode: int | str | None = None,
        error_type: str | None = None,
        fbtrace_id: str | None = None,
        response_body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.error_subcode = error_subcode
        self.error_type = error_type
        self.fbtrace_id = fbtrace_id
        self.response_body = response_body


def configure_console() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def load_environment() -> None:
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
                    f"[post_facebook] Bỏ qua dotenv không đọc được: {path} ({exc})",
                    file=sys.stderr,
                )


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def resolve_local_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = SKILL_DIR / path
    return path.resolve()


def read_caption(caption: str | None, caption_file: str | None) -> str:
    if caption_file:
        path = resolve_local_path(caption_file)
        if not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy caption file: {path}")
        raw = path.read_text(encoding="utf-8").strip()
        try:
            payload = json.loads(raw)
            extracted = (
                payload.get("data", {}).get("caption")
                or payload.get("caption")
            )
            if isinstance(extracted, str):
                raw = extracted.strip()
        except json.JSONDecodeError:
            pass
        value = raw
    else:
        value = (caption or "").strip()

    if not value:
        raise ValueError("Caption không được để trống; bài Facebook phải có cả ảnh và văn bản")
    return value


def parse_response(response: requests.Response) -> dict[str, Any]:
    try:
        body: Any = response.json()
    except ValueError:
        body = {"raw": response.text[:1000]}

    error = body.get("error", {}) if isinstance(body, dict) else {}
    if not response.ok or error:
        raise FacebookAPIError(
            error.get("message") or f"Facebook Graph API trả HTTP {response.status_code}",
            status_code=response.status_code,
            error_code=error.get("code"),
            error_subcode=error.get("error_subcode"),
            error_type=error.get("type"),
            fbtrace_id=error.get("fbtrace_id"),
            response_body=body,
        )
    if not isinstance(body, dict):
        raise FacebookAPIError(
            "Facebook Graph API trả response không hợp lệ",
            status_code=response.status_code,
            response_body=body,
        )
    return body


def post_photo(
    *,
    page_id: str,
    page_token: str,
    graph_version: str,
    caption: str,
    image_path: Path | None,
    image_url: str | None,
    timeout: float,
) -> dict[str, Any]:
    endpoint = f"https://graph.facebook.com/{graph_version}/{page_id}/photos"
    headers = {"Authorization": f"Bearer {page_token}"}
    data = {"caption": caption}

    try:
        if image_path:
            mime_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
            with image_path.open("rb") as image_file:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    data=data,
                    files={"source": (image_path.name, image_file, mime_type)},
                    timeout=timeout,
                )
        else:
            data["url"] = image_url
            response = requests.post(
                endpoint,
                headers=headers,
                data=data,
                timeout=timeout,
            )
    except requests.RequestException as exc:
        raise FacebookAPIError(
            f"Không kết nối được Facebook Graph API: {exc}",
        ) from exc

    return parse_response(response)


def safe_url_filename(image_url: str) -> str:
    name = Path(urlparse(image_url).path).name
    return name if name and "." in name else "image_from_url.jpg"


def dry_run(
    *,
    caption: str,
    image_path: Path | None,
    image_url: str | None,
    page_id: str | None,
    graph_version: str,
    timeout: float,
) -> dict[str, Any]:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = DEFAULT_OUTPUT_DIR / f"dry_run_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)

    caption_path = run_dir / "caption.txt"
    caption_path.write_text(caption, encoding="utf-8")

    saved_image: str | None = None
    image_error: str | None = None
    if image_path:
        destination = run_dir / image_path.name
        shutil.copy2(image_path, destination)
        saved_image = str(destination.resolve())
    elif image_url:
        destination = run_dir / safe_url_filename(image_url)
        try:
            response = requests.get(image_url, timeout=timeout)
            response.raise_for_status()
            destination.write_bytes(response.content)
            saved_image = str(destination.resolve())
        except requests.RequestException as exc:
            image_error = f"Không tải được ảnh URL về local: {exc}"
            (run_dir / "image_url.txt").write_text(image_url, encoding="utf-8")

    payload = {
        "ok": True,
        "dry_run": True,
        "posted": False,
        "endpoint": f"https://graph.facebook.com/{graph_version}/{page_id or '<FB_PAGE_ID>'}/photos",
        "upload_method": "source" if image_path else "url",
        "source_image": str(image_path) if image_path else image_url,
        "saved_image": saved_image,
        "caption_path": str(caption_path.resolve()),
        "caption": caption,
        "image_warning": image_error,
    }
    preview_path = run_dir / "preview.json"
    preview_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    payload["preview_path"] = str(preview_path.resolve())
    return payload


def validate_inputs(
    image: str | None,
    image_url: str | None,
) -> tuple[Path | None, str | None]:
    if bool(image) == bool(image_url):
        raise ValueError("Chỉ truyền một trong hai: --image hoặc --image-url")

    if image:
        image_path = resolve_local_path(image)
        if not image_path.is_file():
            raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")
        if image_path.stat().st_size == 0:
            raise ValueError(f"File ảnh rỗng: {image_path}")
        return image_path, None

    parsed = urlparse(image_url or "")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("--image-url phải là URL public http/https hợp lệ")
    return None, image_url


def error_payload(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, FacebookAPIError):
        return {
            "ok": False,
            "posted": False,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "http_status": exc.status_code,
                "facebook_code": exc.error_code,
                "facebook_subcode": exc.error_subcode,
                "facebook_type": exc.error_type,
                "fbtrace_id": exc.fbtrace_id,
                "response": exc.response_body,
            },
        }
    return {
        "ok": False,
        "posted": False,
        "error": {
            "type": type(exc).__name__,
            "message": str(exc),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Đăng cùng lúc ảnh + caption lên Facebook Page qua /photos."
    )
    image_group = parser.add_mutually_exclusive_group(required=True)
    image_group.add_argument("--image", help="Ảnh local PNG/JPG/WebP.")
    image_group.add_argument("--image-url", help="URL ảnh public http/https.")
    caption_group = parser.add_mutually_exclusive_group(required=True)
    caption_group.add_argument("--caption", help="Caption trực tiếp.")
    caption_group.add_argument(
        "--caption-file",
        help="File text hoặc JSON từ gen_caption.py.",
    )
    parser.add_argument(
        "--graph-version",
        default=os.getenv("FB_GRAPH_VERSION", "v25.0"),
        help="Phiên bản Graph API; mặc định FB_GRAPH_VERSION hoặc v25.0.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("FB_TIMEOUT_SECONDS", "90")),
        help="Timeout HTTP tính bằng giây.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Không gọi Facebook, kể cả khi DRY_RUN trong env là false.",
    )
    parser.add_argument(
        "--confirm-post",
        action="store_true",
        help="Bắt buộc khi đăng thật; xác nhận user đã duyệt cả ảnh và caption.",
    )
    return parser.parse_args()


def main() -> int:
    configure_console()
    load_environment()
    args = parse_args()

    try:
        caption = read_caption(args.caption, args.caption_file)
        image_path, image_url = validate_inputs(args.image, args.image_url)
        page_id = os.getenv("FB_PAGE_ID")
        dry_run_enabled = args.dry_run or env_flag("DRY_RUN")

        if dry_run_enabled:
            result = dry_run(
                caption=caption,
                image_path=image_path,
                image_url=image_url,
                page_id=page_id,
                graph_version=args.graph_version,
                timeout=args.timeout,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if not args.confirm_post:
            raise ValueError(
                "Từ chối đăng thật: thiếu --confirm-post. "
                "Chỉ thêm cờ này sau khi user đã duyệt cả ảnh và caption."
            )

        page_token = os.getenv("FB_PAGE_TOKEN") or os.getenv("FB_ACCESS_TOKEN")
        missing = [
            name for name, value in (
                ("FB_PAGE_ID", page_id),
                ("FB_PAGE_TOKEN or FB_ACCESS_TOKEN", page_token),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"Thiếu biến môi trường: {', '.join(missing)}")

        response = post_photo(
            page_id=page_id,
            page_token=page_token,
            graph_version=args.graph_version,
            caption=caption,
            image_path=image_path,
            image_url=image_url,
            timeout=args.timeout,
        )
        post_id = response.get("post_id") or response.get("id")
        photo_id = response.get("id")
        post_url = (
            f"https://www.facebook.com/permalink.php"
            f"?story_fbid={photo_id}&id={page_id}"
        ) if photo_id and page_id else None
        result = {
            "ok": True,
            "dry_run": False,
            "posted": True,
            "page_id": page_id,
            "post_id": post_id,
            "post_url": post_url,
            "response": response,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(
            json.dumps(error_payload(exc), ensure_ascii=False, indent=2),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
