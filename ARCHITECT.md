# Gà Trống Tre — AI Team Framework Architecture

> **Version:** 1.3.0
> **Status:** REVIEWED — pending final approval
> **Author:** Principal Software Architect
> **Last Updated:** 2026-07-09
> **Architecture Review:** `docs/ARCHITECTURE_REVIEW.md`

---

## Vision

Build an **AI Team Framework** that turns a single AI agent into a multi-agent team with a Manager (Orchestrator), specialized Workers, dynamic routing, and a Task/Kanban system at its core.

The framework must be:
- **Reusable** — clone it for any project (Google Ads, Affiliate, YouTube AI, SEO, Email Marketing, etc.)
- **Extensible** — add new Agents, Skills, and Tools without touching the core
- **Practical** — runs on Claude Code + GoClaw platform; framework = markdown instructions + conventions, not a code runtime
- **Safe** — backward-compatible, no breaking changes to existing workflows

---

## Design Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Task is the center** | Every unit of work is a Task. Agents communicate through Tasks, not direct calls. |
| 2 | **Manager routes, Workers execute** | Manager (Gà Trống Tre) plans and delegates. Workers only execute skills. |
| 3 | **Routing is dynamic + config-driven** | Intent → Route → Worker. Adding a new worker only needs config entries in `ROUTING_TABLE.yaml` and `WORKER_REGISTRY.yaml`. Manager reads config — no hardcoded workers. |
| 4 | **Skills are plugins** | Each Skill is self-contained (trigger, input, output, context). No cross-skill coupling. |
| 5 | **Context is assembled, not dumped** | Manager assembles minimal context for each Worker. Worker only gets what it needs for the Task. No full-knowledge dump. |
| 6 | **Memory is layered** | Short-term (in-session), Session (GoClaw internal), Long-term (file-based), Knowledge Base (static). Each layer has explicit read/write/delete rules. |
| 7 | **No agent-to-agent calls** | No `claude_remote` orchestration. Only Manager → Worker through Tasks via `@agentId`. |
| 8 | **Backward compatibility** | Every existing Telegram flow, Skill, and knowledge file must keep working. |
| 9 | **Framework = instructions + conventions, not code** | This repo is GoClaw config. The "framework" is structured markdown files that tell the AI how to behave. We do NOT rewrite GoClaw runtime features. |
| 10 | **Don't rebuild GoClaw** | Tận dụng Telegram, context loading, skill execution (`use_skill`), multi-agent dispatch (`@agentId`), heartbeat MCP, goclaw.yml. Chỉ xây phần GoClaw không có. |

---

## GoClaw Boundary Analysis

Kiến trúc được chia làm 3 lớp rõ ràng:

### Lớp 1: GoClaw Runtime — KHÔNG ĐỤNG
```
Telegram gateway         (goclaw.yml bindings)
Multi-agent dispatch     (@agentId in group chat)
Skill execution          (use_skill "skill-name")
Context loading          (agent/*.md + knowledge/*.md)
Session memory           (GoClaw internal)
Heartbeat monitoring     (MCP functions)
Agent identity           (SOUL.md files)
```

### Lớp 2: Framework Core — XÂY MỚI (markdown instructions)
```
Intent Analyzer          (core/manager/INTENT_ANALYZER.md)
Planner                  (core/manager/PLANNER.md)
Task Creator             (core/kanban/TASK_SCHEMA.md)
Dynamic Router           (core/router/ROUTING_TABLE.yaml)
Dispatcher               (core/dispatcher/DISPATCHER.md)
Progress Tracker         (core/kanban/KANBAN_BOARD.md)
Result Aggregator        (core/manager/RESULT_AGGREGATOR.md)
Response Builder         (core/manager/RESPONSE_BUILDER.md)
Retry Manager            (core/retry/RETRY_POLICY.md)
Worker Registry          (core/worker/WORKER_REGISTRY.yaml)
Context Assembler        (core/context/CONTEXT_ASSEMBLER.md)
Context Contract         (core/context/CONTEXT_CONTRACT.md)
Prompt Assembly          (core/context/PROMPT_ASSEMBLY.md)
Memory Manager           (core/memory/MEMORY_STRATEGY.md)
Task History             (core/memory/TASK_HISTORY.md)
Session Memory           (core/memory/SESSION_MEMORY.md)
Long-term Memory         (core/memory/LONG_TERM_MEMORY.md)
```

