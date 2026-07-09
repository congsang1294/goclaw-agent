# TASK HISTORY

> **File:** `core/memory/TASK_HISTORY.md`
> **Role:** Define format and rules for task execution history log
> **Part of:** Memory System
> **Phase:** 3 — Memory & Context

---

## 1. Mục đích

Task History là **nhật ký thực thi** của tất cả Tasks. Nó lưu:
- Task nào đã chạy
- Worker nào đã xử lý
- Kết quả thế nào (done/failed)
- Bao lâu (duration)
- Lỗi gì nếu failed

Dữ liệu này dùng để:
- Debug khi có lỗi
- Học từ lịch sử (task nào hay fail)
- Resume session sau crash
- Báo cáo hiệu năng worker

---

## 2. Storage

| Property | Value |
|----------|-------|
| **File** | `memory/long-term/task_history.log` |
| **Format** | JSON Lines (1 JSON object per line) |
| **Access** | Append-only (write), tail + grep (read) |
| **Encoding** | UTF-8 |

---

## 3. Entry Types

### 3.1 Event Entry (Runtime Log — format mới, khuyên dùng)

Ghi mỗi event quan trọng trong vòng đời task. 1 event = 1 dòng JSON.

```json
{"event":"RECEIVE","timestamp":"2026-07-09T10:00:00+07:00","user":"anh Sáng","message":"viết bài Facebook giới thiệu tool"}
{"event":"PLAN","timestamp":"2026-07-09T10:00:01+07:00","plan_id":"plan_20260709_001","plan_type":"simple","task_count":1}
{"event":"DISPATCH","timestamp":"2026-07-09T10:00:02+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb","skill":"viet-bai-facebook","attempt":1}
{"event":"WORKER_START","timestamp":"2026-07-09T10:00:05+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb"}
{"event":"WORKER_FINISH","timestamp":"2026-07-09T10:00:30+07:00","task_id":"task_20260709_001","worker":"viet-bai-fb","status":"done","duration_ms":25000}
{"event":"RETRY","timestamp":"2026-07-09T10:01:00+07:00","task_id":"task_20260709_001","attempt":2,"max_retries":3,"error":"API timeout"}
{"event":"DONE","timestamp":"2026-07-09T10:02:00+07:00","plan_id":"plan_20260709_001","task_count":1}
{"event":"FAIL","timestamp":"2026-07-09T10:03:00+07:00","task_id":"task_20260709_002","worker":"tao-anh","error":"OpenAI API: rate limit","attempts":3}
{"event":"CANCEL","timestamp":"2026-07-09T10:04:00+07:00","task_id":"task_20260709_002","reason":"user cancelled"}
{"event":"RESPOND","timestamp":"2026-07-09T10:05:00+07:00","message_length":450}
```

**Event types:**

| Event | Khi nào | Required Fields |
|-------|---------|----------------|
| `RECEIVE` | Nhận tin nhắn user | user, message |
| `PLAN` | Tạo plan | plan_id, plan_type, task_count |
| `DISPATCH` | Gửi task đến worker | task_id, worker, skill, attempt |
| `WORKER_START` | Worker xác nhận | task_id, worker |
| `WORKER_FINISH` | Worker trả kết quả | task_id, worker, status, duration_ms |
| `RETRY` | Retry task | task_id, attempt, max_retries, error |
| `DONE` | All tasks complete | plan_id, task_count |
| `FAIL` | Task hết retry | task_id, worker, error, attempts |
| `CANCEL` | Task bị hủy | task_id, reason |
| `RESPOND` | Gửi response | message_length |

### 3.2 Task Entry (legacy format — tương thích ngược)

```json
{"type":"task","id":"task_20260709_001","worker":"viet-bai-fb","skill":"viet-bai-facebook","status":"done","attempts":1,"max_retries":3,"duration_sec":90,"input_summary":"viết bài giới thiệu tool","output_summary":"caption 150 từ Hook+Body+CTA","error":null,"timestamp":"2026-07-09T08:02:30+07:00"}
```

