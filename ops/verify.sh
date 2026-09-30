#!/usr/bin/env bash
# ops/verify.sh: checks every clause of CONTRACT.md and prints PASS, FAIL or UNJUDGED for each.
# Exit 0 when all pass, 1 when any fails, 3 when none fails but a check could not be judged.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
command -v python3 >/dev/null 2>&1 || { echo "UNJUDGED  python3 is not installed"; exit 3; }
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C.UTF-8 PYTHONIOENCODING=utf-8
exec python3 - <<'PYEOF'
import hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
LINE = "© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI."
GPL_SHA = "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"
results = []

def report(cid, text, status, details=()):
    results.append(status)
    print(f"  {status:8s} {cid}  {text}")
    for d in list(details)[:12]:
        print(f"           {d}")

def sha(b):
    return hashlib.sha256(b).hexdigest()

def files():
    """The files that make up the repository: git's view when this is a clone, else the tree."""
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             capture_output=True, check=True, cwd=ROOT).stdout.decode("utf-8")
        if out:
            return sorted({p for p in out.split("\0") if p and (ROOT / p).is_file()})
    except Exception:
        pass
    found = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = Path(dirpath).relative_to(ROOT)
        dirnames[:] = [d for d in dirnames if d != ".git" and str(rel / d) != "tools/node_modules"]
        found += [str(rel / f) if str(rel) != "." else f for f in filenames]
    return sorted(found)

FILES = files()

def text(p):
    try:
        return (ROOT / p).read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        return None

try:
    BUILD = json.loads((ROOT / "docs" / "BUILD.json").read_text(encoding="utf-8"))
except Exception:
    BUILD = None

print("Rahnuma: contract verification")

# R01 copyright and SPDX
need_line = [p for p in FILES if re.match(r"^(content/.*\.md|examples/.*|tools/[^/]*\.(py|mjs|css|html)|ops/.*\.sh|vendor/README\.md|"
                                          r"(README|CONTRACT|CONTEXT|AGENTS|PROVENANCE)\.md|docs/(index\.html|rahnuma\.md))$", p)
             and not p.endswith(".uhin")]
bad = [p for p in need_line if LINE not in (text(p) or "")]
bad += [p + " (no SPDX line)" for p in FILES if re.search(r"\.(py|sh|mjs|c)$", p) and not p.startswith(("tools/node_modules", "attest/", "provenance/", "vendor/"))
        and "SPDX-License-Identifier: GPL-3.0-or-later" not in (text(p) or "")]
report("R01", "every source carries the copyright line; every script its SPDX line", "FAIL" if bad else "PASS", bad)

# R02 affiliation
needle = "independent " + "researcher"
bad = [p for p in FILES if not p.startswith(("data/estate-snapshot.json", "LICENSE")) and needle in (text(p) or "").lower()]
report("R02", "no affiliation other than AyeAI is claimed", "FAIL" if bad else "PASS", bad)

# R03 executed examples reproduce their printed output
if BUILD is None:
    report("R03", "every executed example reproduces the output printed in the guide", "FAIL", ["docs/BUILD.json is missing"])
