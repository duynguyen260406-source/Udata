"""Spike (data-type): Nghị quyết / ĐHĐCĐ — PDF + pdfplumber extraction.

Pull a real "Nghị quyết HĐQT" disclosure (newsType:resolutions) from VNDirect
(🟡), download its PDF, and probe it with pdfplumber: page count, whether text
is selectable (else it's a scan needing OCR), and the first 200 chars.

Per task: if the PDF is a scan, we only RECORD that fact — NO OCR here.
Run: .venv\\Scripts\\python.exe spikes\\spike_dt_resolution.py
"""
from __future__ import annotations

from _common import (SAMPLES_DIR, banner, fail, get, pdf_probe, polite_sleep,
                     save_sample)

# Resolutions first; fall back to general meeting (ĐHĐCĐ) docs.
QUERIES = [
    ("Nghị quyết HĐQT", "https://api-finfo.vndirect.com.vn/v4/news?q=newsType:resolutions&size=10&sort=newsDate:desc"),
    ("ĐHĐCĐ / meeting", "https://api-finfo.vndirect.com.vn/v4/news?q=newsType:meeting&size=10&sort=newsDate:desc"),
]


def pick_record() -> dict | None:
    banner("Nghị quyết/ĐHĐCĐ · part 1 — tìm bản ghi có PDF (VNDirect)")
    for label, url in QUERIES:
        r = get(url)
        if r.status_code != 200:
            polite_sleep(1.0)
            continue
        rec = next((x for x in r.json()["data"] if x.get("attachments")), None)
        if rec:
            print(f"  [{label}] picked: {rec['tagCodes']} — {rec['newsTitle']}"
                  f"  (type={rec['newsType']}, date={rec['newsDate']})")
            return rec
        polite_sleep(1.0)
    fail("không thấy bản ghi nghị quyết/ĐHĐCĐ kèm PDF")
    return None


def main() -> None:
    rec = pick_record()
    if not rec:
        return
    att = rec["attachments"][0]
    print(f"  attachment: {att['name']}\n  url: {att['url']}")

    banner("Nghị quyết/ĐHĐCĐ · part 2 — tải PDF + pdfplumber")
    polite_sleep(1.2)
    pr = get(att["url"], timeout=40.0)
    if pr.status_code != 200 or b"%PDF" not in pr.content[:1024]:
        fail(f"PDF download failed (status {pr.status_code})")
        return
    path = save_sample("resolution_sample", pr.content, "pdf")

    info = pdf_probe(path)
    print(f"  số trang        : {info['pages']}")
    print(f"  text-selectable : {info['selectable']}  "
          f"({'có text layer' if info['selectable'] else 'KHÔNG — là scan, cần OCR sau'})")
    print(f"  200 ký tự đầu   : {info['head']!r}")

    banner("Nghị quyết/ĐHĐCĐ · TÓM TẮT")
    print(f"- Lấy được: 1 PDF '{att['name']}' ({len(pr.content):,} bytes, {info['pages']} trang)"
          f" của mã {rec['tagCodes']}.")
    print(f"- Trích text: {'OK (text-selectable)' if info['selectable'] else 'KHÔNG — PDF scan, chưa OCR (đúng yêu cầu)'}.")
    print("- Field có : tagCodes (mã CK), newsTitle, newsType, newsDate, PDF gốc.")
    print("- Field THIẾU: nội dung có cấu trúc (ngày họp, tỷ lệ cổ tức…) nằm trong thân PDF,"
          " phải parse/trích sau; metadata feed không tách sẵn.")
    print("- Cần xử lý sau: phát hiện scan → OCR; trích thực thể (ngày, số nghị quyết, tỷ lệ);"
          " dùng bản VI (có cả bản EN trong attachments).")


if __name__ == "__main__":
    main()
