#!/usr/bin/env python3
"""
list-images.py — Quét thư mục product-photos/ và phân loại ảnh
theo loại shot: hero, detail, lifestyle.

Usage:
    python list-images.py
    python list-images.py --dir /path/to/product-photos

Output:
    output/image-map.json  — mapping ảnh → scene type
"""

import argparse
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SKILL_DIR / "output"

# Nhận diện loại ảnh từ tên file
PATTERN_MAP = {
    "hero": ["hero", "main", "front", "chinh_dien", "chính diện"],
    "detail": ["detail", "close", "can", "cận", "zoom", "texture", "chi_tiet", "chi tiết", "logo"],
    "lifestyle": ["life", "style", "model", "nguoi_mac", "người mặc", "wear", "street", "outfit"],
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def classify_image(filename):
    name_lower = filename.lower().replace("-", "_").replace(" ", "_")
    for shot_type, patterns in PATTERN_MAP.items():
        for p in patterns:
            if p in name_lower:
                return shot_type
    return "other"


def scan_directory(image_dir):
    if not image_dir.exists():
        return {"error": f"Directory not found: {image_dir}", "images": []}

    images = []
    for f in sorted(image_dir.rglob("*")):
        if f.suffix.lower() in IMAGE_EXTENSIONS:
            shot_type = classify_image(f.name)
            if shot_type == "other":
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
            for shot in ["hero", "detail", "lifestyle", "other"]
        },
    }


def suggest_scene_mapping(scan_result):
    images = scan_result.get("images", [])
    if not images:
        return []

    scenes_def = [
        ("scene_1_hook", "hero"),
        ("scene_2_detail", "detail"),
        ("scene_3_detail2", "detail"),
        ("scene_4_lifestyle", "lifestyle"),
        ("scene_5_cta", "hero"),
    ]

    used = set()
    mapping = []
    for scene_name, needed_type in scenes_def:
        candidates = [i for i in images if i["type"] == needed_type and i["filename"] not in used]
        if candidates:
            chosen = candidates[0]
        else:
            fallback = [i for i in images if i["filename"] not in used]
            chosen = fallback[0] if fallback else images[0]
        used.add(chosen["filename"])
        mapping.append({"scene": scene_name, "image": chosen["filename"], "image_type": chosen["type"]})

    return mapping


def main():
    parser = argparse.ArgumentParser(description="List & classify product photos")
    parser.add_argument("--dir", default="", help="Path đến thư mục product-photos")
    args = parser.parse_args()

    if args.dir:
        image_dir = Path(args.dir)
    else:
        # Tự động tìm
        candidates = [
            SKILL_DIR / "product-photos",
            SKILL_DIR.parent / "product-photos",
            SKILL_DIR.parent.parent / "product-photos",
            Path.cwd() / "product-photos",
            Path(__file__).resolve().parent.parent.parent.parent / "product-photos",
        ]
        image_dir = None
        for c in candidates:
            if c.exists():
                image_dir = c
                break
        if image_dir is None:
            image_dir = candidates[0]

    scan_result = scan_directory(image_dir)
    scene_mapping = suggest_scene_mapping(scan_result)

    output = {"scan": scan_result, "scene_suggestions": scene_mapping}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "image-map.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Image map saved → {out_path}")
    total = scan_result.get("total", 0)
    summary = scan_result.get("summary", {})
    images = scan_result.get("images", [])
    print(f"    {total} ảnh tìm thấy: {json.dumps(summary)}")
    source = scan_result.get("source_dir", scan_result.get("error", "?"))
    print(f"    Nguồn: {source}")

    if not images:
        print(f"[!] Không tìm thấy ảnh trong: {image_dir}")
        print(f"    Tạo thư mục và thêm ảnh, hoặc dùng --dir chỉ định đường dẫn khác.")


if __name__ == "__main__":
    main()
