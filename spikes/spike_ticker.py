"""Spike: lấy thông tin cho MỘT mã chứng khoán.

Gộp 3 nguồn dữ liệu về 1 ticker (qua VNDirect, không auth):
  1. Tin tức        (news, lọc tagCodes)
  2. Công bố thông tin (disclosure, có PDF đính kèm)
  3. Khuyến nghị     (recommendations: giá mục tiêu, BUY/HOLD/SELL)

Cách chạy:
  .venv\\Scripts\\python.exe spikes\\spike_ticker.py VCB
  .venv\\Scripts\\python.exe spikes\\spike_ticker.py            (mặc định VCB)
"""
from __future__ import annotations

import sys

from _common import banner, fail, get, polite_sleep

API = "https://api-finfo.vndirect.com.vn/v4"


def show_news(code: str) -> None:
    banner(f"{code} · TIN TỨC (mới nhất)")
    r = get(f"{API}/news?q=tagCodes:{code}&size=5&sort=newsDate:desc")
    if r.status_code != 200:
        fail(f"news status {r.status_code}")
        return
    data = r.json()
    print(f"  tổng số tin có gắn mã {code}: {data.get('totalElements'):,}")
    for x in data["data"]:
        print(f"  • [{x['newsDate']}] ({x['newsGroup']}) {x['newsTitle'][:80]}")
        if x.get("newsUrl"):
            print(f"      {x['newsUrl']}")


def show_disclosures(code: str) -> None:
    banner(f"{code} · CÔNG BỐ THÔNG TIN (CBTT, kèm file)")
    r = get(f"{API}/news?q=tagCodes:{code}~newsGroup:disclosure&size=5&sort=newsDate:desc")
    if r.status_code != 200:
        fail(f"disclosure status {r.status_code}")
        return
    recs = r.json()["data"]
    if not recs:
        print("  (không có CBTT gần đây cho mã này)")
        return
    for x in recs:
        atts = x.get("attachments") or []
        print(f"  • [{x['newsDate']}] {x['newsType']:16s} {x['newsTitle'][:70]}")
        for a in atts:
            print(f"      📎 {a['name']}  ->  {a['url']}")


def show_reco(code: str) -> None:
    banner(f"{code} · KHUYẾN NGHỊ CTCK (giá mục tiêu)")
    r = get(f"{API}/recommendations?q=code:{code}&size=5&sort=reportDate:desc")
    if r.status_code != 200:
        fail(f"recommendations status {r.status_code}")
        return
    recs = r.json()["data"]
    if not recs:
        print("  (chưa có khuyến nghị cho mã này)")
        return
    for x in recs:
        print(f"  • {x['reportDate']} | {x['firm']:10s} | {x['type']:5s}"
              f" | giá hiện tại {x.get('reportPrice')} → mục tiêu {x.get('targetPrice')}"
              f" | {x.get('analyst')}")


def main() -> None:
    code = (sys.argv[1] if len(sys.argv) > 1 else "VCB").upper().strip()
    print(f"\n>>> Lấy thông tin cho mã: {code}")
    show_news(code)
    polite_sleep(1.2)
    show_disclosures(code)
    polite_sleep(1.2)
    show_reco(code)

    banner(f"{code} · TÓM TẮT")
    print("- 3 lát cắt cho 1 mã: tin tức + CBTT (có link PDF) + khuyến nghị giá mục tiêu.")
    print("- Muốn tải PDF của 1 CBTT: copy link 📎 ở trên, hoặc xem spike_dt_resolution.py.")
    print(f"- Đổi mã khác: python spikes\\spike_ticker.py FPT  (thay {code} bằng mã bạn muốn).")


if __name__ == "__main__":
    main()
