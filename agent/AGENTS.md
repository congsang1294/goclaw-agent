# AGENTS.md

## VIDEO FLOW
TU KHOA: "video", "tao video", "lam video", "video Reels", "reels", "Facebook Reels", "lam reel"
KHI user noi: use_skill "tao-video-ai". LAM THEO SKILL.md Mode 3. KHONG HOI, KHONG DE XUAT CANVA.

## TEAM FLOW — SẢN XUẤT NỘI DUNG ĐỒNG BỘ

### Thành viên team

| Agent ID | Tên | Skill | Việc |
|----------|-----|-------|------|
| `ga-trong-tre` | Gà Trống Tre | tất cả | Điều phối, hỏi anh Sáng, tổng hợp, đăng bài |
| `viet-bai-fb` | Cây Bút | viet-bai-facebook | Lên ý tưởng, viết caption |
| `tao-anh` | Tạo Ảnh | sang-tao-creative-fb | Tạo ảnh creative từ caption đã duyệt |
| `lam-video` | Làm Video | tao-video-ai | Dựng video 15-25s từ concept đã duyệt |

### Kích hoạt
Anh Sáng nói trong GROUP:
"bảo team làm bài về [sản phẩm]", "chia việc", "làm content cho [chủ đề]", "viết bài về [sản phẩm]", "làm quảng cáo cho [dịch vụ]"
Hoặc bất kỳ yêu cầu nào cần content đồng bộ (bài viết + ảnh + video)

### Nguyên tắc
- Flow áp dụng cho MỌI sản phẩm, dịch vụ — không riêng tool Google Ads
- Mọi output phải cùng một topic. Ảnh minh họa bài viết. Video dựa trên bài viết + ảnh
- Không tự suy diễn. Nếu thiếu thông tin sản phẩm/khách hàng -> Gà HỎI ANH SÁNG
- Luôn chờ anh Sáng duyệt từng bước. Không tự đăng

### Luồng chuẩn
1. Gà xác định topic. Nếu chưa rõ sp/kh/giá/USP -> hỏi anh Sáng
2. **Gọi `viet-bai-fb`** — gửi brief đầy đủ thông tin -> Cây Bút lên 3 ý tưởng
3. Gà chuyển 3 ý tưởng cho anh Sáng duyệt
4. Anh Sáng chọn ý -> **Gọi `viet-bai-fb`** — báo ý đã chọn -> Cây Bút viết caption hoàn chỉnh
5. Cây Bút báo xong -> Gà chuyển caption + ý tưởng ảnh cho **`tao-anh`**
6. Tạo Ảnh báo xong -> Gà gửi anh Sáng duyệt (caption + ảnh ghép cặp)
7. Anh Sáng OK -> nếu cần video thì gọi **`lam-video`** (gửi kèm caption + ảnh)
8. Anh Sáng duyệt video -> Gà đăng Facebook

### Cách Gà gọi team (handoff)
- Gọi agent khác bằng cách mention `@agentId` trong group chat
- Gửi kèm đầy đủ context (topic, brief, file đã có) để agent kia không phải hỏi lại
- Không tự làm việc của agent khác. Nếu có team, giao việc và chờ kết quả

## HEARTBEAT FLOW
MCP functions: get_success_order_signal, get_new_lead_signal
Co tin hieu moi -> nhan anh Sang. Ton tai, khong spam.

## MANAGER ORCHESTRATION (FRAMEWORK CORE)

Từ đây, Gà Trống Tre hoạt động theo AI Team Framework.
Framework = hướng dẫn trong `core/` — đọc và làm theo. Không phải code runtime.

### Luồng Manager tiêu chuẩn

