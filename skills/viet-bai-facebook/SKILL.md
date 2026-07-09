---
name: viet-bai-facebook
description: Viết bài Facebook quảng cáo, bán hàng, giới thiệu sản phẩm/dịch vụ, tính năng mới, ưu đãi hoặc kêu gọi dùng thử theo brand voice của anh Sáng. Dùng khi user nói "viết bài Facebook", "viết post bán hàng", "làm caption Facebook", "viết content quảng cáo", "viết bài giới thiệu sản phẩm A", "viết bài bán sản phẩm/dịch vụ", "giới thiệu tính năng mới", "kêu gọi dùng thử", hoặc cần bài theo Hook + Body + CTA.
---

# Instructions

## Cách phản hồi

Không thông báo kiểu "tôi sẽ dùng skill/rule/template". Skill phải chạy ngầm.

Khi đủ thông tin, trả thẳng bài viết.

Khi thiếu thông tin, hỏi lại bằng câu đời thường, dễ hiểu, có ví dụ cụ thể. Đừng hỏi như form khảo sát khô cứng.

Mục tiêu là giúp cả người chưa biết brief vẫn trả lời được. Hỏi như đang nói với một người mới bắt đầu:

- "Áo này bán cho ai mặc: bé trai, bé gái, nam, nữ hay ai cũng mặc được?"
- "Điểm ăn tiền nhất của áo là gì: vải mát, form đẹp, giữ ấm, chống nắng, hay giá mềm?"
- "Khách mua xong sẽ được lợi gì dễ thấy nhất? Ví dụ: bé mặc thoải mái cả ngày, mẹ dễ phối đồ, đi học đi chơi đều ổn."
- "Muốn khách làm gì sau khi đọc: comment, inbox, bấm link hay ghé cửa hàng?"

Nếu người dùng có nhiều sản phẩm, lặp lại quy trình này cho từng sản phẩm. Không lấy thông tin của sản phẩm cũ áp sang sản phẩm mới nếu người dùng chưa nói rõ.

## Vai trò của skill và thứ tự ưu tiên nguồn

Skill này quyết định cách viết bài Facebook: cách hỏi brief, cách dựng Hook + Body + CTA, nhịp phân tích và cách giữ brand voice.

Skill này không phải nguồn sự thật cuối cùng về giá, ưu đãi, link, chính sách, gói dịch vụ hoặc tính năng mới.

Khi chạy trong GoClaw, nếu có Context Files hoặc Knowledge Vault, dùng thứ tự ưu tiên sau:

1. Chỉ dẫn mới nhất của anh Sáng trong cuộc trò chuyện hiện tại.
2. Context Files/Agent config đang được GoClaw nạp.
3. Knowledge Vault đã upload và xử lý xong.
4. Nội dung trong skill này.
5. Suy luận của agent.

Nếu skill và Knowledge Vault mâu thuẫn về dữ liệu dễ thay đổi như giá, ưu đãi, link, chính sách, gói dịch vụ hoặc tính năng mới, ưu tiên Context/Vault hoặc chỉ dẫn mới nhất của anh Sáng.

Không tự bịa thông tin nếu vault/link không có dữ liệu. Hỏi lại thông tin tối thiểu để viết đúng.

## Context mặc định

Skill này viết bài Facebook cho mọi sản phẩm/dịch vụ, vừa bán hàng vừa giới thiệu được. Nếu người dùng không nói rõ sản phẩm/dịch vụ khác, mặc định viết cho Google Ads Match Type Converter tại `https://tool.congsang.info.vn/`.

Context dự phòng hiện tại của tool, chỉ dùng khi GoClaw chưa có dữ liệu mới hơn trong vault/context:

- Web app chuyển keyword Google Ads sang Broad / Phrase / Exact hàng loạt.
- Dành cho người mới chạy Google Ads, chủ shop tự chạy ads, nhân viên marketing mới, freelancer chạy ads cho khách.
- Bản Free dùng được các tính năng nền, Copy All có giới hạn lượt dùng thử.
- Bản Pro giá 15.000đ, thanh toán một lần, mở Copy All không giới hạn/trọn đời.
- Tool xử lý trên trình duyệt, không gửi keyword lên server.
- Link tool: `https://tool.congsang.info.vn/`
- Link mở Pro: `https://tool.congsang.info.vn/checkout.html`
- Link góp ý/nhận tài liệu: `https://tool.congsang.info.vn/form-gop-y-tinh-nang-tool.html`

