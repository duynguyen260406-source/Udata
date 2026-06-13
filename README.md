# Udata_1 — Khảo sát nguồn dữ liệu phi cấu trúc chứng khoán Việt Nam

Repo này chứa các **spike script khảo sát** (throwaway) nhằm xác định cách **rẻ nhất có thể** để thu thập tin tức và công bố thông tin (CBTT) từ các nguồn F0 của thị trường chứng khoán Việt Nam (HOSE, HNX, UPCOM).

**Đây KHÔNG phải code production.** Kết quả khảo sát là đầu vào để thiết kế pipeline thu thập thực sự (xem repo `Findata/`).

---

## Cấu trúc thư mục

```
Udata_1/
├── spikes/                  # Script khảo sát, mỗi file = 1 nguồn hoặc 1 loại dữ liệu
│   ├── _common.py               # Helper dùng chung (User-Agent, get(), save_sample(), pdf_probe())
│   │
│   │   # --- Nhóm 1: source spikes ---
│   ├── spike_vndirect.py        # VNDirect finfo-api (JSON API ẩn)
│   ├── spike_vneconomy.py       # VnEconomy (RSS + trafilatura fallback)
│   ├── spike_tinnhanhchungkhoan.py  # Tin nhanh chứng khoán (RSS)
│   ├── spike_vietstock.py       # Vietstock (RSS)
│   ├── spike_baodautu.py        # Báo Đầu tư (HTML tĩnh + trafilatura)
│   ├── spike_cbtt.py            # CBTT: HOSE JSON + HNX + VSDC (--playwright flag)
│   ├── spike_hnx_vsdc.py        # HNX POST endpoints ẩn + VSDC Playwright
│   │
│   │   # --- Nhóm 2: data-type spikes ---
│   ├── spike_dt_news.py         # Tin tức: RSS + trích xuất bài viết (trafilatura)
│   ├── spike_dt_cbtt.py         # CBTT: JSON metadata + tải PDF đính kèm
│   ├── spike_dt_research.py     # Báo cáo CTCK: gap documentation + metadata khuyến nghị
│   ├── spike_dt_resolution.py   # Nghị quyết/ĐHĐCĐ: PDF + pdfplumber (selectable vs scan)
│   │
│   │   # --- Nhóm 3: tiện ích ---
│   ├── spike_ticker.py          # Tổng hợp tin tức + CBTT + khuyến nghị cho 1 mã CK
│   ├── spike_compliance.py      # Kiểm tra robots.txt tất cả nguồn
│   └── samples/                 # Raw response mẫu đã lưu (commit vào repo)
│       ├── vndirect.json
│       ├── vneconomy.xml
│       ├── tinnhanhchungkhoan.xml
│       ├── vietstock.xml
│       ├── baodautu.html
│       ├── cbtt_hose.json
│       ├── cbtt_vsdc.html
│       ├── robots/          # robots.txt đã tải về của từng nguồn
│       └── ...
├── docs/
│   ├── source_matrix.md     # Bảng tổng hợp kết quả khảo sát (đọc cái này trước)
│   ├── legal_notes.md       # Phân tích rủi ro pháp lý từng nguồn
│   ├── data_type_source_map.md  # Loại dữ liệu → nguồn thu thập
│   └── vn_stock_unstructured_data_guide (1).md
├── pyproject.toml           # Metadata dự án + dependencies
├── requirements.txt         # Danh sách dependency (pip install trực tiếp)
└── .venv/                   # Virtualenv (gitignored)
```

---

## Cài đặt môi trường

### Yêu cầu
- Python 3.11+
- Windows (đã test) hoặc Linux/macOS

### Bước 1 — Tạo và kích hoạt virtualenv

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 2 — Cài dependencies

```powershell
pip install -r requirements.txt
```

Hoặc cài từ `pyproject.toml` (editable):

```powershell
pip install -e .
```

### Bước 3 — Cài Playwright (chỉ cần cho VSDC/HOSE spike có flag `--playwright`)

```powershell
playwright install chromium
```

---

## Chạy các spike script

