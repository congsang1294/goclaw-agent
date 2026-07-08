#!/usr/bin/env python3
"""
build-final.py — Ghép video raw + voice thành video cuối 9:16, loop nếu ngắn.

Usage:
    python3 scripts/build-final.py --input output/video_raw.mp4 --output output/final.mp4
    python3 scripts/build-final.py --input output/video_raw.mp4 --output output/final.mp4 --voice output/voice.mp3
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

TARGET_DURATION = 25  # giây, đủ cho Reels 15-30s


def get_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def main():
    parser = argparse.ArgumentParser(description="Build final video với voiceover")
    parser.add_argument("--input", required=True, help="File video raw đầu vào")
    parser.add_argument("--output", required=True, help="File video cuối")
    parser.add_argument("--voice", help="File voice MP3 (tùy chọn)")
    parser.add_argument("--target", type=int, default=TARGET_DURATION, help="Độ dài mục tiêu (giây)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    voice_path = Path(args.voice) if args.voice and Path(args.voice).exists() else None

    if not input_path.exists():
        print(f"[FAIL] Không tìm thấy {input_path}", file=sys.stderr)
        sys.exit(1)

    # Kiểm tra ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=10)
    except FileNotFoundError:
        print("[FAIL] Thiếu ffmpeg. Chạy: apt install ffmpeg", file=sys.stderr)
        sys.exit(2)

    vid_dur = get_duration(input_path)
    tmp_dir = output_path.parent / ".build-tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Loop video nếu ngắn hơn target
    looped = input_path
    if vid_dur < args.target and vid_dur > 0:
        loop_count = int(args.target / vid_dur) + 1
        looped = tmp_dir / "looped.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-stream_loop", str(loop_count), "-i", str(input_path),
             "-c", "copy", "-t", str(args.target), str(looped)],
            capture_output=True, timeout=120, check=True,
        )
        print(f"[INFO] Video looped {loop_count}x -> {looped}", flush=True)

    # Step 2: Thêm voice nếu có
    if voice_path:
        final_tmp = tmp_dir / "with_voice.mp4"
        voice_dur = get_duration(voice_path)
        if voice_dur > 0:
            # Cắt video theo độ dài voice, gắn âm thanh
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(looped), "-i", str(voice_path),
                 "-map", "0:v:0", "-map", "1:a:0",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                 "-c:a", "aac", "-b:a", "128k",
                 "-shortest",
                 str(final_tmp)],
                capture_output=True, timeout=180, check=True,
            )
        else:
            print("[WARN] Voice duration = 0, bỏ qua voice", flush=True)
            final_tmp = looped
    else:
        final_tmp = looped

    # Step 3: Copy ra output (có thể cần re-encode để Facebook chấp nhận)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(final_tmp),
         "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart",
         str(output_path)],
        capture_output=True, timeout=180, check=True,
    )

    # Dọn tmp
    for f in tmp_dir.iterdir():
        f.unlink(missing_ok=True)
    tmp_dir.rmdir()

    print(f"[OK] Final video: {output_path}", flush=True)


if __name__ == "__main__":
    main()
