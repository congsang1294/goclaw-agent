# CONTEXT ASSEMBLER

> **File:** `core/context/CONTEXT_ASSEMBLER.md`
> **Role:** Define how Manager assembles minimal context for each Worker
> **Part of:** Context System
> **Phase:** 3 — Memory & Context

---

## 1. Mục đích

Context Assembler chịu trách nhiệm **tự động assemble context tối thiểu cần thiết** cho từng Worker, tránh nạp toàn bộ knowledge.

**Nguyên tắc:** Worker chỉ nhận đúng context cần cho Task. Không dump toàn bộ knowledge/.

---

## 2. Seven Context Types

| # | Context | Source | Scope | When Assembled |
|---|---------|--------|-------|----------------|
| 1 | **System** | `FRAMEWORK_SPEC.md`, `CLAUDE.md`, `core/*` | Global rules, contracts | Session start (once) |
| 2 | **Project** | `goclaw.yml`, `ARCHITECT.md`, `README.md` | Project config, deployment | Session start (once) |
| 3 | **Agent** | `agent/SOUL.md`, `agent/AGENTS.md`, `agent/<id>/*` | Per-agent identity, role | Agent activation |
| 4 | **User** | `agent/USER.md`, `knowledge/my-business.md` | User profile, preferences | User message received |
| 5 | **Task** | Task schema + Kanban state | Current task, dependencies | Task dispatch |
| 6 | **Session** | `memory/sessions/session_*.json` | Conversation history | Per turn |
| 7 | **Runtime** | MCP signals, heartbeat | Real-time business signals | When available |

---

## 3. Assembly Pipeline

```
User Message
  │
  ├── Step 1: Load System Context ────── once per session
  │   ├── FRAMEWORK_SPEC.md → framework rules, contracts, protocols
  │   └── core/*.md → component instructions (INTENT_ANALYZER, PLANNER, etc.)
  │
  ├── Step 2: Load Project Context ───── once per session
  │   ├── ARCHITECT.md → architecture, design decisions
  │   ├── goclaw.yml → workstations, bindings
  │   └── README.md → project overview
  │
  ├── Step 3: Load Agent Context ─────── per agent
  │   ├── agent/SOUL.md → Manager identity, voice
  │   ├── agent/AGENTS.md → orchestration rules, team flow
  │   ├── agent/HEARTBEAT.md → monitoring rules
  │   └── agent/USER.md → owner authority
  │
  ├── Step 4: Load User Context ──────── per user message
  │   ├── agent/USER.md → anh Sáng's profile
  │   ├── knowledge/my-business.md → business info (filtered)
  │   └── USER_PREDEFINED.md → customer personas
  │
  ├── Step 5: Load Session Context ───── per turn
  │   ├── memory/sessions/session_*.json → active tasks, events
  │   └── In-memory → current conversation turns
  │
  ├── Step 6: Create Task Context ────── per task dispatch
  │   ├── Task schema → id, input, depends_on
  │   └── Kanban → related task statuses
  │
  ├── Step 7: Attach Runtime Context ─── if available
  │   ├── MCP signals → new orders, new leads
  │   └── Heartbeat → business metrics
  │
  ├── Step 8: FILTER ─────────────────── KEY STEP
  │   Filter context per Worker+Skill:
  │
  │   For Cây Bút (viet-bai-facebook):
  │     ✓ agent/SOUL.md (identity)
  │     ✓ agent/USER.md (anh Sáng's preferences)
  │     ✓ knowledge/brand-voice.md (FULL)
  │     ✓ task.input (topic, tone, format)
  │     ✓ session.conversation_summary
  │     ✗ knowledge/knowledge-base.md (skip — FAQ không cần)
  │     ✗ knowledge/my-business.md (skip — pricing không cần)
  │
  │   For Tạo Ảnh (sang-tao-creative-fb):
  │     ✓ agent/SOUL.md (identity)
  │     ✓ knowledge/brand-voice.md (tone only)
  │     ✓ task.input (caption, concept, style)
  │     ✓ session.conversation_summary
  │     ✗ knowledge/knowledge-base.md (skip)
  │
  │   For Làm Video (tao-video-ai):
  │     ✓ agent/SOUL.md (identity)
  │     ✓ task.input (caption, images, duration)
  │     ✓ skills/tao-video-ai/assets/* (style, camera prompts)
  │     ✗ knowledge/*.md (skip — video không cần brand voice text)
  │
  ├── Step 9: Package Context ────────── per worker
  │   → Đóng gói vào CONTEXT_CONTRACT.md format
  │
  └── Step 10: Dispatch ──────────────── with task
      → PROMPT_ASSEMBLY.md ghép prompt cuối cùng
```

