# RISK ANALYSIS

> **File:** `docs/RISK_ANALYSIS.md`
> **Status:** CURRENT
> **Last Updated:** 2026-07-08

---

## 1. Risk Matrix

| # | Risk | Likelihood | Impact | Risk Level | Mitigation |
|---|------|-----------|--------|------------|------------|
| R1 | Breaking existing Telegram flow | Low | Critical | **High** | Never modify existing agent/*.md flow rules; only add |
| R2 | Breaking existing Skill execution | Low | Critical | **High** | Never modify existing SKILL.md steps/triggers; only append |
| R3 | GoClaw compatibility issue | Low | High | **Medium** | Keep goclaw.yml untouched; new core/ files are Claude Code reference only |
| R4 | Framework over-engineering | Medium | Low | **Low** | YAGNI principle — implement only what's needed now |
| R5 | Config drift (goclaw-agent vs google-ads-toolkit) | High | Medium | **Medium** | Keep goclaw-agent as single source of truth |
| R6 | Incomplete routing (missed intent) | Medium | Medium | **Medium** | Default fallback route; test all known intents |
| R7 | Worker not following Task contract | Medium | Medium | **Medium** | Clear instructions in AGENTS.md; code review |
| R8 | Memory/file bloat | Low | Low | **Low** | Set file size limits; rotation |
| R9 | New agent definition conflicts with old | Low | Medium | **Low** | Clear naming convention; no ID collisions |
| R10 | Stakeholder misunderstanding new architecture | Medium | Low | **Low** | Documentation-driven; ARCHITECT.md as reference |

---

## 2. Critical Risks (Detailed)

### R1: Breaking Existing Telegram Flow

**Description:** The existing system works through GoClaw Telegram bindings. Any change to how agents respond could break production.

**Impact:** User cannot communicate with Gà Trống Tre. Orders/leads missed.

**Mitigation:**
- Phase 1 only **adds new files** (`core/` directory) — does not modify `agent/AGENTS.md` flow rules
- All existing agent files remain as-is
- Only after user approval in testing phase do we update agent/*.md
- Rollback plan: `git checkout -- agent/` restores all agent files

### R2: Breaking Skill Execution

**Description:** Skills are executed by GoClaw runtime reading SKILL.md. Changing the structure could break execution.

**Impact:** Content creation, image generation, video production stop working.

**Mitigation:**
- Never change existing trigger phrases
- Never change existing execution steps
- Only ADD new sections (e.g., "Task Status Management") that are informational
- Rollback plan: `git checkout -- skills/` restores all skill files

### R5: Config Drift

**Description:** The `goclaw-agent` repo and `google-ads-toolkit` repo may have divergent configurations.

**Impact:** Inconsistent behavior between repos; confusion about which is authoritative.

**Mitigation:**
- `goclaw-agent` is the **single source of truth** for agent/skill config
- `google-ads-toolkit` is the **web application** (server, HTML, database)
- Clear boundary documented in ARCHITECT.md

---

## 3. Risk by Phase

| Phase | Risks | Overall Risk |
|-------|-------|-------------|
| Phase 0 (Docs) | None — no code changes | ✅ None |
| Phase 1 (Core) | R1, R2, R3, R4, R6 | 🟡 Medium |
| Phase 2 (Workers) | R1, R2, R7 | 🟡 Medium |
| Phase 3 (Memory) | R8 | 🟢 Low |
| Phase 4 (Testing) | R9 | 🟢 Low |
| Phase 5 (Template) | R10 | 🟢 Low |

---

## 4. Decision Log

| Date | Decision | Rationale | Author |
|------|----------|-----------|--------|
| 2026-07-08 | Keep goclaw.yml unchanged | No need to modify existing GoClaw config | Architect |
| 2026-07-08 | File-based storage for Kanban | No DB dependency; easy to back up; migratable later | Architect |
| 2026-07-08 | Never modify existing trigger phrases | Backward compatibility guarantee | Architect |
| 2026-07-08 | `core/` directory for new framework | Clear separation from existing agent/skills | Architect |
| 2026-07-08 | Phase 0 must complete before any code | Alignment before implementation | Architect |
