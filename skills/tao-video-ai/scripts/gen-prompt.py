#!/usr/bin/env python3
"""
gen-prompt.py — Sinh prompt set cho AI Video (Stream 4.5 / Kling 3.0)
từ topic + brand style + camera motion references.

Usage:
    python gen-prompt.py "áo khoác da biker nam"
    python gen-prompt.py "áo khoác da biker nam" --provider claude

Output:
    output/prompts.json  — danh sách scenes với prompt hoàn chỉnh
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
OUTPUT_DIR = SKILL_DIR / "output"

# Load .env nếu có
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass


def load_file(path):
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def build_system_prompt(brand_style, camera_prompts, negative_prompt):
    default_brand = "(Không có brand style — dùng tone mặc định luxury)"
    default_camera = "- orbit nhẹ\n- dolly in\n- pan slow\n- key zoom\n- multishot"
    default_negative = "blurry, distorted, bad anatomy, text, watermark, low quality"

    return f"""Bạn là chuyên gia sinh prompt cho AI video generation (Stream 4.5 / Kling 3.0).

NHIỆM VỤ: Sinh JSON prompt set cho video 15-25s gồm 4-5 scenes.

## BRAND STYLE
{brand_style or default_brand}

## CAMERA MOTION REFERENCE
{camera_prompts or default_camera}

## NEGATIVE PROMPT
{negative_prompt or default_negative}

## YÊU CẦU ĐẦU RA
Trả về JSON hợp lệ (không markdown, không giải thích):

{{
  "scenes": [
    {{
      "id": 1,
      "duration_s": 5,
      "camera_motion": "orbit nhẹ",
      "prompt": "Prompt tiếng Anh, mô tả chi tiết: cảnh, chuyển động, chất liệu, ánh sáng",
      "negative_prompt": "Các thứ cần loại trừ",
      "reference_type": "hero"
    }}
  ],
  "total_duration_s": 20,
  "mood": "mood chính",
  "format": "cinematic | koc",
  "notes": "Ghi chú thêm"
}}

QUY TẮC:
1. Scene 1 (0-5s): Hook — orbit hoặc multishot, thu hút ngay
2. Scene 2-3 (5-14s): Body — dolly-in hoặc key zoom, detail sản phẩm
3. Scene 4 (14-20s): Lifestyle — pan slow, người dùng hoặc bối cảnh
4. Scene 5 (20-25s): CTA — key zoom out hoặc product hero shot cuối
5. Prompt phải bằng TIẾNG ANH (AI video tools xử lý tiếng Anh tốt nhất)
6. Mỗi scene duration 4-7s, tổng 18-25s
7. KHÔNG thêm text hay giải thích, CHỈ trả về JSON
8. Nếu topic là thời trang → format koc. Nếu là sản phẩm cao cấp → format cinematic."""


def call_openai(system_prompt, topic):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        print("[!] openai SDK chưa install. pip install openai", file=sys.stderr)
        return None

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Tạo prompt set video cho: {topic}"},
            ],
        )
        text = response.choices[0].message.content.strip()
        return _parse_json(text)
    except Exception as e:
        print(f"[!] OpenAI API call failed: {e}", file=sys.stderr)
        return None


def call_claude(system_prompt, topic):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        from anthropic import Anthropic
    except ImportError:
        print("[!] anthropic SDK chưa install. pip install anthropic", file=sys.stderr)
        return None

    client = Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Tạo prompt set video cho: {topic}"}],
        )
        text = response.content[0].text.strip()
        return _parse_json(text)
    except Exception as e:
        print(f"[!] Claude API call failed: {e}", file=sys.stderr)
        return None


def _parse_json(text):
    """Parse JSON, kể cả khi bị wrap trong markdown."""
    text = text.strip()
    # Try direct
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # ```json ... ```
    m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    # Lớn nhất: { ... }
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    raise json.JSONDecodeError("Không thể parse JSON từ response", text, 0)


def fallback_result(topic):
    return {
        "scenes": [
            {"id": 1, "duration_s": 5, "camera_motion": "orbit nhẹ",
             "prompt": f"Cinematic establishing shot of {topic}, orbiting slowly, luxury studio lighting, premium atmosphere",
             "negative_prompt": "blurry, distorted, low quality, text, watermark",
             "reference_type": "hero"},
            {"id": 2, "duration_s": 5, "camera_motion": "dolly in",
             "prompt": f"Extreme close-up dolly in on {topic} texture, fine details visible, soft light, shallow depth of field",
             "negative_prompt": "blurry, distorted, low quality",
             "reference_type": "detail"},
            {"id": 3, "duration_s": 5, "camera_motion": "pan slow",
             "prompt": f"Lifestyle shot of {topic} in natural environment, slow horizontal pan, golden hour lighting",
             "negative_prompt": "blurry, distorted, low quality",
             "reference_type": "lifestyle"},
            {"id": 4, "duration_s": 5, "camera_motion": "key zoom",
             "prompt": f"Hero final shot of {topic}, slow zoom out, premium dark background, rim light highlight edges",
             "negative_prompt": "blurry, distorted, low quality, text, watermark",
             "reference_type": "hero"},
        ],
        "total_duration_s": 20,
        "mood": "luxury, premium",
        "format": "cinematic",
        "notes": "Manual fallback — edit prompts trước khi dùng",
    }


def main():
    parser = argparse.ArgumentParser(description="Sinh prompt set cho AI video")
    parser.add_argument("topic", help="Topic video (vd: 'áo khoác da biker nam')")
    parser.add_argument(
        "--provider", choices=["openai", "claude", "auto"], default="auto",
        help="AI provider để sinh prompt")
    args = parser.parse_args()

    # Load assets
    brand_style = load_file(ASSETS_DIR / "brand-style.md")
    camera_prompts = load_file(ASSETS_DIR / "camera-prompts.md")
    negative_prompt = load_file(ASSETS_DIR / "negative-prompt.txt")
    system_prompt = build_system_prompt(brand_style, camera_prompts, negative_prompt)

    # Gen
    result = None
    provider = args.provider

    if provider in ("auto", "openai"):
        result = call_openai(system_prompt, args.topic)
    if result is None and provider in ("auto", "claude"):
        result = call_claude(system_prompt, args.topic)
    if result is None:
        print("[!] Không thể gọi AI API. Dùng fallback mẫu.", file=sys.stderr)
        result = fallback_result(args.topic)

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "prompts.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Prompts saved → {out_path}")
    print(f"    {len(result['scenes'])} scenes, ~{result['total_duration_s']}s, format: {result.get('format', 'N/A')}")


if __name__ == "__main__":
    main()
