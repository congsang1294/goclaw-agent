# AI Team Framework — Specification

> **File:** `FRAMEWORK_SPEC.md`
> **Version:** 1.0.0
> **Status:** CURRENT
> **Last Updated:** 2026-07-09
> **Scope:** This is the single source of truth for how the AI Team Framework operates.
> All components, contracts, and protocols are defined here. Read this before modifying any core/ file.

---

## Table of Contents

1. [Framework Overview](#1-framework-overview)
2. [Architecture](#2-architecture)
3. [Component Reference](#3-component-reference)
4. [Contracts](#4-contracts)
5. [Protocols](#5-protocols)
6. [Configuration Reference](#6-configuration-reference)
7. [Context System](#7-context-system)
8. [Memory System](#8-memory-system)
9. [Prompt Assembly](#9-prompt-assembly)
10. [File Structure](#10-file-structure)
11. [Extension Guide](#11-extension-guide)
12. [Glossary](#12-glossary)

---

## 1. Framework Overview

### 1.1 What It Is

The AI Team Framework turns a single AI agent into a multi-agent team with:
- A **Manager** that plans and delegates
- **Workers** that execute specialized skills
- A **Task/Kanban** system for tracking work
- A **Context System** for assembling minimal context per worker
- A **Memory System** for persistence across sessions
- A **Prompt Assembly** for constructing final prompts

### 1.2 What It Is Not

- ❌ NOT a code runtime — it's markdown instructions + conventions
- ❌ NOT replacing GoClaw — it extends what GoClaw doesn't have
- ❌ NOT a database — it uses file-based storage

### 1.3 Design Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Task is the center** | Every unit of work is a Task. Agents communicate through Tasks. |
| 2 | **Manager routes, Workers execute** | Manager plans and delegates. Workers only execute skills. |
| 3 | **Routing is dynamic + config-driven** | Intent → Route → Worker via YAML config. No hardcoded workers. |
| 4 | **Skills are plugins** | Self-contained (trigger, input, output, context). No cross-skill coupling. |
| 5 | **Context is assembled, not dumped** | Worker gets minimal context for the Task, not the entire knowledge base. |
| 6 | **Memory is layered** | Short-term → Session → Long-term → Knowledge Base. Each has explicit rules. |
| 7 | **No agent-to-agent calls** | Only Manager → Worker through Tasks via `@agentId`. |
| 8 | **Backward compatibility** | Existing Telegram flows, Skills, Knowledge files keep working. |
| 9 | **Framework = instructions + conventions** | Markdown files + YAML config. No code runtime. |

### 1.4 GoClaw Boundary

| Layer | What | Files | Rule |
|-------|------|-------|------|
| **GoClaw Runtime** | Telegram, @agentId, use_skill, context loading, heartbeat | `goclaw.yml`, `agent/*.md`, `knowledge/*.md` | 🚫 DO NOT MODIFY |
| **Framework Core** | Manager, Router, Kanban, Worker, Context, Memory | `core/**/*` | ✅ BUILD NEW |
| **Business Config** | Brand voice, products, agents, skills | `knowledge/*`, `agent/`, `skills/`, `goclaw.yml` | ✅ CUSTOMIZE PER PROJECT |

### 1.5 Framework vs GoClaw

| Feature | GoClaw Provides | Framework Builds |
|---------|----------------|-----------------|
| Telegram routing | ✅ | ❌ |
| Context loading (`*.md`) | ✅ | ❌ |
| Skill execution (`use_skill`) | ✅ | ❌ |
| Multi-agent dispatch (`@agentId`) | ✅ | ❌ |
| Session memory (short-term) | ✅ | ❌ |
| Heartbeat monitoring | ✅ | ❌ |
| Intent Analysis | ❌ | ✅ (INTENT_ANALYZER.md) |
| Planning | ❌ | ✅ (PLANNER.md) |
| Task Management | ❌ | ✅ (TASK_SCHEMA.md, KANBAN_BOARD.md) |
| Dynamic Routing | ❌ | ✅ (ROUTING_TABLE.yaml) |
| Dispatcher | ❌ | ✅ (DISPATCHER.md) |
| Result Aggregation | ❌ | ✅ (RESULT_AGGREGATOR.md) |
| Response Builder | ❌ | ✅ (RESPONSE_BUILDER.md) |
| Retry Manager | ❌ | ✅ (RETRY_POLICY.md) |
| Worker Registry | ❌ | ✅ (WORKER_REGISTRY.yaml) |
| Context Assembly | ❌ | ✅ (CONTEXT_ASSEMBLER.md) |
| Context Contract | ❌ | ✅ (CONTEXT_CONTRACT.md) |
| Prompt Assembly | ❌ | ✅ (PROMPT_ASSEMBLY.md) |
| Session Memory | ❌ | ✅ (SESSION_MEMORY.md) |
| Long-term Memory | ❌ | ✅ (LONG_TERM_MEMORY.md) |
| Task History | ❌ | ✅ (TASK_HISTORY.md) |

---

## 2. Architecture

### 2.1 High-Level System Diagram

```
Telegram (User / Anh Sáng)
    │  [GoClaw: message routing]
    ▼
┌──────────────────────────────────────────────────────────┐
│                    MANAGER                                 │
│                                                           │
│  0. Init: WorkerRegistry → biết N workers                 │
│  1. IntentAnalyzer → intent                               │
│  2. Router → worker, skill, timeout                       │
│  3. Planner → plan (N tasks, dependency graph)            │
│  4. ContextAssembler → minimal context per worker         │
│  5. PromptAssembly → final prompt (role+task+ctx+constraints)
│  6. TaskCreator → Kanban enqueue                          │
│  7. Dispatcher → @workerId in group chat                  │
│  8. Monitor: Kanban + RetryManager                        │
│  9. ResultAggregator → merge outputs                      │
│  10. ResponseBuilder → brand voice format                 │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                 DYNAMIC ROUTER                             │
│  ROUTING_TABLE.yaml: intent → worker                      │
│  WORKER_REGISTRY.yaml: worker metadata                    │
└──────────────────────┬───────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐     ┌──────▼──────┐     ┌─────▼───────┐
│ Cây Bút │     │ Tạo Ảnh    │     │ Làm Video   │
│ Worker  │     │ Worker     │     │ Worker      │
└────────┘     └─────────────┘     └─────────────┘
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                    SKILLS ENGINE                           │
│  (GoClaw: use_skill, SKILL.md, scripts/*.py)              │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Request Flow: Simple

```
User: "viết bài Facebook giới thiệu tool"
  1. GoClaw nhận Telegram, load context
  2. Manager: INTENT_ANALYZER → write_post
  3. Manager: ROUTING_TABLE → viet-bai-fb + viet-bai-facebook
  4. Manager: PLANNER → 1 task (simple)
  5. Manager: ContextAssembler → { agent, user, task, brand_voice }
  6. Manager: PromptAssembly → System+Role+Task+Context+Constraints+Output
  7. Manager: TASK_SCHEMA → task_001 → KANBAN → TODO
  8. Manager: DISPATCHER → @viet-bai-fb [TASK: task_001] ...
  9. Worker: nhận task → in_progress → execute skill → done
  10. Manager: RESULT_AGGREGATOR → pass through
  11. Manager: RESPONSE_BUILDER → brand voice → Telegram
```

### 2.3 Request Flow: Complex (multi-worker)

```
User: "cả team làm bài về sản phẩm mới"
  1. Manager: INTENT_ANALYZER → team_sync
  2. Manager: PLANNER → 3 tasks:
     task_A: viet-bai-fb (depends_on: [])
     task_B: tao-anh (depends_on: [task_A])
     task_C: lam-video (depends_on: [task_B])
  3. task_A → TODO, task_B → BLOCKED, task_C → BLOCKED
  4. Dispatcher: @viet-bai-fb with task_A
  5. Cây Bút → caption → task_A → DONE
  6. Manager unblocks task_B → TODO
  7. Dispatcher: @tao-anh with task_B (có context từ task_A)
  8. Tạo Ảnh → image → task_B → DONE
  9. Manager unblocks task_C → TODO
  10. Dispatcher: @lam-video with task_C (có context từ A+B)
  11. Làm Video → video → task_C → DONE
  12. Manager: RESULT_AGGREGATOR → merge 3 outputs
  13. Manager: RESPONSE_BUILDER → format → Telegram
```

---

## 3. Component Reference

### 3.1 Manager (Gà Trống Tre)

| Aspect | Detail |
|--------|--------|
| **Agent ID** | `ga-trong-tre` |
| **Role** | Orchestrator — does NOT execute skills |
| **Definition** | `agent/AGENTS.md` + `core/manager/*.md` |
| **Soul** | `agent/SOUL.md` |
| **Telegram** | Direct message with owner (ID: 6880126421) |

**Responsibilities:**
1. Read WORKER_REGISTRY.yaml at session init (N workers, skills, bindings)
2. Analyze intent via INTENT_ANALYZER.md
3. Route intent via ROUTING_TABLE.yaml
4. Plan via PLANNER.md (simple/multi-step/complex)
5. Assemble context via CONTEXT_ASSEMBLER.md (minimal per worker)
6. Assemble prompt via PROMPT_ASSEMBLY.md (role+task+context+constraints)
7. Create tasks via TASK_SCHEMA.md
8. Enqueue to KANBAN_BOARD.md
9. Dispatch via DISPATCHER.md
10. Monitor via KANBAN + RETRY_POLICY.md
11. Aggregate via RESULT_AGGREGATOR.md
12. Respond via RESPONSE_BUILDER.md
13. Log memory: SESSION_MEMORY.md → TASK_HISTORY.md

### 3.2 Workers

Workers are specialized agents. Each has exactly one role, one or more Skills.

| Worker | ID | Skills | Input | Output | Timeout |
|--------|-----|--------|-------|--------|---------|
| **Cây Bút** | `viet-bai-fb` | `viet-bai-facebook` | Topic + brief | 3 ideas OR full caption | 120s |
| **Tạo Ảnh** | `tao-anh` | `sang-tao-creative-fb`, `viet-bai-facebook` | Caption + concept | Image + paired caption | 300s |
| **Làm Video** | `lam-video` | `tao-video-ai` | Caption + images | MP4 video | 600s |

**Worker Contract (REQUIRED for every Worker):**
- Receive Task from Manager only (via `@agentId` in group)
- Read Task Contract from own `agent/<id>/AGENTS.md`
- Execute Skill according to SKILL.md
- Update Task status: `in_progress` → `done` / `failed`
- Return structured output (JSON, not raw text)
- Never call another Worker or create Tasks
- Never format the response — Manager handles that

### 3.3 Dynamic Router

| Aspect | Detail |
|--------|--------|
| **Config** | `core/router/ROUTING_TABLE.yaml` |
| **Rules** | `core/router/ROUTING_RULES.md` |
| **Logic** | Intent → lookup in ROUTING_TABLE → { worker, skill, timeout } |

**Route entry schema:**
```yaml
- id: <unique_route_id>
  intents: [<intent_name>]        # From INTENT_ANALYZER intent catalog
  worker: <worker_id>             # Agent ID (or "manager" for self-handling)
  skill: <skill_name>             # Must have SKILL.md
  timeout: <seconds>              # Max execution time
  plan_type: simple | multi_step | complex
```

**Validation rules:**
- `worker` must exist in WORKER_REGISTRY.yaml
- `skill` must have `skills/<skill-name>/SKILL.md`
- `timeout` > 0 (default 120s)
- `intent` should be in INTENT_ANALYZER.md intent catalog

### 3.4 Kanban / Task System

| Aspect | Detail |
|--------|--------|
| **Schema** | `core/kanban/TASK_SCHEMA.md` |
| **Board** | `core/kanban/KANBAN_BOARD.md` |
| **Lifecycle** | `core/kanban/TASK_LIFECYCLE.md` |

**Task schema:**
```json
{
  "id": "task_YYYYMMDD_NNN",
  "type": "skill_execution | approval | notification",
  "status": "created | todo | in_progress | done | failed | retrying | blocked | cancelled",
  "priority": "low | normal | high | critical",
  "worker": "viet-bai-fb",
  "skill": "viet-bai-facebook",
  "input": { "topic": "..." },
  "output": null | { "caption": "..." },
  "error": null | "timeout after 120s",
  "attempts": 1,
  "max_retries": 3,
  "parent_task": null | "task_001",
  "depends_on": ["task_000"],
  "created_at": "2026-07-09T10:00:00+07:00",
  "updated_at": "2026-07-09T10:00:00+07:00",
  "assigned_at": null,
  "completed_at": null
}
```

**Status transitions:**
```
created → todo → in_progress → done
                → failed → retrying → todo → in_progress → done
                → cancelled
      → blocked (waiting on dependency) → todo (unblocked)
```

### 3.5 Skills Engine

| Aspect | Detail |
|--------|--------|
| **Location** | `skills/<skill-name>/` |
| **Entry point** | `skills/<skill-name>/SKILL.md` |
| **Assets** | `skills/<skill-name>/assets/` (optional) |
| **Scripts** | `skills/<skill-name>/scripts/` (optional) |

**SKILL.md required sections:**
```markdown
# Skill: <Name>
## Triggers
## Inputs
## Output
## Steps
## Dependencies
## Guardrails
## Context Sources
## Task Status Management  (if used by a Worker)
```

### 3.6 Retry Manager

| Aspect | Detail |
|--------|--------|
| **Policy** | `core/retry/RETRY_POLICY.md` |
| **Max retries** | 3 (default) |
| **Backoff** | 5s → 10s → 20s (exponential, ±1s jitter) |

**Retryable errors:** API timeout, rate limit, network error, script crash
**Non-retryable errors:** Invalid input, permission denied, missing file, schema validation fail

---

## 4. Contracts

### 4.1 Task Contract (Worker → Manager)

Defined in each Worker's `agent/<worker-id>/AGENTS.md`. Specifies:

| Aspect | Detail |
|--------|--------|
| **Receive** | Worker reads task from `@agentId` mention in group |
| **Status** | Worker self-reports: `in_progress` | `done` | `failed` |
| **Output** | Structured JSON with `{ status, output, error }` |
| **Error** | Worker reports error details for retry decision |

**Contract rules:**
- ✅ Worker may ask Manager 1 clarifying question (still `in_progress`)
- ✅ Worker may report technical errors
- ❌ Worker must NOT create new Tasks
- ❌ Worker must NOT assign Tasks to other Workers
- ❌ Worker must NOT modify task ID or status fields

### 4.2 Context Contract (Manager → Worker)

**What Worker receives:**
```json
{
  "context": {
    "agent": {
      "name": "Cây Bút",
      "id": "viet-bai-fb",
      "role": "Facebook Content Writer",
      "soul_ref": "agent/viet-bai-fb/SOUL.md"
    },
    "user": {
      "name": "anh Sáng",
      "id": "6880126421",
      "preferences": "short, direct, no corporate"
    },
    "task": {
      "id": "task_20260709_001",
      "input": { "topic": "giới thiệu tool" },
      "depends_on": []
    },
    "knowledge": {
      "brand_voice": "knowledge/brand-voice.md",
      "product_info": "knowledge/knowledge-base.md"
    },
    "session": {
      "conversation_summary": "User asked about writing a post...",
      "turn_count": 3
    }
  }
}
```

### 4.3 Worker Contract (Framework → Worker)

Every Worker MUST:
1. Have `agent/<worker-id>/AGENTS.md` with role + task contract
2. Have `agent/<worker-id>/SOUL.md` with identity + tone
3. Be registered in `core/worker/WORKER_REGISTRY.yaml`
4. Have at least one Skill in `skills/<skill-name>/SKILL.md`
5. Be routable via `core/router/ROUTING_TABLE.yaml`
6. Be bindable in `goclaw.yml` (Telegram group, if needed)

---

## 5. Protocols

### 5.1 Dispatch Protocol

```
Manager → Worker:
  1. Manager reads task from Kanban TODO column
  2. Manager reads WORKER_REGISTRY.yaml for worker metadata
  3. Manager assembles context via CONTEXT_ASSEMBLER.md
  4. Manager assembles prompt via PROMPT_ASSEMBLY.md
  5. Manager sends @workerId in group chat with task + context
  6. Manager updates task → IN_PROGRESS, assigned_at = now
  7. Worker receives, acknowledges, starts executing

Format: @workerId [TASK: task_id] {description}\nContext: {context_json}
```

### 5.2 Status Protocol

```
Worker → Manager (status updates):
  in_progress: "Em nhận task [id], đang xử lý..."
  done:        "Xong rồi. Output: {json}"
  failed:      "Lỗi: {error_message}"

Manager reads status from Worker's reply text.
Pattern: keyword at start of message:
  "[in_progress]" → status = in_progress
  "[done]"        → status = done, read output
  "[failed]"      → status = failed, read error
```

### 5.3 Error Protocol

```
1. Worker encounters error → reports [failed] + error message
2. Manager reads RETRY_POLICY.md:
   a. If retryable + attempts < max_retries → retry
   b. If not retryable → keep FAILED, notify user
   c. If max retries reached → keep FAILED, notify user
3. For fatal errors (no retry):
   Manager decides: cancel workflow OR continue with partial results
4. For dependency failures:
   Cancel all dependent tasks → notify user
```

### 5.4 Heartbeat Protocol

```
Every heartbeat tick:
  1. Call MCP get_success_order_signal
  2. Call MCP get_new_lead_signal
  3. If new order → notify anh Sáng (brand voice)
  4. If new lead → notify anh Sáng (brand voice)
  5. If both → combine into one message
  6. If nothing → silence (no spam)
```

---

## 6. Configuration Reference

### 6.1 WORKER_REGISTRY.yaml

```yaml
# Single source of truth for Workers
workers:
  - id: <agent_id>
    name: "<display_name>"
    role: "<role_description>"
    status: active | inactive | planned
    telegram:
      binding: group | direct | none
      mention: "@<agent_id>"
    skills:
      - <skill_name>
    dispatch_to: "@<agent_id> in group chat"
    input_format: "<what worker needs>"
    output_format: "<what worker returns>"
    timeout: <seconds>
    restrictions:
      - "❌ <restriction>"
```

**Adding a Worker (5 steps):**
1. Add entry to WORKER_REGISTRY.yaml
2. Create `agent/<worker-id>/AGENTS.md` (role + task contract)
3. Create `agent/<worker-id>/SOUL.md` (identity + tone)
4. Create/use `skills/<skill-name>/SKILL.md`
5. Add route to ROUTING_TABLE.yaml

### 6.2 ROUTING_TABLE.yaml

```yaml
routes:
  - id: <route_id>
    intents: [<intent_name>]
    worker: <worker_id_or_manager>
    skill: <skill_name_or_orchestration>
    timeout: <seconds>
    plan_type: simple | multi_step | complex
```

**Special worker values:**
- `manager` → Manager self-handles (approve, cancel, check_status, answer_faq, unknown)
- FAQ route uses `tra-loi-faq-khach-hang` skill (manager handles directly)
- Unknown intent uses `orchestration` skill (manager asks for clarification)

### 6.3 goclaw.yml (GoClaw Runtime — DO NOT EDIT LIGHTLY)

```yaml
agent:
  name: "<agent_name>"
  id: <agent_id>
  owners:
    - user_id: "<telegram_id>"
  workstations:
    - name: <workspace_name>
      skills: [<skill_list>]
  bindings:
    - agentId: <worker_id>
      match:
        channel: telegram
        peer:
          kind: group | direct
```

---

## 7. Context System

### 7.1 Seven Context Types

| # | Context | Source | Scope | When Assembled |
|---|---------|--------|-------|----------------|
| 1 | **System** | `FRAMEWORK_SPEC.md`, `core/*`, `CLAUDE.md` | Global rules, contracts | Session start (once) |
| 2 | **Project** | `goclaw.yml`, `ARCHITECT.md`, `README.md` | Project config, deployment | Session start (once) |
| 3 | **Agent** | `agent/<id>/SOUL.md`, `agent/<id>/AGENTS.md` | Per-agent identity | Agent activation |
| 4 | **User** | `agent/USER.md`, `knowledge/my-business.md` | User profile, preferences | User message received |
| 5 | **Task** | Task schema + Kanban state | Current task + dependencies | Task dispatch |
| 6 | **Session** | `memory/sessions/session_YYYY-MM-DD.json` | Current conversation turns | Per turn |
| 7 | **Runtime** | MCP signals, heartbeat | Real-time business data | When available |

### 7.2 Context Assembly Pipeline

```
User Message
  │
  ├── 1. Load System Context ──────────────── once per session
  │     FRAMEWORK_SPEC.md → core rules, behavior constraints
  │
  ├── 2. Load Project Context ─────────────── once per session  
  │     ARCHITECT.md → architecture, key decisions
  │     goclaw.yml → runtime config
  │
  ├── 3. Load Agent Context ───────────────── per manager activation
  │     agent/SOUL.md → identity, voice
  │     agent/AGENTS.md → orchestration rules
  │     agent/HEARTBEAT.md → monitoring rules
  │
  ├── 4. Load User Context ────────────────── per user message
  │     agent/USER.md → owner profile
  │     knowledge/my-business.md → business info (filtered)
  │
  ├── 5. Load Session Context ─────────────── per turn
  │     memory/sessions/session_*.json → conversation history
  │
  ├── 6. Create Task Context ──────────────── per task dispatch
  │     Task schema → id, input, dependencies
  │
  ├── 7. Attach Runtime Context ───────────── if available
  │     MCP signals → orders, leads
  │
  ├── 8. FILTER ────────────────────────────── KEY STEP
  │     Chỉ giữ context cần thiết cho Worker:
  │     - Cây Bút: brand_voice + task.input + user.prefs
  │     - Tạo Ảnh: image concept + paired caption + brand reference
  │     - Làm Video: caption + images + video specs
  │     BỎ: irrelevant knowledge, other workers' context
  │
  ├── 9. Package into Context Contract ─────── per worker
  │     → core/context/CONTEXT_CONTRACT.md format
  │
  └── 10. Dispatch to Worker ───────────────── with task
```

### 7.3 Context Assembly Rules

| Rule | Detail |
|------|--------|
| **Minimal** | Worker only gets what it needs. No full-knowledge dump. |
| **No duplication** | Every context lives in exactly one place. Reference by path, not copy. |
| **Filter first** | Before packaging, remove irrelevant sections per worker type. |
| **Session > Static** | Session context overrides static context when both exist. |
| **Fresh per dispatch** | Context is reassembled for each Task, not cached. |

### 7.4 Context Contract

The structured JSON every Worker receives (see [§4.2 Context Contract](#42-context-contract-manager--worker)).

---

## 8. Memory System

### 8.1 Four Memory Layers

| Layer | Storage | Format | Duration | Read | Write | Delete | Summarize |
|-------|---------|--------|----------|------|-------|--------|-----------|
| **Short-term** | In-memory (GoClaw) | — | Per conversation turn | Every turn | Every turn | Auto on turn end | Never |
| **Session** | `memory/sessions/session_YYYY-MM-DD.json` | JSON | Per session (one file per day) | Session start | On task events, milestone | Session end | Session end → long-term |
| **Long-term** | `memory/long-term/task_history.log` | Text/JSON append | Persistent | Before planning, on resume | On milestone, on session end | Never (only archive) | Weekly or every 1000 entries |
| **Knowledge Base** | `knowledge/*.md` | Markdown | Permanent (static) | Every session | Manual edits | Never | Never |

### 8.2 Memory Read Rules

| When | What to Read | Source |
|------|-------------|--------|
| Session start | Yesterday's session (if exists) | `memory/sessions/session_YYYY-MM-DD.json` |
| Session start | Long-term task history (summary) | `memory/long-term/task_history.log` |
| Before planning | Active tasks from Kanban | `memory/sessions/session_*.json` |
| Before dispatch | Worker-specific history | `memory/long-term/` filtered by worker |
| Every turn | Current session state | In-memory / session file |
| On resume | Last session state | `memory/sessions/` most recent |

### 8.3 Memory Write Rules

| When | What to Write | Target |
|------|-------------|--------|
| Task created | Append task to session | `memory/sessions/session_*.json` |
| Task status changed | Update task in session | `memory/sessions/session_*.json` |
| Task completed | Append to task history | `memory/long-term/task_history.log` |
| Worker done | Log output + duration | `memory/long-term/task_history.log` |
| Error/failure | Log error + retry | `memory/long-term/task_history.log` |
| Session end | Summarize session | `memory/long-term/` (summary entry) |
| Milestone (order, lead) | Log immediately | `memory/long-term/task_history.log` |

### 8.4 Memory Delete Rules

| When | What to Delete | Why |
|------|---------------|-----|
| Turn end | Short-term (auto) | Free context |
| Session end | Session file | Fresh start next day |
| Never | Long-term | Archive instead |
| Never | Knowledge Base | Manual edits only |

### 8.5 Memory Summarize Rules

| Trigger | Action | Target |
|---------|--------|--------|
| Session end | Compress session → 1 summary entry | `memory/long-term/` |
| Every 1000 task history entries | Compress oldest 500 → 1 summary | `memory/long-term/task_history.log` |
| Weekly (triggered by user or cron) | Archive old task history | `memory/archives/` |

---

## 9. Prompt Assembly

### 9.1 Assembly Pipeline

```
Manager assembles final prompt before dispatch:

PROMPT = SYS + ROLE + TASK + CTX + KNOW + CONST + OUT

Where:
  SYS    = System Prompt ─── from FRAMEWORK_SPEC.md (core rules, behavior)
  ROLE   = Agent Role ────── from agent/<id>/SOUL.md + AGENTS.md
  TASK   = Task ──────────── from Task schema (what to do, input params)
  CTX    = Context ───────── from Context Assembler (filtered minimal)
  KNOW   = Knowledge ─────── from knowledge/*.md (filtered per worker)
  CONST  = Constraints ───── from Task Contract + SKILL.md guardrails
  OUT    = Output Format ─── from Task Contract + Worker AGENTS.md
```

### 9.2 Assembly Steps

```
Step 1: SYSTEM ─────────────────────────────────────────────────
  Read FRAMEWORK_SPEC.md sections 1-5 (core rules, contracts)
  Include: golden rules, backward compatibility, no agent-to-agent
  Skip: project-specific sections

Step 2: ROLE ───────────────────────────────────────────────────
  Read agent/<worker-id>/SOUL.md (identity, tone, voice)
  Read agent/<worker-id>/AGENTS.md (role, skills, restrictions)
  Include: who the worker is, how they talk, what they do

Step 3: TASK ───────────────────────────────────────────────────
  From current task in Kanban:
  - task_id, worker, skill
  - input parameters (topic, tone, format)
  - dependencies (if any)

Step 4: CONTEXT ────────────────────────────────────────────────
  From Context Assembler (filtered per worker):
  - agent info (name, id)
  - user info (name, preferences)
  - task context (conversation summary)
  - Skip: irrelevant knowledge sections

Step 5: KNOWLEDGE ──────────────────────────────────────────────
  Filtered by worker type:
  - Cây Bút: brand-voice.md (full), knowledge-base.md (relevant)
  - Tạo Ảnh: brand-voice.md (tone only), image templates
  - Làm Video: brand-style.md, camera-prompts.md
  - Skip: unrelated product info

Step 6: CONSTRAINTS ────────────────────────────────────────────
  From Task Contract:
  - What worker MUST NOT do
  - Guardrails from SKILL.md
  - Restrictions from WORKER_REGISTRY.yaml

Step 7: OUTPUT FORMAT ──────────────────────────────────────────
  From Task Contract + Worker AGENTS.md:
  - Expected output schema (JSON format)
  - Status fields required
  - Error format if failed
```

### 9.3 Assembly Result

```markdown
--- SYSTEM ---
[Core framework rules from FRAMEWORK_SPEC.md]

--- ROLE ---
Bạn là Cây Bút — người viết content Facebook cho team sản xuất nội dung.
Bạn chỉ viết content. Bạn không tạo ảnh, không làm video, không tạo task.

--- TASK ---
Task ID: task_20260709_001
Worker: viet-bai-fb
Skill: viet-bai-facebook
Input: { topic: "giới thiệu tool", tone: "brand_voice" }

--- CONTEXT ---
User: anh Sáng — thích nói thẳng, ngắn gọn, không corporate.
Conversation: User mới hỏi về việc viết bài giới thiệu tool...

--- KNOWLEDGE ---
Brand Voice: Viết như người đã làm thật, sai thật, mất tiền thật...
Product: Google Ads Match Type Converter...

--- CONSTRAINTS ---
- Không tự tạo task mới
- Không gọi worker khác
- Không hứa kết quả ads

--- OUTPUT FORMAT ---
{ "status": "done", "output": { "caption": "..." } }
```

---

## 10. File Structure

```
goclaw-agent/                          # Project root
│
├── goclaw.yml                         # 🚫 GoClaw runtime — DO NOT MODIFY
├── ARCHITECT.md                       # 🏛️ Architecture reference
├── CLAUDE.md                          # 📖 Rule book
├── FRAMEWORK_SPEC.md                  # 📗 THIS FILE — framework specification
├── README.md                          # Quick start
│
├── agent/                             # 📋 Agent definitions
│   ├── AGENTS.md                      # Manager orchestration
│   ├── SOUL.md                        # Manager identity
│   ├── USER.md                        # Owner profile
│   ├── HEARTBEAT.md                   # Monitoring rules
│   ├── CAPABILITIES.md                # What Manager can do
│   ├── IDENTITY.md                    # Manager persona
│   ├── viet-bai-fb/                   # Worker: Cây Bút
│   │   ├── AGENTS.md                  #   Role + Task Contract
│   │   └── SOUL.md                    #   Identity
│   ├── tao-anh/                       # Worker: Tạo Ảnh
│   │   ├── AGENTS.md                  #   Role + Task Contract
│   │   └── SOUL.md                    #   Identity
│   └── lam-video/                     # Worker: Làm Video
│       ├── AGENTS.md                  #   Role + Task Contract
│       └── SOUL.md                    #   Identity
│
├── knowledge/                         # 🧠 Shared knowledge (single truth)
│   ├── brand-voice.md
│   ├── knowledge-base.md
│   └── my-business.md
│
├── skills/                            # 🔌 Skills Engine
│   ├── viet-bai-facebook/             # Skill: Facebook writing
│   ├── sang-tao-creative-fb/          # Skill: Image + caption
│   ├── tao-video-ai/                  # Skill: Video production
│   ├── agent-scout/                   # Skill: Web research
│   └── tra-loi-faq-khach-hang/        # Skill: FAQ support
│
├── core/                              # 🏗️ Framework Core
│   ├── manager/                       # Manager components
│   │   ├── INTENT_ANALYZER.md
│   │   ├── PLANNER.md
│   │   ├── ORCHESTRATION.md
│   │   ├── RESULT_AGGREGATOR.md
│   │   └── RESPONSE_BUILDER.md
│   ├── router/                        # Dynamic Router
│   │   ├── ROUTING_TABLE.yaml
│   │   └── ROUTING_RULES.md
│   ├── kanban/                        # Task System
│   │   ├── TASK_SCHEMA.md
│   │   ├── KANBAN_BOARD.md
│   │   └── TASK_LIFECYCLE.md
│   ├── worker/                        # Worker Registry
│   │   ├── WORKER_REGISTRY.yaml
│   │   └── WORKER_REGISTRY.md
│   ├── dispatcher/                    # Dispatcher
│   │   └── DISPATCHER.md
│   ├── retry/                         # Retry Manager
│   │   └── RETRY_POLICY.md
│   ├── context/                       # Context System (Phase 3)
│   │   ├── CONTEXT_ASSEMBLER.md
│   │   ├── CONTEXT_CONTRACT.md
│   │   └── PROMPT_ASSEMBLY.md
│   └── memory/                        # Memory System (Phase 3)
│       ├── MEMORY_STRATEGY.md
│       ├── TASK_HISTORY.md
│       ├── SESSION_MEMORY.md
│       └── LONG_TERM_MEMORY.md
│
├── memory/                            # 💾 Runtime data
│   ├── sessions/
│   │   └── session_YYYY-MM-DD.json
│   └── long-term/
│       └── task_history.log
│
└── docs/                              # 📚 Documentation
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

## 11. Extension Guide

### 11.1 Adding a New Worker

```
5 steps — no core/ modifications needed:

Step 1: Register → WORKER_REGISTRY.yaml
Step 2: Define → agent/<id>/AGENTS.md (role + task contract)
Step 3: Identity → agent/<id>/SOUL.md (voice + personality)
Step 4: Skill → skills/<name>/SKILL.md (trigger + steps + guardrails)
Step 5: Route → ROUTING_TABLE.yaml (intent → worker)

Optional:
- goclaw.yml → workstation + Telegram binding
- Docs → AGENT_MAP.md, SKILL_MAP.md
```

### 11.2 Adding a New Skill

```
Step 1: mkdir skills/<skill-name>/
Step 2: Write SKILL.md (triggers, input, output, steps, guardrails)
Step 3: Add assets/ (templates, references)
Step 4: Add scripts/ (Python scripts, if needed)
Step 5: Register in ROUTING_TABLE.yaml with target worker
```

### 11.3 Cloning for a New Project

```
1. Copy core/ and docs/
2. Delete: agent/ (except AGENTS.md template), knowledge/, skills/
3. Write new:
   - knowledge/brand-voice.md
   - knowledge/my-business.md
   - knowledge/knowledge-base.md
   - agent/SOUL.md (new identity)
   - agent/USER.md (new owner)
   - skills/*/ (new domain skills)
   - goclaw.yml (new workspaces + bindings)
4. Update:
   - ARCHITECT.md (version, project name)
   - README.md (project description)
   - FRAMEWORK_SPEC.md (section 10 file structure)
5. Keep core/ unchanged
```

---

## 12. Glossary

| Term | Definition |
|------|------------|
| **Agent** | An AI entity with identity (SOUL.md), role (AGENTS.md), and capabilities |
| **Manager** | The orchestrator agent (Gà Trống Tre) that plans, routes, and tracks |
| **Worker** | A specialized agent that executes skills and returns results |
| **Task** | Unit of work — the only way agents communicate |
| **Kanban** | Visual board tracking task statuses (TODO → IN_PROGRESS → DONE) |
| **Skill** | A self-contained plugin (SKILL.md + optional assets/scripts) |
| **Intent** | Parsed user intention from natural language (e.g., `write_post`) |
| **Route** | Mapping from intent to worker (ROUTING_TABLE.yaml) |
| **Context** | Assembled information package sent to Worker with Task |
| **Memory** | Persisted data across sessions (short-term, session, long-term, KB) |
| **Prompt Assembly** | Manager constructs final prompt: System+Role+Task+Context+Knowledge+Constraints+Output |
| **Context Contract** | Structured JSON package: { agent, user, task, knowledge, session } |
| **Task Contract** | Worker's agreement: receive → execute → report → return |
| **GoClaw** | The underlying AI agent runtime (Telegram, @agentId, use_skill) |
| **Heartbeat** | Periodic check for business signals (orders, leads) |

---

*End of FRAMEWORK_SPEC.md — This is the single source of truth for the AI Team Framework.*
*All components, contracts, and protocols must be reflected here.*
*Clone this file with the project for new implementations.*
