# Brand Style — Hướng dẫn tone & visual cho AI Video

## Tone mặc định: Luxury Premium

Áp dụng khi không có brand-specific style. Phù hợp cho: thời trang, phụ kiện, mỹ phẩm cao cấp.

### Visual Guidelines
- **Ánh sáng:** Studio lighting — soft key light + fill, rim light tạo depth
- **Màu sắc:** Ấm (golden hour) hoặc cool tone (xanh dương đậm) — tuỳ mood sản phẩm
- **Background:** Tối giản, texture nhẹ (marble, velvet, concrete mịn)
- **Depth of field:** Shallow DOF — focus vào sản phẩm, background blur
- **Chất liệu:** Highlight texture — da, vải, kim loại phải thấy rõ grain/weave
- **Tỷ lệ:** 9:16 (TikTok/Reels) — luôn giữ sản phẩm ở centre 1/3 trên

### Color Palette (mặc định)
| Màu       | Hex       | Dùng cho               |
|-----------|-----------|------------------------|
| Đen       | #0A0A0A   | Background chính       |
| Beige     | #F5F0E8   | Background phụ         |
| Vàng gold | #C9A84C   | Accent, highlight      |
| Trắng     | #FAFAFA   | Text, product nền sáng |
| Xám đậm   | #2D2D2D   | Shadow, gradient       |

### Typography (cho video text overlay)
- Font: Sans-serif hiện đại (Helvetica Now, Inter, SF Pro)
- Weight: Light cho body, Bold cho CTA
- Animation: Fade in nhẹ, không bounce/quá giật

---

## Tone Casual Streetwear

Áp dụng khi sản phẩm streetwear / sneaker / youthful brand.

### Visual Guidelines
- **Ánh sáng:** Natural lighting, hơi high-key, có thể hơi overexposed một chút
- **Màu sắc:** Vibrant — tương phản cao, saturation nhẹ
- **Background:** Urban — street, concrete wall, graffiti mờ phía sau
- **Camera:** Gần hơn, góc hơi low-angle để tạo mạnh mẽ
- **Chuyển động:** Nhanh hơn luxury — snap transition, motion blur nhẹ

### Color Palette (casual)
| Màu     | Hex       | Dùng cho               |
|---------|-----------|------------------------|
| Trắng   | #FFFFFF   | Nền chính              |
| Đen     | #1A1A1A   | Text, accent           |
| Cam     | #FF6B35   | CTA, highlight         |
| Xanh    | #2563EB   | Accent phụ             |
| Xám     | #F3F4F6   | Background phụ         |

---

## Tone Minimal / Clean

Áp dụng cho tech accessory, skincare basic, hoặc brand muốn tối giản.

### Visual Guidelines
- **Ánh sáng:** Flat lighting, soft diffused, không shadow mạnh
- **Màu sắc:** Pastel / desaturated — beige, cream, xám nhạt
- **Background:** Màu đồng nhất, gradient nhẹ
- **Composition:** Centre frame, đối xứng, nhiều negative space
- **Chuyển động:** Slow, smooth — không camera shake

---

## Cách dùng

Khi gen prompt, append style guidelines vào prompt chính:

```
Ví dụ — thêm vào cuối prompt:
Style: Luxury — studio lighting, shallow DOF, gold accent on black background, soft rim light, 9:16 vertical, rich fabric texture visible.
```

Hoặc override hoàn toàn brand style bằng parameter:
```
python gen-prompt.py "áo khoác" --style assets/brand-style.md
```
