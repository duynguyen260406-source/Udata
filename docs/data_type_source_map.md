# Bản đồ Data Type × Nguồn × Phương thức (Phase 1)

> Bổ sung cho [`source_matrix.md`](source_matrix.md) (nguồn × phương thức) và [`legal_notes.md`](legal_notes.md) (rủi ro).
> Tài liệu này trả lời: **mỗi loại dữ liệu lấy ở ĐÂU, BẰNG CÁCH NÀO, ENDPOINT gì, ĐIỀU KIỆN gì.**
> Ưu tiên nguồn theo legal rating: 🟢 Xanh > 🟡 Vàng; 🔴 Đỏ (Vietstock cho mục đích thương mại) → **bỏ qua**.
> Ngày: **2026-06-13**. Đã kiểm chứng bằng các spike `spikes/spike_dt_*.py`.

## Bảng tổng hợp

| Data type | Lấy ở đâu? (nguồn f0, ưu tiên theo rating) | Lấy như thế nào? | Endpoint / URL pattern | Điều kiện đặc biệt |
|---|---|---|---|---|
| **CBTT** (JSON metadata + PDF) | 1) **HOSE** 🟢 (metadata chính thức) · 2) **VNDirect** 🟡 (metadata **+ PDF** trong 1 call) · 3) VSDC 🟢 / HNX 🟡 (cổng gốc) | **API JSON** + **PDF download** | HOSE: `https://api.hsx.vn/n/api/v1/1/news?pageIndex=1&pageSize=N` · VNDirect: `https://api-finfo.vndirect.com.vn/v4/news?q=newsGroup:disclosure&sort=newsDate:desc` → `attachments[].url` | Không auth. HOSE news JSON **không kèm PDF**; PDF lấy qua VNDirect `attachments[].url` (host `vndirect-resource`, gốc `owa.hnx.vn`). PDF có thể là **scan**. |
| **Nghị quyết / ĐHĐCĐ** (PDF, có thể scan) | **VNDirect** 🟡 (disclosure feed) · cổng gốc HOSE/HNX/VSDC · trang IR doanh nghiệp (*chưa trong matrix*) | **API JSON → PDF download** | `…/v4/news?q=newsType:resolutions` (Nghị quyết HĐQT) · `q=newsType:meeting` (ĐHĐCĐ) · `q=newsType:dividend` (cổ tức)… → `attachments[].url` | Không auth. File song ngữ VI/EN. **PDF có thể scan** (không có text layer) → đánh dấu để OCR ở pipeline sau. |
| **Tin tức** (HTML / RSS) | **VnEconomy** 🟡 · **Tin nhanh chứng khoán** 🟡 · **Báo Đầu tư** 🟡 (HTML) | **RSS** (tiêu đề/ngày/tóm tắt) → **fetch trang bài** → **trafilatura** (toàn văn) | VnEconomy: `https://vneconomy.vn/chung-khoan.rss` · TNCK: `https://www.tinnhanhchungkhoan.vn/rss/home.rss` · Báo Đầu tư: scrape `https://baodautu.vn/<chuyên-mục>/` (RSS rỗng) | Không auth, không cần JS. RSS không có `author` → lấy từ trang bài. **Chỉ lưu excerpt ≤500 ký tự + URL** (yêu cầu bản quyền). |
| **Báo cáo CTCK** (PDF phân tích) | ⚠️ **GAP — chưa có nguồn Xanh/Vàng trong matrix** cấp PDF. Gần nhất: **VNDirect** 🟡 `recommendations` = **metadata** (firm/target price), **không có PDF**. | (metadata) **API JSON**; (PDF) **chưa có** | `https://api-finfo.vndirect.com.vn/v4/recommendations?q=code:VCB&sort=reportDate:desc` → `{firm, type, targetPrice, reportPrice, reportDate, analyst, source}` | PDF báo cáo đầy đủ nằm sau **portal CTCK cần đăng nhập** (VNDirect DStock, MBS, SSI, VCBS…) — **chưa vetted, chưa trong matrix**. Cần khảo sát + đánh giá pháp lý 1 nguồn research ở phase sau. |

