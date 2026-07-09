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
  "campaign_id": "campaign_20260708_001",
  "stage": "caption",
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
  "delivery": {
    "status": "not_ready",
    "required": ["caption"],
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
  "created_at": "2026-07-08T10:00:00+07:00",
  "updated_at": "2026-07-08T10:00:00+07:00",
  "assigned_at": null,
  "deadline_at": null,
  "completed_at": null
}
```

---

## 3. Field Descriptions

| Field | Type | Bắt buộc | Mô tả |
|-------|------|---------|-------|
| `id` | string | ✅ | Unique ID: `task_{YYYYMMDD}_{NNN}` |
| `type` | enum | ✅ | `skill_execution`, `approval`, `notification`, `publish` |
| `status` | enum | ✅ | Xem mục 4 |
| `campaign_id` | string | ❌ | ID gom các task cùng một bộ nội dung |
| `stage` | enum | ❌ | `ideas`, `ideas_approval`, `caption`, `image`, `video`, `final_approval`, `publish_fanpage` |
| `priority` | enum | ✅ | `low`, `normal`, `high`, `critical` |
| `worker` | string | ✅ | Agent ID (e.g., `viet-bai-fb`) |
| `skill` | string | ✅ | Skill name (e.g., `viet-bai-facebook`) |
| `input` | object | ✅ | Parameters for the worker |
| `output` | object | ❌ | Result from worker (null khi chưa done) |
| `error` | string | ❌ | Error message nếu failed |
| `delivery` | object | ❌ | Trạng thái gửi kết quả về Telegram; xem mục 4.1 |
| `progress_percent` | int | ❌ | Tiến độ 0-100 để báo anh Sáng |
| `progress_note` | string | ❌ | Worker đang làm gì |
| `attempts` | int | ✅ | Số lần đã thử (default 0) |
| `max_retries` | int | ✅ | Max retry (default 3) |
| `parent_task` | string | ❌ | Parent task ID (cho multi-step) |
| `depends_on` | [string] | ❌ | Task IDs phải hoàn thành trước |
| `created_at` | datetime | ✅ | Thời gian tạo (Asia/Saigon) |
| `updated_at` | datetime | ✅ | Thời gian cập nhật cuối |
| `assigned_at` | datetime | ❌ | Thời gian dispatch |
| `deadline_at` | datetime | ❌ | Deadline task; team_sync sau duyệt ý tưởng là 5 phút |
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

## 4.1 Progress Rules

Mọi worker task phải cập nhật tiến độ:

| Stage | Progress gợi ý |
|-------|----------------|
| `ideas` | 0 nhận task, 40 đang lên góc, 80 đang chọn lọc, 100 trả đủ 3 ý tưởng |
| `caption` | 0 nhận task, 40 viết nháp, 70 chỉnh brand voice, 100 trả text bài viết |
| `image` | 0 nhận task, 30 dựng prompt/concept, 70 đang gen ảnh, 100 trả file/link ảnh |
| `video` | 0 nhận task, 25 dựng kịch bản/prompt, 60 render, 85 export, 100 trả preview/file video |

Quy tắc deadline:
- Sau khi anh Sáng duyệt ý tưởng, các task `caption`, `image`, `video` có `deadline_at = now + 5 phút`.
- Nếu quá deadline mà chưa `done`, Manager phải báo task nào trễ, worker đang làm gì, progress bao nhiêu phần trăm.
- Output nào đạt `done` trước phải được gửi về Telegram ngay, không chờ đủ bộ.

---

## 4.2 Delivery Status

`task.status = "done"` chỉ có nghĩa là worker đã tạo xong output hợp lệ.
Workflow chỉ được báo hoàn tất với anh Sáng khi các artifact bắt buộc đã gửi về Telegram.

```json
{
  "delivery": {
    "status": "not_ready",
    "required": ["caption", "image", "video"],
    "sent": [],
    "telegram_message_id": null,
    "delivered_at": null,
    "error": null
  }
}
```

| Field | Type | Mô tả |
|-------|------|-------|
| `delivery.status` | enum | `not_ready`, `ready`, `sent`, `failed` |
| `delivery.required` | array | Artifact bắt buộc theo skill: `caption`, `image`, `video` |
| `delivery.sent` | array | Artifact đã gửi thành công về Telegram |
| `delivery.telegram_message_id` | string | ID/message ref sau khi GoClaw gửi thành công, nếu có |
| `delivery.delivered_at` | datetime | Thời điểm gửi đủ artifact về Telegram |
| `delivery.error` | string | Lỗi gửi Telegram nếu có |

Quy tắc bắt buộc:
- `viet-bai-facebook`: phải có `caption`.
- `sang-tao-creative-fb`: phải có `caption_paired` và ít nhất một trong `image_url`, `image_local`.
- `tao-video-ai`: phải có ít nhất một trong `video_preview`, `video_url`; nếu task có caption/ảnh đầu vào thì response cuối phải gửi lại context đó hoặc link tới nó.
- Không log `DONE` cho plan khi bất kỳ task nào có `delivery.status != "sent"` và artifact đó là kết quả cần anh Sáng nhận.

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
