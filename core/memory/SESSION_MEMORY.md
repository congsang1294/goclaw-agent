# SESSION MEMORY

> **File:** `core/memory/SESSION_MEMORY.md`
> **Role:** Define the per-session memory lifecycle — create, update, summarize, delete
> **Part of:** Memory System
> **Phase:** 3 — Memory & Context

---

## 1. Mục đích

Session Memory lưu trạng thái của **phiên làm việc hiện tại**. Mỗi session = một ngày làm việc.
Session memory giúp Manager resume công việc nếu bị gián đoạn.

---

## 2. Storage

| Property | Value |
|----------|-------|
| **Directory** | `memory/sessions/` |
| **File pattern** | `session_YYYY-MM-DD.json` |
| **Format** | JSON |
| **Chunking** | 1 file per day. Nếu >1MB → archive và tạo file mới. |

---

## 3. Session File Format (Runtime)

```json
{
  "session": "2026-07-09",
  "sequence": 3,
  "plan_id": "plan_20260709_001",
  "plan_type": "simple",
  "tasks": [
    {
      "id": "task_20260709_001",
      "type": "skill_execution",
      "status": "done",
      "priority": "normal",
      "worker": "viet-bai-fb",
      "skill": "viet-bai-facebook",
      "input": { "topic": "giới thiệu tool" },
      "output": { "caption": "..." },
      "error": null,
      "attempts": 1,
      "max_retries": 3,
      "parent_task": null,
      "depends_on": [],
      "created_at": "2026-07-09T08:01:00+07:00",
      "updated_at": "2026-07-09T08:02:30+07:00",
      "assigned_at": "2026-07-09T08:01:00+07:00",
      "completed_at": "2026-07-09T08:02:30+07:00"
    }
  ]
}
```

**Fields:**
| Field | Type | Mô tả |
|-------|------|-------|
| `session` | string | Ngày session (YYYY-MM-DD) |
| `sequence` | int | Task ID counter (tăng dần) |
| `plan_id` | string | Plan ID hiện tại (hoặc null) |
| `plan_type` | string | `simple` | `multi_step` | `complex` |
| `tasks` | array | Array of task objects (xem TASK_SCHEMA.md) |

**Ghi chú:**
- `events` array không cần lưu trong session file — log event vào `task_history.log`
- `summary` tính từ tasks array khi cần (không lưu riêng)
- Task object dùng đúng TASK_SCHEMA.md — không dùng field viết tắt

---

## 4. Session Lifecycle (Runtime)

```
TURN START
  │
  ├── 1. Đọc file: memory/sessions/session_YYYY-MM-DD.json
  ├── 2. Nếu không có file → tạo mới: { session, sequence: 0, tasks: [] }
  │
  ▼
PROCESS (theo ORCHESTRATION.md flow)
  │
  ├── Task created → Kanban CREATE → tasks.push(task)
  ├── Task dispatched → UPDATE status + assigned_at
  ├── Task completed → UPDATE status + output + completed_at
  ├── Task failed → UPDATE status + error
  ├── Task unblocked → UPDATE status: blocked → todo
  │
  ▼
TURN END
  │
  ├── GHI file: ghi đè toàn bộ session file
  ├── LOG event: append 1 dòng JSON vào task_history.log
  │
  ▼
CHỜ TURN TIẾP THEO
```

**Không events array trong session file** — log event vào task_history.log.
**Không summary trong session file** — tính từ tasks nếu cần.

---

## 5. CRUD Operations (Runtime)

### CREATE — New Session
```json
{
  "session": "2026-07-09",
  "sequence": 0,
  "plan_id": null,
  "plan_type": null,
  "tasks": []
}
```
Tạo khi: đầu turn, không tìm thấy file session cho ngày hôm nay.

### READ — Load Session
```
if file exists:
    read file → parse JSON → { session, sequence, tasks }
    return tasks (active tasks for Kanban)
else:
    return empty Kanban: { tasks: [], sequence: 0 }
```

### UPDATE — Add Task (CREATE task)
```
1. task_id = task_{today}_{pad(++sequence, 3)}
2. Task object theo TASK_SCHEMA.md
3. tasks.push(task)
4. Save file
```

### UPDATE — Change Task Status
```
1. Find task by id in tasks array
2. Update fields: status, updated_at, (output|error), assigned_at/completed_at
3. Save file
```

### UPDATE — Delete Session (end of day)
```
1. Read current session
2. Write session_summary to task_history.log
3. Delete session file
```

---

## 6. Resume After Interruption

Khi session bị gián đoạn (crash, timeout, restart):

```
1. Kiểm tra memory/sessions/ có file session_*.json không
2. Nếu có:
   a. Đọc file session gần nhất
   b. Kiểm tra tasks: task nào IN_PROGRESS nhưng chưa có output?
   c. Những task đó → FAILED (vì worker đã mất context)
   d. Những task TODO → giữ nguyên
   e. Báo user: "Em bị gián đoạn. Các task đang chạy đã bị hủy."
3. Nếu không có:
   → Session mới bình thường
```

---

## 7. Session Cleanup

| Trigger | Action |
|---------|--------|
| Session end (normal) | Summarize + delete session file |
| Crash (unexpected) | Giữ session file. Resume xử lý cleanup. |
| Session file > 1MB | Archive tasks > 100 cũ nhất. Giữ 100 tasks gần nhất. |
| Midnight (UTC+7) | Session cũ tự động kết thúc khi session mới bắt đầu |

---

## 8. Liên kết

- **Memory Strategy:** `MEMORY_STRATEGY.md`
- **Task History:** `TASK_HISTORY.md`
- **Long-term Memory:** `LONG_TERM_MEMORY.md`
- **Context Assembler:** `core/context/CONTEXT_ASSEMBLER.md`
- **FRAMEWORK_SPEC.md:** §8.2 Session Memory
