# RESPONSE BUILDER

> **File:** `core/manager/RESPONSE_BUILDER.md`
> **Role:** Format final response in brand voice before sending to Telegram
> **Part of:** Manager (Gà Trống Tre)
> **Phase:** 1 — Core Framework

---

## 1. Mục đích

Response Builder format kết quả từ `RESULT_AGGREGATOR.md` thành **tin nhắn Telegram** theo đúng brand voice (`agent/SOUL.md`).

**Đầu vào:** Aggregated result object.
**Đầu ra:** Payload Telegram sẵn sàng gửi, gồm text và attachment refs.

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
      - Cây Bút: {writer_progress}% — {writer_note}
      - Tạo Ảnh: {image_progress}% — {image_note}
      - Làm Video: {video_progress}% — {video_note}
      - Đã gửi: {delivered_outputs}
      - Deadline còn: {time_remaining}

      Anh Sáng chờ em chút ạ.

  partial_output_caption:
    # Text bài viết xong trước
    template: |
      Bài viết xong trước đây anh Sáng:

      {caption_text}

      Em đang chờ ảnh/video còn lại.

  partial_output_image:
    # Ảnh xong trước
    template: |
      Ảnh xong rồi anh Sáng.

      [Ảnh đính kèm hoặc link: {image_ref}]

      Em đang chờ bài/video còn lại.

  partial_output_video:
    # Video xong trước
    template: |
      Video preview xong rồi anh Sáng.

      [Video đính kèm hoặc link: {video_ref}]

      Em đang chờ bài/ảnh còn lại.

  error_report:
    # Báo lỗi
    template: |
      Có vấn đề khi xử lý yêu cầu: {error_message}

      Em đã thử lại {attempts} lần nhưng chưa được.
      Anh Sáng muốn em thử lại hay bỏ qua ạ?

  approval_pending:
    # Chờ duyệt
    template: |
      Đủ bộ rồi anh Sáng xem thử:

      {preview_content}

      Nếu OK thì bảo em "duyệt đăng" hoặc "OK đăng" ạ.

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

- **Caption/text:** Gửi nguyên nội dung cho anh Sáng; không thay bằng placeholder.
- **Ảnh:** Gửi kèm file local nếu có `image_local`. Nếu không có file local thì gửi `image_url` + preview/link.
- **Video:** Gửi `video_preview` trước nếu có; nếu không thì gửi `video_url`. Chỉ post Facebook sau khi duyệt.
- **Partial outputs:** Output nào xong trước thì gửi trước cho anh Sáng, không chờ đủ bộ.
- **Approval:** Khi đủ bài viết + ảnh + video, gửi bản tổng hợp cuối và chờ anh Sáng duyệt đăng.
- **Link:** Chỉ gửi khi appropriate — không câu nào cũng đẩy link
- **Group vs DM:**
  - DM: trực tiếp với anh Sáng
  - Group: thông báo team

### 4.1 Delivery Contract

Response Builder không được chỉ tạo câu "[Hình ảnh đính kèm]" hoặc "[Video đính kèm]" rồi kết thúc.
Các placeholder đó chỉ là nhãn nội bộ, không phải bằng chứng đã gửi file.

Trước khi Manager báo hoàn tất:

1. Build danh sách artifact cần gửi:
   - `caption`: từ `caption`, `caption_paired`, hoặc `combined_output`.
   - `image`: từ `image_local` ưu tiên hơn `image_url`.
   - `video`: từ `video_preview` ưu tiên hơn `video_url`.
2. Gửi từng artifact qua Telegram/GoClaw.
3. Ghi nhận artifact đã gửi vào `task.delivery.sent`.
4. Gửi artifact nào xong trước ngay lập tức.
5. Chỉ khi `sent` chứa đủ artifact bắt buộc mới gửi bản tổng hợp cuối để xin duyệt đăng.

Nếu thiếu artifact:

```
Không báo complete.
Báo ngắn: "Em chưa gửi đủ kết quả về Telegram: thiếu {artifact}. Em đang yêu cầu worker gửi lại."
Giữ workflow ở trạng thái đang xử lý.
```

Nếu Telegram gửi lỗi:

```
Không báo complete.
delivery.status = "failed"
delivery.error = "{telegram_error}"
Báo anh Sáng lỗi gửi file/link, kèm artifact nào đã tạo được.
```

---

## 5. Liên kết

- **Input từ:** `RESULT_AGGREGATOR.md` (aggregated result)
- **Output đến:** Telegram (qua GoClaw)
- **Brand voice:** `agent/SOUL.md`
- **Business info:** `agent/USER.md`
