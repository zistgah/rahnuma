#!/usr/bin/env python3
# tools/syllabus_fetch.py: fetches each board's syllabus from its official site, finds the subject documents
# by regular expression, reads them, and maps them onto the guide's keywords and our syllabus's modules.
# Writes docs/syllabus-map.json with the official link, a SHA-256 of what was read, the page count and
# the matches, and never a word of any syllabus. Run it before publishing; the page reads the result.
#
#   python3 tools/syllabus_fetch.py                 every board in data/syllabi.json
#   python3 tools/syllabus_fetch.py --only icse cbse
#
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import argparse, hashlib, html, io, json, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Rahnuma syllabus linker (+https://zistgah.org/rahnuma/)"}
FOLLOW = re.compile(r"syllab|curricul|regulation|subject|scheme of stud", re.I)
SUBJECT = re.compile(r"computer|informatics|information (technology|practices)|artificial intelligence|mathematic|physics|robotic", re.I)
CLASS = [("6 to 8", re.compile(r"class[\s_-]*(vi|vii|viii|6|7|8)\b", re.I)), ("9 and 10", re.compile(r"class[\s_-]*(ix|x|9|10)\b|icse|secondary", re.I)),
         ("11 and 12", re.compile(r"class[\s_-]*(xi|xii|11|12)\b|\bisc\b|senior", re.I))]

def get(url, limit=25_000_000):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read(limit), r.headers.get("Content-Type", "")

def links(page, base):
    for href, text in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page, re.I | re.S):
        yield urllib.parse.urljoin(base, html.unescape(href)), re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()

def pages_of(data, ctype):
    if data[:4] == b"%PDF" or "pdf" in ctype:
        from pypdf import PdfReader
        return [p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages]
    return [re.sub(r"<[^>]+>", " ", data.decode("utf-8", "replace"))]

def documents(board):
    """The subject documents of one board: a direct document, or found by regex from its official page."""
    url = board["url"]
    if url.lower().endswith(".pdf"):
        return [(url, board["name"])]
    host = urllib.parse.urlparse(url).netloc
    found, seen, queue = [], {url}, [(url, 0)]
    while queue and len(seen) < 40:
        u, depth = queue.pop(0)
        try:
            data, ctype = get(u, 5_000_000)
        except Exception as e:
            print(f"  could not open {u}: {e}", file=sys.stderr)
            continue
        for href, text in links(data.decode("utf-8", "replace"), u):
            if urllib.parse.urlparse(href).netloc != host or href in seen:
                continue
            seen.add(href)
            label = f"{text} {href}"
            if href.lower().split("?")[0].endswith(".pdf") and SUBJECT.search(label):
                found.append((href, text or href.rsplit("/", 1)[-1]))
            elif depth < 2 and FOLLOW.search(label):
                queue.append((href, depth + 1))
    return found[:12]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--registry", default=str(ROOT / "data" / "syllabi.json"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "syllabus-map.json"))
    a = ap.parse_args()
    boards = json.loads(Path(a.registry).read_text(encoding="utf-8"))["boards"]
    rules = json.loads((ROOT / "data" / "correlation.json").read_text(encoding="utf-8"))["rules"]
    mods = json.loads((ROOT / "data" / "standard-syllabus.json").read_text(encoding="utf-8"))["modules"]
    out = {"note": "Derived links only: the official address, a SHA-256 of what was read, page numbers and the guide's own keyword labels. No syllabus text is stored.",
           "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "documents": [], "errors": []}
    old = Path(a.out)
    for b in boards:
        if a.only and b["id"] not in a.only:
            continue
        print(f"{b['id']}: {b['url']}")
        try:
            docs = documents(b)
        except Exception as e:
            out["errors"].append({"board": b["id"], "error": str(e)[:200]})
            continue
        if not docs:
            out["errors"].append({"board": b["id"], "error": "no subject document found from the official page"})
        for url, title in docs:
            try:
                data, ctype = get(url)
                pages = pages_of(data, ctype)
            except Exception as e:
                out["errors"].append({"board": b["id"], "url": url, "error": str(e)[:200]})
                continue
            matches = []
            for r in rules:
                rx = re.compile(r["pattern"], re.I)
                hit = [i + 1 for i, t in enumerate(pages) if rx.search(t)]
                if hit:
                    matches.append({"rule": r["id"], "label": r["label"], "pages": hit[:12], "target": r["target"],
                                    "modules": [m["id"] for m in mods if r["target"] in m["chapters"]]})
            hint = next((c for c, rx in CLASS if rx.search(f"{title} {url}")), "")
            out["documents"].append({"board": b["id"], "title": title[:90], "url": url, "sha256": hashlib.sha256(data).hexdigest(),
                                     "pages": len(pages), "fetched_utc": out["generated_utc"], "class_hint": hint, "matches": matches})
            print(f"  {len(pages):4d} pages, {len(matches):2d} topics linked: {title[:60]}")
    if a.only and old.is_file():
        keep = [d for d in json.loads(old.read_text(encoding="utf-8")).get("documents", []) if d["board"] not in a.only]
        out["documents"] = keep + out["documents"]
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"syllabus map: {len(out['documents'])} documents, {len(out['errors'])} not reached; written to {a.out}")

if __name__ == "__main__":
    main()
