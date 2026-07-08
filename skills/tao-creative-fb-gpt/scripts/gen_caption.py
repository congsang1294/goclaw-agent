#!/usr/bin/env python3
"""Generate Facebook ideas, organic captions, or ad copy from brand context."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

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
PROJECT_DIR = SKILL_DIR.parents[1] if len(SKILL_DIR.parents) > 1 else SKILL_DIR.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"
CONTEXT_FILES = ("SOUL.md", "USER.md", "AGENTS.md", "HEARTBEAT.md")

FALLBACK_BRAND_CONTEXT = """
Business: Google Ads Match Type Converter - cong cu chuyen doi keyword sang Broad, Phrase, Exact.
Tool chay tren trinh duyet, keyword khong gui len server. Dung duoc tren dien thoai va may tinh.
Khong can tai khoan. Ban free co 3 luot Copy All. Ban Pro mo Copy All khong gioi han.
Voice: gan gui, thang than, viet nhu nguoi da lam that, sai that, mat tien that, roi ngoi ke lai.
Viet tieng Viet, cau ngan, ro, doi thuong. Khong dung tu corporate, khong pha tieng Anh vo duyen.
USP: Keyword xu ly ngay tren trinh duyet (client-side), bao mat tuyet doi y tuong tu khoa, khong can tai khoan, free 3 lan Copy All.
Website: https://tool.congsang.info.vn
Gia Pro: 15.000d (mot lan, suu huu tron doi).
Tránh: hua ket qua ads (tang don, giam CPC, tang ROAS), dung tu "hang dau", "so 1", "top 1", "giai phap dot pha".
"""


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
                    f"[gen_caption] Bỏ qua dotenv không đọc được: {path} ({exc})",
                    file=sys.stderr,
                )


def first_existing_file(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.is_file():
            return path.resolve()
    return None


def first_existing_dir(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.is_dir():
            return path.resolve()
    return None


def discovery_roots() -> list[Path]:
    """Return likely project/workspace roots without assuming an agent slug."""
    roots: list[Path] = [PROJECT_DIR]
    for start in (SKILL_DIR, Path.cwd().resolve()):
        roots.extend([start, *start.parents])

    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return unique


def resolve_brain_db(cli_value: str | None) -> Path | None:
    candidates: list[Path] = []
    if cli_value:
        candidates.append(Path(cli_value).expanduser())
    if os.getenv("BRAIN_DB_PATH"):
        candidates.append(Path(os.environ["BRAIN_DB_PATH"]).expanduser())
    candidates.extend(root / "my-brain" / "brain.db" for root in discovery_roots())
    candidates.extend(root / "vault-ready" / "brain.db" for root in discovery_roots())
    candidates.extend([
        Path("/opt/mcp/brain.db"),
        Path("/opt/goclaw/brain.db"),
        Path("/app/workspace/ga-trong-tre/vault-ready/brain.db"),
        Path("/app/workspace/ga-thanh-thoi-bot/vault-ready/brain.db"),
    ])
    return first_existing_file(candidates)


def resolve_context_dir(cli_value: str | None, brain_db: Path | None) -> Path | None:
    candidates: list[Path] = []
    if cli_value:
        candidates.append(Path(cli_value).expanduser())
    if os.getenv("CONTEXT_DIR"):
        candidates.append(Path(os.environ["CONTEXT_DIR"]).expanduser())
    if brain_db:
        candidates.append(brain_db.parent / "context-files")
    candidates.extend(
        root / "my-brain" / "context-files" for root in discovery_roots()
    )
    candidates.extend([
        Path("/opt/mcp/context-files"),
        Path("/opt/goclaw/context-files"),
    ])
    return first_existing_dir(candidates)


def read_brandvoice(brain_db: Path | None) -> str:
    if not brain_db:
        return ""
    try:
        uri = f"file:{brain_db.as_posix()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as conn:
            rows = conn.execute(
                "SELECT title, content FROM brand_voice ORDER BY id"
            ).fetchall()
        return "\n".join(f"- {title}: {content}" for title, content in rows)
    except (sqlite3.Error, OSError) as exc:
        print(f"[gen_caption] Không đọc được brand_voice: {exc}", file=sys.stderr)
        return ""


def read_context_files(context_dir: Path | None) -> str:
    if not context_dir:
        return ""
    sections: list[str] = []
    for filename in CONTEXT_FILES:
        path = context_dir / filename
        if path.is_file():
            try:
                sections.append(f"## {filename}\n{path.read_text(encoding='utf-8')}")
            except OSError as exc:
                print(f"[gen_caption] Không đọc được {path}: {exc}", file=sys.stderr)
    return "\n\n".join(sections)


def read_optional_asset(filename: str) -> str:
    path = SKILL_DIR / "assets" / filename
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def build_brand_context(brain_db: Path | None, context_dir: Path | None) -> str:
    parts = [
        FALLBACK_BRAND_CONTEXT.strip(),
        read_brandvoice(brain_db),
        read_context_files(context_dir),
        read_optional_asset("caption-templates.md"),
    ]
    return "\n\n".join(part for part in parts if part.strip())


def schemas(task: str) -> dict[str, Any]:
    if task == "ideas":
        return {
            "type": "object",
            "properties": {
                "ideas": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "items": {
                        "type": "object",
                        "properties": {
                            "number": {"type": "integer", "enum": [1, 2, 3]},
                            "title": {"type": "string"},
                            "angle": {"type": "string"},
                        },
                        "required": ["number", "title", "angle"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["ideas"],
            "additionalProperties": False,
        }
    return {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["organic", "ads"]},
            "angle": {"type": "string"},
            "title": {"type": "string"},
            "hook_emoji": {"type": "string"},
            "hook": {"type": "string"},
            "benefits": {
                "type": "array",
                "items": {"type": "string"},
            },
            "cta": {"type": "string"},
            "hashtags": {
                "type": "array",
                "items": {"type": "string"},
            },
            "image_prompt": {"type": "string"},
        },
        "required": ["mode", "angle", "title", "hook_emoji", "hook", "benefits", "cta", "hashtags", "image_prompt"],
        "additionalProperties": False,
    }


def compose_caption(payload: dict[str, Any]) -> str:
    title = payload.get("title", "").strip()
    emoji = (payload.get("hook_emoji") or "").strip() or "💧"
    hook = payload.get("hook", "").strip()
    benefits = [b.strip() for b in payload.get("benefits", []) if b.strip()]
    cta = payload.get("cta", "").strip()
    hashtags = " ".join(
        h if h.startswith("#") else f"#{h}"
        for h in payload.get("hashtags", [])
        if h.strip()
    )
    lines = [title, ""]
    lines.append(f"{emoji} {hook}")
    lines.append("")
    for b in benefits:
        lines.append(f"✅ {b}")
    lines.append("")
    lines.append(f"👉 {cta}")
    if hashtags:
        lines.append("")
        lines.append(hashtags)
    return "\n".join(lines)


def build_prompts(task: str, topic: str, angle: str, context: str) -> tuple[str, str]:
    phone = os.getenv("BUSINESS_PHONE", "0978 688 032")
    instructions = f"""
