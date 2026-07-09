# DATABASE ANALYSIS

> **File:** `docs/DATABASE_ANALYSIS.md`
> **Status:** CURRENT
> **Last Updated:** 2026-07-08

---

## 1. Overview

The goclaw-agent repo is a **configuration-only repository**. It does not contain a database directly. However, it references and depends on:

1. **brain.db (SQLite)** — Located in the google-ads-toolkit web project (separate repo)
2. **Markdown files** — Used as file-based "database" for knowledge and context
3. **GoClaw platform state** — Managed by the GoClaw runtime

---

## 2. brain.db (External SQLite)

**Location:** Not in this repo. Referenced from:
- `skills/sang-tao-creative-fb/SKILL.md` — reads `brand_voice` table
- `knowledge/my-business.md` — reads business data from rows

**Referenced Tables:**

| Table | Purpose | Referenced By |
|-------|---------|---------------|
| `brand_voice` | Brand tone and language rules | sang-tao-creative-fb skill |
| `business` | Business info (products, customers, feedback) | knowledge/my-business.md |
| `alembic_version` | Migration tracking | (system) |

**Note:** The brain.db schema is defined in the web project (`google-ads-toolkit/lib/schema.js`), NOT in this repo.

---

## 3. File-Based "Database"

The following files serve as a read-only knowledge store:

| File | Type | Content Type | Records |
|------|------|-------------|---------|
| `knowledge/brand-voice.md` | Markdown | Brand guidelines | ~20 rules |
| `knowledge/knowledge-base.md` | Markdown | FAQ (50 questions) + Objections (10) | 60+ items |
| `knowledge/my-business.md` | Markdown | Business info (3 sections) | 3 sections |
| `agent/*.md` | Markdown | Agent definitions | 7 files |
| `skills/*/SKILL.md` | Markdown | Skill definitions | 5 files |
| `skills/*/assets/*.md` | Markdown | Skill templates | 15+ files |

---

## 4. No Database Changes Needed

**Current state:** The goclaw-agent repo has no database to modify.

**For framework implementation (future):**
- Kanban/Task system may need a lightweight storage (JSON file or SQLite)
- Memory system may need persistent key-value storage
- These will be designed to NOT conflict with existing brain.db
- Any new storage will be additive (never modify brain.db schema)

---

## 5. database/schema.js (Google Ads Toolkit Project)

This file lives in the web project, NOT in goclaw-agent. It defines the brain.db schema:

| Table | Columns | Purpose |
|-------|---------|---------|
| `settings` | key, value, type, group, updated_at | App settings |
| `orders` | id, customer_name, email, phone, product, amount, status, payment_method, created_at | Pro orders |
| `leads` | id, name, phone, email, challenge, interest, source, created_at | Customer leads |
| `email_logs` | id, to, subject, status, sent_at | Email history |
| `notification_log` | id, type, ref_id, telegram_sent, telegram_status, sent_at | Telegram notification tracking |
| `feedback` | id, name, email, message, created_at | User feedback |
| `brand_voice` | id, name, content, updated_at | Brand voice rules |
| `business` | row_id, section, content, updated_at | Business info |

---

## 6. Database Considerations for Framework

| Concern | Current Status | Framework Plan |
|---------|---------------|----------------|
| Task/Kanban storage | Not implemented | JSON file or SQLite (new, non-conflicting) |
| Memory storage | Not implemented | Markdown files in `memory/` |
| Knowledge base | File-based (current) | Keep file-based (no migration) |
| brain.db | External (not in this repo) | Keep external, no changes |
| Migration handling | N/A | Add migration scripts if adding new DB |
