# TOOL MAP

> **File:** `docs/TOOL_MAP.md`
> **Status:** CURRENT
> **Last Updated:** 2026-07-08

---

## 1. Overview

This project uses **two categories** of tools:
1. **GoClaw Runtime Tools** — provided by the GoClaw platform (MCP functions, context, memory)
2. **External API Tools** — called by skill scripts (OpenAI, Facebook, Kling)

---

## 2. GoClaw Internal Tools

### 2.1 Context Files (File-Based "Database")

| File | Purpose | Format |
|------|---------|--------|
| `agent/*.md` | Agent definitions, workflows, soul | Markdown |
| `knowledge/*.md` | Brand voice, product info, business model | Markdown |
| `context-files/*` | Additional context (brain.db brand_voice table) | Markdown + SQLite |
| `skills/*/SKILL.md` | Skill definitions | Markdown |

### 2.2 MCP Functions (GoClaw Runtime)

| Function | Purpose | Output | Used In |
|----------|---------|--------|---------|
| `get_success_order_signal` | Check for new Pro orders | Order details (name, code, amount) | HEARTBEAT.md |
| `get_new_lead_signal` | Check for new leads/forms | Lead details (name, phone, email) | HEARTBEAT.md |
| `use_skill "skill-name"` | Execute a named skill | Skill-specific output | All workflows |

### 2.3 Telegram Bindings

| Binding | Type | Peer ID | Purpose |
|---------|------|---------|---------|
| `ga-trong-tre` | Direct message | `6880126421` | Owner commands |
| `lam-video` | Group | (group) | Video sub-agent |
| `tao-anh` | Group | (group) | Image sub-agent |
| `viet-bai-fb` | Group | (group) | Writing sub-agent |

---

## 3. External API Tools

### 3.1 OpenAI API

| Skill | Usage | Endpoint | Auth |
|-------|-------|----------|------|
| `sang-tao-creative-fb` | Image generation (gpt-image-1) | OpenAI Chat Completions | `OPENAI_API_KEY` |
| `tao-video-ai` | Prompt generation + image gen | OpenAI Chat Completions | `OPENAI_API_KEY` or `OPENAI_KEY_REAL` |

### 3.2 Facebook Graph API

| Skill | Usage | Endpoint | Auth |
|-------|-------|----------|------|
| `sang-tao-creative-fb` | Post photo to Fanpage | `/{page-id}/photos` | `FB_PAGE_ID` + `FB_PAGE_TOKEN` |
| `tao-video-ai` | Upload video to Reels | Facebook Graph API | `FB_PAGE_TOKEN` |

**Required Permission:** `pages_manage_posts`

### 3.3 Kling API

| Skill | Usage | Endpoint | Auth |
|-------|-------|----------|------|
| `tao-video-ai` | Video generation | Kling API | `KLING_API_KEY` + `KLING_SECRET_KEY` or `KLING_TOKEN` |

### 3.4 Image Publishing

| System | Description | Path |
|--------|-------------|------|
| Web server static dir | Public image hosting | `/opt/my-website/google-ads-toolkit/images/fb-creatives/` |
| Public URL | Accessible image URL | `https://tool.congsang.info.vn/images/fb-creatives/` |

---

## 4. Skill Scripts Map

### 4.1 sang-tao-creative-fb scripts

| Script | Purpose | Called When | Dependencies |
|--------|---------|------------|--------------|
| `gen_caption.py` | Generate ideas, captions, or ad bundles | Mode 1 (ideas), Mode 1 (caption), Mode 2 (bundles) | OpenAI API |
| `gen_image.py` | Generate images via GPT | After caption is ready | OpenAI API |
| `mode1_create_preview.py` | Full preview (caption + image + state) | After idea selection | gen_caption.py, gen_image.py |
| `mode1_post_approved.py` | Post approved content | After user says "OK" | state JSON, post_facebook.py |
| `post_facebook.py` | Publish image to Facebook | After approval | Facebook Graph API |
| `publish_image.py` | Copy to web static dir | Before Facebook post | File system |
| `check_env.py` | Verify environment setup | Debugging | Reading .env |

### 4.2 tao-video-ai scripts

| Script | Purpose | Called When | Dependencies |
|--------|---------|------------|--------------|
| `video_auto_facebook.py` | Main pipeline orchestrator | On trigger | All below |
| `gen-prompt.py` | Generate video prompt + voice script | Pipeline step 1 | OpenAI API |
| `gen-video.py` | Generate raw video | Pipeline step 2 | OpenAI/Kling API |
| `gen-voice.py` | Generate voiceover | Pipeline step 3 | TTS API |
| `build-final.py` | Combine into final MP4 | Pipeline step 4 | ffmpeg |
| `post_video.py` | Upload to Facebook Reels | After approval | Facebook Graph API |
| `upload-higgsfield.py` | Alternative upload method | If configured | Higgsfield API |
| `list-images.py` | List reference images | Debugging | File system |
| `check_env.py` | Verify environment | Debugging | Reading .env |

---

## 5. Tool Status Summary

| Tool | Type | Status | Notes |
|------|------|--------|-------|
| Context files (*.md) | GoClaw Internal | ✅ Active | Core knowledge base |
| MCP get_success_order_signal | GoClaw Internal | ✅ Active | Heartbeat monitoring |
| MCP get_new_lead_signal | GoClaw Internal | ✅ Active | Heartbeat monitoring |
| MCP use_skill | GoClaw Internal | ✅ Active | Skill execution |
| Telegram DM | GoClaw Internal | ✅ Active | Owner communication |
| Telegram Group | GoClaw Internal | ✅ Active | Team communication |
| OpenAI GPT Image | External API | ✅ Active | Image generation |
| OpenAI GPT Text | External API | ✅ Active | Caption/prompt generation |
| Facebook Graph API | External API | ✅ Active | Posting to Fanpage/Reels |
| Kling API | External API | ✅ Active | Video generation |
| Python scripts | Local Execution | ✅ Active | Skill automation |
| ffmpeg | Local Tool | ✅ Active | Video processing |
| Docker workspaces | Infrastructure | ✅ Active | 4 containers on VPS |

---

## 6. Adding a New Tool

1. Add environment variables to `.env` / `goclaw.yml`
2. Update skill's SKILL.md with new tool details
3. If external API: add to this TOOL_MAP.md
4. If new script: add to skill's `scripts/` directory
5. Test with dry-run mode first
