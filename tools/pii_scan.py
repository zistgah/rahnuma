#!/usr/bin/env python3
# tools/pii_scan.py: finds personal data in the guide's sources: email addresses, telephone numbers,
# identity and account numbers, payment cards and dates of birth. Prints each find with its place,
# the match masked; exits 1 if anything is found beyond the published identifiers in data/pii-allow.json.
# Also usable across the estate: python3 tools/pii_scan.py <folder> [<folder> ...]
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = [
    ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")),
    ("telephone", re.compile(r"(?<![\w.-])(?:\+91[\s-]?|0)?[6-9]\d{9}(?![\w.-])")),
    ("telephone", re.compile(r"\+\d{1,3}[\s-]\d{2,5}[\s-]\d{3,5}[\s-]?\d{3,5}")),
    ("Aadhaar-like number", re.compile(r"(?<!\d)\d{4} \d{4} \d{4}(?!\d)")),
    ("PAN-like number", re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")),
    ("IFSC-like code", re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")),
    ("date of birth", re.compile(r"(?i)\b(?:date of birth|born on|d\.o\.b\.?)\b[:\s]*\d")),
]
CARD = re.compile(r"(?<![\d.])(?:\d[ -]?){13,19}(?![\d.])")
SAFE_EMAIL = re.compile(r"(?:@example\.(?:com|org|net)|@users\.noreply\.github\.com|^git@github\.com)$", re.I)

def luhn(digits):
    s, alt = 0, False
    for d in reversed(digits):
        n = int(d)
        if alt:
            n = n * 2 - 9 if n > 4 else n * 2
        s, alt = s + n, not alt
    return s % 10 == 0

def scan(paths, allow):
    finds = []
    for base in paths:
        files = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]
        for f in files:
            if any(x in f.parts for x in (".git", "node_modules", "v1", "fonts")) or f.suffix.lower() in {".pdf", ".png", ".jpg", ".woff2", ".svg", ".ots", ".gz"}:
                continue
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            for n, line in enumerate(lines, 1):
                for kind, rx in PATTERNS:
                    for m in rx.finditer(line):
                        t = m.group(0)
                        if any(a in t for a in allow) or (kind == "email" and SAFE_EMAIL.search(t)):
                            continue
                        finds.append((f, n, kind, t))
                for m in CARD.finditer(line):
                    d = re.sub(r"\D", "", m.group(0))
                    if 13 <= len(d) <= 19 and d[0] != "0" and luhn(d) and len(set(d)) > 2:
                        finds.append((f, n, "payment-card-like number", m.group(0)))
    return finds

def main():
    allow = json.loads((ROOT / "data" / "pii-allow.json").read_text(encoding="utf-8"))["allow"]
    args = [Path(a) for a in sys.argv[1:]]
    paths = args or [ROOT / "content", ROOT / "data", ROOT / "examples", ROOT / "README.md", ROOT / "CONTEXT.md", ROOT / "CONTRACT.md", ROOT / "docs" / "rahnuma.md"]
    finds = scan([p for p in paths if p.exists()], allow)
    for f, n, kind, t in finds:
        masked = t[:2] + "*" * max(0, len(t) - 4) + t[-2:]
        print(f"{f}:{n}: {kind}: {masked}")
    print(f"pii_scan: {len(finds)} find(s)")
    sys.exit(1 if finds else 0)

if __name__ == "__main__":
    main()
