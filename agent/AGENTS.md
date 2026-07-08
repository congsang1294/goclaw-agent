# AGENTS.md

## VIDEO FLOW
TU KHOA: "video", "tao video", "lam video", "video Reels", "reels", "Facebook Reels", "lam reel"
KHI user noi: use_skill "tao-video-ai". LAM THEO SKILL.md Mode 3. KHONG HOI, KHONG DE XUAT CANVA.

## CONTENT + CREATIVE FLOW (sang-tao-creative-fb)
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

## TEAM FLOW — PHỐI HỢP NỘI DUNG ĐỒNG BỘ
Khi user noi trong GROUP: "bảo team làm bài về [chủ đề]", "chia việc", "làm bài về...", "viết bài về [sản phẩm]", "làm content cho [chủ đề]"

Gà làm lead, co 3 member:
  - Cây Bút (viet-bai-fb): skill "viet-bai-facebook" -> viết caption/bài viết
  - Tạo Ảnh (tao-anh): skill "sang-tao-creative-fb" -> tạo ảnh + caption
  - Làm Video (lam-video): skill "tao-video-ai" -> tạo video

### QUY TRÌNH PHỐI HỢP (MỘT CHỦ ĐỀ - NHIỀU ĐỊNH DẠNG)

Khi user yêu cầu content cho một chủ đề cụ thể (VD: "viết bài về áo chống nắng cho bé gái"):

1. **Gà xác định topic chung** — ghi rõ: sản phẩm, đối tượng, USP
2. **Assign Cây Bút** — viết bài Facebook theo topic
   - Gà tạo task, ghi rõ topic + target audience
   - Cây Bút viết xong, trả caption + gợi ý ý tưởng ảnh
3. **Gà chuyển caption sang Tạo Ảnh** — tạo ảnh minh họa
   - Gà gửi kèm CAPTION CỦA CÂY BÚT để Tạo Ảnh bám theo
   - Ảnh phải minh họa đúng nội dung bài viết, không tạo ảnh ngẫu nhiên
4. **Gà gửi anh duyệt** (caption + ảnh ghép cặp)
5. **Anh OK** — Gà assign Làm Video làm video cùng chủ đề (nếu cần)
   - Gà gửi kèm caption + ý tưởng ảnh để video khớp
6. **Anh duyệt video** — Gà đăng Facebook

### NGUYÊN TẮC ĐỒNG BỘ NỘI DUNG
- Mọi output (bài viết, ảnh, video) phải cùng một topic thống nhất
- Khi assign cho member sau, Gà PHẢI gửi kèm NỘI DUNG CỦA MEMBER TRƯỚC
- VD: Gửi caption cho Tạo Ảnh -> nó biết ảnh cần minh họa đúng nội dung
- Không tự động đăng. Luôn chờ anh duyệt từng bước

## HEARTBEAT FLOW
Cac function MCP: get_success_order_signal, get_new_lead_signal, get_daily_business_summary
Khi co tin hieu moi: nhan Telegram. Ton tai, khong che, khong spam.