| Field | Type | Mô tả |
|-------|------|-------|
| `type` | `"task"` | Entry type |
| `id` | string | Task ID |
| `worker` | string | Worker ID |
| `skill` | string | Skill name |
| `status` | `"done"` | `"failed"` | `"cancelled"` | Final status |
| `attempts` | int | Số lần thử (kể cả retry) |
| `max_retries` | int | Max retry allowed |
| `duration_sec` | int | Thời gian từ dispatch đến done |
| `input_summary` | string | Tóm tắt input (không lưu toàn bộ) |
| `output_summary` | string | Tóm tắt output |
| `error` | string | null | Error message nếu failed |
| `timestamp` | datetime | Hoàn thành (Asia/Saigon) |

### 3.2 Session Summary Entry (khi session kết thúc)

```json
{"type":"session_summary","date":"2026-07-09","turns":5,"tasks_completed":2,"tasks_failed":0,"tasks_cancelled":0,"milestones":1,"first_task":"task_20260709_001","last_task":"task_20260709_002","duration_min":45,"timestamp":"2026-07-09T18:00:00+07:00"}
```

### 3.3 Milestone Entry (sự kiện business quan trọng)

```json
{"type":"milestone","event":"order_success","detail":"PRO-19 - anh Minh - 15,000đ","timestamp":"2026-07-09T09:15:00+07:00"}
{"type":"milestone","event":"new_lead","detail":"Chị Hà - 0903... - ha@gmail.com","timestamp":"2026-07-09T10:30:00+07:00"}
{"type":"milestone","event":"deploy","detail":"Updated Pro price to 5,000đ","timestamp":"2026-07-09T14:00:00+07:00"}
```

### 3.4 Error Entry (lỗi hệ thống)

```json
{"type":"error","task_id":"task_20260709_003","worker":"tao-anh","error":"OpenAI API: rate limit exceeded","attempts":3,"max_retries":3,"resolution":"max_retries_reached","timestamp":"2026-07-09T11:00:00+07:00"}
```

---

## 4. Read Rules

| Mục đích | Command | Kết quả |
|---------|---------|---------|
| Xem 20 task gần nhất | `tail -20 memory/long-term/task_history.log` | Last 20 lines |
| Xem task của worker cụ thể | `grep '"worker":"viet-bai-fb"' memory/long-term/task_history.log` | All tasks for Cây Bút |
| Xem task failed gần đây | `grep '"status":"failed"' memory/long-term/task_history.log \| tail -10` | Last 10 failures |
| Xem milestone gần đây | `grep '"type":"milestone"' memory/long-term/task_history.log \| tail -10` | Last 10 milestones |
| Đếm task hôm nay | `grep "2026-07-09" memory/long-term/task_history.log \| grep '"type":"task"' \| wc -l` | Count |

---

## 5. Write Rules

| When | Entry Type | Notes |
|------|-----------|-------|
| Task completed → done | `task` | Ghi sau khi worker trả output |
| Task failed (hết retry) | `task` | Ghi kèm error message |
| Task cancelled | `task` | Ghi kèm lý do |
| Session end | `session_summary` | Ghi 1 entry tổng kết |
| Order success (heartbeat) | `milestone` | Ghi ngay khi nhận signal |
| New lead (heartbeat) | `milestone` | Ghi ngay khi nhận signal |
| Deploy/update | `milestone` | Ghi khi anh Sáng deploy |
| Error hết retry | `error` | Ghi kèm resolution |

---

## 6. Archive Rules

| Trigger | Action |
|---------|--------|
| File > 5000 lines | Move oldest 4000 lines to `memory/archives/task_history_YYYYMMDD.log` |
| Archive file > 30 days | Compress with gzip |
| Archive file > 90 days | Keep compressed, or delete if > 1 year (configurable) |

---

## 7. Liên kết

- **Memory Strategy:** `MEMORY_STRATEGY.md`
- **Session Memory:** `SESSION_MEMORY.md`
- **Long-term Memory:** `LONG_TERM_MEMORY.md`
- **FRAMEWORK_SPEC.md:** §8 Memory System
