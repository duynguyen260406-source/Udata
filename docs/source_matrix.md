# Bảng đối chiếu nguồn (Source Matrix) — tuần khảo sát

> Mục tiêu: xác định cách **rẻ nhất chạy được** để lấy tin tức/CBTT chứng khoán VN từ các nguồn F0.
> Đây là kết quả **spike khảo sát**, chưa phải code production. Mỗi nguồn đã được gọi lịch sự 1–2 lần
> với User-Agent `udata-survey/0.1 (research bot; contact: duynguyen260406@gmail.com)`.
>
> Ngày khảo sát: **2026-06-13**. Script tương ứng nằm trong `spikes/`, mẫu raw trong `spikes/samples/`.
> Thứ tự thử nghiệm: **RSS → JSON API ẩn → HTML tĩnh (trafilatura) → Playwright**, dừng ở mức rẻ nhất thành công.

## Bảng tổng hợp

| Nguồn | URL / feed lấy được | Phương thức lấy được | Định dạng trả về | Các trường lấy được | Cần JS? | Độ ổn định | Ghi chú |
|---|---|---|---|---|---|---|---|
| **VNDirect finfo-api** | `https://api-finfo.vndirect.com.vn/v4/news?size=5&sort=newsDate:desc` (lọc ticker: `?q=tagCodes:VCB`; chỉ CBTT: `?q=newsGroup:disclosure`) | **JSON API ẩn (httpx)** — rẻ nhất | JSON `{currentPage, data[], size, totalElements, totalPages}` | `newsId, newsTitle, newsAbstract, newsContent (HTML đầy đủ), newsDate, newsTime, newsSource, newsGroup (disclosure/stock_news), newsType, tagCodes (mã CK), newsUrl, dstockUrl, thumbnailUrl, attachments[] (PDF gốc), locale, hotNews` | Không | **Cao về kỹ thuật / Trung bình về pháp lý** | **Mỏ vàng**: tổng **243.950** bản tin, có cả tin báo chí lẫn CBTT. `attachments[].sourceUrl` trỏ thẳng PDF gốc trên `owa.hnx.vn` (HNX/HOSE). API **không chính thức, không ToS** → coi là dễ vỡ, gọi ≤20 req/phút. Host `finfo-api.*` timeout — dùng host `api-finfo.*`. |
| **VnEconomy** | `https://vneconomy.vn/chung-khoan.rss` (và `/tai-chinh.rss`) | **RSS (feedparser)** — rẻ nhất | RSS 2.0 XML | `title, link, published(+parsed), summary, content, tags, media_content, id` (60 mục/feed) | Không | **Cao** | RSS theo chuyên mục, cập nhật liên tục. Không có trường `author` trong feed. `summary` chứa numeric entity (vd `&#249;`) — decode khi parse. Toàn văn cần fetch trang bài + trafilatura. |
| **Tin nhanh chứng khoán** | `https://www.tinnhanhchungkhoan.vn/rss/home.rss` | **RSS (feedparser)** | RSS XML | `title, link, published(+parsed), updated, summary (HTML có <img>), thumb, tags, id` (50 mục) | Không | **Cao** | Feed chuyên mục dạng `/<slug>.rss` trả 404; chỉ `/rss/home.rss` chạy. **KHÔNG** dùng `/api/` (robots.txt chặn). Toàn văn cần fetch trang bài. |
| **Vietstock** | `https://vietstock.vn/144/chung-khoan.rss` | **RSS (feedparser)** | RSS 2.0 XML (`application/rss+xml`) | `title, link, published(+parsed), summary (HTML có <img>+sapo), id` (30 mục) | Không | **Cao** | RSS chính thức theo channel id (144 = Chứng khoán). **Không** đụng API nội bộ (CSRF) hay `/export` (robots chặn). Toàn văn cần fetch trang bài. |
| **Báo Đầu tư** | Trang chuyên mục `https://baodautu.vn/tai-chinh-chung-khoan-d3/` | **HTML tĩnh + trafilatura** | HTML | Bóc được từ trang bài: `title, body text (4.439 ký tự/bài), ngày đăng, chuyên mục`. Cần selector riêng cho `author`. | Không | **Trung bình** | RSS (`*.rss`) trả channel **rỗng** (link sai thành `baodautu.vn//.rss`) → không dùng được. Phải scrape HTML: lấy link bài ở trang chuyên mục rồi trafilatura bóc nội dung. Selector dễ vỡ khi đổi layout. |
| **CBTT — HOSE (hsx.vn)** | `https://api.hsx.vn/n/api/v1/1/news?pageIndex=1&pageSize=5` | **JSON API ẩn (httpx)** — phát hiện qua Playwright | JSON `{success, message, data:{list[], object, paging}}` | `id, title, summary (HTML), alias, link, newsType, catId, code, postedDate, publishFrom, publishTo, approvedDate, createdDate, relatedId, relatedType, langId` (epoch giây) | **Không** (lúc chạy) | **Trung bình** | `www.hsx.vn` là **Angular SPA** (HTML tĩnh chỉ 1.9KB, 0 link). Dùng Playwright bắt XHR → lộ host `api.hsx.vn/{c,n}/api/v1/...` (JSON, không auth). Sau khi biết endpoint thì gọi httpx trực tiếp, **không cần browser**. API nội bộ không tài liệu → dễ vỡ. |
| **CBTT — HNX (hnx.vn)** | `https://www.hnx.vn/vi-vn/cophieu-etfs/disclosures.html` | **CHƯA lấy được** (lịch sự) | — | — | Có (AJAX) | **Thấp / nghẽn** | Lỗi `SSL: CERTIFICATE_VERIFY_FAILED` (server thiếu intermediate cert). Tắt verify mới ra 41KB/74 link, dữ liệu nạp qua AJAX. **Không bypass TLS** trong production. Khuyến nghị: lấy CBTT HNX **gián tiếp qua VNDirect** (attachments trỏ `owa.hnx.vn`). |
| **CBTT — VSDC (congbothongtin.ssc.gov.vn)** | `https://congbothongtin.ssc.gov.vn/faces/NewsSearch` | HTML tĩnh lấy được khung; **danh sách cần Playwright** | HTML (JSF/Oracle ADF) | Trang khung: menu danh mục (`Thông tin công bố, Công ty đại chúng, Tổ chức kiểm toán, Báo cáo tài chính, Bất thường 24h`), 51 `<tr>`. Danh sách CBTT thực + chi tiết nạp qua **postback ViewState**. | **Có** | **Thấp** | Portal JSF/ADF có `javax.faces.ViewState` → phân trang/tìm kiếm là postback, không lấy được bằng GET đơn thuần. Cần Playwright điều khiển form. Dữ liệu công khai theo luật (cổng nhà nước). |

