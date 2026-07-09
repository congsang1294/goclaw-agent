# PHASE 0.5 — ARCHITECTURE REVIEW

> **File:** `docs/ARCHITECTURE_REVIEW.md`
> **Date:** 2026-07-08
> **Scope:** Đối chiếu kiến trúc đề xuất với GoClaw runtime hiện tại
> **Mục tiêu:** Khóa kiến trúc trước khi implement Phase 1

---

## 1. BOUNDARY ANALYSIS: What GoClaw Already Provides vs What We Build

### 1.1 GoClaw Runtime — KHÔNG ĐỤNG TỚI

GoClaw là Go binary đọc cấu hình từ `goclaw.yml` và các file `.md`. Nó cung cấp:

| Tính năng | File/Mechanism | Ghi chú |
|-----------|---------------|---------|
| Telegram gateway | `goclaw.yml` bindings | DM + group chat |
| Multi-agent dispatch | `@agentId` in group chat | Gọi sub-agent trong group |
| Skill execution | `use_skill "skill-name"` | Đọc SKILL.md và thực thi |
| Context loading | `agent/*.md`, `knowledge/*.md` | Tự động load vào context |
| Session memory | GoClaw internal | Short-term conversation |
| Heartbeat monitoring | MCP functions | `get_success_order_signal`, `get_new_lead_signal` |
| Agent identity | `agent/SOUL.md`, `agent/*/SOUL.md` | Tính cách, giọng nói |
| User profile | `agent/USER.md` | Owner info |

**Quyết định:** ✅ **KHÔNG sửa, KHÔNG viết lại.** Tận dụng hoàn toàn.

### 1.2 GoClaw Gaps — Đây là Phần Framework Xây

| Gap | Module | Lý do GoClaw không có | Cách Framework xử lý |
|-----|--------|----------------------|---------------------|
| **Task System** | `kanban/` | GoClaw không có khái niệm Task | File-based JSON tasks + markdown lifecycle |
| **Intent Analyzer** | `manager/` | GoClaw chỉ match keyword trigger | Rule-based intent mapping via config |
| **Planner** | `manager/` | GoClaw không support multi-step | Decision tree markdown + dependency graph |
| **Dynamic Router** | `router/` | GoClaw routing = goclaw.yml static | Config-driven routing table (yaml/markdown) |
| **Result Aggregator** | `manager/` | GoClaw trả kết quả đơn lẻ | Merge rules trong markdown |
| **Retry Manager** | `retry/` | GoClaw không retry tự động | Retry policy config |
| **Persistent Memory** | `memory/` | GoClaw chỉ có session memory | File-based execution history |
| **Progress Tracking** | `kanban/` | Không có tracking | Kanban board status |

---

## 2. MODULE ANALYSIS: Phần nào đã có, phần nào xây mới

### 2.1 Agent Files — REFACTOR (thêm sections, không sửa structure)

| File | Hiện tại | Sẽ | Lý do |
|------|---------|-----|-------|
| `agent/AGENTS.md` | Manager rules + Team flow + Heartbeat | **UPDATE**: thêm Manager orchestration, Intent Analyzer rules, Planner rules | Tận dụng file đang có |
| `agent/HEARTBEAT.md` | Monitoring rules | **UPDATE**: thêm task monitoring signals | Mở rộng không phá |
| `agent/viet-bai-fb/AGENTS.md` | Worker rules | **UPDATE**: thêm Task contract (receive/update/deliver) | Worker cần biết về Task |
| `agent/tao-anh/AGENTS.md` | Worker rules | **UPDATE**: thêm Task contract | Worker cần biết về Task |
| `agent/lam-video/AGENTS.md` | Worker rules | **UPDATE**: thêm Task contract | Worker cần biết về Task |
| `agent/SOUL.md` | Brand identity | **GIỮ NGUYÊN** | Không cần sửa |
| `agent/USER.md` | User profile | **GIỮ NGUYÊN** | Không cần sửa |
| `agent/IDENTITY.md` | Identity | **GIỮ NGUYÊN** | Không cần sửa |
| `agent/CAPABILITIES.md` | Capabilities | **GIỮ NGUYÊN** | Không cần sửa |
| `agent/viet-bai-fb/SOUL.md` | Worker soul | **GIỮ NGUYÊN** | Không cần sửa |
| `agent/tao-anh/SOUL.md` | Worker soul | **GIỮ NGUYÊN** | Không cần sửa |
| `agent/lam-video/SOUL.md` | Worker soul | **GIỮ NGUYÊN** | Không cần sửa |

