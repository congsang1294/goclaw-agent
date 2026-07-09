# TASK LIFECYCLE

> **File:** `docs/TASK_LIFECYCLE.md`
> **Status:** DESIGN — not yet implemented
> **Last Updated:** 2026-07-08

---

## 1. What is a Task?

A Task is the **atomic unit of work** in the AI Team Framework. Everything flows through Tasks.

**Key principles:**
- No agent calls another agent directly
- All work is assigned, tracked, and completed via Tasks
- Tasks live in the Kanban board
- Task status determines Manager behavior

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

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique task ID (timestamp + sequence) |
| `type` | enum | `skill_execution`, `approval`, `notification` |
| `status` | enum | See statuses below |
| `priority` | enum | `low`, `normal`, `high`, `critical` |
| `worker` | string | Worker agent ID (e.g., `viet-bai-fb`) |
| `skill` | string | Skill name to execute (e.g., `viet-bai-facebook`) |
| `input` | object | Parameters for the skill |
| `output` | object | Result of skill execution |
| `error` | string | Error message if failed |
| `attempts` | int | Number of execution attempts |
| `max_retries` | int | Maximum retry attempts (default: 3) |
| `parent_task` | string | Parent task ID (for multi-step workflows) |
| `depends_on` | [string] | Task IDs that must complete first |
| `timestamps` | dates | Creation, update, assignment, completion |

---

## 3. Task Statuses

```
                    ┌──────────┐
                    │  CREATED  │
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
                    ┌────▼─────┐
                    │   DONE   │  (after retry success)
                    └──────────┘
                         OR
                    ┌────▼─────┐
                    │  FAILED  │  (after max retries)
                    └──────────┘
```

**Status Definitions:**

| Status | Meaning | Triggers |
|--------|---------|----------|
| `created` | Task created but not queued | Task creation |
| `todo` | In Kanban queue, ready for dispatch | Manager enqueue |
| `in_progress` | Worker is executing | Worker picks up task |
| `done` | Worker output is valid and ready for delivery | Worker returns required artifacts |
| `failed` | Execution error (may retry) | Script error, API failure |
| `retrying` | Retry in progress | Retry Manager triggers |
| `blocked` | Waiting on dependency | depends_on not all done |
| `cancelled` | Cancelled by Manager | User cancel, timeout |

---

## 4. Task Lifecycle Flows

### 4.1 Simple Flow (Single Skill)

```
1. Manager receives user intent
2. Planner creates 1 Task
3. Task → TODO (Kanban)
4. Dispatcher assigns to Worker
5. Worker picks up → IN_PROGRESS
6. Worker executes skill
7. Success + required artifact present → DONE, output stored
8. Manager sends output to Telegram
9. Delivery confirmed → workflow complete
```

### 4.2 Complex Flow (Multi-Step with Dependencies)

```
1. Manager receives: "Làm bài đăng Facebook"
2. Planner creates 2 Tasks:
   Task A: { skill: "viet-bai-facebook", worker: "viet-bai-fb" }
   Task B: { skill: "sang-tao-creative-fb", worker: "tao-anh", depends_on: ["A"] }
3. Task A → TODO (unblocked)
   Task B → BLOCKED (waiting for A)
4. Dispatcher: Task A → viet-bai-fb
5. Cây Bút writes caption → Task A → DONE
6. Manager sees A done → unblocks B
7. Task B → TODO → tao-anh
8. Tạo Ảnh creates image with file/link → Task B → DONE
9. Manager aggregates A.output + B.output
10. Manager sends caption + image to Telegram
11. Delivery confirmed → workflow complete
```

### 4.3 Retry Flow

```
1. Task → IN_PROGRESS
2. Worker executes → API timeout
3. Task → FAILED, error: "timeout", attempts: 1
4. Retry Manager checks: attempts(1) < max_retries(3) → RETRYING
5. Task → TODO (re-queued)
6. Worker re-executes → success
7. Task → DONE only after output validation
-- OR --
6. Worker re-executes → fails 3 times
7. Task → FAILED, attempts: 3
8. Retry Manager: max retries reached → notify Manager
9. Manager: cancel workflow, notify user
```

### 4.4 Team Sync Flow (multi-worker)

```
User: "làm bài quảng cáo"
1. Manager: intent = "create_ad_campaign"
2. Planner creates full Kanban plan:
   Task A: 3 ideas (viet-bai-fb)
   Task B: approve ideas (manager)
   Task C: write caption (viet-bai-fb) ← depends on B
   Task D: create image (tao-anh) ← depends on C
   Task E: make video (lam-video) ← depends on C/D
   Task F: approve final package (manager) ← depends on C, D, E
   Task G: publish Fanpage/Reels (manager) ← depends on F
3. A → DONE → Manager sends 3 ideas to Telegram
4. User approves one idea → B DONE → C unblocks with 5-minute deadline
5. C DONE → bài viết gửi Telegram ngay → D/E unblock with caption thật
6. Image/video output finished first is sent to Telegram immediately
7. All 3 outputs delivered → Manager asks final approval
8. User approves final package → Manager publishes to Fanpage/Reels
9. Publish links sent to Telegram → workflow complete
```

---

## 5. Kanban Board

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   TODO   │  │ BLOCKED  │  │IN_PROGRES│  │   DONE   │  │  FAILED  │
├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤
│ task_003 │  │ task_005 │  │ task_001 │  │ task_000 │  │ task_002 │
│ task_004 │  │          │  │          │  │          │  │          │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

**Kanban Operations:**
- `enqueue(task)` → task → TODO
- `assign(task, worker)` → task → IN_PROGRESS
- `complete(task, output)` → task → DONE
- `fail(task, error)` → task → FAILED
- `retry(task)` → task → TODO (if attempts < max_retries)
- `cancel(task)` → task → CANCELLED
- `block(task)` → task → BLOCKED
- `unblock(task)` → task → TODO
- `get_status(task_id)` → current status
- `list_by_status(status)` → all tasks in given status

---

## 6. Task Integration Points

| Component | Creates Tasks | Reads Tasks | Updates Tasks |
|-----------|:---:|:---:|:---:|
| Manager (Intent Analyzer) | ✅ | ✅ | ❌ |
| Manager (Planner) | ✅ | ❌ | ❌ |
| Manager (Dispatcher) | ❌ | ✅ | ✅ (assign) |
| Manager (Progress Tracker) | ❌ | ✅ | ❌ |
| Manager (Retry Manager) | ❌ | ✅ | ✅ (retry) |
| Manager (Result Aggregator) | ❌ | ✅ | ❌ |
| Worker (Cây Bút) | ❌ | ✅ | ✅ (status + output) |
| Worker (Tạo Ảnh) | ❌ | ✅ | ✅ (status + output) |
| Worker (Làm Video) | ❌ | ✅ | ✅ (status + output) |