Bạn là copywriter Facebook của brand được mô tả trong brand context dưới đây.
Chỉ dùng thông tin có trong brand context. Không bịa giá, review, số lượng khách,
chứng chỉ, logo, đồng phục hoặc cam kết mới. Viết tiếng Việt tự nhiên, câu ngắn,
gần gũi, dễ hiểu, viết như đang nói chuyện với người quen.

Điền vào các field JSON sau:
- `title`: tiêu đề ngắn gợi tò mò (kết thúc ? hoặc ! nếu phù hợp).
- `hook_emoji`: 1 emoji phù hợp với chủ đề.
- `hook`: 1–2 câu mô tả tình huống quen thuộc, nói với "anh/chị" hoặc "bạn". Không có emoji.
- `benefits`: mảng 2–3 benefit ngắn — chỉ dùng cam kết/USP có thật trong brand context.
- `cta`: CTA ngắn gọn, kết thúc bằng số điện thoại {phone}. Không có "👉 " prefix.
- `hashtags`: mảng 2–3 hashtag tiếng Việt phù hợp với brand. Không có "#" prefix cũng ok.
- `image_prompt`: prompt tiếng Anh cho ảnh 1024x1024, không render chữ/logo.

BRAND CONTEXT:
{context}
""".strip()

    if task == "ideas":
        user_input = f"""
Tạo đúng 3 ý tưởng content organic Facebook khác nhau cho chủ đề:
{topic or "cách tối ưu match type Google Ads"}

Mỗi ý chỉ gồm tiêu đề ngắn và angle 1–2 câu. Chưa viết caption, chưa tạo ảnh.
Ba ý phải đủ khác nhau để người dùng chọn.
""".strip()
    elif task == "organic":
        user_input = f"""
Tạo một bài organic hoàn chỉnh cho chủ đề: {topic}
Angle đã chọn: {angle or "tư vấn gần gũi"}

Caption theo đúng bố cục đã quy định. Soft CTA.
""".strip()
    else:
        user_input = f"""
Tạo một creative ads hoàn chỉnh cho chủ đề: {topic}
Angle bắt buộc: {angle}

