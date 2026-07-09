# LONG-TERM MEMORY

> **File:** `core/memory/LONG_TERM_MEMORY.md`
> **Role:** Define persistent memory — storage, archive, summarize, rotation
> **Part of:** Memory System
> **Phase:** 3 — Memory & Context

---

## 1. Mục đích

Long-term Memory lưu **dữ liệu bền vững** xuyên suốt các phiên làm việc:
- Task execution history
- Business milestones (orders, leads)
- Key decisions và changes
- Session summaries

Không giống Session Memory (bị xóa khi session end), Long-term Memory **không bao giờ bị xóa** — chỉ được archive khi quá lớn.

---

## 2. Storage

| Property | Value |
|----------|-------|
| **Directory** | `memory/long-term/` |
| **Primary file** | `memory/long-term/task_history.log` |
| **Format** | JSON Lines (`.log`) |
| **Archive dir** | `memory/archives/` |
| **Access pattern** | Append (write), tail+grep (read) |

---

## 3. File Organization

```
memory/
├── long-term/
│   └── task_history.log              # Main log (append-only)
├── sessions/
│   └── session_YYYY-MM-DD.json       # Session files (deleted on end)
└── archives/
    ├── task_history_20260701.log      # Archived history
    ├── task_history_20260601.log.gz   # Compressed archive
    └── task_history_20260501.log.gz
```

---

## 4. Read Patterns

| Mục đích | Cách đọc |
|---------|---------|
| Xem lịch sử gần đây | `tail -50 memory/long-term/task_history.log` |
| Search task của worker | `grep '"worker":"lam-video"' memory/long-term/task_history.log \| tail -20` |
| Đếm failed tasks | `grep '"status":"failed"' memory/long-term/task_history.log \| wc -l` |
| Xem milestones | `grep '"type":"milestone"' memory/long-term/task_history.log \| tail -20` |
| Xem summary các session | `grep '"type":"session_summary"' memory/long-term/task_history.log \| tail -10` |

---

## 5. Write Patterns

**Luôn append. Không bao giờ modify existing lines.**

```json
{"type":"task","id":"task_20260709_001","worker":"viet-bai-fb","skill":"viet-bai-facebook","status":"done","attempts":1,"duration_sec":90,"timestamp":"2026-07-09T08:02:30+07:00"}
```

**Ghi ngay lập tức khi:**
- Task completed → `type:task`
- Milestone xảy ra → `type:milestone`
- Session kết thúc → `type:session_summary`
- Error hết retry → `type:error`

---

## 6. Archive Rules

### Trigger: File > 5000 lines

```
1. Đếm số dòng trong task_history.log
2. Nếu > 5000:
   a. Lấy 4000 dòng đầu tiên
   b. Move vào memory/archives/task_history_YYYYMMDD.log
   c. Giữ 1000 dòng gần nhất trong task_history.log
```

### Trigger: Archive file > 30 days

```
1. Tìm file trong archives/ không có extension .gz
2. Nếu file age > 30 days:
   a. gzip file
   b. Rename → task_history_YYYYMMDD.log.gz
```

### Trigger: Archive file > 365 days

```
1. Tìm file .gz trong archives/ có age > 365 days
2. Xóa file (quá cũ, không cần giữ)
```

---

## 7. Summarize Rules

### Automatic (every 1000 entries)

```
When task_history.log reaches 1000 entries since last summarize:
  1. Read oldest 500 entries
  2. Count: total tasks, by worker, by status
  3. Identify: most common errors, average duration
  4. Write summary entry:
     {"type":"auto_summary","from":"task_20260701_001","to":"task_20260709_500",
      "range":"2026-07-01 to 2026-07-09","total_tasks":500,
      "by_worker":{"viet-bai-fb":200,"tao-anh":150,"lam-video":150},
      "by_status":{"done":450,"failed":30,"cancelled":20},
      "avg_duration_sec":85,"top_errors":["API timeout (15)","rate limit (8)"],
      "timestamp":"2026-07-09T18:00:00+07:00"}
  5. Delete oldest 500 entries (they're now summarized)
```

### Manual (on demand)

```
Khi Manager được yêu cầu "báo cáo" hoặc "tóm tắt":
  1. Đọc toàn bộ task_history.log
  2. Tổng hợp theo worker, status, thời gian
  3. Trả báo cáo ngắn
```

---

## 8. Retention Policy

| Data type | Keep hot | Archive after | Delete after |
|-----------|----------|---------------|-------------|
| Task entries | 1000 newest | 5000 lines threshold | 365 days |
| Milestones | Tất cả | 5000 lines threshold | Never |
| Session summaries | Tất cả | 5000 lines threshold | Never |
| Error entries | Tất cả | 5000 lines threshold | 365 days |

---

## 9. Initialization

Khi framework khởi động lần đầu:

```bash
# Tạo directory structure
mkdir -p memory/long-term memory/sessions memory/archives

# Tạo task_history.log nếu chưa tồn tại
touch memory/long-term/task_history.log

# Ghi entry khởi tạo
echo '{"type":"system","event":"framework_init","timestamp":"2026-07-09T08:00:00+07:00"}' >> memory/long-term/task_history.log
```

---

## 10. Liên kết

- **Memory Strategy:** `MEMORY_STRATEGY.md`
- **Task History:** `TASK_HISTORY.md`
- **Session Memory:** `SESSION_MEMORY.md`
- **FRAMEWORK_SPEC.md:** §8.3 Long-term Memory
