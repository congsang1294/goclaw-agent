#!/usr/bin/env python3
"""Cron 9h: generate 3 Facebook content ideas, send Telegram, then stop."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

import workflow


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = SKILL_DIR / "output"


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def load_environment() -> None:
    candidates = [
        SCRIPT_DIR / ".env",
        SKILL_DIR / ".env",
        Path(os.getenv("GOCLAW_ENV_FILE", "/opt/goclaw/.env")),
    ]
    for path in candidates:
        if path.is_file():
            load_dotenv(path, override=False)


def send_telegram_message(text: str) -> dict[str, Any]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return {"sent": False, "reason": "missing TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID"}

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
        timeout=30,
    )
    if not response.ok:
        return {"sent": False, "status_code": response.status_code, "body": response.text[:500]}
    return {"sent": True, "chat_id": chat_id}


def build_message(result: dict[str, Any]) -> str:
    state_path = result["state_path"]
    ideas = result.get("ideas", [])
    lines = [
        "Chào anh Sáng, 9h rồi. Gà mở 3 ý content Facebook hôm nay:",
        "",
    ]
    for idea in ideas:
        number = idea.get("number", "")
        title = idea.get("title", "")
        angle = idea.get("angle", "")
        lines.append(f"{number}. <b>{title}</b>")
        lines.append(f"   Angle: {angle}")
    lines.extend([
        "",
        "Anh chọn 1, 2 hoặc 3. Gà sẽ tạo caption + ảnh preview để anh duyệt.",
        "Chưa đăng gì lên fanpage ở bước này.",
        f"State: {state_path}",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cron 9h: gửi 3 ý tưởng content Facebook và chờ user chọn."
    )
    parser.add_argument(
        "--topic",
        default=os.getenv("DAILY_CONTENT_TOPIC", "content Facebook hôm nay cho Google Ads Match Type Converter"),
    )
    parser.add_argument("--model", default=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini"))
    parser.add_argument("--output-dir")
    return parser.parse_args()


def main() -> int:
    configure_console()
    load_environment()
    args = parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_dir = args.output_dir or str(
        OUTPUT_DIR / f"daily-content-fb-{time.strftime('%Y%m%d-%H%M%S')}"
    )

    workflow_args = argparse.Namespace(
        topic=args.topic,
        output_dir=run_dir,
        brain_db=None,
        context_dir=None,
        model=args.model,
    )
    result = workflow.command_ideas(workflow_args)

    latest_path = OUTPUT_DIR / "latest-daily-state.json"
    shutil.copy2(result["state_path"], latest_path)
    result["latest_state_path"] = str(latest_path)

    message = build_message(result)
    telegram = send_telegram_message(message)
    result["telegram"] = telegram
    result["posted"] = False
    result["next_step"] = "User chooses 1/2/3; then run workflow.py organic with this state."

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if telegram.get("sent") else 2


if __name__ == "__main__":
    raise SystemExit(main())
