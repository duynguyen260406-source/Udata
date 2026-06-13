"""Spike: compliance recon — fetch robots.txt for every source domain.

ONE request per host. Saves raw robots.txt to spikes/samples/robots/<name>.txt
and prints the User-agent groups + Disallow rules so we can judge whether the
paths we collect are permitted. NOT crawling — this only reads the policy file.

Run: .venv\\Scripts\\python.exe spikes\\spike_compliance.py
"""
from __future__ import annotations

from pathlib import Path

import httpx

from _common import HEADERS, banner, fail, polite_sleep

OUT = Path(__file__).resolve().parent / "samples" / "robots"
OUT.mkdir(parents=True, exist_ok=True)

# (name, robots_url). Multiple hosts per logical source where relevant.
HOSTS = [
    ("vndirect_www",      "https://www.vndirect.com.vn/robots.txt"),
    ("vndirect_apifinfo", "https://api-finfo.vndirect.com.vn/robots.txt"),
    ("vneconomy",         "https://vneconomy.vn/robots.txt"),
    ("tinnhanhchungkhoan", "https://www.tinnhanhchungkhoan.vn/robots.txt"),
    ("vietstock",         "https://vietstock.vn/robots.txt"),
    ("baodautu",          "https://baodautu.vn/robots.txt"),
    ("hsx_www",           "https://www.hsx.vn/robots.txt"),
    ("hsx_api",           "https://api.hsx.vn/robots.txt"),
    ("hnx",               "https://www.hnx.vn/robots.txt"),
    ("vsdc",              "https://congbothongtin.ssc.gov.vn/robots.txt"),
]

# Keywords that matter for what WE collect (news/disclosure/rss/api/export).
RELEVANT = ("rss", "api", "news", "tin", "export", "disclosure", "cong-bo",
            "search", "/", "feed")


def summarize(text: str) -> None:
    """Print User-agent groups + their Disallow/Allow lines, flag AI-bot blocks."""
    ua = "*"
    groups: dict[str, list[str]] = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key == "user-agent":
            ua = val
            groups.setdefault(ua, [])
        elif key in ("disallow", "allow", "crawl-delay", "sitemap"):
            groups.setdefault(ua, []).append(f"{key.title()}: {val}")
    # flag explicit AI/anthropic blocks
    ai_blocked = [u for u in groups if any(b in u.lower()
                  for b in ("claude", "anthropic", "gptbot", "ccbot", "ai"))]
    if ai_blocked:
        print(f"  [!] explicit AI/bot UA groups present: {ai_blocked}")
    for u, rules in groups.items():
        dis = [r for r in rules if r.lower().startswith("disallow")]
        print(f"  UA={u!r}  ({len(dis)} Disallow)")
        for r in rules:
            low = r.lower()
            if low.startswith(("disallow", "allow")) and any(k in low for k in RELEVANT):
                print(f"      {r}")


def main() -> None:
    for name, url in HOSTS:
        banner(f"{name}  —  {url}")
        verify = True
        for attempt in (1, 2):
            try:
                with httpx.Client(headers=HEADERS, timeout=20.0,
                                  follow_redirects=True, verify=verify) as c:
                    r = c.get(url)
                ct = r.headers.get("content-type", "")
                print(f"  -> {r.status_code} {ct} ({len(r.content)} bytes)"
                      + ("" if verify else "  [TLS verify DISABLED to READ policy only]"))
                if r.status_code == 200 and "html" not in ct.lower():
                    (OUT / f"{name}.txt").write_bytes(r.content)
                    summarize(r.text)
                elif r.status_code == 404:
                    print("  robots.txt 404 -> no rules published (treat as 'no robots policy')")
                else:
                    print(f"  unexpected: status {r.status_code}, content-type {ct!r}")
                break
            except Exception as e:  # noqa: BLE001
                if "CERTIFICATE" in repr(e).upper() and verify:
                    fail(f"{name}: TLS error, retrying once with verify off to read policy")
                    verify = False
                    polite_sleep(1.0)
                    continue
                fail(f"{name}: {e!r}")
                break
        polite_sleep(1.2)


if __name__ == "__main__":
    main()