### Lớp 3: Business Config — THAY CHO MỖI DỰ ÁN
```
knowledge/               (brand voice, product info)
agent/USER.md            (owner info)
agent/SOUL.md            (agent identity)
skills/*/                (domain skills)
goclaw.yml               (runtime config)
```

---

## System Architecture

```
Telegram (User / Anh Sáng)
    │
    │  [GoClaw handles: message routing, context loading]
    ▼
┌──────────────────────────────────────────────────────────┐
│              MANAGER (Gà Trống Tre)                       │
│  (Claude Code reads core/*.md for instructions)           │
│                                                           │
│  ┌──────────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │  INTENT_ANALYZER │─▶│  PLANNER   │─▶│ TASK_CREATOR │ │
│  │  (rule-based)    │  │            │  │              │ │
│  └──────────────────┘  └────────────┘  └──────┬───────┘ │
│                                                │         │
│  ┌──────────────────┐  ┌────────────┐          │         │
│  │ RESULT_AGGREGATOR│◀─│  KANBAN    │◀─────────┘         │
│  │                  │  │  BOARD     │                     │
│  └────────┬─────────┘  └────────────┘                     │
│           │            ┌────────────┐  ┌──────────────┐  │
│           │            │   RETRY    │  │  RESPONSE    │  │
│  ┌────────▼─────────┐ │  MANAGER   │  │  BUILDER     │  │
│  │   DISPATCHER     │ └────────────┘  └──────────────┘  │
│  │  (via @agentId)  │                                     │
│  └────────┬─────────┘                                     │
└───────────┼───────────────────────────────────────────────┘
            │
┌───────────▼───────────────────────────────────────────────┐
│                 DYNAMIC ROUTER                             │
│  (core/router/ROUTING_TABLE.yaml: intent → worker)        │
└───────────┬───────────────────────────────────────────────┘
            │
            │  [GoClaw handles: @agentId in group chat]
            │
    ┌───────┼──────────────┬────────────────────┐
    │       │              │                    │
┌───▼────┐ │  ┌───────────▼───┐  ┌──────────────▼──┐
│ viet-  │ │  │  tao-anh     │  │  lam-video     │
│ bai-fb │ │  │  (Worker)    │  │  (Worker)      │
│ (Worker)│ │  │              │  │                │
└────────┘ │  └──────────────┘  └────────────────┘
           │
    ┌──────┴─────────────────────────────────────────────────────────┐
    │                    SKILLS ENGINE                                │
    │  (GoClaw reads SKILL.md, executes scripts via use_skill)       │
    └────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Manager (Gà Trống Tre)

The Manager is the brain of the system. It does NOT execute skills directly. 
Manager behavior is defined in `agent/AGENTS.md` (orchestration) and `core/manager/*.md` (detailed rules).

**Responsibilities:**
- Understand user intent from Telegram messages
- Create a plan from the intent
- Break the plan into Tasks
- Route each Task to the right Worker
- Track progress through Kanban
- Retry failed Tasks
- Aggregate results into a response
- Send response back via Telegram (through GoClaw)

**Manager sub-components (all in `core/manager/`):**

| Component | File | Type | Responsibility |
|-----------|------|------|---------------|
| **Intent Analyzer** | `INTENT_ANALYZER.md` | 🆕 New | Rule-based: user message → intent |
| **Planner** | `PLANNER.md` | 🆕 New | Intent → multi-step plan with dependency graph |
| **Orchestration** | `ORCHESTRATION.md` | 🆕 New | Flow control: which order to invoke components |
| **Result Aggregator** | `RESULT_AGGREGATOR.md` | 🆕 New | Merge outputs from multiple workers |
| **Response Builder** | `RESPONSE_BUILDER.md` | 🆕 New | Format response in brand voice |
| **Context Assembler** | `core/context/CONTEXT_ASSEMBLER.md` | 🆕 New | Assemble minimal context per worker + task |
| **Prompt Assembly** | `core/context/PROMPT_ASSEMBLY.md` | 🆕 New | Combine role + task + context + constraints |
| **Memory Manager** | `core/memory/MEMORY_STRATEGY.md` | 🆕 New | Read/write/delete/archive memory layers |

### 2. Workers

Workers are specialized agents defined in `agent/<worker-id>/`. Each Worker has exactly one role, one or more Skills.

| Worker | ID | Primary Skill | Input | Output |
|--------|-----|-------|-------|--------|
| **Cây Bút** | `viet-bai-fb` | `viet-bai-facebook` | Topic + brief | 3 ideas OR full caption |
| **Tạo Ảnh** | `tao-anh` | `sang-tao-creative-fb` | Caption + concept | Image + paired caption |
| **Làm Video** | `lam-video` | `tao-video-ai` | Caption + images | MP4 video |

**Worker contract:**
- Receive Task from Manager only (via `@agentId` in group)
- Execute Skill according to SKILL.md
- Update Task status (in_progress → done / failed)
- Return result data (never format the response — Manager handles that)
- Never call another Worker or create Tasks

**Task contract** (new section in each worker's AGENTS.md):
- "When you receive a task → set status to `in_progress`"
- "When complete → set status to `done`, attach output"
- "When failed → set status to `failed`, attach error"

### 3. Dynamic Router

The Router maps intent → worker. Defined in `core/router/ROUTING_TABLE.yaml` (config-driven).
Worker metadata (binding, skills, timeout) is read from `core/worker/WORKER_REGISTRY.yaml`.

```yaml
routes:
  - id: write_post
    intents: [write_post]
    worker: viet-bai-fb
    skill: viet-bai-facebook
    timeout: 120s

  - id: create_ideas
    intents: [create_ideas]
    worker: viet-bai-fb
    skill: viet-bai-facebook
    timeout: 120s

  - id: create_images
    intents: [create_image]
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

  - id: answer_faq
    intents: [answer_faq]
    worker: manager
    skill: tra-loi-faq-khach-hang
    timeout: 60s

  - id: unknown_intent
    intents: [unknown]
    worker: manager
    skill: orchestration
    timeout: 15s
```

**To add a new Worker:** add row to ROUTING_TABLE.yaml + create `agent/<worker-id>/` + create `skills/<skill-name>/SKILL.md` + update `goclaw.yml` if needed.

### 4. Kanban / Task System

Tasks are the central unit of work. Defined in `core/kanban/`.

**Task schema:**
```json
{
  "id": "task_20260708_001",
  "status": "todo" | "in_progress" | "done" | "failed" | "cancelled" | "blocked" | "retrying",
  "worker": "viet-bai-fb",
  "skill": "viet-bai-facebook",
  "input": { "topic": "giới thiệu tool", "tone": "brand_voice" },
  "output": null | { "caption": "..." },
  "error": null | "timeout after 30s",
  "attempts": 0,
  "max_retries": 3,
  "parent_task": null | "task_20260708_000",
  "depends_on": [],
  "created_at": "2026-07-08T10:00:00+07:00",
  "updated_at": "2026-07-08T10:00:00+07:00",
  "assigned_at": null,
  "completed_at": null
}
```

**Task lifecycle:**
```
created → todo → in_progress → done
                → failed → retrying → todo → in_progress → done
                → cancelled
                → blocked (waiting on dependency)
```

### 5. Skills Engine

Each Skill is a self-contained plugin directory. GoClaw reads SKILL.md and executes the steps.

**Skill directory structure:**
```
skills/<skill-name>/
├── SKILL.md           # Required: trigger, input, output, steps, guardrails
├── assets/            # Optional: templates, references
├── scripts/           # Optional: Python/shell scripts
└── references/        # Optional: deep reference guides
```

**Skill contract:**
- SKILL.md is the single source of truth for how the skill runs
- Skills receive context from Manager via Context Contract (not raw file reads)
- Skills do NOT call other skills directly
- Skills do NOT write to the Kanban (Workers do that via Task contract)

### 6. Context System (Phase 3)

Context is assembled by the Manager, not dumped. Every Worker receives only the context it needs.

**7 context types:**

| Context | Source | Scope | Assembled When |
|---------|--------|-------|----------------|
| **System Context** | `FRAMEWORK_SPEC.md`, `core/*` | Global — framework rules | Session start |
| **Project Context** | `goclaw.yml`, `ARCHITECT.md` | Project-wide config | Session start |
| **Agent Context** | `agent/SOUL.md`, `agent/AGENTS.md` | Per-agent identity + rules | Agent activation |
| **User Context** | `agent/USER.md`, `USER_PREDEFINED.md` | User profile + preferences | User message |
| **Task Context** | Task schema + Kanban | Current task + dependencies | Task dispatch |
| **Session Context** | `core/memory/SESSION_MEMORY.md` | Current conversation | Per-turn |
| **Runtime Context** | MCP signals, heartbeat | Real-time business signals | When available |

**Context Assembly Pipeline:**
```
User Message
  → 1. Load System Context (once per session)
  → 2. Load Project Context (once per session)
  → 3. Load Agent Context (per agent identity)
  → 4. Load User Context (per user)
  → 5. Load Session Context (current conversation)
  → 6. Create Task Context (per task being dispatched)
  → 7. Attach Runtime Context (if applicable)
  → 8. Filter: chỉ giữ context cần thiết cho Worker/Skill
  → 9. Package into Context Contract → dispatch to Worker
```

**Context Contract** (what Worker receives):
```json
{
  "context": {
    "agent": { "name": "Cây Bút", "role": "...", "soul_ref": "agent/viet-bai-fb/SOUL.md" },
    "user": { "name": "anh Sáng", "preferences": "short, direct" },
    "task": { "id": "task_001", "input": { "topic": "..." }, "depends_on": [] },
    "knowledge": { "brand_voice": "reference to knowledge/brand-voice.md" },
    "session": { "conversation_summary": "..." }
  }
}
```

### 7. Memory System (Phase 3)

Memory is layered — each layer has explicit read/write/delete rules.

**4 memory layers:**

| Layer | Storage | Duration | Read | Write | Delete | Summarize |
|-------|---------|----------|------|-------|--------|-----------|
| **Short-term** | In-memory (GoClaw) | Per-turn | Every turn | Every turn | Auto on turn end | Never |
| **Session** | File-based (`memory/sessions/`) | Per-session | Session start | On task events | Session end | Session end |
| **Long-term** | File-based (`memory/long-term/`) | Persistent | Before planning | On milestone | Never (archive) | Weekly |
| **Knowledge Base** | Static files (`knowledge/*.md`) | Permanent | Every session | Manual edits | Never | Never |

### 8. Prompt Assembly (Phase 3)

Manager automatically assembles the final prompt before dispatching to Worker:

```
PROMPT = System Prompt + Role + Task + Context + Knowledge + Constraints + Output Format

1. SYSTEM PROMPT   → from FRAMEWORK_SPEC.md (core rules, behavior constraints)
2. ROLE            → from agent/<worker-id>/SOUL.md + AGENTS.md (who the worker is)
3. TASK            → from Task schema (what to do, input params)
4. CONTEXT         → from Context Assembler (assembled minimal context)
5. KNOWLEDGE       → from knowledge/*.md (brand voice, product info — filtered)
6. CONSTRAINTS     → from Task Contract + SKILL.md (what NOT to do, guardrails)
7. OUTPUT FORMAT   → from Task Contract + Worker AGENTS.md (JSON schema)
```

---

## File Structure (Framework)

```
goclaw-agent/
│
├── goclaw.yml              ← GIỮ NGUYÊN (GoClaw runtime config)
├── ARCHITECT.md            ← CẬP NHẬT: architecture reference
├── CLAUDE.md               ← GIỮ NGUYÊN
├── README.md               ← Đã cập nhật
│
├── agent/                  ← Agent definitions
│   ├── AGENTS.md           ← THÊM: Manager orchestration rules
│   ├── SOUL.md             ← GIỮ NGUYÊN
│   ├── USER.md             ← GIỮ NGUYÊN
│   ├── HEARTBEAT.md        ← THÊM: task monitoring signals
│   ├── CAPABILITIES.md     ← GIỮ NGUYÊN
│   ├── IDENTITY.md         ← GIỮ NGUYÊN
│   ├── viet-bai-fb/        ← THÊM: Task contract in AGENTS.md
│   ├── tao-anh/            ← THÊM: Task contract in AGENTS.md
│   └── lam-video/          ← THÊM: Task contract in AGENTS.md
│
├── knowledge/              ← GIỮ NGUYÊN (single source of truth)
│   ├── brand-voice.md
│   ├── knowledge-base.md
│   └── my-business.md
│
├── skills/                 ← Plugin directory
│   ├── viet-bai-facebook/  ← APPEND: Task status management section
│   ├── sang-tao-creative-fb/ ← APPEND: Task status management section
│   ├── tao-video-ai/       ← APPEND: Task status management section
│   ├── agent-scout/        ← GIỮ NGUYÊN
│   └── tra-loi-faq-khach-hang/ ← GIỮ NGUYÊN
│
├── core/                   ← 🆕 TẠO MỚI (Framework core)
│   ├── manager/
│   │   ├── INTENT_ANALYZER.md
│   │   ├── PLANNER.md
│   │   ├── ORCHESTRATION.md
│   │   ├── RESULT_AGGREGATOR.md
│   │   └── RESPONSE_BUILDER.md
│   │
│   ├── router/
│   │   ├── ROUTING_TABLE.yaml
│   │   └── ROUTING_RULES.md
│   │
│   ├── kanban/
│   │   ├── TASK_SCHEMA.md
│   │   ├── KANBAN_BOARD.md
│   │   └── TASK_LIFECYCLE.md
│   │
│   ├── dispatcher/
│   │   └── DISPATCHER.md
│   │
│   ├── retry/
│   │   └── RETRY_POLICY.md
│   │
│   ├── worker/
│   │   ├── WORKER_REGISTRY.yaml
│   │   └── WORKER_REGISTRY.md
│   │
│   ├── context/
│   │   ├── CONTEXT_ASSEMBLER.md
│   │   ├── CONTEXT_CONTRACT.md
│   │   └── PROMPT_ASSEMBLY.md
│   │
│   └── memory/
│       ├── MEMORY_STRATEGY.md
│       ├── TASK_HISTORY.md
│       ├── SESSION_MEMORY.md
│       └── LONG_TERM_MEMORY.md
│
├── memory/                 ← 🆕 TẠO MỚI (runtime data)
│   ├── sessions/
│   │   └── session_YYYY-MM-DD.json
│   └── long-term/
│       └── task_history.log
│
└── docs/                   ← Đã tạo
    ├── ARCHITECTURE_REVIEW.md    ← Kết quả Phase 0.5
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

## Request Flow (Detailed)

### Simple Flow (single skill)
```
User: "viết bài Facebook giới thiệu tool"
  → [GoClaw receives Telegram message, loads context]
  → Manager (reads INTENT_ANALYZER.md):
       intent = "write_post", params = { topic: "tool" }
  → Manager (reads PLANNER.md):
       plan = [{ skill: "viet-bai-facebook", input: {...} }]
  → Manager (reads TASK_SCHEMA.md):
       task_001 = { id, status: "todo", worker: "viet-bai-fb", ... }
  → Manager (reads ROUTING_TABLE.yaml):
       "write_post" → "viet-bai-fb"
  → Manager (reads DISPATCHER.md):
       @viet-bai-fb in group chat with task details
  → [GoClaw routes @mention to Cây Bút]
  → Cây Bút (reads SKILL.md):
       executes → caption written
  → Cây Bút: updates task_001 status to "done"
  → Manager (reads RESULT_AGGREGATOR.md):
       single result → pass through
  → Manager (reads RESPONSE_BUILDER.md):
       formats caption in brand voice
  → [GoClaw sends response via Telegram]
```

### Complex Flow (multi-skill team)
```
User: "làm bài đăng Facebook về sản phẩm mới"
  → Manager: intent = "create_campaign_content"
  → Manager (reads planner): plan = [
      { id: 0, skill: "viet-bai-facebook" },
      { id: 1, skill: "sang-tao-creative-fb", depends_on: [0] }
    ]
  → task_001 → TODO (viet-bai-fb)
  → task_002 → BLOCKED (waiting for task_001)
  → Dispatcher: @viet-bai-fb with task_001
  → Cây Bút writes caption → task_001 → DONE
  → Manager sees task_001 done → unblocks task_002
  → task_002 → TODO → @tao-anh
  → Tạo Ảnh creates image + pairs with caption → task_002 → DONE
  → Manager.ResultAggregator: merge caption + image
  → Manager.ResponseBuilder: format
  → Telegram: send paired output
```

---

## Framework vs GoClaw: What We Build vs What We Use

| Feature | GoClaw Provides | Framework Builds | File |
|---------|----------------|-----------------|------|
| Telegram | ✅ Message routing | ❌ | goclaw.yml |
| Context loading | ✅ *.md auto-loaded | ❌ | agent/*, knowledge/* |
| Skill execution | ✅ use_skill | ❌ | skills/*/SKILL.md |
| Multi-agent dispatch | ✅ @agentId in group | ❌ | goclaw.yml |
| Session memory | ✅ Short-term | ❌ | GoClaw internal |
| Monitoring | ✅ MCP heartbeat | ❌ | HEARTBEAT.md |
| Intent Analysis | ❌ | ✅ Rule-based | INTENT_ANALYZER.md |
| Planning | ❌ | ✅ Decision tree | PLANNER.md |
| Task Management | ❌ | ✅ JSON + Kanban | TASK_SCHEMA.md |
| Dynamic Routing | ❌ (static goclaw.yml) | ✅ Config-driven YAML | ROUTING_TABLE.yaml |
| Dispatcher | ❌ | ✅ Instructions | DISPATCHER.md |
| Result Aggregation | ❌ | ✅ Merge rules | RESULT_AGGREGATOR.md |
| Response Builder | ❌ | ✅ Brand voice format | RESPONSE_BUILDER.md |
| Retry Manager | ❌ | ✅ Policy | RETRY_POLICY.md |
| Context Assembly | ❌ | ✅ Minimal context per worker | CONTEXT_ASSEMBLER.md |
| Context Contract | ❌ | ✅ Structured context between Manager/Worker | CONTEXT_CONTRACT.md |
| Prompt Assembly | ❌ | ✅ Role + Task + Context + Constraints | PROMPT_ASSEMBLY.md |
| Short-term Memory | ✅ In-session | ❌ | GoClaw internal |
| Session Memory | ❌ | ✅ File-based per session | SESSION_MEMORY.md |
| Long-term Memory | ❌ | ✅ File-based persistent | LONG_TERM_MEMORY.md |
| Task History | ❌ | ✅ Execution log for debugging | TASK_HISTORY.md |

