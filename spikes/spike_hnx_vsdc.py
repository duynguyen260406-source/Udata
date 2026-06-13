"""Spike: HNX disclosures + VSDC (SSC portal) — confirmed strategies.

HNX (hnx.vn) — CONFIRMED: ASP.NET SPA với POST endpoints ẩn.
  Trang CBTT: https://hnx.vn/vi-vn/thong-tin-cong-bo-ny-hnx.html
              https://hnx.vn/vi-vn/thong-tin-cong-bo-up-hnx.html

  Endpoints (tất cả POST, không cần auth, không cần JS):
    /ModuleArticles/ArticlesCPEtfs/NextPageTinCPNY          — danh sách (Niêm yết từ HNX)
    /ModuleArticles/ArticlesCPEtfs/NextPageTinCPNY_CBTCPH   — danh sách (từ tổ chức phát hành)
    /ModuleArticles/ArticlesCPEtfs/PopupTinCongBoDetail      — nội dung chi tiết 1 bài
    /ModuleArticles/ArticlesCPEtfs/ArticlesFileAttach        — link PDF đính kèm

  Strategy:
    1. POST NextPageTinCPNY tăng pPageIndex → parse HTML lấy rows (ID, ngày, mã, tiêu đề)
    2. POST ArticlesFileAttach?pArticlesID={id} → parse HTML lấy link PDF
    3. Download PDF từ owa.hnx.vn/ftp/...

VSDC / congbothongtin.ssc.gov.vn — PENDING: Oracle ADF, cần Playwright.
  Các REST endpoint đã probe → tất cả 404.
  Playwright render được 31 tables nhưng XHR chỉ thấy JS file, không phải data call.
  → Cần dùng Chrome DevTools thủ công để capture ADF partial-page-refresh requests.

Run:
  .venv\\Scripts\\python.exe spikes\\spike_hnx_vsdc.py            # HNX httpx only
  .venv\\Scripts\\python.exe spikes\\spike_hnx_vsdc.py --playwright  # + VSDC Playwright
"""
from __future__ import annotations

import re
import sys

import httpx
from selectolax.parser import HTMLParser

from _common import (
    HEADERS,
    banner,
    fail,
    polite_sleep,
    pretty,
    save_sample,
)

USE_PW = "--playwright" in sys.argv

# ---------------------------------------------------------------------------
# HNX helpers
# ---------------------------------------------------------------------------

HNX_BASE = "https://hnx.vn"

HNX_HEADERS = {
    "Accept": "text/html, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://hnx.vn/vi-vn/thong-tin-cong-bo-ny-hnx.html",
    "Origin": "https://hnx.vn",
}

# Endpoints đã xác nhận qua browser network capture:
#   NextPageTinCPNY_CBTCPH  — CBTT từ tổ chức phát hành (137k+ records)  ← tab chính
#   NextPageTinCPNY_LTHQ    — Lịch tổ chức họp
#   NextPageTinTCPHChuaGD_NY — TCPH chưa giao dịch
# Params: pNumPage, pAction, pNhomTin, pTieuDeTin, pMaChungKhoan, pFromDate, pToDate, pOrderBy


def post_hnx(path: str, data: dict) -> httpx.Response:
    """POST to HNX with SSL verify=False (their cert chain is broken)."""
    h = {**HEADERS, **HNX_HEADERS}
    url = HNX_BASE + path
    body = "&".join(f"{k}={v}" for k, v in data.items())
    with httpx.Client(headers=h, timeout=30.0, follow_redirects=True, verify=False) as c:
        r = c.post(url, content=body)
    print(f"  POST {url}\n    -> {r.status_code} {r.headers.get('content-type','?')} "
          f"({len(r.content)} bytes)")
    return r


def parse_hnx_list(html: str) -> list[dict]:
    """Extract rows từ HTML bảng danh sách CBTT của HNX.

    Cấu trúc bảng (NextPageTinCPNY_CBTCPH):
      STT | Ngày đăng tin | Mã CK | Tên TCPH | Tiêu đề tin | File đính kèm
    """
    tree = HTMLParser(html)
    rows = tree.css("table#_tableDatas tbody tr")
    records = []
    for row in rows:
        cells = row.css("td")
        if len(cells) < 5:
            continue
        title_link = row.css_first("a.hrefViewDetail")
        file_link = row.css_first("a.icon-FileAttach")
        article_id = None
        if title_link:
            m = re.search(r"funcViewDetailArticlesByID\((\d+)", title_link.attributes.get("onclick", ""))
            if m:
                article_id = int(m.group(1))
        ticker_link = cells[2].css_first("a")
        # col index: 0=STT, 1=date, 2=ticker, 3=issuer_name, 4=title, 5=attachment
        records.append({
            "article_id": article_id,
            "published_at": cells[1].text(strip=True),
            "ticker": cells[2].text(strip=True),
            "ticker_url": ticker_link.attributes.get("href") if ticker_link else None,
            "issuer_name": cells[3].text(strip=True),
            "title": cells[4].text(strip=True),
            "has_attachment": file_link is not None,
        })
    return records


