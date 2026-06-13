# spikes/ — script khảo sát nguồn (throwaway)

Mỗi file là một **spike độc lập** cho 1 nguồn F0. Mục đích: tìm cách **rẻ nhất chạy được**
để lấy dữ liệu, KHÔNG phải code production. Tất cả gọi mạng lịch sự (1–2 lần, có User-Agent).

Kết quả khảo sát tổng hợp ở [`../docs/source_matrix.md`](../docs/source_matrix.md).

## Chạy

```powershell
# từ thư mục gốc dự án (Udata_1\)
.\.venv\Scripts\python.exe spikes\spike_vndirect.py
.\.venv\Scripts\python.exe spikes\spike_vneconomy.py
.\.venv\Scripts\python.exe spikes\spike_tinnhanhchungkhoan.py
.\.venv\Scripts\python.exe spikes\spike_vietstock.py
.\.venv\Scripts\python.exe spikes\spike_baodautu.py
.\.venv\Scripts\python.exe spikes\spike_cbtt.py              # HOSE(JSON)+HNX+VSDC
.\.venv\Scripts\python.exe spikes\spike_cbtt.py --playwright # + bắt XHR để tìm API HOSE
```

Mỗi spike: in 1–2 bản tin mẫu + danh sách trường quan sát được + lưu 1 raw mẫu vào `samples/`.

## File

| Spike | Nguồn | Phương thức chốt |
|---|---|---|
| `spike_vndirect.py` | VNDirect finfo-api | JSON API ẩn (httpx) |
| `spike_vneconomy.py` | VnEconomy | RSS (feedparser) |
| `spike_tinnhanhchungkhoan.py` | Tin nhanh chứng khoán | RSS (feedparser) |
| `spike_vietstock.py` | Vietstock | RSS (feedparser) |
| `spike_baodautu.py` | Báo Đầu tư | HTML tĩnh + trafilatura (RSS rỗng) |
| `spike_cbtt.py` | CBTT HOSE / HNX / VSDC | HOSE: JSON `api.hsx.vn`; HNX: nghẽn SSL; VSDC: JSF cần Playwright |
| `_common.py` | (helper dùng chung) | UA lịch sự, `get()`, `save_sample()`, ép stdout UTF-8 |

## samples/

Một file raw mẫu cho mỗi nguồn (để đối chiếu định dạng/trường, có commit vào repo):

- `vndirect.json`, `vneconomy.xml`, `tinnhanhchungkhoan.xml`, `vietstock.xml`, `baodautu.html`
- `cbtt_hose.json` (API thật) · `cbtt_hose.html` (khung SPA 1.9KB) · `cbtt_hose_rendered.html` (sau render) · `cbtt_vsdc.html` (portal JSF)
