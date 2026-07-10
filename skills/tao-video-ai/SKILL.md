---
name: tao-video-ai
description: "BẮT BUỘC dùng khi user nói video, Video, tạo video, làm video, đăng video, Reels hoặc Facebook Reels. Tạo video AI 15-30s bằng OpenAI-KenBurns hoặc Kling, trả preview/file/link video về Telegram trước; chỉ đăng Facebook Reels sau khi anh Sáng duyệt. Không dùng create_image, không trả JSON ảnh, không hỏi lại."
---

# TAO VIDEO AI — PREVIEW FIRST, POST AFTER APPROVAL

## Mục tiêu

Khi anh Sáng nhắn `video`, Gà phải tạo video AI và trả preview/file/link về Telegram trước. Không tự đăng Facebook Reels trước khi anh Sáng duyệt.

## Luồng chuẩn hiện tại

1. Anh Sáng nhắn Telegram: `video` hoặc câu có ý định tạo/đăng video.
2. Gà dùng `use_skill tao-video-ai`.
3. **Gà (hoặc worker Làm Video) gọi tool `create_video`** để tạo MP4 thật:

```jsonc
// create_video — tool built-in của GoClaw (provider chain: Gemini → MiniMax → OpenRouter)
{
  "prompt": "<prompt sinh từ gen-prompt.py hoặc tự viết theo topic>",
  "duration": 8,            // 4 | 6 | 8 (giây)
  "aspect_ratio": "9:16"    // dọc cho Reels/TikTok/Shorts
}
// → trả về MEDIA:<path>, file lưu workspace/generated/{YYYY-MM-DD}/
```

> **BẮT BUỘC**: media chỉ về Telegram qua `MEDIA:` token. Để file đến chat,
> gọi `send_file` sau khi `create_video` xong (xem "Trả video về Telegram" bên dưới).
> Nếu agent thiếu tool `create_video`/`send_file` → skill KHÔNG trả được preview.
> Fix: chạy `scripts/fix-agent-tools.sh` (profile `full`).

4. **Pipeline nâng cao (nếu cần voiceover + ghép)** — chỉ khi cần voice, chạy
   qua workstation_exec (yêu cầu đã `bind-workstation.sh` + allowlist có `python3`, `ffmpeg`):

```bash
# qua tool workstation_exec, KHÔNG phải shell trực tiếp
python3 scripts/gen-prompt.py     # sinh prompt + voice script
python3 scripts/gen-video.py      # tạo video_raw.mp4 (provider hợp lệ)
python3 scripts/gen-voice.py      # tạo voice.mp3
python3 scripts/build-final.py    # ghép final.mp4
```

5. **Trả video về Telegram** — gọi `send_file`:

```jsonc
// send_file — built-in, render thành Telegram sendVideo
{
  "path": "workspace/generated/2026-07-10/abc.mp4",
  "caption": "Preview video nhé anh Sáng. Duyệt rồi em đăng."
}
// hoặc dùng attachments: [{path, caption}, ...] để gửi batch
```

> KHÔNG gọi `post_video.py` ở bước preview. Chỉ đăng Reels sau khi anh Sáng duyệt.

6. Sau khi gửi preview, Gà trả lời:

`Em đang tạo video preview cho anh Sáng. Xong em gửi video ở Telegram để anh duyệt trước.`

## Provider video

Chỉ dùng 2 provider này:

1. `OpenAI-KenBurns`
   - Dùng `OPENAI_API_KEY` hoặc `OPENAI_KEY_REAL`.
   - Tạo ảnh bằng OpenAI `gpt-image-1`.
   - Dùng `ffmpeg` tạo MP4 dọc 9:16.

2. `Kling`
   - Chỉ chạy nếu có `KLING_API_KEY`, `KLING_SECRET_KEY`, hoặc `KLING_TOKEN`.
   - Kling hiện dùng 1 key, ưu tiên biến `KLING_API_KEY`.

Không dùng Pollinations. Không dùng HuggingFace. Nếu thiếu key provider nào thì bỏ qua provider đó, không hỏi user.

## Facebook posting (Gà đăng cuối cùng)

- Gà là người duy nhất đăng lên Fanpage (Manager role), **sau khi anh Sáng duyệt** bộ cuối.
- Worker Làm Video **chỉ trả preview về Telegram**, không tự đăng.
- Gà đăng qua `workstation_exec` chạy `post_video.py` (Graph API Reels endpoint):

```bash
# Gà gọi workstation_exec (workstation ga-trong-tre-docker, allowlist có python3)
python3 scripts/post_video.py --video output/final.mp4 --caption "<caption đã duyệt>"
```

- Facebook Page token nằm trong env VPS (`FB_PAGE_ID`, `FB_PAGE_TOKEN`).
- Khi đăng thành công, `post_video.py` trả link dạng `https://www.facebook.com/reel/...`.
- Gà phải gửi link đó về Telegram cho anh Sáng ngay.

## Lệnh bắt buộc

**Cách 1 (ưu tiên):** Dùng GoClaw built-in `create_video` tool
```jsonc
// create_video → MEDIA:<path> → send_file về Telegram
{"prompt": "<topic>", "duration": 8, "aspect_ratio": "9:16"}
```

