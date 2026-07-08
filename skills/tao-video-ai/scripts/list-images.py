#!/usr/bin/env python3
"""
list-images.py — Quét thư mục product-photos/ và phân loại ảnh
theo loại shot: hero, detail, lifestyle, packshot.

Usage:
    python list-images.py [--dir path/to/product-photos]

Output:
    output/image-map.json  — mapping ảnh → scene type
"""

import argparse
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ưu tiên nhận diện loại ảnh từ tên file
PATTERN_MAP = {
    "hero": ["hero", "main", "front", "chinh_dien", "chính diện"],
    "detail": ["detail", "close", "can", "cận", "zoom", "texture", "vai", "vải", "chi_tiet", "chi tiết"],
    "lifestyle": ["life", "style", "model", "nguoi_mac", "người mặc", "wear", "street"],
    "packshot": ["pack", "box", "bao_bi", "bao bì", "package", "unbox"],
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def classify_image(filename: str) -> str:
    """Phân loại ảnh dựa trên tên file."""
    name_lower = filename.lower().replace("-", "_").replace(" ", "_")
    for shot_type, patterns in PATTERN_MAP.items():
        for p in patterns:
            if p in name_lower:
                return shot_type
    return "other"


def scan_directory(image_dir: Path) -> dict:
    """Quét thư mục và trả về dict các ảnh phân loại."""
    if not image_dir.exists():
        return {"error": f"Directory not found: {image_dir}", "images": []}

    images = []
    for f in sorted(image_dir.rglob("*")):
        if f.suffix.lower() in IMAGE_EXTENSIONS:
            # Phân loại từ tên file + thư mục cha
            shot_type = classify_image(f.name)
            if shot_type == "other":
                # Thử phân loại từ tên thư mục cha
                parent_dir = f.parent.name.lower()
                for st, patterns in PATTERN_MAP.items():
                    if parent_dir in patterns:
                        shot_type = st
                        break
            images.append({
                "filename": f.name,
                "path": str(f.resolve()),
                "type": shot_type,
                "size_kb": round(f.stat().st_size / 1024, 1),
            })

    return {
        "source_dir": str(image_dir.resolve()),
        "total": len(images),
        "images": images,
        "summary": {
            shot: len([img for img in images if img["type"] == shot])
            for shot in ["hero", "detail", "lifestyle", "packshot", "other"]
        },
    }


def suggest_scene_mapping(scan_result: dict) -> list:
    """Gợi ý mapping ảnh → scenes dựa trên phân loại."""
    images = scan_result.get("images", [])
    if not images:
        return []

    mapping = []
    scenes_def = [
        ("scene_1_hook", "hero"),
        ("scene_2_detail", "detail"),
        ("scene_3_detail2", "detail"),
        ("scene_4_lifestyle", "lifestyle"),
        ("scene_5_cta", "hero"),
    ]

    used = set()
    for scene_name, needed_type in scenes_def:
        candidates = [i for i in images if i["type"] == needed_type and i["filename"] not in used]
        if candidates:
            chosen = candidates[0]
        else:
            # Fallback: lấy ảnh đầu tiên chưa dùng
            fallback = [i for i in images if i["filename"] not in used]
            chosen = fallback[0] if fallback else images[0]

        used.add(chosen["filename"])
        mapping.append({
            "scene": scene_name,
            "image": chosen["filename"],
            "image_type": chosen["type"],
        })

    return mapping


def main():
    parser = argparse.ArgumentParser(description="List & classify product photos")
    parser.add_argument("--dir", default="",
                        help="Path đến thư mục product-photos (mặc định: tìm trong project)")
    parser.add_argument("--json", action="store_true", default=True,
                        help="In ra JSON (mặc định: save + print)")
    args = parser.parse_args()

    # Tìm thư mục ảnh
    if args.dir:
        image_dir = Path(args.dir)
    else:
        # Tự động tìm
        candidates = [
            PROJECT_ROOT / "product-photos",
            PROJECT_ROOT.parent / "product-photos",
            Path.cwd() / "product-photos",
        ]
        image_dir = None
        for c in candidates:
            if c.exists():
                image_dir = c
                break
        if image_dir is None:
            image_dir = candidates[0]  # fallback

    scan_result = scan_directory(image_dir)
    scene_mapping = suggest_scene_mapping(scan_result)

    output = {
        "scan": scan_result,
        "scene_suggestions": scene_mapping,
    }

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "image-map.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Image map saved → {out_path}")
    print(f"    Tổng {scan_result['total']} ảnh tìm thấy")
    print(f"    Phân loại: {json.dumps(scan_result.get('summary', {}))}")

    if not scan_result.get("images"):
        print(f"[!] Không tìm thấy ảnh trong: {image_dir}")
        print(f"    Tạo thư mục và thêm ảnh, hoặc dùng --dir chỉ định đường dẫn khác.")


if __name__ == "__main__":
    main()
