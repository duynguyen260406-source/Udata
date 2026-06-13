"""Spike: CBTT (official disclosures) — HOSE / HNX / VSDC.

These official portals are the hardest tier. We probe, cheapest first:
  1. Hidden JSON API endpoints the portals' front-ends call (httpx)
  2. Static HTML landing pages (to detect JSF/ASP.NET/JS gating)
  3. (optional) Playwright render — run with:  ... spike_cbtt.py --playwright

We hit each host only 1-2 times. Goal is to CLASSIFY access method, not to crawl.
Run: .venv\\Scripts\\python.exe spikes\\spike_cbtt.py [--playwright]
"""
from __future__ import annotations

import sys

from _common import banner, fail, get, polite_sleep, pretty, save_sample, show_keys

# --- candidate hidden JSON APIs (front-end XHR endpoints) -------------------
# The HOSE endpoint below was DISCOVERED by capturing the SPA's network calls
# with Playwright (see try_playwright_capture): www.hsx.vn is an Angular SPA that
# talks to api.hsx.vn/{c,n}/api/v1/... — no auth, plain JSON. So HOSE does NOT
# actually need a browser at runtime once the endpoint is known.
HOSE_HEADERS = {"Accept": "application/json", "Origin": "https://www.hsx.vn",
                "Referer": "https://www.hsx.vn/"}
JSON_CANDIDATES = [
    ("HOSE news (api.hsx.vn)", "https://api.hsx.vn/n/api/v1/1/news?pageIndex=1&pageSize=5"),
]

# --- landing pages to classify gating --------------------------------------
HTML_PAGES = [
    ("HOSE",  "https://www.hsx.vn/Modules/Listed/Web/Disclosures"),
    ("HNX",   "https://www.hnx.vn/vi-vn/cophieu-etfs/disclosures.html"),
    ("VSDC",  "https://congbothongtin.ssc.gov.vn/faces/NewsSearch"),
]


def try_json() -> bool:
    banner("CBTT: METHOD 1 — hidden JSON API probe (httpx)")
    got = False
    for label, url in JSON_CANDIDATES:
        print(f"\n-- {label}")
        try:
            r = get(url, headers=HOSE_HEADERS)
        except Exception as e:  # noqa: BLE001
            fail(f"{label}: {e!r}")
            polite_sleep(1.0)
            continue
        ctype = r.headers.get("content-type", "")
        if r.status_code == 200 and "json" in ctype:
            try:
                data = r.json()
            except Exception as e:  # noqa: BLE001
                fail(f"{label}: status 200 but not JSON ({e!r})")
                polite_sleep(1.0)
                continue
            print(f"  JSON OK. top-level type={type(data).__name__}")
            if isinstance(data, dict):
                print(f"  envelope keys: {sorted(data.keys())}")
            # HOSE envelope: {success, message, data:{list, object, paging}}
            recs = data.get("data") if isinstance(data, dict) else data
            if isinstance(recs, dict):
                recs = recs.get("list") or recs.get("items")
            if isinstance(recs, list) and recs:
                show_keys(recs, "record keys")
                print(pretty(recs[:1])[:900])
                save_sample("cbtt_hose", r.content, "json")
                got = True
        else:
            fail(f"{label}: status {r.status_code}, content-type {ctype!r}")
        polite_sleep(1.2)
    return got


def classify_html() -> None:
    banner("CBTT: METHOD 2 — static HTML landing pages (classify gating)")
    for label, url in HTML_PAGES:
        print(f"\n-- {label}")
        try:
            r = get(url)
        except Exception as e:  # noqa: BLE001
            fail(f"{label}: {e!r}")
            polite_sleep(1.0)
            continue
        body = r.text.lower()
        markers = {
            "JSF/ADF (ViewState)": "javax.faces.viewstate" in body or "oracle" in body,
            "ASP.NET (__VIEWSTATE)": "__viewstate" in body,
            "heavy JS app (root div, few links)": body.count("<a ") < 10 and "app" in body,
        }
        detected = [k for k, v in markers.items() if v] or ["(plain HTML?)"]
        print(f"  status {r.status_code}, {len(r.content)} bytes; anchors={r.text.count('<a ')}")
        print(f"  gating signals: {detected}")
        # save the first landing page as the cbtt HTML sample if no JSON sample exists
        save_sample(f"cbtt_{label.lower()}", r.content, "html")
        polite_sleep(1.2)


def try_playwright_capture() -> None:
    """How the HOSE API was discovered: load the SPA and log its XHR/fetch calls.
    Not needed at runtime (we hit api.hsx.vn directly) — kept to document method.
    """
    banner("CBTT: METHOD 3 — Playwright XHR capture (endpoint discovery)")
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:  # noqa: BLE001
        fail(f"playwright import failed: {e!r}")
        return
    url = "https://www.hsx.vn/Modules/Listed/Web/Disclosures"
    xhr: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="udata-survey/0.1 (research; contact: duynguyen260406@gmail.com)"
        )
        page.on("request", lambda r: xhr.append(f"{r.method} {r.url}")
                if r.resource_type in ("xhr", "fetch") else None)
        page.goto(url, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(3000)
        save_sample("cbtt_hose_rendered", page.content(), "html")
        browser.close()
    print(f"  captured {len(xhr)} XHR/fetch calls (the data API lives among these):")
    for line in xhr:
        print("   ", line)


if __name__ == "__main__":
    use_pw = "--playwright" in sys.argv
    if not try_json():
        classify_html()
    else:
        classify_html()  # still classify HNX/VSDC gating for the matrix
    if use_pw:
        try_playwright_capture()
