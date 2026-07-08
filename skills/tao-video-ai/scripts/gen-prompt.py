#!/usr/bin/env python3
"""
gen-prompt.py — Sinh prompt set cho AI Video (Kling 3.0 / Runway Gen-4 / Stream 4.5)
từ topic + brand style + camera motion references.

Usage:
    python gen-prompt.py "áo khoác da biker nam" --style assets/brand-style.md --camera assets/camera-prompts.md

Output:
    output/prompts.json  — danh sách scenes với prompt hoàn chỉnh
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Thử import — fallback về http request nếu không có SDK
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Load .env nếu có
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass


def load_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def build_system_prompt(brand_style: str, camera_prompts: str, negative_prompt: str) -> str:
    fallback_camera = "- orbit nhẹ\n- dolly in\n- pan slow\n- key zoom\n- multishot"
    return f"""Bạn là chuyên gia sinh prompt cho AI video generation (Kling 3.0, Runway Gen-4, Stream 4.5).

NHIỆM VỤ: Sinh JSON prompt set cho video 15-25s gồm 3-5 scenes.

## BRAND STYLE
{brand_style or "(Không có brand style — dùng tone mặc định luxury)"}

## CAMERA MOTION REFERENCE (chọn 1 trong 5 dạng)
{camera_prompts or fallback_camera}

## NEGATIVE PROMPT MẶC ĐỊNH
{negative_prompt or "blurry, distorted, bad anatomy, extra limbs, missing fingers, text, watermark, logo, signature, low quality"}

## YÊU CẦU ĐẦU RA
Trả về JSON hợp lệ (không markdown, không giải thích):

{{
  "scenes": [
    {{
      "id": 1,
      "duration_s": 5,
      "camera_motion": "orbit nhẹ",
      "prompt": "Prompt tiếng Anh, mô tả chi tiết: cảnh, chuyển động, chất liệu, ánh sáng, mood. Chi tiết đến từng sợi vải.",
      "negative_prompt": "Các thứ cần loại trừ",
      "reference_type": "hero | detail | lifestyle"
    }}
  ],
  "total_duration_s": 20,
  "mood": "mood chính",
  "notes": "Ghi chú thêm cho scene đặc biệt"
}}

