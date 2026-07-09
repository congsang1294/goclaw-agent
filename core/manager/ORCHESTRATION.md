# ORCHESTRATION

> **File:** `core/manager/ORCHESTRATION.md`
> **Role:** Define the Manager's runtime execution flow — turn-by-turn instructions
> **Part of:** Manager (Gà Trống Tre)
> **Phase:** 4 — Runtime Integration

---

## 1. Mục đích

Orchestration file này là **runtime executable** — Manager (Gà Trống Tre) đọc và làm theo **từng bước trên mỗi turn**.
Không phải tài liệu tham khảo. Đây là "main loop" của framework.

**Cơ chế hoạt động:** Mỗi lần GoClaw agent runtime nhận tin nhắn Telegram → chạy flow này từ đầu.
Trong GoClaw Telegram runtime, `team_tasks` là Kanban thật. Session file (`memory/sessions/session_YYYY-MM-DD.json`) chỉ lưu cache/resume phụ khi tool không khả dụng.

## 0. Telegram Runtime Hard Rules

1. Mọi workflow team phải gọi `team_tasks` tạo task trước khi delegate worker.
2. Mọi progress phải đi qua `team_tasks` (`progress_percent`, `progress_step`), rồi mới báo text.
3. Mọi output xong phải được lưu vào `team_tasks.result` và gửi ngay về Telegram.
4. SLA 5 phút là mốc báo trễ: caption tính từ lúc anh duyệt ý tưởng; image/video tính từ lúc caption DONE. Quá hạn thì báo worker nào trễ, % nào, đang ở bước nào, rồi tiếp tục chạy/retry.
5. Nếu không gọi được `team_tasks`, phải báo lỗi Kanban cho anh Sáng, không được tự nhận complete.

---

## 2. Turn-by-Turn Runtime Flow

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TURN START — Telegram message received
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 0: LOAD SESSION
  Đọc memory/sessions/session_{today}.json
  → Lấy danh sách active tasks bằng `team_tasks` nếu tool khả dụng
  → Lấy task sequence counter
  → Nếu file không tồn tại → tạo mới

STEP 1: ANALYZE INTENT
  Đọc core/manager/INTENT_ANALYZER.md
  → Parse user message → { intent, confidence, params }
  → Nếu unknown → hỏi clarification → TURN END
  → Nếu approve/cancel/check_status → xử lý system intent → TURN END

STEP 2: CHECK EXISTING TASKS
  Nếu Kanban có task IN_PROGRESS:
    → Worker đã trả lời chưa? Nếu có → xử lý kết quả (STEP 5)
    → Nếu chưa → chờ (TURN END)
  Nếu Kanban có task TODO:
    → Dispatch task tiếp theo (STEP 4)
  Nếu Kanban có task FAILED:
    → Xử lý retry (STEP 6)
  Nếu không có task nào → tạo plan mới (STEP 3)

STEP 3: CREATE PLAN
  Đọc core/manager/PLANNER.md
  → Dùng intent → sinh 1 hoặc nhiều tasks
  → Mỗi task theo TASK_SCHEMA.md
  → Gọi `team_tasks` tạo tasks (STEP 7)
  Với `team_sync`:
    → Tạo `campaign_id`
    → Tạo task ideas đầu tiên cho `viet-bai-fb`
    → Tạo sẵn các task caption/image/video/final_approval/publish_fanpage ở trạng thái BLOCKED
    → caption chờ anh Sáng duyệt ideas; image/video chờ caption thật

STEP 4: DISPATCH
  Đọc core/dispatcher/DISPATCHER.md
  → Đọc ROUTING_TABLE.yaml → worker + skill
  → Đọc WORKER_REGISTRY.yaml → worker metadata
  → Assemble context (CONTEXT_ASSEMBLER.md)
  → Assemble prompt (PROMPT_ASSEMBLY.md)
  → Gửi @workerId trong group chat
  → Gọi `team_tasks` update task → IN_PROGRESS

