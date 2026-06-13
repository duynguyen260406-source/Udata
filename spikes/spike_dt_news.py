"""Spike (data-type): Tin tức — RSS + trafilatura article extraction.

Take 1 entry from VnEconomy RSS (🟡), fetch the article page, and extract
title/author/date/body with trafilatura. Save the extracted record as JSON.

NOTE on copyright: production must store only excerpt (≤500 chars) + URL. Here
we print the full body LENGTH (not the body) to demonstrate extraction works.
Run: .venv\\Scripts\\python.exe spikes\\spike_dt_news.py
"""
from __future__ import annotations

import json

import feedparser
import trafilatura

from _common import SAMPLES_DIR, banner, fail, get, polite_sleep, save_sample

RSS = "https://vneconomy.vn/chung-khoan.rss"


def main() -> None:
    banner("Tin tức · part 1 — RSS (VnEconomy)")
    r = get(RSS)
    feed = feedparser.parse(r.content)
    if not feed.entries:
        fail("RSS có 0 entry")
        return
    e = feed.entries[0]
    rss_fields = sorted(e.keys())
    print(f"  RSS entry fields: {rss_fields}")
    print(f"  • title    : {e.get('title')}")
    print(f"  • link     : {e.get('link')}")
    print(f"  • published: {e.get('published')}")

    banner("Tin tức · part 2 — fetch trang bài + trafilatura")
    polite_sleep(1.2)
    ar = get(e.link, timeout=30.0)
    if ar.status_code != 200:
        fail(f"article status {ar.status_code}")
        return
    extracted = trafilatura.extract(
        ar.text, output_format="json", with_metadata=True,
        include_comments=False, url=e.link,
    )
    if not extracted:
        fail("trafilatura không bóc được nội dung")
        return
    meta = json.loads(extracted)

    body = meta.get("text") or ""
    record = {
        "title": meta.get("title"),
        "author": meta.get("author"),
        "date": meta.get("date"),
        "url": meta.get("source") or e.link,
        "sitename": meta.get("sitename"),
        "tags": meta.get("tags"),
        "excerpt": body[:500],          # what production WOULD store
        "body_len": len(body),
    }
    print(f"  trafilatura metadata keys: {sorted(meta.keys())}")
    print("  --- bóc được ---")
    for k in ("title", "author", "date", "url", "sitename"):
        print(f"  • {k:8s}: {record[k]}")
    print(f"  • body text: {len(body):,} ký tự (excerpt lưu 500 đầu)")
    print(f"  • excerpt  : {record['excerpt'][:160]}...")

    save_sample("news_sample", json.dumps(record, ensure_ascii=False, indent=2), "json")

    banner("Tin tức · TÓM TẮT")
    have = [k for k in ("title", "author", "date") if record[k]]
    miss = [k for k in ("title", "author", "date") if not record[k]]
    print(f"- Lấy được: 1 bài VnEconomy qua RSS + bóc toàn văn bằng trafilatura"
          f" ({len(body):,} ký tự).")
    print(f"- Field có : {have} + url + body text.")
    print(f"- Field THIẾU/yếu: {miss or 'không'}"
          " (RSS không có author; date/author đôi khi trafilatura bỏ sót → cần fallback selector).")
    print("- Cần xử lý sau: chuẩn hoá ngày (RSS RFC822 vs trafilatura ISO);"
          " resolve ticker từ title/body; CHỈ lưu excerpt ≤500 ký tự + URL (bản quyền 🟡).")


if __name__ == "__main__":
    main()
