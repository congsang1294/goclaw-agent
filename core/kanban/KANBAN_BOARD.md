# KANBAN BOARD

> **File:** `core/kanban/KANBAN_BOARD.md`
> **Role:** Runtime Kanban contract for `team_tasks`
> **Part of:** Kanban / Task System
> **Phase:** 4 — Runtime Integration

---

## 1. Mục đích

Kanban Board là **runtime data layer** cho tất cả tasks.
Trong GoClaw Telegram runtime, Kanban thật là tool/bảng `team_tasks`.
File session chỉ là cache phụ khi tool không khả dụng; không được dùng file local thay cho `team_tasks` nếu runtime đã expose tool này.

## 0. GoClaw Runtime Rule

- Tạo task: gọi `team_tasks` trước khi delegate/mention worker.
- Cập nhật progress: gọi `team_tasks` với `status=in_progress`, `progress_percent`, `progress_step`.
- Hoàn thành: gọi `team_tasks` với `status=completed`, `progress_percent=100`, `result` chứa output thật.
- Nhắc quá hạn 5 phút: set `followup_at`, `followup_message`, `followup_channel`, `followup_chat_id` nếu tool schema hỗ trợ.
- Nếu `team_tasks` lỗi: báo anh Sáng ngay "Kanban tool chưa cập nhật được"; không báo complete giả.
- Chỉ dùng file/session memory làm cache phụ hoặc fallback; trạng thái hiển thị cho anh Sáng phải nằm trong `team_tasks`.

---

## 2. File Operations

### 2.1 READ — Đọc Kanban state

```json
// Đọc từ: memory/sessions/session_{today}.json
// Nếu không có file → khởi tạo Kanban rỗng

{
  "session": "2026-07-09",
  "sequence": 0,
  "plan_id": null,
  "plan_type": null,
  "tasks": []
}
```

**Cách đọc:**
1. Xác định today = ngày hiện tại (Asia/Saigon, UTC+7)
2. Đọc file `memory/sessions/session_{today}.json`
3. Nếu file không tồn tại → dùng Kanban rỗng (sequence=0, tasks=[])
4. Parse JSON → lấy tasks array

### 2.2 WRITE — Ghi Kanban state

```json
// Ghi đè toàn bộ file sau mỗi thay đổi
// JSON hợp lệ, không comment, không trailing commas
```

**Cách ghi:**
1. Cập nhật Kanban object trong memory
2. Serialize thành JSON (không format, hoặc 2-space indent)
3. Ghi đè file session
4. Nếu lỗi ghi → log lỗi, không crash

### 2.3 CREATE — Tạo task mới

```
Input: { worker, skill, input, depends_on, type }

Steps:
1. Đọc Kanban từ file
2. Tạo task ID: task_{YYYYMMDD}_{pad(sequence+1, 3)}
3. Tăng sequence lên 1
4. Tạo task object đúng TASK_SCHEMA.md:
   {
     "id": "task_20260709_001",
     "type": "skill_execution",
     "status": "todo",                         // depends_on rỗng
     // hoặc
     "status": "blocked",                      // depends_on không rỗng
     "priority": "normal",
     "campaign_id": "campaign_20260709_001",
     "stage": "ideas",
     "worker": "viet-bai-fb",
     "skill": "viet-bai-facebook",
     "input": { "topic": "..." },
     "output": null,
     "error": null,
     "delivery": {
       "status": "not_ready",
       "required": [],
       "sent": [],
       "telegram_message_id": null,
       "delivered_at": null,
       "error": null
     },
     "progress_percent": 0,
     "progress_note": null,
     "attempts": 0,
     "max_retries": 3,
     "parent_task": null,
     "depends_on": [],
     "created_at": "2026-07-09T10:00:00+07:00",
     "updated_at": "2026-07-09T10:00:00+07:00",
     "assigned_at": null,
     "deadline_at": null,
     "completed_at": null
   }
5. Thêm vào tasks array
6. GHI file
7. Log event: PLAN
```

### 2.4 UPDATE STATUS — Cập nhật trạng thái task

```
Input: task_id, new_status, additional_fields

Steps:
1. Đọc Kanban từ file
2. Tìm task theo id trong tasks array
3. Cập nhật status thành new_status
4. Cập nhật updated_at = now
5. Nếu additional_fields (output, error, progress_percent, progress_note, delivery, deadline_at) → cập nhật
6. Nếu status = in_progress → set assigned_at = now
7. Nếu status = done/failed → set completed_at = now
8. Nếu status = done → validate output và set delivery.status = "ready"
9. Sau khi gửi Telegram đủ artifact → set delivery.status = "sent", delivery.delivered_at = now
8. GHI file
```

**Status transition matrix:**