STEP 5: PROCESS WORKER REPLY
  Đọc reply từ worker (tin nhắn group chat)
  → Parse status ở đầu câu: [done] | [failed] | [in_progress]
  → Nếu [in_progress] → parse progress_percent/progress_note → gọi `team_tasks` update progress, log WORKER_PROGRESS
  → Nếu [done] → parse output JSON → validate artifact bắt buộc → nếu hợp lệ mới gọi `team_tasks` completed
  → Nếu [failed] → parse error → gọi `team_tasks` failed
  → Nếu task ideas DONE → gửi 3 ý tưởng cho anh Sáng và tạo/chuyển approval ý tưởng sang IN_PROGRESS
  → Nếu task caption DONE → gửi bài viết ngay cho anh Sáng, rồi mới mở image/video
  → Nếu task image/video DONE → gửi artifact đó ngay cho anh Sáng, cập nhật delivery.sent
  → Nếu task publish_fanpage DONE → gửi link Fanpage/Reels về Telegram và log DONE

STEP 5a: UNLOCK DEPENDENCIES
  Nếu task vừa DONE:
    → Duyệt Kanban tìm task BLOCKED depends_on task này
    → Unblock: BLOCKED → TODO
    → Save session
  Riêng team_sync:
    → Không unblock caption/image/video chỉ vì ideas task done
    → Chỉ unblock caption khi anh Sáng đã approve một `chosen_idea`
    → Chỉ unblock image/video khi caption DONE và có bài viết thật
    → Sau khi đủ content + image + video delivered, unblock final_approval
    → Sau khi final_approval done, unblock publish_fanpage

STEP 5b: CHECK ALL DONE
  Nếu output caption/image/video nào vừa DONE:
    → Đọc RESPONSE_BUILDER.md → gửi output đó ngay cho anh Sáng
    → Không chờ đủ bộ mới gửi
  Nếu đủ content + image + video đều DONE và delivered:
    → Đọc RESULT_AGGREGATOR.md → gom kết quả
    → Đọc RESPONSE_BUILDER.md → format bản tổng hợp cuối
    → Hỏi anh Sáng duyệt đăng
    → Log APPROVAL_PENDING stage=final
  Nếu có task FAILED → xử lý retry (STEP 6)

STEP 5c: DELIVER RESULT TO TELEGRAM
  Chỉ chạy khi worker outputs đã hợp lệ và aggregator đã có đủ artifact bắt buộc.
  → Gửi caption/text trước nếu có
  → Gửi ảnh bằng file local nếu có; nếu không có file thì gửi image_url
  → Gửi video_preview/video_url nếu có
  → Sau mỗi lần gửi thành công: cập nhật task.delivery.sent
  → Khi artifact nào gửi thành công: task.delivery.status = "sent", delivered_at = now
  → Chỉ log DONE cho workflow sau khi đã publish hoặc sau khi workflow không có bước publish
  → Nếu gửi Telegram lỗi: task.delivery.status = "failed", lưu error, KHÔNG báo complete

STEP 5d: APPROVAL + PUBLISH
  Khi anh Sáng approve ideas:
    → Lưu chosen_idea vào session
    → Set approval ideas task DONE
    → Chỉ unblock caption
    → Dispatch task TODO kế tiếp theo Dispatcher
  Khi caption DONE:
    → Gửi bài viết cho anh Sáng ngay
    → Unblock image trước; video chờ caption + ảnh nếu cần reference
  Khi anh Sáng approve final:
    → Set final_approval DONE
    → Unblock publish_fanpage
    → Gọi skill/script đăng Fanpage/Reels bằng artifact đã duyệt
    → Publish xong: log PUBLISHED, gửi link về Telegram, workflow DONE

STEP 6: RETRY
  Đọc core/retry/RETRY_POLICY.md
  → Kiểm tra retryable + attempts < max_retries?
    YES → Kanban: FAILED → RETRYING → TODO → dispatch lại
    NO  → Kanban: giữ FAILED → báo user → hủy workflow nếu cần

STEP 7: SAVE SESSION
  Ghi Kanban state vào memory/sessions/session_{today}.json
  → tasks array (đầy đủ fields)
  → sequence counter
  → session metadata

STEP 8: LOG
  Ghi event vào memory/long-term/task_history.log
  → Mỗi event 1 dòng JSON
  → Bao gồm: timestamp, event_type, task_id, worker, status, message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TURN END — Chờ tin nhắn tiếp theo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 3. Session File Management

### 3.1 Read Session

Mở đầu mỗi turn, đọc session file:

```json
{
  "session": "2026-07-09",
  "sequence": 5,
  "tasks": [
    {
      "id": "task_20260709_001",
      "type": "skill_execution",
      "status": "done",
      "worker": "viet-bai-fb",
      "skill": "viet-bai-facebook",
      "input": { "topic": "giới thiệu tool" },
      "output": { "caption": "..." },
      "error": null,
      "attempts": 1,
      "max_retries": 3,
      "depends_on": [],
      "created_at": "2026-07-09T10:00:00+07:00",
      "updated_at": "2026-07-09T10:05:00+07:00",
      "assigned_at": "2026-07-09T10:00:00+07:00",
      "completed_at": "2026-07-09T10:05:00+07:00"
    }
  ],
  "plan_id": "plan_20260709_001",
  "plan_type": "simple"
}
```

### 3.2 Write Session

Sau mỗi thay đổi task status, ghi lại toàn bộ file.

**Chú ý:** JSON phải hợp lệ. Không comment, không trailing commas.
Ghi đè toàn bộ file (không append) — file nhỏ, thao tác đơn giản.

### 3.3 Session Path

```
memory/sessions/session_2026-07-09.json
```

Dùng múi giờ Asia/Saigon (UTC+7). Nếu chưa có file → tạo file mới với sequence = 0, tasks = [].

---

## 4. Task Sequence Counter

```
task_{YYYYMMDD}_{NNN}
```

- `NNN`: bắt đầu từ 001, tăng dần
- Reset về 001 mỗi ngày (file session mới)
- Lưu trong session file: `sequence` field

**Cách dùng:**
1. Đọc `session.sequence` từ file
2. Task mới = `task_{today}_{pad(sequence+1, 3)}`
3. Tăng `session.sequence` lên 1
4. Ghi lại file

---

## 5. Logging Specification

### 5.1 Log File

```
memory/long-term/task_history.log
```

Format: **mỗi dòng là 1 JSON object**, append vào cuối file.

### 5.2 Log Event Types

| Event Type | Khi nào | Fields |
|-----------|---------|--------|
| `RECEIVE` | Nhận tin nhắn user | `{ event, timestamp, user, message }` |
| `PLAN` | Tạo plan | `{ event, timestamp, plan_id, plan_type, task_count }` |
| `DISPATCH` | Gửi task đến worker | `{ event, timestamp, task_id, worker, skill, attempt }` |
| `WORKER_START` | Worker xác nhận nhận task | `{ event, timestamp, task_id, worker }` |
| `WORKER_PROGRESS` | Worker cập nhật tiến độ | `{ event, timestamp, task_id, worker, progress_percent, progress_note }` |
| `WORKER_FINISH` | Worker trả kết quả | `{ event, timestamp, task_id, worker, status, duration_ms }` |
| `RETRY` | Retry task | `{ event, timestamp, task_id, attempt, max_retries, error }` |
| `DONE` | Tất cả tasks hoàn thành, đã gửi đủ artifact, và đã publish nếu có bước đăng | `{ event, timestamp, plan_id, task_count }` |
| `FAIL` | Task failed hết retry | `{ event, timestamp, task_id, worker, error, attempts }` |
| `CANCEL` | Task bị hủy | `{ event, timestamp, task_id, reason }` |
| `RESPOND` | Gửi response cho user | `{ event, timestamp, message_length }` |
| `DELIVERED` | Gửi đủ artifact về Telegram | `{ event, timestamp, plan_id, sent, telegram_message_ids }` |
| `APPROVAL_PENDING` | Chờ anh Sáng duyệt | `{ event, timestamp, plan_id, stage }` |
| `APPROVED` | Anh Sáng đã duyệt | `{ event, timestamp, plan_id, stage, approved_by }` |
| `PUBLISHED` | Đã đăng Fanpage/Reels | `{ event, timestamp, plan_id, facebook_urls }` |

### 5.3 Log Example

```json
{"event":"RECEIVE","timestamp":"2026-07-09T10:00:00+07:00","user":"anh Sáng","message":"viết bài Facebook giới thiệu tool"}
{"event":"PLAN","timestamp":"2026-07-09T10:00:01+07:00","plan_id":"plan_20260709_001","plan_type":"simple","task_count":1}
{"event":"DISPATCH","timestamp":"2026-07-09T10:00:02+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb","skill":"viet-bai-facebook","attempt":1}
{"event":"WORKER_START","timestamp":"2026-07-09T10:00:05+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb"}
{"event":"WORKER_FINISH","timestamp":"2026-07-09T10:00:30+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb","status":"done","duration_ms":25000}
{"event":"DELIVERED","timestamp":"2026-07-09T10:00:31+07:00","plan_id":"plan_20260709_001","sent":["caption"],"telegram_message_ids":["12345"]}
{"event":"DONE","timestamp":"2026-07-09T10:00:32+07:00","plan_id":"plan_20260709_001","task_count":1}
{"event":"RESPOND","timestamp":"2026-07-09T10:00:33+07:00","message_length":450}
```