## Tuân thủ & rủi ro pháp lý (khảo sát 2026-06-13)

> ⚠️ **Đây KHÔNG phải tư vấn pháp lý** — chỉ là thông tin để cân nhắc. Chỗ đánh dấu 🟡/🔴 nên hỏi luật sư.
> Cách đọc cột: **robots cho phép?** = các path ta thu thập (RSS / news JSON / trang bài) có bị `Disallow` không.
> **ToS có cấm?** = điều khoản về crawl / sao chép / tái phát hành. Chi tiết & lý do xếp mức rủi ro ở [`legal_notes.md`](legal_notes.md).
> Raw robots.txt đã lưu ở `spikes/samples/robots/`; script: `spikes/spike_compliance.py`.

| Nguồn | robots cho phép? | ToS có cấm? | Mức rủi ro | Lưu full-text hay snippet+URL |
|---|---|---|---|---|
| **VNDirect finfo-api** | ✅ Có — robots.txt **404** ở cả `www` và `api-finfo` (không công bố chính sách) | API không có ToS riêng. ToS website **không** cấm crawl rõ ràng; có © "Công ty CP Chứng khoán VNDirect" | 🟡 **Vàng** | **Snippet + URL + metadata**. Không lưu full-text vào DB; PDF công bố chỉ giữ link / raw nội bộ |
| **VnEconomy** | ✅ Có — `Allow: /` (mở hoàn toàn) | Không cấm crawl. **Tái sử dụng: "đăng lại phải có chấp thuận bằng văn bản"**; © Tạp chí của Hội KH Kinh tế VN | 🟡 **Vàng** | **Snippet + URL** (raw HTML chỉ nội bộ) |
| **Tin nhanh chứng khoán** | ✅ Có cho RSS & bài — chỉ chặn `/api/`, `/search/`, `/tag.html`, `/print.html` | Không cấm crawl rõ. **"Ghi rõ nguồn khi phát hành lại"**; © Báo Tài chính - Đầu tư (Bộ Tài chính) | 🟡 **Vàng** | **Snippet + URL**; ghi nguồn "Báo Đầu tư Chứng khoán" nếu hiển thị lại |
| **Vietstock** | ✅ Có cho RSS & bài — chặn `/*.js`, `/*.css`, `/manager`, `/export`, `/cache` | **Cấm "tái bản / sao chụp / mua bán / lợi dụng vì mục đích thương mại"**; © Vietstock; có gói DataFeed thương mại riêng | 🟡→🔴 **Vàng (Đỏ nếu thương mại)** | **Snippet + URL** cho nghiên cứu; dùng thương mại/diện rộng → mua **DataFeed** |
| **Báo Đầu tư** | ✅ Có — `Allow: /` (mở hoàn toàn) | Không cấm crawl. **"Mọi sử dụng nội dung phải có đồng ý bằng văn bản"** (khắt khe); © Báo Tài chính - Đầu tư (Bộ Tài chính) | 🟡 **Vàng (khắt khe)** | **Snippet + URL**; cân nhắc xin phép bằng văn bản trước khi kích hoạt |
| **CBTT — HOSE (hsx.vn)** | ✅ Có — `Disallow:` rỗng = mở hoàn toàn | Không tìm thấy ToS cấm (site JS-heavy, chưa xác minh được footer). CBTT là thông tin công khai bắt buộc theo luật | 🟢 **Xanh** (nên xác minh footer trên trình duyệt) | **Snippet + URL** |
| **CBTT — HNX (hnx.vn)** | ⚠️ robots.txt **404** (+ lỗi chuỗi chứng chỉ TLS) | Trang **"Khuyến cáo": liên hệ HNX trước khi đăng/phát lại thông tin**; © Sở GDCK Hà Nội | 🟡 **Vàng** | **Snippet + URL**; phải xử lý TLS hợp lệ trước khi triển khai |
| **CBTT — VSDC (ssc.gov.vn)** | ⚠️ robots.txt **404** (cổng nhà nước) | Không có ToS cấm bên đọc; quy chế (QĐ 820/QĐ-UBCK) chỉ ràng buộc bên **NỘP** báo cáo; © UBCKNN | 🟢 **Xanh** | **Snippet + URL** |

