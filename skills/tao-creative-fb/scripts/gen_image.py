#!/usr/bin/env python3
"""
gen_image.py — XỬ LÝ ẢNH OFFLINE (CHỈ PILLOW, KHÔNG MẠNG)

Chức năng: Đọc file ảnh có sẵn, vẽ gradient + chèn chữ tiếng Việt, lưu lại.

Usage (MODE 1 - có chữ):
  python3 gen_image.py --input-image "output/raw.png" --add-text "Dòng 1|Dòng 2" --output "output/final.png"

Usage (MODE 2 - không chữ, chỉ copy):
  python3 gen_image.py --input-image "output/raw.png" --mode 2 --output "output/result.png"
"""

import os
import sys
import json
import argparse

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print(json.dumps({"success": False, "error": "Thiếu Pillow. Chạy: pip install Pillow"}), file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    dotenv = None


def add_text_overlay(image_path, text_lines, output_path=None):
    """Vẽ gradient đen mờ 1/3 dưới + chèn chữ tiếng Việt. KHÔNG gọi mạng."""
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    # Tìm font hỗ trợ tiếng Việt
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    font_file = None
    for fp in font_paths:
        if os.path.isfile(fp):
            font_file = fp
            break

    # Vẽ gradient đen mờ 1/3 dưới
    overlay_h = height // 3
    overlay = Image.new("RGBA", (width, overlay_h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for y in range(overlay_h):
        alpha = int(80 + (y / overlay_h) * 100)
        overlay_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    img.paste(overlay, (0, height - overlay_h), overlay)

    # Vẽ chữ
    draw = ImageDraw.Draw(img)
    margin = 60
    line_height_headline = 64
    line_height_sub = 44

    current_y = height - overlay_h + 30
    for i, line in enumerate(text_lines):
        if not line.strip():
            current_y += 10
            continue
        font_size = line_height_headline if i == 0 else line_height_sub

        if font_file:
            try:
                font = ImageFont.truetype(font_file, font_size)
            except Exception:
                font = ImageFont.load_default()
        else:
            font = ImageFont.load_default()

        text = line.strip()
        max_text_width = width - margin * 2
        while font.getlength(text) > max_text_width:
            text = text[:-1]

        draw.text((margin + 2, current_y + 2), text, fill=(0, 0, 0, 200), font=font)
        draw.text((margin, current_y), text, fill=(255, 255, 255), font=font)
        current_y += font_size + 8

    img = img.convert("RGB")
    if output_path is None:
        output_path = image_path
    img.save(output_path, "PNG")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Xử lý ảnh offline - Pillow only")
    parser.add_argument("--input-image", required=True, help="Đường dẫn ảnh gốc (đã tải từ OpenAI)")
    parser.add_argument("--output", required=True, help="Đường dẫn lưu ảnh sau xử lý")
    parser.add_argument("--mode", default="1", choices=["1", "2"],
                        help="1 = có chèn chữ, 2 = chỉ copy ảnh gốc")
    parser.add_argument("--add-text", default="",
                        help="Chữ chèn lên ảnh (MODE 1). Phân cách dòng bằng |")
    args = parser.parse_args()

    if not os.path.isfile(args.input_image):
        print(json.dumps({"success": False, "error": f"Không tìm thấy file: {args.input_image}"}), file=sys.stderr)
        sys.exit(1)

    # Đọc file ảnh gốc
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    if args.mode == "2":
        # Chỉ copy ảnh gốc, không chèn chữ
        img = Image.open(args.input_image)
        img.save(args.output, "PNG")
        result = {
            "success": True,
            "local_path": os.path.abspath(args.output),
            "text_overlay": False,
        }
    else:
        # Mode 1: vẽ gradient + chèn chữ
        text_lines = [t.strip() for t in args.add_text.split("|") if t.strip()] if args.add_text else []
        add_text_overlay(args.input_image, text_lines, args.output)
        result = {
            "success": True,
            "local_path": os.path.abspath(args.output),
            "text_overlay": bool(text_lines),
        }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
