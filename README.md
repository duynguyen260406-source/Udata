# Udata_1 — Khảo sát nguồn dữ liệu phi cấu trúc chứng khoán Việt Nam

Repo này chứa các **spike script khảo sát** (throwaway) nhằm xác định cách **rẻ nhất có thể** để thu thập tin tức và công bố thông tin (CBTT) từ các nguồn F0 của thị trường chứng khoán Việt Nam (HOSE, HNX, UPCOM).

**Đây KHÔNG phải code production.** Kết quả khảo sát là đầu vào để thiết kế pipeline thu thập thực sự (xem repo `Findata/`).

---

## Cấu trúc thư mục

```
Udata_1/
├── spikes/                  # Script khảo sát, mỗi file = 1 nguồn
│   ├── _common.py           # Helper dùng chung (User-Agent, get(), save_sample())
│   ├── spike_vndirect.py    # VNDirect finfo-api (JSON API ẩn)
│   ├── spike_vneconomy.py   # VnEconomy (RSS)
│   ├── spike_tinnhanhchungkhoan.py  # Tin nhanh chứng khoán (RSS)
│   ├── spike_vietstock.py   # Vietstock (RSS)
│   ├── spike_baodautu.py    # Báo Đầu tư (HTML + trafilatura)
│   ├── spike_cbtt.py        # CBTT: HOSE (JSON) + HNX + VSDC (Playwright)
│   ├── spike_compliance.py  # Kiểm tra robots.txt của từng nguồn
│   ├── spike_ticker.py      # Thử nghiệm resolve mã chứng khoán
│   └── samples/             # Raw response mẫu đã lưu (commit vào repo)
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

Tất cả lệnh chạy **từ thư mục gốc `Udata_1\`**.

```powershell
# VNDirect — JSON API ẩn (không cần browser)
.\.venv\Scripts\python.exe spikes\spike_vndirect.py

# VnEconomy — RSS feed
.\.venv\Scripts\python.exe spikes\spike_vneconomy.py

# Tin nhanh chứng khoán — RSS feed
.\.venv\Scripts\python.exe spikes\spike_tinnhanhchungkhoan.py

# Vietstock — RSS feed
.\.venv\Scripts\python.exe spikes\spike_vietstock.py

# Báo Đầu tư — HTML tĩnh + trafilatura
.\.venv\Scripts\python.exe spikes\spike_baodautu.py

# CBTT HOSE + HNX + VSDC
.\.venv\Scripts\python.exe spikes\spike_cbtt.py              # HOSE JSON + thử HNX/VSDC
.\.venv\Scripts\python.exe spikes\spike_cbtt.py --playwright # Bắt XHR để tìm API HOSE

# Kiểm tra robots.txt
.\.venv\Scripts\python.exe spikes\spike_compliance.py
```

Mỗi spike sẽ in ra terminal:
- Kết quả GET (status, content-type, kích thước)
- 1–2 bản tin mẫu với các trường quan sát được
- Đường dẫn file raw mẫu đã lưu vào `spikes/samples/`

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
