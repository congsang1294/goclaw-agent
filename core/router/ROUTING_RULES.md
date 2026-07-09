# ROUTING RULES

> **File:** `core/router/ROUTING_RULES.md`
> **Role:** Define how routing works — matching logic, priority, error handling
> **Part of:** Dynamic Router
> **Phase:** 1 — Core Framework

---

## 1. Mục đích

Router chịu trách nhiệm **map intent → worker**. Nó đọc `ROUTING_TABLE.yaml` và chọn route phù hợp nhất dựa trên intent từ `INTENT_ANALYZER.md`.

---

## 2. Cách hoạt động

```
Intent từ INTENT_ANALYZER
    │
    ▼
Tìm trong ROUTING_TABLE.yaml route có intent match
    │
    ├── Match tìm thấy? ──▶ Trả về { worker, skill, timeout }
    │
    └── Không match? ──▶ Báo lỗi "no route found"
```

---

## 3. Matching Rules

### 3.1 Exact Match (ưu tiên cao nhất)

Intent từ Analyzer khớp chính xác với 1 intent trong routing table.
→ Dùng route đó.

Ví dụ: `write_post` → route `write_post` → worker `viet-bai-fb`.

### 3.2 Multi-Intent Match (ít phổ biến)

Nếu user nói "viết bài và tạo ảnh" cùng lúc:
- Intent Analyzer trả về `team_sync`
- Router: `team_sync` → Manager tự lập plan

### 3.3 Fallback

Nếu không có route nào match:
- Manager hỏi user: "Anh muốn làm gì ạ?"
- Hoặc dùng route `unknown` 

---

## 4. Route đầu ra

Khi route được chọn, nó trả về:

```json
{
  "route_id": "write_post",
  "worker": "viet-bai-fb",
  "skill": "viet-bai-facebook",
  "timeout": 120,
  "plan_type": "simple"
}
```

**Các trường:**
| Field | Mô tả |
|-------|-------|
| `route_id` | ID của route trong ROUTING_TABLE.yaml |
| `worker` | Agent ID để dispatch task đến |
| `skill` | Skill name để worker thực thi |
| `timeout` | Thời gian tối đa (giây) trước khi timeout |
| `plan_type` | Plan type: Manager quyết định cần Planner không |

---

## 5. Thêm route mới

```yaml
# Bước 1: Thêm entry vào ROUTING_TABLE.yaml
- id: my_new_route
  intents: [my_new_intent]
  worker: my-worker
  skill: my-skill
  timeout: 120s
  plan_type: simple

# Bước 2: Đảm bảo intent `my_new_intent` có trong INTENT_ANALYZER.md
# Bước 3: Đảm bảo worker `my-worker` có AGENTS.md + SOUL.md
# Bước 4: Đảm bảo skill `my-skill` có SKILL.md
# Bước 5: Nếu worker mới → thêm vào goclaw.yml
```

---

## 6. Route validation rules

| Điều kiện | Hợp lệ? | Xử lý nếu không |
|-----------|---------|-----------------|
| worker tồn tại trong WORKER_REGISTRY.yaml | ✅ Bắt buộc | Báo lỗi khi tạo task |
| skill có SKILL.md | ✅ Bắt buộc | Skill không chạy được |
| timeout > 0 | ✅ Bắt buộc | Dùng default 120s |
| intent có trong INTENT_ANALYZER | ✅ Khuyến nghị | Intent không bao giờ được phân tích |
| plan_type hợp lệ | ✅ Bắt buộc | Mặc định simple |

---

## 7. Liên kết

- **Config:** `ROUTING_TABLE.yaml`
- **Input từ:** `INTENT_ANALYZER.md` (intent)
- **Output đến:** `PLANNER.md` (để tạo task) và `DISPATCHER.md` (để gửi task)
- **ORCHESTRATION.md** gọi router như 1 bước trong flow
