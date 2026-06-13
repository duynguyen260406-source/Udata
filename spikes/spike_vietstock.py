"""Spike: Vietstock (vietstock.vn) — stock news & analysis.

NOTE: Vietstock's internal AJAX API is CSRF-gated and /export is blocked. We do
NOT attempt those. Try the public RSS first, then static HTML.
Strategy: RSS first, fallback static HTML + trafilatura.
Run: .venv\\Scripts\\python.exe spikes\\spike_vietstock.py
"""
from __future__ import annotations

import feedparser

from _common import banner, fail, get, polite_sleep, save_sample

NAME = "vietstock"

# Vietstock historically exposes per-channel RSS under /<id>/...rss and a listing
# at vietstock.vn/rss. We probe several known channel ids + the generic page.
RSS_CANDIDATES = [
    "https://vietstock.vn/144/chung-khoan.rss",
    "https://vietstock.vn/145/chung-khoan/co-phieu.rss",
    "https://vietstock.vn/761/doanh-nghiep.rss",
    "https://vietstock.vn/rss",
    "https://vietstock.vn/830/tai-chinh.rss",
]


def try_rss() -> bool:
    banner(f"{NAME}: METHOD 1 — RSS (feedparser)")
    for url in RSS_CANDIDATES:
        r = get(url)
        head = r.content[:2000].lower()
        if r.status_code != 200 or (b"<rss" not in head and b"<feed" not in head):
            polite_sleep(1.0)
            continue
        feed = feedparser.parse(r.content)
        if not feed.entries:
            polite_sleep(1.0)
            continue
        save_sample(NAME, r.content, "xml")
        print(f"\n  WORKING FEED: {url}")
        print(f"  channel title: {feed.feed.get('title')!r}  entries: {len(feed.entries)}")
        e0 = feed.entries[0]
        print(f"  observed entry fields: {sorted(e0.keys())}")
        print("\n  --- sample entries ---")
        for e in feed.entries[:2]:
            print(f"  • title     : {e.get('title')}")
            print(f"    link      : {e.get('link')}")
            print(f"    published : {e.get('published')}")
            print(f"    author    : {e.get('author', '(none)')}")
            summary = (e.get('summary') or '').strip().replace('\n', ' ')
            print(f"    summary   : {summary[:160]}")
            print()
        return True
    fail("No RSS candidate returned parseable entries.")
    return False


def try_html() -> bool:
    banner(f"{NAME}: METHOD 2 — static HTML + trafilatura")
    r = get("https://vietstock.vn/chung-khoan.htm")
    if r.status_code != 200:
        fail(f"section status {r.status_code}")
        return False
    save_sample(NAME, r.content, "html")
    import trafilatura
    text = trafilatura.extract(r.text, include_comments=False)
    print("  trafilatura extracted chars:", len(text or ""))
    print((text or "")[:300])
    return True


if __name__ == "__main__":
    if not try_rss():
        try_html()
