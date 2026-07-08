#!/usr/bin/env python3
"""
gen_queue.py — Cron 1 (9:00): Chào + 3 ý tưởng → chọn ý 1 → gen caption + ảnh → queue

Luồng:
  1. LLM gen 3 ý tưởng xoay quanh tool.congsang.info.vn (3 góc: pain, solution, proof)
  2. Chọn ý số 1 (mặc định)
  3. LLM gen caption cho ý đã chọn (gpt-4o-mini)
  4. Gen ảnh cho ý đã chọn (gpt-image-2)
  5. Copy ảnh ra thư mục public
  6. Ghi /tmp/post-queue.json (kèm cả 3 ý + lời chào)

Cách dùng:
  python3 gen_queue.py                         # chạy mặc định
  python3 gen_queue.py --pick 2                # chọn ý số 2 thay vì số 1
  python3 gen_queue.py --no-upload             # không upload ảnh

Biến môi trường (tự động load từ .env):
  OPENAI_API_KEY
  VPS_HOST, VPS_PORT, VPS_USER, VPS_PASS, VPS_IMAGE_DIR, VPS_BASE_URL
"""

import os, sys, json, time, re, base64, shutil, argparse, subprocess
from openai import OpenAI
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
QUEUE_FILE = "/tmp/post-queue.json"

load_dotenv(ENV_PATH)


def log(msg):
    print(f"  {msg}", file=sys.stderr)


def slugify(text, max_len=50):
    """Rút slug từ text."""
    text = re.sub(r'[^a-zA-Z0-9àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễđìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ\s-]', '', text.lower())
    text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
    text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
    text = re.sub(r'[đ]', 'd', text)
    text = re.sub(r'[ìíịỉĩ]', 'i', text)
    text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
    text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
    text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
    words = re.split(r'\s+', text.strip())
    words = [w for w in words if len(w) >= 3][:5]
    slug = "-".join(words) if words else "post"
    return slug[:max_len]


def gen_ideas(client):
    """Sinh 3 ý tưởng, trả về list [{'title':'...','angle':'...','description':'...'}, ...]."""
    prompt = """Bạn là Gà Thảnh Thơi, trợ lý Google Ads. Sinh 3 ý tưởng caption Facebook.

SẢN PHẨM: Google Ads Match Type Converter (tool.congsang.info.vn) - web app chuyển đổi keyword Broad/Phrase/Exact, xử lý local trên trình duyệt, không gửi lên server, dùng được trên điện thoại.

3 Ý TƯỞNG — mỗi ý 1 góc khác nhau, theo thứ tự:
1. Góc PAIN — khoét nỗi đau mất thời gian xử lý thủ công
2. Góc SOLUTION — giải pháp tiện lợi, xử lý local, không mất data
3. Góc SOCIAL PROOF — kể chuyện người đã dùng và có kết quả

LUẬT CHO MỖI Ý TƯỞNG:
- Mở bài CHỈ được 1 trong 4: "Mình từng...", "Mình hay thấy...", "Mình mở Excel ra...", "Nói thật là..."
- Xưng: "mình" hoặc "Gà"
- Gọi người đọc: "anh em" (KHÔNG dùng "bạn")

CẤM: synergy, leverage, hàng đầu, số 1, emoji, hứa kết quả.

Description CHỈ 1 câu, ngắn gọn, đúng brand voice.

Trả JSON array CHÍNH XÁC format này:
[{"title":"Mình từng...","angle":"pain","description":"Mình từng [trải nghiệm]. Anh em ghé xem thử."}]"""

    for attempt in range(2):
        try:
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.7,
            )
            text = r.choices[0].message.content.strip()
            # Parse JSON array từ response
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            if match:
                text = match.group()
            ideas = json.loads(text)
            if isinstance(ideas, dict):
                # Nếu trả về object, lấy values
                ideas = list(ideas.values())
            # Đảm bảo mỗi idea có title, angle, description
            validated = []
            for i, idea in enumerate(ideas):
                if isinstance(idea, str):
                    validated.append({"title": idea, "angle": ["pain", "solution", "proof"][i], "description": idea[:100]})
                elif isinstance(idea, dict):
                    validated.append({
                        "title": idea.get("title", idea.get("name", f"Ý {i+1}")),
                        "angle": idea.get("angle", ["pain", "solution", "proof"][i]),
                        "description": idea.get("description", idea.get("desc", "")),
                    })
            if len(validated) >= 2:
                return validated
        except Exception as e:
            err = str(e)
            log(f"⚠ Lỗi parse ideas (lần {attempt+1}): {err[:100]}")
            if attempt == 0 and ("rate" in err.lower() or "timeout" in err.lower()):
                time.sleep(3)

    # Fallback ideas
    log("⚠ Dùng fallback ideas")
    return [
        {"title": "Mình từng mất cả buổi tối ngồi copy paste từ khóa", "angle": "pain", "description": "Mình từng mất cả buổi tối ngồi copy paste từ khóa từ file Excel vào Google Ads. Anh em ghé xem thử."},
        {"title": "Mình hay thấy anh em lo lắng về bảo mật data", "angle": "solution", "description": "Mình hay thấy anh em lo lắng về bảo mật data khi dùng tool online. Anh em ghé xem thử."},
        {"title": "Nói thật là, có anh học viên kể", "angle": "proof", "description": "Nói thật là, có anh học viên kể từ ngày dùng tool này, mỗi tối rảnh rang hơn hẳn."},
    ]


