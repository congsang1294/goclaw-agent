#!/usr/bin/env python3
"""
gen-voice.py — Tạo voiceover từ text bằng OpenAI TTS.

Usage:
    python3 scripts/gen-voice.py --text "Nội dung" --output output/voice.mp3
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("[FAIL] Thiếu openai. Chạy: pip install openai", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
    _env = Path(__file__).resolve().parent.parent / ".env"
    if _env.exists():
        load_dotenv(_env)
except ImportError:
    pass


def main():
    parser = argparse.ArgumentParser(description="Tạo voiceover bằng OpenAI TTS")
    parser.add_argument("--text", required=True, help="Nội dung đọc")
    parser.add_argument("--output", required=True, help="File MP3 đầu ra")
    parser.add_argument("--voice", default="nova", choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
    parser.add_argument("--speed", type=float, default=1.0, help="Tốc độ đọc (0.25-4.0)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY_REAL")
    if not api_key:
        print("[FAIL] Thiếu OPENAI_API_KEY hoặc OPENAI_KEY_REAL", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=args.voice,
            speed=args.speed,
            input=args.text[:4096],
        )
        response.stream_to_file(str(output_path))
        print(f"[OK] Voice saved: {output_path}", flush=True)
    except Exception as e:
        print(f"[FAIL] OpenAI TTS: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