| Hành động | Từ status | Đến status | Cập nhật thêm |
|-----------|----------|------------|---------------|
| Enqueue | created | todo | — |
| Enqueue có dep | created | blocked | — |
| Dispatch | todo | in_progress | assigned_at = now |
| Progress update | in_progress | in_progress | progress_percent, progress_note, updated_at |
| Worker hoàn thành | in_progress | done | output, completed_at = now |
| Worker lỗi | in_progress | failed | error, attempts += 1 |
| Output sẵn sàng gửi | done | done | delivery.status = ready, delivery.required = [...] |
| Đã gửi Telegram đủ artifact | done | done | delivery.status = sent, delivery.sent, delivered_at |
| Gửi Telegram lỗi | done | done | delivery.status = failed, delivery.error |
| Retry — còn lượt | failed | retrying | — |
| Retry — dispatch lại | retrying | in_progress | assigned_at = now |
| Retry — hết lượt | retrying | failed | — |
| Unblock | blocked | todo | — |
| Cancel | bất kỳ (trừ done) | cancelled | — |
| Cascade cancel | blocked | cancelled | — |

### 2.5 DELETE — Xóa task (hiếm khi dùng)

Chỉ xóa task khi:
- Task được tạo nhầm (created nhưng chưa enqueue)
- Cleanup session đầu ngày mới

```
1. Tìm task trong tasks array
2. Xóa khỏi array
3. GHI file
```

### 2.6 FIND — Tìm task

```
Các truy vấn:
- Tìm task theo id: task.id === target_id
- Tìm tasks theo worker: task.worker === worker_id
- Tìm tasks theo status: task.status === target_status
- Tìm tasks theo plan: Tất cả tasks trong session
- Tìm task TODO đầu tiên: tasks.find(t => t.status === "todo")
- Tìm task IN_PROGRESS: tasks.filter(t => t.status === "in_progress")
- Kiểm tra all DONE: tasks.every(t => t.status === "done" || t.status === "cancelled")
- Kiểm tra all DELIVERED: tasks.every(t => t.status !== "done" || t.delivery?.status === "sent" || t.type === "internal")
- Tìm task FAILED retryable: tasks.find(t => t.status === "failed" && t.attempts < t.max_retries)
```

---

## 3. Kanban Queries (cho Manager)

| Câu hỏi | Logic |
|---------|-------|
| "Task nào đang chạy?" | `tasks.filter(t => t.status === 'in_progress')` |
| "Có task chờ không?" | `tasks.filter(t => t.status === 'todo')` |
| "Task [id] tới đâu rồi?" | `tasks.find(t => t.id === id)?.status` |
| "All tasks done?" | `tasks.every(t => ['done','cancelled'].includes(t.status))` |
| "Đã gửi đủ kết quả về Telegram?" | `tasks.every(t => t.status !== 'done' || t.delivery?.status === 'sent')` |
| "Tiến độ từng worker?" | `tasks.filter(t => ['todo','in_progress','blocked'].includes(t.status)).map(t => [t.worker, t.stage, t.progress_percent, t.progress_note])` |
| "Task nào quá deadline?" | `tasks.filter(t => t.deadline_at && now > t.deadline_at && t.status !== 'done')` |
| "Có task nào lỗi?" | `tasks.filter(t => t.status === 'failed')` |
| "Task nào chờ dependency?" | `tasks.filter(t => t.status === 'blocked')` |
| "Task TODO đầu tiên?" | `tasks.find(t => t.status === 'todo')` |

---

## 4. Board Layout (tham khảo)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        KANBAN BOARD                                  │
│  Session: 2026-07-09 | Tasks: 3 | Plan: plan_20260709_001          │
├────────────┬────────────┬────────────┬────────────┬──────────────────┤
│   TODO     │  BLOCKED   │IN_PROGRESS │   DONE     │     FAILED       │
├────────────┼────────────┼────────────┼────────────┼──────────────────┤
│ task_003   │ —          │ task_001   │ —          │ —                │
├────────────┴────────────┴────────────┴────────────┴──────────────────┤
│  Legend: ✅ DONE  🔄 IN_PROGRESS  ⏳ TODO  🚫 BLOCKED  ❌ FAILED    │
└─────────────────────────────────────────────────────────────────────┘
```

Board layout chỉ là visual reference. Dữ liệu thật ở session file.

---

## 5. Task ID Generation

```
Công thức: task_{YYYYMMDD}_{NNN}

NNN = pad(session.sequence + 1, 3)
Ví dụ: session.sequence = 0 → task_20260709_001
       session.sequence = 1 → task_20260709_002
```

**Rules:**
- `NNN` = 3 digits, zero-padded, reset về 001 mỗi ngày
- Dùng `session.sequence` từ file (không đếm tasks array)
- Luôn tăng sequence sau khi tạo task

---

## 6. Plan ID Generation

```
Công thức: plan_{YYYYMMDD}_{NNN}

NNN = số thứ tự plan trong ngày (bắt đầu từ 001)
```

---

## 7. Liên kết

- **Session file:** `core/memory/SESSION_MEMORY.md`
- **Task schema:** `TASK_SCHEMA.md`
- **Task lifecycle:** `TASK_LIFECYCLE.md`
- **Orchestration:** `core/manager/ORCHESTRATION.md`
- **Dispatcher:** `core/dispatcher/DISPATCHER.md`
- **Retry:** `core/retry/RETRY_POLICY.md`
- **Log:** `memory/long-term/task_history.log`
