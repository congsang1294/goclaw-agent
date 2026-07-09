# IMPLEMENTATION PLAN

> **File:** `docs/IMPLEMENTATION_PLAN.md`
> **Status:** REVIEWED — awaiting final approval
> **Last Updated:** 2026-07-08
> **Architecture Review:** `docs/ARCHITECTURE_REVIEW.md`

---

## ⚠️ IMPORTANT: Framework = Markdown Instructions, Not Code

Repo này là GoClaw config. Framework core là **file markdown hướng dẫn** cho Claude Code đọc và làm theo, không phải code runtime. 

**Nguyên tắc:**
- Nếu GoClaw đã có → DÙNG, không viết lại
- Nếu GoClaw không có → XÂY (dưới dạng markdown instructions + conventions)
- Không tạo thêm dependency (Python package, npm modules, database)
- Chỉ dùng: `.md` (instructions) + `.yaml` (config) + tận dụng scripts Python hiện có

---

## Phase Overview

| Phase | Name | Effort | Risk | Dependencies |
|-------|------|--------|------|-------------|
| 0 | 📚 Documentation & Architecture | Low | Low | None |
| **0.5** | 🔍 **Architecture Review** | **Low** | **Low** | **Phase 0** |
| 1 | 🏗️ Core Framework — Manager + Router + Kanban | Medium | Low | Phase 0.5 |
| 2 | 🔌 Worker Integration | Medium | Low | Phase 1 |
| 3 | 🧠 Memory & Context System | Low | Low | Phase 1 |
| 4 | 🧪 Testing & Hardening | Medium | Low | Phase 2, 3 |
| 5 | 📦 Project Template & Docs | Low | Low | Phase 4 |

---

## Phase 0: Documentation & Architecture

**Goal:** Complete architecture docs and get alignment before writing code.

**Status:** ✅ COMPLETE

**Files Created (13 files):**
- [x] `ARCHITECT.md` — System architecture document
- [x] `CLAUDE.md` — Rule book for Claude Code
- [x] `docs/SYSTEM_ARCHITECTURE.md` — Architecture deep-dive
- [x] `docs/AGENT_MAP.md` — Agent inventory and details
- [x] `docs/SKILL_MAP.md` — Skill definitions and dependencies
- [x] `docs/TOOL_MAP.md` — Tool inventory
- [x] `docs/TASK_LIFECYCLE.md` — Task and Kanban design
- [x] `docs/ROUTING_RULES.md` — Dynamic routing design
- [x] `docs/DATABASE_ANALYSIS.md` — Database analysis
- [x] `docs/IMPLEMENTATION_PLAN.md` — This plan
- [x] `docs/TEST_PLAN.md` — Test strategy
- [x] `docs/RISK_ANALYSIS.md` — Risk assessment
- [x] `docs/ROADMAP.md` — Long-term roadmap

---

## Phase 0.5: Architecture Review

**Goal:** Đối chiếu kiến trúc đề xuất với GoClaw hiện tại. Khóa kiến trúc trước khi code.

**Status:** ✅ COMPLETE

**Files Created:**
- [x] `docs/ARCHITECTURE_REVIEW.md` — Full boundary analysis (GoClaw vs Framework)
- [x] `ARCHITECT.md` — Updated to v1.1.0 with review findings

**Key Findings:**
- GoClaw handles: Telegram, context loading, skill execution, multi-agent dispatch, heartbeat
- Framework builds: Intent Analyzer, Planner, Task system, Router, Dispatcher, Retry, Result Aggregator
- Framework = markdown instructions (not code), tận dụng GoClaw tối đa
- Không đụng: goclaw.yml, knowledge/, SOUL.md, USER.md, CAPABILITIES.md, IDENTITY.md
- Chỉ APPEND: AGENTS.md, HEARTBEAT.md, worker AGENTS.md, SKILL.md

---

## Phase 1: Core Framework

**Goal:** Tạo core/ directory với các file markdown instruction cho Manager (Gà Trống Tre).
Framework = hướng dẫn Claude Code đọc và làm theo. KHÔNG phải code runtime.

**Risk Level:** LOW (tất cả đều là .md files mới, không sửa existing)
**Duration Estimate:** 3-4 sessions

### Tổng quan: 12 files 🆕 CREATE + 2 files APPEND

#### Files 🆕 TẠO MỚI

