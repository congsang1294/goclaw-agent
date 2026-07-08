---
name: tao-creative-fb
description: "Dual-cron auto post Facebook: Cron 1 gen (LLM), Cron 2 đăng (script thuần)"
---

# TAO CREATIVE FB — DUAL-CRON AUTO POST

## ⏱ Lịch chạy (mỗi ngày)

| Cron   | Giờ   | Agent            | Việc                                                  | File đích                  |
|--------|-------|------------------|-------------------------------------------------------|----------------------------|
| 1️⃣ Gen  | 9:00  | Agent Chat (LLM) | Gen caption (gpt-4o-mini) + ảnh (gpt-image-2)        | `/tmp/post-queue.json`     |
| 2️⃣ Đăng | 9:05  | Script thuần     | Đọc queue → gọi `post_facebook.py` → đăng FB          | Đọc từ `/tmp/post-queue.json` |

→ Cron 2 **KHÔNG dùng LLM** — chạy script trực tiếp. Có queue file là đăng — 100%.

## 📂 Scripts

Tất cả nằm trong `/opt/goclaw/skills/tao-creative-fb/scripts/`:

| Script              | Dùng LLM? | Chức năng                                      |
|---------------------|-----------|------------------------------------------------|
| `gen_queue.py`      | ✅ Có     | Cron 1: Gen caption + ảnh → ghi queue file     |
| `post_from_queue.py`| ❌ Không  | Cron 2: Đọc queue → đăng Facebook              |
| `post_facebook.py`  | ❌ Không  | Engine đăng ảnh + caption lên FB Page API       |

## 🚀 Deploy lên VPS

### 1. Copy scripts lên VPS

```bash
# Tạo thư mục
ssh -p 2018 root@103.97.126.13 "mkdir -p /opt/goclaw/skills/tao-creative-fb/scripts"
ssh -p 2018 root@103.97.126.13 "mkdir -p /opt/goclaw/skills/tao-creative-fb/scripts/output"

# Copy scripts
scp -P 2018 gen_queue.py root@103.97.126.13:/opt/goclaw/skills/tao-creative-fb/scripts/
scp -P 2018 post_from_queue.py root@103.97.126.13:/opt/goclaw/skills/tao-creative-fb/scripts/
scp -P 2018 post_facebook.py root@103.97.126.13:/opt/goclaw/skills/tao-creative-fb/scripts/
scp -P 2018 .env root@103.97.126.13:/opt/goclaw/skills/tao-creative-fb/scripts/

# Copy output/ nếu có ảnh cũ
scp -P 2018 output/*.png root@103.97.126.13:/opt/goclaw/skills/tao-creative-fb/scripts/output/
```

### 2. Cài thư viện trên VPS

```bash
ssh -p 2018 root@103.97.126.13
apt update && apt install -y sshpass jq python3-pip
pip3 install openai python-dotenv requests
```

### 3. Set up CRON trên VPS

```bash
# Mở crontab
crontab -e

# Thêm 2 dòng:
# ┌───────── phút (0-59)
# │ ┌───────── giờ (0-23)
# │ │ ┌───────── ngày (1-31)
# │ │ │ ┌───────── tháng (1-12)
# │ │ │ │ ┌───────── thứ (0-7, CN=0/7)
# │ │ │ │ │
# 0 9 * * * cd /opt/goclaw/skills/tao-creative-fb/scripts && python3 gen_queue.py --idea "So sánh chi phí nhân viên vs AI tự động xử lý từ khóa" --angle pain --mode 1 >> /var/log/goclaw-cron1-gen.log 2>&1
# 5 9 * * * cd /opt/goclaw/skills/tao-creative-fb/scripts && python3 post_from_queue.py >> /var/log/goclaw-cron2-post.log 2>&1
```

### 4. Kiểm tra thủ công

```bash
# Test gen (Cron 1)
cd /opt/goclaw/skills/tao-creative-fb/scripts
python3 gen_queue.py --idea "Mất thời gian xử lý từ khóa thủ công" --angle pain --mode 1

# Kiểm tra queue
cat /tmp/post-queue.json | jq .

# Test đăng (Cron 2)
python3 post_from_queue.py

# Kiểm tra archive
ls -la /tmp/post-queue-history/
```

## 📋 Chi tiết queue file

`/tmp/post-queue.json` — file queue trung gian giữa Cron 1 và Cron 2:

```json
{
  "created_at": "2026-06-25 09:00:01",
  "idea": "So sánh chi phí nhân viên vs AI",
  "angle": "pain",
  "caption": "Mình từng mất cả buổi tối...",
  "image_local": "/opt/.../output/post-1234567890.png",
  "status": "PENDING",
  "fb_post_result": null
}
```

Các trạng thái: `PENDING` → `POSTING` → `DONE` / `FAILED`

## 📹 Chế độ Video & Đăng Đa Nền Tảng (Reels, TikTok, YouTube Shorts)

Khi người dùng nhắn **"video"** trên Telegram hoặc đến lịch tự động **(9:00 sáng Thứ 3 và Thứ 6 hằng tuần)**, Agent thực hiện quy trình sau:

### 1. Phân tích Topic & Gen Video
- **Bước 1:** Đọc `content_plan.json` hoặc bảng `business`/`knowledge` trong `brain.db` để chọn 1 topic phù hợp (ví dụ: sản phẩm mới, KOC review, pain point khách hàng).
- **Bước 2:** Gọi skill `tao-video-ai` để bắt đầu sinh prompt cho Higgsfield (Stream 4.5) hoặc Kling AI.
  ```bash
  cd /app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-video-ai && \
  python3 scripts/gen-prompt.py "<topic>" && \
  python3 scripts/list-images.py && \
  python3 scripts/upload-higgsfield.py
  ```
- **Bước 3:** Gửi file video MP4 (15-25s) preview về Telegram của người dùng để duyệt.

### 2. Đăng tải đa kênh sau khi được duyệt
Khi nhận tin nhắn phản hồi **"OK" / "Duyệt"** từ người dùng:
1. **Facebook Reels:** Đăng video qua Facebook Graph Video API (Publishing Reels API).
2. **TikTok:** Tải lên tự động qua TikTok API (hoặc hướng dẫn người dùng upload manual qua app di động nếu API chưa cấu hình).
3. **YouTube Shorts:** Đăng video lên kênh qua YouTube Data API v3 (thiết lập flag `#Shorts`).

### 3. Báo cáo
Gửi tin nhắn Telegram thông báo kết quả kèm liên kết trực tiếp của 3 nền tảng:
```text
✅ Đã đăng video thành công lên 3 kênh:
🔗 Facebook Reels: <link>
🔗 TikTok: <link>
🔗 YouTube Shorts: <link>
```

## 📜 Logs

- Cron 1 (gen): `/var/log/goclaw-cron1-gen.log`
- Cron 2 (post): `/var/log/goclaw-cron2-post.log`
- Chi tiết post: `/tmp/post-queue-log.txt`
- Archive queue sau khi xử lý: `/tmp/post-queue-history/`

## 🎯 So với SOP

| Yêu cầu SOP                | Cách này                      |
|----------------------------|-------------------------------|
| ✅ Bot GoClaw tự động đăng | Đúng — cron gọi script        |
| ✅ Agent gen nội dung      | Đúng — LLM gen ảnh + caption  |
| ✅ Không cần người canh    | Đúng — 2 cron tự chạy         |
| ✅ Không bị LLM "lười"     | Đúng — Cron 2 thuần script    |
| ✅ Chế độ Video đa kênh    | Đúng — Đăng Reels, TikTok, Shorts |