def gen_caption(client, idea_title, angle):
    """Sinh caption 80-150 từ bằng gpt-4o-mini."""
    sys_prompt = """Bạn viết caption Facebook theo brand voice của anh Sáng — chủ Google Ads Match Type Converter (tool.congsang.info.vn).

XƯNG HÔ: "mình" hoặc "Gà". Gọi "anh em".

GIỌNG VIẾT: Như người đã làm thật, sai thật, mất tiền thật, rồi kể lại. Gần gũi, đời thường.

MỞ BÀI (CHỌN 1): "Mình từng...", "Mình hay thấy...", "Mình mở Excel ra...", "Nói thật là..."

CẤM: "Bạn" ở đầu câu, synergy, leverage, maximize, emoji, icon, hứa kết quả.

DẪN DẮT: Cảnh quen → cái khó → vì sao khó → giải pháp. KHÔNG đưa giải pháp quá sớm.

80-150 từ. CHỈ trả caption, không giải thích."""

    angle_hint = {
        "pain": "Góc PAIN: Khoét nỗi đau mất thời gian, bất tiện. Hook từ trải nghiệm thật.",
        "solution": "Góc SOLUTION: Giải pháp, USP: xử lý local, không gửi server, dùng được trên điện thoại.",
        "proof": "Góc SOCIAL PROOF: Kể chuyện người đã dùng và có kết quả.",
    }

    for attempt in range(2):
        try:
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"Viết caption Facebook. Sản phẩm: tool.congsang.info.vn. Ý tưởng: {idea_title}. {angle_hint.get(angle, '')} 80-150 từ."}
                ],
                max_tokens=1024,
                temperature=0.7,
            )
            caption = r.choices[0].message.content.strip()
            wc = len(caption.split())
            return caption, wc
        except Exception as e:
            err = str(e)
            if attempt == 0 and ("rate" in err.lower() or "timeout" in err.lower()):
                time.sleep(3)
            else:
                return None, err
    return None, "Hết lần retry."


def gen_image(client, prompt, output_path):
    """Sinh ảnh 1024x1024 bằng gpt-image-2."""
    for attempt in range(2):
        try:
            r = client.images.generate(
                model="gpt-image-2",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="low",
            )
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(r.data[0].b64_json))
            return output_path
        except Exception as e:
            err = str(e)
            if attempt == 0 and ("rate" in err.lower() or "timeout" in err.lower()):
                time.sleep(3)
            else:
                return None
    return None


def is_local_vps():
    """Kiểm tra script đang chạy trên chính VPS đích."""
    host = os.environ.get("VPS_HOST", "")
    if not host:
        return False
    try:
        import socket
        local_ip = socket.gethostbyname(socket.gethostname())
        return local_ip == host or host in ("127.0.0.1", "localhost")
    except Exception:
        return False


