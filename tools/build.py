#!/usr/bin/env python3
# tools/build.py: builds docs/ (the site, the single Markdown file, the PDF) from content/,
# examples/ and data/. Every example the guide shows is executed here and its real output is
# written into the text; ops/verify.sh re-runs the same commands and compares.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
#
#   python3 tools/build.py            site + Markdown + PDF
#   python3 tools/build.py --no-pdf   site + Markdown only
#
# Needs python3, pandoc and node. The PDF also needs playwright with Chromium, and pypdf.
# Everything is written inside this folder; nothing outside it is touched.
import hashlib, html, json, os, re, shutil, subprocess, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS, DOCS, CONTENT, DATA = ROOT / "tools", ROOT / "docs", ROOT / "content", ROOT / "data"
LINE = "© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI."
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", LC_ALL="C.UTF-8", PYTHONIOENCODING="utf-8")

def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()

def die(msg):
    print("build: " + msg, file=sys.stderr)
    sys.exit(1)

def sh(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        die(f"command failed ({p.returncode}): {cmd}\n{p.stdout}\n{p.stderr}")
    return p.stdout

META = json.loads((ROOT / "misty.json").read_text(encoding="utf-8"))
REL = json.loads((DATA / "release.json").read_text(encoding="utf-8"))
ESTATE = json.loads((DATA / "estate.json").read_text(encoding="utf-8"))
RUNS, CAPTURES = [], []

# ------------------------------------------------------------------ directives
def fence(text, lang="text"):
    text = text.rstrip("\n")
    ticks = "```"
    while ticks in text:
        ticks += "`"
    return f"{ticks}{lang}\n{text}\n{ticks}"

def needs_for(cmd):
    """Tools a re-run of this command needs beyond python3, so the gate can say UNJUDGED, not FAIL."""
    if "hindawi.sh urdu" in cmd or "hindawi.sh debug" in cmd:
        return ["gcc", "make", "flex", "gawk", "iconv", "gdb"] if "debug" in cmd else ["gcc", "make", "flex", "gawk", "iconv"]
    if "hindawi.sh" in cmd:
        return ["gcc", "make", "flex", "gawk", "iconv"]
    if "gcc" in cmd:
        return ["gcc"]
    return []

def run_block(cmd, record):
    out = sh(cmd)
    n = len(RUNS) + len(CAPTURES) + 1
    (DOCS / "outputs").mkdir(parents=True, exist_ok=True)
    name = f"outputs/{n:02d}.txt"
    (DOCS / name).write_text(out, encoding="utf-8")
    record.append({"cmd": cmd, "sha256": sha(out), "file": "docs/" + name, "needs": needs_for(cmd)})
    label = "Executed while this guide was built" if record is RUNS else "Captured while this guide was built"
    return f"*{label}:* `{cmd}`\n\n{fence(out)}"

def cell(s):
    return s.replace("|", "\\|")

def estate_table(gid):
    grp = next((g for g in ESTATE["groups"] if g["id"] == gid), None)
    if grp is None:
        die(f"no estate group {gid}")
    rows = ["| Repository | What it is | DOI |", "|:-----------|:------------------------------------|:------------|"]
    for it in grp["items"]:
        repo = f"[{it['repo']}](https://github.com/{it['repo']})"
        if it["page"]:
            repo += f", [page]({it['page']})"
        d = it["description"] or "No description recorded on the forge."
        if it.get("fork"):
            d += " (a fork)"
        dois = ", ".join(f"[{x.split('.')[-1]}](https://doi.org/{x})" for x in it["doi"]) or "none recorded"
        rows.append(f"| {repo} | {cell(d)} | {dois} |")
    return "\n".join(rows)

def records_table():
    rows = ["| Record | DOI |", "|:--------------------------------------------|:----------|"]
    for r in ESTATE["records"]:
        rows.append(f"| {cell(r['what'])} | [{r['doi']}](https://doi.org/{r['doi']}) |")
    return "\n".join(rows)

def counts_block():
    c = ESTATE["counts"]
    total = sum(c.values())
    listed = sum(len(g["items"]) for g in ESTATE["groups"])
    minted = sum(1 for g in ESTATE["groups"] for i in g["items"] if i["doi"])
    lines = ["| Organisation | Public repositories |", "|:-------------|------:|"]
    for o in ["zistgah", "project-ilm", "hindawiai", "pvjournal", "ayeai", "obonac"]:
        lines.append(f"| [{o}](https://github.com/{o}) | {c[o]} |")
    lines.append(f"| Total | {total} |")
    forks = "; ".join(f"{o}: {', '.join(sorted(v, key=str.lower))}" for o, v in sorted(ESTATE["forks"].items()))
    return ("\n".join(lines) + f"\n\nThe tables below place {listed} of these repositories by what they do; "
            f"{minted} of them record a DOI of their own. The organisations "
            f"{' and '.join(ESTATE['empty_orgs'])} hold no public repositories yet. "
            f"Forks of third-party projects kept for toolchains and study, by organisation: {forks}.")

def include_block(arg):
    parts = arg.split()
    path, lang = parts[0], (parts[1] if len(parts) > 1 else None)
    p = ROOT / path
    if not p.is_file():
        die(f"include: no file {path}")
    if lang is None:
        lang = {".py": "python", ".sh": "bash", ".csv": "text", ".c": "c", ".md": "markdown"}.get(p.suffix, "text")
    return f"*File:* `{path}`\n\n{fence(p.read_text(encoding='utf-8'), lang)}"

def md_include(arg):
    p = ROOT / arg.strip()
    if not p.is_file():
        die(f"md: no file {arg}")
    return p.read_text(encoding="utf-8").strip()

DIRECTIVE = re.compile(r"<!--\s*(run|capture|include|log|estate|records|counts|md)\s*(?::\s*(.*?))?\s*-->")

def expand(md):
    def rep(m):
        kind, arg = m.group(1), (m.group(2) or "").strip()
        if kind == "run":
            return run_block(arg, RUNS)
        if kind == "capture":
            return run_block(arg, CAPTURES)
        if kind == "include":
            return include_block(arg)
        if kind == "log":
            p = ROOT / arg
            return f"*Recorded run:* `{arg}`\n\n{fence(p.read_text(encoding='utf-8'))}"
        if kind == "estate":
            return estate_table(arg)
        if kind == "records":
            return records_table()
        if kind == "counts":
            return counts_block()
        if kind == "md":
            return md_include(arg)
        return m.group(0)
    return DIRECTIVE.sub(rep, md)

# ------------------------------------------------------------------ assembly
CHAPTER = re.compile(r"^## (.+?) \{#(ch-[\w-]+)\}\s*$", re.M)

def number_chapters(md):
    """Chapters are numbered in reading order; [[ch-id]] in the text becomes that chapter's number."""
    order = {cid: i + 1 for i, (_, cid) in enumerate(CHAPTER.findall(md))}
    md = CHAPTER.sub(lambda m: f"## {order[m.group(2)]}. {m.group(1)} {{#{m.group(2)}}}", md)
    def ref(m):
        if m.group(1) not in order:
            die("a reference names no chapter: " + m.group(1))
        return str(order[m.group(1)])
    return re.sub(r"\[\[(ch-[\w-]+)\]\]", ref, md)

def title_block():
    return (f"# {META['title']}\n\n{LINE}\n\nVersion {META['version']}, {REL['date_text']}. "
            f"Abhishek Choudhary, AyeAI. ORCID 0009-0002-0684-8320.\n\n"
            f"Text: CC BY-SA 4.0. Scripts: GPL-3.0-or-later. Site: {REL['site']}\n")

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def build_toc(body):
    heads = re.findall(r'<h([12]) id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S)
    items, cur = [], None
    for lvl, hid, txt in heads:
        t = strip_tags(txt)
        if lvl == "1":
            cur = {"id": hid, "text": t, "children": []}
            items.append(cur)
        elif cur is not None:
            cur["children"].append({"id": hid, "text": t})
    def render(printed):
        out = ['<ol class="toc">']
        for p in items:
            pg = f'<span class="pg" data-id="{p["id"]}"></span>' if printed else ""
            out.append(f'<li class="toc-part"><a href="#{p["id"]}">{html.escape(p["text"])}</a>{pg}<ol>')
            for c in p["children"]:
                pg = f'<span class="pg" data-id="{c["id"]}"></span>' if printed else ""
                out.append(f'<li><a href="#{c["id"]}">{html.escape(c["text"])}</a>{pg}</li>')
            out.append("</ol></li>")
        out.append("</ol>")
        return "\n".join(out)
    return render(False), render(True), items

FONT_FILES = [
    ("Tiro Devanagari Sanskrit", "tiro-devanagari-sanskrit", ["devanagari", "latin", "latin-ext"], [("400", "normal"), ("400", "italic")]),
    ("Noto Serif", "noto-serif", ["latin", "latin-ext"], [("400", "normal"), ("400", "italic"), ("700", "normal"), ("700", "italic")]),
    ("Noto Serif Devanagari", "noto-serif-devanagari", ["devanagari"], [("400", "normal"), ("700", "normal")]),
    ("Noto Serif Bengali", "noto-serif-bengali", ["bengali"], [("400", "normal"), ("700", "normal")]),
    ("Noto Serif Kannada", "noto-serif-kannada", ["kannada"], [("400", "normal"), ("700", "normal")]),
    ("Noto Naskh Arabic", "noto-naskh-arabic", ["arabic"], [("400", "normal")]),
    ("Noto Serif Telugu", "noto-serif-telugu", ["telugu"], [("400", "normal"), ("700", "normal")]),
    ("Noto Nastaliq Urdu", "noto-nastaliq-urdu", ["arabic"], [("400", "normal"), ("700", "normal")]),
    ("Noto Sans Mono", "noto-sans-mono", ["latin", "latin-ext"], [("400", "normal"), ("700", "normal")]),
]

def fonts():
    nm = TOOLS / "node_modules" / "@fontsource"
    dest = DOCS / "fonts"
    dest.mkdir(parents=True, exist_ok=True)
    css = []
    for family, pkg, subsets, styles in FONT_FILES:
        pdir = nm / pkg
        if not pdir.is_dir():
            die(f"font package @fontsource/{pkg} missing; run: npm ci --prefix tools")
        shutil.copyfile(pdir / "LICENSE", dest / f"LICENSE-{pkg}.txt")
        idx = "\n".join(f.read_text(encoding="utf-8") for f in sorted(pdir.glob("*.css")))
        for sub in subsets:
            for w, st in styles:
                fn = f"{pkg}-{sub}-{w}-{st}.woff2"
                src = pdir / "files" / fn
                if not src.exists():
                    continue
                shutil.copyfile(src, dest / fn)
                m = re.search(r"/\* " + re.escape(pkg) + r"-" + re.escape(sub) + r"-" + w + "-" + st + r" \*/\s*@font-face\s*\{(.*?)\}", idx, re.S)
                ur = re.search(r"unicode-range:\s*([^;]+);", m.group(1)).group(1) if m else None
                css.append("@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;src:url(fonts/%s) format('woff2');%s}"
                           % (family, st, w, fn, f"unicode-range:{ur};" if ur else ""))
    return "\n".join(css)

def cover_rows():
    """The cover is produced by the Hindawi tools themselves; the gate re-runs this command."""
    cmd = "bash examples/hindawi.sh cover"
    out = sh(cmd)
    RUNS.append({"cmd": cmd, "sha256": sha(out), "file": None, "needs": needs_for(cmd)})
    return [line.split("\t") for line in out.strip("\n").split("\n")]

def hero():
    lang = {"Devanagari": "hi", "Telugu": "te", "Bengali": "bn"}
    rows = []
    for label, written, hub, rmn, inv, back in cover_rows():
        wl = lang.get(label, "ur")
        if not back:
            back_html = '<span class="same">the same identity</span>'
        else:
            back_html = f'<span lang="{wl if label == "Telugu" else "hi"}">{html.escape(back)}</span>'
        rows.append(f'<div class="path"><span class="lab">{html.escape(label)}</span>'
                    f'<span class="cell" lang="{wl}">{html.escape(written)}</span><span class="arr">→</span>'
                    f'<span class="cell" lang="hi">{html.escape(hub)}</span><span class="arr">→</span>'
                    f'<code class="cell rmn">{html.escape(rmn)}</code><span class="arr">→</span>'
                    f'<span class="cell">{back_html}</span></div>')
    return f"""<div class="cover-inner">
<h1 class="title">Rahnuma</h1>
<p class="title-scripts"><span lang="hi">रहनुमा</span><span lang="ur" dir="rtl">رہنما</span></p>
<p class="subtitle">A working guide to the ILM, PANINI and Zistgah stack, from bytes and scripts to compilers, Pāṇini and quantum substrates</p>
<figure class="layers"><div class="word" lang="sa">प्रकृति</div>
<div class="paths"><div class="path head"><span class="lab"></span><span class="cell">written</span><span class="arr"></span><span class="cell">Devanagari hub</span><span class="arr"></span><span class="cell">Romenagri</span><span class="arr"></span><span class="cell">and back</span></div>
{''.join(rows)}</div>
<figcaption>One identity, many scripts. Telugu and Bengali meet Devanagari in one hub, become the same Romenagri word, and come back exactly. Urdu meets the hub at what is written: without its short-vowel marks the word reads hanadawee; with zer and sukun it is hindawi. Every cell here was produced by the Hindawi tools while this guide was built.</figcaption></figure>
<p class="byline">Abhishek Choudhary, AyeAI. Version {META['version']}, {REL['date_text']}.</p>
</div>"""

def wrap_tables(body):
    return re.sub(r"(<table>.*?</table>)", r'<div class="tablewrap">\1</div>', body, flags=re.S)

def pandoc(md):
    p = subprocess.run(["pandoc", "-f", "markdown+pipe_tables+tex_math_dollars+fenced_code_attributes+header_attributes+auto_identifiers-implicit_figures",
                        "-t", "html5", "--mathjax", "--no-highlight", "--wrap=none"],
                       input=md, capture_output=True, text=True, cwd=ROOT)
    if p.returncode != 0:
        die("pandoc failed: " + p.stderr)
    return p.stdout

def ensure_node_modules():
    if not (TOOLS / "node_modules" / "mathjax-full").is_dir():
        sh("npm ci --prefix tools --no-audit --no-fund", timeout=1800)

# ------------------------------------------------------------------ PDF
def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if not unicodedata.combining(c)).lower())

