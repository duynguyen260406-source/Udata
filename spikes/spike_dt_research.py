"""Spike (data-type): Báo cáo CTCK — GAP DOCUMENTATION.

Finding: NO 🟢/🟡 source in source_matrix serves full broker-research PDFs.
The closest in-matrix touchpoint is VNDirect's `recommendations` endpoint, which
returns RECOMMENDATION METADATA (firm, rating, target price) — not the report PDF.

Per project rules we do NOT pull a PDF from an un-vetted / off-matrix broker
portal. This spike documents the gap and captures the available metadata.
Run: .venv\\Scripts\\python.exe spikes\\spike_dt_research.py
"""
from __future__ import annotations

import json

from _common import banner, fail, get, pretty, save_sample

REC_URL = ("https://api-finfo.vndirect.com.vn/v4/recommendations"
           "?q=code:VCB&size=5&sort=reportDate:desc")


def main() -> None:
    banner("Báo cáo CTCK · metadata khuyến nghị (VNDirect recommendations 🟡)")
    r = get(REC_URL)
    recs = []
    if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
        recs = r.json().get("data", [])
        if recs:
            print(f"  record fields: {sorted(recs[0].keys())}")
            print("  --- mẫu khuyến nghị (metadata, KHÔNG phải báo cáo PDF) ---")
            for x in recs[:3]:
                print(f"  • {x.get('code')} {x.get('type'):4s} | {x.get('firm'):8s}"
                      f" | mục tiêu {x.get('targetPrice')} | {x.get('reportDate')}"
                      f" | {x.get('analyst')}")
            save_sample("research_recommendations", pretty(recs), "json")
    else:
        fail(f"recommendations status {r.status_code}")

    banner("Báo cáo CTCK · TÓM TẮT (GAP)")
    print("- Lấy được: CHỈ metadata khuyến nghị (firm/rating/targetPrice/reportDate/analyst)"
          " từ VNDirect — KHÔNG có PDF báo cáo đầy đủ.")
    print("- Field có : code, firm, type(BUY/HOLD/SELL), reportPrice, targetPrice,"
          " avgTargetPrice, reportDate, analyst, source.")
    print("- Field THIẾU: toàn văn báo cáo / file PDF / link tới PDF — KHÔNG có trong bất kỳ"
          " nguồn 🟢/🟡 nào của source_matrix.")
    print("- KHÔNG tạo research_sample.pdf: không kéo PDF từ nguồn chưa vetted (đúng ràng buộc).")
    print("- Cần xử lý sau: KHẢO SÁT + ĐÁNH GIÁ PHÁP LÝ 1 nguồn research (VNDirect DStock cần"
          " login, hoặc MBS/SSI/VCBS IR công khai) → thêm vào source_matrix rồi mới spike PDF.")
    print("  => Đây là KHOẢNG TRỐNG Phase 1, đã ghi rõ trong docs/data_type_source_map.md.")


if __name__ == "__main__":
    main()
