# SYSTEM ARCHITECTURE

> **File:** `docs/SYSTEM_ARCHITECTURE.md`
> **For detailed architecture, read `ARCHITECT.md` first.**

---

## 1. High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TELEGRAM                                      │
│  ┌──────────┐  ┌─────────────┐  ┌─────────┐  ┌──────────────────┐  │
│  │ Anh Sáng │  │ User DM     │  │ Group   │  │ Heartbeat Events │  │
│  │ (Owner)  │  │ (Customers) │  │ Chats   │  │ (Orders/Leads)   │  │
│  └────┬─────┘  └──────┬──────┘  └────┬────┘  └────────┬─────────┘  │
│       └───────────────┴──────────────┴─────────────────┘            │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────┐
│                    MANAGER (Gà Trống Tre)                            │
│                                                                      │
│  ┌──────────────┐  ┌───────────┐  ┌────────────┐  ┌─────────────┐  │
│  │ Intent       │─▶│ Planner   │─▶│ Task       │─▶│ Dispatcher  │  │
│  │ Analyzer     │  │           │  │ Creator    │  │             │  │
│  └──────────────┘  └───────────┘  └────────────┘  └──────┬──────┘  │
│                                                           │          │
│  ┌──────────────┐  ┌───────────┐  ┌────────────┐         │          │
│  │ Result       │◀─│ Progress  │◀─│ Retry      │         │          │
│  │ Aggregator   │  │ Tracker   │  │ Manager    │         │          │
│  └──────┬───────┘  └───────────┘  └────────────┘         │          │
│         │                                                 │          │
│  ┌──────▼───────┐                                         │          │
│  │ Response     │                                         │          │
│  │ Builder      │◀────────────────────────────────────────┘          │
│  └──────┬───────┘                                                    │
└─────────┼────────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────────┐
│                        DYNAMIC ROUTER                                 │
│                                                                       │
│  Intent: "viết"   ───▶ Worker: viet-bai-fb                           │
│  Intent: "ảnh"    ───▶ Worker: tao-anh                               │
│  Intent: "video"  ───▶ Worker: lam-video                             │
│                       (routing is config-driven, not hardcoded)       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────────┐
│                        KANBAN / TASK QUEUE                            │
│                                                                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐  │
│  │  TODO          │  │  IN PROGRESS   │  │  DONE / FAILED        │  │
│  │  task_001      │──│  task_001      │──│  task_001 (done)      │  │
│  │  task_002 (blk)│  │                │  │                        │  │
│  └────────────────┘  └────────────────┘  └────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
┌─────────▼────┐  ┌───────▼──────┐  ┌──────▼──────────┐
│ WORKER        │  │ WORKER       │  │ WORKER           │
│ Cây Bút      │  │ Tạo Ảnh     │  │ Làm Video        │
│ viet-bai-fb  │  │ tao-anh     │  │ lam-video        │
│              │  │              │  │                  │
│ Skills:      │  │ Skills:      │  │ Skills:          │
│ • viet-bai-  │  │ • sang-tao-  │  │ • tao-video-ai   │
│   facebook   │  │   creative-  │  │                  │
│              │  │   fb         │  │                  │
│              │  │ • viet-bai-  │  │                  │
│              │  │   facebook   │  │                  │
│              │  │   (read ref) │  │                  │
└──────────────┘  └──────────────┘  └──────────────────┘
```

---

## 2. Core Components

### 2.1 Telegram Layer
**Files:** N/A (handled by GoClaw runtime)
**Function:** Gateway for all user interaction. Messages in, responses out.

### 2.2 Manager (Gà Trống Tre)
**Defined in:** `agent/AGENTS.md` (main), `agent/SOUL.md`
**Function:** Orchestrator — intent analysis, planning, task creation, dispatching, monitoring, aggregation, response.

### 2.3 Workers
**Defined in:** `agent/<worker-name>/AGENTS.md`, `agent/<worker-name>/SOUL.md`
**Function:** Execute skills, return results. Never plan or delegate.

| Worker | Agent Dir | Primary Skill |
|--------|-----------|---------------|
| Cây Bút | agent/viet-bai-fb/ | viet-bai-facebook |
| Tạo Ảnh | agent/tao-anh/ | sang-tao-creative-fb |
| Làm Video | agent/lam-video/ | tao-video-ai |

### 2.4 Skills Engine
**Location:** `skills/<skill-name>/`
**Function:** Self-contained plugin — trigger, input, output, steps, guardrails.

### 2.5 Knowledge Base
**Location:** `knowledge/`
**Function:** Single source of truth for brand voice, product info, business model.

---

## 3. Data Flow

### 3.1 Simple Intent (write a post)
```
User: "viết bài Facebook giới thiệu tool"
  → Telegram → Manager → Intent Analyzer
  → Intent: { type: "write_post", params: { topic: "tool" } }
  → Planner: [{ skill: "viet-bai-facebook", input: { topic: "tool" } }]
  → Task: { id, status: "todo", worker: "viet-bai-fb", input: {...} }
  → Router: "write_post" → "viet-bai-fb"
  → Kanban: task pushed to todo
  → Worker picks up task → executes SKILL.md steps
  → Worker returns result → Task → done
  → Manager aggregates → formats response → Telegram
```

### 3.2 Complex Team Intent (make an ad)
```
User: "làm bài đăng quảng cáo sản phẩm"
  → Manager: intent = "create_ad"
  → Planner: [
      { id: 0, skill: "viet-bai-facebook", input: {...} },
      { id: 1, skill: "sang-tao-creative-fb", input: {...}, depends_on: [0] }
    ]
  → Task 0 → viet-bai-fb (caption)
  → Task 1 → blocked until Task 0 done
  → Cây Bút → caption ready → Task 0 done
  → Task 1 unblocked → tao-anh (image + pair with caption)
  → Tạo Ảnh → image ready → Task 1 done
  → Manager aggregates caption + image → Telegram
```

### 3.3 Heartbeat Monitoring
```
Heartbeat tick → HEARTBEAT.md flow:
  → Check Pro orders (mcp_...get_success_order_signal)
  → Check new leads (mcp_...get_new_lead_signal)
  → If new: notify anh Sáng via Telegram (brand voice)
  → If both: combine into one message
  → If nothing: silence
```

---

## 4. Configuration

### 4.1 GoClaw Config (`goclaw.yml`)
- Agent ID: `ga-trong-tre`
- Owner: Công Sáng Nguyễn (Telegram 6880126421)
- Workstations: 4 Docker containers
- Telegram bindings: DM + group chats

### 4.2 Workshop Mapping
| Workspace | Container | Skills |
|-----------|-----------|--------|
| ga-trong-tre-docker | Main | All skills |
| viet-bai-fb-docker | FB Writing | viet-bai-facebook |
| tao-anh-docker | Design | sang-tao-creative-fb, viet-bai-facebook |
| lam-video-docker | Video | tao-video-ai |
