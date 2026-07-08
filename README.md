# GoClaw Agent — Gà Trống Tre (ga-trong-tre)

Agent configuration và skills cho GoClaw platform. Phục vụ business Google Ads Toolkit của anh Công Sáng.

## Agent chính

| Agent | ID | Workspace | Vai trò |
|---|---|---|---|
| 🐔 Gà Trống Tre | `ga-trong-tre` | `/app/workspace/ga-trong-tre` | Lead agent, exec scripts qua workstation |

## Agent hỗ trợ (team)

| Agent | Skill | Vai trò |
|---|---|---|
| 🎨 Tạo Ảnh (`tao-anh`) | `sang-tao-creative-fb` | Tạo ảnh + caption Facebook |
| 🎬 Làm Video (`lam-video`) | `tao-video-ai` | Tạo video AI + đăng Facebook Reels |
| ✍️ Cây Bút (`viet-bai-fb`) | `viet-bai-facebook` | Viết bài Facebook |
| 🦊 Fox Spirit (`fox-spirit`) | `agent-scout`, `tra-loi-faq` | Research web, FAQ khách hàng |

## Skills

| Skill | Mô tả |
|---|---|
| [sang-tao-creative-fb](skills/sang-tao-creative-fb/) | Tạo content Facebook (caption + ảnh + đăng Page) |
| [agent-scout](skills/agent-scout/) | Research web, phân tích đối thủ, SWOT |
| [tao-video-ai](skills/tao-video-ai/) | Tạo video AI + đăng Facebook Reels |
| [viet-bai-facebook](skills/viet-bai-facebook/) | Viết bài Facebook quảng cáo/bán hàng |
| [tra-loi-faq-khach-hang](skills/tra-loi-faq-khach-hang/) | FAQ và tư vấn nhanh Google Ads |

## Workstation

- Tên: `ga-trong-tre-docker`
- Type: Docker
- Path: `/app/workspace/ga-trong-tre`

## Knowledge Base

- `knowledge/brand-voice.md` — Brand voice
- `knowledge/knowledge-base.md` — Kiến thức Google Ads
- `knowledge/my-business.md` — Thông tin business

## Cập nhật

Push code lên GitHub → báo Gà deploy lên VPS.
