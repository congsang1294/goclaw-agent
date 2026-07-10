# DEPLOYMENT GUIDE — Gà Trống Tre AI Team Framework

> **File:** `DEPLOYMENT.md`
> **Version:** 1.0.0
> **Applies to:** v1.0.0-framework

---

## 1. Overview

This document describes how to deploy the Gà Trống Tre AI Team Framework to a production VPS running GoClaw.

**Architecture:**
- **VPS:** Single server with Docker Compose
- **GoClaw:** Multi-agent AI gateway (Postgres-backed)
- **Telegram:** Bot API (polling mode)
- **Framework:** Markdown instructions + YAML config loaded by GoClaw agent runtime

---

## 2. Prerequisites

| Resource | Requirement |
|----------|------------|
| VPS | Ubuntu 22.04+, 4GB RAM, 2 CPU cores |
| Docker | 24.0+ with Compose V2 |
| Domain | (Optional) For web dashboard |
| Telegram | Bot tokens for Manager + Workers |
| LLM Keys | Anthropic / OpenAI / Gemini API keys |

---

## 3. First-Time Deployment

### 3.1 GoClaw Setup

```bash
# Clone GoClaw
git clone https://github.com/nextlevelbuilder/goclaw.git /opt/goclaw
cd /opt/goclaw

# Generate env
cp .env.example .env
./prepare-env.sh
# Edit .env: add TELEGRAM_TOKEN, LLM API keys

# Start GoClaw + Postgres
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d

# Verify
docker ps
# → goclaw Up (healthy)
# → postgres Up
```

### 3.2 Create Agents

> **CRITICAL — tool profile:** Để skill tạo ảnh/video và **trả output về Telegram** được, mỗi agent phải có tool profile `full` (hoặc ít nhất đủ `group:media_gen` + `group:fs` + `group:messaging`).
>
> - `full` = có `create_image`/`create_video` (gen) **và** `message`/`send_file` (deliver).
> - `coding` = có gen nhưng **không** deliver → triệu chứng "chạy xong không trả ảnh về Telegram".
> - `messaging` = có deliver nhưng không gen.
>
> Tool `delegate` **đã bị gỡ bỏ** trong GoClaw hiện tại. Delegation giờ qua `team_tasks` + `spawn`.
>
> Xem chi tiết: [docs/SKILL_OUTPUT_FIX.md](docs/SKILL_OUTPUT_FIX.md)

```bash
GATEWAY_TOKEN="<token from .env>"
API="http://localhost:18790"

# Create ga-trong-tre (Manager/Lead)
# Profile: full (gen media + deliver + spawn worker + post Facebook)
curl -X POST "$API/v1/agents" \
  -H "Authorization: Bearer $GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_key": "ga-trong-tre",
    "display_name": "Gà Trống Tre",
    "agent_type": "predefined",
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "tools_config": {
      "profile": "full",
      "team_tasks": {"enabled": true},
      "allow": ["create_image", "create_video", "send_file", "message", "workstation_exec"]
    }
  }'

# Worker: Cây Bút (text only — không cần media gen, nhưng cần deliver message)
curl -X POST "$API/v1/agents" \
  -H "Authorization: Bearer $GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_key": "viet-bai-fb",
    "display_name": "Cây Bút",
    "agent_type": "predefined",
    "provider": "anthropic",
    "model": "claude-sonnet-5",
    "tools_config": {
      "profile": "full",
      "team_tasks": {"enabled": true},
      "allow": ["message", "send_file"]
    }
  }'

# Worker: Tạo Ảnh (CẦN create_image + send_file để trả ảnh về Telegram)
curl -X POST "$API/v1/agents" \
  -H "Authorization: Bearer $GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_key": "tao-anh",
    "display_name": "Tạo Ảnh",
    "agent_type": "predefined",
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "tools_config": {
      "profile": "full",
      "team_tasks": {"enabled": true},
      "allow": ["create_image", "send_file", "message"]
    }
  }'

# Worker: Làm Video (CẦN create_video + send_file + workstation_exec cho ffmpeg)
curl -X POST "$API/v1/agents" \
  -H "Authorization: Bearer $GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_key": "lam-video",
    "display_name": "Làm Video",
    "agent_type": "predefined",
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "tools_config": {
      "profile": "full",
      "team_tasks": {"enabled": true},
      "allow": ["create_video", "create_image", "send_file", "message", "workstation_exec"]
    }
  }'
```

