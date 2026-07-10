# SKILL_OUTPUT_FIX.md — Skill chạy xong nhưng không trả output về Telegram

> **File:** `docs/SKILL_OUTPUT_FIX.md`
> **Triệu chứng:** Skill chạy (tạo ảnh/video/caption) — output không về Telegram.
> **V3 fix date:** 2026-07-10

---

## 🧬 Tóm tắt 3 lỗi chồng

| # | Lỗi | Tác hại | Fix |
|---|-----|---------|-----|
| A | Tool profile `coding` — có `create_image`/`create_video` (gen) nhưng **không có** `send_file`/`message` (deliver) | Gen được ảnh/video nhưng Telegram không nhận | `scripts/fix-agent-tools.sh` → profile `full` |
| B | Skills trỏ tới scripts **không tồn tại** trong thư mục (`gen_caption.py`, `mode1_*.py`) | Skill không chạy được → báo lỗi | Fix SKILL.md → dùng `create_image`/`create_video` built-in |
| C | `delegate` tool **đã bị gỡ** khỏi GoClaw runtime | Manager không delegate được task cho worker | Dùng `team_tasks` assign + `@agentId` |

---

## 1. Nguyên nhân gốc rễ: Tool profile (lỗi chính)

### Cơ chế media trong GoClaw

```
Agent tool call: create_image / create_video
    │
    ▼
Tool sinh file → workspace/generated/{YYYY-MM-DD}/file.xxx
    │
    ▼
Tool trả MEDIA:<path> token
    │
    ▼
Agent gọi send_file {path, caption}
    │
    ▼
Telegram render → sendPhoto / sendVideo / sendMediaGroup
```

**Để pipeline này chạy, agent cần BẢY tool group:**

| Tool group | Tools | Agent cần để? |
|------------|-------|--------------|
| `group:media_gen` | `create_image`, `create_video`, `create_audio` | Tạo media |
| `group:fs` | `send_file`, `write_file`, `read_file` | Gửi file về chat |
| `group:messaging` | `message` | Gửi text + MEDIA token |

### Bảng profile và hậu quả

| Profile | Có media_gen? | Có send_file? | Có message? | Kết quả |
|---------|:---:|:---:|:---:|---------|
| `full` | ✅ | ✅ | ✅ | ✅ Skill trả output về Telegram |
| `coding` | ✅ | ❌ | ❌ | ❌ Gen được, **không deliver được** |
| `messaging` | ❌ | ✅ | ✅ | ❌ Không gen được |

**Triệu chứng đúng của bạn:** skill chạy, ảnh/video được tạo (có file trong workspace), nhưng không về Telegram. Đây chính là dấu hiệu của **profile `coding`**.

### Fix

```bash
# Xem profile hiện tại
curl -s -H "Authorization: Bearer $GOCLAW_GATEWAY_TOKEN" \
  http://localhost:18790/v1/agents | jq '.agents[] | {key: .agent_key, tools: .tools_config}'

# Cập nhật → profile full
./scripts/fix-agent-tools.sh
docker restart goclaw-bai-13-goclaw-1
```

Nếu API không nhận `"profile": "full"`, set thủ công trong `config.json`:
```json5
// config.json — phần tools
{
  "tools": {
    "profile": "full",  // hoặc "coding" tùy agent
    "alsoAllow": ["send_file", "message", "create_image", "create_video"]
  }
}
```

Sau đó restart gateway.

---

## 2. Script không tồn tại trong skill

### sang-tao-creative-fb

Thư mục skill có: caption-templates.md, image-prompt-templates.md, SKILL.md
**Không có:** scripts/, gen_caption.py, gen_image.py, mode1_*.py, post_facebook.py

**Skill cũ bảo chạy:**
```bash
python3 scripts/gen_caption.py --task ideas
python3 scripts/mode1_create_preview.py --idea "..."
python3 scripts/post_facebook.py --image output/creative.png
```
→ **tất cả đều không tồn tại** → skill fail ngay.

