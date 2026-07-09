# RESPONSE BUILDER

> **File:** `core/manager/RESPONSE_BUILDER.md`
> **Role:** Format final response in brand voice before sending to Telegram
> **Part of:** Manager (Gà Trống Tre)
> **Phase:** 1 — Core Framework

---

## 1. Mục đích

Response Builder format kết quả từ `RESULT_AGGREGATOR.md` thành **tin nhắn Telegram** theo đúng brand voice (`agent/SOUL.md`).

**Đầu vào:** Aggregated result object.
**Đầu ra:** Tin nhắn Telegram sẵn sàng gửi.

---

## 2. Format Rules

### 2.1 Content Type → Format Template

```yaml
formats:
  single_caption:
    # Kết quả là 1 caption/idea
    template: |
      {caption_text}
      
      ---
      Gửi anh Sáng duyệt ạ.

  paired_content:
    # Caption + Ảnh
    template: |
      {caption_text}
      
      [Hình ảnh đính kèm]
      
      ---
      Anh Sáng xem thử nếu thấy ổn thì bảo em đăng ạ.

  campaign_content:
    # Caption + Ảnh + Video
    template: |
      {caption_text}
      
      [Hình ảnh + Video đính kèm]
      
      ---
      Cả bộ đã xong. Anh Sáng duyệt em đăng nhé.

  status_report:
    # Báo cáo tiến độ
    template: |
      Hiện tại em đang xử lý:
      - {task_count} tasks đang chạy
      - {task_details}
      
      Anh Sáng chờ em chút ạ.

  error_report:
    # Báo lỗi
    template: |
      Có vấn đề khi xử lý yêu cầu: {error_message}
      
      Em đã thử lại {attempts} lần nhưng chưa được.
      Anh Sáng muốn em thử lại hay bỏ qua ạ?

  approval_pending:
    # Chờ duyệt
    template: |
      Đã xong phần của em. Anh Sáng xem thử:
      
      {preview_content}
      
      Nếu OK thì bảo em "đăng" ạ.

  signal_order:
    # HEARTBEAT: đơn hàng mới
    template: |
      Có đơn Pro thành công: {customer_name}, mã {order_code}, {amount}đ.
      Hôm nay: {daily_orders} đơn, {daily_revenue}đ. Tổng lead: {total_leads}.

  signal_lead:
    # HEARTBEAT: lead mới
    template: |
      Có lead mới: {customer_name}, {phone}, {email}.
      Khó khăn: {challenge}. Quan tâm: {interest}.
      Tổng lead: {total_leads}.
```

### 2.2 Brand Voice Rules

Khi format response, luôn tuân theo `agent/SOUL.md`:

- **Giọng:** gần gũi, thẳng, ngắn, không corporate
- **Tiếng Việt:** có dấu, tự nhiên
- **Không:** jargon, hoa mỹ, bán hàng quá sớm
- **CTA:** nhẹ nhàng — "Anh em ghé vào xem thử"
- **Ngắn gọn:** không viết lại toàn bộ lịch sử

---

## 3. Các trường hợp đặc biệt

| Tình huống | Format |
|-----------|--------|
| User hủy task | "Đã hủy. Anh Sáng cần gì thêm không?" |
| Unknown intent | "Em chưa hiểu ý anh lắm. Anh muốn viết bài, tạo ảnh, hay làm video ạ?" |
| Task đang chạy, user hỏi | Dùng `status_report` |
| Không có gì mới (heartbeat) | Im lặng — không gửi gì |
| Lỗi kỹ thuật | Dùng `error_report`, không đổ lỗi cho AI |

---

## 4. Telegram-specific Rules

- **Ảnh:** Gửi kèm file hoặc URL. Nếu là URL → gửi link + preview
- **Video:** Gửi preview trước, chỉ post Facebook sau khi duyệt
- **Link:** Chỉ gửi khi appropriate — không câu nào cũng đẩy link
- **Group vs DM:** 
  - DM: trực tiếp với anh Sáng
  - Group: thông báo team

---

## 5. Liên kết

- **Input từ:** `RESULT_AGGREGATOR.md` (aggregated result)
- **Output đến:** Telegram (qua GoClaw)
- **Brand voice:** `agent/SOUL.md`
- **Business info:** `agent/USER.md`
