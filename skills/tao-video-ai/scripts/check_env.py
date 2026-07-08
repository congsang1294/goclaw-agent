#!/usr/bin/env python3
"""
Kiểm tra môi trường cho skill tao-video-ai.
Không in secret ra console.

Usage:
    python3 scripts/check_env.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


SCRIPT_DIR = Path(__file__).resolve().parent


def mask(value: str) -> str:
    if not value:
        return "(empty)"
    if len(value) < 12:
        return value[:4] + "***"
    return value[:6] + "..." + value[-4:]


def check_env() -> list[dict]:
    if load_dotenv:
        load_dotenv(SCRIPT_DIR / ".env")
    results = []

    checks = [
        ("OPENAI_API_KEY", "Prompt generation (OpenAI)", False),
        ("ANTHROPIC_API_KEY", "Prompt generation (Claude)", True),
        ("KLING_API_KEY", "Kling AI API key", True),
        ("KLING_SECRET_KEY", "Kling AI API secret", True),
    ]

    all_ok = True
    for key, purpose, optional in checks:
        value = os.environ.get(key, "")
        if not value:
            if optional:
                status = "⚠️  OPTIONAL"
            else:
                status = "❌  MISSING"
                all_ok = False
        else:
            status = f"✅  OK ({mask(value)})"
        results.append({"key": key, "purpose": purpose, "status": status, "value": value, "optional": optional})
        print(f"  {status}  {key}  ({purpose})")

    # Kiểm tra thư mục ảnh
    image_dirs = [
        Path.cwd() / "product-photos",
        SCRIPT_DIR.parent.parent / "product-photos",
    ]
    found_dir = None
    for d in image_dirs:
        if d.exists():
            found_dir = d
            break

    if found_dir:
        images = list(found_dir.rglob("*"))
        image_files = [f for f in images if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
        print(f"  📁  product-photos: {found_dir} ({len(image_files)} ảnh)")
        results.append({"key": "product-photos", "status": f"Found: {len(image_files)} images"})
    else:
        print(f"  ⚠️  product-photos: Không tìm thấy thư mục. Tạo product-photos/ với ảnh sản phẩm.")
        results.append({"key": "product-photos", "status": "Not found"})

    print()
    if all_ok:
        print("  ✅  Các biến bắt buộc đã đủ. Ready to generate video.")
    else:
        print("  ⚠️  Còn thiếu biến bắt buộc. Copy env.example thành .env và điền key.")

    return results


def main():
    print(f"\n  🔍  tao-video-ai — Kiểm tra môi trường")
    print(f"  {'─' * 40}")
    check_env()
    print(f"  {'─' * 40}\n")


if __name__ == "__main__":
    main()