**Fix:** SKILL.md đã được cập nhật. Giờ dùng GoClaw built-in tools:
- `create_image` thay cho `gen_image.py`
- `send_file` thay cho cơ chế publish ảnh thủ công
- `workstation_exec` + `post_facebook.py` cho đăng Fanpage (Gà thực hiện, không phải worker)

### tao-video-ai

Thư mục skill có: scripts/ thật (gen-video.py, build-final.py...). OK.
Nhưng skill cũ **không dùng `create_video` + `send_file`** để trả preview về Telegram.
Nó dùng pipeline `video_auto_facebook.py` — cơ chế watcher không phải GoClaw built-in.

**Fix:** SKILL.md đã được cập nhật. Flow mới:
1. Gọi `create_video` → tạo MP4 + trả `MEDIA:<path>`
2. Gọi `send_file` → gửi preview về Telegram

Pipeline scripts vẫn dùng cho voiceover + ghép nâng cao (qua `workstation_exec`).

---

## 3. `delegate` tool đã bị gỡ

Theo `goclaw-docs/core-concepts/tools-overview.md`:
> "The `delegate` tool has been removed. Delegation is now handled via agent teams:
> leads create tasks on the shared board (`team_tasks`) and delegate to member agents via `spawn`."

### Fix trong codebase
- `agent/AGENTS.md` — xóa tham chiếu `delegate`, thay bằng `team_tasks` + `@agentId`
- DEPLOYMENT — `tools_config` không có `delegate.enabled`
- Worker dispatch qua: `team_tasks` tạo task → assign → `@agentId` trong group chat

---

## 4. Cách Gà output artifact về Telegram (CHECKLIST)

| Loại | Công cụ | Định dạng | Ví dụ |
|------|---------|-----------|-------|
| Text (caption, ideas) | Reply message | Text thường | `"Bài viết đây anh Sáng:..."` |
| Ảnh | `send_file` | `{path, caption}` | `{"path":"workspace/.../img.png","caption":"Ảnh creative"}` |
| Video | `send_file` | `{path, caption}` | `{"path":"workspace/.../vid.mp4","caption":"Preview video"}` |
| Batch ảnh | `send_file` | `{attachments: [...]}` | `{"attachments":[{"path":"...","caption":"..."}]}` |
| Đăng Fanpage | `workstation_exec` + `post_facebook.py` | — | Gà thực hiện sau duyệt |

---

## 5. Luồng fix trên VPS

```bash
# Bước 1: Fix workstation binding
export GOCLAW_GATEWAY_TOKEN="<admin token>"
./scripts/bind-workstation.sh

# Bước 2: Fix tool profile (full → gen + deliver)
./scripts/fix-agent-tools.sh

# Bước 3: Restart GoClaw
docker restart goclaw-bai-13-goclaw-1

# Bước 4: Test
# Gửi Telegram: "tạo ảnh" hoặc "tạo video"
# Output phải về Telegram (ảnh = sendPhoto, video = sendVideo, caption = text)
```

---

## 6. Debug nếu vẫn không về Telegram

| Triệu chứng | Nguyên nhân | Kiểm tra |
|-------------|------------|----------|
| Image gen → OK, nhưng không gửi | Profile sai (`coding`) | `docker logs goclaw... | grep "tool call"` — có `create_image` mà không có `send_file`? |
| Image gen → "binary 'python3' not allowed" | Allowlist workstation thiếu | `./scripts/verify-workstation.sh` |
| Video quá to → bị skip | > 20MB (`media_max_bytes`) | Kiểm tra file size. Set `media_max_bytes` to 50MB. |
| `MEDIA:` path sai | File không tồn tại trên workspace | `docker exec ... ls -la workspace/generated/` |
| Worker trả `[done]` nhưng Gà không gửi | Gà chưa gọi `send_file` | Parse log: worker done → Gà có gọi send_file không? |
| `delegate tool not found` | Tool cũ đã gỡ | Dùng `team_tasks` + `@agentId` thay thế |

---

*Nguồn: goclaw-docs (core-concepts/tools-overview.md, advanced/media-generation.md, reference/config-reference.md)*