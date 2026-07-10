---
name: sang-tao-creative-fb
description: "Tạo content Facebook hoàn chỉnh cho Google Ads Match Type Converter, luôn có đủ ảnh và văn bản đi cùng nhau. Dùng khi user hoặc GoClaw/Bot Telegram Gà Thảnh Thơi nói: tạo content cho ngày mai, gen bài Page, content free, content organic, tạo creative ads, gen ads, cần creative cho chiến dịch, hoặc đăng bài đã duyệt lên Facebook Fanpage. Mode 1 tạo 3 ý tưởng organic để user chọn, sau đó tạo ảnh GPT Image + caption 80-150 từ và post ảnh kèm caption lên Fanpage. Mode 2 tạo 3 bộ creative ads thủ công, mỗi bộ gồm ảnh ads + ad copy theo 3 angle pain point, solution, social proof. Skill này không bao giờ trả output chỉ có ảnh hoặc chỉ có chữ."
---

# Sáng Tạo Creative FB

Skill này dùng để GoClaw/Bot Telegram Gà Thảnh Thơi tạo nội dung Facebook cho business Google Ads Match Type Converter.

Một output hợp lệ luôn phải có đủ:

- Ảnh: tạo bằng GPT Image API.
- Văn bản: caption hoặc ad copy theo brand voice.

Skill này không gửi bài lên Telegram. Bot Telegram chỉ là nơi anh Sáng ra lệnh, chọn ý, duyệt bài và nhận preview. Khi được duyệt, bài public sẽ được đăng lên Facebook Fanpage.

## Nguồn Context

Trước khi viết content, đọc các nguồn sau nếu có trong môi trường GoClaw:

- `brain.db`: đọc bảng `brand_voice`, giữ đúng tinh thần giọng viết.
- `context-files/SOUL.md`: tone nói chuyện.
- `context-files/USER.md`: thông tin sản phẩm, khách hàng, offer.
- `context-files/AGENTS.md`: giới hạn hành động.
- `context-files/HEARTBEAT.md`: cách nhắn gọn cho Bot Gà/Telegram.

Thông tin sản phẩm phải giữ đúng:

- Sản phẩm là Google Ads Match Type Converter.
- Tool giúp đổi danh sách keyword sang Broad, Phrase, Exact.
- Tool chạy trên trình duyệt, keyword không gửi lên server.
- Dùng được trên điện thoại và máy tính.
- Không cần đăng ký tài khoản.
- Bản free có 3 lượt Copy All.
- Bản Pro mở Copy All không giới hạn và nhận thêm tính năng mới về sau.
- Form lead/góp ý là luồng riêng, không phải cách mở khóa Copy All.

## Mode 1: Content Free Organic

Trigger:

- `tạo content cho ngày mai`
- `gen bài Page`
- `content free`
- `content organic`
- các câu tương tự về bài organic Facebook Page

Luồng chuẩn:

1. Tạo 3 ý tưởng caption (gen bằng LLM, không cần script — agent tự viết theo brand voice).
2. Gửi 3 ý tưởng cho anh Sáng, mỗi ý gồm tiêu đề + angle ngắn.
3. Chờ anh Sáng chọn 1 ý.
4. **Gọi tool `create_image`** để tạo ảnh từ ý tưởng đã chọn:

```jsonc
// create_image — built-in GoClaw tool (provider chain: OpenRouter → Gemini → OpenAI)
// CHỈ dùng 2 tham số này. KHÔNG thêm tham số nào khác.
{
  "prompt": "<prompt ảnh theo ý tưởng đã duyệt + brand style>",
  "aspect_ratio": "1:1"   // hoặc "4:3" cho post Facebook
}
// ⛔ KHÔNG dùng: response_format, n, size, style, quality — create_image không hỗ trợ
```