**Quy ước mức rủi ro:** 🟢 Xanh = dữ liệu công khai theo luật / mở, rào cản thấp · 🟡 Vàng = có bản quyền hoặc ràng buộc tái phát hành, mặc định **chỉ lưu metadata + URL + đoạn trích ngắn (≤500 ký tự)** · 🔴 Đỏ = ToS cấm rõ với mục đích của ta (Vietstock cho mục đích thương mại).

## Khuyến nghị xếp ưu tiên triển khai (rẻ → đắt)

1. **VNDirect finfo-api (JSON)** — 1 endpoint phủ cả tin tức + CBTT (kèm PDF gốc HNX/HOSE), lọc theo ticker. Cách rẻ và phủ rộng nhất. *Rủi ro: không chính thức.*
2. **RSS: VnEconomy, Tin nhanh chứng khoán, Vietstock** — ổn định, đúng chuẩn, gần như zero-maintenance cho phần tiêu đề/tóm tắt/ngày.
3. **HOSE api.hsx.vn (JSON)** — CBTT chính thức HOSE, không cần browser khi đã biết endpoint.
4. **Báo Đầu tư (HTML + trafilatura)** — cần selector, bảo trì vừa.
5. **VSDC (Playwright)** — chỉ làm khi cần CBTT trực tiếp từ VSDC; chi phí cao.
6. **HNX trực tiếp** — hoãn; ưu tiên lấy gián tiếp qua VNDirect cho tới khi xử lý được chuỗi chứng chỉ TLS.

## Nguồn CHƯA lấy được (trực tiếp) và lý do

| Nguồn / cách | Lý do chưa lấy được | Hướng xử lý |
|---|---|---|
| **CBTT HNX (trực tiếp)** | `SSL: CERTIFICATE_VERIFY_FAILED` — server hnx.vn không trả intermediate certificate; client không dựng được chuỗi tin cậy. | Không bypass TLS. Nạp đúng CA bundle / chờ HNX sửa cert. **Tạm thời lấy gián tiếp qua VNDirect** (`newsGroup:disclosure`, attachments `owa.hnx.vn`). |
| **CBTT VSDC (danh sách)** | Portal JSF/Oracle ADF, phân trang & tìm kiếm chạy bằng postback `ViewState`; GET tĩnh chỉ trả khung trang. | Playwright điều khiển form tìm kiếm + phân trang (tier đắt nhất). |
| **Báo Đầu tư RSS** | Mọi đường dẫn `*.rss` trả channel rỗng (`<link>https://baodautu.vn//.rss</link>`), không có `<item>`. | Bỏ RSS, dùng HTML + trafilatura (đã chạy được). Có thể dò lại path RSS đúng theo category-id sau. |
| **Vietstock API nội bộ / `/export`** | Có CSRF token; `robots.txt` chặn `/export`. **Không thử** (tuân thủ). | Dùng RSS chính thức (đã chạy được). Cần dữ liệu sâu hơn → cân nhắc Vietstock DataFeed thương mại. |
| **Tin nhanh chứng khoán `/api/`** | `robots.txt` chặn `/api/`. **Không thử** (tuân thủ). | Dùng RSS (đã chạy được). |
| **HOSE qua HTML tĩnh** | `www.hsx.vn` là SPA Angular, HTML tĩnh rỗng (1.9KB, 0 link). | Đã giải bằng JSON API `api.hsx.vn` (xem bảng). |

## Ghi chú tuân thủ (đã áp dụng khi spike)

- Gửi User-Agent định danh + email liên hệ ở **mọi** request.
- Mỗi endpoint chỉ gọi **1–2 lần**, có `sleep` giữa các lần; **không** crawl hàng loạt.
- Tôn trọng `robots.txt`: **không** chạm `/api/` (Tin nhanh CK) và `/export` (Vietstock).
- **Không** tắt xác thực TLS ngoài bước phân loại; **không** giải CAPTCHA, **không** giả mạo fingerprint.
- Các API không chính thức (VNDirect, HOSE) được đánh dấu *dễ vỡ* — phải có cảnh báo & fallback khi lên production.
