#!/bin/sh
set -eu

WORKSPACE_SKILL_DIR="${WORKSPACE_SKILL_DIR:-/var/lib/docker/volumes/goclaw_goclaw-workspace/_data/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt}"
GOCLAW_UID="${GOCLAW_UID:-1000}"
GOCLAW_GID="${GOCLAW_GID:-1000}"

if [ ! -d "$WORKSPACE_SKILL_DIR" ]; then
  echo "[FAIL] Không tìm thấy workspace skill: $WORKSPACE_SKILL_DIR" >&2
  echo "       Deploy skill trước bằng docker cp + chown, sau đó chạy script này." >&2
  exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "[FAIL] setup_goclaw.sh cần chạy bằng root để sửa owner/quyền." >&2
  exit 1
fi

mkdir -p "$WORKSPACE_SKILL_DIR/output"
chown -R "$GOCLAW_UID:$GOCLAW_GID" "$WORKSPACE_SKILL_DIR"
find "$WORKSPACE_SKILL_DIR" -type d -exec chmod 755 {} \;
find "$WORKSPACE_SKILL_DIR" -type f -exec chmod 644 {} \;
find "$WORKSPACE_SKILL_DIR/scripts" -type f -name "*.sh" -exec chmod 755 {} \;

chown -R "$GOCLAW_UID:$GOCLAW_GID" "$WORKSPACE_SKILL_DIR/output"
chmod 775 "$WORKSPACE_SKILL_DIR/output"

if [ -f "$WORKSPACE_SKILL_DIR/.env" ]; then
  chown root:"$GOCLAW_GID" "$WORKSPACE_SKILL_DIR/.env"
  chmod 640 "$WORKSPACE_SKILL_DIR/.env"
fi

echo "[OK] GoClaw permissions configured: $WORKSPACE_SKILL_DIR"
echo "     .env=640 root:$GOCLAW_GID · output=775 $GOCLAW_UID:$GOCLAW_GID"
