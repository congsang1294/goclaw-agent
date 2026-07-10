# Workstation Setup — Cách bind agent ↔ workstation ĐÚNG

> **File:** `docs/WORKSTATION_SETUP.md`
> **Fix lỗi:** `no workstation bound to agent`
> **Nguồn sự thật:** [goclaw-docs/advanced/workstations.md](https://github.com/nextlevelbuilder/goclaw-docs/blob/master/advanced/workstations.md)

---

## ❌ Hiểu sai phổ biến (chính là lỗi của repo trước đây)

Nhiều người nghĩ khai báo workstation trong `goclaw.yml` là đủ:

```yaml
# ❌ SAI — GoClaw KHÔNG đọc block này để bind workstation
agent:
  workstations:
    - name: ga-trong-tre-docker
      type: docker
```

**Thực tế:** khối đó chỉ là metadata tự viết. GoClaw runtime **bỏ qua** nó khi resolve workstation cho agent.

---

## ✅ Cách GoClaw thực sự bind workstation

Workstation binding đi qua **cơ sở dữ liệu**, không qua config file:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Tạo workstation                                          │
│    POST /v1/workstations  →  bảng `workstations`            │
│                                                              │
│ 2. Link agent ↔ workstation                                 │
│    WebSocket RPC `workstations.linkAgent`                   │
│                       →  bảng `agent_workstation_links`     │
│                                                              │
│ 3. Mở allowlist binaries                                    │
│    POST /v1/workstations/{id}/permissions                   │
│                       →  bảng `workstation_permissions`     │
└─────────────────────────────────────────────────────────────┘
```

Khi agent gọi `workstation_exec`, gateway lookup trong `agent_workstation_links`.
**Không có row → lỗi `no workstation bound to agent`.**

### Bảng DB liên quan (migration 062-064)

| Bảng | Vai trò |
|------|---------|
| `workstations` | Row định nghĩa workstation (backend ssh/docker, metadata mã hóa AES-256-GCM) |
| `agent_workstation_links` | Junction N:M agent↔workstation. PK `(agent_id, workstation_id)`. `is_default` = 1 default/agent |
| `workstation_permissions` | Allowlist binary (argv[0]). **Default-deny**, seed: `echo,pwd,ls,cat,git,whoami,hostname,date,uname,claude` |
| `workstation_activity` | Audit log mọi exec/deny (append-only) |

---

## 🚀 Fix nhanh (1 lệnh)

```bash
# Trên VPS
cd /opt/goclaw-agent
export GOCLAW_GATEWAY_TOKEN="<admin token từ .env>"
./scripts/bind-workstation.sh                    # bind tất cả 4 agent
# hoặc:
./scripts/bind-workstation.sh --scope manager-only   # chỉ Gà
./scripts/bind-workstation.sh --scope workers-only   # chỉ 3 worker
```

Script tự động: tạo workstation → mở allowlist → link agent → test.

Verify:
```bash
./scripts/verify-workstation.sh
```

---

## 🔧 Các lệnh thủ công (nếu cần)

### Tạo workstation (Docker backend)

```bash
curl -X POST http://localhost:18790/v1/workstations \
  -H "Authorization: Bearer $GOCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workstationKey": "ga-trong-tre-docker",
    "name": "Gà Trống Tre Docker Workspace",
    "backendType": "docker",
    "metadata": {
      "image": "goclaw-workspace:latest",
      "socketPath": "/var/run/docker.sock"
    },
    "defaultCwd": "/app/workspace/ga-trong-tre"
  }'
```

> `workstationKey` phải khớp regex `^[a-z0-9][a-z0-9-]{0,99}$` (kebab-case lowercase).

### Mở allowlist binaries cho skill

Seed mặc định **không có** `python3`, `ffmpeg`, `convert` → skill video/ảnh sẽ bị deny:

```bash
WS_ID="<id từ bước tạo>"
for bin in python3 python pip3 pip ffmpeg ffprobe convert montage gm node npm; do
  curl -X POST http://localhost:18790/v1/workstations/$WS_ID/permissions \
    -H "Authorization: Bearer $GOCLAW_GATEWAY_TOKEN" \
    -d "{\"pattern\": \"$bin\"}"
done
```

> **Quan trọng:** allowlist default-deny trên `argv[0]`. Nếu deny → xem `workstation_activity` sẽ có row `action=deny` với `denyReason`.

### Link agent ↔ workstation (WebSocket)

`linkAgent` **chỉ có qua WebSocket** (không có REST):

```jsonc
// ws://localhost:18790/ws
{"type":"req","id":"c","method":"connect","params":{"token":"<admin-token>"}}
{"type":"req","id":"l","method":"workstations.linkAgent",
 "params":{"workstationId":"<ws-uuid>","agentId":"<agent-uuid>","isDefault":true}}
```

Hoặc qua **dashboard GoClaw** (UI Workstations → Link Agent).

Hoặc **DB fallback** (chỉ khi có quyền psql):
```sql
INSERT INTO agent_workstation_links(agent_id, workstation_id, is_default, tenant_id)
VALUES ('<agent-uuid>','<ws-uuid>', true, '<tenant-id>')
ON CONFLICT (agent_id, workstation_id) DO UPDATE SET is_default=true;
```

---

## 🗺️ Workstation mapping cho team Gà Trống Tre

| Workstation | Backend | Default CWD | Linked Agents |
|-------------|---------|-------------|---------------|
| `ga-trong-tre-docker` | docker | `/app/workspace/ga-trong-tre` | ga-trong-tre, viet-bai-fb, tao-anh, lam-video |

**Dùng chung 1 workstation** cho cả 4 agent (link N:M là per-agent, `is_default` cũng per-agent → không xung đột).

### Ai cần workstation gì?

| Agent | Binaries cần | Lý do |
|-------|-------------|-------|
| 🐔 ga-trong-tre | `python3`, `curl` | Post bài cuối lên fanpage (Graph API) |
| ✍️ viet-bai-fb | (text only) | Viết caption — bind dự phòng |
| 🎨 tao-anh | `convert`, `gm` | Xử lý ảnh / paired caption |
| 🎬 lam-video | `python3`,`pip3`,`ffmpeg` | Render video (nặng nhất) |

---

## 🐞 Troubleshooting

| Triệu chứng | Nguyên nhân | Fix |
|-------------|------------|-----|
| `no workstation bound to agent` | Thiếu row trong `agent_workstation_links` | `bind-workstation.sh` |
| `binary 'python3' not allowed` | Allowlist thiếu binary | Thêm qua `POST /permissions` |
| `invalid slug: workstationKey` | Key có chữ hoa / underscore | Dùng kebab-case lowercase |
| `501 not implemented` từ `/test` | Test là stub | Verify bằng `echo` exec thật |
| WS link không kết nối | Token sai / agent UUID sai | Lấy UUID từ `GET /v1/agents` |
| Lỗi vẫn sau khi bind | GoClaw chưa reload link | `docker restart goclaw-bai-13-goclaw-1` |

---

*Schema dựa trên goclaw-docs commit `392f0fda` (2026-05-21). Nếu GoClaw update, kiểm lại `workstations.md`.*
