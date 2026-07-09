# CLAUDE.md — Gà Trống Tre AI Team Framework

> **Rule Book for Claude Code**
> Read this before any work. If ARCHITECT.md conflicts with a user request, ARCHITECT.md wins — explain why.
> 
> **For framework specification, read `FRAMEWORK_SPEC.md`.**

---

## 🚨 Golden Rules

### 1. READ FIRST, EDIT SECOND
- Always read ARCHITECT.md before starting any work.
- Always read the existing file before modifying it.
- Never assume — verify from source code.

### 2. NO HARDCODING
- Every configurable value → config file, env var, or `goclaw.yml`.
- No magic strings, no hardcoded paths, no hardcoded limits.
- No API keys in code.

### 3. NO BYPASSING FRAMEWORK
- All work flows through: Intent → Plan → Task → Kanban → Worker → Result.
- No agent-to-agent direct calls.
- No bypassing Manager for task routing.

### 4. NO DUPLICATE LOGIC
- If a function exists, import it — don't rewrite.
- If a skill exists, route to it — don't recreate it.
- Knowledge lives in `knowledge/` — one source of truth.

### 5. BACKWARD COMPATIBILITY
- Never break existing Telegram flows.
- Never break existing Skills.
- Never break existing Knowledge files.
- Never break existing Agent definitions.
- Never change database schema without explicit plan + migration.

### 6. EVERY CHANGE REQUIRES:
| Step | Action |
|------|--------|
| 1. Analyze | Read relevant files, understand context |
| 2. Plan | Write implementation plan in docs/ |
| 3. Review | Get user approval on plan |
| 4. Implement | Change code in small, reversible steps |
| 5. Test | Unit → Integration → Smoke → Regression |
| 6. Update Docs | Update ARCHITECT.md + relevant docs/ files |
| 7. Confirm | Show git diff, wait for approval |
| 8. Deploy | Only after user says "commit" and "deploy" |

---

## 📁 Project Structure

```
goclaw-agent/              # Project root
├── goclaw.yml             # GoClaw runtime — DO NOT MODIFY without reason
├── ARCHITECT.md           # System architecture — MUST stay current
├── CLAUDE.md              # This file — rules of engagement
├── FRAMEWORK_SPEC.md      # 🆕 Framework specification — formal contracts
├── README.md              # Quick start
│
├── agent/                 # Agent definitions — each agent has AGENTS.md + SOUL.md
├── knowledge/             # Shared knowledge — brand voice, product, business
├── skills/                # Skills plugins — each is self-contained
├── core/                  # Framework core — Manager, Router, Kanban, Worker, Context, Memory
├── memory/                # Runtime data — sessions, task history
└── docs/                  # All documentation
```

---

## 🔄 Standard Workflow

```
User Request
    → 1. Read relevant source files
    → 2. Load System Context (FRAMEWORK_SPEC.md, once per session)
    → 3. Load Project Context (goclaw.yml, once per session)
    → 4. Determine approach (simple vs multi-step)
    → 5. If multi-step: create Tasks via Kanban flow
    → 6. Assemble minimal Context per Worker via CONTEXT_ASSEMBLER.md
    → 7. Route to correct Worker(s)
    → 8. Wait for results
    → 9. Aggregate if multiple workers
    → 10. Format response in brand voice (SOUL.md)
    → 11. Deliver via Telegram
    → 12. Log to TASK_HISTORY.md (if task executed)
```

---

## 🧠 Skill Development Rules

### Creating a New Skill
1. `mkdir skills/<skill-name>/`
2. Write `SKILL.md` with:
   - Triggers (phrases that activate this skill)
   - Input requirements
   - Output format
   - Step-by-step flow
   - Dependencies (files, scripts, APIs)
   - Guardrails (what NOT to do)
   - Brand voice reference
3. Add assets/ for templates and references
4. Add scripts/ for executable code
5. Register in routing table (when Routing exists)

### SKILL.md Template Required Sections
```markdown
# Skill: <Name>

## Triggers
<phrases that activate this skill>

## Inputs
<what the skill needs to run>

## Output
<what the skill produces>

## Steps
<execution flow>

## Dependencies
<files, scripts, APIs, env vars>

## Guardrails
<constraints, safety rules>

## Context Sources
<knowledge files, agent files>
```

---

## 🧠 Knowledge Management

