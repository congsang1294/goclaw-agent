# SKILL MAP

> **File:** `docs/SKILL_MAP.md`
> **Status:** CURRENT
> **Last Updated:** 2026-07-08

---

## 1. Skill Inventory

| # | Skill Name | Location | Type | Status | Worker |
|---|-----------|----------|------|--------|--------|
| 1 | viet-bai-facebook | `skills/viet-bai-facebook/` | Content Writing | ✅ Active | Cây Bút |
| 2 | sang-tao-creative-fb | `skills/sang-tao-creative-fb/` | Creative Image + Caption | ✅ Active | Tạo Ảnh |
| 3 | tao-video-ai | `skills/tao-video-ai/` | AI Video Production | ✅ Active | Làm Video |
| 4 | agent-scout | `skills/agent-scout/` | Web Research + Analysis | ✅ Active | (no dedicated worker) |
| 5 | tra-loi-faq-khach-hang | `skills/tra-loi-faq-khach-hang/` | Customer FAQ | ✅ Active | (no dedicated worker) |

---

## 2. Skill Details

### 2.1 viet-bai-facebook

| Field | Value |
|-------|-------|
| **SKILL.md** | `skills/viet-bai-facebook/SKILL.md` |
| **Worker** | Cây Bút (viet-bai-fb) |
| **Trigger Phrases** | "viết bài Facebook", "viết post bán hàng", "làm caption Facebook", "viết content quảng cáo", "giới thiệu tính năng mới", "kêu gọi dùng thử" |
| **Output Format** | Hook + Body + CTA (Vietnamese, brand voice) |
| **Scripts** | None (pure AI generation) |
| **Templates** | `hook-template.md`, `body-template.md`, `cta-template.md`, `post-example.md` |

**Flow:**
1. Check input completeness (product, audience, pain point, benefit, CTA)
2. If missing info → ask up to 5 clarifying questions
3. Generate post: Hook (real story/scene) → Body (problem → insight → solution) → CTA (light, clear)
4. Self-audit against 9 quality checks
5. Deliver post

**Context Sources:**
- `knowledge/brand-voice.md`
- `agent/*.md` context files
- Own assets (templates)
- Live user instructions (highest priority)

**Guardrails:**
- Never fabricate product info
- Never promise business results
- Never demean competitors
- Max 5 clarifying questions
- Solution never appears too early

---

### 2.2 sang-tao-creative-fb

| Field | Value |
|-------|-------|
| **SKILL.md** | `skills/sang-tao-creative-fb/SKILL.md` |
| **Worker** | Tạo Ảnh (tao-anh) |
| **Trigger Phrases** | "tạo content cho ngày mai", "gen bài Page", "content organic", "tạo creative ads", "gen ads", "cần creative cho chiến dịch" |
| **Output Format** | Pair: image + caption (always together) |
| **Scripts** | `gen_caption.py`, `gen_image.py`, `mode1_create_preview.py`, `mode1_post_approved.py`, `post_facebook.py`, `publish_image.py`, `check_env.py` |

**Modes:**
| Mode | Description | Output |
|------|-------------|--------|
| Mode 1 (Organic) | Daily Facebook Page content | 1 image + 1 caption (80-150 words) |
| Mode 2 (Ad Creative) | Paid ad creatives | 3 bundles (3 images + 3 captions), angles: pain/solution/proof |

**Mode 1 Flow (7 steps):**
1. `gen_caption.py --task ideas` → 3 ideas
2. Send 3 ideas to anh Sáng → wait for selection
3. `mode1_create_preview.py` → caption + image + state JSON
4. Send preview to anh Sáng
5. On "OK" → `mode1_post_approved.py`
6. `publish_image.py` → public URL
7. `post_facebook.py` → Facebook Graph API

**Environment Variables Required:**
- `OPENAI_API_KEY`
- `FB_PAGE_ID`
- `FB_PAGE_TOKEN`
- `PUBLIC_IMAGE_DIR`, `PUBLIC_BASE_URL` (for image hosting)

**Guardrails:**
- Always produce image + text together
- No auto-post without approval
- `DRY_RUN=true` → no actual Facebook calls
- One retry on OpenAI failure, then error

---

### 2.3 tao-video-ai

| Field | Value |
|-------|-------|
| **SKILL.md** | `skills/tao-video-ai/SKILL.md` |
| **Worker** | Làm Video (lam-video) |
| **Trigger Phrases** | "video", "làm video", "tạo video", "đăng video", "Reels", "Facebook Reels", uploaded MP4 |
| **Output Format** | MP4 video (15-25s), Facebook Reels link |
| **Scripts** | `video_auto_facebook.py`, `gen-prompt.py`, `gen-video.py`, `gen-voice.py`, `build-final.py`, `post_video.py`, `upload-higgsfield.py`, `list-images.py`, `check_env.py` |

