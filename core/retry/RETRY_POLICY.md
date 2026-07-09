# RETRY POLICY

> **File:** `core/retry/RETRY_POLICY.md`
> **Role:** Define when and how to retry failed tasks — runtime retry execution
> **Part of:** Retry Manager
> **Phase:** 4 — Runtime Integration

---

## 1. Mục đích

Retry Manager quyết định **khi nào nên retry** một task failed và **khi nào nên bỏ qua**.
Đây là runtime execution — Manager đọc và thực thi quyết định retry ngay trong turn.

---

## 2. Retry Decision Tree

```
Task FAILED đến tay Manager
    │
    ├── STEP 1: Kiểm tra error type
    │   ├── Retryable? → STEP 2
    │   └── Not retryable? → giữ FAILED → báo user → STOP
    │
    ├── STEP 2: Kiểm tra attempts vs max_retries
    │   ├── attempts < max_retries? → STEP 3 (RETRY)
    │   └── attempts >= max_retries? → giữ FAILED → báo user → STOP
    │
    ├── STEP 3: EXECUTE RETRY
    │   1. Log event: RETRY
    │   2. Kanban: failed → retrying
    │   3. GHI session file
    │   4. Kanban: retrying → todo
    │   5. GHI session file
    │   6. Dispatcher: gửi lại task (với attempt + 1)
    │
    └── STEP 4: SAU RETRY
        ├── Worker thành công → done → tiếp tục workflow
        └── Worker failed lần nữa → quay lại STEP 1
```

---

## 3. Retryable vs Non-Retryable Errors

### Retryable Errors

| Error Type | Cách nhận biết | Retry Strategy |
|-----------|----------------|----------------|
| API timeout | "timeout", "timed out", "time_out" | Exponential backoff |
| API rate limit | "rate limit", "429", "too many requests" | Backoff + chờ |
| Network error | "network", "connection", "ECONNREFUSED" | Retry ngay |
| Script crash | "script error", "exit code", "traceback" | Retry 1 lần |
| OpenAI/API fail | "API error", "500", "503", "internal server" | Retry với backoff |
| General retryable | Không khớp non-retryable list | Retry 1 lần (cautious) |

### Non-Retryable Errors

| Error Type | Cách nhận biết | Lý do |
|-----------|----------------|-------|
| Invalid input | "invalid input", "wrong format", "missing required" | Cần fix input |
| Permission | "permission denied", "unauthorized", "403" | Cần human fix |
| Invalid API key | "invalid API key", "auth failed", "401" | Cần human fix |
| File not found | "file not found", "No such file", "ENOENT" | Cần human fix |
| Schema validation | "validation error", "schema mismatch" | Cần fix skill |
| User cancelled | "cancelled", "canceled" | User chủ động |
| Unknown critical | "null pointer", "segfault", "out of memory" | System issue |

**Quy tắc:** Nếu error message không match retryable list → coi là non-retryable (cautious).
Nếu lỡ mark nhầm retryable → retry vẫn an toàn vì có max_retries guard.

---

## 4. Retry Strategy

### 4.1 Default Config

```yaml
max_retries: 3
backoff:
  initial_delay: 5s
  multiplier: 2
  max_delay: 60s
jitter: true
```

### 4.2 Backoff Timeline

| Attempt | Delay | Backoff Formula |
|---------|-------|----------------|
| 1 (first try) | 0s | Chạy ngay |
| 2 (first retry) | ~5s | initial_delay × 2^(attempt-2) + jitter |
| 3 (second retry) | ~10s | initial_delay × 2^(attempt-2) + jitter |
| 4 (third retry) | ~20s | initial_delay × 2^(attempt-2) + jitter |

**Jitter:** ±1s ngẫu nhiên để tránh thundering herd.
**Lưu ý:** Vì Claude Code xử lý turn-by-turn, delay là số turn chờ trước khi retry, không phải thời gian thực.
- 5s delay ≈ 1 turn (turn tiếp theo)
- 10s delay ≈ 2 turns
- 20s delay ≈ 3-4 turns

