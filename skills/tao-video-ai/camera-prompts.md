# Camera Prompts — 5 Motion Thắng Cho AI Video

Đây là **5 dạng camera motion đã kiểm chứng** cho AI video generation
(Kling 3.0, Runway Gen-4, Stream 4.5, Pika, Higgsfield).

## 1. Orbit Nhẹ (Light Orbit)

**Khi dùng:** Scene mở / Hero shot — giới thiệu sản phẩm từ từ

```
Prompt pattern:
"A cinematic [product] rotating slowly on a [surface], gentle orbiting camera movement,
[specific lighting], [background], 8K quality, shallow depth of field"

Ví dụ:
"A premium leather jacket rotating slowly on a marble pedestal, gentle orbiting camera movement,
warm studio lighting with golden rim light, dark minimalist background, 8K quality, shallow depth of field"
```

**Tips:**
- Tốc độ orbit: "slow orbiting" — không "fast spin"
- Kết hợp: orbit + slight upward tilt để tạo grand reveal
- Duration lý tưởng: 4-6s

---

## 2. Dolly In (Slow Push)

**Khi dùng:** Detail shot — kéo từ tổng thể vào chi tiết

```
Prompt pattern:
"A cinematic close-up of [detail], slow dolly in camera movement,
[texture description], [lighting], hyperrealistic, 8K"

Ví dụ:
"A cinematic close-up of leather texture, slow dolly in camera movement,
visible grain and stitching details, soft key light from left,
hyperrealistic, 8K"
```

**Tips:**
- Dolly in chậm hơn bình thường — AI dễ bị overshoot nếu nhanh
- Focus keyword: "hyperrealistic texture" — giúp AI giữ detail khi zoom
- Duration lý tưởng: 4-5s

---

## 3. Pan Slow (Horizontal Pan)

**Khi dùng:** Lifestyle / Context — cho thấy sản phẩm trong môi trường

```
Prompt pattern:
"A cinematic scene of [subject wearing/using product], slow horizontal pan camera movement,
[environment description], [lighting], natural motion, cinematic color grading"

Ví dụ:
"A model wearing a leather jacket walking down an urban street, slow horizontal pan camera movement,
golden hour lighting, city background with bokeh lights, natural motion, cinematic color grading"
```

**Tips:**
- Pan chậm + có foreground element để tạo depth
- Tránh pan quá nhanh — AI hay sinh ghosting artifacts
- Duration lý tưởng: 5-7s

---

## 4. Key Zoom (Push-Pull)

**Khi dùng:** CTA / Kết — tạo impact cuối video

```
Prompt pattern:
"A dramatic [product] centered in frame, key zoom camera movement — slow zoom out revealing
[value prop / context], [dramatic lighting], cinematic atmosphere, volumetric lighting"

Ví dụ:
"A dramatic leather jacket centered in frame, key zoom camera movement — slow zoom out revealing
the complete silhouette, dramatic spotlight lighting, cinematic atmosphere, volumetric lighting"
```

**Tips:**
- Zoom out (pull) thường đẹp hơn zoom in (push) cho CTA
- Kết hợp lighting thay đổi: tối → sáng dần
- Duration lý tưởng: 4-6s

---

## 5. Multishot / Composite

**Khi dùng:** Hook mở / Showcase tổng thể — nhiều góc một lúc

```
Prompt pattern:
"A cinematic composite shot of [product], multishot style showing [number] different angles simultaneously,
[lighting consistent across all angles], [background], 8K quality"

Ví dụ:
"A cinematic composite shot of a leather jacket, multishot style showing 3 different angles simultaneously,
consistent warm studio lighting across all angles, dark gradient background, 8K quality"
```

**Tips:**
- Số lượng góc: 2-3 — nhiều hơn AI dễ bị confuse
- Keyword "consistent lighting" rất quan trọng để giữ đồng bộ
- Duration lý tưởng: 4-5s

---

## Cheat Sheet — Chọn motion theo scene

| Scene Type     | Nên dùng        | Không nên dùng  |
|----------------|-----------------|-----------------|
| Hook / Mở      | Orbit, Multishot| Pan (quá chậm)  |
| Detail         | Dolly In        | Orbit (mất focus)|
| Lifestyle      | Pan Slow        | Key Zoom        |
| CTA / Kết      | Key Zoom        | Multishot       |
| Transition     | Pan + Dolly combo | Orbit (say)   |

## Lưu ý khi viết prompt cho AI Video

1. **Luôn bắt đầu với "cinematic"** — set quality expectation ngay từ đầu
2. **Specify camera movement ở vị trí thứ 2** — AI cần biết camera làm gì trước detail
3. **Chất liệu ở vị trí thứ 3** — texture là yếu tố quyết định realistic
4. **Ánh sáng ở vị trí thứ 4** — lighting quyết định mood
5. **Thêm "8K" hoặc "4K" ở cuối** — push quality
6. **KHÔNG dùng** từ "video" hay "animation" trong prompt — AI dễ hiểu nhầm
