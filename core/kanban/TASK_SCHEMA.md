# TASK SCHEMA

> **File:** `core/kanban/TASK_SCHEMA.md`
> **Role:** Define the Task data structure — every unit of work in the framework
> **Part of:** Kanban / Task System
> **Phase:** 1 — Core Framework

---

## 1. Mục đích

Task là **đơn vị công việc trung tâm** của Framework. Mọi thứ đều là Task:
- Worker nhận Task và thực thi
- Manager theo dõi Task qua Kanban
- Task là cách duy nhất để các Agent giao tiếp với nhau

---

## 2. Task Schema

```json
{
  "id": "task_20260708_001",
  "type": "skill_execution",
  "status": "todo",
  "priority": "normal",
  "worker": "viet-bai-fb",
  "skill": "viet-bai-facebook",
  "input": {
    "topic": "giới thiệu tool",
    "tone": "brand_voice",
    "format": "hook_body_cta"
  },
  "output": null,
  "error": null,
  "attempts": 0,
  "max_retries": 3,
  "parent_task": null,
  "depends_on": [],
  "created_at": "2026-07-08T10:00:00+07:00",
  "updated_at": "2026-07-08T10:00:00+07:00",
  "assigned_at": null,
  "completed_at": null
}
```

---

## 3. Field Descriptions

| Field | Type | Bắt buộc | Mô tả |
|-------|------|---------|-------|
| `id` | string | ✅ | Unique ID: `task_{YYYYMMDD}_{NNN}` |
| `type` | enum | ✅ | `skill_execution` | `approval` | `notification` |
| `status` | enum | ✅ | Xem mục 4 |
| `priority` | enum | ✅ | `low` | `normal` | `high` | `critical` |
| `worker` | string | ✅ | Agent ID (e.g., `viet-bai-fb`) |
| `skill` | string | ✅ | Skill name (e.g., `viet-bai-facebook`) |
| `input` | object | ✅ | Parameters for the worker |
| `output` | object | ❌ | Result from worker (null khi chưa done) |
| `error` | string | ❌ | Error message nếu failed |
| `attempts` | int | ✅ | Số lần đã thử (default 0) |
| `max_retries` | int | ✅ | Max retry (default 3) |
| `parent_task` | string | ❌ | Parent task ID (cho multi-step) |
| `depends_on` | [string] | ❌ | Task IDs phải hoàn thành trước |
| `created_at` | datetime | ✅ | Thời gian tạo (Asia/Saigon) |
| `updated_at` | datetime | ✅ | Thời gian cập nhật cuối |
| `assigned_at` | datetime | ❌ | Thời gian dispatch |
| `completed_at` | datetime | ❌ | Thời gian hoàn thành |

---

## 4. Task Statuses

| Status | Ý nghĩa | Next Status |
|--------|---------|-------------|
| `created` | Vừa được tạo | `todo` |
| `todo` | Trong Kanban queue, sẵn sàng dispatch | `in_progress` hoặc `cancelled` |
| `in_progress` | Worker đang xử lý | `done` hoặc `failed` |
| `done` | Hoàn thành thành công | (cuối) |
| `failed` | Có lỗi (có thể retry) | `retrying` hoặc `cancelled` |
| `retrying` | Đang retry | `in_progress` |
| `blocked` | Chờ dependency hoàn thành | `todo` (khi dependency done) |
| `cancelled` | Bị hủy bởi Manager/user | (cuối) |

---

## 5. Task ID Format

```
task_{YYYYMMDD}_{NNN}

Ví dụ:
task_20260708_001
task_20260708_002
task_20260708_003
```

- `YYYYMMDD`: ngày hiện tại (Asia/Saigon, UTC+7)
- `NNN`: số thứ tự trong ngày, bắt đầu từ 001
- Reset về 001 mỗi ngày

---

## 6. Task ví dụ cho từng loại

### Skill Execution Task
```json
{
  "id": "task_20260708_001",
  "type": "skill_execution",
  "status": "todo",
  "worker": "viet-bai-fb",
  "skill": "viet-bai-facebook",
  "input": { "topic": "giới thiệu tool" },
  "depends_on": []
}
```

### Dependent Task (chờ task khác)
```json
{
  "id": "task_20260708_002",
  "type": "skill_execution",
  "status": "blocked",
  "worker": "tao-anh",
  "skill": "sang-tao-creative-fb",
  "input": { "use_output_from": "task_20260708_001" },
  "depends_on": ["task_20260708_001"]
}
```

### Failed Task (đã retry hết)
```json
{
  "id": "task_20260708_003",
  "type": "skill_execution",
  "status": "failed",
  "worker": "lam-video",
  "skill": "tao-video-ai",
  "error": "API timeout after 30s",
  "attempts": 3,
  "max_retries": 3
}
```

---

## 7. Liên kết

- **Tạo bởi:** `PLANNER.md`
- **Theo dõi bởi:** `KANBAN_BOARD.md`
- **Xử lý bởi:** Worker (Cây Bút, Tạo Ảnh, Làm Video)
- **Retry bởi:** `RETRY_POLICY.md`