### 4.3 Retry với Multi-Task

Khi task failed trong multi-task workflow:

```
Tình huống: task_A (dependency của task_B) failed

Nếu task_A retry được:
  → Retry task_A
  → task_B giữ BLOCKED

Nếu task_A hết retry:
  → Hủy task_B (cascade)
  → Báo user: "Task A failed, đã hủy task B phụ thuộc"
```

---

## 5. Retry Execution Steps (Runtime)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RETRY EXECUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KHI: task.status === "failed" và Manager đang xử lý

STEP 1: ĐỌC TASK
  task = kanban.tasks.find(t => t.id === failed_task_id)
  error = task.error
  attempts = task.attempts
  max_retries = task.max_retries

STEP 2: KIỂM TRA ERROR TYPE
  error_type = classify_error(error)  // retryable | non_retryable
  
  Nếu non_retryable:
    → Log FAIL: { event: "FAIL", task_id, error, attempts }
    → Báo user: "Task [id] lỗi: {error}. Không thể retry."
    → Nếu task có dependent → hủy cascade
    → STOP

STEP 3: KIỂM TRA ATTEMPTS
  Nếu attempts >= max_retries:
    → Log FAIL: { event: "FAIL", task_id, error, attempts }
    → Báo user: "Em đã thử {attempts} lần. Lỗi: {error}. Anh muốn thử lại?"
    → Nếu task có dependent → hủy cascade
    → STOP

STEP 4: THỰC HIỆN RETRY
  attempts += 1
  
  Log RETRY:
  {"event":"RETRY","timestamp":"...","task_id":"...","attempt":attempts,"max_retries":max_retries,"error":error}
  
  Kanban:
  task.status = "retrying"
  task.attempts = attempts
  task.updated_at = now
  GHI session file
  
  → Dispatch lại task
  → Worker chạy lại skill với input cũ

STEP 5: CHỜ KẾT QUẢ
  Worker sẽ trả lời [done] hoặc [failed] trong turn này hoặc turn sau.
  → Nếu [done] → update Kanban: done → tiếp tục workflow
  → Nếu [failed] → quay lại STEP 1 (kiểm tra lại attempts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Per-Skill Retry Config

Có thể override retry config trong `ROUTING_TABLE.yaml`:

```yaml
routes:
  - id: make_video
    worker: lam-video
    skill: tao-video-ai
    timeout: 600s
    max_retries: 2          # Video tốn token, chỉ retry 2 lần
```

**Cách đọc:** Manager kiểm tra route có `max_retries` override không.
Nếu có → dùng giá trị đó. Nếu không → dùng default (3).

---

## 7. What Happens After Max Retries

Khi task failed hết lượt retry:

```
1. Task status = FAILED (vĩnh viễn)
2. Log: FAIL event
3. Manager quyết định:
   a. Task độc lập (không ai depends_on) → báo user, tiếp tục workflow
   b. Task là dependency → hủy toàn bộ dependent tasks
   c. Partial results → aggregate partial, báo user task nào fail
4. Báo user:
   "Em đã thử {attempts} lần nhưng chưa được. Lỗi: {error}.
    Anh Sáng muốn em thử lại hay bỏ qua ạ?"
```

---

## 8. Liên kết

- **Input từ:** `core/kanban/KANBAN_BOARD.md` (FAILED tasks)
- **Output đến:** `core/kanban/KANBAN_BOARD.md` (update status)
- **Log:** `memory/long-term/task_history.log`
- **Routing config:** `core/router/ROUTING_TABLE.yaml` (timeout + max_retries)
- **Task schema:** `core/kanban/TASK_SCHEMA.md` (attempts, max_retries)
- **Orchestration:** `core/manager/ORCHESTRATION.md`
