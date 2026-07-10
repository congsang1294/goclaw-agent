#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# deploy.sh — Deploy goclaw-agent lên VPS
# Chạy trên VPS sau khi git pull
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail

log()  { printf '\033[1;34m▸ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# Đường dẫn
REPO_DIR="/opt/goclaw-agent"
GOCLAW_CONTAINER="goclaw-bai-13-goclaw-1"
POSTGRES_CONTAINER="goclaw-bai-13-postgres-1"

cd "$REPO_DIR"

# ─── Bước 1: Git pull ───────────────────────────────────────────────
log "1. Git pull..."
git pull origin main || die "Git pull failed"
ok "Pull OK"

# ─── Bước 2: Kiểm tra API keys ──────────────────────────────────────
log "2. Kiểm tra API keys cần thiết..."
MISSING=""
[[ -z "${GOCLAW_GATEWAY_TOKEN:-}" ]] && MISSING="$MISSING GOCLAW_GATEWAY_TOKEN"
[[ -z "${FB_PAGE_ID:-}" ]] && MISSING="$MISSING FB_PAGE_ID"
[[ -z "${FB_PAGE_TOKEN:-}" ]] && MISSING="$MISSING FB_PAGE_TOKEN"
if docker exec "$POSTGRES_CONTAINER" psql -U goclaw -d goclaw -c \
  "SELECT count(*) FROM llm_providers WHERE enabled=true;" 2>/dev/null | grep -q "0"; then
  log "  ⚠️  Chưa có LLM provider nào enabled. Kiểm tra OPENAI_API_KEY trong .env của GoClaw."
fi
[[ -n "$MISSING" ]] && log "  ⚠️  Thiếu env vars:$MISSING"
ok "Kiểm tra xong"

# ─── Bước 3: Chạy bind workstation ──────────────────────────────────
log "3. Bind workstation..."
if [[ -f "$REPO_DIR/scripts/bind-workstation.sh" ]]; then
  bash "$REPO_DIR/scripts/bind-workstation.sh" --scope all || log "  ⚠️  bind-workstation có lỗi"
  ok "Workstation binding done"
else
  log "  ⚠️  scripts/bind-workstation.sh chưa có"
fi

# ─── Bước 4: Fix agent tools ────────────────────────────────────────
log "4. Fix agent tools profile..."
if [[ -f "$REPO_DIR/scripts/fix-agent-tools.sh" ]]; then
  bash "$REPO_DIR/scripts/fix-agent-tools.sh" || log "  ⚠️  fix-agent-tools có lỗi"
  ok "Agent tools fixed"
else
  log "  ⚠️  scripts/fix-agent-tools.sh chưa có"
fi

# ─── Bước 5: Sync context files ─────────────────────────────────────
log "5. Sync context files to workspaces..."
WORKSPACE_BASE="/app/workspace"
for agent in ga-trong-tre viet-bai-fb tao-anh lam-video; do
  ws_dir="$WORKSPACE_BASE/$agent/context-files"
  docker exec "$GOCLAW_CONTAINER" mkdir -p "$ws_dir" 2>/dev/null
  if [[ -d "$REPO_DIR/agent/$agent" ]]; then
    docker cp "$REPO_DIR/agent/$agent/AGENTS.md" "$GOCLAW_CONTAINER:$ws_dir/" 2>/dev/null
    docker cp "$REPO_DIR/agent/$agent/SOUL.md" "$GOCLAW_CONTAINER:$ws_dir/" 2>/dev/null
  fi
  docker cp "$REPO_DIR/knowledge/brand-voice.md" "$GOCLAW_CONTAINER:$ws_dir/" 2>/dev/null
  docker cp "$REPO_DIR/knowledge/knowledge-base.md" "$GOCLAW_CONTAINER:$ws_dir/" 2>/dev/null
done
# Gà cần thêm file
docker cp "$REPO_DIR/agent/AGENTS.md" "$GOCLAW_CONTAINER:$WORKSPACE_BASE/ga-trong-tre/context-files/" 2>/dev/null
docker cp "$REPO_DIR/agent/HEARTBEAT.md" "$GOCLAW_CONTAINER:$WORKSPACE_BASE/ga-trong-tre/context-files/" 2>/dev/null
docker cp "$REPO_DIR/agent/USER.md" "$GOCLAW_CONTAINER:$WORKSPACE_BASE/ga-trong-tre/context-files/" 2>/dev/null
docker cp "$REPO_DIR/agent/SOUL.md" "$GOCLAW_CONTAINER:$WORKSPACE_BASE/ga-trong-tre/context-files/" 2>/dev/null
ok "Context files synced"

# ─── Bước 6: Copy skill scripts vào workspace ───────────────────────
log "6. Copy skill scripts..."
for skill in tao-video-ai; do
  src="$REPO_DIR/skills/$skill/scripts"
  if [[ -d "$src" ]]; then
    docker cp "$src" "$GOCLAW_CONTAINER:$WORKSPACE_BASE/ga-trong-tre/scripts/" 2>/dev/null || true
  fi
done
ok "Skill scripts copied"

# ─── Bước 7: Restart GoClaw ─────────────────────────────────────────
log "7. Restart GoClaw..."
docker restart "$GOCLAW_CONTAINER"
sleep 3
health=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:18790/health 2>/dev/null || echo "000")
if [[ "$health" == "200" ]]; then
  ok "GoClaw healthy (HTTP 200)"
else
  log "  ⚠️  GoClaw health trả $health — kiểm tra docker logs"
fi

echo
ok "══════ DEPLOY XONG ══════"
echo "  Đã deploy: $(git log --oneline -1)"
echo "  Health: http://localhost:18790/health → $health"
echo "  Test: nhắn Telegram cho Gà: 'tạo ảnh' hoặc 'làm video'"