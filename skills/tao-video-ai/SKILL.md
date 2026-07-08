---
name: tao-video-ai
description: "Tạo video 15-25s TikTok/Reels/Shorts từ topic bất kỳ. Gen prompt = OpenAI/Claude cho Stream 4.5/KP3. Render = Higgsfield API hoặc manual paste. Dùng khi user nói: video, tạo video, gen video, làm video quảng cáo, video TikTok, video sản phẩm, tạo content video, dựng video AI."
---

# Tạo Video AI — Workflow 7 Bước (Higgsfield / Stream 4.5 / Kling 3.0)

Skill này tạo video ngắn 15-25s từ **1 topic + thư mục ảnh sản phẩm**.

Pipeline tự động:

- **Gen prompt** → OpenAI (`OPENAI_API_KEY`) hoặc Claude (`ANTHROPIC_API_KEY`) tạo prompt cho Stream 4.5 / KP3.
- **Render video** → Higgsfield API (`HIGGSFIELD_API_KEY`) — hoặc hướng dẫn paste tay lên Higgsfield Dashboard/App.
- **Reference** → `references/` chứa format video thắng (KOC, cinematic) + troubleshoot.

## Trigger

Skill này chạy khi user nói:

- `tạo video [topic]`
- `gen video cho [sản phẩm]`
- `làm video quảng cáo [topic]`
- `video TikTok [sản phẩm]`
- `dựng video AI [chủ đề]`
- `tạo content video [sản phẩm]`
- `video sản phẩm [tên]`

## Pipeline tổng quan

```
Topic → [1] Research Format → [2] Gen Prompt → [3] List Ảnh → [4] Upload & Render → [5] Review → [6] Export → [7] Đăng tải
```

---

## Bước 1: Research & Chọn Format

**Đầu vào:** Topic từ user (vd: "áo khoác da nam phong cách biker")

**Hành động:**
- Xác định format phù hợp:
  - **KOC Format** — thời trang, lifestyle (`references/koc-format.md`)
  - **Cinematic Format** — sản phẩm cao cấp, detail-shot (`references/cinematic-format.md`)
- Tham khảo `assets/brand-style.md` cho brand tone
- Xác định mood, angle storytelling

**Đầu ra:** Format + mood đã chọn.

---

## Bước 2: Sinh Prompt

**Script:** `scripts/gen-prompt.py`

```bash
python3 scripts/gen-prompt.py "tên sản phẩm / chủ đề"
```

**Hành động:**
- Đọc `assets/brand-style.md`, `assets/camera-prompts.md`, `assets/negative-prompt.txt`
- Gọi OpenAI (`gpt-4o`) hoặc Claude (`claude-sonnet-4`) mặc định là OpenAI
- Output: `output/prompts.json` — 4-5 scenes với prompt tiếng Anh cho từng scene

**Đầu ra:** `output/prompts.json`

---

## Bước 3: List Ảnh Sản Phẩm

**Script:** `scripts/list-images.py`

```bash
python3 scripts/list-images.py
```

**Hành động:**
- Quét `product-photos/` trong workspace
- Phân loại ảnh: hero, detail, lifestyle
- Map ảnh vào scenes (output/image-map.json)

**Đầu ra:** `output/image-map.json`

---

## Bước 4: Upload & Render

**Script:** `scripts/upload-higgsfield.py`

```bash
# Tự động (nếu có HIGGSFIELD_API_KEY)
python3 upload-higgsfield.py

# Hoặc manual — in hướng dẫn paste dashboard
python3 upload-higgsfield.py --manual
```

**Chế độ:**
- **API:** Nếu `HIGGSFIELD_API_KEY` được set → tự động gửi scenes
- **Manual:** In ra từng scene với ảnh reference + prompt → user paste lên Higgsfield dashboard

**Lưu ý:** Dashboard là ổn định nhất. API có thể thay đổi.

**Đầu ra:** `output/upload-result.json`

---

## Bước 5: Kiểm Tra Video

**Hành động:**
- Xem video từng scene đã render:
  - Nội dung đúng sản phẩm ✅
  - Màu sắc đúng brand ✅
  - Motion mượt, không artifact ✅
- Nếu sai → xem `references/troubleshoot.md` để fix

---

## Bước 6: Ghép & Export

**Hành động:**
- Ghép 4-5 scenes bằng CapCut / Premiere / DaVinci
- Thêm music + transition
- Export MP4 15-25s

---

## Bước 7: Đăng tải (Tùy chọn)

**Hành động:**
- Đăng lên Facebook Reels / TikTok / Instagram Reels
- Dùng FB_PAGE_ID + FB_PAGE_TOKEN trong .env để auto post (nếu cần)

---

## Các lệnh thường dùng

```bash
# Kiểm tra môi trường
python3 scripts/check_env.py

# Gen prompt
python3 scripts/gen-prompt.py "áo khoác da biker nam"

# List ảnh
python3 scripts/list-images.py

# Upload & render (manual mode)
python3 scripts/upload-higgsfield.py --manual
```

## Pipeline one-shot (toàn bộ)

```bash
cd skills/tao-video-ai
python3 scripts/check_env.py && \
python3 scripts/gen-prompt.py "tên sản phẩm" && \
python3 scripts/list-images.py && \
python3 scripts/upload-higgsfield.py --manual
```

## Nếu gặp lỗi

Xem `references/troubleshoot.md`:
- Sai chi tiết → thêm ảnh cận
- Sai logo → dùng Kling 3.0 element pin
- Motion giật → giảm tốc, tăng duration
