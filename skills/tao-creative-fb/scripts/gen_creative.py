#!/usr/bin/env python3
"""
gen_creative.py — MODE 2: Gen 3 BỘ CREATIVE hoàn chỉnh cùng lúc.

Mỗi bộ = 1 ảnh (gpt-image-2 quality medium) + 1 ad copy ghép đôi.
3 góc khác nhau: pain point / solution / social proof.

KHÔNG tự đăng — chỉ trả kết quả để user paste vào Ads Manager.

Usage:
  python gen_creative.py --product "Google Ads Match Type Converter"
  python gen_creative.py --product "Dịch vụ tư vấn Google Ads" --dry-run

Lib: openai, requests, python-dotenv
"""

import os
import sys
import json
import re
import time
import argparse
from openai import OpenAI
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

load_dotenv(ENV_PATH)


def make_slug(text, max_words=5):
    """Rút keyword từ text, trả về slug dạng cac-tu-cach-nhau-bang-gach-ngang."""
    vietnamese_stop = ["ve", "la", "cua", "voi", "cho", "mot", "cac", "nhu",
                       "duoc", "co", "vao", "ra", "len", "xuong", "the", "hien",
                       "khi", "da", "se", "dang", "tu", "noi", "tai", "that",
                       "rat", "nhieu", "lam", "co", "khong", "vui", "long",
                       "anh", "em", "nguoi", "bai", "lam", "cai", "dieu"]
    # Hỗ trợ cả tiếng Việt có dấu
    words = re.findall(r"[a-zA-Zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễđìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ]+", text.lower())
    words = [w for w in words if len(w) >= 3 and w not in vietnamese_stop and not w.startswith("http")]
    words = words[:max_words]
    # Loại bỏ trùng
    seen = set()
    unique = []
    for w in words:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    return "-".join(unique) if unique else "creative-bundle"


def product_slugify(product_name):
    """Rút slug từ tên sản phẩm, loại bỏ từ chung chung."""
    words = re.findall(r"[a-zA-Zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễđìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ]+", product_name.lower())
    stop = ["khoa", "hoc", "cho", "cua", "voi", "va", "la", "cac", "co", "ngay"]
    words = [w for w in words if len(w) >= 3 and w not in stop]
    seen = set()
    unique = []
    for w in words:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    return "-".join(unique[:3]) if unique else "creative-bundle"


# === 3 GÓC TIẾP CẬN cho 3 bộ (MODE 2 — ảnh trơn 100% không chữ) ===
ANGLES = [
    {
        "key": "pain",
        "title": "Pain Point — Khoét nỗi đau",
        "image_prompt": """Realistic photo, candid shot, cinematic lighting. A Vietnamese business owner around 30 sitting alone at a messy home office desk late at night. Only light comes from the laptop screen showing lines of code. Coffee cups, receipts scattered around. He looks exhausted, rubbing his temples. Very authentic documentary style. No text in image.""",
        "caption_angle_hint": "Khoét nỗi đau: mất thời gian, bất tiện, tốn thời gian/tiền bạc nếu không dùng sản phẩm. Hook từ trải nghiệm thật hoặc cảnh thật. Không viết 'dùng thử miễn phí' nếu sản phẩm có giá."
    },
    {
        "key": "solution",
        "title": "Solution — Giải pháp & USP",
        "image_prompt": """Realistic photo, natural daylight. A Vietnamese freelancer working from a cozy coffee shop in Saigon. Large window with afternoon light. Laptop open, notebook and phone on wooden table. Calm, focused expression, subtle smile. Warm tones, plants in background. Lifestyle photography. No text in image.""",
        "caption_angle_hint": "Giải pháp, lợi ích cốt lõi khớp USP. TUYỆT ĐỐI không viết 'dùng thử miễn phí' nếu sản phẩm có giá bán. Hook từ vấn đề thật → USP → CTA rõ."
    },
    {
        "key": "proof",
        "title": "Social Proof — Kết quả thật",
        "image_prompt": """Realistic photo, candid shot. Close-up of a smartphone held by a Vietnamese person. Screen shows a notification with positive business results. Blurred cozy home office background with warm evening light. Very authentic, like a real moment captured quickly. No text in image.""",
        "caption_angle_hint": "Testimonial, câu chuyện kết quả thực tế. Kể chuyện học viên/khách hàng đã dùng và có kết quả. Dùng feedback thật, không bịa."
    }
]


