#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# fix-agent-tools.sh — Fix lỗi skill chạy xong KHÔNG trả output về Telegram
#
# Nguyên nhân (xem docs/SKILL_OUTPUT_FIX.md):
#   - Tool profile `coding` có create_image/create_video (gen được)
#     nhưng KHÔNG có message/send_file (gửi về Telegram được).
#   - Chỉ profile `full` mới có cả gen + deliver.
#   - Tool `delegate` đã bị gỡ → đổi sang team_tasks + spawn.
#
# Script này cập nhật tools_config cho 4 agent → profile `full`.
# Chạy trên VPS hoặc máy có quyền gọi GoClaw API.
#
# Cách dùng:
#   export GOCLAW_GATEWAY_TOKEN="<admin token>"
#   export GOCLAW_HOST="http://localhost:18790"
#   ./scripts/fix-agent-tools.sh
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail

HOST="${GOCLAW_HOST:-http://localhost:18790}"
command -v jq >/dev/null 2>&1 || { echo "Cần jq"; exit 1; }
[[ -n "${GOCLAW_GATEWAY_TOKEN:-}" ]] || { echo "Thiếu GOCLAW_GATEWAY_TOKEN"; exit 1; }
AUTH=(-H "Authorization: Bearer $GOCLAW_GATEWAY_TOKEN" -H "Content-Type: application/json")

log()  { printf '\033[1;34m▸ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m⚠ %s\033[0m\n' "$*" >&2; }
die()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# tools_config per agent (profile=full + tools cần thiết)
# LƯU Ý: delegate đã bị gỡ, KHÔNG đưa vào.
declare -A ALLOW=(
  [ga-trong-tre]='["create_image","create_video","send_file","message","workstation_exec"]'
  [viet-bai-fb]='["message","send_file"]'
  [tao-anh]='["create_image","send_file","message"]'
  [lam-video]='["create_video","create_image","send_file","message","workstation_exec"]'
)

# Health check
code=$(curl -s -o /dev/null -w '%{http_code}' "$HOST/health" || true)
[[ "$code" == "200" ]] || die "Gateway không healthy (HTTP $code)"

for agent_key in ga-trong-tre viet-bai-fb tao-anh lam-video; do
  log "Cập nhật tools_config cho '$agent_key' ..."

  # Tìm agent UUID
  agent_id=$(curl -s "${AUTH[@]}" "$HOST/v1/agents" \
    | jq -r --arg k "$agent_key" '.agents[]? | select(.agent_key==$k) | .id')

  if [[ -z "$agent_id" ]]; then
    warn "Agent '$agent_key' chưa tồn tại — tạo trước qua DEPLOYMENT.md §3.2"
    continue
  fi

  # PUT cập nhật tools_config (profile=full + allow list)
  resp=$(curl -s -w '\n%{http_code}' "${AUTH[@]}" -X PUT "$HOST/v1/agents/$agent_id" -d "$(cat <<JSON
{
  "tools_config": {
    "profile": "full",
    "team_tasks": {"enabled": true},
    "allow": ${ALLOW[$agent_key]}
  }
}
JSON
)")
  http_code="${resp##*$'\n'}"; body="${resp%$'\n'*}"

  if [[ "$http_code" =~ ^(200|204)$ ]]; then
    ok "'$agent_key' → profile=full, allow=${ALLOW[$agent_key]}"
  else
    warn "'$agent_key' cập nhật fail (HTTP $http_code): $body"
    warn "Nếu API không nhận 'profile' ở cấp này, set qua config.json tools.profile=full rồi restart."
  fi
done

echo
ok "══════ XONG — restart GoClaw để apply ══════"
echo "  docker restart goclaw-bai-13-goclaw-1"
echo
echo "Verify: nhờ anh Sáng test 'tạo ảnh' / 'tạo video' qua Telegram."
echo "        Output (ảnh/video preview) phải về Telegram qua send_file."