Tất cả lệnh chạy **từ thư mục gốc `Udata_1\`**. Mỗi spike in ra terminal: status HTTP, các trường quan sát được, và đường dẫn file raw mẫu đã lưu vào `spikes/samples/`.

### Nhóm 1 — Khảo sát nguồn (source spikes)

#### `spike_vndirect.py` — VNDirect finfo-api (JSON API ẩn)
Probe các endpoint JSON của VNDirect: tin tức toàn thị trường, tin theo ticker, và chỉ CBTT.
```powershell
.\.venv\Scripts\python.exe spikes\spike_vndirect.py
```

#### `spike_vneconomy.py` — VnEconomy (RSS + trafilatura fallback)
Fetch RSS chứng khoán VnEconomy, thử trafilatura nếu RSS không đủ nội dung.
```powershell
.\.venv\Scripts\python.exe spikes\spike_vneconomy.py
```

#### `spike_tinnhanhchungkhoan.py` — Tin nhanh chứng khoán (RSS)
Fetch RSS `home.rss` của tinnhanhchungkhoan.vn (không dùng `/api/` — robots chặn).
```powershell
.\.venv\Scripts\python.exe spikes\spike_tinnhanhchungkhoan.py
```

#### `spike_vietstock.py` — Vietstock (RSS)
Fetch RSS chuyên mục Chứng khoán (channel 144) của Vietstock.
```powershell
.\.venv\Scripts\python.exe spikes\spike_vietstock.py
```

#### `spike_baodautu.py` — Báo Đầu tư (HTML tĩnh + trafilatura)
Scrape trang chuyên mục tài chính-chứng khoán, bóc nội dung bài bằng trafilatura (RSS rỗng).
```powershell
.\.venv\Scripts\python.exe spikes\spike_baodautu.py
```

#### `spike_cbtt.py` — CBTT HOSE / HNX / VSDC
Khảo sát 3 cổng công bố thông tin. Mặc định dùng httpx; flag `--playwright` bắt XHR để xác nhận endpoint HOSE.
```powershell
.\.venv\Scripts\python.exe spikes\spike_cbtt.py              # HOSE JSON + thử HNX + VSDC tĩnh
.\.venv\Scripts\python.exe spikes\spike_cbtt.py --playwright # Bắt XHR qua browser (cần: playwright install chromium)
```

#### `spike_hnx_vsdc.py` — HNX POST endpoints + VSDC (Playwright)
Xác nhận chiến lược lấy CBTT HNX qua POST endpoints ẩn (ASP.NET SPA, không cần JS); VSDC cần Playwright.
```powershell
.\.venv\Scripts\python.exe spikes\spike_hnx_vsdc.py
```

---

### Nhóm 2 — Khảo sát theo loại dữ liệu (data-type spikes)

#### `spike_dt_news.py` — Tin tức: RSS + trích xuất bài viết đầy đủ
Lấy 1 mục từ RSS VnEconomy, fetch trang bài, bóc title/author/date/body bằng trafilatura. In độ dài body (không in toàn văn — tuân thủ bản quyền).
```powershell
.\.venv\Scripts\python.exe spikes\spike_dt_news.py
```

#### `spike_dt_cbtt.py` — CBTT: JSON metadata + tải PDF đính kèm
Lấy record CBTT đầy đủ từ HOSE (api.hsx.vn) và 1 bản ghi từ VNDirect có PDF đính kèm, tải thử PDF.
```powershell
.\.venv\Scripts\python.exe spikes\spike_dt_cbtt.py
```

#### `spike_dt_research.py` — Báo cáo CTCK: gap documentation
Ghi nhận việc không có nguồn 🟢/🟡 nào cung cấp PDF báo cáo phân tích đầy đủ. Lấy metadata khuyến nghị (firm, rating, target price) từ VNDirect làm điểm gần nhất.
```powershell
.\.venv\Scripts\python.exe spikes\spike_dt_research.py
```

#### `spike_dt_resolution.py` — Nghị quyết HĐQT / ĐHĐCĐ: PDF + pdfplumber
Lấy 1 bản tin loại `resolutions` từ VNDirect, tải PDF đính kèm, dùng pdfplumber kiểm tra: số trang, text có selectable không (hay là scan cần OCR), 200 ký tự đầu.

> Yêu cầu thêm: `pip install pdfplumber`
```powershell
.\.venv\Scripts\python.exe spikes\spike_dt_resolution.py
```

---

### Nhóm 3 — Tiện ích

#### `spike_ticker.py` — Tổng hợp dữ liệu cho 1 mã chứng khoán
Gộp 3 loại dữ liệu về 1 ticker từ VNDirect: tin tức, CBTT (có PDF), và khuyến nghị. Nhận ticker làm argument dòng lệnh.
```powershell
.\.venv\Scripts\python.exe spikes\spike_ticker.py VCB   # tra cứu mã VCB
.\.venv\Scripts\python.exe spikes\spike_ticker.py HPG   # tra cứu mã HPG
.\.venv\Scripts\python.exe spikes\spike_ticker.py       # mặc định: VCB
```

#### `spike_compliance.py` — Kiểm tra robots.txt tất cả nguồn
Fetch robots.txt của mọi domain trong danh sách (1 request/host), lưu vào `spikes/samples/robots/`, in ra các nhóm `User-agent` và `Disallow` để đánh giá.
```powershell
.\.venv\Scripts\python.exe spikes\spike_compliance.py
```

---

## Kết quả khảo sát tóm tắt

Xem chi tiết tại [docs/source_matrix.md](docs/source_matrix.md).

| Nguồn | Phương thức | Trạng thái |
|---|---|---|
| **VNDirect finfo-api** | JSON API ẩn (httpx) | Hoạt động — 243.950 bản tin, lọc được theo ticker |
| **VnEconomy** | RSS (feedparser) | Hoạt động — 60 mục/feed |
| **Tin nhanh chứng khoán** | RSS (feedparser) | Hoạt động — 50 mục/feed |
| **Vietstock** | RSS (feedparser) | Hoạt động — 30 mục/feed |
| **Báo Đầu tư** | HTML tĩnh + trafilatura | Hoạt động (RSS rỗng, phải scrape HTML) |
| **CBTT HOSE (hsx.vn)** | JSON API ẩn (httpx) | Hoạt động — phát hiện endpoint qua Playwright |
| **CBTT HNX (hnx.vn)** | — | Tạm hoãn — lỗi SSL certificate |
| **CBTT VSDC** | Playwright (JSF/ADF) | Cần Playwright — portal postback |

### Thứ tự ưu tiên triển khai

1. **VNDirect finfo-api** — 1 endpoint phủ tin tức + CBTT + PDF gốc HNX/HOSE
2. **RSS: VnEconomy, Tin nhanh CK, Vietstock** — ổn định, zero-maintenance
3. **HOSE api.hsx.vn** — CBTT chính thức, không cần browser
4. **Báo Đầu tư** — cần selector, bảo trì vừa
5. **VSDC (Playwright)** — chỉ khi cần CBTT trực tiếp từ VSDC

---

## Tuân thủ & luật lệ

- **robots.txt**: Luôn kiểm tra trước khi fetch. Không bao giờ bypass `Disallow`.
- **User-Agent**: Mọi request đều gửi `udata-survey/0.1 (research bot; contact: duynguyen260406@gmail.com)`.
- **Rate limit**: Mỗi endpoint chỉ gọi 1–2 lần trong spike, có sleep giữa các lần. Không crawl hàng loạt.
- **TLS**: Không tắt xác thực TLS (HNX SSL lỗi → hoãn, không bypass).
- **Lưu trữ**: Chỉ lưu snippet ≤500 ký tự + URL + metadata. Không lưu full-text vào DB.
- **VnExpress**: Bị loại — robots.txt chặn `ClaudeBot` và `anthropic-ai` tường minh.

Phân tích pháp lý đầy đủ từng nguồn: [docs/legal_notes.md](docs/legal_notes.md).

---

## Dependencies chính

| Thư viện | Mục đích |
|---|---|
| `httpx` | HTTP client — gọi JSON API và HTML tĩnh |
| `feedparser` | Parse RSS/Atom feed |
| `selectolax` | Parse HTML nhanh (Modest/Lexbor engine) |
| `beautifulsoup4` + `lxml` | Parse HTML, fallback cho bs4 |
| `trafilatura` | Bóc nội dung bài viết từ HTML |
| `playwright` | Điều khiển browser cho trang JS-rendered |