def copy_to_public(local_path, filename):
    """Copy ảnh ra thư mục public (local copy nếu trên VPS, scp nếu ở xa)."""
    vps_image_dir = os.environ.get("VPS_IMAGE_DIR", "/opt/my-website/google-ads-toolkit/images")
    base_url = os.environ.get("VPS_BASE_URL", "https://tool.congsang.info.vn/images")

    if is_local_vps():
        os.makedirs(vps_image_dir, exist_ok=True)
        dest = os.path.join(vps_image_dir, filename)
        shutil.copy2(local_path, dest)
        log(f"✅ Copy ảnh public: {dest}")
        return f"{base_url}/{filename}"
    else:
        host = os.environ.get("VPS_HOST", "")
        port = os.environ.get("VPS_PORT", "22")
        user = os.environ.get("VPS_USER", "root")
        password = os.environ.get("VPS_PASS", "")
        if not host:
            log("⚠ Không có VPS_HOST, bỏ qua upload")
            return None
        dest = f"{user}@{host}:{vps_image_dir}/{filename}"
        cmd = ["sshpass", "-p", password, "scp", "-P", str(port),
               "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
               local_path, dest]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                log(f"✅ Upload VPS: {vps_image_dir}/{filename}")
                return f"{base_url}/{filename}"
            else:
                log(f"⚠ Lỗi scp: {r.stderr.strip()[:200]}")
                return None
        except Exception as e:
            log(f"⚠ Lỗi upload VPS: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="Cron 1: Chào + 3 ý tưởng → gen caption + ảnh → queue")
    parser.add_argument("--pick", type=int, default=1, choices=[1, 2, 3],
                        help="Chọn ý thứ mấy để gen (mặc định 1)")
    parser.add_argument("--no-upload", action="store_true", help="Không upload ảnh")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print(json.dumps({"success": False, "error": "Thiếu OPENAI_API_KEY"}))
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    ts = int(time.time())
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # === Bước 1: Gen 3 ý tưởng ===
    log(f"💡 Gen 3 ý tưởng xoay quanh tool.congsang.info.vn...")
    ideas = gen_ideas(client)
    log(f"✅ 3 ý tưởng:")
    for i, idea in enumerate(ideas, 1):
        log(f"   {i}. [{idea['angle']}] {idea['title'][:80]}")

    selected_idx = args.pick - 1
    if selected_idx >= len(ideas):
        selected_idx = 0
    selected = ideas[selected_idx]
    log(f"🎯 Chọn ý số {selected_idx + 1}: {selected['angle']} — {selected['title'][:80]}")
    angle = selected["angle"]

    # === Bước 2: Gen caption cho ý đã chọn ===
    log(f"🧠 Gen caption — ý: {selected['title'][:60]}...")
    caption, wc = gen_caption(client, selected["title"], angle)
    if caption is None:
        print(json.dumps({"success": False, "error": f"Lỗi caption: {wc}"}))
        sys.exit(1)
    log(f"✅ Caption OK ({wc} từ)")

    # === Bước 3: Gen ảnh ===
    image_prompts = {
        "pain": "Realistic photo, candid, cinematic lighting. A Vietnamese business owner sitting at a cluttered desk late at night, tired, rubbing temples. Laptop screen glowing. Coffee cups, papers scattered. No text in image.",
        "solution": "Realistic photo, natural daylight. A Vietnamese freelancer working at a cozy coffee shop. Laptop open, calm expression. Warm tones. Lifestyle photography. No text in image.",
        "proof": "Realistic photo, candid. Close-up of a smartphone held by a Vietnamese person showing positive notification. Blurred background. Warm evening light. No text in image.",
    }
    img_prompt = image_prompts.get(angle, image_prompts["pain"])
    slug = slugify(selected["title"])
    img_filename = f"{slug}-{ts}.png"
    img_local_path = os.path.join(OUTPUT_DIR, img_filename)

    log(f"🖼 Gen ảnh — góc {angle}")
    result_path = gen_image(client, img_prompt, img_local_path)
    if result_path is None:
        print(json.dumps({"success": False, "error": "Lỗi gen ảnh", "caption": caption}))
        sys.exit(1)
    log(f"✅ Ảnh OK: {result_path}")
    img_abs_path = os.path.abspath(result_path)

    # === Bước 4: Copy ảnh public ===
    image_url = None
    if not args.no_upload:
        image_url = copy_to_public(img_abs_path, img_filename)
        if image_url:
            log(f"🌐 Public URL: {image_url}")

    # === Bước 5: Soạn lời chào + ghi queue ===
    greeting_lines = [
        "Chào sáng anh Sáng. Hôm nay em có 3 ý tưởng cho web tool.congsang.info.vn, mời anh tham khảo:",
        "",
    ]
    for i, idea in enumerate(ideas, 1):
        greeting_lines.append(f"{i}. {idea['title']} — {idea['description']}")
    greeting_lines.append("")
    greeting_lines.append(f"Em chọn ý số {selected_idx + 1} để gen ảnh + caption. Anh xem có ổn không ạ.")
    greeting = "\n".join(greeting_lines)

    queue_data = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": ts,
        "product": "Google Ads Match Type Converter (tool.congsang.info.vn)",
        "greeting": greeting,
        "ideas": ideas,
        "selected_index": selected_idx,
        "selected_idea": selected,
        "angle": angle,
        "caption": caption,
        "word_count": wc,
        "image_local": img_abs_path,
        "image_filename": img_filename,
        "image_url": image_url,
        "status": "PENDING",
        "fb_post_result": None,
        "fb_posted_at": None,
    }

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue_data, f, ensure_ascii=False, indent=2)
    log(f"📝 Queue file: {QUEUE_FILE}")

    # In kết quả
    print(json.dumps({
        "success": True,
        "queue_file": QUEUE_FILE,
        "greeting": greeting,
        "selected_idea": selected,
        "caption": caption,
        "word_count": wc,
        "image_url": image_url,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
