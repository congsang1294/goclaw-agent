# TEST PLAN

> **File:** `docs/TEST_PLAN.md`
> **Status:** DRAFT — awaiting implementation start
> **Last Updated:** 2026-07-08

---

## 1. Test Strategy

| Level | Scope | Method | Frequency |
|-------|-------|--------|-----------|
| **Unit** | Individual components | Manual trace | Per phase |
| **Integration** | Component interactions | End-to-end flow | Per phase |
| **Smoke** | Critical paths | Live Telegram | After deploy |
| **Regression** | Existing features | Full flow check | Per release |

---

## 2. Test Categories

### 2.1 Unit Tests (Per Component)

| Component | Test Case | Expected | Method |
|-----------|-----------|----------|--------|
| Intent Analyzer | "viết bài Facebook" → write_post | Correct intent | Manual |
| Intent Analyzer | "tạo ảnh quảng cáo" → create_image | Correct intent | Manual |
| Intent Analyzer | "làm video Reels" → create_video | Correct intent | Manual |
| Intent Analyzer | Ambiguous input → clarification | Question asked | Manual |
| Intent Analyzer | Unknown input → error | Graceful handling | Manual |
| Router | Write intent → viet-bai-fb | Correct worker | Manual |
| Router | Image intent → tao-anh | Correct worker | Manual |
| Router | Video intent → lam-video | Correct worker | Manual |
| Task Creator | Simple task → valid schema | Valid task | Manual |
| Task Creator | Complex task chain → valid deps | Valid dependency graph | Manual |
| Dispatcher | Task → worker | Worker receives task | Manual |
| Dispatcher | Worker `[done]` thiếu artifact | Task giữ `in_progress`, yêu cầu gửi lại JSON | Manual |
| Retry Manager | Failure → retry (up to N) | Retry count respected | Manual |
| Retry Manager | Max retries → fail | Final failure | Manual |
| Result Aggregator | Single result → pass through | Correct output | Manual |
| Result Aggregator | Multiple results → merged | Combined output | Manual |
| Kanban | Enqueue → todo | Status correct | Manual |
| Kanban | Complete → done | Status correct | Manual |

### 2.2 Integration Tests (Flows)

| # | Flow | Steps | Expected |
|---|------|-------|----------|
| F1 | Simple: Write post | User → Intent → Route → Task → Worker → Done → Response | Post written correctly |
| F2 | Simple: Create image | User → Intent → Route → Task → Worker → Done → Response | Image + caption created |
| F3 | Simple: Make video | User → Intent → Route → Task → Worker → Preview → Approve → Post | Video posted to Reels |
| F4 | Simple: Research | User → Intent → Route → Task → Worker → Done → Response | Research delivered |
| F5 | Simple: Answer FAQ | User → Intent → Route → Task → Worker → Done → Response | FAQ answered |
| F6 | Complex: Write → Image | User → Planner → Task A (write) → Task B (image, dep on A) → Aggregate | Paired output |
| F7 | Complex: Full campaign | User → Planner → Write → Image → Video → Aggregate | Complete campaign output |
| F8 | Team ideas first | User assigns team task → Cây Bút returns 3 ideas → user approves one | No image/video assigned before idea approval |
| F9 | Caption before media | After idea approval → caption task runs first → image/video wait for caption | No image/video concept appears before bài viết |
| F10 | Progress tracking | Workers send `[in_progress]` with progress_percent | Kanban shows worker + % + note |
| F11 | Partial output first | Caption sends first; then image/video output sends as each finishes | Gà sends valid artifact immediately in Telegram |
| F12 | 5-minute SLA | Caption deadline after idea approval; image/video deadline after caption done | Gà reports late worker and progress if >5 min |
| F13 | Final approval publish | All outputs delivered → user approves → publish Fanpage/Reels | Publish only after final approval |
| F14 | Delivery gate | Worker done → Aggregator ready → Telegram sends caption/image/video | DONE only after delivery đủ |
| F15 | Missing artifact guard | Worker says `[done]` without image/video URL/file | No DONE log; worker asked to resend |
| F16 | Telegram delivery fail | Artifact exists but Telegram send fails | delivery failed, no complete message |
| F17 | Failure + Retry | Task fails → Retry → Succeeds | Task completes after retry |
| F18 | Failure + Max retry | Task fails 3x → Fails permanently | Error reported |
| F19 | Ambiguous intent | Unclear request → 1 clarifying question → Continues | Correct flow |

### 2.3 Smoke Tests (Post-Deploy)

| # | Test | Command | Expected |
|---|------|---------|----------|
| S1 | Bot alive | Send "hello" to Telegram | Response in brand voice |
| S2 | Write post | "viết bài Facebook giới thiệu tool" | Post generated |
| S3 | Create image | "tạo ảnh quảng cáo" | Image + caption |
| S4 | Video preview | "làm video" | Preview sent |
| S4b | Delivery completion | Sau S2-S4 kiểm log | `DELIVERED` xuất hiện trước `DONE` |
| S4c | Team Telegram flow | "bảo team làm bài về..." → duyệt 1 ý → chờ outputs | 3 ideas first, then partial outputs + progress |
| S5 | FAQ | "tool này giá bao nhiêu" | FAQ answered |
| S6 | Heartbeat | Wait for next heartbeat | Signal check (silent if none) |

### 2.4 Regression Tests (Pre-Release)

| # | Existing Feature | Test | Expected |
|---|-----------------|------|----------|
| R1 | Telegram flow | Send command via Telegram | Response in correct format |
| R2 | Cây Bút workflow | @viet-bai-fb in group | Correct response |
| R3 | Tạo Ảnh workflow | @tao-anh in group | Correct response |
| R4 | Làm Video workflow | @lam-video in group | Correct response |
| R4b | Complete gate | Simulate missing media output | Bot không báo complete |
| R5 | Knowledge lookup | Ask product question | Correct info from knowledge/ |
| R6 | Brand voice | Any response | Matches SOUL.md tone |
| R7 | Heartbeat signals | Check order/lead | Correct notification or silence |

---

## 3. Test Environment

| Environment | Location | Purpose |
|-------------|----------|---------|
| Development | Local clone | File creation, unit tests |
| Staging | VPS (dry-run mode) | Integration tests |
| Production | VPS | Smoke + regression |

**Dry-run mode:** `DRY_RUN=true` prevents actual API calls to Facebook.

---

## 4. Bug Tracking

| Priority | Definition | Response Time |
|----------|-----------|---------------|
| Critical | Existing flow broken | Immediate fix |
| High | New flow broken | Fix before next deploy |
| Medium | Non-functional issue | Next phase |
| Low | Cosmetic, docs | When convenient |

---

## 5. Acceptance Criteria

For each phase to be considered complete:

- [ ] All unit tests pass
- [ ] All integration tests pass (F1-F10)
- [ ] All smoke tests pass (S1-S6)
- [ ] All regression tests pass (R1-R7)
- [ ] No critical or high bugs open
- [ ] ARCHITECT.md updated
- [ ] CLAUDE.md updated
- [ ] Relevant docs/* updated
- [ ] Git diff reviewed
- [ ] User approved
