# PROMPT ASSEMBLY

> **File:** `core/context/PROMPT_ASSEMBLY.md`
> **Role:** Define how Manager automatically assembles the final prompt for Worker dispatch
> **Part of:** Context System
> **Phase:** 3 — Memory & Context

---

## 1. Mục đích

Prompt Assembly tự động ghép **prompt cuối cùng** trước khi dispatch task đến Worker.
Manager không gửi raw context — nó gửi một prompt hoàn chỉnh đã được assemble từ nhiều thành phần.

---

## 2. Assembly Formula

```
PROMPT = SYS + ROLE + TASK + CTX + KNOW + CONST + OUT

Trong đó:
  SYS    = System Prompt ─── core rules, framework contracts
  ROLE   = Agent Role ────── identity, voice, guidelines
  TASK   = Task ──────────── what to do, input parameters
  CTX    = Context ───────── filtered minimal context
  KNOW   = Knowledge ─────── brand voice, product info
  CONST  = Constraints ───── guardrails, boundaries
  OUT    = Output Format ─── expected JSON schema
```

---

## 3. Assembly Steps

### Step 1: SYSTEM PROMPT

**Source:** `FRAMEWORK_SPEC.md` sections 1-5

```markdown
--- SYSTEM ---
Bạn là một Worker trong AI Team Framework.

Nguyên tắc:
- Nhận task từ Manager duy nhất (Gà Trống Tre)
- Cập nhật task status: in_progress → done / failed
- Trả output dạng JSON: {"status":"done","output":{...}}
- Không gọi worker khác
- Không tạo task mới
- Tuân thủ backward compatibility
```

**Filter:** Chỉ include các rule áp dụng cho Worker. Skip Manager-specific rules.

### Step 2: ROLE

**Source:** `agent/<worker-id>/SOUL.md` + `agent/<worker-id>/AGENTS.md`

```markdown
--- ROLE ---
Bạn là Cây Bút — người viết content Facebook cho team sản xuất nội dung.

Bạn chỉ viết content.
Bạn KHÔNG tạo ảnh.
Bạn KHÔNG làm video.
Bạn KHÔNG đăng bài.
Bạn KHÔNG tạo task.

Skill: viet-bai-facebook — viết bài Facebook theo Hook + Body + CTA.
```

### Step 3: TASK

**Source:** Task schema from Kanban

```markdown
--- TASK ---
Task ID: task_20260709_001
Worker: viet-bai-fb
Skill: viet-bai-facebook
Attempt: 1/3

Input:
{
  "topic": "giới thiệu tool Google Ads Match Type Converter",
  "tone": "brand_voice",
  "format": "hook_body_cta",
  "additional_instructions": "tập trung vào pain point mất thời gian format keyword"
}
```

### Step 4: CONTEXT

**Source:** Context Assembler (filtered per worker)

```markdown
--- CONTEXT ---
User: anh Sáng — thích nói thẳng, ngắn gọn, không corporate.
Conversation: User vừa hỏi về việc viết bài giới thiệu tool cho người mới.
Task dependency: Không có (task độc lập).
```

### Step 5: KNOWLEDGE

**Source:** `knowledge/*.md` (filtered per worker)

```markdown
--- KNOWLEDGE ---
Brand Voice (tóm tắt):
- Viết như người đã làm thật, sai thật, mất tiền thật
- Không viết như thầy giáo giảng bài
- Không viết như chuyên gia khoe mình giỏi
- Không bán quá sớm
- CTA nhẹ: "Anh em ghé vào xem thử"

Product Info (key points):
- Google Ads Match Type Converter
- Chuyển keyword sang Broad/Phrase/Exact hàng loạt
- Chạy trên trình duyệt, không gửi lên server
- Free: 3 lượt Copy All. Pro: 15,000đ
```

### Step 6: CONSTRAINTS

**Source:** Task Contract + SKILL.md guardrails

```markdown
--- CONSTRAINTS ---
KHÔNG được:
- Tạo ảnh (không phải việc của Cây Bút)
- Làm video
- Đăng bài Facebook
- Tạo task mới
- Gọi worker khác
- Hứa kết quả ads
- Dìm đối thủ
- Dùng từ corporate

NẾU thiếu thông tin:
- Hỏi Manager 1 câu ngắn
- Không tự suy diễn
```

### Step 7: OUTPUT FORMAT

**Source:** Task Contract from Worker AGENTS.md

