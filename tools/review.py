#!/usr/bin/env python3
# tools/review.py: the author's review marks. "mark <id> [note]" records a review of one object;
# "check" confirms every mark names an object that exists. The register itself is built from the objects.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import json, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402  (main is guarded; importing only reads the object list)

def objects():
    return {oid: (kind, title) for oid, kind, title in build.review_objects()}

def main():
    f = ROOT / "data" / "review.json"
    R = json.loads(f.read_text(encoding="utf-8"))
    objs = objects()
    if len(sys.argv) >= 3 and sys.argv[1] == "mark":
        oid, note = sys.argv[2], " ".join(sys.argv[3:])
        if oid not in objs:
            near = [o for o in objs if oid.lower() in o.lower()][:8]
            sys.exit(f"no object {oid}" + (f"; did you mean: {', '.join(near)}" if near else ""))
        R["reviewed"][oid] = {"date": date.today().isoformat()} | ({"note": note} if note else {})
        f.write_text(json.dumps(R, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"marked {oid} as reviewed; next: python3 tools/build.py, then bash ops/verify.sh")
        return
    if len(sys.argv) >= 2 and sys.argv[1] == "check":
        stray = [o for o in R["reviewed"] if o not in objs]
        dupes = len(build.review_objects()) - len(objs)
        for o in stray:
            print(f"a mark names no object: {o}")
        if dupes:
            print(f"{dupes} object identifiers are repeated")
        print(f"review: {len(R['reviewed'])} of {len(objs)} objects reviewed")
        sys.exit(1 if stray or dupes else 0)
    sys.exit("usage: python3 tools/review.py mark <id> [note] | check")

if __name__ == "__main__":
    main()
