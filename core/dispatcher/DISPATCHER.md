# DISPATCHER

> **File:** `core/dispatcher/DISPATCHER.md`
> **Role:** Send tasks to workers and parse their replies — runtime dispatch
> **Part of:** Dispatcher
> **Phase:** 4 — Runtime Integration

---

## 1. Mục đích

Dispatcher chịu trách nhiệm:
1. Gửi task đến worker qua GoClaw `@agentId` trong group chat
2. Parse reply từ worker để cập nhật Kanban
3. Ghi log mỗi lần dispatch

**Cơ chế:** Manager (Gà Trống Tre) đọc file này để biết CÁCH dispatch.
Không phải code runtime — là hướng dẫn cho Manager.

---

## 2. Dispatch Runtime Flow

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DISPATCH TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INPUT: task từ Kanban (status = todo)

STEP 1: ĐỌC ROUTING TABLE
  Đọc core/router/ROUTING_TABLE.yaml
  → Tìm route match: intent + worker + skill
  → Lấy timeout

STEP 2: ĐỌC WORKER REGISTRY
  Đọc core/worker/WORKER_REGISTRY.yaml  
  → Kiểm tra worker active
  → Kiểm tra Telegram binding
  → Lấy dispatch_to format
  → Lấy restrictions

STEP 3: ASSEMBLE CONTEXT
  Đọc core/context/CONTEXT_ASSEMBLER.md
  → Filter context per worker type
  → Package vào CONTEXT_CONTRACT.md format

STEP 4: ASSEMBLE PROMPT
  Đọc core/context/PROMPT_ASSEMBLY.md
  → SYS + ROLE + TASK + CTX + KNOW + CONST + OUT

STEP 5: FORMAT DISPATCH MESSAGE
  Template:
  
  @{worker_id} [TASK: {task_id}]
  
  --- TASK ---
  Input: {task.input}
  
  --- OUTPUT FORMAT ---
  {output_format}
  
  Khi hoàn thành, trả lời với [done] hoặc [failed] ở đầu câu.

STEP 6: SEND VIA GOCLAW
  Gửi tin nhắn trong group chat:
  → @viet-bai-fb [TASK: task_001] ...
  → GoClaw tự động route mention đến worker agent

STEP 7: UPDATE KANBAN
  task.status = "in_progress"
  task.assigned_at = now
  task.updated_at = now
  GHI session file

STEP 8: LOG
  {"event":"DISPATCH","timestamp":"...","task_id":"...","worker":"...","skill":"...","attempt":1}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 3. Status Protocol — Parse Worker Reply

Worker trả lời với status marker ở **đầu câu**.
Manager parse marker để biết trạng thái.

### 3.1 Status Markers

| Marker | Ý nghĩa | Manager hành động |
|--------|---------|-------------------|
| `[in_progress]` | Worker đã nhận, đang xử lý | Log WORKER_START. Chưa cập nhật Kanban (đã in_progress). |
| `[done]` | Worker hoàn thành | Parse output JSON sau marker. Update Kanban → DONE. Log WORKER_FINISH. |
| `[failed]` | Worker lỗi | Parse error message. Update Kanban → FAILED. Log WORKER_FINISH. |

### 3.2 Parse Rules

```
1. Lấy 3 dòng đầu reply của worker
2. Tìm [in_progress] hoặc [done] hoặc [failed] trong 200 ký tự đầu
3. Nếu không tìm thấy marker nào → coi là [in_progress] (worker chưa báo)
4. Nếu có [done]:
   a. Tìm JSON object { "status": "done", "output": {...} }
   b. Parse output vào task.output
   c. Update Kanban: task → DONE
5. Nếu có [failed]:
   a. Tìm error message
   b. Update Kanban: task → FAILED, task.error = error
6. Nếu [in_progress]:
   a. Log WORKER_START
   b. Giữ task IN_PROGRESS
   c. Chờ turn sau
```

### 3.3 Output JSON Detection

Worker trả output JSON trong reply. Manager cần tìm JSON object:

```
Cách tìm:
1. Tìm { đầu tiên sau [done] marker
2. Tìm } cuối cùng
3. Parse JSON ở giữa
4. Nếu parse fail → log lỗi, coi toàn bộ reply text là output.caption
```