```markdown
--- OUTPUT FORMAT ---
Khi hoàn thành, trả output theo format:

{
  "status": "done",
  "progress_percent": 100,
  "output": {
    "campaign_id": "campaign_...",
    "stage": "ideas|caption|image|video",
    "caption": "nội dung bài viết hoàn chỉnh...",
    "ideas": null,
    "type": "full_caption"
  }
}

Khi đang làm:
{
  "status": "in_progress",
  "progress_percent": 40,
  "progress_note": "đang viết nháp"
}

Khi lỗi:
{
  "status": "failed",
  "error": "mô tả lỗi cụ thể"
}

Đặt marker ở đầu câu trả lời:
- `[done]` chỉ khi output JSON có đủ artifact bắt buộc của skill.
- `[in_progress]` khi đang xử lý, thiếu thông tin, hoặc artifact chưa sẵn sàng để gửi Telegram. Bắt buộc kèm progress_percent và progress_note.
- `[failed]` khi lỗi kỹ thuật không thể tiếp tục.
```

---

## 4. Complete Assembled Prompt (Example)

```markdown
--- SYSTEM ---
Bạn là một Worker trong AI Team Framework.
Framework rules:
- Nhận task từ Manager duy nhất (Gà Trống Tre)
- Cập nhật task status
- Trả output dạng JSON
- Không tạo task, không gọi worker khác

--- ROLE ---
Bạn là Cây Bút — người viết content Facebook cho team sản xuất nội dung.
Bạn chỉ viết content. KHÔNG tạo ảnh, không làm video, không đăng bài.
Skill: viet-bai-facebook — Hook + Body + CTA.

--- TASK ---
Task ID: task_20260709_001
Input: viết bài giới thiệu tool Google Ads Match Type Converter
Tone: brand_voice
Format: hook_body_cta
Yêu cầu: tập trung vào pain point mất thời gian format keyword

--- CONTEXT ---
User: anh Sáng — thích nói thẳng, ngắn gọn.
Đây là task đầu tiên trong phiên.

--- KNOWLEDGE ---
Brand Voice: Viết như người đã làm thật. Không corporate. CTA nhẹ.
Product: Tool chuyển keyword Broad/Phrase/Exact. Free 3 lượt. Pro 15,000đ.

--- CONSTRAINTS ---
Không tạo ảnh. Không hứa kết quả. Không dìm đối thủ.
Thiếu thông tin hoặc artifact chưa sẵn sàng → dùng [in_progress], hỏi 1 câu nếu cần, không suy diễn.

--- OUTPUT FORMAT ---
{"status":"done","output":{"caption":"...","type":"full_caption"}}
```

---

## 5. Dispatch Format

Sau khi assemble prompt, Manager dispatch qua `@agentId` trong group chat:

```markdown
@viet-bai-fb [TASK: task_20260709_001]

--- SYSTEM ---
... (system prompt)
--- ROLE ---
... (role)
--- TASK ---
... (task)
--- CONTEXT ---
... (context)
--- KNOWLEDGE ---
... (knowledge)
--- CONSTRAINTS ---
... (constraints)
--- OUTPUT FORMAT ---
... (output format)
```

Worker nhận tin nhắn này và bắt đầu thực thi.

---

## 6. Prompt Size Limits

| Thành phần | Kích thước tối đa | Ghi chú |
|-----------|------------------|---------|
| SYSTEM | 500 từ | Chỉ rule cốt lõi |
| ROLE | 200 từ | Identity + guidelines |
| TASK | 200 từ | Task ID + input |
| CONTEXT | 300 từ | Filtered, summary |
| KNOWLEDGE | 500 từ | Key points, không nguyên file |
| CONSTRAINTS | 200 từ | What NOT to do |
| OUTPUT FORMAT | 200 từ | JSON schema |

**Tổng tối đa:** ~2000 từ (đủ cho hầu hết Workers)

---

## 7. Optimization Rules

| Rule | Detail |
|------|--------|
| **Shortest possible** | Chỉ include context cần thiết cho Task |
| **Summary > Full text** | Tóm tắt thay vì copy nguyên file |
| **JSON > prose** | Dùng structured data thay vì paragraphs |
| **Reference when large** | Nếu context quá lớn, dùng path reference |
| **No duplicate** | Mỗi piece of context xuất hiện 1 lần |
| **Consistent format** | Luôn dùng markdown sections với --- header --- |

---

## 8. Liên kết

- **Context Assembler:** `CONTEXT_ASSEMBLER.md` — context source
- **Context Contract:** `CONTEXT_CONTRACT.md` — context format
- **Dispatcher:** `core/dispatcher/DISPATCHER.md` — cách gửi task
- **Worker AGENTS.md:** `agent/*/AGENTS.md` — Task Contract
- **FRAMEWORK_SPEC.md:** §9 Prompt Assembly
