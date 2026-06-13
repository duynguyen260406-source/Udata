"""Spike: VNDirect finfo-api (unauthenticated REST JSON).

Cheapest possible source if it works: public JSON, no auth, no HTML parsing.
We probe a few candidate endpoints on the finfo-api host (these are the
hidden/public endpoints the VNDirect web app calls) and report which respond
with JSON + their keys.

robots.txt is 404 for this host, so we skip a robots fetch (documented in CLAUDE.md).
Run: .venv\\Scripts\\python.exe spikes\\spike_vndirect.py
"""
from __future__ import annotations

from _common import banner, fail, get, polite_sleep, pretty, save_sample, show_keys

NAME = "vndirect"

# (label, url) — ordered. Confirmed working host is api-finfo.vndirect.com.vn
# (finfo-api.* times out from here). The ticker filter field is `tagCodes`,
# NOT `code`. Without a filter the endpoint returns the full market news stream.
CANDIDATES = [
    ("news latest (all market)", "https://api-finfo.vndirect.com.vn/v4/news?size=5&sort=newsDate:desc"),
    ("news for VCB (tagCodes)",  "https://api-finfo.vndirect.com.vn/v4/news?q=tagCodes:VCB&size=5&sort=newsDate:desc"),
    ("disclosures only",         "https://api-finfo.vndirect.com.vn/v4/news?q=newsGroup:disclosure&size=5&sort=newsDate:desc"),
]


def main() -> None:
    banner(f"{NAME}: METHOD = hidden/public JSON API (httpx)")
    saved = False
    for label, url in CANDIDATES:
        print(f"\n-- candidate: {label}")
        try:
            r = get(url)
        except Exception as e:  # noqa: BLE001
            fail(f"{label}: request error {e!r}")
            polite_sleep(1.0)
            continue
        ctype = r.headers.get("content-type", "")
        if r.status_code != 200 or "json" not in ctype:
            fail(f"{label}: status {r.status_code}, content-type {ctype!r}")
            polite_sleep(1.0)
            continue
        try:
            data = r.json()
        except Exception as e:  # noqa: BLE001
            fail(f"{label}: not valid JSON ({e!r})")
            polite_sleep(1.0)
            continue

        print(f"  top-level type: {type(data).__name__}")
        if isinstance(data, dict):
            print(f"  top-level keys: {sorted(data.keys())}")
        records = data.get("data") if isinstance(data, dict) else data
        if isinstance(records, list) and records:
            print(f"  record count in 'data': {len(records)}")
            show_keys(records, "record keys")
            print("\n  --- sample record(s) ---")
            print(pretty(records[: min(2, len(records))])[:1200])
            if not saved:
                save_sample(NAME, r.content, "json")
                saved = True
        else:
            print("  'data' empty or not a list — endpoint reachable but no records for VCB")
        polite_sleep(1.2)

    if not saved:
        print("\n  (No news/events payload saved — see per-candidate status above.)")


if __name__ == "__main__":
    main()
