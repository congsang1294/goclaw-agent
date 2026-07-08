---
name: tao-creative-fb-gpt
description: Tạo full content cho Facebook business page, trong đó MỖI output bắt buộc gồm CẢ ẢNH VÀ VĂN BẢN đi cùng nhau. Dùng cho Mode 1 Content Free/Organic khi người dùng nói "tạo content cho ngày mai", "gen bài Page", "content free", "content organic" hoặc muốn tạo bài đăng Page hằng ngày; quy trình gồm đề xuất 3 ý tưởng, chờ chọn, tạo ảnh GPT Image và caption, chờ duyệt rồi mới đăng cả ảnh lẫn caption lên Facebook Page. Dùng cho Mode 2 Creative Ads khi người dùng nói "tạo creative ads", "gen ads", "cần creative cho chiến dịch" hoặc muốn tạo quảng cáo Facebook; tạo 3 bộ ghép đôi ảnh ads + ad copy theo ba angle pain point, solution và social proof, chỉ bàn giao để dùng trong Ads Manager và không tự đăng.
---

# Tạo Creative Facebook

Tạo nội dung cho Facebook Page dựa trên brand context. Luôn coi một sản phẩm hoàn chỉnh là một cặp không tách rời:

- Bài organic hoàn chỉnh = 1 ảnh + 1 caption.
- Creative ads hoàn chỉnh = 1 ảnh ads + 1 ad copy.

Không trả về chỉ ảnh hoặc chỉ văn bản. Không đánh tráo copy giữa các ảnh.

## Nạp brand context

Trước khi viết ý tưởng, prompt ảnh hoặc copy:

1. Đọc bảng `brand_voice` từ đường dẫn `BRAIN_DB_PATH`; nếu chưa cấu hình, để script tự tìm trong cấu trúc local hoặc GoClaw/VPS.
2. Đọc `SOUL.md`, `USER.md`, `AGENTS.md`, `HEARTBEAT.md` từ `CONTEXT_DIR`; nếu chưa cấu hình, để script tự tìm trong cấu trúc local hoặc GoClaw/VPS.
3. Dùng `assets/image-prompt-templates.md` cho định hướng hình ảnh.
4. Dùng `assets/caption-templates.md` cho cấu trúc caption và ad copy.

Ưu tiên dữ liệu brand cụ thể hơn hướng dẫn chung. Giữ giọng gần gũi, thẳng thắn, dùng câu ngắn, nói thật, viết từ trải nghiệm cá nhân/công việc thực tế. Không dùng từ corporate hay thuật ngữ dông dài.

Không tự đặt giá cố định khi chưa có dữ liệu được xác nhận. Có thể dùng các thông tin đã có trong brand context như bản free được Copy All tối đa 3 lần, bản Pro trọn đời giá 15.000đ mở khóa không giới hạn lượt copy.

## Chọn mode

- Chọn **Mode 1 — Content Free** khi yêu cầu nói về bài Page hằng ngày, content free hoặc organic.
- Chọn **Mode 2 — Creative Ads** khi yêu cầu nói về creative quảng cáo hoặc chiến dịch ads.
- Nếu yêu cầu chưa rõ mode, hỏi một câu ngắn trước khi tạo.

## Chạy trên GoClaw

Agent GoClaw bị giới hạn trong workspace. Không chạy scripts từ `/app/skills` hoặc `/app/data/skills-store`; các đường dẫn đó sẽ bị `access denied: path outside workspace`.

Luôn dùng tool `exec` với **đường dẫn tuyệt đối**:

```text
cd /app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt
```

- Đọc credentials từ environment variables đã inject vào agent. `.env` chỉ là fallback.
- Lưu mọi artifact vào `output/`.
- Khi cần gửi preview ảnh cho user trên GoClaw, dùng đường dẫn media:
  `MEDIA:/app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt/output/<file>.png`
- Không chạy `post_facebook.py` trong Mode 2.
- Trong Mode 1, chỉ chạy `post_facebook.py` sau khi user duyệt rõ ràng.
- Giữ trạng thái ý tưởng, lựa chọn và content chờ duyệt trong file JSON dưới `output/` để dùng được qua nhiều tin nhắn.

Sau khi upload/cập nhật skill, chạy một lần bằng root trên VPS host:

```text
sh /var/lib/docker/volumes/goclaw_goclaw-workspace/_data/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt/scripts/setup_goclaw.sh
```

