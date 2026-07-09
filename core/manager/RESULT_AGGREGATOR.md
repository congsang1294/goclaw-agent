# RESULT AGGREGATOR

> **File:** `core/manager/RESULT_AGGREGATOR.md`
> **Role:** Collect and merge outputs from multiple worker tasks
> **Part of:** Manager (Gà Trống Tre)
> **Phase:** 1 — Core Framework

---

## 1. Mục đích

Khi một workflow có nhiều tasks, mỗi worker trả về một phần output.
Result Aggregator **gom tất cả output lại** thành một kết quả thống nhất để Response Builder xử lý.

**Đầu vào:** Array of completed tasks `[{ id, status: "done", output, ... }]`.
**Đầu ra:** Aggregated result object `{ combined_output, sources, delivery_required }`.

---

## 2. Nguyên tắc

- **Không thay đổi nội dung output của worker** — chỉ gom lại
- **Không đánh giá chất lượng** — worker đã tự audit (theo SKILL.md guardrails)
- **Nếu 1 task fail và không retry được** → workflow fail → không aggregate
- **Không đánh dấu workflow complete** — Aggregator chỉ xác nhận output đã sẵn sàng để gửi; Response Builder/Telegram delivery mới quyết định complete cuối cùng
- **Chỉ gom cùng campaign** — mọi output phải cùng `campaign_id` và `chosen_idea`

---

## 3. Aggregation Rules

### 3.1 Single Task (simple plan)

```
Nếu chỉ có 1 task:
  → Pass through: output của task đó là kết quả cuối cùng
  → Không cần merge
```

### 3.2 Multi-Step (write → image)

```
Tasks:
  A: viet-bai-fb → { caption: "..." }
  B: tao-anh → { image_url: "...", caption: "..." }

Kết quả:
{
  "type": "paired_content",
  "caption": "từ task A (hoặc B nếu B có caption riêng)",
  "image_url": "từ task B",
  "sources": ["viet-bai-fb", "tao-anh"]
}
```

### 3.3 Complex (write → image → video)

```
Tasks:
  A: agent-scout → { sources: [...], analysis: "..." }

Kết quả:
{
  "type": "research",
  "content": analysis từ task A,
  "sources": sources từ task A
}
```

---

## 4. Output Format

```json
{
  "type": "paired_content" | "campaign_content" | "single",
  "campaign_id": "string",
  "chosen_idea": "string",
  "caption": "string | null",
  "image_url": "string | null",
  "image_local": "string | null",
  "video_url": "string | null",
  "video_preview": "string | null",
  "delivery_required": ["caption", "image", "video"],
  "sources": ["worker_id_1", "worker_id_2"],
  "status": "ready_for_delivery" | "partial"
}
```

**`partial`** = có tasks thành công nhưng cũng có tasks fail (đã retry hết lượt).
Trường hợp partial → chỉ aggregate các output thành công, báo user task nào failed.

**`ready_for_delivery`** = output có đủ artifact trong object aggregate, nhưng chưa có nghĩa là Telegram đã gửi xong.

## 5. Required Artifacts

Aggregator phải điền `delivery_required` dựa trên nội dung workflow:

| Result type | Required |
|-------------|----------|
| `single` caption/ideas | `["caption"]` |
| `paired_content` | `["caption", "image"]` |
| `campaign_content` | `["caption", "image", "video"]` |
| video-only | `["video"]` |

Nếu required artifact thiếu field tương ứng, trả `status = "partial"` và nêu rõ thiếu gì; không chuyển sang Response Builder để báo complete.

## 6. Partial Output Rules

Trong team_sync, Aggregator/Manager không cần chờ đủ bộ để gửi từng output:

| Worker output xong | Manager làm ngay |
|--------------------|------------------|
| `caption` | Gửi bài viết cho anh Sáng |
| `image` | Gửi ảnh/file/link cho anh Sáng |
| `video` | Gửi video preview/file/link cho anh Sáng |

Khi đủ cả 3:
1. Kiểm tra cùng `campaign_id`.
2. Kiểm tra cùng `chosen_idea`.
3. Tạo bản tổng hợp cuối.
4. Chuyển sang `final_approval`.
5. Chỉ sau khi anh Sáng approve mới chuyển sang publish.

---

## 7. Liên kết

- **Input từ:** `KANBAN_BOARD.md` (tasks đã done/failed)
- **Output đến:** `RESPONSE_BUILDER.md` (aggregated result)
- **Gọi khi:** Tất cả tasks trong plan đã done hoặc failed hết lượt retry