### 2.2 Skill Files — REFACTOR (append sections)

| File | Hiện tại | Sẽ | Lý do |
|------|---------|-----|-------|
| `skills/*/SKILL.md` | Skill definition | **APPEND**: Task status management section | Skill vẫn chạy như cũ, chỉ thêm hướng dẫn quản lý Task |

### 2.3 Knowledge Files — GIỮ NGUYÊN

| File | Lý do |
|------|-------|
| `knowledge/brand-voice.md` | Single source of truth, không sửa |
| `knowledge/knowledge-base.md` | Single source of truth, không sửa |
| `knowledge/my-business.md` | Single source of truth, không sửa |

### 2.4 Config Files — GIỮ NGUYÊN

| File | Lý do |
|------|-------|
| `goclaw.yml` | GoClaw runtime config, không đụng |
| `.gitignore` | Standard, không đụng |

### 2.5 Framework Core — TẠO MỚI (thuần markdown config)

| File | Module | Mức độ |
|------|--------|--------|
| `core/manager/INTENT_ANALYZER.md` | Manager | 🆕 Tạo mới |
| `core/manager/PLANNER.md` | Manager | 🆕 Tạo mới |
| `core/manager/ORCHESTRATION.md` | Manager | 🆕 Tạo mới |
| `core/manager/RESULT_AGGREGATOR.md` | Manager | 🆕 Tạo mới |
| `core/manager/RESPONSE_BUILDER.md` | Manager | 🆕 Tạo mới |
| `core/router/ROUTING_TABLE.yaml` | Router | 🆕 Tạo mới |
| `core/router/ROUTING_RULES.md` | Router | 🆕 Tạo mới |
| `core/kanban/TASK_SCHEMA.md` | Kanban | 🆕 Tạo mới |
| `core/kanban/KANBAN_BOARD.md` | Kanban | 🆕 Tạo mới |
| `core/kanban/TASK_LIFECYCLE.md` | Kanban | 🆕 Tạo mới |
| `core/dispatcher/DISPATCHER.md` | Dispatcher | 🆕 Tạo mới |
| `core/retry/RETRY_POLICY.md` | Retry | 🆕 Tạo mới |
| `core/events/EVENT_BUS.md` | Events | 🆕 Tạo mới (future) |
| `memory/TASK_HISTORY.md` | Memory | 🆕 Tạo mới (future) |
| `memory/PATTERNS.md` | Memory | 🆕 Tạo mới (future) |

---

## 3. CHI TIẾT TỪNG MODULE: Nội dung sẽ viết

### 3.1 Manager — Intent Analyzer (`core/manager/INTENT_ANALYZER.md`)

**Mới hay tận dụng:** 🆕 Tạo mới — GoClaw không có intent analysis.

**Nội dung:**
- Rule-based intent detection: map user message keywords → intent
- Priority ordering: explicit command > keyword match > context
- Ambiguity handling: khi không rõ ràng, hỏi 1 câu clarification
- Intent catalog (mở rộng được):
  - `write_post` → "viết bài", "post", "caption"
  - `create_image` → "ảnh", "hình", "design"
  - `create_video` → "video", "reels", "short"
  - `research` → "tìm", "research", "scout"
  - `answer_faq` → "hỏi", "faq", "giá", "tool"
  - `team_sync` → "cả team", "đồng bộ", "làm đồng loạt"
  - `approve` → "ok", "duyệt", "đăng", "tốt"
  - `check_status` → "kiểm tra", "tiến độ"
  - `cancel` → "hủy", "stop", "dừng"

**File tạo:** `core/manager/INTENT_ANALYZER.md`
**File sửa:** Không (tạo mới)

