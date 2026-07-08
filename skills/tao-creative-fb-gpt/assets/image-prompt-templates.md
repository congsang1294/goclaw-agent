# Image Prompt Templates — Google Ads Match Type Converter

Dùng các khối dưới đây để tạo `image_prompt` cho GPT Image. Prompt cuối phải viết bằng tiếng Anh và mô tả một ảnh duy nhất.

## Brand visual

- Bối cảnh: văn phòng làm việc hiện đại, góc làm việc cá nhân (home office) tối giản, sáng sủa, sạch sẽ, đầy ánh sáng tự nhiên.
- Nhân vật chính: một digital marketer, chủ shop online, hoặc freelancer người Việt (nam hoặc nữ) đang tập trung làm việc hoặc cười mỉm nhẹ nhõm, thể hiện sự thảnh thơi, hài lòng.
- Cảm giác: an tâm, bảo mật, thảnh thơi, tiết kiệm thời gian nhờ công nghệ offline xử lý tại chỗ.
- Phong cách: commercial lifestyle photography, photorealistic, natural skin texture, realistic screen displays.
- Màu gợi ý: xanh dương (đặc trưng Google Ads), trắng, xám trung tính, ánh sáng tự nhiên.
- Không tự tạo logo, biểu tượng, hoặc các giao diện chứa chữ tiếng Việt méo mó.
- Hạn chế vẽ chi tiết các chữ trên màn hình laptop, nên vẽ màn hình mờ hậu cảnh hoặc chỉ hiển thị các biểu đồ đơn giản không chữ.

## Organic template

```text
Create a photorealistic square Facebook image for a modern, secure digital marketing workspace in Vietnam.

TOPIC: {topic}
SCENE: a clean, minimalist home office desk with natural morning light coming through a window.
SUBJECT: an approachable Vietnamese digital marketer working contentedly on a laptop. The keyboard and screen are visible but slightly blurred in the background.
CUSTOMER CONTEXT: the marketer looks relaxed, relieved from tedious manual work.
MOOD: calm, secure, organized, highly efficient, professional.
COMPOSITION: natural candid moment, balanced 1:1 framing, shallow depth of field focusing on the person.
LIGHTING: soft natural daylight, clean neutral colors with subtle blue accents.
CAMERA: commercial lifestyle photography, realistic proportions, high detail.

No text, no logo, no watermark, no gibberish letters on screen, no messy workspace.
```

Organic nên ưu tiên khoảnh khắc hữu ích:

- Người dùng thảnh thơi nhấp ngụm cà phê khi công việc convert keyword hoàn thành tức thì.
- Marketer làm việc thoải mái trên điện thoại di động khi đang di chuyển (ngoài quán cà phê, taxi).
- Marketer chỉ tay vào màn hình laptop hiển thị một biểu đồ tăng trưởng sạch sẽ, tối giản.
- Hai cộng sự làm việc chung, cười nhẹ nhõm khi chuẩn bị xong list keyword cho dự án mới.

## Ads — Pain point

```text
Create a photorealistic square Facebook ad image showing the frustration of {problem} in digital marketing.

Show a Vietnamese digital marketer or business owner aged about 25–40 looking tired or overwhelmed while working at a desk late in the evening. They are looking at a laptop screen filled with messy spreadsheets. Keep the situation realistic and relatable, with no exaggerated expressions.

Composition: subject and messy laptop screen placed on the right two-thirds, clean negative space on the left for later text overlay, strong visual hierarchy.
Lighting: dim indoor evening lighting with a soft desk lamp, creating a slightly tense but realistic mood.
Style: premium office lifestyle photography, authentic desk details.

No generated text, no logo, no watermark, no fake charts, no chaotic desk clutter.
```

## Ads — Solution

```text
Create a photorealistic square Facebook ad image showing a Vietnamese digital marketer easily solving {problem} using a modern web tool.

The marketer is calm, smiling with relief, working on a clean laptop at a bright, minimalist workspace. The desktop screen displays a simple, clean interface with a large, successful "check" graphic or progress ring, with no letters. The workspace is tidy and organized.

Composition: marketer and action on the left or center, clean negative space on the upper-right for later text overlay.
Lighting: bright natural daylight, clean blue and white accents, optimistic and modern.
Style: polished commercial lifestyle photography, realistic desk context.

No generated text, no logo, no watermark, no fake credentials, no messy interface.
```

## Ads — Social proof / trust

Chỉ thể hiện niềm tin bằng quy trình thật hoặc cam kết có trong brand context. Không tạo sao đánh giá, số khách hàng hoặc lời chứng thực giả.

```text
Create a photorealistic square Facebook ad image centered on trust and security for a local digital marketing tool in Vietnam.

SCENE: {trust_scene}
Show a professional Vietnamese marketer working at a bright cafe table, looking relaxed and confident. They might be working on a laptop with an offline network status indicator clearly visible, showing that their strategic keywords are processed locally and securely without server transmission.

Composition: person working as the focal point, clean negative space on one side for later text overlay, balanced 1:1 framing.
Mood: secure, private, trustworthy, modern, professional.
Lighting: warm natural daylight, clean neutral palette with subtle blue accents.
Style: authentic premium lifestyle photography, candid rather than staged.

No generated text, no logo, no watermark, no star rating, no customer count, no fake testimonial.
```

## Prompt assembly checklist

Trước khi gửi prompt cho `gen_image.py`, kiểm tra:

- Chủ đề và hành động có cụ thể không?
- Bối cảnh có phù hợp văn phòng hay góc làm việc hiện đại không?
- Có mô tả marketer thảnh thơi, yên tâm và bảo mật không?
- Ads có negative space cho overlay không?
- Có vô tính yêu cầu chữ, logo, review, giá hoặc chứng chỉ giả không?
- Ảnh có thể đứng độc lập với caption tương ứng không?

## Negative constraints chung

```text
no text, no typography, no logo, no watermark, no QR code, no phone number,
no fake certificate, no fake review, no star rating, no customer-count claim,
no gibberish characters, no messy interface, no cluttered workspace,
no distorted hands, no extra fingers, no unrealistic lighting
```
