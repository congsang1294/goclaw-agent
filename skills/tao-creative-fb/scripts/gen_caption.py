#!/usr/bin/env python3
"""
gen_caption.py — Viết caption Facebook theo brand voice bằng OpenAI.

Model: gpt-4o-mini (OpenAI)
Header: Authorization: Bearer OPENAI_API_KEY
Retry: 1 lần nếu rate limit/timeout.

Usage:
  # MODE 1 — Organic (tone nhẹ, CTA mềm)
  python gen_caption.py --idea "Tiêu đề" --angle "pain" --mode 1

  # MODE 2 — Ads (tone mạnh, USP rõ, CTA mạnh)
  python gen_caption.py --idea "..." --angle "solution" --mode 2

Output: caption 80-150 từ, tiếng Việt, brand voice.
"""

import os
import sys
import json
import time
import argparse
from openai import OpenAI
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")

load_dotenv(ENV_PATH)


def build_system_prompt(angle, mode):
    """Xây system prompt từ 5 file vault-ready: brand-voice.md, SOUL.md, USER.md, AGENTS.md, HEARTBEAT.md."""

    # ----- BASE: Brand Voice + SOUL.md + USER.md + AGENTS.md + HEARTBEAT.md -----
    base = """Bạn viết content Facebook theo brand voice của anh Sáng — đã được định nghĩa trong 5 file: brand-voice.md, SOUL.md, USER.md (USER_SANG.md), AGENTS.md, HEARTBEAT.md.

XƯNG HÔ:
- Tự xưng: "mình" (hoặc "Gà" nếu đang ở vai Gà Thảnh Thơi — trợ lý Google Ads thực chiến).
- Gọi người đọc: "anh em", "bạn". Với anh Sáng: "anh".

GIỌNG VIẾT (từ brand-voice.md + SOUL.md):
- Viết như một người đã làm thật, sai thật, mất tiền thật, rồi ngồi kể lại cho anh em nghe.
- Không viết như thầy giáo giảng bài, không như chuyên gia khoe mình giỏi, không như người bán hàng cố đẩy sản phẩm.
- Gần gũi, thẳng thắn, đời thường, có trải nghiệm, có góc nhìn chiến lược.
- Vui vẻ, hóm hỉnh nhưng nghiêm túc đúng lúc — nhất là khi nói về kỹ thuật, ngân sách, tracking.
- Thân thiện, am hiểu, thực tế. Không lý thuyết suông.
- Viết sâu nhưng không viết khó. Một đứa trẻ 5 tuổi cũng hiểu được ý chính.
- Nếu một câu phải đọc lại 2 lần mới hiểu, câu đó chưa đúng giọng.

CÁCH MỞ BÀI (4 kiểu, CHỌN 1):
1. Mở bằng trải nghiệm thật: "Mình từng...", "Mình đã từng..."
2. Mở bằng vấn đề thật trên thị trường: "Mình hay thấy một chuyện..."
3. Mở bằng cảnh cụ thể: "Mình mở Excel ra..."
4. Mở bằng nhận xét đời thường có góc nhìn: "Nói thật là..."

NGHIÊM CẤM (từ brand-voice.md + AGENTS.md):
- "Bạn có biết rằng...", "Trong thời đại hiện nay...", "Thị trường đầy rẫy..."
- synergy, leverage, solution, streamline, maximize, optimize
- hàng đầu, số 1, top 1, giải pháp đột phá, cam kết, đảm bảo
- Không hứa kết quả: "tăng đơn", "giảm CPC", "tăng ROAS"
- Không dìm đối thủ
- Không nhại lại câu hỏi của người đọc
- Không đệm từ sáo rỗng kiểu "câu hỏi rất hay"
- Không kết thúc bằng "có cần giúp gì thêm không" nếu không cần

CÁCH DẪN DẮT:
1. Kể cảnh quen → 2. Chỉ ra cái khó → 3. Giải thích vì sao khó → 4. Xác nhận cảm giác người đọc → 5. Mới đưa giải pháp.
Không đưa giải pháp quá sớm. Người đọc phải thấy được hiểu trước khi được chào mời.

TỪ NGỮ NÊN DÙNG (từ brand-voice.md + SOUL.md):
mình, anh em, thật ra thì, đơn giản thôi, không cần phức tạp, nói thật là, nghe thì nhỏ, nhưng làm nhiều mới thấy mệt, bình tĩnh xử lý, vít camp, cắn tiền, né bão, đối sánh

CTA ĐÚNG GIỌNG (từ brand-voice.md):
- Nhẹ, không ép, không ra lệnh.
- "Anh em ghé vào xem thử", "Nếu đang mất thời gian ở đoạn này thì thử xem có hợp không"
- Không: "Đăng ký ngay", "Mua ngay", "Click ngay kẻo lỡ"
- Với bài cho Fanpage: có thể thêm dòng giải thích link dùng để làm gì.
- Không dán link quá sớm. Chỉ đưa link khi đúng ngữ cảnh.

CHIỀU SÂU (từ brand-voice.md):
- Nhìn ra vấn đề phía sau vấn đề. Bề mặt → tầng sâu hơn → tầng chiến lược.
- Viết bằng lời đời thường.

NGUYÊN TẮC BÁO CÁO (từ USER.md + HEARTBEAT.md):
- Khi báo anh Sáng: nói rõ chuyện gì xảy ra, ai liên quan, số liệu chính, có cần xử lý gì không.
- Chỉ nhắn khi có VIỆC GIÁ TRỊ. Không spam.
- Gom thành 1 tin nếu có nhiều thông tin.

OUTPUT:
- CHỈ gồm caption, không giải thích, không ghi chú.
- Từ 80 đến 150 từ. ĐẾM KỸ trước khi trả."""

    # ----- MODE 1: Organic -----
    organic = """

=== MODE: CONTENT ORGANIC ===
Giọng như đang tâm sự. CTA nhẹ, không ép.

Cấu trúc:
1. Hook: mở từ cảnh thật, pain thật, quan sát đời thường.
2. Body: vấn đề → insight → giải pháp. Không đưa giải pháp quá sớm.
3. CTA nhẹ: "Anh em ghé vào xem thử", "Nếu đang mất thời gian thì thử xem có hợp không"
"""

    # ----- MODE 2: Ads -----
    ads = """

=== MODE: CREATIVE ADS ===
Hook mạnh hơn organic, USP rõ, CTA phù hợp với mục tiêu chiến dịch.

Cấu trúc:
1. HOOK MẠNH: Câu ngắn, đánh vào pain hoặc mong muốn. Mở từ trải nghiệm thật hoặc cảnh thật.
2. BODY: Vấn đề → USP nổi bật → lợi ích cốt lõi khớp USP. TUYỆT ĐỐI không viết "dùng thử miễn phí" nếu sản phẩm có giá bán.
3. CTA: Hành động rõ ràng, khớp mục tiêu. Ví dụ: "Nhận lộ trình tư vấn 1-1", "Giữ chỗ suất ưu đãi"."""

    # ----- Góc tiếp cận -----
    angle_map = {
        "pain": """

GÓC: PAIN POINT
Khoét nỗi đau, sự bất tiện, tốn thời gian/tiền bạc nếu không dùng sản phẩm.
Mở bài bằng một cảnh quen thuộc, một pain thật.
Xác nhận cảm giác trước. Rồi mới đưa giải pháp.""",
        "solution": """

GÓC: SOLUTION
Giải pháp, lợi ích cốt lõi ăn khớp với USP sản phẩm.
Nói rõ USP: tool xử lý local, không gửi lên server, dùng được trên điện thoại, không cần tài khoản.
Không viết "dùng thử miễn phí" nếu sản phẩm có giá bán thật.""",
        "proof": """

GÓC: SOCIAL PROOF
Dạng testimonial, câu chuyện kết quả thực tế của khách hàng.
Kể chuyện: "Anh Minh, học viên khóa trước, sau 21 ngày đã..."
Dùng feedback/kết quả thật. Không bịa.""",
    }

    prompt = base
    if mode == "1":
        prompt += organic
    elif mode == "2":
        prompt += ads
    prompt += angle_map.get(angle, angle_map["pain"])
    prompt += """

QUAN TRỌNG: ĐẾM SỐ TỪ TRƯỚC KHI TRẢ. Caption từ 80 đến 150 từ. KHÔNG dưới 80, KHÔNG trên 150."""

    return prompt