### 3.2 Manager — Planner (`core/manager/PLANNER.md`)

**Mới hay tận dụng:** 🆕 Tạo mới — GoClaw không có multi-step planning.

**Nội dung:**
- Plan = array of Tasks với dependency graph
- Simple intent → 1 task (single skill)
- Complex intent → N tasks with `depends_on`
- Team sync → 3 tasks (write → image → video)
- Plan template cho từng complex intent

**File tạo:** `core/manager/PLANNER.md`
**File sửa:** Không (tạo mới)

### 3.3 Router (`core/router/ROUTING_TABLE.yaml`)

**Mới hay tận dụng:** 🆕 Tạo mới — GoClaw routing hardcoded trong goclaw.yml.

**Nội dung:**
```yaml
routes:
  - id: write_post
    intents: [write_post, create_ideas]
    worker: viet-bai-fb
    skill: viet-bai-facebook
    timeout: 120s
    
  - id: create_images
    intents: [create_image, create_ad]
    worker: tao-anh
    skill: sang-tao-creative-fb
    timeout: 300s
    
  - id: make_video
    intents: [create_video]
    worker: lam-video
    skill: tao-video-ai
    timeout: 600s
    
  - id: team_sync
    intents: [team_sync]
    worker: manager
    skill: orchestration
    timeout: 900s
```

**File tạo:** `core/router/ROUTING_TABLE.yaml`, `core/router/ROUTING_RULES.md`
**File sửa:** Không

### 3.4 Kanban/Task (`core/kanban/TASK_SCHEMA.md`)

**Mới hay tận dụng:** 🆕 Tạo mới — GoClaw không có task concept.

**Nội dung:**
- Task JSON schema: id, status, worker, skill, input, output, error, attempts, max_retries, depends_on, timestamps
- Status: created → todo → in_progress → done | failed → retrying → done | failed | cancelled | blocked
- Task lifecycle transitions
- Kanban board: TODO | BLOCKED | IN_PROGRESS | DONE | FAILED

**File tạo:** `core/kanban/TASK_SCHEMA.md`, `core/kanban/KANBAN_BOARD.md`, `core/kanban/TASK_LIFECYCLE.md`
**File sửa:** Không

### 3.5 Dispatcher (`core/dispatcher/DISPATCHER.md`)

**Mới hay tận dụng:** 🆕 Tạo mới — cần middleware giữa router và GoClaw's `@agentId`.

**Nội dung:**
1. Đọc task từ Kanban TODO
2. Match worker từ routing table
3. Gọi worker qua GoClaw: `@workerId` trong group hoặc `use_skill`
4. Update task status → IN_PROGRESS
5. Chờ worker trả kết quả

**Lưu ý:** Dispatcher KHÔNG gọi AI. Nó chỉ là hướng dẫn cho Manager (Gà Trống Tre) biết cách dispatch task đến worker thông qua cơ chế GoClaw đã có.

**File tạo:** `core/dispatcher/DISPATCHER.md`
**File sửa:** Không

### 3.6 Retry Manager (`core/retry/RETRY_POLICY.md`)

**Mới hay tận dụng:** 🆕 Tạo mới — GoClaw không có retry.

**Nội dung:**
- Retry policy: max 3 attempts, exponential backoff
- Which errors are retryable: API timeout, API failure, script error
- Which errors are NOT retryable: invalid input, permission denied
- After max retries → notify Manager, fail task

**File tạo:** `core/retry/RETRY_POLICY.md`
**File sửa:** Không

### 3.7 Event Bus (`core/events/EVENT_BUS.md`)

**Mới hay tận dụng:** 🆕 Tạo mới — nhưng để dành cho Phase sau.

**Nội dung (future):**
- Task events: created, assigned, completed, failed
- System events: deploy, config change
- Business events: new order, new lead (tận dụng HEARTBEAT MCP)

**File tạo:** `core/events/EVENT_BUS.md`
**File sửa:** Không

### 3.8 Memory (`memory/TASK_HISTORY.md`)

**Mới hay tận dụng:** 🆕 Tạo mới — GoClaw chỉ có session memory.