def gen_image(client, prompt, output_path, quality="medium"):
    """Gọi GPT Image API sinh ảnh, trả về image_url (cloud) + local_path + alt_text."""
    for attempt in range(2):
        try:
            response = client.images.generate(
                model="gpt-image-2",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality=quality,
            )
            image_data = response.data[0].b64_json

            import base64
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_data))

            local_path = os.path.abspath(output_path)

            # Alt text từ prompt (câu đầu tiên, gọn)
            alt_text = prompt.replace("\n", " ").strip()
            dot_idx = alt_text.find(".")
            if dot_idx > 20:
                alt_text = alt_text[:dot_idx]
            if len(alt_text) > 100:
                alt_text = alt_text[:97] + "..."

            # Mode 2: chỉ lưu local, không upload cloud
            return {"success": True, "image_url": None, "local_path": local_path, "alt_text": alt_text}

        except Exception as e:
            err_msg = str(e)
            if attempt == 0 and ("rate" in err_msg.lower() or "timeout" in err_msg.lower()):
                time.sleep(3)
            else:
                return {"success": False, "error": err_msg}

    return {"success": False, "error": "Hết lần retry."}


def gen_caption(client, angle_key, angle_hint, product):
    """Gọi OpenRouter gen ad copy theo brand-voice.md vault-ready + 4 file cốt lõi."""
    mode_ads_system = """Bạn viết ad copy Facebook theo brand voice của anh Sáng — từ 5 file: brand-voice.md, SOUL.md, USER.md (USER_SANG.md), AGENTS.md, HEARTBEAT.md.

XƯNG HÔ:
- Tự xưng: "mình" (hoặc "Gà" nếu ở vai Gà Thảnh Thơi).
- Gọi người đọc: "anh em", "bạn".

GIỌNG VIẾT:
- Viết như một người đã làm thật, sai thật, mất tiền thật, rồi ngồi kể lại cho anh em nghe.
- Không viết như thầy giáo giảng bài, không như chuyên gia khoe mình giỏi, không như người bán hàng cố đẩy sản phẩm.
- Gần gũi, thẳng thắn, đời thường, có trải nghiệm, có góc nhìn chiến lược.
- Vui vẻ, hóm hỉnh nhưng nghiêm túc đúng lúc. Thân thiện, am hiểu, thực tế.
- Một đứa trẻ 5 tuổi cũng hiểu được ý chính.
- Không nhại lại, không đệm từ sáo rỗng.

CẤU TRÚC AD COPY:
1. HOOK MẠNH: Mở từ trải nghiệm thật hoặc cảnh thật. Câu ngắn, đánh vào pain.
2. BODY: Vấn đề → USP → lợi ích cốt lõi. TUYỆT ĐỐI không viết "dùng thử miễn phí" nếu sản phẩm có giá bán.
3. CTA: Hành động rõ ràng, khớp mục tiêu. Ví dụ: "Nhận lộ trình tư vấn 1-1", "Giữ chỗ suất ưu đãi".

NGHIÊM CẤM:
- "Bạn có biết rằng...", "Trong thời đại hiện nay...", "Thị trường đầy rẫy..."
- synergy, leverage, maximize, optimize, hàng đầu, số 1, giải pháp đột phá
- "Dùng thử miễn phí" nếu sản phẩm có giá
- Không hứa kết quả, không cam kết ra đơn
- Không dìm đối thủ

TỪ NGỮ: mình, anh em, thật ra thì, đơn giản thôi, nói thật là, nghe thì nhỏ, nhưng làm nhiều mới thấy mệt

OUTPUT:
- CHỈ gồm ad copy, không giải thích, không ghi chú.
- Từ 80 đến 150 từ. ĐẾM KỸ trước khi trả."""

    user_prompt = f"""Viết 1 ad copy cho Facebook Ads.

Sản phẩm: {product}
Góc: {angle_key}
Hướng dẫn: {angle_hint}

Yêu cầu:
- Hook mạnh mở từ cảnh thật/trải nghiệm thật
- Body: vấn đề → USP → lợi ích
- CTA rõ ràng khớp mục tiêu
- Tiếng Việt, brand voice
- 80-150 từ — đếm kỹ
- Chỉ trả ad copy, không kèm giải thích"""

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": mode_ads_system},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1024,
                temperature=0.7,
            )
            caption = response.choices[0].message.content.strip()
            word_count = len(caption.split())

            return {"success": True, "caption": caption, "word_count": word_count, "alt_text": caption[:100] + ("..." if len(caption) > 100 else "")}

        except Exception as e:
            err_msg = str(e)
            if attempt == 0 and ("rate" in err_msg.lower() or "timeout" in err_msg.lower()):
                time.sleep(3)
            else:
                return {"success": False, "error": err_msg}

    return {"success": False, "error": "Hết lần retry."}