Không chạy lệnh này bằng `docker exec`: root trong container có thể không được phép đổi mode của Docker volume.
Lệnh đặt `.env` thành `640 root:1000`, `output/` thành `775 1000:1000`.
Bản public trong `/app/data/skills-store` không được chứa `.env`.
Nếu chưa chạy setup, scripts vẫn phải bỏ qua dotenv không đọc được và ưu tiên environment variables đã inject vào agent.

## Mode 1 — Content Free

### Bước A: Đề xuất ý tưởng

Chạy đúng một lệnh:

```text
cd /app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt &&
python3 scripts/gen_caption.py --task ideas --topic "<topic>"
```

Đọc file JSON được trả về và trình bày đúng 3 ý tưởng khác nhau. Mỗi ý tưởng gồm:

- Số thứ tự.
- Tiêu đề.
- Angle ngắn.

Chỉ trình bày 3 ý tưởng ở bước này. Chờ người dùng chọn một ý.

**TUYỆT ĐỐI KHÔNG** gọi `gen_image.py`, không viết caption và không tạo file content bằng `write_file` ở Bước A.
Nếu `exec` lỗi, báo đúng lỗi; không fallback sang tự viết nội dung.

### Bước B1: Tạo caption

**TRIGGER DUY NHẤT của Bước B1:** user vừa chọn ý tưởng từ danh sách (nói "ý 1", "ý 2", "ý 3", hoặc tên ý).

Chạy ĐÚNG MỘT lệnh:

```text
cd /app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt &&
python3 scripts/gen_caption.py --task organic --topic "<ý đã chọn>" --angle trust
```

Sau khi exec xong, in RA ĐÚNG GIÁ TRỊ của field `data.caption` từ JSON output — không thêm nhãn, không mô tả từng field, không tóm tắt:

```
📋 Caption đề xuất:

<in nguyên văn data.caption>
```

Hỏi ngay: "Caption ok không hay cần chỉnh gì?"

⛔ **RESPONSE KẾT THÚC Ở ĐÂY. KHÔNG EXEC THÊM LỆNH NÀO SAU KHI IN CAPTION. KHÔNG GỌI gen_image.py. KHÔNG GEN ẢNH. KHÔNG ĐỀ CẬP ẢNH HAY BƯỚC TIẾP THEO.**

Nếu user "sửa..." → chạy lại gen_caption với topic điều chỉnh (chỉ B1, không B2).
Nếu user "ok/duyệt" → đây là trigger của Bước B2 bên dưới.

### Bước B2: Tạo ảnh và gửi Telegram preview

**TRIGGER DUY NHẤT của Bước B2:** user vừa reply "ok" / "duyệt" / "ok tạo ảnh" / "ok đăng" vào câu hỏi caption ở Bước B1.

**KHÔNG bao giờ chạy B2 cùng turn với B1. KHÔNG chạy B2 khi user chọn ý.**

Đọc field `data.image_prompt` từ JSON Bước B1. Chạy:

```text
cd /app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt &&
python3 scripts/gen_image.py --mode organic --prompt "<data.image_prompt>" --output "output/organic-image.png"
```

`gen_image.py` tự gửi ảnh về Telegram. Báo ngắn: "Ảnh đã gửi về Telegram. Duyệt để đăng hoặc nhắn 'tạo lại ảnh'."

- Nếu user "tạo lại" → chạy lại gen_image.py cùng prompt.
- Nếu user "ok" / "duyệt" / "đăng đi" → sang Bước D.

`gen_image.py` chỉ nhận `--prompt`, `--mode`, `--output`. Không có `--topic`.

### Bước D: Đăng Page

**TRIGGER:** user duyệt ảnh ("ok đăng đi", "đăng đi", "đăng").

Chạy:

```text
cd /app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt &&
python3 scripts/post_facebook.py \
  --image output/organic-image.png \
  --caption-file output/<caption-json-từ-B1> \
  --confirm-post
```

**Bắt buộc `--confirm-post`** — script từ chối đăng nếu thiếu.

Sau khi đăng thành công, đọc field `data.post_url` từ JSON output và báo:

```
✅ Đã đăng lên Facebook!
🔗 <data.post_url>
```

- Nếu `DRY_RUN=true` → không gọi Facebook, chỉ lưu preview local.
- Nếu Facebook lỗi → báo HTTP status + error code + message. Không báo thành công giả.

