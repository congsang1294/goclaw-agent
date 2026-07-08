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