### 5.4 Append Log

Luôn dùng append, không ghi đè. Mỗi dòng một JSON object.

```json
{"event":"RECEIVE","timestamp":"...","user":"...","message":"..."}
```

---

## 6. Branching Conditions

### 6.1 Khi user gửi "approve" (OK, duyệt, đăng đi)

```
1. Intent = approve
2. Kiểm tra approval task đang in_progress:
   a. stage = "ideas" → parse số ý tưởng anh chọn, lưu chosen_idea, log APPROVED, chỉ unblock caption
   b. stage = "final" → log APPROVED, unblock publish_fanpage, tự động đăng Fanpage/Reels
3. Nếu không có approval task → "không có gì để duyệt"
```

### 6.2 Khi user gửi "cancel" (hủy, stop, dừng)

```
1. Intent = cancel
2. Tìm task IN_PROGRESS gần nhất
3. Update Kanban: task → CANCELLED
4. Cancel luôn task depends_on (cascade)
5. Log: CANCEL
6. Báo user
```

### 6.3 Khi user gửi "check_status" (kiểm tra, tiến độ)

```
1. Intent = check_status
2. Đọc Kanban từ session file
3. Liệt kê tasks đang active (todo, in_progress, blocked), kèm worker, progress_percent, progress_note, deadline_at
4. Định dạng status_report → gửi user:
   - Cây Bút: đang làm gì, bao nhiêu %
   - Tạo Ảnh: đang làm gì, bao nhiêu %
   - Làm Video: đang làm gì, bao nhiêu %
   - Output nào đã gửi
   - Còn bao lâu tới deadline 5 phút
```

---

## 7. Error Handling

| Tình huống | Xử lý |
|-----------|--------|
| Task fail lần đầu | RETRY (STEP 6) |
| Task fail hết lượt retry | Log FAIL + báo user + hủy dependent tasks |
| Worker không phản hồi | Chờ timeout (theo route config) → fail |
| Task quá deadline 5 phút | Báo anh Sáng worker nào trễ, progress hiện tại, tiếp tục retry hoặc xin thêm thời gian |
| Mất kết nối Telegram | Log lỗi, chờ turn sau |
| Worker báo done nhưng thiếu artifact bắt buộc | Không update DONE; giữ `in_progress`, hỏi worker gửi lại đúng output |
| Gửi Telegram lỗi hoặc thiếu message id | `delivery.status = failed`; không log DONE, báo lỗi kỹ thuật cho anh Sáng |
| Input thiếu thông tin | Hỏi user 1 câu, không suy diễn |
| Session file corrupt | Tạo session mới (backup file cũ) |
| Worker reply không parse được | Coi là in_progress, chờ reply khác |

---

## 8. Resume Flow (khi session gián đoạn)

Khi GoClaw agent runtime khởi động lại (session mới nhưng Kanban còn task active):

```
1. Đọc session file mới nhất (memory/sessions/)
2. Kiểm tra tasks chưa hoàn thành (in_progress, todo, blocked)
3. Nếu có task IN_PROGRESS:
   → Hỏi user: "Đang còn task [id] dang dở. Anh muốn tiếp tục không?"
   → User OK → dispatch lại task
4. Nếu không → bắt đầu flow mới
```

---

## 9. Liên kết

- **Runtime flow:** file này (ORCHESTRATION.md)
- **Intent:** `INTENT_ANALYZER.md`
- **Plan:** `PLANNER.md`
- **Kanban:** `core/kanban/KANBAN_BOARD.md`
- **Dispatch:** `core/dispatcher/DISPATCHER.md`
- **Retry:** `core/retry/RETRY_POLICY.md`
- **Aggregate:** `RESULT_AGGREGATOR.md`
- **Response:** `RESPONSE_BUILDER.md`
- **Context:** `core/context/CONTEXT_ASSEMBLER.md`, `PROMPT_ASSEMBLY.md`
- **Routing:** `core/router/ROUTING_TABLE.yaml`
- **Worker:** `core/worker/WORKER_REGISTRY.yaml`
- **Session:** `core/memory/SESSION_MEMORY.md`
- **Log:** `memory/long-term/task_history.log`
