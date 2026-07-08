---
name: tao-video-ai
description: "BẮT BUỘC dùng khi user nói video, Video, tạo video, làm video, đăng video, Reels hoặc Facebook Reels. Tự tạo video AI 15-30s cho Google Ads Match Type Converter bằng OpenAI-KenBurns hoặc Kling 1-key, tự đăng Facebook Reels, rồi trả link về Telegram. Không dùng create_image, không trả JSON ảnh, không hỏi lại."
---

# TAO VIDEO AI — AUTO FACEBOOK REELS

## Mục tiêu

Khi anh Sáng nhắn `video`, Gà phải tự tạo video AI và tự đăng lên Facebook Reels. Không dừng ở kịch bản, không tạo ảnh riêng, không hỏi thêm.

## Luồng chuẩn hiện tại

1. Anh Sáng nhắn Telegram: `video` hoặc câu có ý định tạo/đăng video.
2. Gà dùng `use_skill tao-video-ai`.
3. Gà chạy đúng lệnh trong workspace hiện tại:

```bash
python3 scripts/video_auto_facebook.py
```

4. Script tạo file `video-pipeline.trigger` trong workspace với JSON:

```json
{
  "status": "gen",
  "topic": "Google Ads Match Type Converter - chuyển đổi match type nhanh cho nhà quảng cáo",
  "caption": "default",
  "auto_post_facebook": true
}
```

5. VPS watcher đọc trigger, tự chạy pipeline:
   - `gen-prompt.py` tạo prompt + voice script.
   - `gen-video.py` tạo `video_raw.mp4` bằng provider hợp lệ.
   - `gen-voice.py` tạo `voice.mp3`.
   - `build-final.py` tạo `final.mp4` và gửi preview video về Telegram.
   - `post_video.py` đăng `final.mp4` lên Facebook Reels.
   - Watcher gửi link Facebook Reels về Telegram.

6. Sau khi chạy command, Gà chỉ trả lời:

`Em đang tạo video và sẽ tự đăng Facebook Reels cho anh Sáng. Xong em gửi link lại ngay.`

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

## Facebook posting

- Facebook Page token đã nằm trong env VPS.
- Uploader dùng `scripts/post_video.py` ở workspace Gà.
- Đăng bằng Graph API/Reels endpoint.
- Khi đăng thành công, link có dạng `https://www.facebook.com/reel/...`.

## Lệnh bắt buộc

Khi cần tạo video, chỉ chạy:

```bash
python3 scripts/video_auto_facebook.py
```

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
- Không nói “chưa có quyền đăng Facebook”.
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
