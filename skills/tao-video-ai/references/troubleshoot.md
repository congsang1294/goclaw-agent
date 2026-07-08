# Troubleshoot — Lỗi Thường Gặp Và Cách Fix

## 1. AI ra sai chi tiết sản phẩm
**Ví dụ:** Áo khoác da nhưng AI vẽ thành áo vải, sai màu, sai kiểu dáng.

**Fix:** Thêm ảnh cận của đúng chi tiết vào reference. Dùng image-to-video thay vì text-to-video.

**Trong prompt:** "exact copy of [product], matching reference image colors, accurate [specific detail]"

---

## 2. Logo / thương hiệu bị sai
**Ví dụ:** Logo méo, lệch màu, hoặc AI tự vẽ logo sai.

**Fix:** 
- Dùng **Kling 3.0 Element Pin** (upload logo ảnh → AI giữ đúng logo qua các scene)
- Hoặc thêm ảnh logo reference kèm prompt: "exact brand logo, do not modify, keep original colors"
- Hoặc bỏ qua phần logo, thêm logo thật vào video sau bằng CapCut

---

## 3. Motion không mượt / giật
**Ví dụ:** Camera dolly/phốt, zoom giật cục, sản phẩm bị nhòe.

**Fix:**
- Giảm tốc độ: dùng "very slow", "gentle", "smooth"
- Tăng duration mỗi scene lên 1-2s
- Dùng "60fps" trong prompt nếu nền tảng hỗ trợ

---

## 4. Màu sắc lệch brand
**Ví dụ:** Sản phẩm đen thành xám, vàng gold thành đồng.

**Fix:**
- Thêm ảnh reference màu đúng
- Prompt: "exact [color] shade, color code [#XXXXXX], consistent lighting"
- Trên Kling: set image reference weight cao (cfg_scale=0.7+)

---

## 5. Video quá dài / quá ngắn
**Fix:**
- Mỗi scene nên 4-6s
- Tổng 4-5 scenes = 20-25s đẹp
- Nếu cần đúng timing: set duration_s chính xác trong prompts.json

---

## 6. API lỗi / timeout
**Fix:**
- Kiểm tra API key còn hạn không
- Thử dùng dashboard (manual mode) thay vì API
- Higgsfield: API có thể deprecated — dùng Dashboard là an toàn nhất

---

## 7. Background không đẹp
**Fix:**
- Dùng "studio background" hoặc "solid color background #XXXXXX"
- Hoặc upload ảnh background reference
- Đơn giản nhất: "minimalist background, no clutter"
