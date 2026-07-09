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

1. Gọi `scripts/gen_caption.py --task ideas` để tạo 3 ý tưởng.
2. Gửi 3 ý tưởng cho anh Sáng qua Bot Gà, mỗi ý gồm tiêu đề + angle ngắn.
3. Chờ anh Sáng chọn 1 ý.
4. Gọi `scripts/mode1_create_preview.py --idea "..." --angle "..."` để tạo caption + ảnh + state JSON.
5. Gửi preview cho anh Sáng: ảnh local + caption đầy đủ.
6. Chỉ khi anh Sáng OK, gọi `scripts/mode1_post_approved.py --state "..."`.
7. `mode1_post_approved.py` gọi `post_facebook.py`.
8. `post_facebook.py` tự publish ảnh local thành URL public rồi post lên Facebook bằng endpoint `/{page-id}/photos`.

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

1. Gọi `scripts/gen_caption.py --task ad-bundles`.
2. Gọi `scripts/gen_image.py --mode ads --quality medium --bundle-file "..."`
3. Trả đúng 3 bộ creative cho anh Sáng.
4. Không tự đăng Facebook.

Mỗi bộ creative ads phải gồm:

- 1 ảnh ads.
- 1 ad copy 80-150 từ.
- Angle rõ ràng: `pain`, `solution`, hoặc `proof`.

Không được tách ảnh và copy thành output rời. Một creative ads hoàn chỉnh là một cặp ảnh + copy.

## Cơ Chế Ảnh Public Cho Facebook

Facebook Graph API `/photos` cần ảnh public URL. Vì vậy production flow phù hợp nhất là:

1. GPT Image tạo ảnh local trong `scripts/output/`.
2. Khi post thật, `post_facebook.py` gọi `publish_image.py`.
3. `publish_image.py` copy ảnh vào thư mục web tĩnh trên VPS, ví dụ `/opt/my-website/google-ads-toolkit/images/fb-creatives`.
4. Script trả URL public, ví dụ `https://tool.congsang.info.vn/images/fb-creatives/file.png`.
5. `post_facebook.py` gửi `url=image_url` và `caption=caption_text` lên `/{page-id}/photos`.

Lý do chọn cách này:

- Bot Gà/cron chỉ cần xử lý file local, đơn giản và ít lỗi.
- Không cần upload ảnh lên dịch vụ thứ ba.
- Facebook nhận đúng URL public.
- Dễ dry-run và dễ debug bằng file JSON local.

## Cron/Telegram Flow Gợi Ý

Cron không nên tự đăng khi chưa có duyệt.

Flow an toàn:

- Cron sáng gọi `gen_caption.py --task ideas`, Bot Gà gửi 3 ý tưởng cho anh Sáng.
- Anh Sáng trả lời chọn ý 1/2/3.
- Bot Gà gọi `mode1_create_preview.py` để tạo preview ảnh + caption.
- Bot Gà gửi preview ảnh + caption và giữ lại file state.
- Anh Sáng nhắn `OK đăng`.
- Bot Gà gọi `mode1_post_approved.py --state output/mode1_preview_state.json`.

Nếu muốn auto hoàn toàn sau này, chỉ bật khi:

- `DRY_RUN=false`.
- `PUBLIC_IMAGE_DIR` và `PUBLIC_BASE_URL` đã đúng.
- Fanpage token còn quyền `pages_manage_posts`.
- Anh Sáng đã xác nhận lịch auto-post.

## Lệnh Thường Dùng

Tạo 3 ý tưởng:

```bash
python3 scripts/gen_caption.py --task ideas --product "Google Ads Match Type Converter"
```

Tạo caption organic cho ý đã chọn:

```bash
python3 scripts/gen_caption.py --task caption --mode organic --idea "Mỗi lần format keyword lại thấy mệt" --output output/caption.json
```

Tạo ảnh organic:

```bash
python3 scripts/gen_image.py --mode organic --quality low --prompt "..."
```

Tạo preview Mode 1 trong một lệnh cho Bot Gà:

```bash
python3 scripts/mode1_create_preview.py --idea "Mỗi lần format keyword lại thấy mệt" --angle pain --output output/mode1_preview_state.json
```

Post bài đã duyệt từ state:

```bash
python3 scripts/mode1_post_approved.py --state output/mode1_preview_state.json
```

Đăng bài đã duyệt bằng ảnh local:

```bash
python3 scripts/post_facebook.py --image output/post.png --caption-file output/caption.json
```

Đăng bài đã duyệt bằng URL public có sẵn:

```bash
python3 scripts/post_facebook.py --image-url "https://tool.congsang.info.vn/images/fb-creatives/post.png" --caption-file output/caption.json
```

## Biến Môi Trường

Credential chỉ được để trong `scripts/.env`. Không hard-code token/key vào code hoặc tài liệu.

Bắt buộc:

- `OPENAI_API_KEY`
- `FB_PAGE_ID`
- `FB_PAGE_TOKEN`

Bắt buộc khi post thật bằng ảnh local:

- `PUBLIC_IMAGE_DIR`
- `PUBLIC_BASE_URL`

Khuyến nghị:

- `PUBLIC_IMAGE_SUBDIR=fb-creatives`
- `DRY_RUN=true`
- `GRAPH_API_VERSION=v21.0`
- `OUTPUT_DIR=output`
- `BRAND_DB_PATH=/Users/congsang94/Desktop/my-brain/brain.db`
- `CONTEXT_DIR=/Users/congsang94/Desktop/google-ads-toolkit/context-files`

Kiểm tra môi trường:

```bash
python3 scripts/check_env.py
```

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
| Đang gen ảnh (OpenAI) | `in_progress` | Chạy gen_image.py |
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