Caption theo đúng bố cục đã quy định. CTA rõ ràng. Ảnh có negative space cho text overlay.
""".strip()
    return instructions, user_input


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


def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Model không trả JSON object")
    return json.loads(cleaned[start:end + 1])


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def validate_payload(task: str, payload: dict[str, Any]) -> None:
    if task == "ideas":
        ideas = payload.get("ideas")
        if not isinstance(ideas, list) or len(ideas) != 3:
            raise ValueError("Output ideas phải có đúng 3 ý tưởng")
        return
    if not payload.get("title", "").strip():
        raise ValueError("Thiếu title")
    caption = payload.get("caption", "")
    if not caption.strip():
        raise ValueError("Caption rỗng")
    count = word_count(caption)
    if count < 40:
        raise ValueError(f"Caption có {count} từ; quá ngắn (tối thiểu 40)")
    if not payload.get("image_prompt"):
        raise ValueError("Thiếu image_prompt")


def call_openai(
    task: str,
    topic: str,
    angle: str,
    context: str,
    model: str,
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_KEY_REAL") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Thiếu OPENAI_KEY_REAL hoặc OPENAI_API_KEY trong environment/.env"
        )

    client = OpenAI(api_key=api_key)
    instructions, user_input = build_prompts(task, topic, angle, context)
    schema = schemas(task)

    for attempt in range(2):
        try:
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input=user_input,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": f"facebook_{task}",
                        "strict": True,
                        "schema": schema,
                    }
                },
            )
            payload = extract_json(response.output_text)
            if task != "ideas":
                payload["caption"] = compose_caption(payload)
            validate_payload(task, payload)
            return payload
        except Exception as exc:
            print(
                f"[gen_caption] Lần {attempt + 1} thất bại: "
                f"{type(exc).__name__}: {str(exc)[:500]}",
                file=sys.stderr,
            )
            should_retry = is_retryable(exc) or isinstance(
                exc, (json.JSONDecodeError, ValueError)
            )
            if attempt == 0 and should_retry:
                time.sleep(2)
                continue
            raise

    raise RuntimeError("Không thể tạo nội dung sau 2 lần thử")


def resolve_output_path(raw_path: str | None, task: str) -> Path:
    if raw_path:
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = SKILL_DIR / path
    else:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        path = DEFAULT_OUTPUT_DIR / f"{task}_{stamp}.json"
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sinh 3 ý tưởng, caption organic hoặc ad copy theo brand voice."
    )
    parser.add_argument(
        "--task",
        default="ideas",
        choices=("ideas", "organic", "ads"),
        help="Mặc định ideas để tạo 3 ý tưởng ở Bước A.",
    )
    parser.add_argument("--topic", default="", help="Chủ đề hoặc concept cần viết.")
    parser.add_argument(
        "--angle",
        default="",
        choices=("", "pain_point", "solution", "social_proof", "education", "trust"),
        help="Angle của bài; ads nên dùng pain_point, solution hoặc social_proof.",
    )
    parser.add_argument("--brain-db", help="Override đường dẫn brain.db.")
    parser.add_argument("--context-dir", help="Override thư mục chứa 4 context files.")
    parser.add_argument("--output", help="File JSON đầu ra.")
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini"),
        help="OpenAI text model; mặc định lấy OPENAI_TEXT_MODEL.",
    )
    return parser.parse_args()


def main() -> int:
    configure_console()
    load_environment()
    args = parse_args()

    if args.task in {"organic", "ads"} and not args.topic.strip():
        print(json.dumps({
            "ok": False,
            "error": "--topic là bắt buộc với task organic và ads",
        }, ensure_ascii=False), file=sys.stderr)
        return 2
    if args.task == "ads" and args.angle not in {
        "pain_point", "solution", "social_proof"
    }:
        print(json.dumps({
            "ok": False,
            "error": "Task ads yêu cầu --angle pain_point|solution|social_proof",
        }, ensure_ascii=False), file=sys.stderr)
        return 2

    brain_db = resolve_brain_db(args.brain_db)
    context_dir = resolve_context_dir(args.context_dir, brain_db)
    context = build_brand_context(brain_db, context_dir)
    output_path = resolve_output_path(args.output, args.task)

    try:
        payload = call_openai(
            task=args.task,
            topic=args.topic.strip(),
            angle=args.angle,
            context=context,
            model=args.model,
        )
        result = {
            "ok": True,
            "task": args.task,
            "model": args.model,
            "brain_db": str(brain_db) if brain_db else None,
            "context_dir": str(context_dir) if context_dir else None,
            "data": payload,
        }
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        result["output_path"] = str(output_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        error = {
            "ok": False,
            "task": args.task,
            "output_path": str(output_path),
            "error": {
                "type": type(exc).__name__,
                "status_code": getattr(exc, "status_code", None),
                "code": getattr(exc, "code", None),
                "request_id": getattr(exc, "request_id", None),
                "message": str(exc)[:500],
            },
        }
        print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