| # | File | Mô tả | Kích thước |
|---|------|-------|-----------|
| 1 | `core/manager/INTENT_ANALYZER.md` | Rule-based intent detection | ~200 lines |
| 2 | `core/manager/PLANNER.md` | Multi-step plan with dependency graph | ~150 lines |
| 3 | `core/manager/ORCHESTRATION.md` | Manager flow control | ~100 lines |
| 4 | `core/manager/RESULT_AGGREGATOR.md` | Merge outputs from multiple workers | ~80 lines |
| 5 | `core/manager/RESPONSE_BUILDER.md` | Format response in brand voice | ~80 lines |
| 6 | `core/router/ROUTING_TABLE.yaml` | Config-driven intent → worker mapping | ~60 lines |
| 7 | `core/router/ROUTING_RULES.md` | How routing works, how to add routes | ~100 lines |
| 8 | `core/kanban/TASK_SCHEMA.md` | JSON task schema definition | ~120 lines |
| 9 | `core/kanban/KANBAN_BOARD.md` | Board layout and operations | ~100 lines |
| 10 | `core/kanban/TASK_LIFECYCLE.md` | Status transitions and lifecycle flows | ~150 lines |
| 11 | `core/dispatcher/DISPATCHER.md` | How to send tasks to workers via @agentId | ~100 lines |
| 12 | `core/retry/RETRY_POLICY.md` | Retry rules and policies | ~80 lines |

#### Files 📝 APPEND (chỉ thêm section, không sửa existing)

| # | File | Thêm section | Lý do |
|---|------|-------------|-------|
| 1 | `agent/AGENTS.md` | "Manager Orchestration" section | Manager cần biết flow mới |
| 2 | `agent/HEARTBEAT.md` | "Task Monitoring" section | Theo dõi task trong heartbeat |

#### Files ✅ KHÔNG ĐỤNG (trong Phase 1)

- `goclaw.yml` — GoClaw runtime
- `agent/SOUL.md` — Brand voice
- `agent/USER.md` — User profile
- `agent/CAPABILITIES.md` — Capabilities
- `agent/IDENTITY.md` — Identity
- `agent/viet-bai-fb/*` — Worker (Phase 2)
- `agent/tao-anh/*` — Worker (Phase 2)
- `agent/lam-video/*` — Worker (Phase 2)
- `knowledge/*.md` — Shared knowledge
- `skills/*` — Skill plugins (Phase 2)
- `core/events/EVENT_BUS.md` — Future Phase
- `memory/` — Future Phase

### Database Changes
**NO** — Không đụng brain.db. File-based storage.