## Chi tiết theo từng data type

### 1. CBTT — Công bố thông tin
- **Lấy ở đâu:** HOSE (🟢, chính thức) cho metadata; **VNDirect (🟡)** là cách rẻ nhất lấy **metadata + PDF trong một feed** (có cả HOSE & HNX). VSDC/HNX là cổng gốc nhưng đắt/nghẽn (xem source_matrix).
- **Lấy như thế nào:** GET JSON. Mỗi record disclosure của VNDirect có `attachments[]` trỏ PDF gốc.
- **Endpoint:** `api.hsx.vn/n/api/v1/1/news` (HOSE) · `api-finfo.vndirect.com.vn/v4/news?q=newsGroup:disclosure` (VNDirect, kèm PDF).
- **Điều kiện:** không auth, không JS. PDF có thể scan. Lưu metadata + link; PDF/raw chỉ nội bộ.

### 2. Nghị quyết / ĐHĐCĐ
- **Lấy ở đâu:** VNDirect disclosure feed lọc theo `newsType` (`resolutions`, `meeting`, `dividend`, `charter`…). Cổng gốc HOSE/HNX/VSDC hoặc trang IR doanh nghiệp là phương án bổ sung.
- **Lấy như thế nào:** API JSON → tải `attachments[].url` (PDF).
- **Endpoint:** `…/v4/news?q=newsType:resolutions&sort=newsDate:desc`.
- **Điều kiện:** không auth. **PDF thường là scan** với doanh nghiệp nhỏ → cần OCR sau (không OCR ở bước spike).

### 3. Tin tức
- **Lấy ở đâu:** VnEconomy / Tin nhanh chứng khoán (RSS) ưu tiên; Báo Đầu tư (HTML, RSS rỗng). Tất cả 🟡 — chỉ lưu snippet + URL.
- **Lấy như thế nào:** RSS lấy danh sách → fetch trang bài → trafilatura bóc `title/author/date/text`.
- **Endpoint:** xem bảng. Không cần JS.
- **Điều kiện:** RSS thiếu `author` (lấy từ HTML). Bản quyền: không lưu full-text vào DB truy vấn.

### 4. Báo cáo CTCK — ⚠️ GAP
- **Hiện trạng:** Không nguồn 🟢/🟡 nào trong matrix cấp **PDF báo cáo phân tích**. VNDirect `recommendations` chỉ cho **metadata khuyến nghị** (giá mục tiêu, khuyến nghị BUY/HOLD, CTCK phát hành, ngày) — hữu ích cho tín hiệu nhưng **không phải báo cáo đầy đủ**.
- **Vì sao:** PDF research nằm sau portal CTCK cần đăng nhập (VNDirect DStock; hoặc MBS/SSI/VCBS) — chưa được đưa vào matrix và **chưa đánh giá pháp lý**.
- **Hành động đề xuất (phase sau):** chọn & vet 1 nguồn research (broker IR công khai hoặc tài khoản hợp lệ), kiểm tra robots/ToS như đã làm cho các nguồn khác, rồi mới spike. **Không** kéo PDF từ nguồn chưa vetted ở bước này.

## Tóm tắt độ phủ Phase 1

| Data type | JSON metadata | PDF / full-text | Trạng thái spike |
|---|---|---|---|
| CBTT | ✅ HOSE + VNDirect | ✅ VNDirect attachment | **Lấy được thật** |
| Nghị quyết/ĐHĐCĐ | ✅ VNDirect | ✅ VNDirect attachment (có thể scan) | **Lấy được thật** |
| Tin tức | ✅ RSS | ✅ trafilatura (excerpt-only khi lưu) | **Lấy được thật** |
| Báo cáo CTCK | 🟡 chỉ metadata (recommendations) | ❌ chưa có nguồn vetted | **GAP — cần bổ sung nguồn** |