## Mode 2 — Creative Ads

Tạo đúng 3 bộ creative, mỗi bộ là một cặp ảnh + ad copy:

1. **Pain point** — làm rõ nỗi lo hoặc tình huống khách đang gặp.
2. **Solution** — làm rõ cách brand giải quyết vấn đề.
3. **Social proof** — xây dựng niềm tin bằng bằng chứng hoặc cam kết có thật trong brand context.

Với từng bộ (lặp 3 lần cho `pain_point`, `solution`, `social_proof`):

1. Tạo ad copy + image_prompt:

```text
cd /app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt &&
python3 scripts/gen_caption.py --task ads --topic "<topic>" --angle <pain_point|solution|social_proof> --output output/<stem>-copy.json
```

2. Đọc `data.image_prompt` từ JSON đầu ra.
3. Tạo ảnh ads:

```text
cd /app/workspace/quan-ly-mang-xa-hoi/my-skills/tao-creative-fb-gpt &&
python3 scripts/gen_image.py --mode ads --prompt "<data.image_prompt>" --output "output/<stem>.png"
```

4. Chừa khoảng trống hợp lý cho text overlay nếu concept cần, nhưng không phụ thuộc vào chữ do model vẽ chính xác.
5. Dùng hook mạnh, USP nổi bật và CTA rõ ràng.
6. Gắn nhãn angle và trình bày ảnh ngay cùng copy tương ứng.

Không gọi `scripts/post_facebook.py` trong Mode 2. Không tự đăng Page hoặc tạo chiến dịch. Chỉ trả đủ 3 bộ để người dùng đưa vào Ads Manager.

## Bố cục caption

Caption phải theo đúng cấu trúc sau (không có prefix "Tiêu đề:" hay "Nội dung:" trong nội dung đăng thật):

```
[Tiêu đề ngắn gợi tò mò]

[emoji] [Hook 1–2 câu, tình huống đời thường]

✅ [Benefit 1 — cam kết có thật]
✅ [Benefit 2]
✅ [Benefit 3 nếu đủ nội dung]

👉 [CTA ngắn, có số điện thoại]

#GoogleAdsMatchTypeConverter #GoogleAds #từkhóa
```

## Quy tắc hình ảnh

- Dùng bối cảnh văn phòng làm việc hiện đại, góc làm việc (home office) tối giản, sáng sủa và năng động.
- Thể hiện hình ảnh một digital marketer, chủ shop online, hoặc freelancer người Việt đang làm việc thảnh thơi, thoải mái bên laptop/máy tính, thể hiện cảm giác tiết kiệm thời gian và an tâm bảo mật.
- Không dùng logo, giao diện chứa chữ bị lỗi, hoặc đánh giá giả nếu không có asset/dữ liệu thật.
- Hạn chế yêu cầu model render nhiều chữ tiếng Việt hay các kí tự lạ trong ảnh.
- Không dùng hình ảnh quá phức tạp, cồng kềnh.

## Xử lý lỗi

- Khi OpenAI lỗi, log lỗi và retry đúng 1 lần đối với lỗi tạm thời.
- Không retry mù với lỗi xác thực, prompt bị chặn hoặc request không hợp lệ.
- Khi hết retry, giữ các output đã tạo thành công và báo rõ phần nào thất bại.
- Không trình bày một bộ creative là hoàn chỉnh nếu thiếu ảnh hoặc thiếu copy.

## Bảo mật

- Đọc secret từ `.env`; không hard-code API key hoặc Page token.
- Trên GoClaw/VPS, ưu tiên biến môi trường container hoặc `/opt/goclaw/.env`.
- Không in toàn bộ token ra log hoặc preview.
- Giữ `.env` ngoài version control.
- Chỉ để placeholder trong `scripts/env.example`.

## Kiểm tra đầu ra

Trước khi bàn giao, xác nhận:

- Mode 1 có đúng 1 ảnh và 1 caption sau khi chọn ý tưởng.
- Mode 2 có đúng 3 ảnh và 3 ad copy, ghép thành đúng 3 bộ.
- Mỗi caption/copy khoảng 80–150 từ và đúng brand voice.
- Organic dùng soft CTA; ads dùng CTA rõ.
- Mode 1 chưa đăng nếu chưa được duyệt.
- Mode 2 không bao giờ tự đăng.