### Risk Assessment

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Breaking existing Telegram flow | Low | High | AGENTS.md chỉ APPEND section, không sửa existing |
| GoClaw compatibility | Low | Medium | goclaw.yml giữ nguyên; core/*.md chỉ là reference |
| Over-engineering | Low | Low | YAGNI; chỉ build cái cần cho Phase 1 |
| File bloat | Low | Low | Markdown files có kích thước giới hạn |

### Rollback Plan
```bash
# Phase 1 chỉ tạo mới + append, rollback an toàn:
git checkout -- agent/AGENTS.md agent/HEARTBEAT.md
rm -rf core/
# Không file nào khác bị ảnh hưởng
```

### Test Plan
- [ ] Verify existing Telegram flows không bị ảnh hưởng
- [ ] Verify routing table covers all 5 existing skills
- [ ] Verify task schema handles simple + complex workflows
- [ ] Smoke: trace "viết bài" qua Intent → Route → Task → Response

---

## Phase 2: Worker Integration (Config-Driven)

**Goal:** Chuẩn hóa giao tiếp Manager ↔ Worker qua Task Contract. Xóa Fox Spirit. Worker đăng ký qua config (N Workers, không hardcode). Routing hoàn toàn động.

**Risk Level:** LOW (chỉ APPEND sections + tạo file config mới)
**Duration Estimate:** 2-3 sessions

### Files 🆕 TẠO MỚI

| File | Mô tả |
|------|-------|
| `core/worker/WORKER_REGISTRY.yaml` | Config-driven worker registry — single source of truth cho tất cả workers |
| `core/worker/WORKER_REGISTRY.md` | Hướng dẫn đăng ký/hủy worker — không cần sửa core |

### Files 📝 APPEND

| File | Thêm section |
|------|-------------|
| `agent/viet-bai-fb/AGENTS.md` | "Task Contract" — how to receive/update/deliver Tasks |
| `agent/tao-anh/AGENTS.md` | "Task Contract" |
| `agent/lam-video/AGENTS.md` | "Task Contract" |
| `skills/viet-bai-facebook/SKILL.md` | "Task Status Management" — update task status during execution |
| `skills/sang-tao-creative-fb/SKILL.md` | "Task Status Management" |
| `skills/tao-video-ai/SKILL.md` | "Task Status Management" |

### Files 🗑️ XÓA THAM CHIẾU (Fox Spirit)

| File | Hành động |
|------|----------|
| Tất cả docs + core | Xóa mọi tham chiếu tới `fox-spirit`, `Fox Spirit` |

### Files ✅ KHÔNG ĐỤNG

- `agent/viet-bai-fb/SOUL.md` — Identity
- `agent/tao-anh/SOUL.md` — Identity
- `agent/lam-video/SOUL.md` — Identity
- `agent/fox-spirit/` — Không tạo (đã loại bỏ khỏi framework)
- `skills/agent-scout/SKILL.md` — Giữ nguyên (không có Task Status section)
- `skills/tra-loi-faq-khach-hang/SKILL.md` — Giữ nguyên (không có Task Status section)
- `knowledge/*.md` — Shared knowledge
- `skills/*/assets/` — Skill templates
- `skills/*/scripts/` — Execution scripts

### Risk Assessment

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Breaking skill execution | Low | High | Only APPEND sections, never modify steps/triggers |
| Worker contract confusion | Low | Low | Clear language, examples in AGENTS.md |
| Config migration | Low | Low | BACKWARD COMPATIBLE — all existing workers registered in WORKER_REGISTRY.yaml |

### Rollback Plan
```bash
git checkout -- agent/viet-bai-fb/AGENTS.md agent/tao-anh/AGENTS.md agent/lam-video/AGENTS.md
git checkout -- skills/viet-bai-facebook/SKILL.md skills/sang-tao-creative-fb/SKILL.md skills/tao-video-ai/SKILL.md
rm -rf core/worker/
```

### Test Plan
- [ ] Trace "viết bài": Intent → Task → Cây Bút → Task done → Response
- [ ] Trace "tạo ảnh": same flow
- [ ] Trace "làm video": same flow
- [ ] Trace "cả team": 3 workers với dependency chain
- [ ] Verify existing Telegram commands still work
- [ ] Verify WORKER_REGISTRY.yaml matches goclaw.yml bindings

---

## Phase 3: Memory & Context

**Goal:** File-based persistent memory for task execution history.

**Risk Level:** LOW
**Duration Estimate:** 1 session

### Files 🆕 TẠO MỚI

| File | Mô tả |
|------|-------|
| `memory/TASK_HISTORY.md` | Task execution log format + rotation |

### Files 📝 APPEND

| File | Thêm section |
|------|-------------|
| `agent/AGENTS.md` | "Memory Management" — read/write task history |

### Risk Assessment

| Risk | L | I | Mitigation |
|------|---|---|------------|
| File bloat | Low | Low | Rotation policy; max 1000 entries |

### Rollback Plan
```bash
rm -rf memory/
git checkout -- agent/AGENTS.md
```

---

## Phase 4: Testing & Hardening

**Goal:** Systematic testing of all flows.

**Risk Level:** LOW
**Duration Estimate:** 1-2 sessions

### Files Changed

| File | Action |
|------|--------|
| `docs/TEST_PLAN.md` | Update with results |
| Various | Bug fixes |

### Test Scenarios
- [ ] All single-skill flows (5 skills)
- [ ] Multi-step team (write → image → video)
- [ ] Failure + retry (simulate API timeout)
- [ ] Ambiguous intent → clarification
- [ ] Unknown intent → graceful handling
- [ ] Cancellation mid-flow

---

## Phase 5: Project Template & Final Docs

**Goal:** Script để scaffold project mới từ framework template.

**Risk Level:** LOW
**Duration Estimate:** 1 session

### Files Created

| File | Mô tả |
|------|-------|
| `scripts/new-project.sh` | Scaffold: copy core/ + docs/, clean business files |
| `TEMPLATE.md` | Usage guide for template |
| `README.md` | Update with "Create New Project" section |

---

## Implementation Order

```
Phase 0     (Docs) ────────── ✅ DONE
Phase 0.5   (Review) ──────── ✅ DONE
    │
    ▼
Phase 1     (Core Framework) ─────── ⏳ PENDING APPROVAL
    │
    ├── 1a. core/manager/INTENT_ANALYZER.md
    ├── 1b. core/manager/PLANNER.md
    ├── 1c. core/manager/ORCHESTRATION.md
    ├── 1d. core/manager/RESULT_AGGREGATOR.md
    ├── 1e. core/manager/RESPONSE_BUILDER.md
    ├── 1f. core/router/ROUTING_TABLE.yaml + ROUTING_RULES.md
    ├── 1g. core/kanban/TASK_SCHEMA.md + KANBAN_BOARD.md + TASK_LIFECYCLE.md
    ├── 1h. core/dispatcher/DISPATCHER.md
    ├── 1i. core/retry/RETRY_POLICY.md
    ├── 1j. agent/AGENTS.md (append orchestration section)
    └── 1k. agent/HEARTBEAT.md (append task monitoring section)
    │
    ▼
Phase 2     (Worker Integration + Config-Driven) ── ⏳
    │
    ├── 2a. Xóa Fox Spirit khỏi toàn bộ tài liệu
    ├── 2b. Tạo core/worker/WORKER_REGISTRY.yaml + WORKER_REGISTRY.md
    ├── 2c. Cập nhật core/* để đọc từ config (không hardcode)
    ├── 2d. Append Task contract → 3 worker AGENTS.md
    └── 2e. Append Task status → 3 skill SKILL.md (content workers)
    │
    ▼
Phase 3     (Memory) ── ⏳
Phase 4     (Testing) ── ⏳
Phase 5     (Template) ── ⏳
```
