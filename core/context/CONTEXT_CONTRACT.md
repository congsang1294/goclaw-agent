# CONTEXT CONTRACT

> **File:** `core/context/CONTEXT_CONTRACT.md`
> **Role:** Define the structured context contract between Manager and Worker
> **Part of:** Context System
> **Phase:** 3 — Memory & Context

---

## 1. Mục đích

Context Contract định nghĩa **format giao tiếp context** giữa Manager (Gà Trống Tre) và Worker.
Worker chỉ nhận đúng phần Context cần thiết cho Task, được đóng gói trong cấu trúc JSON thống nhất.

**Nguyên tắc:** Worker nhận context = tham số, không phải toàn bộ file dump.

---

## 2. Contract Format

```json
{
  "context_version": "1.0",
  "context": {
    "agent": {
      "id": "viet-bai-fb",
      "name": "Cây Bút",
      "role": "Facebook Content Writer",
      "soul_ref": "agent/viet-bai-fb/SOUL.md",
      "guidelines": "Viết Hook + Body + CTA. Không tạo ảnh. Không đăng bài."
    },
    "user": {
      "name": "anh Sáng",
      "id": "6880126421",
      "language": "Tiếng Việt",
      "timezone": "Asia/Saigon (UTC+7)",
      "preferences": "nói thẳng, ngắn gọn, không corporate"
    },
    "task": {
      "id": "task_20260709_001",
      "type": "skill_execution",
      "worker": "viet-bai-fb",
      "skill": "viet-bai-facebook",
      "priority": "normal",
      "attempts": 1,
      "max_retries": 3,
      "input": {
        "topic": "giới thiệu tool Google Ads Match Type Converter",
        "tone": "brand_voice",
        "format": "hook_body_cta",
        "additional_instructions": "tập trung vào pain point mất thời gian format keyword"
      },
      "depends_on": [],
      "parent_task": null
    },
    "knowledge": {
      "brand_voice": {
        "ref": "knowledge/brand-voice.md",
        "summary": "Viết như người đã làm thật, sai thật... Không corporate, không bán quá sớm.",
        "key_rules": [
          "Không dùng từ corporate",
          "CTA nhẹ: 'Anh em ghé vào xem thử'",
          "Không hứa kết quả ads"
        ]
      },
      "product_info": {
        "ref": "knowledge/knowledge-base.md",
        "summary": "Google Ads Match Type Converter — chuyển keyword Broad/Phrase/Exact",
        "key_points": [
          "Tool chạy trên trình duyệt, không gửi lên server",
          "Free có 3 lượt Copy All",
          "Pro 15,000đ mở Copy All không giới hạn"
        ]
      }
    },
    "session": {
      "conversation_summary": "User vừa hỏi về việc viết bài giới thiệu tool cho người mới bắt đầu.",
      "turn_count": 3,
      "active_tasks": ["task_20260709_001"],
      "recent_events": []
    }
  },
  "assembled_at": "2026-07-09T08:01:00+07:00"
}
```

---

## 3. Field Descriptions

| Field | Bắt buộc | Mô tả |
|-------|---------|-------|
| `context_version` | ✅ | Version của contract format (hiện tại "1.0") |
| `context.agent` | ✅ | Agent identity + guidelines |
| `context.agent.id` | ✅ | Agent ID |
| `context.agent.name` | ✅ | Tên hiển thị |
| `context.agent.role` | ✅ | Role description |
| `context.agent.soul_ref` | ✅ | Path đến SOUL.md (để Worker đọc nếu cần) |
| `context.agent.guidelines` | ✅ | Key rules từ AGENTS.md + Task Contract |
| `context.user` | ✅ | User profile (từ USER.md + preferences) |
| `context.user.name` | ✅ | Tên user |
| `context.user.id` | ✅ | Telegram ID |
| `context.user.preferences` | ✅ | Communication preferences |
| `context.task` | ✅ | Task thông tin (từ Task schema) |
| `context.task.id` | ✅ | Task ID |
| `context.task.input` | ✅ | Input parameters |
| `context.knowledge` | ✅ | Filtered knowledge (từ CONTEXT_ASSEMBLER) |
| `context.knowledge.*.ref` | ✅ | Path reference đến source file |
| `context.knowledge.*.summary` | ✅ | Tóm tắt ngắn |
| `context.knowledge.*.key_rules` | ❌ | Key rules (list) |
| `context.session` | ❌ | Session context (nếu có) |
| `assembled_at` | ✅ | Timestamp assemble |

---

## 4. Contract Rules

### 4.1 Manager Rules

| Rule | Detail |
|------|--------|
| **Always include `context_version`** | Để Worker biết format |
| **Always include `agent` block** | Worker cần biết mình là ai |
| **Always include `task` block** | Worker cần biết làm gì |
| **Include `user` block** | Worker cần biết nói chuyện với ai |
| **Include `knowledge` block** | Filtered — chỉ cái cần |
| **Include `session` block** | Nếu có conversation context |
| **Reference, don't copy** | Dùng `ref` path thay vì copy nội dung |
| **Keep summary short** | Key rules + tóm tắt, không nguyên file |

### 4.2 Worker Rules

| Rule | Detail |
|------|--------|
| **Read `agent` first** | Biết vai trò, guidelines |
| **Read `task.input`** | Biết cần làm gì |
| **Read `knowledge`** | Biết brand voice + product info |
| **Read `user`** | Biết đối tượng |
| **Follow `agent.guidelines`** | Giới hạn của Worker |
| **Ignore unknown fields** | Backward compatible |

---

## 5. Contract Versions

| Version | Changes |
|---------|---------|
| 1.0 | Initial contract format |

Khi thay đổi contract format:
- Add field → backward compatible (Worker ignore unknown)
- Remove field → update worker AGENTS.md
- Change field type → bump major version

---

## 6. Minimal Contract (cho system tasks)

Cho task đơn giản (approve, cancel, check_status), contract có thể tối thiểu:

```json
{
  "context_version": "1.0",
  "context": {
    "agent": {
      "id": "ga-trong-tre",
      "name": "Gà Trống Tre"
    },
    "user": {
      "name": "anh Sáng"
    },
    "task": {
      "id": "task_20260709_999",
      "type": "approval",
      "input": {
        "action": "approve",
        "target_task": "task_20260709_001",
        "target_output": "caption đã viết xong..."
      }
    },
    "knowledge": {},
    "session": {}
  }
}
```

---

## 7. Liên kết

- **Context Assembler:** `CONTEXT_ASSEMBLER.md` — cách assemble context
- **Prompt Assembly:** `PROMPT_ASSEMBLY.md` — prompt cuối cùng
- **Worker AGENTS.md:** `agent/*/AGENTS.md` — Task Contract per worker
- **FRAMEWORK_SPEC.md:** §4.2 Context Contract