else:
    bad, unjudged = [], []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", LC_ALL="C.UTF-8", PYTHONIOENCODING="utf-8")
    for r in BUILD.get("runs", []):
        missing = [t for t in r.get("needs", []) if not shutil.which(t)]
        if missing:
            unjudged.append(f"{', '.join(missing)} absent: {r['cmd'][:60]}")
            continue
        p = subprocess.run(r["cmd"], shell=True, cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
        if p.returncode != 0 or sha(p.stdout.encode("utf-8")) != r["sha256"]:
            bad.append(f"differs (exit {p.returncode}): {r['cmd'][:70]}")
    for leftover in (".work", ".work-ident"):
        if (ROOT / leftover).exists():
            bad.append(f"left behind: {leftover}")
    status = "FAIL" if bad else ("UNJUDGED" if unjudged else "PASS")
    report("R03", f"every executed example reproduces the output printed in the guide ({len(BUILD.get('runs', []))} runs)", status, bad + unjudged)

# R04 the guide was built from these sources
if BUILD is None:
    report("R04", "every input's hash matches docs/BUILD.json", "FAIL", ["docs/BUILD.json is missing"])
else:
    bad = []
    for p, h in BUILD.get("inputs", {}).items():
        f = ROOT / p
        if not f.is_file():
            bad.append(f"missing: {p}")
        elif sha(f.read_bytes()) != h:
            bad.append(f"changed since the build: {p}")
    recorded = set(BUILD.get("inputs", {}))
    for p in FILES:
        if re.match(r"^(content/[^/]*\.md|examples/[^/]+|data/[^/]*\.(json|csv|md)|data/logs/[^/]+|tools/[^/]*\.(py|mjs|html|css)|vendor/.+)$", p) and p not in recorded:
            bad.append(f"not in the build: {p}")
    report("R04", "every input's hash matches docs/BUILD.json", "FAIL" if bad else "PASS", bad)

# R05 dashes
bad = []
skip = ("LICENSE", "data/estate-snapshot.json", "docs/fonts/", "attest/", "provenance/", "MANIFEST", "vendor/chintamani/", "vendor/urdu-ilm/")
for p in FILES:
    if p.startswith(skip) or p.endswith(".csv"):
        continue
    t = text(p)
    if t is None:
        continue
    for n, ln in enumerate(t.splitlines(), 1):
        if "\u2014" in ln:
            bad.append(f"{p}:{n} em dash")
        if "\u2013" in ln and not (ln.count("\u2013") == 1 and "1993\u20132026 Abhishek Choudhary" in ln):
            bad.append(f"{p}:{n} en dash outside the copyright line")
report("R05", "no em dash; an en dash only inside the copyright line", "FAIL" if bad else "PASS", bad)

# R06 citation metadata
bad = []
try:
    misty = json.loads((ROOT / "misty.json").read_text(encoding="utf-8"))
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    def field(k):
        m = re.search(r"^" + k + r":\s*\"?(.*?)\"?\s*$", cff, re.M)
        return m.group(1) if m else None
    for k in ("title", "version", "license"):
        if field(k) != str(misty.get(k)):
            bad.append(f"{k} differs: CITATION.cff has {field(k)!r}, misty.json has {misty.get(k)!r}")
except Exception as e:
    bad.append(f"cannot read the metadata: {e}")
for p in ("CITATION.cff", "misty.json", "README.md"):
    if re.search(r"zenodo\.(X{3,}|0{5,}|TBD|NNN)|doi:\s*(TBD|TODO)|10\.5281/zenodo\.\s*$", text(p) or "", re.I | re.M):
        bad.append(f"placeholder DOI in {p}")
report("R06", "CITATION.cff and misty.json agree; no placeholder DOI", "FAIL" if bad else "PASS", bad)

# R07 licences
bad = []
if not (ROOT / "LICENSE").is_file() or sha((ROOT / "LICENSE").read_bytes()) != GPL_SHA:
    bad.append("LICENSE is not the FSF's verbatim GPL-3.0 text")
docs_lic = text("LICENSE-docs") or ""
if "Attribution-ShareAlike 4.0 International" not in docs_lic or "Section 1 -- Definitions." not in docs_lic:
    bad.append("LICENSE-docs is not the CC BY-SA 4.0 legal code")
report("R07", "LICENSE is the verbatim GPL-3.0; LICENSE-docs is the CC BY-SA 4.0 legal code", "FAIL" if bad else "PASS", bad)

# R08 no build artefacts
bad = [p for p in FILES if re.search(r"(^|/)(__pycache__|node_modules|\.work|\.build)(/|$)|\.pyc$|\.tar\.gz$|^\.work-ident$|^\.build-page\.html$", p)]
report("R08", "no build artefacts", "FAIL" if bad else "PASS", bad)

# R09 no path outside the folder
outside = ["/" + "tmp", "$" + "HOME", "~" + "/", ".." + "/", "/" + "home/", "/" + "Users/"]
bad = []
for p in FILES:
    if re.match(r"^(ops/.*\.sh|tools/[^/]*\.(py|mjs)|examples/[^/]*\.(py|sh))$", p):
        for n, ln in enumerate((text(p) or "").splitlines(), 1):
            for o in outside:
                if o in ln:
                    bad.append(f"{p}:{n} names {o}")
report("R09", "no script names a path outside this folder", "FAIL" if bad else "PASS", bad)

# R10 internal links
page = text("docs/index.html")
if page is None:
    report("R10", "every internal link in the site resolves", "FAIL", ["docs/index.html is missing"])
else:
    ids = set(re.findall(r'\sid="([^"]+)"', page))
    bad = sorted({h for h in re.findall(r'(?<![:\w])href="#([^"]*)"', page) if h not in ids})
    report("R10", f"every internal link in the site resolves ({len(ids)} anchors)", "FAIL" if bad else "PASS", bad)

# R11 estate links exist in the retrieved listing
bad = []
try:
    snap = set(json.loads((ROOT / "data" / "estate-snapshot.json").read_text(encoding="utf-8")))
    seed = json.loads((ROOT / "seed.json").read_text(encoding="utf-8"))
    own = f"{seed['org']}/{seed['slug']}"
    owners = "zistgah|project-ilm|hindawiai|pvjournal|ayeai|obonac|hmnsq|kaivalyik|c-polis"
    md = text("docs/rahnuma.md") or ""
    for o, r in sorted(set(re.findall(r"https://github\.com/(" + owners + r")/([A-Za-z0-9._-]+)", md))):
        r = re.sub(r"\.git$", "", r.rstrip("."))
        if f"{o}/{r}" not in snap and f"{o}/{r}" != own:
            bad.append(f"{o}/{r}")
except Exception as e:
    bad.append(f"cannot check: {e}")
report("R11", "every estate repository linked is in the retrieved listing", "FAIL" if bad else "PASS", bad)

# R12 the outputs match the build record
if BUILD is None:
    report("R12", "the site, the Markdown and the PDF match docs/BUILD.json", "FAIL", ["docs/BUILD.json is missing"])
else:
    bad = []
    for p in ("docs/index.html", "docs/rahnuma.md", "docs/rahnuma.pdf"):
        f = ROOT / p
        if not f.is_file():
            bad.append(f"missing: {p}")
        elif sha(f.read_bytes()) != BUILD["outputs"].get(p):
            bad.append(f"differs from the build record: {p}")
    if (ROOT / "docs/rahnuma.pdf").is_file() and not (ROOT / "docs/rahnuma.pdf").read_bytes().startswith(b"%PDF"):
        bad.append("docs/rahnuma.pdf is not a PDF")
    for p in ("docs/llms.txt", "docs/.nojekyll"):
        if not (ROOT / p).is_file():
            bad.append(f"missing: {p}")
    report("R12", "the site, the Markdown and the PDF match docs/BUILD.json", "FAIL" if bad else "PASS", bad)

n_pass, n_fail, n_unj = results.count("PASS"), results.count("FAIL"), results.count("UNJUDGED")
print(f"  {n_pass} passed, {n_fail} failed, {n_unj} unjudged")
sys.exit(1 if n_fail else (3 if n_unj else 0))
PYEOF