def parse_hnx_attachments(html: str) -> list[str]:
    """Extract PDF URLs từ HTML popup file đính kèm."""
    tree = HTMLParser(html)
    links = tree.css("div.divFileAttach a[href]")
    return [a.attributes["href"] for a in links if a.attributes.get("href", "").endswith(".pdf")]


# ---------------------------------------------------------------------------
# HNX: Step 1 — lấy danh sách CBTT (nhiều trang)
# ---------------------------------------------------------------------------

def fetch_hnx_list(pages: int = 2) -> list[dict]:
    banner(f"HNX: STEP 1 — danh sách CBTT từ TCPH (fetch {pages} trang)")
    all_records: list[dict] = []

    for page_idx in range(1, pages + 1):
        print(f"\n-- trang {page_idx}")
        try:
            r = post_hnx(
                "/ModuleArticles/ArticlesCPEtfs/NextPageTinCPNY_CBTCPH",
                {
                    "pNumPage": page_idx,
                    "pAction": 0,
                    "pNhomTin": "",
                    "pTieuDeTin": "",
                    "pMaChungKhoan": "",
                    "pFromDate": "",
                    "pToDate": "",
                    "pOrderBy": "",
                },
            )
        except Exception as e:  # noqa: BLE001
            fail(f"page {page_idx}: {e!r}")
            polite_sleep(1.5)
            continue

        if r.status_code != 200:
            fail(f"status {r.status_code}")
            polite_sleep(1.5)
            continue

        if page_idx == 1:
            save_sample("hnx_list_page1", r.content, "html")

        records = parse_hnx_list(r.text)

        # Extract tổng số bản ghi từ paging div (chỉ trang 1)
        if page_idx == 1:
            m = re.search(r"Tổng số ([\d.]+) bản ghi", r.text)
            if m:
                print(f"  Tổng số bản ghi trên server: {m.group(1)}")

        print(f"  parsed {len(records)} records")
        for rec in records[:3]:
            print(f"    [{rec['article_id']}] {rec['published_at']}  {rec['ticker']:<12}  {rec['title'][:60]}")
        all_records.extend(records)
        polite_sleep(1.2)

    print(f"\n  Total records fetched: {len(all_records)}")
    return all_records


# ---------------------------------------------------------------------------
# HNX: Step 2 — lấy link PDF đính kèm cho từng bài
# ---------------------------------------------------------------------------

def fetch_hnx_attachments(records: list[dict], max_items: int = 3) -> None:
    banner(f"HNX: STEP 2 — file đính kèm (sample {max_items} bài có attachment)")
    candidates = [r for r in records if r["has_attachment"] and r["article_id"]][:max_items]

    if not candidates:
        fail("Không có bài nào có file đính kèm trong danh sách")
        return

    for rec in candidates:
        print(f"\n-- article_id={rec['article_id']}  {rec['title'][:60]}")
        try:
            r = post_hnx(
                "/ModuleArticles/ArticlesCPEtfs/ArticlesFileAttach",
                {"pArticlesID": rec["article_id"]},
            )
        except Exception as e:  # noqa: BLE001
            fail(f"{e!r}")
            polite_sleep(1.0)
            continue

        if r.status_code != 200:
            fail(f"status {r.status_code}")
            polite_sleep(1.0)
            continue

        pdfs = parse_hnx_attachments(r.text)
        if pdfs:
            print(f"  PDFs found: {len(pdfs)}")
            for url in pdfs:
                print(f"    {url}")
            save_sample(f"hnx_attach_{rec['article_id']}", r.content, "html")
        else:
            print("  (no PDF links found in response)")
            print(f"  raw preview: {r.text[:300]}")
        polite_sleep(1.2)


# ---------------------------------------------------------------------------
# HNX: Step 3 — xem nội dung chi tiết 1 bài
# ---------------------------------------------------------------------------

