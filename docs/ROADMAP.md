# ROADMAP

> **File:** `docs/ROADMAP.md`
> **Status:** CURRENT
> **Last Updated:** 2026-07-08
> **Architecture Review:** `docs/ARCHITECTURE_REVIEW.md`

---

## Phase Map

```
Phase 0: 2026-07-08 ─────■ (DONE)
Phase 0.5: 2026-07-08 ───■ (DONE)
                              ⏳ PENDING APPROVAL
Phase 1: ─────────────────◇───■ (3-4 sessions)
Phase 2: ────────────────────────■───■ (2-3 sessions)
Phase 3: ──────────────────────────────■ (1 session)
Phase 4: ──────────────────────────────────■───■ (1-2 sessions)
Phase 5: ────────────────────────────────────────■ (1 session)
```

**Estimate:** 8-11 sessions total after approval.

---

## Phase 0: 📚 Foundation

**Status:** ✅ COMPLETE — 2026-07-08

**Deliverables:**
- [x] Full source code analysis (goclaw-agent repo)
- [x] ARCHITECT.md — System architecture document
- [x] CLAUDE.md — Rule book
- [x] docs/SYSTEM_ARCHITECTURE.md — Architecture deep-dive
- [x] docs/AGENT_MAP.md — Agent inventory
- [x] docs/SKILL_MAP.md — Skill definitions
- [x] docs/TOOL_MAP.md — Tool inventory
- [x] docs/TASK_LIFECYCLE.md — Task & Kanban design
- [x] docs/ROUTING_RULES.md — Dynamic routing design
- [x] docs/DATABASE_ANALYSIS.md — Database analysis
- [x] docs/IMPLEMENTATION_PLAN.md — Implementation plan
- [x] docs/TEST_PLAN.md — Testing strategy
- [x] docs/RISK_ANALYSIS.md — Risk assessment
- [x] docs/ROADMAP.md — Roadmap
- [x] Updated README.md

---

## Phase 0.5: 🔍 Architecture Review

**Status:** ✅ COMPLETE — 2026-07-08

**Goal:** Đối chiếu kiến trúc đề xuất với GoClaw hiện tại. Xác định rõ: phần nào GoClaw có (không đụng), phần nào Framework xây mới, phần nào chỉ refactor.

**Deliverables:**
- [x] `docs/ARCHITECTURE_REVIEW.md` — Full boundary analysis
- [x] `ARCHITECT.md` — Updated to v1.1.0 with GoClaw boundary
- [x] `docs/IMPLEMENTATION_PLAN.md` — Updated with precise file list
- [x] `docs/ROADMAP.md` — Updated with Phase 0.5

**Key Decisions:**
- Framework = markdown instructions + conventions (not code)
- Tận dụng GoClaw tối đa (Telegram, context, skill execution, multi-agent dispatch)
- Chỉ APPEND sections vào file hiện có, không sửa existing
- core/*.md files là hướng dẫn cho Claude Code đọc và làm theo

---

## Phase 1: 🏗️ Core Framework

**Status:** 🟡 NOT STARTED — awaiting final approval

**Goal:** Tạo `core/` directory với 12 file markdown hướng dẫn Manager. Framework core = instructions, not code.

**What we build (12 files):**
| Module | Files | Type |
|--------|-------|------|
| Manager | `INTENT_ANALYZER.md`, `PLANNER.md`, `ORCHESTRATION.md`, `RESULT_AGGREGATOR.md`, `RESPONSE_BUILDER.md` | 🆕 New |
| Router | `ROUTING_TABLE.yaml`, `ROUTING_RULES.md` | 🆕 New |
| Kanban | `TASK_SCHEMA.md`, `KANBAN_BOARD.md`, `TASK_LIFECYCLE.md` | 🆕 New |
| Dispatcher | `DISPATCHER.md` | 🆕 New |
| Retry | `RETRY_POLICY.md` | 🆕 New |

**What we update (2 files):**
- `agent/AGENTS.md` — Append Manager Orchestration section
- `agent/HEARTBEAT.md` — Append Task Monitoring section

**What we DON'T touch:**
- goclaw.yml, SOUL.md, USER.md, CAPABILITIES.md, IDENTITY.md
- agent/viet-bai-fb/, agent/tao-anh/, agent/lam-video/
- knowledge/*.md, skills/*/

**Risk Level:** LOW (all new files + append-only updates)

---

## Phase 2: 🔌 Worker Integration + Config-Driven

**Status:** 🟡 NOT STARTED

**Goal:** Chuẩn hóa giao tiếp Manager ↔ Worker. Worker đăng ký qua config. Xóa Fox Spirit.

| Step | Task | Files | Duration |
|------|------|-------|----------|
| 2a | Remove Fox Spirit references | Tất cả docs + core | 1 session |
| 2b | Create Worker Registry | core/worker/WORKER_REGISTRY.yaml + .md | 1 session |
| 2c | Update Manager to read from config | core/manager/* | 1 session |
| 2d | Append Task contract | 3 worker AGENTS.md | 1 session |
| 2e | Append Task status to skills | 3 content skill SKILL.md | 1 session |

**Risk Level:** LOW (append-only + new config files)

---

## Phase 3: 🧠 Memory & Context System

**Status:** 🟡 NOT STARTED

**Goal:** File-based persistent memory for task execution history.

| Step | Task | Duration |
|------|------|----------|
| 3a | Create memory/TASK_HISTORY.md | 1 session |

**Risk Level:** LOW

---

## Phase 4: 🧪 Testing & Hardening

**Status:** 🟡 NOT STARTED

**Goal:** Systematic quality assurance.

| Step | Task | Duration |
|------|------|----------|
| 4a | Run all flow tests | 1 session |
| 4b | Run failure + retry tests | 1 session |
| 4c | Fix bugs | 1 session |

---

## Phase 5: 📦 Project Template & Finalization

**Status:** 🟡 NOT STARTED

**Goal:** Script để scaffold project mới từ framework template.

| Step | Task | Duration |
|------|------|----------|
| 5a | Create scripts/new-project.sh | 1 session |
| 5b | Write TEMPLATE.md | 1 session |
| 5c | Final docs sweep | 1 session |

---

## Future Vision

| Feature | Description | Priority |
|---------|-------------|----------|
| **Event Bus** | Publish/subscribe for task events | Medium |
| **Multi-project CLI** | `goclaw new <project-name>` | Medium |
| **Web Dashboard** | Visual Kanban board | Low |
| **Analytics** | Task completion rates, worker perf | Low |
| **Plugin Registry** | Community skill marketplace | Low |
| **Slack Integration** | Additional messenger | Low |

---

## Dependencies

| Phase | Depends On | Blocked By |
|-------|-----------|------------|
| 0 | None | — |
| 0.5 | Phase 0 | — |
| 1 | Phase 0.5 approval | **User approval** |
| 2 | Phase 1 | Review + fix |
| 3 | Phase 1 | Review + fix |
| 4 | Phase 2 + 3 | Review + fix |
| 5 | Phase 4 | Review + fix |