**Nội dung:**
- Task execution history (JSON log)
- Pattern recognition (recurring requests)
- Performance metrics (success rate, avg time)

**File tạo:** `memory/TASK_HISTORY.md`
**File sửa:** Không

### 3.9 Agent Files Update — `agent/AGENTS.md`

**Refactor:** THÊM sections mới, KHÔNG sửa sections hiện có.

**Thêm:**
- Section: "Manager Orchestration Flow"
- Section: "Intent Analysis Rules" (gọi INTENT_ANALYZER.md)
- Section: "Planning Rules" (gọi PLANNER.md)
- Section: "Task Management" (gọi TASK_SCHEMA.md)

**Giữ nguyên:**
- "VIDEO FLOW" section
- "TEAM FLOW" section
- "HEARTBEAT FLOW" section

**Rủi ro:** Thấp — chỉ append, không delete/edit existing

### 3.10 Worker Files Update — `agent/<worker>/AGENTS.md`

**Refactor:** THÊM Task contract section.

**Thêm:**
- Section: "Task Contract — How to handle Tasks from Manager"
  - When you receive a task → set status to `in_progress`
  - When executing → follow SKILL.md
  - When complete → set status to `done`, attach output
  - When failed → set status to `failed`, attach error

**Giữ nguyên:**
- "Role" section
- "Responsibilities" section
- "Rules" section

**Rủi ro:** Thấp — chỉ append

---

## 4. KIẾN TRÚC CUỐI CÙNG SAU REVIEW

```
┌──────────────────────────────────────────────────────────────────────┐
│                         TELEGRAM                                      │
│  (GoClaw handles: routing, message format, group/DM dispatch)        │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────┐
│                     MANAGER (Gà Trống Tre)                            │
│  (GoClaw agent runtime reads core/*.md for instructions)             │
│                                                                       │
│  ┌──────────────────┐     ┌────────────┐     ┌───────────────────┐  │
│  │ INTENT_ANALYZER  │────▶│  PLANNER   │────▶│  TASK_CREATOR     │  │
│  │ (rule-based)     │     │            │     │                   │  │
│  └──────────────────┘     └────────────┘     └────────┬──────────┘  │
│                                                       │              │
│  ┌──────────────────┐     ┌────────────┐              │              │
│  │ RESULT_AGGREGATOR│◀────│  KANBAN    │◀─────────────┘              │
│  │                  │     │  BOARD     │                              │
│  └────────┬─────────┘     └────────────┘                              │
│           │               ┌────────────┐     ┌───────────────────┐  │
│           │               │  RETRY     │     │  RESPONSE_BUILDER │  │
│  ┌────────▼─────────┐    │  MANAGER   │     │  (brand voice)    │  │
│  │ DISPATCHER       │    └────────────┘     └───────────────────┘  │
│  │ (via @agentId)   │                                                   │
│  └────────┬─────────┘                                                   │
└───────────┼─────────────────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────────────────────┐
│                            ROUTER                                       │
│  (ROUTING_TABLE.yaml: intent → worker mapping, config-driven)           │
└───────────┬─────────────────────────────────────────────────────────────┘
            │
            │  (GoClaw handles: @agentId in group chat)
            │
    ┌───────┼───────────────┬───────────────────┐
    │       │               │                   │
┌───▼────┐ │  ┌────────────▼──┐  ┌─────────────▼───┐
│ viet-  │ │  │  tao-anh     │  │  lam-video     │
│ bai-fb │ │  │  (Worker)    │  │  (Worker)      │
│ (Worker)│  │               │  │                │
│         │ │  │ skill: sang- │  │ skill: tao-    │
│ skill: │ │  │ tao-         │  │ video-ai       │
│ viet-  │ │  │ creative-fb  │  │                │
│ bai-   │ │  │               │  │                │
│ face-  │ │  │               │  │                │
│ book   │ │  │               │  │                │
└────────┘ │  └───────────────┘  └────────────────┘
           │
    ┌──────┴────────────────────────────────────────────────────────────┐
    │                     SKILLS ENGINE                                  │
    │  (GoClaw reads SKILL.md, executes scripts)                        │
    └───────────────────────────────────────────────────────────────────┘
```