def fetch_hnx_detail(article_id: int) -> None:
    banner(f"HNX: STEP 3 — nội dung chi tiết bài {article_id}")
    try:
        r = post_hnx(
            "/ModuleArticles/ArticlesCPEtfs/PopupTinCongBoDetail",
            {"pArticlesID": article_id, "pFileAttach": 1},
        )
    except Exception as e:  # noqa: BLE001
        fail(f"{e!r}")
        return

    if r.status_code != 200:
        fail(f"status {r.status_code}")
        return

    tree = HTMLParser(r.text)
    title = tree.css_first(".Box-TieuDe label")
    body = tree.css_first(".Box-Noidung")
    print(f"  title : {title.text(strip=True) if title else '(not found)'}")
    print(f"  body  : {body.text(strip=True)[:400] if body else '(not found)'}")
    save_sample(f"hnx_detail_{article_id}", r.content, "html")


# ---------------------------------------------------------------------------
# VSDC — Playwright (cần --playwright flag)
# ---------------------------------------------------------------------------

def try_vsdc_playwright() -> None:
    """VSDC dùng Oracle ADF — render bằng Playwright, scrape table, capture network."""
    banner("VSDC: Playwright render + table scrape + network capture")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fail("playwright not installed — pip install playwright && playwright install chromium")
        return

    url = "https://congbothongtin.ssc.gov.vn/faces/NewsSearch"
    network_calls: list[tuple[str, str, int]] = []  # (method, url, size)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="udata-survey/0.1 (research; contact: duynguyen260406@gmail.com)"
        )

        def on_response(resp):
            if resp.request.resource_type in ("xhr", "fetch", "document"):
                try:
                    size = len(resp.body())
                except Exception:  # noqa: BLE001
                    size = -1
                network_calls.append((resp.request.method, resp.url, size))

        page.on("response", on_response)

        print(f"  Loading {url} (Oracle ADF — slow) ...")
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:  # noqa: BLE001
            fail(f"goto timeout: {e!r}")
            browser.close()
            return

        page.wait_for_timeout(5000)
        rendered = page.content()
        save_sample("vsdc_rendered", rendered.encode(), "html")

        # Scrape tables từ rendered HTML
        tree = HTMLParser(rendered)
        tables = tree.css("table")
        print(f"\n  Tables found in rendered page: {len(tables)}")
        found_data = False
        for i, tbl in enumerate(tables):
            rows = tbl.css("tr")
            if len(rows) < 2:
                continue
            # Chỉ in table có nội dung thực (text > 10 chars per cell)
            sample_cells = [td.text(strip=True) for td in rows[1].css("td, th")]
            if any(len(c) > 10 for c in sample_cells):
                print(f"\n  Table {i} ({len(rows)} rows) — sample:")
                for row in rows[:4]:
                    cells = [td.text(strip=True)[:50] for td in row.css("td, th")]
                    if any(cells):
                        print(f"    {cells}")
                found_data = True

        # Screenshot
        try:
            page.screenshot(path="spikes/samples/vsdc_screenshot.png")
            print("\n  Screenshot: spikes/samples/vsdc_screenshot.png")
        except Exception:  # noqa: BLE001
            pass

        browser.close()

    print(f"\n  Network calls captured ({len(network_calls)}):")
    for method, url, size in network_calls:
        print(f"    [{method}] {size:>8} bytes  {url[:100]}")

    if not found_data:
        print("\n  NOTE: Không tìm thấy table có dữ liệu — VSDC cần thêm interaction")
        print("        Dùng Chrome DevTools thủ công: Network tab → filter Fetch/XHR → click Search")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("SPIKE: HNX + VSDC — confirmed strategies")
    print(f"Playwright mode: {'ON' if USE_PW else 'OFF (pass --playwright to enable VSDC)'}")
    print("=" * 70)

    # --- HNX (httpx POST, no JS needed) ---
    records = fetch_hnx_list(pages=2)
    polite_sleep(1.0)

    if records:
        fetch_hnx_attachments(records, max_items=3)
        polite_sleep(1.0)

        # Xem chi tiết bài đầu tiên có article_id
        first = next((r for r in records if r["article_id"]), None)
        if first:
            fetch_hnx_detail(first["article_id"])

    # --- VSDC (cần Playwright) ---
    polite_sleep(1.5)
    if USE_PW:
        try_vsdc_playwright()
    else:
        print("\n  VSDC: Oracle ADF — chạy với --playwright để thử browser scrape")
        print("        Hoặc dùng Chrome DevTools thủ công để tìm ADF data endpoint")
