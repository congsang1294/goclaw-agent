# MEMORY STRATEGY

> **File:** `core/memory/MEMORY_STRATEGY.md`
> **Role:** Define the overall memory architecture — layers, read/write/delete rules
> **Part of:** Memory System
> **Phase:** 3 — Memory & Context

---

## 1. Mục đích

Memory Strategy định nghĩa **cách Framework quản lý dữ liệu xuyên suốt vòng đời**:
- Dữ liệu lưu ở đâu
- Khi nào đọc
- Khi nào ghi
- Khi nào xóa
- Khi nào tóm tắt

Framework có 4 memory layers, mỗi layer có mục đích và vòng đời riêng.

---

## 2. Four Memory Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE BASE (static)                      │
│  knowledge/*.md — brand voice, product info, business model     │
│  Đọc: mỗi session. Ghi: thủ công. Xóa: không bao giờ.          │
├─────────────────────────────────────────────────────────────────┤
│                      LONG-TERM MEMORY (persistent)               │
│  memory/long-term/*.log — completed tasks, decisions, milestones │
│  Đọc: khi planning, khi resume. Ghi: milestone, session end.    │
│  Xóa: không bao giờ (archive). Tóm tắt: hàng tuần.              │
├─────────────────────────────────────────────────────────────────┤
│                       SESSION MEMORY (per session)               │
│  memory/sessions/session_YYYY-MM-DD.json — current session data │
│  Đọc: session start. Ghi: task events. Xóa: session end.        │
│  Tóm tắt: session end → long-term.                              │
├─────────────────────────────────────────────────────────────────┤
│                      SHORT-TERM MEMORY (volatile)                │
│  GoClaw in-memory — current conversation turns                  │
│  Đọc: mỗi turn. Ghi: mỗi turn. Xóa: auto on turn end.          │
│  Tóm tắt: không bao giờ.                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer Details

### 3.1 Short-term Memory

| Property | Value |
|----------|-------|
| **Storage** | GoClaw internal (in-memory) |
| **Format** | Conversation context (GoClaw managed) |
| **Duration** | Per conversation turn |
| **Read** | Every turn — automatic via GoClaw |
| **Write** | Every turn — automatic via GoClaw |
| **Delete** | Auto on turn end |
| **Summarize** | Never |
| **Managed by** | GoClaw runtime — Framework không cần can thiệp |

**Framework usage:**
- Manager dùng short-term memory để nhớ user nói gì ở turn trước
- Worker dùng short-term memory để nhớ task context
- Không cần code đặc biệt — GoClaw tự quản lý

### 3.2 Session Memory

| Property | Value |
|----------|-------|
| **Storage** | `memory/sessions/session_YYYY-MM-DD.json` |
| **Format** | JSON — structured task + event log |
| **Duration** | Per session (one file per day) |
| **Read** | Session start (để resume) |
| **Write** | On task events (create, update, complete) |
| **Delete** | Session end (hoặc khi session file quá lớn >1MB) |
| **Summarize** | Session end → 1 entry in long-term |

**Session file format:**
```json
{
  "session_id": "2026-07-09",
  "started_at": "2026-07-09T08:00:00+07:00",
  "ended_at": null,
  "turn_count": 0,
  "tasks": [
    {
      "id": "task_20260709_001",
      "status": "done",
      "worker": "viet-bai-fb",
      "skill": "viet-bai-facebook",
      "input_summary": "viết bài giới thiệu tool",
      "output_summary": "caption 150 từ Hook+Body+CTA",
      "attempts": 1,
      "created_at": "2026-07-09T08:01:00+07:00",
      "completed_at": "2026-07-09T08:02:30+07:00"
    }
  ],
  "events": [
    {
      "type": "task_created",
      "task_id": "task_20260709_001",
      "timestamp": "2026-07-09T08:01:00+07:00"
    },
    {
      "type": "task_completed",
      "task_id": "task_20260709_001",
      "timestamp": "2026-07-09T08:02:30+07:00"
    }
  ],
  "summary": "3 turns, 2 tasks completed, 0 failed"
}
```

### 3.3 Long-term Memory

| Property | Value |
|----------|-------|
| **Storage** | `memory/long-term/task_history.log` |
| **Format** | Append-only text (JSON lines or structured markdown) |
| **Duration** | Persistent — không bao giờ xóa |
| **Read** | Before planning, on session resume |
| **Write** | On task complete, on milestone, on session end |
| **Delete** | Never (archive to `memory/archives/` when >5000 entries) |
| **Summarize** | Weekly or every 1000 entries |

**Long-term entry format:**
```json
{"type":"task","id":"task_20260709_001","worker":"viet-bai-fb","skill":"viet-bai-facebook","status":"done","duration_sec":90,"timestamp":"2026-07-09T08:02:30+07:00"}
{"type":"milestone","event":"order_success","detail":"PRO-19 - anh Minh - 15,000đ","timestamp":"2026-07-09T09:15:00+07:00"}
{"type":"session_summary","date":"2026-07-09","turns":5,"tasks_completed":2,"tasks_failed":0,"milestones":1,"timestamp":"2026-07-09T18:00:00+07:00"}
```

### 3.4 Knowledge Base

| Property | Value |
|----------|-------|
| **Storage** | `knowledge/brand-voice.md`, `knowledge/knowledge-base.md`, `knowledge/my-business.md` |
| **Format** | Markdown |
| **Duration** | Permanent |
| **Read** | Every session |
| **Write** | Manual edits (by anh Sáng or via Claude) |
| **Delete** | Never |
| **Summarize** | Never — đây là source of truth |

---

## 4. Read Rules

| When | What to Read | Source | How |
|------|-------------|--------|-----|
| Session start | Yesterday's session (if exists) | `memory/sessions/session_YYYY-MM-DD.json` | Read most recent file |
| Session start | Long-term summary | `memory/long-term/task_history.log` | Read last 20 lines |
| Before planning | Active tasks | `memory/sessions/session_*.json` | Filter status != done/cancelled |
| Before planning | Worker performance history | `memory/long-term/task_history.log` | grep by worker_id |
| Task dispatch | Worker context | `core/worker/WORKER_REGISTRY.yaml` | Read specific entry |
| Response | Session context | In-memory | Current conversation |
| Heartbeat | N/A | N/A | Signal only, no memory read |

---

## 5. Write Rules

| When | What to Write | Target | Format |
|------|-------------|--------|--------|
| Task created | Append task to session | `memory/sessions/session_*.json` | JSON |
| Task status changed | Update task in session | `memory/sessions/session_*.json` | JSON |
| Task completed | Append to task history | `memory/long-term/task_history.log` | JSON line |
| Worker done | Log output summary + duration | `memory/long-term/task_history.log` | JSON line |
| Error/failure | Log error + retry attempts | `memory/long-term/task_history.log` | JSON line |
| Session end | Summarize session → long-term | `memory/long-term/task_history.log` | Summary entry |
| Milestone (order) | Log immediately | `memory/long-term/task_history.log` | Milestone entry |
| Milestone (lead) | Log immediately | `memory/long-term/task_history.log` | Milestone entry |

---

## 6. Delete & Archive Rules

| Trigger | Action | Detail |
|---------|--------|--------|
| Turn end | Auto-delete short-term | GoClaw tự quản lý |
| Session end | Delete session file | Framework xóa file sau khi đã summarize |
| Session file > 1MB | Archive + truncate | Giữ 100 tasks gần nhất, archive phần còn lại |
| Task history > 5000 entries | Archive oldest 4000 | `memory/archives/task_history_YYYYMMDD.log` |
| Weekly (triggered) | Rotate archives | Nén archives cũ hơn 30 ngày |
| Knowledge Base | Never | Manual edits only |

---

## 7. Summarize Rules

| Trigger | Action | Output Format |
|---------|--------|--------------|
| Session end | Compress session → 1 summary entry | JSON line in long-term (type: session_summary) |
| Every 1000 entries | Compress oldest 500 → 1 summary | "From task_XXX to task_YYY: X done, Y failed, Z retried" |
| Weekly | Archive old history | Tar.gz to `memory/archives/` |

---

## 8. Initialization

Khi session bắt đầu:

```
1. Check if memory/sessions/ exists → create if not
2. Check if memory/long-term/ exists → create if not
3. Load most recent session file (if any) → resume context
4. Load last 20 lines of task_history.log → recent activity
5. If resume from crash: check for uncompleted tasks
```

---

## 9. Liên kết

- **Task History:** `TASK_HISTORY.md` — format chi tiết cho task log
- **Session Memory:** `SESSION_MEMORY.md` — session lifecycle
- **Long-term Memory:** `LONG_TERM_MEMORY.md` — archive + summarize
- **Context Assembler:** `core/context/CONTEXT_ASSEMBLER.md` — memory → context
- **FRAMEWORK_SPEC.md:** §8 Memory System