**Pipeline (7 steps):**
1. Receive trigger → write `video-pipeline.trigger` JSON
2. Watch for trigger → `gen-prompt.py` → prompt + voice script
3. `gen-video.py` → `video_raw.mp4`
4. `gen-voice.py` → `voice.mp3`
5. `build-final.py` → `final.mp4` + Telegram preview
6. Wait for user approval
7. `post_video.py` → Facebook Reels → return link

**Video Providers:**
| Provider | Authentication | Method |
|----------|---------------|--------|
| OpenAI-KenBurns | `OPENAI_API_KEY` | gpt-image-1 + ffmpeg |
| Kling | `KLING_API_KEY`, `KLING_SECRET_KEY` | Kling API |

**Assets:**
- `brand-style.md` — Tone-specific style guides
- `camera-prompts.md` — 5 verified camera motions
- `cinematic-format.md` — Luxury product video structure
- `koc-format.md` — KOC fashion video structure
- `negative-prompt.txt` — Default negative prompts
- `troubleshoot.md` — 7 error categories with fixes

**Guardrails:**
- Phase 1: preview only (no auto-post)
- Phase 2: post only on user approval ("OK", "duyệt", "đăng đi")
- No Canva, InVideo, CapCut
- No questions about style/dimensions after trigger
- No promises about TikTok/YouTube
- User must be called "anh Sáng" (not "Anh Sang")

---

### 2.4 agent-scout

| Field | Value |
|-------|-------|
| **SKILL.md** | `skills/agent-scout/SKILL.md` |
| **Worker** | (no dedicated worker — Manager uses directly) |
| **Trigger Phrases** | "tìm...", "research nhanh...", "đánh giá thông tin về...", "phân tích đối thủ...", "so sánh đối thủ...", "phân tích SWOT..." |
| **Output Format** | Analysis in specified template |
| **Scripts** | None (web search + AI analysis) |
| **Templates** | `general-scout-template.md`, `competitor-scout-template.md`, `swot-template.md` |

**Modes:**
| Mode | Description | Sources |
|------|-------------|---------|
| General Scout | Info, products, trends, pricing, news | 3-5 sources |
| Competitor Scout | Competitor analysis | Official sources |
| SWOT | Strategic analysis | 3 sources |

**Flow:**
1. Identify real question
2. If broad → ask 1 clarifying question
3. Search with specific keywords
4. Prioritize official/recent sources
5. Read each source before summarizing
6. Discard SEO spam/thin content
7. Return in template format

**Guardrails:**
- Always Vietnamese output
- 1-2 sentences per source
- Never fabricate links/data
- If no info → "Không tìm thấy thông tin phù hợp"
- Not for file finding or code editing

---

### 2.5 tra-loi-faq-khach-hang

| Field | Value |
|-------|-------|
| **SKILL.md** | `skills/tra-loi-faq-khach-hang/SKILL.md` |
| **Worker** | (no dedicated worker — Manager uses directly) |
| **Trigger Phrases** | "tool này dùng để làm gì", "giá bao nhiêu", "dữ liệu có bị lưu không", "Copy All là gì", "match type là gì", "mới chạy ads bắt đầu từ đâu", "vì sao ads cắn tiền", "có tư vấn Google Ads không" |
| **Output Format** | FAQ answer in brand voice |
| **Scripts** | None |

**FAQ Coverage: 50 questions**
- Questions 1-29: Tool-related (pricing, features, privacy, payment, comparison)
- Questions 30-50: Google Ads knowledge (basics, match types, negative keywords, budget, consulting)

**Response Routing:**
| Question Type | Response Target |
|---------------|----------------|
| Tool questions | `tool.congsang.info.vn` |
| Foundational knowledge | Plain explanation (don't push services) |
| Account issues, setup | Brief explanation → `congsang.info.vn` |
| Overwhelmed beginners | Reassure first |

**Guardrails:**
- No made-up refund/warranty policies
- No promising results
- No disparaging competitors
- Copy All unlock ONLY via checkout
- Links only in appropriate context

---

## 3. Skill Dependency Graph

```
viet-bai-facebook
    └── knowledge/brand-voice.md
    └── own assets/*.md

sang-tao-creative-fb
    └── knowledge/brand-voice.md
    └── brain.db (brand_voice table)
    └── context-files/*.md
    └── scripts/*.py (Python execution)

tao-video-ai
    └── own assets/*.md
    └── scripts/*.py (Python execution)
    └── OpenAI API / Kling API

agent-scout
    └── own templates/*.md

tra-loi-faq-khach-hang
    └── knowledge/knowledge-base.md
    └── knowledge/my-business.md
```

**Key Rule:** No skill directly depends on another skill. Dependencies are only on knowledge/ and assets/.