---

## Template for New Projects (Phase 5)

```
Framework = core/ + docs/     ← GIỮ NGUYÊN cho mọi dự án
Business   = agent/ + knowledge/ + skills/ + goclaw.yml  ← THAY ĐỔI theo dự án

Để tạo dự án mới:
1. Copy core/ và docs/
2. Xóa agent/, knowledge/, skills/
3. Viết mới: brand voice, knowledge, skills, goclaw.yml, WORKER_REGISTRY.yaml
4. Không sửa core/
```

---

## Existing System Compatibility

| Existing Component | Status | Why |
|-------------------|--------|-----|
| `goclaw.yml` | ✅ GIỮ NGUYÊN | GoClaw runtime — không đụng |
| `agent/AGENTS.md` | ✅ APPEND sections | Không sửa existing, chỉ thêm |
| `agent/SOUL.md` | ✅ GIỮ NGUYÊN | Brand identity |
| `agent/USER.md` | ✅ GIỮ NGUYÊN | User profile |
| `agent/viet-bai-fb/` | ✅ APPEND Task contract | Thêm section mới |
| `agent/tao-anh/` | ✅ APPEND Task contract | Thêm section mới |
| `agent/lam-video/` | ✅ APPEND Task contract | Thêm section mới |
| `knowledge/*.md` | ✅ GIỮ NGUYÊN | Single source of truth |
| `skills/*/SKILL.md` | ✅ APPEND Task status | Thêm section mới |
| `skills/*/assets/` | ✅ GIỮ NGUYÊN | Skill templates |
| `skills/*/scripts/` | ✅ GIỮ NGUYÊN | Execution scripts |
| Telegram flows | ✅ GIỮ NGUYÊN | Preserved as-is |