> **LƯU Ý QUAN TRỌNG:** `create_image` tool chỉ chấp nhận ĐÚNG 2 tham số: `prompt` (string) và `aspect_ratio` (1:1|3:4|4:3|9:16|16:9).
> **KHÔNG thêm** `response_format`, `n`, `size`, `style`, `quality` hoặc bất kỳ tham số OpenAI API nào khác.
> Nếu thêm tham số không hợp lệ → API trả lỗi "response_format invalid" → ảnh không tạo được.
// → trả MEDIA:<path>, file lưu workspace/generated/{YYYY-MM-DD}/
```

5. **Gọi `send_file`** để gửi ảnh preview + caption về Telegram cho anh Sáng duyệt:

```jsonc
{
  "path": "workspace/generated/2026-07-10/creative_001.png",
  "caption": "<caption organic 80-150 từ>"
}
```

6. Chờ anh Sáng OK. **Gà** (Manager) đăng lên Fanpage, KHÔNG phải worker.

> **QUAN TRỌNG**: Agent phải có tool `create_image` + `send_file` (profile `full`).
> Nếu thiếu → ảnh không về Telegram. Fix: `scripts/fix-agent-tools.sh`.

Yêu cầu caption organic:

- 80-150 từ tiếng Việt.
- Có hook, body, CTA mềm.
- Bắt đầu từ cảnh thật, pain thật, hoặc quan sát thật.
- Không bán quá sớm.
- Không hứa kết quả ads.
- CTA nhẹ, ví dụ: `Anh em ghé vào xem thử`, `Nếu đang mất thời gian ở đoạn này thì thử xem có hợp không`.

## Mode 2: Creative Ads

Trigger:

- `tạo creative ads`
- `gen ads`
- `cần creative cho chiến dịch`
- các câu tương tự về creative quảng cáo

Luồng chuẩn:

1. Tạo 3 bộ creative (gen bằng LLM — ad copy 80-150 từ × 3 angle).
2. **Gọi `create_image` 3 lần** (1 ảnh/bundle):

```jsonc
// Bundle 1: pain angle
{"prompt": "<pain angle creative>", "aspect_ratio": "1:1"}
// Bundle 2: solution angle
{"prompt": "<solution angle creative>", "aspect_ratio": "1:1"}
// Bundle 3: proof angle
{"prompt": "<proof angle creative>", "aspect_ratio": "1:1"}
```

3. **Gọi `send_file` với `attachments`** để gửi cả 3 ảnh + ad copy về Telegram:

```jsonc
{
  "attachments": [
    {"path": "workspace/generated/.../bundle1.png", "caption": "[pain] <ad copy>"},
    {"path": "workspace/generated/.../bundle2.png", "caption": "[solution] <ad copy>"},
    {"path": "workspace/generated/.../bundle3.png", "caption": "[proof] <ad copy>"}
  ]
}
```

4. Không tự đăng Facebook. Chờ anh Sáng duyệt → Gà đăng.

> **QUAN TRỌNG**: `create_image` + `send_file` cần profile `full`. Fix: `scripts/fix-agent-tools.sh`.

## Cơ Chế Giao Media Trong GoClaw

GoClaw dùng **`MEDIA:<path>` token** để giao file giữa tool và Telegram:

1. `create_image` tạo file → lưu `workspace/generated/{date}/` → trả `MEDIA:<path>`.
2. `send_file` nhận path → Telegram render thành `sendPhoto`/`sendMediaGroup`.
3. **KHÔNG cần URL public** để preview. Chỉ cần khi **đăng Fanpage** mới cần public URL.

Đăng Fanpage (Gà thực hiện, không phải worker):
- Gà dùng `workstation_exec` chạy `post_facebook.py` (script trong `skills/tao-video-ai/scripts/`).
- Script publish ảnh → web tĩnh → URL public → Graph API `/photos`.
- Hoặc dùng `send_file` với `caption` + path trực tiếp nếu channel hỗ trợ.

> Chi tiết cơ chế: `docs/SKILL_OUTPUT_FIX.md`.

## Cron/Telegram Flow Gợi Ý

Cron không nên tự đăng khi chưa có duyệt.

Flow an toàn:

- Cron sáng (hoặc Gà) tạo 3 ý tưởng caption bằng LLM, gửi cho anh Sáng qua Telegram.
- Anh Sáng trả lời chọn ý 1/2/3.
- Gà gọi tool `create_image` để tạo ảnh + `send_file` để gửi preview về Telegram.
- Gà gửi preview ảnh + caption cho anh Sáng duyệt.
- Anh Sáng nhắn `OK đăng`.
- Gà (Manager) dùng `workstation_exec` chạy `post_facebook.py` (script có thật trong tao-video-ai/scripts/) để đăng lên Fanpage.

Nếu muốn auto hoàn toàn sau này, chỉ bật khi:

- `DRY_RUN=false`.
- `PUBLIC_IMAGE_DIR` và `PUBLIC_BASE_URL` đã đúng.
- Fanpage token còn quyền `pages_manage_posts`.
- Anh Sáng đã xác nhận lịch auto-post.

## Lệnh Thường Dùng (GoClaw Built-in Tools)

> **LƯU Ý:** Các script `gen_caption.py`, `gen_image.py`, `mode1_*.py` **không tồn tại**
> trong thư mục skill này. Skill giờ dùng GoClaw built-in tools.

**Tạo ảnh creative (trong workspace GoClaw):**

```jsonc
// Tool call: create_image
{
  "prompt": "Google Ads tool screenshot, minimalist, blue theme, professional",
  "aspect_ratio": "1:1"
}
// → file: workspace/generated/2026-07-10/image_xxx.png
```

**Gửi ảnh + caption về Telegram cho anh Sáng:**

```jsonc
// Tool call: send_file (single)
{
  "path": "workspace/generated/2026-07-10/image_xxx.png",
  "caption": "<caption organic 80-150 từ>"
}

