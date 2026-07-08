# Troubleshooting — Xử lý lỗi thường gặp khi gen AI Video

## 1. Sai Chi Tiết Sản Phẩm

**Vấn đề:** AI sinh sai số lượng dây kéo, sai vị trí logo, sai kiểu cổ áo, v.v.

**Nguyên nhân:** Prompt quá chung chung, thiếu reference ảnh.

**Cách fix:**
1. **Thêm ảnh cận (detail shot)** — chụp cận chỗ hay sai nhất
2. **Thêm ảnh từ nhiều góc** — front, side, back, inside
3. **Mô tả trong prompt chi tiết hơn:**
   - "double zipper with silver hardware, not single"
   - "stand collar, not notch lapel"
   - "embossed logo on left chest, 3cm below shoulder seam"
4. **Dùng Element Pin trên Kling 3.0** — nếu platform support

```bash
# Sau khi thêm ảnh detail, chạy lại list-images để cập nhật mapping
python scripts/list-images.py
# Sửa prompt với detail hơn
python scripts/gen-prompt.py "áo khoác da" --provider claude
```

---

## 2. Sai Logo

**Vấn đề:** AI sinh sai logo, logo biến dạng, hoặc không có logo.

**Nguyên nhân:** AI video không handle text/logo tốt.

**Cách fix:**
1. **Kling 3.0 Element Pin** — dùng feature này để pin logo vào sản phẩm
2. **Chia tách:** Gen video KHÔNG logo, sau đó overlay logo bằng hậu kỳ (CapCut/Premiere)
3. **Prompt điều chỉnh:**
   - KHÔNG yêu cầu AI tự sinh logo — chỉ "product without branding"
   - Hoặc: "product with embossed text on front" nếu logo là emboss
4. **Nếu bắt buộc có logo:** Dùng image-to-video với ảnh đã có logo thật

---

## 3. Motion Sai Hướng / Quá Nhanh / Quá Giật

**Vấn đề:** Camera chạy sai hướng, speed không đúng, bị giật (stutter)

**Nguyên nhân:** Prompt camera không rõ ràng, duration không phù hợp.

**Cách fix:**
1. **Speed specifier:**
   - Thay "orbiting camera" → "slow gentle orbiting camera, 1 full rotation in 5 seconds"
   - Thay "dolly in" → "extremely slow dolly in, push 30cm over 4 seconds"
2. **Duration:**
   - Scene ngắn (4s) → motion nhẹ
   - Scene dài (6-7s) → motion chậm hơn
3. **Nếu bị stutter:** Giảm camera motion, làm minimal movement
4. **Tham khảo camera-prompts.md** để chọn đúng motion cho scene

---

## 4. Artifact / Glitch / Morphing

**Vấn đề:** Sản phẩm bị biến dạng, chảy nhựa, merge với background.

**Nguyên nhân:** Model không hiểu rõ đối tượng — phổ biến ở Kling/Runway với object phức tạp.

**Cách fix:**
1. **Thêm negative prompt:**
   ```
   morphing, warping, melting, stretching, distorting, twisting,
   plastic, liquid, clay, dripping, disintegrating, flickering, glitch artifact
   ```
2. **Giảm độ phức tạp:** Đơn giản hóa prompt — ít elements hơn
3. **Tăng reference image weight** (nếu platform support)
4. **Chia scene ngắn hơn:** 4s thay vì 6s — giảm cơ hội artifact
5. **Thử platform khác:** Nếu Kling bị artifact → thử Runway Gen-4

---

## 5. Màu Sắc Sai So Với Sản Phẩm Thật

**Vấn đề:** AI thay đổi màu sản phẩm — đen thành xám, đỏ thành cam, v.v.

**Nguyên nhân:** AI color shift do lighting prompt.

**Cách fix:**
1. **Specify exact color:**
   - "exact color: #1A1A1A black, not charcoal, not gray"
   - "the product color must remain pure black throughout"
2. **Dùng ảnh reference chất lượng cao** — màu đúng với sản phẩm thật
3. **Lighting neutral:**
   - Thay "warm golden lighting" → "neutral white studio lighting, no color cast"
   - Tránh colored lighting nếu cần giữ màu chính xác
4. **Nếu đã sai:** Gen lại scene đó với prompt màu chính xác hơn, không regen toàn bộ

---

## 6. Video Quá Ngắn / Quá Dài

**Mục tiêu:** 15-25s

**Quá ngắn (<15s):**
- Thêm transition scene giữa các scene (0.5s fade)
- Thêm 1 scene B-roll (lifestyle hoặc detail khác)
- Slow motion từng scene (kéo 5s → 6-7s)

**Quá dài (>25s):**
- Bỏ scene ít quan trọng nhất (thường là scene lifestyle)
- Rút ngắn scene CTA (3s thay vì 5s)
- Tăng tốc motion nhẹ

---

## 7. AI Không Giữ Được Consistent Sản Phẩm

**Vấn đề:** Sản phẩm ở scene 1 khác scene 3

**Nguyên nhân:** AI video không có "memory" giữa các scene.

**Cách fix:**
1. **Dùng same reference image cho tất cả scene**
2. **Copy exact description của sản phẩm vào mọi prompt** — không rút gọn
3. **Seed number** — nếu platform hỗ trợ, dùng same seed
4. **Model tốt hơn:** Kling 3.0 > Runway Gen-3 > Pika về consistency

**Template product description để copy vào mọi prompt:**
```
[Product]: Black matte leather biker jacket with silver double zipper,
asymmetric zip front, notched lapel, quilted shoulder panels,
4 exterior pockets, silver snap buttons on pockets, ribbed hem.
```

---

## Quick Reference

| Lỗi | Fix Priority |
|-----|-------------|
| Sai chi tiết | Thêm ảnh cận + mô tả chi tiết |
| Sai logo | Kling 3.0 Element Pin hoặc overlay hậu kỳ |
| Motion sai | Speed specifier + check camera type |
| Artifact | Negative prompt + scene ngắn hơn |
| Sai màu | Neutral lighting + exact color hex |
| Inconsistent | Copy exact product desc vào mọi scene |
| Quá ngắn | Thêm transition + B-roll |
| Quá dài | Bỏ scene lifestyle |
