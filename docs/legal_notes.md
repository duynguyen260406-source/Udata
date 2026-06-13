# Ghi chú pháp lý — nguồn dữ liệu (thông tin để cân nhắc)

> ⚠️ **KHÔNG phải tư vấn pháp lý.** Đây là tổng hợp thông tin công khai (robots.txt + 1 trang ToS/footer mỗi
> nguồn) để **bạn tự đánh giá** và quyết định điểm nào cần hỏi luật sư. Mọi nhận định trình bày dạng
> "thông tin để cân nhắc", không phải kết luận.
>
> Ngày khảo sát: **2026-06-13**. Mỗi domain chỉ được gọi tối thiểu (robots.txt + 1 trang ToS), không crawl.
> Bảng tóm tắt 4 cột ở [`source_matrix.md`](source_matrix.md) (mục "Tuân thủ & rủi ro pháp lý").

## Khuyến nghị mặc định

- **Nguồn 🟡 Vàng:** chỉ lưu **metadata + URL + đoạn trích ngắn (≤500 ký tự)** vào DB truy vấn.
  KHÔNG lưu full-text vào DB; raw payload (HTML/JSON/PDF) chỉ giữ **nội bộ**, có TTL, không tái phân phối.
- **Nguồn 🟢 Xanh:** áp dụng cùng chính sách snippet+URL cho an toàn, dù rào cản thấp.
- **Nguồn 🔴 Đỏ (mục đích thương mại):** dừng lại, chuyển sang kênh có giấy phép (vd Vietstock DataFeed)
  hoặc xin phép bằng văn bản, trước khi dùng cho sản phẩm thương mại.
- **Xuyên suốt:** User-Agent có email liên hệ, rate-limit thận trọng, tôn trọng robots.txt, **không** bypass TLS,
  **không** giải CAPTCHA / giả mạo fingerprint.

---

## VNDirect finfo-api — 🟡 Vàng

- **Lý do:** robots.txt 404 (không cấm), và API `api-finfo` **không có ToS riêng** → không có cấm crawl tường minh.
  Nhưng ToS website có © "Công ty CP Chứng khoán VNDirect", và dữ liệu là nội dung tổng hợp (aggregated) → tái
  phát hành nguyên văn có rủi ro bản quyền. API không chính thức nên còn rủi ro **bị chặn/đổi bất ngờ**, không phải pháp lý thuần.
- **Điểm cần hỏi chuyên môn:** (1) API không tài liệu có ngầm chịu ToS chung của website/ứng dụng VNDirect không?
  (2) PDF công bố thông tin (đính kèm) vốn là tài liệu công khai theo luật của doanh nghiệp/sàn — bản quyền thuộc ai,
  VNDirect chỉ trung chuyển hay có quyền? (3) Lưu excerpt ≤500 ký tự có nằm trong "trích dẫn hợp lý" không.

## VnEconomy — 🟡 Vàng

- **Lý do:** robots.txt mở (`Allow: /`) nên crawl RSS/bài ở mức rủi ro kỹ thuật thấp. Rủi ro nằm ở bản quyền:
  footer yêu cầu **"đăng lại phải có chấp thuận bằng văn bản"** — mạnh hơn chỉ "dẫn nguồn". Là tạp chí điện tử
  (Hội KH Kinh tế VN, giấy phép 272/GP-BTTTT).
- **Điểm cần hỏi chuyên môn:** (1) "Đăng lại/republish" có bao gồm lưu tóm tắt ngắn + link để phân tích nội bộ,
  hay chỉ khi xuất bản công khai? (2) Ranh giới "trích dẫn hợp lý" (Điều 25 Luật SHTT) cho excerpt ≤500 ký tự.
  (3) Nếu sau này cấp dữ liệu (kể cả excerpt) cho bên thứ ba thương mại thì có cần thỏa thuận cấp phép không.

## Tin nhanh chứng khoán — 🟡 Vàng

- **Lý do:** robots cho phép RSS & trang bài (chỉ chặn `/api/`, `/search/`, `/tag.html`, `/print.html`). Footer:
  **"Ghi rõ nguồn 'Báo Đầu tư Chứng khoán' khi phát hành lại"**; © Báo Tài chính - Đầu tư (cơ quan **Bộ Tài chính**)
  → cơ quan báo chí nhà nước, độ nhạy & khả năng thực thi cao hơn báo tư nhân.
- **Điểm cần hỏi chuyên môn:** (1) Lưu title + excerpt ≤500 ký tự + URL nội bộ có cấu thành "phát hành lại"
  (kèm nghĩa vụ ghi nguồn) không? (2) Quyền trích dẫn hợp lý cho mục đích nghiên cứu vs thương mại.
  (3) Nội dung của cơ quan nhà nước có chế độ bản quyền khác báo tư nhân không.

## Vietstock — 🟡 → 🔴 (Đỏ nếu thương mại)

- **Lý do:** robots cho phép RSS & bài, nhưng trang "Quy định" **cấm "tái bản / sao chụp / mua bán / lợi dụng vì
  mục đích thương mại"** và Vietstock **giữ toàn bộ bản quyền**. Quan trọng: Vietstock **bán dữ liệu qua gói DataFeed
  thương mại** → tự thu thập rồi dùng/phát hành lại có thể bị xem là vi phạm ToS + cạnh tranh trực tiếp với sản phẩm trả phí.
  Có điều khoản chung cấm gây "tổn hại hệ thống/băng thông" — dễ bị viện dẫn nếu tự động hóa gây tải nặng.