// Tool call: send_file (batch — 3 creative ads)
{
  "attachments": [
    {"path": "...bundle1.png", "caption": "[pain] ad copy..."},
    {"path": "...bundle2.png", "caption": "[solution] ad copy..."},
    {"path": "...bundle3.png", "caption": "[proof] ad copy..."}
  ]
}
```

**Gà đăng bài lên Fanpage (sau khi anh Sáng duyệt):**

```bash
# Qua workstation_exec (workstation ga-trong-tre-docker)
python3 scripts/post_video.py --image output/creative.png --caption "caption đã duyệt"
# Hoặc dùng post_facebook.py nếu có
```

## Biến Môi Trường

Credential chỉ được để trong `.env` (workspace hoặc VPS env). Không hard-code vào code.

**GoClaw provider chain** (cấu hình ở agent config, không phải skill):
- `OPENAI_API_KEY` → provider OpenAI cho `create_image`
- Provider chain: OpenRouter → Gemini → OpenAI (tự động fallback)

**Fanpage** (chỉ Gà dùng khi đăng):
- `FB_PAGE_ID`
- `FB_PAGE_TOKEN`

Khuyến nghị:

- `DRY_RUN=true` (chỉ preview, không post thật khi chưa duyệt)
- `GRAPH_API_VERSION=v21.0`
- `PUBLIC_IMAGE_SUBDIR=fb-creatives`

## Luật An Toàn

- Luôn tạo đủ ảnh + văn bản.
- Không post Facebook khi chưa có xác nhận của anh Sáng.
- `DRY_RUN=true` thì không gọi Facebook thật.
- Nếu OpenAI fail, retry 1 lần rồi trả lỗi rõ.
- Nếu publish ảnh fail, không được gọi Facebook.
- Nếu Facebook fail, trả nguyên lỗi Graph API rõ ràng.
- Không in token/key ra output.

---

## Task Status Management — Worker Integration

Khi skill này chạy trong context của một Task (Worker Tạo Ảnh), Worker tự quản lý trạng thái task như sau:

### Status Transitions

| Giai đoạn | Status | Khi nào |
|-----------|--------|---------|
| Nhận task, bắt đầu gen ý tưởng | `in_progress` | Ngay sau khi nhận task |
| Đang gen ảnh (OpenAI) | `in_progress` | Dùng tool `create_image` |
| Đang chờ duyệt | `in_progress` | Đã gửi preview, chờ Manager OK |
| Hoàn thành | `done` | Đã trả ảnh + caption ghép cặp, có file/link ảnh thật |
| Lỗi OpenAI | `failed` | Retry 1 lần → vẫn fail |

### Progress Reporting

- "Đang gen ảnh... (có thể mất 15-20s)"
- "Ảnh đã xong. Đang ghép caption..."
- "Chờ anh Sáng duyệt ạ."

### Error Handling (Task-aware)

- **OpenAI API fail:** Retry 1 lần với backoff 5s. Nếu vẫn fail → `failed`
- **Publish ảnh fail:** `failed` với error message. Không gọi Facebook.
- **Thiếu concept:** Hỏi Manager concept cụ thể. Vẫn `in_progress`.

### Output Delivery

Chỉ trả `status: "done"` khi có đủ:
- `caption_paired`
- ít nhất một trong `image_url`, `image_local`

Nếu ảnh đã tạo nhưng chưa public URL, trả `image_local` để Manager gửi file về Telegram.
Nếu thiếu artifact, dùng `in_progress` hoặc `failed`, không được báo done.

```json
{
  "status": "done",
  "output": {
    "image_url": "https://...png",
    "image_local": "output/creative_001.png",
    "caption_paired": "caption đi kèm...",
    "mode": "organic"
  }
}
```

Khi lỗi:
```json
{
  "status": "failed",
  "error": "OpenAI API: rate limit exceeded after 1 retry"
}
```
