#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# bind-workstation.sh — Fix lỗi "no workstation bound to agent"
#
# Nguyên nhân (xem docs/WORKSTATION_SETUP.md):
#   GoClaw KHÔNG bind workstation từ goclaw.yml. Workstation phải được:
#     1. tạo qua REST  → POST /v1/workstations            (bảng workstations)
#     2. link agent   → WebSocket RPC workstations.linkAgent
#                                                       (bảng agent_workstation_links)
#     3. mở allowlist → POST /v1/workstations/{id}/permissions
#   Lỗi "no workstation bound to agent" = thiếu row trong agent_workstation_links.
#
# Script này tự động hóa cả 3 bước cho 1 workstation + N agent.
#
# Cách dùng:
#   ./scripts/bind-workstation.sh                    # mặc định: all 4 agent
#   ./scripts/bind-workstation.sh --scope manager-only
#   ./scripts/bind-workstation.sh --scope workers-only
#   GOCRAW_HOST=http://localhost:18790 ./scripts/bind-workstation.sh
#
# Env:
#   GOCLAW_HOST          (default http://localhost:18790)
#   GOCLAW_GATEWAY_TOKEN (admin token — BẮT BUỘC)
#   WORKSTATION_KEY      (default ga-trong-tre-docker)
#   WORKSTATION_IMAGE    (default goclaw-workspace:latest)
#   DOCKER_SOCKET        (default /var/run/docker.sock)
#   DEFAULT_CWD          (default /app/workspace/ga-trong-tre)
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ─── Config ────────────────────────────────────────────────────────────
HOST="${GOCLAW_HOST:-http://localhost:18790}"
WS_KEY="${WORKSTATION_KEY:-ga-trong-tre-docker}"
WS_IMAGE="${WORKSTATION_IMAGE:-goclaw-workspace:latest}"
DOCKER_SOCKET="${DOCKER_SOCKET:-/var/run/docker.sock}"
DEFAULT_CWD="${DEFAULT_CWD:-/app/workspace/ga-trong-tre}"

# Binaries mà skill cần (mặc định seed chỉ echo,ls,cat,git,... → phải thêm)
ALLOWLIST_BINARIES=(python3 python pip3 pip ffmpeg ffprobe convert montage gm node npm)

# Phạm vi agent cần bind
SCOPE="all"

# ─── Helpers ───────────────────────────────────────────────────────────
log()  { printf '\033[1;34m▸ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m⚠ %s\033[0m\n' "$*" >&2; }
die()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# jq có sẵn không?
command -v jq >/dev/null 2>&1 || die "Cần cài 'jq'. Cài: apt-get install -y jq (hoặc brew install jq)"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)        SCOPE="$2"; shift 2 ;;
    --scope=*)      SCOPE="${1#*=}"; shift ;;
    -h|--help)
      sed -n '2,30p' "$0"; exit 0 ;;
    *) die "Tham số không rõ: $1" ;;
  esac
done

# Chọn agent theo scope
case "$SCOPE" in
  all)            AGENTS=(ga-trong-tre viet-bai-fb tao-anh lam-video) ;;
  manager-only)   AGENTS=(ga-trong-tre) ;;
  workers-only)   AGENTS=(viet-bai-fb tao-anh lam-video) ;;
  *) die "--scope phải là: all | manager-only | workers-only" ;;
esac

[[ -n "${GOCLAW_GATEWAY_TOKEN:-}" ]] || die "Thiếu GOCLAW_GATEWAY_TOKEN (admin token). Export từ .env"

AUTH=(-H "Authorization: Bearer $GOCLAW_GATEWAY_TOKEN" -H "Content-Type: application/json")

# ─── Health check ──────────────────────────────────────────────────────
log "Kiểm tra gateway tại $HOST ..."
code=$(curl -s -o /dev/null -w '%{http_code}' "$HOST/health" 2>/dev/null || true)
[[ "$code" == "200" ]] || die "Gateway không healthy (HTTP $code). Kiểm GOCLAW_HOST + docker ps"
ok "Gateway OK"

# ─── Bước 1: Tạo (hoặc tái sử dụng) workstation ────────────────────────
log "Tìm workstation '$WS_KEY' ..."
existing=$(curl -s "${AUTH[@]}" "$HOST/v1/workstations" | jq -r \
  ".workstations[]? | select(.workstationKey==\"$WS_KEY\") | .id" || true)

if [[ -n "$existing" ]]; then
  WS_ID="$existing"
  ok "Workstation đã tồn tại (id=$WS_ID) — tái sử dụng"