def pdf(items):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter
    work = ROOT / ".build"
    work.mkdir(exist_ok=True)
    uri = (DOCS / "index.html").resolve().as_uri()
    footer = ('<div style="width:100%;font-family:\'Noto Serif\',serif;font-size:7.5pt;color:#5a6078;'
              'padding:0 16mm;display:flex;justify-content:space-between"><span>Rahnuma ' + META["version"] +
              '</span><span class="pageNumber"></span></div>')
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_default_timeout(90000)
        pg.goto(uri)
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.emulate_media(media="print")
        pg.evaluate("document.body.classList.add('print-cover')")
        pg.pdf(path=str(work / "cover.pdf"), format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        pg.evaluate("document.body.classList.remove('print-cover'); document.body.classList.add('print-body')")
        opts = dict(format="A4", print_background=True, display_header_footer=True, header_template="<span></span>",
                    footer_template=footer, margin={"top": "17mm", "bottom": "19mm", "left": "17mm", "right": "17mm"},
                    outline=True, tagged=True)
        pg.pdf(path=str(work / "body.pdf"), **opts)
        # page numbers for the printed contents: find each heading in the first render
        pages = [norm(x.extract_text() or "") for x in PdfReader(str(work / "body.pdf")).pages]
        found, start = {}, 1
        for part in items:
            for i in range(start, len(pages)):
                if pages[i].startswith(norm(part["text"])[:24]):
                    found[part["id"]] = i + 1
                    start = i
                    break
            for ch in part["children"]:
                for i in range(start, len(pages)):
                    if norm(ch["text"])[:28] in pages[i]:
                        found[ch["id"]] = i + 1
                        start = i
                        break
        missing = [c["id"] for p_ in items for c in [p_] + p_["children"] if c["id"] not in found]
        if missing:
            die("pdf: could not place in the page count: " + ", ".join(missing))
        pg.evaluate("m => { for (const s of document.querySelectorAll('.toc-print .pg')) s.textContent = m[s.dataset.id] || ''; }", found)
        pg.pdf(path=str(work / "body.pdf"), **opts)
        b.close()
    w = PdfWriter()
    w.append(str(work / "cover.pdf"))
    w.append(str(work / "body.pdf"), import_outline=True)
    w.add_metadata({"/Title": META["title"], "/Author": "Abhishek Choudhary, AyeAI", "/Subject": "Version " + META["version"],
                    "/Keywords": ", ".join(META["keywords"]), "/Creator": "tools/build.py (Chromium, MathJax, pandoc)"})
    out = DOCS / "rahnuma.pdf"
    with open(out, "wb") as f:
        w.write(f)
    n = len(PdfReader(str(out)).pages)
    shutil.rmtree(work)
    return n

# ------------------------------------------------------------------ main
def main():
    make_pdf = "--no-pdf" not in sys.argv
    if (DOCS / "outputs").exists():
        shutil.rmtree(DOCS / "outputs")
    DOCS.mkdir(exist_ok=True)
    chapters = sorted(CONTENT.glob("*.md"))
    if not chapters:
        die("no content/*.md")
    body_md = number_chapters("\n\n".join(expand(p.read_text(encoding="utf-8")) for p in chapters))
    for bad in ("\u2014",):
        if bad in body_md:
            i = body_md.index(bad)
            die("an em dash is in the text near: " + body_md[max(0, i - 60):i + 20].replace("\n", " "))
    full_md = title_block() + "\n\n" + body_md + "\n"
    (DOCS / "rahnuma.md").write_text(full_md, encoding="utf-8")
    body = wrap_tables(pandoc(body_md))
    toc_side, toc_print, items = build_toc(body)
    tpl = (TOOLS / "template.html").read_text(encoding="utf-8")
    style = (TOOLS / "style.css").read_text(encoding="utf-8")
    ensure_node_modules()
    page = (tpl.replace("{{FONTS}}", fonts()).replace("{{STYLE}}", style).replace("{{HERO}}", hero())
               .replace("{{TOC}}", toc_side).replace("{{TOC_PRINT}}", toc_print).replace("{{CONTENT}}", body)
               .replace("{{VERSION}}", META["version"]).replace("{{DATE}}", REL["date_text"])
               .replace("{{TITLE}}", html.escape(META["title"])).replace("{{DESCRIPTION}}", html.escape(REL["summary"])))
    raw = ROOT / ".build-page.html"
    raw.write_text(page, encoding="utf-8")
    sh(f"node tools/mathjax_page.mjs {raw.name} docs/index.html")
    raw.unlink()
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    llms = ["# Rahnuma", "", f"> {REL['summary']}", "", LINE, "",
            "- [The whole guide as one Markdown file](rahnuma.md)", "- [The guide as a PDF](rahnuma.pdf)",
            "- [The guide as a web page](index.html)", "", "## Chapters", ""]
    for p_ in items:
        llms.append(f"- {p_['text']}")
        llms += [f"  - [{c['text']}](index.html#{c['id']})" for c in p_["children"]]
    (DOCS / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    pages = None
    if make_pdf:
        for attempt in (1, 2):   # headless Chromium occasionally stalls on start; one retry, then fail loudly
            try:
                pages = pdf(items)
                break
            except Exception as e:
                if attempt == 2:
                    die(f"the PDF could not be printed: {e}")
                print(f"build: the PDF step stalled ({type(e).__name__}); retrying once", file=sys.stderr)
    inputs = {}
    for pat in ("content/*.md", "examples/*", "data/*.json", "data/*.csv", "data/*.md", "data/logs/*", "tools/*.py", "tools/*.mjs",
                "tools/*.html", "tools/*.css", "tools/package.json", "misty.json"):
        for f in sorted(ROOT.glob(pat)):
            if f.is_file():
                inputs[str(f.relative_to(ROOT))] = sha(f.read_bytes())
    for f in sorted((ROOT / "vendor").rglob("*")):
        if f.is_file():
            inputs[str(f.relative_to(ROOT))] = sha(f.read_bytes())
    def ver(cmd):
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip().splitlines()[0]
        except Exception:
            return "absent"
    build = {"built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "version": META["version"],
             "inputs": inputs, "runs": RUNS, "captures": CAPTURES,
             "outputs": {"docs/index.html": sha((DOCS / "index.html").read_bytes()), "docs/rahnuma.md": sha(full_md),
                         "docs/rahnuma.pdf": sha((DOCS / "rahnuma.pdf").read_bytes()) if (DOCS / "rahnuma.pdf").exists() else None,
                         "pdf_pages": pages if pages is not None else json.loads((DOCS / "BUILD.json").read_text()).get("outputs", {}).get("pdf_pages") if (DOCS / "BUILD.json").exists() else None},
             "tools": {"python": sys.version.split()[0], "pandoc": ver("pandoc --version"), "node": ver("node --version"),
                       "gcc": ver("gcc --version"), "mathjax-full": json.loads((TOOLS / "node_modules" / "mathjax-full" / "package.json").read_text())["version"]}}
    (DOCS / "BUILD.json").write_text(json.dumps(build, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"built docs/index.html, docs/rahnuma.md{', docs/rahnuma.pdf (' + str(pages) + ' pages)' if pages else ''}; "
          f"{len(RUNS)} runs and {len(CAPTURES)} captures written into the text")

if __name__ == "__main__":
    main()
