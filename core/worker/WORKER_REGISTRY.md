# WORKER REGISTRY

> **File:** `core/worker/WORKER_REGISTRY.md`
> **Role:** Instructions for managing workers — register, update, remove
> **Part of:** Worker Registry
> **Phase:** 2 — Worker Integration

---

## 1. Mục đích

Worker Registry là **single source of truth** cho tất cả Workers trong Framework.
Manager đọc `WORKER_REGISTRY.yaml` để biết:

- Có bao nhiêu workers đang hoạt động
- Worker nào làm gì (skills, role)
- Worker nào có Telegram binding không
- Cách dispatch task đến worker

**Nguyên tắc cốt lõi:**
- **Config-driven:** Worker được đăng ký qua config, không hardcode trong core
- **N Workers:** Framework hỗ trợ N workers — Manager đọc từ config, không hardcode
- **Add/Remove = chỉ sửa config:** Không cần sửa core/*.md

---

## 2. Worker Lifecycle

```
TẠO MỚI:
  1. Định nghĩa worker trong WORKER_REGISTRY.yaml
  2. Tạo agent/<worker-id>/AGENTS.md (task contract)
  3. Tạo agent/<worker-id>/SOUL.md (identity)
  4. Tạo skill (nếu chưa có) trong skills/<skill-name>/SKILL.md
  5. Thêm route trong ROUTING_TABLE.yaml
  6. Thêm workstation + binding trong goclaw.yml

XÓA:
  1. Xóa entry khỏi WORKER_REGISTRY.yaml
  2. Xóa route khỏi ROUTING_TABLE.yaml
  3. (Tùy chọn) Xóa agent/<worker-id>/
  4. (Tùy chọn) Xóa binding khỏi goclaw.yml
  
SỬA:
  - Sửa trực tiếp entry trong WORKER_REGISTRY.yaml
  - Không cần sửa core/*.md
```

---

## 3. Worker Registry Schema

```yaml
workers:
  - id: <agent_id>              # Bắt buộc: unique, khớp @agentId
    name: "<display_name>"      # Bắt buộc: tên hiển thị
    role: "<role_description>"  # Bắt buộc: vai trò
    status: active               # active | inactive | planned
    telegram:
      binding: group             # group | direct | none
      mention: "@<agent_id>"    # Cách mention trong group
    skills:
      - skill-name              # Danh sách skills (1 hoặc nhiều)
    dispatch_to: "..."          # Cách dispatch task
    input_format: "..."         # Mô tả input
    output_format: "..."        # Mô tả output
    timeout: <seconds>          # Timeout mặc định
    restrictions:               # Các giới hạn (optional)
      - "❌ Không làm X"
```

### Field Descriptions

| Field | Bắt buộc | Mô tả |
|-------|---------|-------|
| `id` | ✅ | Agent ID — khớp với `@agentId` trong group chat và goclaw.yml |
| `name` | ✅ | Tên hiển thị (Tiếng Việt, có dấu) |
| `role` | ✅ | Mô tả vai trò bằng tiếng Việt |
| `status` | ✅ | `active` = đang hoạt động; `inactive` = tạm ngưng; `planned` = kế hoạch |
| `telegram.binding` | ✅ | `group` = worker ở group chat; `direct` = DM; `none` = không có Telegram |
| `telegram.mention` | ✅ | Cú pháp mention trong group chat |
| `skills` | ✅ | Danh sách skill IDs (phải có SKILL.md tương ứng) |
| `dispatch_to` | ✅ | Mô tả cách dispatch (cho Manager đọc) |
| `input_format` | ✅ | Worker cần input gì để chạy |
| `output_format` | ✅ | Worker trả về output gì |
| `timeout` | ✅ | Timeout mặc định (giây) |
| `restrictions` | ❌ | Danh sách giới hạn (cho Manager và Worker đọc) |

---

## 4. Manager sử dụng Worker Registry như thế nào

Khi Manager cần dispatch task, flow chuẩn là:

```
1. INTENT_ANALYZER xác định intent
2. ROUTING_TABLE.yaml map intent → worker
3. Manager đọc WORKER_REGISTRY.yaml để kiểm tra:
   - Worker có tồn tại không?
   - Worker có skill cần thiết không?
   - Worker có active không?
   - Worker có Telegram binding không?
4. DISPATCHER dùng thông tin từ registry để dispatch
5. Kanban theo dõi task status
```

### Các câu hỏi Manager có thể hỏi Worker Registry:

| Câu hỏi | Cách trả lời |
|---------|-------------|
| "Có worker nào làm skill X không?" | Đọc `workers[].skills` — tìm worker có skill X |
| "Worker viet-bai-fb còn active không?" | Kiểm tra `workers[].status` == active |
| "Dispatch đến worker nào cho intent write_post?" | Đọc `ROUTING_TABLE.yaml` → `WORKER_REGISTRY.yaml` |
| "Có bao nhiêu workers đang active?" | Đếm `workers[].status == active` |
| "Worker tao-anh có Telegram binding không?" | Kiểm tra `workers[].telegram.binding` |

---

## 5. Quy tắc

- **Không hardcode worker trong core/**: Manager luôn đọc từ config
- **WORKER_REGISTRY.yaml là nguồn duy nhất**: Mọi thông tin worker đều ở đây
- **goclaw.yml là config GoClaw runtime**: Worker registry không thay thế goclaw.yml, chỉ bổ sung metadata
- **ROUTING_TABLE.yaml quyết định routing**: Worker registry chỉ cung cấp thông tin worker
- **Thêm worker = 5 bước**: registry → agent → skill → route → goclaw.yml

---

## 6. Ví dụ: Thêm Worker mới

Giả sử cần thêm **Email Marketer**:

### Bước 1: Thêm vào WORKER_REGISTRY.yaml

```yaml
  - id: email-marketer
    name: "Email Marketer"
    role: "Email Sequence Creator"
    status: active
    telegram:
      binding: group
      mention: "@email-marketer"
    skills:
      - email-copy
    dispatch_to: "@email-marketer in group chat"
    input_format: "Campaign brief + audience segment"
    output_format: |
      Email sequence: welcome → nurture → offer
    timeout: 180
    restrictions:
      - "❌ Không viết Facebook post"
      - "❌ Không tạo ảnh"
```

### Bước 2-5: Tạo các file còn lại

```
agent/email-marketer/AGENTS.md  (task contract)
agent/email-marketer/SOUL.md    (identity)
skills/email-copy/SKILL.md      (skill definition)
core/router/ROUTING_TABLE.yaml  (route entry)
goclaw.yml                      (workstation + binding)
```

---

## 7. Liên kết

- **Config:** `WORKER_REGISTRY.yaml`
- **Routing:** `core/router/ROUTING_TABLE.yaml`
- **Dispatcher:** `core/dispatcher/DISPATCHER.md`
- **Orchestration:** `core/manager/ORCHESTRATION.md`
- **Agent maps:** `docs/AGENT_MAP.md`