else
  log "Tạo workstation '$WS_KEY' (docker backend) ..."
  resp=$(curl -s -w '\n%{http_code}' "${AUTH[@]}" -X POST "$HOST/v1/workstations" -d "$(cat <<JSON
{
  "workstationKey": "$WS_KEY",
  "name": "Gà Trống Tre Docker Workspace",
  "backendType": "docker",
  "metadata": {
    "image": "$WS_IMAGE",
    "socketPath": "$DOCKER_SOCKET"
  },
  "defaultCwd": "$DEFAULT_CWD"
}
JSON
)")
  http_code="${resp##*$'\n'}"; body="${resp%$'\n'*}"
  [[ "$http_code" =~ ^(200|201)$ ]] || die "Tạo workstation thất bại (HTTP $http_code): $body"
  WS_ID=$(echo "$body" | jq -r '.workstation.id')
  ok "Đã tạo workstation id=$WS_ID"
fi

# ─── Bước 2: Mở allowlist ─────────────────────────────────────────────
log "Kiểm tra + mở allowlist binaries cho skill ..."
mapfile -t current < <(curl -s "${AUTH[@]}" "$HOST/v1/workstations/$WS_ID/permissions" \
  | jq -r '.permissions[]? | select(.enabled==true) | .pattern')

for bin in "${ALLOWLIST_BINARIES[@]}"; do
  if printf '%s\n' "${current[@]}" | grep -qx "$bin"; then
    : # đã có
  else
    curl -s -o /dev/null "${AUTH[@]}" -X POST "$HOST/v1/workstations/$WS_ID/permissions" \
      -d "{\"pattern\":\"$bin\"}" || warn "Không thêm được allowlist: $bin"
  fi
done
ok "Allowlist: ${ALLOWLIST_BINARIES[*]}"

# ─── Bước 3: Link agent ↔ workstation ─────────────────────────────────
# linkAgent chỉ có qua WebSocket. Dùng websocat nếu có, không thì patch thẳng DB.
link_via_ws() {
  local agent_key="$1"
  command -v websocat >/dev/null 2>&1 || return 1

  # Lấy agent UUID từ REST
  local agent_uuid
  agent_uuid=$(curl -s "${AUTH[@]}" "$HOST/v1/agents" \
    | jq -r --arg k "$agent_key" '.agents[]? | select(.agent_key==$k) | .id')
  [[ -n "$agent_uuid" ]] || return 1

  websocat -1 "ws://$(printf '%s' "$HOST" | sed 's#^http##; s#^s##')/ws" >/dev/null 2>&1 <<WS || return 1
{"type":"req","id":"link-$agent_key","method":"connect","params":{"token":"$GOCLAW_GATEWAY_TOKEN"}}
{"type":"req","id":"link-$agent_key","method":"workstations.linkAgent","params":{"workstationId":"$WS_ID","agentId":"$agent_uuid","isDefault":true}}
WS
}

link_via_db() {
  # Fallback: insert thẳng vào Postgres (nếu script chạy trên VPS có quyền)
  local agent_key="$1"
  local pg="docker exec goclaw-bai-13-postgres-1 psql -U goclaw -d goclaw -t"
  local agent_uuid
  agent_uuid=$($pg -c "SELECT id FROM agents WHERE agent_key='$agent_key';" 2>/dev/null | tr -d '[:space:]')
  [[ -n "$agent_uuid" ]] || return 1
  $pg -c "INSERT INTO agent_workstation_links(agent_id, workstation_id, is_default, tenant_id)
          VALUES('$agent_uuid', '$WS_ID', true,
                 (SELECT tenant_id FROM agents WHERE id='$agent_uuid'))
          ON CONFLICT (agent_id, workstation_id) DO UPDATE SET is_default=true;" >/dev/null 2>&1
}

for agent in "${AGENTS[@]}"; do
  log "Link agent '$agent' ↔ workstation ..."
  if link_via_ws "$agent"; then
    ok "Linked '$agent' (qua WebSocket)"
  elif link_via_db "$agent"; then
    ok "Linked '$agent' (qua DB fallback)"
  else
    warn "Không link được '$agent' tự động. Link thủ công qua dashboard hoặc:"
    echo "    WS: workstations.linkAgent {workstationId:\"$WS_ID\", agentId:<uuid của $agent>, isDefault:true}"
  fi
done

# ─── Bước 4: Test connectivity ────────────────────────────────────────
log "Test connectivity workstation ..."
test_code=$(curl -s -o /dev/null -w '%{http_code}' "${AUTH[@]}" -X POST "$HOST/v1/workstations/$WS_ID/test")
[[ "$test_code" =~ ^(200|204|501)$ ]] \
  && ok "Test OK (501 = stub, dùng echo exec để verify thật)" \
  || warn "Test trả HTTP $test_code — xem logs"

# ─── Tóm tắt ──────────────────────────────────────────────────────────
echo
ok "══════════ XONG ══════════"
echo "  Workstation : $WS_KEY (id=$WS_ID)"
echo "  Allowlist   : ${ALLOWLIST_BINARIES[*]}"
echo "  Agents      : ${AGENTS[*]}"
echo
echo "Verify:"
echo "  ./scripts/verify-workstation.sh"