> **Update agent đã tồn tại:** nếu agent đã tạo, dùng `PUT /v1/agents/{id}` với cùng `tools_config` để cập nhật profile. Xem `scripts/fix-agent-tools.sh`.

### 3.3 Create Team

```bash
# Via WebSocket RPC (use goclaw CLI or a WS client)
# teams.create with:
#   name: "Đội Content Gà Trống Tre"
#   lead: "ga-trong-tre"
#   members: ["viet-bai-fb", "tao-anh", "lam-video"]
```

### 3.4 Setup Telegram Channels

```bash
# Via GoClaw UI dashboard
# Or via API:
curl -X POST "$API/v1/channels/telegram/instances" \
  -H "Authorization: Bearer $GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "<ga-trong-tre-uuid>",
    "token": "<telegram-bot-token>",
    "name": "ga-trong-tre",
    "config": {"allow_from": ["6880126421"]}
  }'
```

### 3.5 Sync Framework Files

```bash
# Clone framework repo to VPS
git clone https://github.com/congsang1294/goclaw-agent.git /opt/goclaw-agent

# Copy context files to workspaces
cp /opt/goclaw-agent/agent/AGENTS.md /app/workspace/ga-trong-tre/context-files/
cp /opt/goclaw-agent/agent/SOUL.md /app/workspace/ga-trong-tre/context-files/
cp /opt/goclaw-agent/agent/HEARTBEAT.md /app/workspace/ga-trong-tre/context-files/
cp /opt/goclaw-agent/agent/USER.md /app/workspace/ga-trong-tre/context-files/

# Copy skill files
cp /opt/goclaw-agent/skills/viet-bai-facebook/SKILL.md /app/workspace/viet-bai-fb/
cp /opt/goclaw-agent/skills/sang-tao-creative-fb/SKILL.md /app/workspace/tao-anh/
cp /opt/goclaw-agent/skills/tao-video-ai/SKILL.md /app/workspace/lam-video/

# Copy worker context files
for w in viet-bai-fb tao-anh lam-video; do
  cp /opt/goclaw-agent/agent/$w/AGENTS.md /app/workspace/$w/context-files/
  cp /opt/goclaw-agent/agent/$w/SOUL.md /app/workspace/$w/context-files/
  cp /opt/goclaw-agent/knowledge/brand-voice.md /app/workspace/$w/context-files/
  cp /opt/goclaw-agent/knowledge/knowledge-base.md /app/workspace/$w/context-files/
done
```

---

## 4. Update Deployment

```bash
cd /opt/goclaw-agent
git pull origin main

# Sync context files (see section 3.5)
# Restart GoClaw to pick up changes
docker restart goclaw-bai-13-goclaw-1
```

---

## 5. Rollback

```bash
# Rollback GoClaw version
cd /opt/goclaw && git checkout <previous-tag>
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d --build

# Rollback framework files
cd /opt/goclaw-agent && git checkout <previous-tag>
# Re-sync files (section 3.5)
docker restart goclaw-bai-13-goclaw-1
```

---

## 6. Verification Checklist

- [ ] `docker ps` — both containers healthy
- [ ] `curl localhost:18790/health` — HTTP 200
- [ ] Telegram bot responds to messages
- [ ] Agents exist in DB: `SELECT * FROM agents`
- [ ] Team exists: `SELECT * FROM agent_teams`
- [ ] Team members match: `SELECT * FROM agent_team_members`
- [ ] Context files present in each workspace
- [ ] SKILL.md present for each worker
- [ ] Providers are enabled: `SELECT * FROM llm_providers`