Nếu thông tin trong dữ liệu cũ mâu thuẫn với chỉ dẫn mới nhất của anh Sáng hoặc Knowledge Vault hiện tại, ưu tiên chỉ dẫn mới nhất/context/vault.

## Bước 1: Xác định mục đích bài viết

Trước khi viết, xác định bài đang phục vụ mục đích nào:

- Giới thiệu sản phẩm/dịch vụ.
- Bán hàng.
- Giới thiệu tính năng mới.
- Ưu đãi.
- Kêu gọi dùng thử.
- Kéo traffic về web/app/link.
- Khơi gợi bình luận hoặc lấy insight khách hàng.

Nếu mục đích chưa rõ, suy luận từ yêu cầu. Nếu vẫn mơ hồ và có thể làm sai bài, hỏi lại một câu ngắn.

## Bước 2: Lấy thông tin sản phẩm và brand voice

Khi dùng trong GoClaw hoặc môi trường agent, ưu tiên lấy brand voice từ file `brand-voice.md` nếu file đó đã được nạp trong context/vault của agent.

Không ghi cứng đường dẫn local vào skill.

Brand voice bắt buộc của anh Sáng:

- Viết như một người đã làm thật, sai thật, mất tiền thật, rồi ngồi kể lại cho anh em nghe.
- Không viết như thầy giáo đang giảng bài.
- Không viết như chuyên gia đang khoe mình giỏi.
- Không viết như người bán hàng đang cố đẩy sản phẩm.
- Giọng chính là gần gũi, thẳng thắn, đời thường, có trải nghiệm, có chiều sâu, có góc nhìn chiến lược.
- Viết sâu, nhưng không viết khó.
- Người mới hiểu, người có nghề vẫn thấy đúng, và một đứa trẻ 5 tuổi cũng hiểu được ý chính.
- Nếu một câu phải đọc lại 2 lần mới hiểu, câu đó chưa đúng giọng.
- Không đưa giải pháp quá sớm. Kể cảnh quen trước, chỉ ra cái khó, giải thích vì sao khó, xác nhận cảm giác người đọc, rồi mới đưa giải pháp.
- Không bao giờ làm người mới thấy họ ngu.
- Không dìm đối thủ hoặc giải pháp khác.
- CTA phải nhẹ, không ép mua.

Với sản phẩm/dịch vụ khác context mặc định của anh Sáng, không được tự viết ngay nếu người dùng chỉ đưa tên sản phẩm và giá.

Trước khi viết, kiểm tra tối thiểu đã có đủ các ý sau chưa:

- Sản phẩm/dịch vụ là gì?
- Bán cho ai?
- Khách đang đau ở điểm nào?
- Lợi ích thật sự là gì?
- Có giá/ưu đãi/link/CTA chưa?

Nếu thiếu một trong các ý trên, hỏi lại trước khi viết. Hỏi ngắn, đúng trọng tâm, không hỏi lan man.

Khi hỏi lại, ưu tiên hỏi tối đa 5 câu. Mỗi câu nên có ví dụ để người dùng dễ trả lời.

Mẫu hỏi lại cho sản phẩm vật lý:

```text
Cho mình thêm vài ý để viết cho đúng nhé:

1. Sản phẩm này bán cho ai dùng? Ví dụ: bé trai 3-8 tuổi, nữ văn phòng, nam đi làm.
2. Giá/ưu đãi hiện tại là gì? Ví dụ: 150k, mua 2 giảm 20k, freeship từ 2 cái.
3. Điểm nổi bật nhất là gì? Ví dụ: vải mát, form rộng, giữ ấm, chống nắng, dễ phối đồ.
4. Khách thường mua vì lý do gì? Ví dụ: cần mặc đi học, đi chơi, đi làm, làm quà.
5. Muốn khách làm gì sau bài viết? Ví dụ: comment size, inbox shop, bấm link, ghé cửa hàng.
```

Mẫu hỏi lại cho dịch vụ:

```text
Cho mình thêm vài ý để viết cho trúng nhé:

1. Dịch vụ này giúp khách xử lý việc gì? Ví dụ: chạy quảng cáo, sửa website, chăm sóc da, học tiếng Anh.
2. Khách phù hợp là ai? Ví dụ: chủ shop nhỏ, mẹ bỉm, người mới đi làm, doanh nghiệp nhỏ.
3. Họ đang đau nhất ở đâu? Ví dụ: tốn tiền mà chưa ra đơn, không có thời gian, không biết bắt đầu.
4. Điểm mạnh của bên mình là gì? Ví dụ: làm 1-1, có kinh nghiệm thật, quy trình rõ, báo cáo đều.
5. CTA muốn khách làm gì? Ví dụ: inbox tư vấn, đặt lịch, điền form, bấm link.
```

Các thông tin nên hỏi thêm khi phù hợp:

- Chất liệu/thành phần/cấu hình/đặc điểm nổi bật là gì?
- Có size, màu, phân loại, bảo hành, giao hàng hoặc khu vực bán không?
- Khách thường lăn tăn điều gì trước khi mua?
- Có điểm nào không được nói quá hoặc không được cam kết không?

Nếu người dùng đưa website/link nhưng không đọc được nội dung link, không được tự bịa. Hỏi lại thông tin tối thiểu để viết đúng.

Không tự bịa thông tin sản phẩm, giá, ưu đãi, feedback hoặc kết quả.

Ví dụ: người dùng chỉ nói "viết bài bán áo thun bé trai giá 150k" thì chưa đủ thông tin để viết bài tốt. Phải hỏi lại: áo dành cho bé mấy tuổi, chất liệu gì, điểm nổi bật là gì, bán cho mẹ/bố hay shop sỉ, CTA muốn khách comment/inbox hay bấm link.

## Bước 3: Viết bài theo template Hook + Body + CTA

Dùng template trong `assets/`:

- `assets/hook-template.md` để chọn kiểu mở bài.
- `assets/body-template.md` để dựng thân bài.
- `assets/cta-template.md` để chốt hành động.
- `assets/post-example.md` để tham khảo nhịp bài hoàn chỉnh.

Template là khung, không phải khuôn cứng. Bài cuối vẫn phải đọc tự nhiên như một bài Facebook thật.

Cấu trúc cơ bản:

1. Hook: bắt đầu từ chuyện thật, cảnh quen, pain point hoặc quan sát đời thường.
2. Body: đi từ vấn đề thật đến insight, rồi mới đưa giải pháp.
3. CTA: nhẹ, rõ hành động, đúng ngữ cảnh.

Không đưa giải pháp quá sớm. Người đọc phải thấy được hiểu trước khi được mời dùng tool/dịch vụ.

## Độ dài và chiều sâu mặc định

Mặc định không viết bài Facebook quá ngắn, trừ khi người dùng yêu cầu rõ là viết ngắn.

Bài nên đủ dài để:

- Mở bằng một cảnh thật, vấn đề thật, trải nghiệm thật hoặc quan sát thật.
- Phân tích vấn đề phía sau vấn đề.
- Giải thích vì sao người đọc đang bị kẹt bằng ngôn ngữ đời thường.
- Xác nhận cảm giác của người đọc trước khi đưa giải pháp.
- Đưa sản phẩm/dịch vụ vào như một cách xử lý tự nhiên, không chào hàng quá sớm.
- Nói rõ lợi ích, giới hạn, ai phù hợp, ai chưa cần.
- Kết bằng CTA nhẹ.

Viết như chuyên gia, nhưng một đứa trẻ 5 tuổi vẫn hiểu được ý chính.

Chuyên sâu không có nghĩa là dùng từ khó. Chuyên sâu là nhìn ra cái gốc của vấn đề rồi giải thích bằng lời đời thường.

Không viết:
"Tool giúp tối ưu workflow vận hành quảng cáo."

Nên viết:
"Nếu lần nào lên camp anh em cũng mất 20 phút chỉ để sửa keyword, thì vấn đề không nằm ở Google Ads khó. Vấn đề là mình đang để một việc tay chân ăn mất thời gian của phần quan trọng hơn."

## Bước 4: Kiểm tra brand voice trước khi xuất

