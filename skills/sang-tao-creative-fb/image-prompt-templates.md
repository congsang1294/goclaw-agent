# Template Prompt Ảnh

Dùng các mẫu này với `gpt-image-1`. Mỗi output cuối cùng cho Facebook phải đi kèm caption hoặc ad copy, không tạo ảnh rời.

## Quy Tắc Chung

- Kích thước: 1024x1024.
- Phong cách: ảnh thật, bối cảnh Việt Nam, bố cục sạch, không giống stock quá lộ.
- Không có chữ trong ảnh.
- Không có chữ giả, dòng keyword đọc được, logo, watermark, UI méo.
- Nếu có màn hình laptop/điện thoại, màn hình phải mờ, trừu tượng, bị nghiêng, overexposed, hoặc chỉ là ánh sáng mềm để không sinh chữ giả.
- Tránh cartoon, flat vector, illustration, cảm xúc quá kịch.
- Ảnh cần hiểu được ý chính mà không cần chữ, nhưng vẫn nên có khoảng trống nếu sau này muốn overlay.

## Mode 1: Content Organic

Dùng `quality=low` để tiết kiệm chi phí.

Khung prompt:

```text
Ảnh vuông realistic tại Việt Nam. [một cảnh người thật/bối cảnh công việc gắn với ý tưởng]. Ánh sáng tự nhiên, khoảnh khắc đời thường, chi tiết bàn làm việc thực tế. Cảm xúc thật, bình tĩnh, không quảng cáo. Có một vùng nền sạch để có thể chèn text nếu cần. Không có chữ trong ảnh, không có logo, không watermark, không có ký tự giả.
```

Ví dụ:

```text
Ảnh vuông realistic tại Việt Nam. Một chủ shop nhỏ ngồi trước laptop vào buổi tối, màn hình laptop quay nghiêng và chỉ hiện ánh sáng mờ, không có chữ đọc được. Trên bàn có sổ tay, ly cà phê, điện thoại. Người này hơi mệt nhưng vẫn tập trung, giống đang xử lý một việc lặp lại. Ánh sáng phòng tự nhiên, cảm giác candid. Có một vùng nền sạch bên phải. Không có chữ trong ảnh, không có logo, không watermark, không có ký tự giả.
```

## Mode 2: Creative Ads

Dùng `quality=medium`. Tạo 3 angle khác nhau.

Pain point:

```text
Ảnh vuông realistic tại Việt Nam. Một người chạy ads hoặc chủ shop làm việc muộn bên laptop, màn hình bị làm mờ hoàn toàn và không có chữ đọc được. Trên bàn có giấy note trống, ly cà phê, điện thoại. Cảm xúc hơi mệt vì phải làm việc nhỏ lặp lại nhiều lần. Bố cục có khoảng trống cho headline overlay. Không có chữ trong ảnh, không logo, không watermark, không ký tự giả.
```

Solution:

```text
Ảnh vuông realistic tại Việt Nam. Một freelancer ngồi ở quán cà phê, laptop mở nhưng màn hình chỉ là ánh sáng mờ không chữ. Gương mặt nhẹ nhõm vì vừa xử lý xong việc setup keyword nhanh hơn. Ánh sáng ban ngày, bàn sạch, cảm giác đời thường. Có khoảng trống cho headline overlay. Không có chữ trong ảnh, không logo, không watermark.
```

Social proof:

```text
Ảnh vuông realistic tại Việt Nam. Một người nhìn checklist giấy trống cạnh laptop, biểu cảm nhẹ nhõm sau khi hoàn thành việc format keyword. Background là góc làm việc nhỏ, ánh sáng ấm, chân thật. Có khoảng trống sạch cho headline overlay. Không có chữ trong ảnh, không logo, không watermark, không ký tự giả.
```