def main():
    parser = argparse.ArgumentParser(description="Gen 3 bộ creative (ảnh + ad copy)")
    parser.add_argument("--product", default="Google Ads Match Type Converter",
                        help="Sản phẩm/dịch vụ cần gen creative")
    parser.add_argument("--dry-run", action="store_true",
                        help="Chạy giả lập, không gọi API (xem plan)")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "success": True,
            "dry_run": True,
            "note": "DRY RUN: đây là plan. Set DRY_RUN=false để gen thật.",
            "bundles": [
                {
                    "angle": a["key"],
                    "title": a["title"],
                    "image_prompt": a["image_prompt"][:80] + "...",
                    "caption_angle": a["caption_angle_hint"][:80] + "..."
                }
                for a in ANGLES
            ]
        }, ensure_ascii=False))
        sys.exit(0)

    openai_key = os.environ.get("OPENAI_API_KEY", "")

    if not openai_key:
        print(json.dumps({"success": False, "error": "Thiếu OPENAI_API_KEY"}), file=sys.stderr)
        sys.exit(1)

    image_client = OpenAI(api_key=openai_key)
    caption_client = OpenAI(api_key=openai_key)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = int(time.time())

    bundles = []
    all_ok = True

    for i, angle in enumerate(ANGLES):
        print(f"\n  🔨 Đang tạo bộ {i+1}/3: {angle['title']}...", file=sys.stderr)

        # Bước 1: Gen caption TRƯỚC
        cap_result = gen_caption(caption_client, angle["key"], angle["caption_angle_hint"], args.product)

        if not cap_result["success"]:
            print(f"  ❌ Lỗi caption bộ {i+1}: {cap_result.get('error')}", file=sys.stderr)
            bundles.append({
                "angle": angle["key"],
                "title": angle["title"],
                "image": {"success": False, "error": "Bỏ qua do lỗi caption"},
                "caption": {"success": False, "error": cap_result.get("error")}
            })
            all_ok = False
            continue

        caption_text = cap_result["caption"]
        print(f"  ✅ Caption bộ {i+1} OK ({cap_result.get('word_count', 0)} từ)", file=sys.stderr)

        # Bước 2: Rút keyword từ caption để đặt tên file
        caption_slug = make_slug(caption_text, max_words=6)
        img_filename = f"{caption_slug}-{timestamp}.png"
        img_path = os.path.join(OUTPUT_DIR, img_filename)

        # Bước 3: Gen ảnh SAU, dùng tên file từ caption
        img_result = gen_image(image_client, angle["image_prompt"], img_path, quality="medium")

        if not img_result["success"]:
            print(f"  ❌ Lỗi ảnh bộ {i+1}: {img_result.get('error')}", file=sys.stderr)
            bundles.append({
                "angle": angle["key"],
                "title": angle["title"],
                "image": {"success": False, "error": img_result.get("error")},
                "caption": {"success": False, "error": "Bỏ qua do lỗi ảnh"}
            })
            all_ok = False
            continue

        print(f"  ✅ Ảnh bộ {i+1} OK", file=sys.stderr)

        bundles.append({
            "angle": angle["key"],
            "title": angle["title"],
            "image": {"url": img_result["image_url"], "local_path": img_result["local_path"]},
            "caption": cap_result["caption"],
            "word_count": cap_result.get("word_count", 0),
            "alt_text": img_result.get("alt_text", "")
        })

    # === Tạo file bundle .txt tổng hợp ===
    product_slug = product_slugify(args.product)
    bundle_txt_path = os.path.join(OUTPUT_DIR, f"{product_slug}-{timestamp}.txt")
    txt_lines = []
    txt_lines.append(f"Sản phẩm: {args.product}")
    txt_lines.append(f"Số bộ: {len(bundles)}")
    txt_lines.append("")

    angle_icons = {"pain": "🔥", "solution": "💡", "proof": "✅"}
    for i, b in enumerate(bundles):
        icon = angle_icons.get(b.get("angle", ""), "📦")
        txt_lines.append(f"{'='*40}")
        txt_lines.append(f"{icon} BỘ {i+1} — {b['title']}")
        txt_lines.append(f"{'='*40}")
        img_path = b.get("image", {}).get("local_path", "")
        if img_path:
            txt_lines.append(f"Ảnh: output/{os.path.basename(img_path)}")
        alt_text = b.get("alt_text", "")
        if alt_text:
            txt_lines.append(f"Alt: {alt_text}")
        txt_lines.append("")
        txt_lines.append(b.get("caption", ""))
        txt_lines.append("")

    with open(bundle_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))
    print(f"  📄 File bundle: {bundle_txt_path}", file=sys.stderr)

    output = {
        "success": all_ok,
        "product": args.product,
        "model_image": "gpt-image-2 (quality medium)",
        "model_caption": "gpt-4o-mini",
        "bundles": bundles,
        "total": len(bundles),
        "note": "Đây là creative ads — không tự động đăng. User copy vào Ads Manager."
    }

    # Lưu kết quả ra file
    result_path = os.path.join(OUTPUT_DIR, f"creative_full_{timestamp}.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