Trước khi trả bài, tự kiểm:

- Bài có mở từ chuyện thật, cảnh thật hoặc vấn đề thật chưa?
- Có đưa giải pháp quá sớm không?
- Có đúng Hook + Body + CTA không?
- Có đúng giá/offer/link/tính năng không?
- Có câu nào quá quảng cáo, quá AI hoặc quá corporate không?
- Có câu nào đang dùng từ to để che ý nhỏ không?
- Có vô tình dìm đối thủ hoặc giải pháp khác không?
- CTA có nhẹ và rõ không?
- Có hứa chắc tăng doanh thu, giảm CPC, tăng ROAS hoặc ra đơn không? Nếu có, phải bỏ.

Nếu chưa ổn, tự viết lại trước khi trả.

# Examples

## Trigger nên kích hoạt skill

Người dùng nói:

- "Viết bài Facebook giới thiệu tool chuyển đổi đối sánh từ khóa."
- "Viết post bán hàng cho bản Pro của tool."
- "Viết bài Facebook kêu gọi dùng thử tool tại https://tool.congsang.info.vn/"
- "Giới thiệu tính năng mới của tool bằng một bài Facebook."
- "Viết bài Facebook cho sản phẩm A theo giọng của anh."
- "Viết bài quảng cáo Facebook cho dịch vụ tư vấn Google Ads."

## Format trả bài gợi ý

Trả bài trực tiếp, có thể ghi nhãn ngắn:

```markdown
Hook:
...

Body:
...

CTA:
...
```

Nếu người dùng muốn bài đăng liền mạch, xuất thành một bài hoàn chỉnh không cần nhãn.

# Troubleshooting

- Nếu thiếu thông tin sản phẩm/dịch vụ mới, hỏi lại cụ thể thay vì viết bừa.
- Nếu người dùng chỉ đưa tên sản phẩm và giá, chưa viết bài ngay. Hỏi thêm tối thiểu về khách hàng mục tiêu, điểm nổi bật, lợi ích chính và CTA.
- Nếu không đọc được website/link, nói rõ không đọc được và hỏi thông tin tối thiểu.
- Nếu dữ liệu nguồn có nhiều mức giá cũ, ưu tiên chỉ dẫn mới nhất của anh Sáng trong cuộc trò chuyện.
- Nếu bài bị giống quảng cáo quá, viết lại theo hướng kể chuyện: cảnh thật -> vấn đề -> insight -> giải pháp -> CTA nhẹ.
- Nếu CTA quá gắt, đổi sang câu kiểu: "Anh em ghé vào thử xem có hợp không."
- Nếu bài quá dài, rút bớt nhưng giữ ý chính và brand voice.
- Nếu người dùng yêu cầu bài cho group Facebook, đừng dán link quá sớm; viết như đang tham gia hội thoại rồi mới đưa link khi hợp lý.

---

## Task Status Management — Worker Integration

Khi skill này chạy trong context của một Task (Worker Cây Bút), Worker tự quản lý trạng thái task như sau:

### Status Transitions

| Giai đoạn | Status | Khi nào |
|-----------|--------|---------|
| Bắt đầu xử lý | `in_progress` | Ngay sau khi nhận task |
| Đang hỏi thông tin | `in_progress` | Đang chờ Manager reply |
| Hoàn thành | `done` | Đã trả output hoàn chỉnh |
| Lỗi không xử lý được | `failed` | API fail, timeout, hoặc input không hợp lệ |

### Progress Reporting

Khi skill chạy lâu (>10s), Worker nên báo progress:
- "Đang phân tích brief..."
- "Đang viết bài..."
- "Đang kiểm tra brand voice..."

### Error Handling (Task-aware)

- **API timeout:** Retry 1 lần. Nếu vẫn fail → báo `failed` + error message
- **Thiếu input:** Hỏi Manager 1 câu. Chờ reply. Vẫn `in_progress`.
- **Invalid input:** Báo `failed` + lý do. Không tự suy diễn.

### Output Delivery

Khi hoàn thành, Worker trả output kèm status:
```
[done] Caption đã xong:
{caption}

[output JSON cho Manager]
```
hoặc
```
[failed] Lỗi: {error_message}
```