**Cách 2 (nâng cao — cần voiceover + ghép:** Qua `workstation_exec`:
```bash
python3 scripts/video_auto_facebook.py
```
> Script này tồn tại trong `tao-video-ai/scripts/`. Dùng khi cần voiceover hoặc pipeline đầy đủ.
> Yêu cầu workstation đã bind + allowlist có `python3`, `ffmpeg`.

Không chạy các lệnh cũ:

```bash
python3 scripts/tao_video.py
facebook-post-video
```

## Luật cứng

- Luôn gọi đúng là `anh Sáng`, không gọi `Anh Sang`.
- Không gọi `create_image` cho lệnh video.
- Không trả JSON ảnh kiểu `{ "aspect_ratio": ..., "filename_hint": ..., "prompt": ... }`.
- Không hỏi style/kích thước/video sản phẩm gì nếu anh chỉ nhắn `video`.
- Không đề xuất Canva, InVideo, CapCut.
- Không nói “hệ thống chưa hỗ trợ tạo video”.
- Không nói “chưa có quyền đăng Facebook” nếu env đã có token; nhưng vẫn phải chờ anh Sáng duyệt trước khi đăng.
- Không dùng `/tmp/video-pipeline.trigger`; trigger phải nằm trong workspace hiện tại.
- Không tự hứa TikTok/Youtube khi chưa setup API. Flow hiện tại chỉ chốt Facebook Reels.

# GÀ TRỐNG TRE - VIDEO/REELS APPROVAL FLOW LOCK
- Chỉ dùng OpenAI và Kling cho tạo video; không dùng create_image, Canva, InVideo hoặc provider không có key.
- Khi anh Sáng nhắn "video", "làm video", "Reels" hoặc gửi file MP4: nhận yêu cầu và tạo/gửi preview về Telegram trước.
- Tuyệt đối không tự đăng Facebook ngay ở bước tạo preview.
- Chỉ khi anh Sáng nhắn "OK", "duyệt", "đăng đi" sau preview thì mới gọi uploader Facebook Reels.
- Sau khi đăng thành công, phải trả link Reels Facebook cho anh Sáng ngay trong Telegram.
- Nếu có file video anh Sáng upload trong `.uploads`, ưu tiên đăng chính file đó sau khi anh nhắn OK.
- Luồng hợp lệ để nộp bài: anh Sáng nói chuyện với Gà trên Telegram → Gà nhận/tạo video → anh OK → Gà đăng Facebook → Gà trả link.

---

## Task Status Management — Worker Integration

Khi skill này chạy trong context của một Task (Worker Làm Video), Worker tự quản lý trạng thái task như sau:

### Status Transitions

| Giai đoạn | Status | Khi nào |
|-----------|--------|---------|
| Nhận task, bắt đầu pipeline | `in_progress` | Ngay sau khi nhận task |
| Đang gen prompt | `in_progress` | Chạy gen-prompt.py |
| Đang render video | `in_progress` | Chạy gen-video.py (có thể 2-3 phút) |
| Đang ghép voice + final | `in_progress` | Chạy gen-voice.py + build-final.py |
| Preview sẵn sàng | `done` | Trả video preview cho Manager |
| Lỗi provider hoặc timeout | `failed` | Retry hết lượt → fail |

### Progress Reporting (quan trọng — video generation lâu)

Worker nên báo progress định kỳ nếu pipeline chạy >30s:

- "Đang gen prompt..."
- "Đang render video với OpenAI-KenBurns... (ước tính 2 phút)"
- "Đang ghép voice..."
- "Video sắp xong..."

### Error Handling (Task-aware)

- **Provider fail (OpenAI/Kling):** Retry với provider còn lại. Nếu cả 2 fail → `failed`
- **Timeout (>600s):** Task tự động `failed`. Báo Manager.
- **ffmpeg error:** `failed` + error log. Không retry.

### Output Delivery

Chỉ trả `status: "done"` khi có video thật để Manager gửi Telegram:
- ưu tiên `video_preview`
- nếu không có preview thì phải có `video_url`
- nếu mới có file local, ghi path đó vào `video_preview`

Nếu render/upload chưa xong, dùng `in_progress`.
Nếu provider fail hết lượt, dùng `failed`.
Không báo done khi chưa có preview/file/link video.

```json
{
  "status": "done",
  "output": {
    "video_url": "https://...final.mp4",
    "video_preview": "https://...preview.mp4",
    "duration_seconds": 18,
    "provider": "openai-ken-burns"
  }
}
```

Khi lỗi:
```json
{
  "status": "failed",
  "error": "Cả OpenAI và Kling đều fail. OpenAI: timeout. Kling: API error 500."
}
```

### Lưu ý đặc thù Video

- **Không tự đăng Facebook** — chỉ trả preview. Chờ Manager bảo "OK" mới post.
- **Pipeline dài** — Worker nên báo progress mỗi 30s để Manager biết task vẫn alive.
- **Retry chiến lược** — Nếu OpenAI fail, thử Kling. Nếu Kling fail, thử OpenAI lại. Retry tối đa 2 lần/provider.