- `knowledge/brand-voice.md` — Tone of voice, vocabulary rules
- `knowledge/knowledge-base.md` — Product/domain FAQ + knowledge
- `knowledge/my-business.md` — Business model, pricing, customers
- **One source of truth:** Don't duplicate knowledge across skill files
- **Priority order:** 1. Live user instruction > 2. agent/*.md > 3. knowledge/*.md > 4. SKILL.md > 5. AI reasoning

---

## 🧩 Memory & Context Management (Phase 3)

### Memory Layers

| Layer | What | Where | When |
|-------|------|-------|------|
| **Short-term** | Current conversation turns | In-memory (GoClaw) | Every turn |
| **Session** | Current session tasks + events | `memory/sessions/session_YYYY-MM-DD.json` | Session lifecycle |
| **Long-term** | Completed tasks, decisions | `memory/long-term/*.log` or `.md` | On milestone / end of session |
| **Knowledge Base** | Brand voice, product info | `knowledge/*.md` | Every session (static) |

### Context Assembly Rules

1. **Minimal context per Worker** — Don't dump all knowledge. Only what the Worker needs for the Task.
2. **7 context types** — System, Project, Agent, User, Task, Session, Runtime. See `core/context/CONTEXT_ASSEMBLER.md`.
3. **Context Contract** — Worker receives structured JSON, not raw file dumps. See `core/context/CONTEXT_CONTRACT.md`.
4. **Prompt Assembly** — Manager assembles final prompt: System + Role + Task + Context + Knowledge + Constraints + Output.
5. **No context duplication** — Every piece of context lives in exactly one place. Reference by path, not copy.

### Reading Context
- Before planning: load System + Project + User + Session context
- Before dispatch: assemble minimal context for target Worker
- Before response: load Response Builder formatting context

### Writing Context
- After task complete: write to Session Memory
- At session end: summarize Session → append to Long-term
- On milestone (order, lead, deploy): write to Long-term immediately

---

## 🏗️ Implementation Process

### Each Phase Must Have:

```markdown
## Phase N: <Name>

**Goal:** <clear statement of what this phase achieves>

**Files Changed:**
- [ ] file1.js — <why>
- [ ] file2.md — <why>

**Database Changes:** YES/NO
- If YES: schema change, migration plan, rollback plan

**Risk Level:** LOW / MEDIUM / HIGH
- Risk: <description>
- Mitigation: <how to prevent>

**Rollback Plan:**
- <exact steps to undo this phase>

**Test Plan:**
- [ ] Unit test: <what>
- [ ] Integration: <what>
- [ ] Smoke test: <what>
- [ ] Regression: <what>

**Deploy Steps:**
- <step-by-step deployment>
```

---

## ✅ Pre-Commit Checklist

- [ ] Read ARCHITECT.md for context?
- [ ] Read FRAMEWORK_SPEC.md for contracts?
- [ ] Read all relevant source files?
- [ ] No hardcoded values?
- [ ] No duplicate logic?
- [ ] No breaking changes to existing flows?
- [ ] Memory rules followed? (read before write, minimal context)
- [ ] Docs updated?
- [ ] Tested (unit/integration/smoke)?
- [ ] User approved plan?
- [ ] Git diff reviewed?

---

## 🔒 Security Rules

1. Never commit `.env` files or API keys
2. Never print tokens to output
3. Never bypass auth/validation
4. Never fabricate product info, prices, or customer feedback
5. Never promise business results (orders, CPC reduction, ROAS)
6. Never disparage competitors — only state real differences

---

## ⚡ Quick References

### Telegram Flow
- Owner Telegram ID: 6880126421 (anh Sáng)
- Group chats for sub-agents (lam-video, tao-anh, viet-bai-fb)
- HEARTBEAT checks Pro orders + leads → notify only if new

### Communication Style (SOUL.md)
- "Giọng gần gũi, thẳng, ngắn, không corporate"
- Vietnamese, conversational, experience-backed
- No jargon, no hype, no aggressive CTAs
- CTA: "Anh em ghé vào xem thử" — light, clear

### Key Business Facts
- Product: Google Ads Match Type Converter (tool.congsang.info.vn)
- Service: Google Ads Consulting (congsang.info.vn)
- Pro price: 15,000 VND (one-time)
- Free: 3 Copy All uses
- Runs in-browser (no server upload)