---

## Key Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Framework = markdown instructions, not code | Repo này là GoClaw config. Framework là conventions cho Claude Code. |
| Không viết lại GoClaw features | Tận dụng Telegram, skill execution, context loading. Chỉ xây phần thiếu. |
| Task dùng file-based storage | Không cần database; dễ backup; migrate sau nếu cần. |
| Routing = YAML config | Config-driven, không hardcode, dễ mở rộng. |
| Intent Analysis = rule-based | Đơn giản, đủ dùng, không cần ML. |
| Planner = decision tree markdown | Đủ cho số lượng intent giới hạn. |
| Event Bus = Phase sau | Tránh over-engineering. |
| Context = assembled per task | Worker chỉ nhận đúng context cần thiết, không dump toàn bộ knowledge. |
| Memory = file-based, layered | Short-term (in-memory), Session (file), Long-term (file), KB (static). |
| Prompt Assembly = Manager's job | Manager ghép prompt cuối cùng. Worker không tự assemble context. |

## Coding Standards

1. **Read before write** — Always read existing files before modifying
2. **No hardcoding** — Every configurable value lives in a config file
3. **Backward compatibility** — Never break existing flows; only append sections
4. **Single responsibility** — Each core/*.md file covers one concern
5. **No cross-skill coupling** — Skills never import or call each other
6. **No rebuilding GoClaw** — If GoClaw has it, use it. Don't rewrite.
7. **Document first** — Architecture docs before implementation
8. **Test after every phase** — Unit → Integration → Smoke → Regression

---

## Deployment Model

```
GitHub (congsang1294/goclaw-agent)
    │  git push
    ▼
VPS (Docker)
    ├── ga-trong-tre-docker     # Main workspace — all skills
    ├── viet-bai-fb-docker      # FB writing workspace
    ├── tao-anh-docker          # Image design workspace
    └── lam-video-docker        # Video production workspace
```

Each Docker container runs:
- GoClaw agent runtime
- Assigned skills + scripts
- Python environment for script execution

---

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 0** | Documentation & Architecture | ✅ Complete |
| **Phase 0.5** | Architecture Review | ✅ Complete |
| **Phase 1** | Core Framework (markdown instructions) | ✅ Complete |
| **Phase 2** | Worker Integration (config-driven, N Workers) | ✅ Complete |
| **Phase 3** | Memory & Context Layer | 🔄 In Progress |
| **Phase 4** | Testing & Hardening | ⏳ |
| **Phase 5** | Project Template & Docs | ⏳ |

---

*This document is the single source of truth for system architecture. All changes must be reflected here.*
