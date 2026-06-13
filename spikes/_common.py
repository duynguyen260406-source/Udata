"""Shared helpers for survey-week spikes (throwaway).

Each spike is independent (targets one source) but reuses these tiny utilities so
they all send the same polite User-Agent and save raw samples the same way.

Politeness rules for the survey week:
  * Identify ourselves with a contact User-Agent.
  * Hit each endpoint only 1-2 times. NEVER loop/crawl.
  * Small delay between the (few) calls.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

# Windows consoles default to cp1252 and choke on Vietnamese text. Force UTF-8
# so spikes can print sample headlines without UnicodeEncodeError.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001
        pass

CONTACT = "duynguyen260406@gmail.com"
UA = f"udata-survey/0.1 (research bot; contact: {CONTACT})"

HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "vi,en;q=0.8",
}

SAMPLES_DIR = Path(__file__).resolve().parent / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


def get(url: str, *, headers: dict | None = None, timeout: float = 20.0, **kw) -> httpx.Response:
    """Single polite GET. Raises for nothing — caller inspects status."""
    h = dict(HEADERS)
    if headers:
        h.update(headers)
    with httpx.Client(headers=h, timeout=timeout, follow_redirects=True) as c:
        r = c.get(url, **kw)
    print(f"  GET {url}\n    -> {r.status_code} {r.headers.get('content-type','?')} "
          f"({len(r.content)} bytes)")
    return r


def polite_sleep(seconds: float = 1.5) -> None:
    time.sleep(seconds)


def save_sample(name: str, content: bytes | str, ext: str) -> Path:
    """Save one raw sample to spikes/samples/<name>.<ext> and return the path."""
    path = SAMPLES_DIR / f"{name}.{ext}"
    mode = "wb" if isinstance(content, bytes) else "w"
    enc = None if isinstance(content, bytes) else "utf-8"
    with open(path, mode, encoding=enc) as f:
        f.write(content)
    print(f"  saved raw sample -> {path}  ({path.stat().st_size} bytes)")
    return path


def show_keys(obj, label: str = "keys") -> None:
    """Print the observed keys of a JSON object (or of the first list element)."""
    if isinstance(obj, list) and obj:
        obj = obj[0]
    if isinstance(obj, dict):
        print(f"  observed {label}: {sorted(obj.keys())}")
    else:
        print(f"  (not a dict; type={type(obj).__name__})")


def banner(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def fail(msg: str) -> None:
    print(f"  [NOT OBTAINED] {msg}", file=sys.stderr)


def pretty(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def pdf_probe(path, head_chars: int = 200) -> dict:
    """Open a PDF with pdfplumber: count pages, decide if text is selectable
    (else likely a scan needing OCR), and grab the first chars of text.
    Does NOT run OCR — that's a later pipeline concern.
    """
    import pdfplumber

    texts = []
    with pdfplumber.open(path) as pdf:
        n_pages = len(pdf.pages)
        for page in pdf.pages[:3]:          # sample first 3 pages only
            texts.append(page.extract_text() or "")
    full = "\n".join(texts).strip()
    selectable = len(full) >= 20            # <20 chars over 3 pages -> treat as scan
    return {"pages": n_pages, "selectable": selectable, "head": full[:head_chars]}