QUY TẮC:
1. Scene 1 (0-5s): Hook — dùng orbit hoặc multishot, thu hút ngay
2. Scene 2-3 (5-15s): Body — dolly-in hoặc key zoom, detail sản phẩm
3. Scene 4 (15-20s): Context / lifestyle — pan slow, người dùng hoặc bối cảnh
4. Scene 5 (20-25s): CTA / kết — key zoom ra hoặc product hero shot cuối
5. Prompt phải bằng TIẾNG ANH (AI video tools xử lý tiếng Anh tốt nhất)
6. Mỗi scene có duration 4-7s, tổng 15-25s
7. KHÔNG thêm text hay giải thích, CHỈ trả về JSON
"""


def call_claude(system_prompt: str, topic: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[!] ANTHROPIC_API_KEY chưa set. Dùng fallback ChatGPT hoặc manual.", file=sys.stderr)
        return None

    if Anthropic is None:
        print("[!] anthropic SDK chưa install. pip install anthropic", file=sys.stderr)
        return None

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Tạo prompt set cho: {topic}"}],
    )
    text = response.content[0].text.strip()
    return json.loads(text)


def _extract_json(text: str) -> dict:
    """Parse JSON từ response, kể cả khi bị wrap trong markdown."""
    import re
    text = text.strip()
    # Thử parse trực tiếp
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Tìm ```json ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    # Tìm { ... } lớn nhất
    brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(1))
        except json.JSONDecodeError:
            pass
    raise json.JSONDecodeError("Không thể parse JSON từ response", text, 0)


def call_chatgpt(system_prompt: str, topic: str) -> dict | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[!] OPENAI_API_KEY chưa set.", file=sys.stderr)
        return None

    if OpenAI is None:
        print("[!] openai SDK chưa install. pip install openai", file=sys.stderr)
        return None

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Tạo prompt set cho: {topic}"},
            ],
        )
        text = response.choices[0].message.content.strip()
        return _extract_json(text)
    except Exception as e:
        print(f"[!] ChatGPT API call failed: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Sinh prompt set cho AI video")
    parser.add_argument("topic", help="Topic video (vd: 'áo khoác da biker nam')")
    parser.add_argument("--style", default=str(ASSETS_DIR / "brand-style.md"),
                        help="Path đến brand-style.md")
    parser.add_argument("--camera", default=str(ASSETS_DIR / "camera-prompts.md"),
                        help="Path đến camera-prompts.md")
    parser.add_argument("--negative", default=str(ASSETS_DIR / "negative-prompt.txt"),
                        help="Path đến negative-prompt.txt")
    parser.add_argument("--provider", choices=["claude", "chatgpt", "auto"], default="auto",
                        help="AI provider để sinh prompt")
    args = parser.parse_args()

    # Load assets
    brand_style = load_file(Path(args.style))
    camera_prompts = load_file(Path(args.camera))
    negative_prompt = load_file(Path(args.negative))
    system_prompt = build_system_prompt(brand_style, camera_prompts, negative_prompt)

    # Gen
    result = None
    provider = args.provider

    if provider in ("auto", "claude"):
        result = call_claude(system_prompt, args.topic)
    if result is None and provider in ("auto", "chatgpt"):
        result = call_chatgpt(system_prompt, args.topic)

    if result is None:
        print("[!] Không thể gọi AI. Hãy set ANTHROPIC_API_KEY hoặc OPENAI_API_KEY.", file=sys.stderr)
        print("[*] Fallback: output mẫu để bạn edit tay.", file=sys.stderr)
        result = {
            "scenes": [
                {"id": 1, "duration_s": 5, "camera_motion": "orbit nhẹ",
                 "prompt": f"[Manual] Cinematic shot of {args.topic}, orbiting view, luxury lighting",
                 "negative_prompt": negative_prompt or "blurry, distortion",
                 "reference_type": "hero"},
                {"id": 2, "duration_s": 5, "camera_motion": "dolly in",
                 "prompt": f"[Manual] Close-up detail shot of {args.topic}, dolly in slow, fabric texture visible",
                 "negative_prompt": negative_prompt or "blurry, distortion",
                 "reference_type": "detail"},
                {"id": 3, "duration_s": 5, "camera_motion": "pan slow",
                 "prompt": f"[Manual] Lifestyle shot of {args.topic} being worn, pan slow, natural lighting",
                 "negative_prompt": negative_prompt or "blurry, distortion",
                 "reference_type": "lifestyle"},
                {"id": 4, "duration_s": 5, "camera_motion": "key zoom",
                 "prompt": f"[Manual] Hero shot of {args.topic} on display, key zoom out, premium atmosphere",
                 "negative_prompt": negative_prompt or "blurry, distortion",
                 "reference_type": "hero"},
            ],
            "total_duration_s": 20,
            "mood": "luxury, premium",
            "notes": "Manual mode — edit prompts trước khi dùng",
        }

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "prompts.json"
    n_scenes = len(result.get("scenes", [])) if isinstance(result, dict) else 0
    # Debug trạng thái
    is_api_result = not result.get("notes", "").startswith("Manual")
    print(f"[debug] result_source={'API' if is_api_result else 'FALLBACK'}, scenes={n_scenes}", file=sys.stderr)
    # Nếu là fallback, in thêm debug về env
    if not is_api_result:
        import os
        print(f"[debug] OPENAI_API_KEY in env: {'YES' if os.environ.get('OPENAI_API_KEY') else 'NO'}", file=sys.stderr)
        print(f"[debug] Script dir: {Path(__file__).resolve().parent}", file=sys.stderr)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Prompts saved → {out_path}")
    print(f"    Tổng {len(result['scenes'])} scenes, ~{result['total_duration_s']}s")


if __name__ == "__main__":
    main()
