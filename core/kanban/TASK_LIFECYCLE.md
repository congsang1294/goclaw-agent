# TASK LIFECYCLE

> **File:** `core/kanban/TASK_LIFECYCLE.md`
> **Role:** Define all possible status transitions and lifecycle flows
> **Part of:** Kanban / Task System
> **Phase:** 1 — Core Framework

---

## 1. Status Transition Diagram

```
                    ┌──────────┐
                    │ CREATED  │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
              ┌─────│   TODO   │─────┐
              │     └────┬─────┘     │
              │          │           │
              │     ┌────▼─────┐     │
              │     │ IN_      │     │
              │     │ PROGRESS │     │
              │     └────┬─────┘     │
              │          │           │
         ┌────▼─────┐    │    ┌──────▼─────┐
         │ CANCELLED│    │    │  BLOCKED   │
         └──────────┘    │    └──────┬─────┘
                         │          │
                    ┌────▼─────┐    │
                    │   DONE   │    │
                    └──────────┘    │
                         │          │
                    ┌────▼─────┐    │
                    │  FAILED  │◄───┘
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ RETRYING │
                    └────┬─────┘
                         │
                    ┌────▼─────┐     ┌──────────┐
                    │   DONE   │     │  FAILED  │
                    └──────────┘     │ (max retry)│
                                     └──────────┘
```

---

## 2. Transition Rules

| From | To | Điều kiện | Trigger |
|------|-----|-----------|---------|
| `created` | `todo` | Task được enqueue vào Kanban | Planner |
| `todo` | `in_progress` | Dispatcher chọn task để gửi worker | Dispatcher |
| `todo` | `cancelled` | User hủy task trước khi dispatch | Manager/User |
| `in_progress` | `done` | Worker hoàn thành thành công | Worker |
| `in_progress` | `failed` | Worker báo lỗi | Worker |
| `failed` | `retrying` | Còn lượt retry | Retry Manager |
| `retrying` | `in_progress` | Retry bắt đầu | Dispatcher |
| `retrying` | `done` | Retry thành công | Worker |
| `retrying` | `failed` | Retry hết lượt | Retry Manager |
| `blocked` | `todo` | Dependency hoàn thành | Manager |
| `blocked` | `cancelled` | User hủy | Manager/User |
| `failed` | `cancelled` | Người dùng chọn bỏ qua | Manager/User |

---

## 3. Lifecycle Flows

### 3.1 Simple Flow (1 task)

```
1. Manager nhận intent
2. Planner tạo 1 task
3. Task → CREATED → TODO (Kanban)
4. Dispatcher lấy task → IN_PROGRESS
5. Worker thực thi skill
6. Worker báo done + output đủ artifact → DONE
7. Manager gửi artifact về Telegram
8. Telegram delivery đủ → workflow complete
```

**Thời gian dự kiến:** 30-120 giây (tùy skill)

### 3.2 Multi-Step Flow (N tasks có dependency)

```
1. Manager nhận "tạo quảng cáo"
2. Planner tạo 2 tasks:
   task_A: { worker: "viet-bai-fb", depends_on: [] }
   task_B: { worker: "tao-anh", depends_on: ["task_A"] }
3. task_A → TODO
   task_B → BLOCKED (chờ task_A)
4. Dispatcher: task_A → viet-bai-fb → IN_PROGRESS
5. Cây Bút viết caption xong, output hợp lệ → task_A → DONE
6. Manager thấy task_A done → unblock task_B
   task_B → TODO
7. Dispatcher: task_B → tao-anh → IN_PROGRESS
8. Tạo Ảnh tạo ảnh xong, có file/link ảnh → task_B → DONE
9. Manager aggregate kết quả → gửi caption + ảnh về Telegram
10. Chỉ báo complete sau khi Telegram delivery đủ
```

### 3.3 Retry Flow

```
1. Task → IN_PROGRESS
2. Worker gặp lỗi API timeout
3. Task → FAILED, error: "API timeout", attempts: 1
4. Retry Manager: attempts(1) < max_retries(3) → RETRYING
5. Retry Manager: gửi lại task → TODO
6. Dispatcher → IN_PROGRESS
7a. Worker thành công + output đủ artifact → DONE
    HOẶC
7b. Worker failed 3 lần → FAILED, attempts: 3
    → Retry Manager: max retries → báo Manager
    → Manager: hủy workflow, báo user
```

### 3.4 Team Sync Flow (full team)

```
1. Manager nhận "cả team làm bài về sản phẩm X"
2. Planner:
   task_A: viet-bai-fb (ideas: 3 ý tưởng)
   task_B: approval ideas (anh Sáng chọn 1 ý)
   task_C: viet-bai-fb (caption, depends_on: task_B)
   task_D: tao-anh (image, depends_on: task_C)
   task_E: lam-video (video, depends_on: task_C, optional task_D)
   task_F: approval final (depends_on: C, D, E)
   task_G: publish_fanpage (depends_on: F)
3. Dispatch A trước
4. A DONE → Gà gửi 3 ý tưởng cho anh Sáng duyệt
5. Anh Sáng duyệt ý → unblock C và set deadline 5 phút cho bài viết
6. C DONE → Gà gửi bài viết cho anh Sáng, rồi unblock D/E với caption thật
7. Đủ bài viết + ảnh + video → Gà gửi bản tổng hợp cuối xin duyệt đăng
8. Anh Sáng duyệt final → Gà đăng Fanpage/Reels
9. Đăng xong mới complete workflow
```

---

## 4. Task Timeout

Mỗi route có `timeout` config trong `ROUTING_TABLE.yaml`:

| Skill | Timeout | Worker |
|-------|---------|--------|
| viet-bai-facebook | 120s | Cây Bút |
| sang-tao-creative-fb | 300s | Tạo Ảnh |
| tao-video-ai | 600s | Làm Video |

**Khi timeout:** task tự động FAILED với error "timeout after Ns".

---

## 5. Liên kết

- **Task schema:** `TASK_SCHEMA.md`
- **Board operations:** `KANBAN_BOARD.md`
- **Retry policy:** `RETRY_POLICY.md`
- **Timeout config:** `ROUTING_TABLE.yaml`
