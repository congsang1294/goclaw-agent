#!/usr/bin/env python3
"""
Pipeline end-to-end: gen ảnh từ prompts → ghép video MP4 → output video-final.mp4

Usage:
    cd /Users/congsang94/Desktop/google-ads-toolkit/skills/tao-video-ai
    python3 scripts/gen_video_mp4.py
"""

import base64
import json
import os
import sys
import time
from pathlib import Path

# Fix: thêm dotenv load trước
# Load env from .env (scripts/.env)
ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SKILL_DIR / "output"

def load_prompts():
    path = OUTPUT_DIR / "prompts.json"
    if not path.exists():
        # fallback: gen mới
        print("[!] prompts.json not found, re-running gen-prompt...")
        import subprocess
        subprocess.run([sys.executable, str(SKILL_DIR / "scripts/gen-prompt.py"), "Google Ads keyword tool", "--provider", "openai"], cwd=str(SKILL_DIR))
    return json.loads((OUTPUT_DIR / "prompts.json").read_text(encoding="utf-8"))

def generate_images(prompts):
    """Generate 5 scene images using OpenAI gpt-image-1"""
    api_key = os.environ.get("OPENAI_KEY_REAL") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)
    scenes = prompts["scenes"]
    image_paths = []

    # Tạo scene images
    for scene in scenes:
        output_path = OUTPUT_DIR / f"scene_{scene['id']:02d}.png"
        if output_path.exists() and output_path.stat().st_size > 1000:
            print(f"  Scene {scene['id']}: already exists, skipping")
            image_paths.append(output_path)
            continue

        prompt = scene["prompt"]
        # Remove text/UI references for better image generation
        prompt = prompt.replace(" displaying Google Ads Keyword Tool", "")
        prompt = prompt.replace(" focusing on the swift changing of match types in Google Ads Keyword Tool", "")
        prompt = prompt.replace("feature of quick match type conversion, revealing detail, dramatic composition, focus pull from the interface to user interaction", "feature of a modern digital tool interface, dramatic composition, focus pull")
        prompt = prompt.replace(" working on Google Ads Keyword Tool", " working on a laptop, typing efficiently")
        print(f"  Generating Scene {scene['id']} ({scene['duration_s']}s): {prompt[:60]}...")

        for attempt in range(3):
            try:
                result = client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size="1024x1024",
                    quality="medium",
                    n=1,
                )
                if result.data and result.data[0].b64_json:
                    img_bytes = base64.b64decode(result.data[0].b64_json, validate=True)
                    output_path.write_bytes(img_bytes)
                    image_paths.append(output_path)
                    print(f"    -> {output_path.name} ({len(img_bytes)} bytes)")
                    break
                else:
                    print(f"    Failed attempt {attempt+1}: no data")
            except Exception as e:
                print(f"    Attempt {attempt+1} failed: {e}")
                time.sleep(3)
        else:
            print(f"    Failed after 3 attempts, using placeholder")
            image_paths.append(None)

    return image_paths

def create_video(image_paths, prompts):
    """Create MP4 video from images using imageio"""
    import numpy as np
    from PIL import Image

    try:
        import imageio
        from imageio_ffmpeg import get_ffmpeg_exe
        print(f"  Using ffmpeg: {get_ffmpeg_exe()}")
    except ImportError:
        os.system("pip3 install imageio[ffmpeg] -q")
        import imageio
        from imageio_ffmpeg import get_ffmpeg_exe
        print(f"  Using ffmpeg: {get_ffmpeg_exe()}")

    scenes = prompts["scenes"]
    total_duration = prompts.get("total_duration_s", 20)
    fps = 24
    video_path = OUTPUT_DIR / "video-final.mp4"

    print(f"  Creating video: {total_duration}s at {fps}fps")

    writer = imageio.get_writer(video_path, fps=fps, codec='libx264', quality=8)

    valid_images = [p for p in image_paths if p is not None and p.exists()]
    if not valid_images:
        print("[!] No valid images, creating placeholder")
        # Create a solid color placeholder
        import numpy as np
        placeholder = (np.ones((1024, 1024, 3)) * 200).astype(np.uint8)
        for _ in range(fps * total_duration):
            writer.append_data(placeholder)
        writer.close()
        return video_path

    # Tính tổng thời gian
    total_frames_needed = fps * total_duration
    frames_per_scene = total_frames_needed // len(valid_images)

    for i, img_path in enumerate(valid_images):
        img = Image.open(img_path).convert("RGB")
        img_array = np.array(img)

        # Zoom effect (ken burns) - nhẹ cho đỡ giật
        h, w = img_array.shape[:2]
        for frame_idx in range(frames_per_scene):
            progress = frame_idx / frames_per_scene
            zoom = 1.0 + progress * 0.05  # zoom in nhẹ 5%
            new_h, new_w = int(h / zoom), int(w / zoom)
            ih = (h - new_h) // 2
            iw = (w - new_w) // 2
            cropped = img_array[ih:ih+new_h, iw:iw+new_w]
            resized = np.array(Image.fromarray(cropped).resize((w, h), Image.LANCZOS))

            writer.append_data(resized)

    writer.close()

    file_size = video_path.stat().st_size
    print(f"  Video saved: {video_path} ({file_size/1024/1024:.1f}MB)")
    return video_path

def send_telegram_video(video_path):
    """Gửi video preview lên Telegram"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "8818246003:AAGc_oD-8UFDGNnRoiQAi7tytlJgqlaqHxA")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "6880126421")

    import requests
    try:
        with video_path.open("rb") as f:
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendVideo",
                data={
                    "chat_id": chat_id,
                    "caption": "🎬 *Video moi* — Google Ads Keyword Tool\n\n15-25s AI video generated.\nDuyet de dang Facebook Reels?",
                    "parse_mode": "Markdown",
                    "has_spoiler": "false",
                },
                files={"video": (video_path.name, f, "video/mp4")},
                timeout=120,
            )
        if resp.ok:
            print(f"[TG] Sent video preview to Telegram chat {chat_id}")
            return True
        print(f"[TG] Failed: {resp.text[:200]}")
        return False
    except Exception as e:
        print(f"[TG] Error: {e}")
        return False

def main():
    print("=" * 50)
    print("  tao-video-ai — Pipeline End-to-End")
    print("=" * 50)

    # Step 1: Load prompts
    print("\n[1] Loading prompts...")
    prompts = load_prompts()
    print(f"    {len(prompts['scenes'])} scenes, {prompts['total_duration_s']}s, format: {prompts.get('format','N/A')}")

    # Step 2: Generate images
    print("\n[2] Generating scene images (OpenAI gpt-image-1)...")
    image_paths = generate_images(prompts)
    print(f"    {len([p for p in image_paths if p])}/{len(image_paths)} images generated")

    # Step 3: Create video
    print("\n[3] Creating MP4 video...")
    video_path = create_video(image_paths, prompts)

    # Step 4: Send Telegram preview
    print("\n[4] Sending Telegram preview...")
    send_telegram_video(video_path)

    # Summary
    print("\n" + "=" * 50)
    print("  ✅ Pipeline complete!")
    print(f"  Output: {video_path}")
    print(f"  Duration: ~{prompts['total_duration_s']}s")
    print(f"  Scenes: {len(prompts['scenes'])}")
    print(f"  Size: {video_path.stat().st_size/1024/1024:.1f}MB")
    print("=" * 50)

if __name__ == "__main__":
    main()
