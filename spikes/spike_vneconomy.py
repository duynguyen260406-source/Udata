"""Spike: VnEconomy (vneconomy.vn) — stock/finance news.

Strategy cheap -> expensive:
  1. RSS via feedparser  <-- try first
  2. (fallback) static HTML + trafilatura for one article body

Run: .venv\\Scripts\\python.exe spikes\\spike_vneconomy.py
"""
from __future__ import annotations

import feedparser

from _common import HEADERS, banner, fail, get, polite_sleep, save_sample

NAME = "vneconomy"

# Candidate RSS feeds (VnEconomy exposes per-section .rss). We try a few and
# keep the first that yields entries.
RSS_CANDIDATES = [
    "https://vneconomy.vn/chung-khoan.rss",
    "https://vneconomy.vn/tai-chinh.rss",
    "https://vneconomy.vn/rss/home.rss",
    "https://vneconomy.vn/rss.htm",
]


def try_rss() -> bool:
    banner(f"{NAME}: METHOD 1 — RSS (feedparser)")
    for url in RSS_CANDIDATES:
        r = get(url)
        if r.status_code != 200 or b"<rss" not in r.content[:2000].lower() and b"<feed" not in r.content[:2000].lower():
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
    banner(f"{NAME}: METHOD 2 — static HTML homepage probe")
    r = get("https://vneconomy.vn/chung-khoan.htm")
    if r.status_code != 200:
        fail(f"homepage status {r.status_code}")
        return False
    save_sample(NAME, r.content, "html")
    # selectolax quick title scan
    from selectolax.parser import HTMLParser
    tree = HTMLParser(r.text)
    links = [a for a in tree.css("a") if a.attributes.get("href", "").endswith(".htm")]
    print(f"  found {len(links)} .htm <a> links on section page (manual inspection needed)")
    print("  first 3 anchor texts:")
    for a in links[:3]:
        print("   •", (a.text() or "").strip()[:80], "->", a.attributes.get("href"))
    return True


if __name__ == "__main__":
    if not try_rss():
        try_html()
