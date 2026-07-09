# ORCHESTRATION

> **File:** `core/manager/ORCHESTRATION.md`
> **Role:** Define the Manager's runtime execution flow — turn-by-turn instructions
> **Part of:** Manager (Gà Trống Tre)
> **Phase:** 4 — Runtime Integration

---

## 1. Mục đích

Orchestration file này là **runtime executable** — Manager (Gà Trống Tre) đọc và làm theo **từng bước trên mỗi turn**.
Không phải tài liệu tham khảo. Đây là "main loop" của framework.

**Cơ chế hoạt động:** Mỗi lần Claude Code nhận tin nhắn Telegram → chạy flow này từ đầu.
Session file (`memory/sessions/session_YYYY-MM-DD.json`) lưu trạng thái Kanban để resume.

---

## 2. Turn-by-Turn Runtime Flow

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TURN START — Telegram message received
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 0: LOAD SESSION
  Đọc memory/sessions/session_{today}.json
  → Lấy danh sách active tasks (Kanban state)
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
  → Ghi tasks vào Kanban (STEP 7)

STEP 4: DISPATCH
  Đọc core/dispatcher/DISPATCHER.md
  → Đọc ROUTING_TABLE.yaml → worker + skill
  → Đọc WORKER_REGISTRY.yaml → worker metadata
  → Assemble context (CONTEXT_ASSEMBLER.md)
  → Assemble prompt (PROMPT_ASSEMBLY.md)
  → Gửi @workerId trong group chat
  → Update Kanban: task → IN_PROGRESS

STEP 5: PROCESS WORKER REPLY
  Đọc reply từ worker (tin nhắn group chat)
  → Parse status ở đầu câu: [done] | [failed] | [in_progress]
  → Nếu [done] → parse output JSON → update Kanban: task → DONE
  → Nếu [failed] → parse error → update Kanban: task → FAILED
  → Nếu [in_progress] → chờ (TURN END)

STEP 5a: UNLOCK DEPENDENCIES
  Nếu task vừa DONE:
    → Duyệt Kanban tìm task BLOCKED depends_on task này
    → Unblock: BLOCKED → TODO
    → Save session

STEP 5b: CHECK ALL DONE
  Nếu tất cả tasks trong plan đều DONE:
    → Đọc RESULT_AGGREGATOR.md → gom kết quả
    → Đọc RESPONSE_BUILDER.md → format → gửi Telegram
  Nếu có task FAILED → xử lý retry (STEP 6)

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
| `WORKER_FINISH` | Worker trả kết quả | `{ event, timestamp, task_id, worker, status, duration_ms }` |
| `RETRY` | Retry task | `{ event, timestamp, task_id, attempt, max_retries, error }` |
| `DONE` | Tất cả tasks hoàn thành | `{ event, timestamp, plan_id, task_count }` |
| `FAIL` | Task failed hết retry | `{ event, timestamp, task_id, worker, error, attempts }` |
| `CANCEL` | Task bị hủy | `{ event, timestamp, task_id, reason }` |
| `RESPOND` | Gửi response cho user | `{ event, timestamp, message_length }` |

### 5.3 Log Example

```json
{"event":"RECEIVE","timestamp":"2026-07-09T10:00:00+07:00","user":"anh Sáng","message":"viết bài Facebook giới thiệu tool"}
{"event":"PLAN","timestamp":"2026-07-09T10:00:01+07:00","plan_id":"plan_20260709_001","plan_type":"simple","task_count":1}
{"event":"DISPATCH","timestamp":"2026-07-09T10:00:02+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb","skill":"viet-bai-facebook","attempt":1}
{"event":"WORKER_START","timestamp":"2026-07-09T10:00:05+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb"}
{"event":"WORKER_FINISH","timestamp":"2026-07-09T10:00:30+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb","status":"done","duration_ms":25000}
{"event":"DONE","timestamp":"2026-07-09T10:00:31+07:00","plan_id":"plan_20260709_001","task_count":1}
{"event":"RESPOND","timestamp":"2026-07-09T10:00:32+07:00","message_length":450}
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
2. Kiểm tra Kanban có task IN_PROGRESS hoặc chờ duyệt không
3. Nếu có → cho phép worker tiếp tục
4. Nếu không → "không có gì để duyệt"
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
3. Liệt kê tasks đang active (todo, in_progress, blocked)
4. Định dạng status_report → gửi user
```

---

## 7. Error Handling

| Tình huống | Xử lý |
|-----------|--------|
| Task fail lần đầu | RETRY (STEP 6) |
| Task fail hết lượt retry | Log FAIL + báo user + hủy dependent tasks |
| Worker không phản hồi | Chờ timeout (theo route config) → fail |
| Mất kết nối Telegram | Log lỗi, chờ turn sau |
| Input thiếu thông tin | Hỏi user 1 câu, không suy diễn |
| Session file corrupt | Tạo session mới (backup file cũ) |
| Worker reply không parse được | Coi là in_progress, chờ reply khác |

---

## 8. Resume Flow (khi session gián đoạn)

Khi Claude Code khởi động lại (session mới nhưng Kanban còn task active):

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
