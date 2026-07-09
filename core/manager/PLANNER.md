# PLANNER

> **File:** `core/manager/PLANNER.md`
> **Role:** Convert intent → multi-step execution plan
> **Part of:** Manager (Gà Trống Tre)
> **Phase:** 1 — Core Framework

---

## 1. Mục đích

Planner nhận intent từ `INTENT_ANALYZER.md` và tạo ra **một hoặc nhiều Tasks** có thứ tự.
Đối với intent phức tạp, nó tạo dependency graph để đảm bảo task sau chờ task trước.

**Đầu vào:** Intent object `{ type, confidence, params, plan_type }`.
**Đầu ra:** Array of Task objects `[{ id, worker, skill, input, depends_on, ... }]`.

---

## 2. Plan Types

### 2.1 Simple Plan — 1 Task duy nhất

```json
{
  "plan_type": "simple",
  "tasks": [
    {
      "id": "task_20260708_001",
      "status": "todo",
      "worker": "viet-bai-fb",
      "skill": "viet-bai-facebook",
      "input": {
        "topic": "tool",
        "format": "hook_body_cta",
        "tone": "brand_voice"
      },
      "depends_on": []
    }
  ]
}
```

Áp dụng cho: `write_post`, `create_ideas`, `create_image`, `create_video`, `approve`, `check_status`, `cancel`.

### 2.2 Multi-Step Plan — Tasks có dependency

```json
{
  "plan_type": "multi_step",
  "tasks": [
    {
      "id": "task_001",
      "worker": "viet-bai-fb",
      "skill": "viet-bai-facebook",
      "input": { "topic": "sản phẩm mới" },
      "depends_on": []
    },
    {
      "id": "task_002",
      "worker": "tao-anh",
      "skill": "sang-tao-creative-fb",
      "input": { "use_output_from": "task_001" },
      "depends_on": ["task_001"]
    }
  ]
}
```

Áp dụng cho: `create_ad` (nếu cần cả caption + ảnh).

### 2.3 Complex Plan — Team Sync (Ideas → Parallel Production → Publish)

```json
{
  "plan_type": "complex",
  "campaign_id": "campaign_20260709_001",
  "deadline_minutes": 5,
  "tasks": [
    {
      "id": "task_001",
      "worker": "viet-bai-fb",
      "skill": "viet-bai-facebook",
      "input": { "topic": "...", "stage": "ideas", "required_ideas": 3 },
      "depends_on": []
    },
    {
      "id": "task_002",
      "type": "approval",
      "worker": "manager",
      "skill": null,
      "input": { "stage": "ideas", "wait_for": "task_001" },
      "depends_on": ["task_001"]
    },
    {
      "id": "task_003",
      "worker": "viet-bai-fb",
      "skill": "viet-bai-facebook",
      "input": { "stage": "caption", "use_chosen_idea_from": "task_002" },
      "depends_on": ["task_002"]
    },
    {
      "id": "task_004",
      "worker": "tao-anh",
      "skill": "sang-tao-creative-fb",
      "input": { "stage": "image", "use_chosen_idea_from": "task_002" },
      "depends_on": ["task_002"]
    },
    {
      "id": "task_005",
      "worker": "lam-video",
      "skill": "tao-video-ai",
      "input": { "stage": "video", "use_chosen_idea_from": "task_002" },
      "depends_on": ["task_002"]
    },
    {
      "id": "task_006",
      "type": "approval",
      "worker": "manager",
      "skill": null,
      "input": { "stage": "final", "wait_for": ["task_003", "task_004", "task_005"] },
      "depends_on": ["task_003", "task_004", "task_005"]
    },
    {
      "id": "task_007",
      "type": "publish",
      "worker": "manager",
      "skill": "facebook_publish",
      "input": { "stage": "publish_fanpage", "use_approved_outputs_from": "task_006" },
      "depends_on": ["task_006"]
    }
  ]
}
```

Áp dụng cho: `team_sync` (yêu cầu đồng bộ cả team).

Quy tắc:
- Task `ideas` phải chạy trước và trả đúng 3 ý tưởng.
- Chỉ sau khi anh Sáng duyệt 1 ý tưởng thì mới unblock song song `caption`, `image`, `video`.
- Ba task `caption`, `image`, `video` dùng chung `campaign_id`, `chosen_idea`, topic, key message và deadline 5 phút.
- Output nào xong trước thì Manager gửi ngay cho anh Sáng và cập nhật Kanban.
- `publish` chỉ chạy sau khi anh Sáng duyệt bộ cuối.

---

## 3. Plan Templates

```yaml
plan_templates:
  write_post:
    type: simple
    tasks:
      - worker: viet-bai-fb
        skill: viet-bai-facebook
        input_from_user: true

  create_image:
    type: simple
    tasks:
      - worker: tao-anh
        skill: sang-tao-creative-fb
        input_from_user: true

  create_video:
    type: simple
    tasks:
      - worker: lam-video
        skill: tao-video-ai
        input_from_user: true

  create_ad:
    type: multi_step
    tasks:
      - worker: viet-bai-fb
        skill: viet-bai-facebook
        input_from_user: true
      - worker: tao-anh
        skill: sang-tao-creative-fb
        depends_on_previous: true

  team_sync:
    type: complex
    tasks:
      - worker: viet-bai-fb
        skill: viet-bai-facebook
        stage: ideas
        input_from_user: true
      - worker: manager
        type: approval
        stage: ideas
      - worker: tao-anh
        skill: sang-tao-creative-fb
        stage: image
        depends_on_ideas_approval: true
      - worker: lam-video
        skill: tao-video-ai
        stage: video
        depends_on_ideas_approval: true
      - worker: viet-bai-fb
        skill: viet-bai-facebook
        stage: caption
        depends_on_ideas_approval: true
      - worker: manager
        type: approval
        stage: final
        depends_on_outputs: [caption, image, video]
      - worker: manager
        type: publish
        stage: publish_fanpage
        depends_on_final_approval: true
```

---

## 4. Task ID Format

```
task_{YYYYMMDD}_{3-digit-sequence}
task_20260708_001
task_20260708_002
```

Mỗi phiên làm việc bắt đầu từ 001. Dùng ngày giờ Việt Nam (Asia/Saigon, UTC+7).

---

## 5. Đầu ra cho Dispatcher

Sau khi Planner tạo plan, nó gửi toàn bộ tasks đến `KANBAN_BOARD.md` để enqueue.

Các task có `depends_on` không rỗng sẽ được đặt ở trạng thái `blocked`.
Các task không có dependency sẽ được đặt ở trạng thái `todo` để Dispatcher xử lý.

> **Lưu ý về worker/skill trong plan:** Planner xác định worker và skill dựa trên `ROUTING_TABLE.yaml` và `WORKER_REGISTRY.yaml`.
> Không hardcode worker trong plan template — luôn tra cứu từ config.

---

## 6. Liên kết

- **Input từ:** `INTENT_ANALYZER.md` (intent object)
- **Output đến:** `KANBAN_BOARD.md` (tasks array)
- **Template định nghĩa tại:** file này
- **File liên quan:** `ORCHESTRATION.md` (flow control)
