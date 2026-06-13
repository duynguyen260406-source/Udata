"""Spike (data-type): CBTT — JSON metadata + PDF attachment.

- Full JSON record from HOSE official API (api.hsx.vn).
- A real disclosure record WITH a PDF attachment from VNDirect (the cheapest way
  to get metadata + the actual filing PDF in one feed), then download 1 PDF.

Sources: HOSE 🟢, VNDirect 🟡 (both in source_matrix). No auth, no JS.
Run: .venv\\Scripts\\python.exe spikes\\spike_dt_cbtt.py
"""
from __future__ import annotations

from _common import (SAMPLES_DIR, banner, fail, get, polite_sleep, pretty,
                     save_sample)

HOSE_HEADERS = {"Accept": "application/json", "Origin": "https://www.hsx.vn",
                "Referer": "https://www.hsx.vn/"}


def hose_metadata() -> dict | None:
    banner("CBTT · part 1 — HOSE official JSON metadata (api.hsx.vn)")
    r = get("https://api.hsx.vn/n/api/v1/1/news?pageIndex=1&pageSize=3",
            headers=HOSE_HEADERS)
    if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
        fail(f"HOSE API status {r.status_code}")
        return None
    rec = r.json()["data"]["list"][0]
    print(f"  HOSE record fields ({len(rec)}): {sorted(rec.keys())}")
    print("  --- 1 full HOSE record ---")
    print(pretty(rec)[:900])
    return rec


def vndirect_disclosure_with_pdf() -> dict | None:
    banner("CBTT · part 2 — VNDirect disclosure record + PDF download")
    r = get("https://api-finfo.vndirect.com.vn/v4/news"
            "?q=newsGroup:disclosure&size=10&sort=newsDate:desc")
    if r.status_code != 200:
        fail(f"VNDirect status {r.status_code}")
        return None
    recs = r.json()["data"]
    rec = next((x for x in recs if x.get("attachments")), None)
    if not rec:
        fail("no disclosure record with attachments in this page")
        return None
    print(f"  picked: {rec['tagCodes']} — {rec['newsTitle']}  "
          f"(group={rec['newsGroup']}, type={rec['newsType']}, date={rec['newsDate']})")
    print(f"  VNDirect record fields: {sorted(rec.keys())}")
    att = rec["attachments"][0]
    pdf_url = att["url"]                    # vndirect-resource host (reliable)
    print(f"  attachment: {att['name']}")
    print(f"  url: {pdf_url}")

    polite_sleep(1.2)
    pr = get(pdf_url, timeout=40.0)
    if pr.status_code != 200 or b"%PDF" not in pr.content[:1024]:
        fail(f"PDF download failed (status {pr.status_code}, not a PDF?)")
        return rec
    save_sample("cbtt_sample", pr.content, "pdf")
    print(f"  PDF file name : {att['name']}")
    print(f"  PDF size      : {len(pr.content):,} bytes")
    return rec


def main() -> None:
    hose = hose_metadata()
    polite_sleep(1.2)
    vnd = vndirect_disclosure_with_pdf()

    banner("CBTT · TÓM TẮT")
    pdf = SAMPLES_DIR / "cbtt_sample.pdf"
    print("- Lấy được: metadata CBTT chính thức từ HOSE (JSON) + 1 bản ghi disclosure"
          " VNDirect kèm PDF gốc.")
    print(f"- Field HOSE JSON: {sorted(hose.keys()) if hose else 'N/A'}")
    print(f"- Field VNDirect : {sorted(vnd.keys()) if vnd else 'N/A'}")
    print(f"- PDF đính kèm   : {'cbtt_sample.pdf (%d bytes)' % pdf.stat().st_size if pdf.exists() else 'CHƯA tải được'}")
    print("- Field THIẾU    : HOSE news JSON KHÔNG kèm PDF (link=null) → PDF phải lấy qua"
          " VNDirect attachments. `newsContent` disclosure thường rỗng (nội dung nằm trong PDF).")
    print("- Cần xử lý sau  : map record HOSE ↔ PDF (qua mã CK + ngày); PDF có thể là scan"
          " → OCR ở pipeline; chuẩn hoá `newsDate` epoch/ISO giữa 2 nguồn.")


if __name__ == "__main__":
    main()
