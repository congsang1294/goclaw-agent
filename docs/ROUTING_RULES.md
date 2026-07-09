# ROUTING RULES

> **File:** `docs/ROUTING_RULES.md`
> **Status:** DESIGN — not yet implemented
> **Last Updated:** 2026-07-08

---

## 1. Core Principle

**Intent → Route → Worker → Skill**

The Router is a **config-driven mapping layer** that translates user intent (derived from natural language) into a Worker assignment. It is NOT hardcoded — adding a new route is adding a config entry.

---

## 2. Intent Detection

### 2.1 Trigger Keywords

| Intent | Keywords | Example Phrases |
|--------|----------|-----------------|
| `write_post` | viết, post, caption, content, bài viết | "viết bài Facebook", "làm caption", "viết content quảng cáo" |
| `create_ideas` | idea, ý tưởng, góc nhìn, concept | "cho 3 ý tưởng", "gợi ý góc viết" |
| `create_image` | ảnh, hình, design, creative, visual | "tạo ảnh", "làm hình quảng cáo", "design creative" |
| `create_video` | video, reels, short, làm video, quay | "làm video", "tạo Reels", "video quảng cáo" |
| `research` | tìm, research, search, tra cứu | "tìm thông tin về", "research đối thủ" |
| `answer_faq` | faq, hỏi, giá?, tool gì?, bao nhiêu | "tool này làm gì", "giá bao nhiêu", "có tư vấn không" |
| `analyze_competitor` | phân tích đối thủ, so sánh, SWOT | "phân tích đối thủ", "so sánh với", "SWOT" |
| `create_ad` | quảng cáo, ads, campaign, chiến dịch | "tạo quảng cáo", "làm campaign" |
| `team_sync` | cả team, đồng bộ, làm đồng loạt | "cả team làm", "làm bài post + ảnh + video" |
| `approve` | ok, duyệt, được, đăng, tốt | "OK", "duyệt", "đăng đi" |
| `check_status` | kiểm tra, tình trạng, tiến độ | "kiểm tra task", "tiến độ đến đâu rồi" |
| `cancel` | hủy, stop, dừng | "hủy task", "dừng lại" |

### 2.2 Intent Resolution Priority

1. **Explicit skill call:** `use_skill "tao-video-ai"` → direct
2. **Keyword match:** Multiple keywords → highest specificity wins
3. **Context-aware:** Previous conversation context disambiguates
4. **Default:** If unclear → Manager asks a clarifying question (max 1)

---

## 3. Routing Table

```yaml
routes:
  - id: write_post
    intents: [write_post, create_ideas]
    worker: viet-bai-fb
    skill: viet-bai-facebook
    description: "Route Facebook post writing to Cây Bút"
    priority: 10

  - id: create_images
    intents: [create_image, create_ad]
    worker: tao-anh
    skill: sang-tao-creative-fb
    description: "Route image creation to Tạo Ảnh"
    priority: 10

  - id: make_video
    intents: [create_video]
    worker: lam-video
    skill: tao-video-ai
    description: "Route video production to Làm Video"
    priority: 10

  - id: team_sync_content
    intents: [team_sync]
    worker: manager  # special: Manager orchestrates all workers
    skill: orchestration
    description: "Multi-worker orchestration by Manager"
    priority: 5  # lower priority = checked first for team requests
```

---

## 4. Routing Logic

### 4.1 Simple Routing

```
Input: "viết bài Facebook giới thiệu tool"
  → Intent: write_post
  → Route lookup: write_post → viet-bai-fb / viet-bai-facebook
  → Result: Task({ worker: "viet-bai-fb", skill: "viet-bai-facebook" })
  → Manager dispatches to Cây Bút
```

### 4.2 Multi-Step Routing (Planner)

```
Input: "làm bài quảng cáo sản phẩm mới"
  → Intent: create_ad
  → Route lookup: create_ad → matches multiple (team_sync has lower priority)
  → Manager.Planner decides based on context:
      If simple image ad → single task to tao-anh
      If full campaign → multi-step: write → image
  → Result: [Task({worker: "viet-bai-fb", ...}), Task({worker: "tao-anh", ...})]
```

### 4.3 Team Sync Routing

```
Input: "cả team làm bài về sản phẩm X"
  → Intent: team_sync
  → Route: team_sync → manager (orchestration mode)
  → Manager.Planner creates full 3-task plan:
      1. viet-bai-fb → caption
      2. tao-anh → image (depends on 1)
      3. lam-video → video (depends on 1, 2)
  → All tasks dispatched with dependency graph
```

---

## 5. Adding a New Route

### 5.1 New Worker + Skill

```
Step 1: Create worker agent
  - agent/<worker-id>/AGENTS.md
  - agent/<worker-id>/SOUL.md

Step 2: Create skill
  - skills/<skill-name>/SKILL.md
  - skills/<skill-name>/assets/ (optional)

Step 3: Register in routing table
  - Add entry to routes.yaml or equivalent config

Step 4: Register in goclaw.yml
  - Add workstation
  - Add Telegram binding (if needed)

Step 5: Update docs
  - AGENT_MAP.md
  - SKILL_MAP.md
  - ROUTING_RULES.md
```

### 5.2 New Route for Existing Worker

```
Just add a new route entry:
  - id: <new_route_id>
    intents: [<new_intent>]
    worker: <existing_worker_id>
    skill: <existing_or_new_skill>
```

---

## 6. Routing Edge Cases

| Case | Behavior |
|------|----------|
| **Ambiguous intent** | Manager asks 1 clarifying question |
| **No route matched** | Manager asks for clarification |
| **Multiple routes** | Highest priority wins; for ties, ask user |
| **Worker unavailable** | Queue task, notify user of delay |
| **Skill execution error** | Retry (up to 3x), then fail task |
| **Cancelled mid-flow** | Cancel all dependent tasks too |
| **Timeout** | Task fails after timeout → retry or cancel |

---

## 7. Route Configuration Format (Future)

```yaml
# config/routes.yaml
routes:
  write_post:
    intents: [write_post, create_ideas]
    worker: viet-bai-fb
    skill: viet-bai-facebook
    timeout: 120
    retry: 3

  create_image:
    intents: [create_image]
    worker: tao-anh
    skill: sang-tao-creative-fb
    timeout: 300
    retry: 2

  # ... more routes
```