---

## 5. CẤU TRÚC THƯ MỤC CUỐI CÙNG

```
goclaw-agent/
│
├── goclaw.yml              ← GIỮ NGUYÊN (GoClaw runtime config)
│
├── ARCHITECT.md            ← CẬP NHẬT sau review
├── CLAUDE.md               ← GIỮ NGUYÊN
├── README.md               ← Đã cập nhật
│
├── agent/                  ← AGENTS.md: CẬP NHẬT (thêm sections)
│   ├── AGENTS.md           ← THÊM: Manager orchestration rules
│   ├── SOUL.md             ← GIỮ NGUYÊN
│   ├── USER.md             ← GIỮ NGUYÊN
│   ├── HEARTBEAT.md        ← CẬP NHẬT (thêm task monitoring)
│   ├── CAPABILITIES.md     ← GIỮ NGUYÊN
│   ├── IDENTITY.md         ← GIỮ NGUYÊN
│   │
│   ├── viet-bai-fb/
│   │   ├── AGENTS.md       ← THÊM: Task contract section
│   │   └── SOUL.md         ← GIỮ NGUYÊN
│   ├── tao-anh/
│   │   ├── AGENTS.md       ← THÊM: Task contract section
│   │   └── SOUL.md         ← GIỮ NGUYÊN
│   └── lam-video/
│       ├── AGENTS.md       ← THÊM: Task contract section
│       └── SOUL.md         ← GIỮ NGUYÊN
│
├── knowledge/              ← GIỮ NGUYÊN (single source of truth)
│   ├── brand-voice.md
│   ├── knowledge-base.md
│   └── my-business.md
│
├── skills/                 ← SKILL.md: CẬP NHẬT (append task section)
│   ├── viet-bai-facebook/
│   ├── sang-tao-creative-fb/
│   ├── tao-video-ai/
│   ├── agent-scout/
│   └── tra-loi-faq-khach-hang/
│
├── core/                   ← 🆕 TẠO MỚI (Framework core)
│   ├── manager/
│   │   ├── INTENT_ANALYZER.md    ← Rule-based intent detection
│   │   ├── PLANNER.md            ← Multi-step plan creation
│   │   ├── ORCHESTRATION.md      ← Manager flow (which order to do things)
│   │   ├── RESULT_AGGREGATOR.md  ← Merge results from multiple workers
│   │   └── RESPONSE_BUILDER.md   ← Format response in brand voice
│   │
│   ├── router/
│   │   ├── ROUTING_TABLE.yaml    ← Config-driven routing
│   │   └── ROUTING_RULES.md      ← How routing works
│   │
│   ├── kanban/
│   │   ├── TASK_SCHEMA.md        ← Task data structure
│   │   ├── KANBAN_BOARD.md       ← Board layout and operations
│   │   └── TASK_LIFECYCLE.md     ← Status transitions
│   │
│   ├── dispatcher/
│   │   └── DISPATCHER.md         ← How to send tasks to workers
│   │
│   ├── retry/
│   │   └── RETRY_POLICY.md       ← Retry rules
│   │
│   └── events/
│       └── EVENT_BUS.md          ← (Future) Event system
│
├── memory/                 ← 🆕 TẠO MỚI (future)
│   └── TASK_HISTORY.md
│
└── docs/                   ← Đã tạo từ Phase 0
    ├── ARCHITECTURE_REVIEW.md    ← File này — kết quả Phase 0.5
    ├── SYSTEM_ARCHITECTURE.md
    ├── AGENT_MAP.md
    ├── SKILL_MAP.md
    ├── TOOL_MAP.md
    ├── TASK_LIFECYCLE.md
    ├── ROUTING_RULES.md
    ├── DATABASE_ANALYSIS.md
    ├── IMPLEMENTATION_PLAN.md
    ├── TEST_PLAN.md
    ├── RISK_ANALYSIS.md
    └── ROADMAP.md
```

---

## 6. CƠ CHẾ TEMPLATE CHO DỰ ÁN MỚI