**Ví dụ worker reply:**

```
[done] Xong rồi ạ. Caption đây:
{"status":"done","output":{"caption":"Bạn đang mất bao nhiêu thời gian...","type":"full_caption"}}
```

**Manager parse:**
```
status = done
output.caption = "Bạn đang mất bao nhiêu thời gian..."
output.type = "full_caption"
```

---

## 4. Dispatch Message Templates

### 4.1 Generic Template

```
@{worker_id} [TASK: {task_id}]

--- TASK ---
Worker: {worker}
Skill: {skill}
Input: {input}

--- CONTEXT ---
{context_summary}

--- CONSTRAINTS ---
{restrictions}

--- OUTPUT FORMAT ---
{output_format}

Khi xong, trả lời [done] kèm output JSON.
Khi lỗi, trả lời [failed] kèm error message.
```

### 4.2 Worker-Specific Format (mỗi worker có template trong WORKER_REGISTRY.yaml)

**Cây Bút (viet-bai-fb):**
```
@viet-bai-fb [TASK: task_20260709_001]
Viết caption Facebook với chủ đề: {topic}
Tone: brand voice | Format: Hook + Body + CTA

Output: {"status":"done","output":{"caption":"...","type":"full_caption"}}
```

**Tạo Ảnh (tao-anh):**
```
@tao-anh [TASK: task_20260709_002]
Tạo ảnh creative cho caption: {caption}
Concept: {concept}

Output: {"status":"done","output":{"image_url":"...","caption_paired":"...","mode":"organic"}}
```

**Làm Video (lam-video):**
```
@lam-video [TASK: task_20260709_003]
Làm video từ caption + ảnh.
Caption: {caption}
Ảnh: {image_urls}

Output: {"status":"done","output":{"video_url":"...","duration_seconds":18}}
```

---

## 5. Dispatch Method Resolution

| Worker binding | Dispatch method | Ví dụ |
|---------------|----------------|-------|
| `group` | `@agentId` trong group chat | `@viet-bai-fb [TASK: ...]` |
| `direct` | `@agentId` trong DM | `@tao-anh [TASK: ...]` |
| `none` | `use_skill "skill-name"` | `use_skill "viet-bai-facebook"` |
| `manager` | Manager tự xử lý | approve/cancel/check_status |

**Cách quyết định:**
1. Đọc `worker.telegram.binding` từ WORKER_REGISTRY.yaml
2. Nếu `group` → dispatch via @mention trong group chat
3. Nếu `direct` → dispatch via @mention trong DM
4. Nếu `none` → dùng `use_skill "skill-name"` với task context
5. Nếu worker = "manager" → Manager tự xử lý

---

## 6. Error Handling

| Tình huống | Xử lý |
|-----------|--------|
| Worker không respond | Chờ timeout (từ ROUTING_TABLE.yaml) → fail |
| Worker không tìm thấy | Log + fail task |
| Skill không tồn tại | Log + fail task |
| Worker reply không có marker | Coi là in_progress, chờ |
| Worker reply không parse được | Log cả raw reply, coi output.text |
| Timeout đạt | Kanban: in_progress → failed, error = "timeout" |

---

## 7. Multi-Task Dispatch

Khi plan có nhiều tasks:

```
1. Chỉ dispatch task TODO đầu tiên
2. Các task BLOCKED không dispatch (chờ dependency)
3. Sau khi task DONE → unblock → dispatch task tiếp theo
4. Mỗi lần dispatch = 1 turn (không dispatch 2 tasks cùng lúc)
```

---

## 8. Liên kết

- **Input từ:** `core/kanban/KANBAN_BOARD.md` (TODO tasks)
- **Output đến:** Worker (qua GoClaw @agentId)
- **Status parse:** file này (mục 3)
- **Routing config:** `core/router/ROUTING_TABLE.yaml`
- **Worker config:** `core/worker/WORKER_REGISTRY.yaml`
- **Kanban update:** `core/kanban/KANBAN_BOARD.md`
- **Log:** `memory/long-term/task_history.log`
- **Orchestration:** `core/manager/ORCHESTRATION.md`