def count_words(text):
    """Đếm số từ tiếng Việt (tách bằng khoảng trắng)."""
    return len(text.strip().split())


def main():
    parser = argparse.ArgumentParser(description="Viết caption Facebook")
    parser.add_argument("--idea", required=True, help="Ý tưởng / chủ đề bài viết")
    parser.add_argument("--angle", default="pain", choices=["pain", "solution", "proof"],
                        help="Góc tiếp cận")
    parser.add_argument("--mode", default="1", choices=["1", "2"],
                        help="1 = organic (tone nhẹ, CTA mềm), 2 = ads (tone mạnh, CTA rõ)")
    parser.add_argument("--product", default="", help="Tên sản phẩm")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print(json.dumps({"success": False, "error": "Thiếu OPENAI_API_KEY"}), file=sys.stderr)
        sys.exit(1)

    mode_label = "organic" if args.mode == "1" else "ads"
    system_prompt = build_system_prompt(args.angle, args.mode)
    product = args.product or "Google Ads Match Type Converter"

    user_prompt = f"""Viết {'caption organic' if args.mode == '1' else 'ad copy'} cho Facebook.

Sản phẩm: {product}
Ý tưởng chủ đề: {args.idea}
Góc tiếp cận: {args.angle}
{'MODE: CONTENT FREE — tone nhẹ, CTA mềm' if args.mode == '1' else 'MODE: CREATIVE ADS — hook mạnh hơn, USP rõ, CTA rõ ràng'}

Yêu cầu:
- Hook, Body, CTA đầy đủ
- Toàn bộ tiếng Việt
- Đúng brand voice
- {'Không' if args.mode == '1' else 'KHÔNG'} ép mua
- {'CTA nhẹ' if args.mode == '1' else 'CTA rõ ràng, dễ làm theo'}
- Từ 80 đến 150 từ — đếm kỹ trước khi trả
- Chỉ trả caption, không kèm giải thích"""

    # Gọi OpenAI API
    client = OpenAI(api_key=api_key)

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1024,
                temperature=0.7,
            )

            caption = response.choices[0].message.content.strip()
            word_count = count_words(caption)

            # Log cảnh báo nếu vượt quá giới hạn
            warning = ""
            if word_count < 80:
                warning = f"⚠ Chỉ {word_count} từ, thiếu so với yêu cầu 80-150"
            elif word_count > 150:
                warning = f"⚠ {word_count} từ, hơi dài so với yêu cầu 80-150"

            result = {
                "success": True,
                "caption": caption,
                "word_count": word_count,
                "idea": args.idea,
                "angle": args.angle,
                "mode": mode_label,
                "model": "gpt-4o-mini",
                "alt_text": caption[:100] + ("..." if len(caption) > 100 else "")
            }
            if warning:
                result["warning"] = warning

            print(json.dumps(result, ensure_ascii=False))
            sys.exit(0)

        except Exception as e:
            err_msg = str(e)
            if attempt == 0 and ("rate" in err_msg.lower() or "timeout" in err_msg.lower() or "too many" in err_msg.lower()):
                print(f"  ⚠ Retry sau 3s: {err_msg[:100]}", file=sys.stderr)
                time.sleep(3)
            else:
                print(json.dumps({"success": False, "error": err_msg}))
                sys.exit(1)

    print(json.dumps({"success": False, "error": "Hết lần retry."}))
    sys.exit(1)


if __name__ == "__main__":
    main()
