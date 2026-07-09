# AGENT MAP

> **File:** `docs/AGENT_MAP.md`
> **Status:** CURRENT
> **Last Updated:** 2026-07-08

---

## 1. Agent Inventory

### 1.1 Manager Agent

| Field | Value |
|-------|-------|
| **Name** | Gà Trống Tre |
| **ID** | `ga-trong-tre` |
| **Role** | Manager / Orchestrator |
| **Status** | ✅ Active |
| **Defined in** | `agent/AGENTS.md` |
| **Soul** | `agent/SOUL.md` |

**Responsibilities:**
- Understand user intent from Telegram
- Plan multi-step workflows
- Create and dispatch Tasks
- Track progress via Kanban
- Retry failed operations
- Aggregate results
- Format and send responses
- Monitor heartbeat signals (orders, leads)

**Skills Used:** All skills (orchestration only, not execution)
**Telegram Binding:** Direct message (owner: anh Sáng, ID 6880126421)

---

### 1.2 Worker Agents

| # | Name | ID | Role | Status | Defined In |
|---|------|----|------|--------|------------|
| 1 | **Cây Bút** | `viet-bai-fb` | Facebook Content Writer | ✅ Active | `agent/viet-bai-fb/AGENTS.md` |
| 2 | **Tạo Ảnh** | `tao-anh` | Facebook Image Creator | ✅ Active | `agent/tao-anh/AGENTS.md` |
| 3 | **Làm Video** | `lam-video` | Short-Form Video Editor | ✅ Active | `agent/lam-video/AGENTS.md` |

---

## 2. Worker Details

### 2.1 Cây Bút (viet-bai-fb)

| Field | Value |
|-------|-------|
| **Role** | Facebook content writer |
| **Primary Skill** | `viet-bai-facebook` |
| **Soul** | `agent/viet-bai-fb/SOUL.md` |
| **Commands** | `viet-bai-fb` in group |
| **Output** | 3 ideas OR full caption (Hook + Body + CTA) |
| **Restrictions** | ❌ No images ❌ No video ❌ No posting ❌ No task creation |
| **Receives from** | Gà Trống Tre only |
| **Reports to** | Gà Trống Tre only |

**Workflow:**
1. Receive topic + brief from Gà
2. Generate 3 article ideas
3. Gà forwards to anh Sáng for selection
4. Receive selected idea → write full caption
5. Return caption to Gà (no image, no posting)

---

### 2.2 Tạo Ảnh (tao-anh)

| Field | Value |
|-------|-------|
| **Role** | Facebook image creator |
| **Primary Skill** | `sang-tao-creative-fb` |
| **Reference Skill** | `viet-bai-facebook` (read-only, for brand voice) |
| **Soul** | `agent/tao-anh/SOUL.md` |
| **Commands** | `tao-anh` in group |
| **Output** | Paired image + caption |
| **Restrictions** | ❌ No writing captions ❌ No video ❌ No posting ❌ No task creation |
| **Receives from** | Gà Trống Tre only |
| **Reports to** | Gà Trống Tre only |

**Workflow:**
1. Receive caption + concept from Gà
2. Run `gen_image.py` → create GPT image
3. Pair image with caption
4. Return paired output to Gà

---

### 2.3 Làm Video (lam-video)

| Field | Value |
|-------|-------|
| **Role** | Short-form video editor (TikTok/Reels/Shorts) |
| **Primary Skill** | `tao-video-ai` |
| **Soul** | `agent/lam-video/SOUL.md` |
| **Commands** | `lam-video` in group |
| **Output** | MP4 video (15-25s) |
| **Restrictions** | ❌ No writing content ❌ No creating images ❌ No posting without approval |
| **Receives from** | Gà Trống Tre only |
| **Reports to** | Gà Trống Tre only |

**Pipeline:**
Research → Gen Prompt → List Images → Upload & Render → Review → Export

---

### 2.4 (Reserved for future Worker)

*No worker currently assigned. Xem `core/worker/WORKER_REGISTRY.yaml` để biết danh sách workers hiện tại.*

---

## 3. Agent Interaction Matrix

```
From \ To    | Gà Trống Tre | Cây Bút | Tạo Ảnh | Làm Video
-------------|-------------|---------|---------|-----------
Gà Trống Tre |      -      |   ✅    |   ✅    |    ✅
Cây Bút      |   ✅        |   -     |   ❌    |    ❌
Tạo Ảnh      |   ✅        |   ❌    |   -     |    ❌
Làm Video    |   ✅        |   ❌    |   ❌    |    -
```

**Legend:** ✅ = allowed, ❌ = forbidden, - = N/A

---

## 4. Agent Context Files

| File | Purpose | Read By |
|------|---------|---------|
| `agent/AGENTS.md` | Manager orchestration rules | Manager |
| `agent/SOUL.md` | Brand identity / voice | All agents |
| `agent/USER.md` | User/owner profile | Manager |
| `agent/HEARTBEAT.md` | Monitoring rules | Manager |
| `agent/CAPABILITIES.md` | System capabilities | All agents |
| `agent/IDENTITY.md` | Agent identity definition | All agents |
| `agent/viet-bai-fb/AGENTS.md` | Cây Bút workflow | Cây Bút |
| `agent/viet-bai-fb/SOUL.md` | Cây Bút soul | Cây Bút |
| `agent/tao-anh/AGENTS.md` | Tạo Ảnh workflow | Tạo Ảnh |
| `agent/tao-anh/SOUL.md` | Tạo Ảnh soul | Tạo Ảnh |
| `agent/lam-video/AGENTS.md` | Làm Video workflow | Làm Video |
| `agent/lam-video/SOUL.md` | Làm Video soul | Làm Video |
| `knowledge/brand-voice.md` | Brand tone | All agents |
| `knowledge/knowledge-base.md` | Product FAQ | Manager |
| `knowledge/my-business.md` | Business info | Manager |

---

## 5. Adding a New Agent

**Process:**
1. Create `agent/<worker-id>/AGENTS.md` with role, skills, workflow, restrictions
2. Create `agent/<worker-id>/SOUL.md` with identity and tone
3. Define skill in `skills/<skill-name>/SKILL.md`
4. Register in `goclaw.yml` (add workstation + binding)
5. Add routing rule to Dynamic Router
6. Update this AGENT_MAP.md
7. Update ARCHITECT.md if architecture changes