### 6.1 Khái Niệm "Template = Framework - Business"

Framework là phần `core/` + `docs/` — KHÔNG chứa business logic.

Để tạo dự án mới:

```
Step 1: Copy framework template
  cp -r goclaw-agent-template/ my-new-project/

Step 2: Xóa business-specific files
  rm my-new-project/knowledge/my-business.md  (viết lại)
  rm my-new-project/knowledge/brand-voice.md  (viết lại)
  rm my-new-project/knowledge/knowledge-base.md  (viết lại)
  rm -rf my-new-project/skills/*  (thay skills mới)

Step 3: Giữ nguyên framework core
  my-new-project/core/manager/        ← GIỮ NGUYÊN
  my-new-project/core/router/         ← GIỮ NGUYÊN
  my-new-project/core/kanban/         ← GIỮ NGUYÊN

Step 4: Thêm business mới
  my-new-project/agent/USER.md        ← Sửa
  my-new-project/agent/SOUL.md        ← Sửa  
  my-new-project/knowledge/brand-voice.md  ← Viết mới
  my-new-project/skills/*/SKILL.md    ← Viết mới
  my-new-project/goclaw.yml           ← Sửa
```

### 6.2 Template CLI (Phase 5)

```bash
goclaw new my-project --template /path/to/goclaw-agent
# Hoặc
./scripts/new-project.sh my-project
```

Template CLI sẽ:
1. Copy `core/`, `docs/`, `ARCHITECT.md`, `CLAUDE.md`, `.gitignore`
2. Xóa `knowledge/`, `agent/`, `skills/`, `goclaw.yml`
3. Tạo file template mới (empty branded voice, empty knowledge, example skill)
4. Khởi tạo git repo mới

---

## 7. CƠ CHẾ PLUGIN/SKILL

### 7.1 Skill Plugin Contract

Mỗi Skill là 1 directory với contract:

```
skills/<skill-name>/
├── SKILL.md           ← BẮT BUỘC: trigger, input, output, steps, guardrails
├── assets/            ← TÙY CHỌN: templates, references
├── scripts/           ← TÙY CHỌN: Python/shell scripts
└── references/        ← TÙY CHỌN: deep guides
```

**Để thêm Skill mới:**
1. Tạo thư mục `skills/<skill-name>/`
2. Viết `SKILL.md` theo template
3. Thêm route trong `core/router/ROUTING_TABLE.yaml`
4. Tạo worker agent nếu cần `agent/<worker-id>/AGENTS.md`
5. Thêm vào `goclaw.yml` workstations nếu cần

**Để xóa/replace Skill:**
1. Xóa thư mục skill
2. Xóa route
3. Xóa worker agent (nếu không dùng nữa)
4. Update goclaw.yml

**Không cần:** Sửa core framework, sửa docs, sửa AGENTS.md chính.

### 7.2 Skill Isolation

- Skill KHÔNG gọi skill khác
- Skill KHÔNG biết về Kanban/Task (Worker làm việc đó)
- Skill chỉ biết: input → process → output
- Skill chỉ đọc: `knowledge/*.md`, `agent/*.md` context

---

## 8. NGĂN CHẶN BACKWARD COMPATIBILITY

### 8.1 Risk: Phá vỡ Telegram flow hiện tại

**Cơ chế:** GoClaw xử lý Telegram → đọc goclaw.yml → dispatch.

**Ngăn chặn:** 
- `goclaw.yml` GIỮ NGUYÊN
- `agent/AGENTS.md` chỉ APPEND sections, không sửa tồn tại
- BINDINGS giữ nguyên

### 8.2 Risk: Phá vỡ Skill execution

**Cơ chế:** GoClaw đọc `SKILL.md` → thực thi steps.

**Ngăn chặn:**
- `skills/*/SKILL.md` chỉ APPEND "Task Status Management" section
- KHÔNG sửa trigger phrases
- KHÔNG sửa execution steps
- KHÔNG sửa input/output format

### 8.3 Risk: Phá vỡ Knowledge

**Cơ chế:** GoClaw load `knowledge/*.md` vào context.

