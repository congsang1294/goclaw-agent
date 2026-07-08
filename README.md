# GoClaw Agent — Google Ads Toolkit

Agent configuration cho GoClaw platform. Agent **Gà Trống Tre** phục vụ business Google Ads Toolkit của anh Công Sáng.

## Cấu trúc

```
agent/           — cấu hình nhân dạng, quyền hạn, heartbeat, soul
skills/          — kỹ năng và script triển khai
goclaw.yml       — cấu hình GoClaw platform
```

## Các kỹ năng

- **tao-creative-fb-gpt**: Tạo content Facebook (caption + ảnh) qua GPT, đăng lên Page
- **tao-creative-fb**: Dual-cron auto post Facebook (gen + đăng)
- **tao-video-ai**: Tạo video AI (Higgsfield/Kling) và đăng đa nền tảng
- **viet-bai-facebook**: Viết bài Facebook organic
- **sang-tao-creative-fb**: Sáng tạo creative Facebook ads

## Workstation

Agent sử dụng Docker workstation `ga-trong-tre-docker` để exec Python scripts.

## Quyền Telegram

Chỉ Telegram user ID `6880126421` (anh Sáng) mới có quyền ra lệnh sửa đổi hệ thống.
