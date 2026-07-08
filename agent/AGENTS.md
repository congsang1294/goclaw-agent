# AGENTS.md

## VIDEO FLOW
TU KHOA: "video", "tao video", "lam video", "video Reels", "reels", "Facebook Reels", "lam reel"
KHI user noi: use_skill "tao-video-ai". LAM THEO SKILL.md Mode 3. KHONG HOI, KHONG DE XUAT CANVA.

## CONTENT FLOW (sang-tao-creative-fb)
TU KHOA: "content", "bai viet", "caption", "dang bai", "content hom nay", "bai Page"
Day 17 flow:
  Buoc A: cd /app/workspace/ga-trong-tre && python3 scripts/gen_caption.py --task ideas --topic "..."
          Doc JSON, gui 3 y tuong len Telegram. CHO ANH CHON 1/2/3.
  Buoc B1: user chon y -> cd /app/workspace/ga-trong-tre && python3 scripts/gen_caption.py --task organic --topic "..." --angle trust
          In data.caption. HOI "Caption ok khong?"
  Buoc B2: user OK -> cd /app/workspace/ga-trong-tre && python3 scripts/gen_image.py --mode organic --prompt "..." --output output/organic-image.png
          gen_image.py tu gui anh ve Telegram. BAO "Anh da gui ve Telegram. Duyet de dang?"
  Buoc D: user duyet -> cd /app/workspace/ga-trong-tre && python3 scripts/post_facebook.py --image output/organic-image.png --caption-file output/... --confirm-post
          BAO "Da dang! Link: ..."

## TEAM FLOW (Đội Content Gà Tre 2)
Khi user noi trong GROUP: "bảo team làm bài", "chia việc", "giao việc", "làm bài về..."
Gà làm lead, có 3 member:
  - Cây Bút (viet-bai-fb): skill "viet-bai-facebook" -> viết caption
  - Tạo Ảnh (tao-anh): skill "sang-tao-creative-fb" -> tạo ảnh
  - Làm Video (lam-video): skill "tao-video-ai" -> tạo video
  
Cac buoc:
1. Tao task tren Kanban (create_task/assign_task)
2. Dung delegation (agent_links) gui task cho member
3. Thong bao trong group: "Da chia viec: [member A] lam X, [member B] lam Y"
4. Khi co ket qua, bao user

## HEARTBEAT FLOW
Cac function MCP: get_success_order_signal, get_new_lead_signal, get_daily_business_summary
Khi co tin hieu moi: nhan Telegram. Ton tai, khong che, khong spam.
