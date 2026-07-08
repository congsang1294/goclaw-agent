#!/usr/bin/env python3
"""
video_auto_facebook.py — Trigger pipeline tạo video + đăng Facebook Reels.
Chạy từ workspace ga-trong-tre.

Usage:
    python3 scripts/video_auto_facebook.py
    python3 scripts/video_auto_facebook.py --topic "Nội dung tuỳ chỉnh"
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
OUTPUT_DIR = SKILL_DIR / "output"

TOPIC_DEFAULT = "Google Ads Match Type Converter - chuyển đổi match type nhanh cho nhà quảng cáo"


def run_step(step_name: str, cmd: list, timeout: int = 300) -> bool:
    print(f"[pipeline] {step_name}...", flush=True)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            print(f"[FAIL] {step_name}: {r.stderr.strip()[:500]}", flush=True)
            return False
        if r.stdout.strip():
            print(f"[OK] {step_name}: {r.stdout.strip()[:200]}", flush=True)
        else:
            print(f"[OK] {step_name}", flush=True)
        return True
    except FileNotFoundError as e:
        print(f"[FAIL] {step_name}: {e}", flush=True)
        return False
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {step_name}: timeout {timeout}s", flush=True)
        return False


def ensure_env() -> bool:
    """Kiểm tra các biến môi trường tối thiểu."""
    missing = []
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_KEY_REAL"):
        missing.append("OPENAI_API_KEY hoặc OPENAI_KEY_REAL")
    if not os.environ.get("FB_PAGE_ID"):
        missing.append("FB_PAGE_ID")
    if not os.environ.get("FB_PAGE_TOKEN"):
        missing.append("FB_PAGE_TOKEN")
    if missing:
        print(f"[FAIL] Thiếu biến môi trường: {', '.join(missing)}", flush=True)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Tạo video AI và đăng Facebook Reels")
    parser.add_argument("--topic", default=TOPIC_DEFAULT, help="Chủ đề video")
    parser.add_argument("--skip-post", action="store_true", help="Chỉ tạo video, không đăng FB")
    args = parser.parse_args()

    if not ensure_env():
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # B1: Gen prompt
    if not run_step("Gen prompt", [
        "python3", str(SCRIPTS_DIR / "gen-prompt.py"),
        args.topic,
        "--style", str(SKILL_DIR / "assets/brand-style.md"),
        "--camera", str(SKILL_DIR / "assets/camera-prompts.md"),
    ]):
        sys.exit(2)

    # B2: Gen video (raw)
    prompt_file = OUTPUT_DIR / "prompts.json"
    if not prompt_file.exists():
        print(f"[FAIL] Không tìm thấy {prompt_file}", flush=True)
        sys.exit(3)

    if not run_step("Gen video", [
        "python3", str(SCRIPTS_DIR / "gen-video.py"),
        "--prompt-file", str(prompt_file),
        "--aspect", "9:16",
    ], timeout=600):
        print("[WARN] Gen video thất bại, nhưng vẫn tiếp tục nếu có file raw cũ", flush=True)

    # B3: Gen voice (OpenAI TTS)
    script_text = args.topic
    script_file = OUTPUT_DIR / "voice-script.txt"
    if script_file.exists():
        script_text = script_file.read_text(encoding="utf-8").strip() or script_text
    if not run_step("Gen voice", [
        "python3", str(SCRIPTS_DIR / "gen-voice.py"),
        "--text", script_text,
        "--output", str(OUTPUT_DIR / "voice.mp3"),
    ], timeout=120):
        print("[WARN] Gen voice thất bại, sẽ tạo video không voice", flush=True)

    # B4: Build final (ghép video + voice)
    raw_video = OUTPUT_DIR / "video_raw.mp4"
    if not raw_video.exists():
        print(f"[FAIL] Không tìm thấy {raw_video}", flush=True)
        sys.exit(4)

    voice_file = OUTPUT_DIR / "voice.mp3"
    voice_args = ["--voice", str(voice_file)] if voice_file.exists() else []
    if not run_step("Build final", [
        "python3", str(SCRIPTS_DIR / "build-final.py"),
        "--input", str(raw_video),
        "--output", str(OUTPUT_DIR / "final.mp4"),
        *voice_args,
    ], timeout=120):
        sys.exit(5)

    # B5: Post Facebook Reels
    final_video = OUTPUT_DIR / "final.mp4"
    if not final_video.exists():
        print(f"[FAIL] Không tìm thấy {final_video}", flush=True)
        sys.exit(6)

    if args.skip_post:
        print(f"[DONE] Video tạo tại: {final_video}", flush=True)
        print("[SKIP] --skip-post, không đăng Facebook", flush=True)
        sys.exit(0)

    if not run_step("Post Facebook Reels", [
        "python3", str(SCRIPTS_DIR / "post_video.py"),
        "--video", str(final_video),
        "--caption", args.topic,
    ], timeout=120):
        sys.exit(7)

    print("[DONE] Pipeline hoàn tất!", flush=True)


if __name__ == "__main__":
    main()