**Ngăn chặn:**
- `knowledge/` GIỮ NGUYÊN
- Chỉ thêm kiến thức mới, không xóa

### 8.4 Risk: Conflict với agent identity

**Cơ chế:** GoClaw đọc `agent/SOUL.md` + `agent/*/SOUL.md` cho tone.

**Ngăn chặn:**
- `SOUL.md` files GIỮ NGUYÊN
- `USER.md` GIỮ NGUYÊN

---

## 9. FILE CHANGE SUMMARY (Phase 1)

### Files sẽ TẠO MỚI (12 files)

| # | File | Dung lượng dự kiến |
|---|------|-------------------|
| 1 | `core/manager/INTENT_ANALYZER.md` | ~200 lines |
| 2 | `core/manager/PLANNER.md` | ~150 lines |
| 3 | `core/manager/ORCHESTRATION.md` | ~100 lines |
| 4 | `core/manager/RESULT_AGGREGATOR.md` | ~80 lines |
| 5 | `core/manager/RESPONSE_BUILDER.md` | ~80 lines |
| 6 | `core/router/ROUTING_TABLE.yaml` | ~60 lines |
| 7 | `core/router/ROUTING_RULES.md` | ~100 lines |
| 8 | `core/kanban/TASK_SCHEMA.md` | ~120 lines |
| 9 | `core/kanban/KANBAN_BOARD.md` | ~100 lines |
| 10 | `core/kanban/TASK_LIFECYCLE.md` | ~150 lines |
| 11 | `core/dispatcher/DISPATCHER.md` | ~100 lines |
| 12 | `core/retry/RETRY_POLICY.md` | ~80 lines |

### Files sẽ SỬA (8 files)

| # | File | Thay đổi |
|---|------|----------|
| 1 | `agent/AGENTS.md` | APPEND orchestration section |
| 2 | `agent/HEARTBEAT.md` | APPEND task monitoring |
| 3 | `agent/viet-bai-fb/AGENTS.md` | APPEND task contract |
| 4 | `agent/tao-anh/AGENTS.md` | APPEND task contract |
| 5 | `agent/lam-video/AGENTS.md` | APPEND task contract |
| 6 | `skills/viet-bai-facebook/SKILL.md` | APPEND task status section |
| 7 | `skills/sang-tao-creative-fb/SKILL.md` | APPEND task status section |
| 8 | `skills/tao-video-ai/SKILL.md` | APPEND task status section |

### Files KHÔNG ĐỤNG (24 files)

`goclaw.yml`, `agent/SOUL.md`, `agent/USER.md`, `agent/CAPABILITIES.md`, `agent/IDENTITY.md`, `agent/viet-bai-fb/SOUL.md`, `agent/tao-anh/SOUL.md`, `agent/lam-video/SOUL.md`, `knowledge/*.md` (3 files), `skills/agent-scout/SKILL.md`, `skills/tra-loi-faq-khach-hang/SKILL.md`, `skills/*/assets/` (10+ files), `skills/*/scripts/` (10+ files), `.gitignore`

---

## 10. TÓM TẮT QUYẾT ĐỊNH KIẾN TRÚC

| Quyết định | Lý do |
|-----------|-------|
| **Core framework = markdown instructions**, không phải code | GoClaw runtime là Go binary, repo này chỉ chứa config. Framework là conventions + instructions cho GoClaw agent runtime. |
| **Không viết lại GoClaw features** | Tận dụng: Telegram, skill execution, context loading, multi-agent dispatch |
| **Task dùng file-based storage** | Không cần database; dễ backup; có thể migrate sau |
| **Routing = YAML config** | Config-driven, không hardcode, dễ mở rộng |
| **Intent Analysis = rule-based matching** | Đơn giản, đủ dùng, không cần ML |
| **Planner = decision tree markdown** | Không cần code; đủ cho số lượng intent giới hạn |
| **Event Bus = để dành Phase sau** | Chưa cần ngay; tránh over-engineering |
| **Template = `core/` + script** | Framework core độc lập business; script scaffold project mới |
| **Skill plugin = directory contract** | Add/remove skill không cần sửa core |
