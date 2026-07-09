# 🐔 Gà Trống Tre — AI Team Framework

> **Version:** 1.0.0 | **Status:** Active | **Runtime:** GoClaw

**Gà Trống Tre** là một AI Team Framework có thể tái sử dụng cho nhiều dự án. Framework biến một AI agent đơn thành đội nhóm multi-agent với Manager điều phối, Worker chuyên môn hóa, và Task/Kanban làm trung tâm.

Dự án gốc phục vụ business **Google Ads Toolkit** của anh **Công Sáng**, nhưng framework được thiết kế để clone và tùy chỉnh cho bất kỳ dự án nào.

---

## 🎯 Use Cases

| Dự Án | Chỉ Cần Thay |
|-------|-------------|
| Google Ads | Brand Voice, Knowledge, Skills |
| Affiliate Marketing | Offers, Funnel, Content Skills |
| YouTube AI | Video Script, Thumbnail Skills |
| SEO | Keyword Research, Content Skills |
| Email Marketing | Sequence, Copy, Automation Skills |
| Customer Support | FAQ, Knowledge Base, Ticket Skills |

---

## 🏗️ Architecture

```
Telegram (User)
    │
    ▼
Manager (Gà Trống Tre) — Intent → Plan → Task
    │
    ▼
Dynamic Router — maps intent to Worker
    │
    ▼
Kanban / Task Board — TODO → IN_PROGRESS → DONE
    │
    ├── Cây Bút (Content Writer)
    ├── Tạo Ảnh (Image Creator)
    └── Làm Video (Video Editor)
```

**Nguyên tắc:** Manager điều phối, Worker thực thi, Task là trung tâm. Không Agent gọi Agent trực tiếp.

---

## 👥 Team Hiện Tại

| Agent | ID | Skill | Vai Trò |
|-------|-----|-------|---------|
| 🐔 **Gà Trống Tre** | `ga-trong-tre` | All (orchestration) | Manager — điều phối tổng thể |
| ✍️ **Cây Bút** | `viet-bai-fb` | `viet-bai-facebook` | Viết bài Facebook |
| 🎨 **Tạo Ảnh** | `tao-anh` | `sang-tao-creative-fb` | Tạo ảnh + caption |
| 🎬 **Làm Video** | `lam-video` | `tao-video-ai` | Tạo video AI + đăng Reels |

---

## 📁 Project Structure

```
goclaw-agent/
│
├── goclaw.yml              # GoClaw runtime config (DO NOT MODIFY lightly)
├── ARCHITECT.md            # 🏛️ System architecture (read this first)
├── CLAUDE.md               # 📖 Rule book for development
├── README.md               # This file
│
├── agent/                  # 📋 Agent definitions
│   ├── AGENTS.md           # Manager orchestration rules
│   ├── SOUL.md             # Brand identity & voice
│   ├── USER.md             # Owner profile
│   ├── HEARTBEAT.md        # Monitoring signals
│   ├── viet-bai-fb/        # Cây Bút Worker
│   ├── tao-anh/            # Tạo Ảnh Worker
│   └── lam-video/          # Làm Video Worker
│
├── knowledge/              # 🧠 Shared knowledge (one source of truth)
│   ├── brand-voice.md      # Brand tone & language
│   ├── knowledge-base.md   # Product FAQ & knowledge
│   └── my-business.md      # Business model, pricing, customers
│
├── skills/                 # 🔌 Skills Engine (plugin directory)
│   ├── viet-bai-facebook/  # Facebook post writing
│   ├── sang-tao-creative-fb/ # Creative image + caption
│   ├── tao-video-ai/       # AI video production
│   ├── agent-scout/        # Web research & analysis
│   └── tra-loi-faq-khach-hang/ # Customer FAQ support
│
├── core/                   # 🏗️ Framework core (Phase 1+)
│   ├── manager/            # Manager orchestration
│   ├── router/             # Dynamic routing
│   ├── kanban/             # Task/Kanban system
│   └── dispatcher/         # Task dispatching
│
├── memory/                 # 💾 Persistent memory (Phase 3+)
│
└── docs/                   # 📚 Documentation
    ├── SYSTEM_ARCHITECTURE.md  # Architecture deep-dive
    ├── AGENT_MAP.md            # Agent inventory
    ├── SKILL_MAP.md            # Skill definitions
    ├── TOOL_MAP.md             # Tool inventory
    ├── TASK_LIFECYCLE.md       # Task & Kanban design
    ├── ROUTING_RULES.md        # Dynamic routing
    ├── DATABASE_ANALYSIS.md    # Database analysis
    ├── IMPLEMENTATION_PLAN.md  # Implementation phases
    ├── TEST_PLAN.md            # Testing strategy
    ├── RISK_ANALYSIS.md        # Risk assessment
    └── ROADMAP.md              # Long-term roadmap
```

---

## 🚀 Getting Started

### Clone cho dự án mới

```bash
# (Coming in Phase 5)
git clone <repo-url> my-project
cd my-project
# Edit knowledge/, agent/, skills/ cho dự án của bạn
# Framework core không cần sửa
```

### Các bước tùy chỉnh

| Step | File | What to Change |
|------|------|----------------|
| 1 | `knowledge/brand-voice.md` | Tone, vocabulary, writing rules |
| 2 | `knowledge/my-business.md` | Business model, products, pricing |
| 3 | `knowledge/knowledge-base.md` | Domain FAQ, objections |
| 4 | `agent/USER.md` | Owner info |
| 5 | `agent/SOUL.md` | Agent identity |
| 6 | `agent/AGENTS.md` | Orchestration rules |
| 7 | `agent/HEARTBEAT.md` | Monitoring signals |
| 8 | `skills/` | Add/modify domain-specific skills |
| 9 | `goclaw.yml` | Workspace, Telegram bindings |

---

## 🧠 Design Principles

| # | Principle | Mô Tả |
|---|-----------|-------|
| 1 | **Task is center** | Mọi việc đều là Task. Agent giao tiếp qua Task |
| 2 | **Manager routes, Workers execute** | Manager lập kế hoạch. Worker chỉ chạy Skill |
| 3 | **Routing is dynamic** | Intent → Route → Worker. Thêm Worker = thêm route |
| 4 | **Skills are plugins** | Skill tự chứa (trigger, input, output). Không gọi chéo |
| 5 | **Context shared** | Một nguồn sự thật duy nhất (knowledge/) |
| 6 | **Memory persists** | Lịch sử Task để học và cải thiện |
| 7 | **No agent-to-agent** | Chỉ Manager → Worker qua Task. Không gọi trực tiếp |
| 8 | **Backward compatible** | Không phá vỡ flow Telegram, Skill, Knowledge hiện có |

---

## 🔗 Related Projects

- **Web App:** [tool.congsang.info.vn](https://tool.congsang.info.vn/) — Google Ads Match Type Converter
- **Consulting:** [congsang.info.vn](https://congsang.info.vn/) — Google Ads consulting services

---

## 📝 License & Ownership

© 2026 **Công Sáng Nguyễn** — All rights reserved.

Owner: [anh Sáng](agent/USER.md) (Telegram: `6880126421`)

---

## 🔄 Deploy

```bash
git push origin main
# Báo Gà deploy lên VPS
# Docker containers tự động cập nhật
```

---

*Built with ❤️ cho anh Sáng và Gà Trống Tre — "Không làm màu. Không dạy đời. Không bán quá sớm."*