- **Điểm cần hỏi chuyên môn:** (1) Lưu title + excerpt ≤500 ký tự + link (không full-text) cho mục đích thương mại
  có thuộc "tái bản/sao chụp vì mục đích thương mại" bị cấm, hay là trích dẫn hợp lý? (2) Sự tồn tại của DataFeed có
  nâng mức rủi ro (vi phạm ToS + cạnh tranh không lành mạnh) khi tự thu thập dù robots cho phép không?
- **Khuyến nghị:** nếu dùng thương mại/diện rộng → liên hệ mua **DataFeed**. Nếu chỉ nghiên cứu nội bộ → tốc độ thấp, excerpt+URL.

## Báo Đầu tư — 🟡 Vàng (khắt khe)

- **Lý do:** robots.txt mở (`Allow: /`) nhưng footer áp đặt **"mọi việc sử dụng nội dung phải có đồng ý bằng văn bản"**
  — tín hiệu pháp lý mạnh nhất trong nhóm báo chí. © Báo Tài chính - Đầu tư (cơ quan **Bộ Tài chính**, giấy phép 1/GP-BC).
- **Điểm cần hỏi chuyên môn:** (1) Lưu title + excerpt ≤500 ký tự + URL nội bộ (không phát hành) có rơi vào "sử dụng
  nội dung cần xin phép bằng văn bản", hay được miễn theo quyền trích dẫn hợp lý (Điều 25 Luật SHTT)? (2) Lưu raw HTML
  đầy đủ (TTL 90 ngày, nội bộ, để re-parse) có vi phạm không? (3) Có nên chủ động xin văn bản đồng ý của tòa soạn không.

## CBTT — HOSE (hsx.vn) — 🟢 Xanh

- **Lý do:** robots.txt mở hoàn toàn (`Disallow:` rỗng). CBTT là **thông tin công bố bắt buộc theo Luật Chứng khoán 2019
  + Thông tư 96/2020/TT-BTC** → bản chất công khai. Chưa xác minh được trang ToS/footer (site Angular JS-heavy).
- **Điểm cần hỏi chuyên môn:** (1) Tự xác minh footer/trang "Điều khoản" của hsx.vn trên trình duyệt thật.
  (2) Phân biệt bản quyền **nội dung CBTT** (công khai theo luật) vs **layout/biên tập của website** sở.

## CBTT — HNX (hnx.vn) — 🟡 Vàng

- **Lý do:** robots.txt 404 (không công bố) **và** lỗi chuỗi chứng chỉ TLS (server thiếu intermediate cert). Trang
  "Khuyến cáo" yêu cầu **liên hệ HNX trước khi đăng/phát lại thông tin** — rào cản tái phân phối rõ nhất trong nhóm CBTT.
  © Sở GDCK Hà Nội. Hiện đang lấy **gián tiếp qua VNDirect** (PDF gốc `owa.hnx.vn`).
- **Điểm cần hỏi chuyên môn:** (1) Yêu cầu "liên hệ trước khi đăng/phát" có áp dụng cho lưu excerpt + link nội bộ
  (không tái phân phối công khai) không? (2) Bỏ qua/chấp nhận lỗi TLS để truy cập có rủi ro pháp lý/an ninh nào,
  và có kênh hợp lệ thay thế (broker/API) không — **chưa** bypass TLS cho tới khi rõ.

## CBTT — VSDC (congbothongtin.ssc.gov.vn) — 🟢 Xanh

- **Lý do:** Cổng của UBCKNN/SSC; dữ liệu nhà nước, **công bố bắt buộc theo luật** (Luật Chứng khoán 2019 + TT 96/2020).
  Quy chế hiện hành (QĐ 820/QĐ-UBCK, 2025) ràng buộc **bên NỘP báo cáo** (tài khoản + chữ ký số), **không** ràng buộc
  bên đọc/khai thác dữ liệu đã công khai. Không tìm thấy điều khoản cấm sao chép/tái sử dụng. © UBCKNN.
- **Điểm cần hỏi chuyên môn:** (1) Bản chất "công bố bắt buộc theo luật" có vô hiệu hóa hạn chế bản quyền/ToS đối với
  chính nội dung CBTT không? (2) Có ràng buộc nào với việc tái phân phối dữ liệu công khai cho bên thứ ba thương mại không.

---

## Lưu ý chung cần đối chiếu với chuyên môn

1. **Quyền trích dẫn hợp lý** (Điều 25 Luật SHTT VN) là trục pháp lý lặp lại ở hầu hết nguồn — ranh giới giữa
   "trích dẫn hợp lý" và "đăng lại cần xin phép" cho excerpt ≤500 ký tự cần ý kiến luật sư, đặc biệt nếu **thương mại hóa**.
2. **Nội dung cơ quan nhà nước** (Tin nhanh CK & Báo Đầu tư thuộc Bộ Tài chính; CBTT thuộc UBCKNN/sở) có thể có chế độ
   bản quyền/được phép sử dụng khác báo tư nhân — cần xác nhận.
3. **Dữ liệu CBTT công bố theo luật** (HOSE/HNX/VSDC) nên tách bạch: bản quyền *nội dung công bố* (công khai) vs *giao diện/biên tập* của cổng.
4. **API không chính thức** (VNDirect, api.hsx.vn): rủi ro chính là kỹ thuật (đổi/chặn) cộng thêm ToS không rõ — luôn coi là *dễ vỡ*.
5. **Nghị định 13/2023/NĐ-CP (dữ liệu cá nhân):** các nguồn hiện tại là tin tức/CBTT, **không** phải forum/social, nên
   ít chạm dữ liệu cá nhân. Chỉ phát sinh nếu sau này thêm nguồn social (đã hoãn sang v2) hoặc lưu trường tác giả/bình luận
   — khi đó chỉ giữ tối thiểu cho mục đích dẫn nguồn, không tổng hợp PII.
