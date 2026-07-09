# INTENT ANALYZER

> **File:** `core/manager/INTENT_ANALYZER.md`
> **Role:** Parse user message → determine intent
> **Part of:** Manager (Gà Trống Tre)
> **Phase:** 1 — Core Framework

> **Note on worker/skill fields:** The `worker` and `skill` fields in the intent catalog below are **references** for quick lookup. The actual routing decision is made by `core/router/ROUTING_TABLE.yaml`, which is the single source of truth. When adding/removing workers, only update `ROUTING_TABLE.yaml` and `WORKER_REGISTRY.yaml` — do NOT modify this file's intent catalog for routing purposes.
> 
> **Ở Phase 2 trở đi:** `worker` và `skill` trong intent catalog chỉ mang tính tham khảo. Routing thực tế đọc từ ROUTING_TABLE.yaml và WORKER_REGISTRY.yaml.

---

## 1. Mục đích

Intent Analyzer chịu trách nhiệm **phân loại ý định của user** từ tin nhắn Telegram.
Nó biến câu nói tự nhiên thành một **intent** có cấu trúc để Planner xử lý tiếp.

**Đầu vào:** Tin nhắn Telegram từ anh Sáng hoặc khách hàng.
**Đầu ra:** Intent object `{ type, confidence, params }`.

---

## 2. Cơ chế hoạt động

### 2.1 Priority Order

1. **Explicit skill call** — `use_skill "skill-name"` → dùng ngay, không phân tích
2. **Compound intent detection** — Nếu message match nhiều intents → compound rules (mục 5.1)
3. **Keyword match** — So khớp với intent catalog bên dưới
4. **Context-aware** — Dùng lịch sử hội thoại gần nhất để xác định
5. **Ambiguous** — Nếu không rõ → hỏi 1 câu clarification

### 2.2 Intent Catalog

```yaml
intents:
  write_post:
    keywords: ["viết bài", "viết post", "làm caption", "viết content", "bài viết", "post facebook", "viết quảng cáo", "làm bài"]
    description: "Viết bài Facebook — Hook + Body + CTA"
    worker: viet-bai-fb
    skill: viet-bai-facebook
    plan_type: simple

  create_ideas:
    keywords: ["cho ý tưởng", "gợi ý góc viết", "3 ý tưởng", "idea", "concept"]
    description: "Tạo ý tưởng nội dung"
    worker: viet-bai-fb
    skill: viet-bai-facebook
    plan_type: simple

  create_image:
    keywords: ["tạo ảnh", "làm ảnh", "design", "hình quảng cáo", "creative", "visual", "gen ảnh"]
    description: "Tạo ảnh quảng cáo / creative"
    worker: tao-anh
    skill: sang-tao-creative-fb
    plan_type: simple

  create_video:
    keywords: ["làm video", "tạo video", "video reels", "reels", "short", "facebook reels", "lam reel"]
    description: "Tạo video ngắn — TikTok / Reels / Shorts"
    worker: lam-video
    skill: tao-video-ai
    plan_type: simple

  answer_faq:
    keywords: ["faq", "tool này làm gì", "giá bao nhiêu", "dữ liệu có bị lưu không", "copy all là gì", "match type là gì", "có tư vấn không", "cắn tiền", "bắt đầu từ đâu"]
    description: "Trả lời câu hỏi FAQ / tư vấn nhanh"
    worker: manager
    skill: tra-loi-faq-khach-hang
    plan_type: simple

  create_ad:
    keywords: ["quảng cáo", "ads", "campaign", "chiến dịch", "creative ads", "gen ads"]
    description: "Tạo quảng cáo hoàn chỉnh"
    plan_type: multi_step  # cần planner vì có thể gồm write + image

  team_sync:
    keywords: ["cả team", "đồng bộ", "chia việc", "làm đồng loạt", "bảo team làm", "làm content cho"]
    description: "Sản xuất nội dung đồng bộ — bài viết + ảnh + video"
    plan_type: complex     # full team orchestration

  approve:
    keywords: ["ok", "duyệt", "được", "đăng", "tốt", "đăng đi", "ok đăng"]
    description: "Phê duyệt kết quả công việc"
    plan_type: simple

  check_status:
    keywords: ["kiểm tra", "tình trạng", "tiến độ", "đến đâu rồi"]
    description: "Kiểm tra trạng thái task"
    plan_type: simple

  cancel:
    keywords: ["hủy", "stop", "dừng", "hủy task", "bỏ"]
    description: "Hủy công việc đang chạy"
    plan_type: simple

  unknown:
    keywords: []
    description: "Intent không xác định"
    plan_type: simple
```

### 2.3 Matching Rules

1. **Mỗi message chỉ map vào 1 intent** — intent có độ ưu tiên cao nhất
2. **Keyword match** — so khớp không phân biệt hoa/thường, tiếng Việt có dấu
3. **Nếu có nhiều intent match** — intent dài nhất (specific nhất) thắng
4. **Nếu không match** → `unknown` → Manager hỏi clarification

---

## 3. Đầu ra

```json
{
  "intent": "write_post",
  "confidence": "high",         // high | medium | low
  "params": {
    "raw_message": "viết bài Facebook giới thiệu tool",
    "keywords_matched": ["viết bài"],
    "topic": "tool",            // extracted from context
    "tone": "brand_voice"       // default
  },
  "plan_type": "simple"
}
```

---

## 4. Ambiguity Handling

Nếu intent = `unknown` hoặc `confidence < medium`:

> "Anh muốn làm gì? Viết bài, tạo ảnh, hay làm video?"

Chỉ hỏi **1 câu**, cung cấp các lựa chọn cụ thể. Không hỏi dài dòng.

---

## 5. Intent Priority Rules

### 5.1 Compound Intent Detection

Khi message match **nhiều intents**, áp dụng compound rules:

| Message matches | Compound Intent | Plan Type | Workers |
|----------------|----------------|-----------|---------|
| `write_post` + `create_image` | `create_ad` | `multi_step` | viet-bai-fb → tao-anh |
| `write_post` + `create_video` | `team_sync` | `complex` | viet-bai-fb → tao-anh → lam-video |
| `create_image` + `create_video` | `team_sync` | `complex` | viet-bai-fb → tao-anh → lam-video |
| 3+ intents match | `team_sync` | `complex` | All workers |

**Ví dụ:**
- "viết bài rồi tạo ảnh" → matches write_post + create_image → compound = create_ad
- "viết bài và làm video" → matches write_post + create_video → compound = team_sync
- "làm ảnh rồi làm video" → matches create_image + create_video → compound = team_sync

### 5.2 Single Intent Rules

| Tình huống | Cách xử lý |
|-----------|-------------|
| User gửi "ok" giữa flow | → `approve` — xác nhận kết quả đang chờ duyệt |
| User gửi "viết bài + tạo ảnh" | → `team_sync` — cả hai |
| User gửi "làm video Reels" | → `create_video` — specific nhất |
| User gửi "cho 3 ý tưởng" | → `create_ideas` |
| User gửi câu hỏi về tool | → `answer_faq` |

---

## 6. Liên kết

- **Input từ:** Telegram message (qua GoClaw)
- **Output đến:** `PLANNER.md` để tạo kế hoạch
- **Routing:** `ROUTING_TABLE.yaml` để tra worker
- **File liên quan:** `agent/AGENTS.md` (Manager rules)