---

## 4. Worker-Specific Filtering

### 4.1 Cây Bút (viet-bai-facebook)

| Include | Source | Why |
|---------|--------|-----|
| ✅ Agent identity | `agent/viet-bai-fb/SOUL.md` | Biết mình là ai |
| ✅ Agent role | `agent/viet-bai-fb/AGENTS.md` | Biết nhiệm vụ, giới hạn |
| ✅ User info | `agent/USER.md` | Biết anh Sáng thích gì |
| ✅ Brand voice | `knowledge/brand-voice.md` | Viết đúng giọng |
| ✅ Task input | Task schema | Topic, tone, format |
| ✅ Conversation | Session memory | Biết ngữ cảnh gần đây |
| ❌ Full KB | `knowledge/knowledge-base.md` | FAQ không cần cho viết bài |
| ❌ Business model | `knowledge/my-business.md` | Pricing không cần cho caption |

### 4.2 Tạo Ảnh (sang-tao-creative-fb)

| Include | Source | Why |
|---------|--------|-----|
| ✅ Agent identity | `agent/tao-anh/SOUL.md` | Biết mình là ai |
| ✅ Agent role | `agent/tao-anh/AGENTS.md` | Biết nhiệm vụ |
| ✅ Brand tone | `knowledge/brand-voice.md` (tone chương) | Ảnh đúng vibe |
| ✅ Task input | Task schema | Caption, concept, style |
| ✅ Conversation | Session memory | Ngữ cảnh |
| ❌ Full brand voice | `knowledge/brand-voice.md` | Chỉ cần tone, không cần rules |
| ❌ FAQ | `knowledge/knowledge-base.md` | Không cần cho tạo ảnh |

### 4.3 Làm Video (tao-video-ai)

| Include | Source | Why |
|---------|--------|-----|
| ✅ Agent identity | `agent/lam-video/SOUL.md` | Biết mình là ai |
| ✅ Agent role | `agent/lam-video/AGENTS.md` | Biết pipeline |
| ✅ Task input | Task schema | Caption, images, duration |
| ✅ Style references | `skills/tao-video-ai/assets/*` | Brand style, camera prompts |
| ❌ Brand voice text | `knowledge/brand-voice.md` | Video không cần text voice |
| ❌ FAQ/knowledge | `knowledge/` | Không cần cho video |

---

## 5. Context Priority

Khi có conflict giữa các context source:

```
1. Runtime Context (MCP signals) ─── highest — real-time data
2. User Context (current message) ── second — direct instruction
3. Session Context (conversation) ── third — current context
4. Agent Context (identity) ──────── fourth — agent definition
5. Project Context (config) ──────── fifth — project setup
6. System Context (framework) ────── lowest — general rules
```

---

## 6. Optimization Rules

| Rule | Detail |
|------|--------|
| **Load once** | System + Project context chỉ load 1 lần/session |
| **Filter before package** | Always filter before packaging to Worker |
| **Reference, don't copy** | Dùng path reference thay vì copy nội dung |
| **Session over static** | Session context override static context |
| **Fresh per dispatch** | Context được assemble lại mỗi lần dispatch |

---

## 7. Liên kết

- **Context Contract:** `CONTEXT_CONTRACT.md` — định dạng output
- **Prompt Assembly:** `PROMPT_ASSEMBLY.md` — prompt cuối cùng
- **Memory Strategy:** `core/memory/MEMORY_STRATEGY.md`
- **Worker Registry:** `core/worker/WORKER_REGISTRY.yaml`
- **FRAMEWORK_SPEC.md:** §7 Context System