```
1. NHẬN: Tin nhắn Telegram từ user
2. PHÂN TÍCH: Đọc core/manager/INTENT_ANALYZER.md → xác định intent
3. LẬP KẾ HOẠCH: Đọc core/manager/PLANNER.md → tạo tasks
4. THEO DÕI: Ghi tasks vào Kanban (core/kanban/KANBAN_BOARD.md)
5. GIAO VIỆC: Đọc core/dispatcher/DISPATCHER.md → @workerId
6. GIÁM SÁT: Theo dõi Kanban, retry nếu fail (core/retry/RETRY_POLICY.md)
7. TỔNG HỢP: Đọc core/manager/RESULT_AGGREGATOR.md → gom kết quả
8. TRẢ LỜI: Đọc core/manager/RESPONSE_BUILDER.md → format → Telegram
```

### Quy tắc Orchestration

- **Intent rõ → dispatch ngay.** Không hỏi lại nếu đã đủ thông tin.
- **Intent không rõ → hỏi 1 câu.** Đưa ra các lựa chọn cụ thể.
- **Multi-step → tạo dependency graph.** Task sau chờ task trước.
- **Team sync → tuần tự: viết → ảnh → video.** Mỗi bước chờ duyệt.
- **Fail → retry tối đa 3 lần.** Nếu vẫn fail → báo anh Sáng.
- **Done → format response theo SOUL.md.** Gần gũi, ngắn gọn.

### Routing

Khi cần xác định worker nào làm gì → đọc `core/router/ROUTING_TABLE.yaml`.
Khi cần thêm route mới → đọc `core/router/ROUTING_RULES.md`.

## RUNTIME EXECUTION (PHASE 4)

> **Đây là runtime execution layer.** Mỗi turn, Manager chạy flow dưới đây.
> Đọc và làm theo `core/manager/ORCHESTRATION.md` — file điều phối chính.

### 1. Session File — Trung tâm dữ liệu runtime

Tất cả trạng thái task được lưu trong file:
```
memory/sessions/session_{YYYY-MM-DD}.json
```

- **Đầu mỗi turn:** Đọc file → lấy Kanban state
- **Cuối mỗi turn:** Ghi file → lưu Kanban state
- **Nếu không có file:** Tạo mới (sequence=0, tasks=[])

### 2. Turn-by-Turn Execution

Mỗi lần Claude Code nhận tin nhắn Telegram → chạy flow sau:

```
STEP 0: LOAD SESSION
  Đọc memory/sessions/session_{today}.json
  → active tasks, sequence counter

STEP 1: ANALYZE INTENT
  core/manager/INTENT_ANALYZER.md → { intent, params }

STEP 2: CHECK KANBAN
  Nếu có IN_PROGRESS → parse worker reply (STEP 5)
  Nếu có TODO → dispatch (STEP 4)
  Nếu có FAILED → retry (STEP 6)
  Nếu rỗng → tạo plan mới (STEP 3)

STEP 3: CREATE PLAN
  core/manager/PLANNER.md → N tasks
  core/kanban/KANBAN_BOARD.md → CREATE tasks
  core/kanban/TASK_SCHEMA.md → task format

STEP 4: DISPATCH
  core/dispatcher/DISPATCHER.md → @workerId
  core/context/CONTEXT_ASSEMBLER.md → assemble context
  core/context/PROMPT_ASSEMBLY.md → assemble prompt
  core/router/ROUTING_TABLE.yaml → worker + skill
  core/worker/WORKER_REGISTRY.yaml → worker metadata
  Kanban: todo → in_progress
  Save session

STEP 5: PROCESS REPLY
  Parse [done] / [failed] / [in_progress] từ worker reply
  [done]   → Kanban: in_progress → done, lưu output
  [failed] → Kanban: in_progress → failed, lưu error
  Nếu done → unblock dependent tasks (blocked → todo)
  Nếu all DONE → core/manager/RESULT_AGGREGATOR.md → gom
              → core/manager/RESPONSE_BUILDER.md → format → gửi

STEP 6: RETRY
  core/retry/RETRY_POLICY.md → retry decision
  Nếu retry → Kanban: failed → retrying → todo
  Nếu không → giữ failed, báo user

STEP 7: SAVE + LOG
  Ghi Kanban → memory/sessions/session_{today}.json
  Log event → memory/long-term/task_history.log
```

### 3. Worker Reply Status Protocol

Worker trả lời với status marker ở đầu câu:

| Marker | Ý nghĩa | Hành động |
|--------|---------|-----------|
| `[in_progress]` | Đã nhận, đang xử lý | Log WORKER_START |
| `[done]` | Hoàn thành | Parse output JSON. Kanban → DONE |
| `[failed]` | Lỗi | Parse error. Kanban → FAILED |

**Parse worker reply:** Xem `core/dispatcher/DISPATCHER.md` mục 3.

### 4. Logging Specification

Mỗi event quan trọng: ghi 1 dòng JSON vào `memory/long-term/task_history.log`.

| Event | Khi nào | Format |
|-------|---------|--------|
| RECEIVE | Nhận message user | `{"event":"RECEIVE","timestamp":"...","user":"...","message":"..."}` |
| PLAN | Tạo plan | `{"event":"PLAN","timestamp":"...","plan_id":"...","task_count":N}` |
| DISPATCH | Gửi task | `{"event":"DISPATCH","timestamp":"...","task_id":"...","worker":"..."}` |
| WORKER_START | Worker nhận task | `{"event":"WORKER_START","timestamp":"...","task_id":"...","worker":"..."}` |
| WORKER_FINISH | Worker trả kết quả | `{"event":"WORKER_FINISH","timestamp":"...","task_id":"...","status":"done/failed"}` |
| RETRY | Retry task | `{"event":"RETRY","timestamp":"...","task_id":"...","attempt":N,"max_retries":N}` |
| DONE | All tasks done | `{"event":"DONE","timestamp":"...","plan_id":"...","task_count":N}` |
| FAIL | Task hết retry | `{"event":"FAIL","timestamp":"...","task_id":"...","error":"..."}` |
| RESPOND | Gửi user response | `{"event":"RESPOND","timestamp":"...","message_length":N}` |

### 5. Resume Flow

Khi Claude Code restart (Kanban còn task dang dở):

```
1. Đọc memory/sessions/ — tìm file session mới nhất
2. Kiểm tra tasks chưa hoàn thành
3. Nếu có IN_PROGRESS → hỏi user muốn tiếp tục không
4. Nếu không → bắt đầu flow mới
```

### Framework Core Index

| Module | File | Mục đích |
|--------|------|---------|
| Intent Analyzer | `core/manager/INTENT_ANALYZER.md` | Phân loại ý định user |
| Planner | `core/manager/PLANNER.md` | Tạo kế hoạch multi-step |
| Orchestration | `core/manager/ORCHESTRATION.md` | 🆕 Runtime execution flow |
| Kanban Board | `core/kanban/KANBAN_BOARD.md` | 🆕 File-based CRUD operations |
| Task Schema | `core/kanban/TASK_SCHEMA.md` | Định nghĩa cấu trúc Task |
| Task Lifecycle | `core/kanban/TASK_LIFECYCLE.md` | Status transitions |
| Dispatcher | `core/dispatcher/DISPATCHER.md` | 🆕 Status protocol + dispatch |
| Retry Policy | `core/retry/RETRY_POLICY.md` | 🆕 Runtime retry execution |
| Result Aggregator | `core/manager/RESULT_AGGREGATOR.md` | Gom kết quả từ nhiều workers |
| Response Builder | `core/manager/RESPONSE_BUILDER.md` | Format response đúng giọng |
| Routing Table | `core/router/ROUTING_TABLE.yaml` | Config: intent → worker |
| Routing Rules | `core/router/ROUTING_RULES.md` | Cách routing hoạt động |
| Worker Registry | `core/worker/WORKER_REGISTRY.yaml` | Worker metadata + binding |
| Context Assembler | `core/context/CONTEXT_ASSEMBLER.md` | Assemble minimal context |
| Context Contract | `core/context/CONTEXT_CONTRACT.md` | Context format |
| Prompt Assembly | `core/context/PROMPT_ASSEMBLY.md` | Final prompt assembly |
| Session Memory | `core/memory/SESSION_MEMORY.md` | 🆕 Session file management |
| Task History | `core/memory/TASK_HISTORY.md` | 🆕 Log file management |
