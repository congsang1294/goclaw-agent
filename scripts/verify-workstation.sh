#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# verify-workstation.sh — Kiểm tra workstation đã bind đúng chưa
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail

HOST="${GOCLAW_HOST:-http://localhost:18790}"
WS_KEY="${WORKSTATION_KEY:-ga-trong-tre-docker}"

command -v jq >/dev/null 2>&1 || { echo "Cần jq"; exit 1; }
[[ -n "${GOCLAW_GATEWAY_TOKEN:-}" ]] || { echo "Thiếu GOCLAW_GATEWAY_TOKEN"; exit 1; }

AUTH=(-H "Authorization: Bearer $GOCLAW_GATEWAY_TOKEN" -H "Content-Type: application/json")

log()  { printf '\033[1;34m▸ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
fail() { printf '\033[1;31m✗ %s\033[0m\n' "$*"; }

# ─── Workstation tồn tại? ─────────────────────────────────────────────
log "1. Workstation '$WS_KEY'"
ws=$(curl -s "${AUTH[@]}" "$HOST/v1/workstations" \
  | jq -e --arg k "$WS_KEY" '.workstations[]? | select(.workstationKey==$k)')
if [[ -z "$ws" ]]; then
  fail "Workstation '$WS_KEY' KHÔNG tồn tại → chạy bind-workstation.sh"
  exit 1
fi
WS_ID=$(echo "$ws" | jq -r '.id')
ok "Tồn tại (id=$WS_ID, active=$(echo "$ws" | jq -r '.active'))"

# ─── Allowlist ────────────────────────────────────────────────────────
log "2. Allowlist"
curl -s "${AUTH[@]}" "$HOST/v1/workstations/$WS_ID/permissions" \
  | jq -r '.permissions[]? | select(.enabled==true) | "  ✓ \(.pattern)"'
ok "(cho phép các binaries trên)"

# ─── Agent links (qua DB) ─────────────────────────────────────────────
log "3. Agent ↔ workstation links (agent_workstation_links)"
if docker exec goclaw-bai-13-postgres-1 psql -U goclaw -d goclaw -c \
  "SELECT a.agent_key, l.is_default
   FROM agent_workstation_links l
   JOIN agents a ON a.id=l.agent_id
   WHERE l.workstation_id='$WS_ID';" 2>/dev/null; then
  ok "Links ở trên"
else
  warn "Không query được Postgres — kiểm link qua dashboard REST:"
  echo "  GET $HOST/v1/agents  (lấy UUID)"
  echo "  GET $HOST/v1/workstations/$WS_ID"
fi

# ─── Activity log gần nhất ────────────────────────────────────────────
log "4. Activity log (5 gần nhất)"
curl -s "${AUTH[@]}" "$HOST/v1/workstations/$WS_ID/activity?limit=5" \
  | jq -r '.activity[]? | "  [\(.action)] \(.cmdPreview // "—") (exit=\(.exitCode // "-"))"'

echo
ok "Xong. Nếu link đầy đủ → 'no workstation bound to agent' đã hết."
