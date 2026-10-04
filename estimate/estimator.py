#!/usr/bin/env python3
# estimator.py: model-based size, complexity and cost estimation of a set of git repositories.
# Counts tracked files only, once each across the whole estate, then applies COCOMO II and the rates
# in rates.json. Writes report.md, report.json, repos.csv and languages.csv to the output folder.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import argparse, csv, hashlib, json, math, os, re, shutil, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
# extension: (language, category, line-comment tokens, block-comment pairs)
C_LIKE = (["//"], [("/*", "*/")])
LANGS = {
    ".c": ("C", "code") + C_LIKE, ".h": ("C header", "code") + C_LIKE, ".cpp": ("C++", "code") + C_LIKE, ".cc": ("C++", "code") + C_LIKE,
    ".hpp": ("C++", "code") + C_LIKE, ".cu": ("CUDA", "code") + C_LIKE, ".java": ("Java", "code") + C_LIKE, ".js": ("JavaScript", "code") + C_LIKE,
    ".mjs": ("JavaScript", "code") + C_LIKE, ".cjs": ("JavaScript", "code") + C_LIKE, ".jsx": ("JavaScript", "code") + C_LIKE,
    ".ts": ("TypeScript", "code") + C_LIKE, ".tsx": ("TypeScript", "code") + C_LIKE, ".go": ("Go", "code") + C_LIKE, ".rs": ("Rust", "code") + C_LIKE,
    ".cs": ("C#", "code") + C_LIKE, ".swift": ("Swift", "code") + C_LIKE, ".kt": ("Kotlin", "code") + C_LIKE, ".scala": ("Scala", "code") + C_LIKE,
    ".y": ("Yacc", "code") + C_LIKE, ".l": ("Lex", "code") + C_LIKE, ".lex": ("Lex", "code") + C_LIKE, ".css": ("CSS", "web", [], [("/*", "*/")]),
    ".py": ("Python", "code", ["#"], []), ".sh": ("Shell", "code", ["#"], []), ".bash": ("Shell", "code", ["#"], []),
    ".awk": ("AWK", "code", ["#"], []), ".pl": ("Perl", "code", ["#"], []), ".rb": ("Ruby", "code", ["#"], []), ".r": ("R", "code", ["#"], []),
    ".mk": ("Makefile", "code", ["#"], []), ".cmake": ("CMake", "code", ["#"], []), ".ps1": ("PowerShell", "code", ["#"], []),
    ".pni": ("PANINI", "code", ["'", "REM"], []), ".panini": ("PANINI", "code", ["#", "'"], []), ".uhin": ("Hindawi", "code") + C_LIKE,
    ".lua": ("Lua", "code", ["--"], []), ".sql": ("SQL", "code", ["--"], []), ".hs": ("Haskell", "code", ["--"], []), ".vhd": ("VHDL", "code", ["--"], []),
    ".v": ("Verilog", "code") + C_LIKE, ".sv": ("SystemVerilog", "code") + C_LIKE, ".sp": ("SPICE", "code", ["*"], []), ".cir": ("SPICE", "code", ["*"], []),
    ".asm": ("Assembly", "code", [";", "#"], []), ".s": ("Assembly", "code", [";", "#", "//"], []), ".S": ("Assembly", "code", [";", "#", "//"], []),
    ".m": ("MATLAB", "code", ["%"], []), ".jl": ("Julia", "code", ["#"], []), ".el": ("Emacs Lisp", "code", [";"], []), ".scm": ("Scheme", "code", [";"], []),
    ".bas": ("BASIC", "code", ["'", "REM"], []), ".html": ("HTML", "web", [], [("<!--", "-->")]), ".htm": ("HTML", "web", [], [("<!--", "-->")]),
    ".svg": ("SVG", "asset-text", [], [("<!--", "-->")]), ".xml": ("XML", "data", [], [("<!--", "-->")]), ".json": ("JSON", "data", [], []),
    ".yml": ("YAML", "config", ["#"], []), ".yaml": ("YAML", "config", ["#"], []), ".toml": ("TOML", "config", ["#"], []), ".ini": ("INI", "config", [";", "#"], []),
    ".csv": ("CSV", "data", [], []), ".tsv": ("TSV", "data", [], []), ".ipynb": ("Notebook", "code", [], []),
    ".md": ("Markdown", "prose", [], []), ".rst": ("reStructuredText", "prose", [], []), ".txt": ("Text", "prose", [], []),
    ".tex": ("TeX", "prose", ["%"], []), ".bib": ("BibTeX", "data", [], []), ".cff": ("CFF", "config", ["#"], []),
}
NAMED = {"Makefile": ("Makefile", "code", ["#"], []), "Dockerfile": ("Dockerfile", "code", ["#"], []), "CMakeLists.txt": ("CMake", "code", ["#"], [])}
ASSET_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".mp4", ".webm", ".mp3", ".wav", ".ogg", ".tif", ".tiff", ".bmp", ".ico"}
CODE_CATS = {"code", "web"}


def sh(cmd, cwd=None):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600).stdout
    except Exception:
        return ""


def count_lines(text, lc, bc):
    code = comment = blank = 0
    in_block = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            blank += 1
            continue
        if in_block:
            comment += 1
            if in_block in line:
                in_block = None
            continue
        started = next(((a, b) for a, b in bc if line.startswith(a)), None)
        if started:
            comment += 1
            if started[1] not in line[len(started[0]):]:
                in_block = started[1]
            continue
        if any(line.startswith(t) for t in lc):
            comment += 1
            continue
        code += 1
    return code, comment, blank


def prose_words(text, ext):
    if ext == ".md":
        text = re.sub(r"```.*?```", " ", text, flags=re.S)
    if ext == ".tex":
        text = re.sub(r"(?m)%.*$", " ", text)
        text = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return len(re.findall(r"\w+", text))


def notebook_lines(text):
    try:
        nb = json.loads(text)
    except Exception:
        return 0, 0
    code = words = 0
    for c in nb.get("cells", []):
        src = "".join(c.get("source", []))
        if c.get("cell_type") == "code":
            code += sum(1 for l in src.splitlines() if l.strip() and not l.strip().startswith("#"))
        else:
            words += len(re.findall(r"\w+", src))
    return code, words


def git_metrics(repo):
    shallow = sh(["git", "rev-parse", "--is-shallow-repository"], repo).strip() == "true"
    log = sh(["git", "log", "--format=%ad|%ae", "--date=short"], repo).splitlines()
    days = sorted({l.split("|")[0] for l in log if "|" in l})
    return {"commits": len(log), "active_days": len(days), "authors": len({l.split("|")[1] for l in log if "|" in l}),
            "first": days[0] if days else "", "last": days[-1] if days else "", "shallow": shallow, "days": days}


def lizard_metrics(repo, files):
    exe = shutil.which("lizard")
    if not exe or not files:
        return None
    out = sh([exe, "--csv"] + [str(repo / f) for f in files][:4000])
    fn, ccn = 0, []
    for row in csv.reader(out.splitlines()):
        if len(row) > 2 and row[1].isdigit():
            fn += 1
            ccn.append(int(row[1]))
    if not fn:
        return None
    ccn.sort()
    return {"functions": fn, "ccn_mean": round(sum(ccn) / fn, 2), "ccn_p90": ccn[int(0.9 * (fn - 1))], "ccn_max": ccn[-1],
            "over_10": sum(1 for c in ccn if c > 10), "over_20": sum(1 for c in ccn if c > 20)}


def scan(repos, model):
    skip_dirs, skip_files = set(model["skip_dirs"]), set(model["skip_files"])
    seen = {}
    rows, by_lang = [], defaultdict(Counter)
    for repo in repos:
        name = repo.name
        files = sh(["git", "ls-files", "-z"], repo).split("\0") if (repo / ".git").exists() else [str(p.relative_to(repo)) for p in repo.rglob("*") if p.is_file()]
        r = Counter()
        cx_files = []
        for rel in filter(None, files):
            parts = Path(rel).parts
            if any(p in skip_dirs for p in parts[:-1]) or parts[-1] in skip_files:
                r["skipped_vendored"] += 1
                continue
            if any(rel.startswith(x) for x in model.get("exclude_paths", {}).get(name, [])):
                r["skipped_excluded"] += 1
                continue
            p = repo / rel
            if not p.is_file():
                continue
            ext = p.suffix.lower() if p.suffix != ".S" else ".S"
            size = p.stat().st_size
            if ext in ASSET_EXT:
                r["assets"] += 1
                r["asset_bytes"] += size
                if size >= RATES["assets"]["min_bytes"]:
                    r["figures"] += 1
                continue
            spec = NAMED.get(p.name) or LANGS.get(ext)
            if not spec:
                r["other_files"] += 1
                continue
            lang, cat, lc, bc = spec
            try:
                data = p.read_bytes()
                text = data.decode("utf-8")
            except Exception:
                r["binary_or_undecodable"] += 1
                continue
            digest = hashlib.sha256(re.sub(rb"[ \t]+(\r?\n)", rb"\1", data)).hexdigest()
            dup = digest in seen
            if not dup:
                seen[digest] = f"{name}/{rel}"
            lines = text.splitlines()
            if cat in CODE_CATS and lines and sum(len(l) for l in lines) / len(lines) > model["minified_line_chars"]:
                r["skipped_minified"] += 1
                continue
            head = "\n".join(lines[:6]).lower()
            if cat in CODE_CATS and "generated" in head and any(t in head for t in ("do not edit", "automatically", "auto-generated", "generated by", "@generated")):
                r["skipped_generated"] += 1
                continue
            if cat == "prose" and ext == ".txt":
                nonblank = [l for l in lines if l.strip()]
                if len(nonblank) > 200 and sum(len(l.split()) for l in nonblank) / len(nonblank) < model["wordlist_words_per_line"]:
                    cat = "data"
            if lang == "JSON" and size > model["data_json_bytes"]:
                cat = "data"
            if lang == "Notebook":
                code, words = notebook_lines(text)
                comment = blank = 0
            elif cat == "prose":
                code, comment, blank, words = 0, 0, 0, prose_words(text, ext)
            else:
                code, comment, blank = count_lines(text, lc, bc)
                words = 0
            key = "dup_" if dup else ""
            r[key + "files"] += 1
            if cat in CODE_CATS:
                r[key + "sloc"] += code
                r[key + "comments"] += comment
                if not dup:
                    by_lang[lang]["sloc"] += code
                    by_lang[lang]["files"] += 1
                    if cat == "code":
                        cx_files.append(rel)
            elif cat == "prose":
                r[key + "words"] += words
            elif cat == "data":
                r[key + "data_bytes"] += size
            else:
                r[key + "config_lines"] += code
            if lang == "Notebook" and not dup:
                r["words"] += words
        g = git_metrics(repo) if (repo / ".git").exists() else {}
        cx = lizard_metrics(repo, cx_files)
        rows.append({"repo": name, **dict(r), **g, "complexity": cx})
    return rows, by_lang


def cocomo(ksloc, sf, em, k):
    if ksloc <= 0:
        return 0.0, 0.0
    E = k["B"] + 0.01 * sf
    pm = k["A"] * ksloc ** E * em
    tdev = k["C"] * pm ** (k["D"] + 0.2 * (E - k["B"]))
    return pm, tdev


def model_all(rows, model, rates):
    k = model["cocomo"]
    out = {}
    hpm = rates["hours_per_person_month"]["value"]
    for case in ("low", "likely", "high"):
        sf, em = k["scale_factor_sum"][case], k["effort_multiplier_product"][case]
        per = [cocomo(r.get("sloc", 0) / 1000, sf, em, k) for r in rows]
        total_ksloc = sum(r.get("sloc", 0) for r in rows) / 1000
        whole_pm, whole_tdev = cocomo(total_ksloc, sf, em, k)
        words = sum(r.get("words", 0) for r in rows)
        doc_pm = words / rates["writing"]["words_per_day"][case] / (hpm / 8)
        fig_pm = sum(r.get("figures", 0) for r in rows) * rates["assets"]["hours_per_figure"][case] / hpm
        out[case] = {"sum_of_repos_pm": sum(p for p, _ in per), "integrated_pm": whole_pm, "integrated_tdev_months": whole_tdev,
                     "longest_repo_tdev_months": max((t for _, t in per), default=0), "documentation_pm": doc_pm, "figures_pm": fig_pm}
    return out


def costs(mod, rates):
    res = {}
    for region, r in rates["regions"].items():
        res[region] = {}
        for case in ("low", "likely", "high"):
            per_pm = r[case] * rates["loaded_cost_factor"][case] / 12
            m = mod[case]
            res[region][case] = {"per_person_month": per_pm,
                                 "software_sum_of_repos": m["sum_of_repos_pm"] * per_pm,
                                 "software_integrated": m["integrated_pm"] * per_pm,
                                 "documentation": m["documentation_pm"] * per_pm,
                                 "figures": m["figures_pm"] * per_pm}
    return res


def ai_scenario(rows, mod, rates, cost):
    ai = rates["ai"]
    cpt = ai["chars_per_token"]["value"]
    produced_chars = sum(r.get("sloc", 0) * MODEL["chars_per_sloc"] + r.get("words", 0) * MODEL["chars_per_word"] for r in rows)
    out_tok = produced_chars / cpt
    res = {}
    for case in ("low", "likely", "high"):
        u = ai["usage"][case]
        rework, ctx, tier, cached = u["redrafts"], u["context_ratio"], u["tier"], u["cached_share"]
        p = ai["prices_usd_per_mtok"][tier]
        o = out_tok * rework
        i = o * ctx
        usd = (o * p["output"] + i * (1 - cached) * p["input"] + i * cached * p["input"] * ai["prices_usd_per_mtok"]["cache_read_fraction"]) / 1e6
        ratio = ai["productivity_time_ratio"][case]
        human_pm = (mod["likely"]["integrated_pm"] + mod["likely"]["documentation_pm"]) * ratio
        res[case] = {"output_tokens": o, "input_tokens": i, "model_tier": tier, "api_usd": usd, "time_ratio": ratio, "human_pm": human_pm,
                     "human_cost": {reg: human_pm * cost[reg]["likely"]["per_person_month"] for reg in cost}}
    return res, out_tok


def money(v, region):
    if region == "India":
        return f"₹{v / 1e7:,.2f} crore" if v >= 1e7 else f"₹{v / 1e5:,.1f} lakh"
    return f"${v / 1e6:,.2f} million" if v >= 1e6 else f"${v:,.0f}"


def main():
    global RATES, MODEL
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", nargs="+", required=True)
    ap.add_argument("--out", default="estimate-out")
    a = ap.parse_args()
    model = MODEL = json.loads((HERE / "model.json").read_text(encoding="utf-8"))
    RATES = json.loads((HERE / "rates.json").read_text(encoding="utf-8"))
    repos = sorted({Path(r).resolve() for r in a.repos if Path(r).is_dir()})
    rows, by_lang = scan(repos, model)
    mod = model_all(rows, model, RATES)
    cost = costs(mod, RATES)
    ai, out_tok = ai_scenario(rows, mod, RATES, cost)
    T = lambda key: sum(r.get(key, 0) for r in rows)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    keys = ["repo", "files", "sloc", "comments", "words", "data_bytes", "config_lines", "assets", "figures", "dup_files", "dup_sloc", "dup_words",
            "skipped_vendored", "skipped_excluded", "skipped_generated", "skipped_minified", "commits", "active_days", "authors", "first", "last", "shallow"]
    with open(out / "repos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(keys + ["functions", "ccn_mean", "ccn_p90", "ccn_max", "over_10", "over_20"])
        for r in rows:
            cx = r.get("complexity") or {}
            w.writerow([r.get(k, "") for k in keys] + [cx.get(k, "") for k in ("functions", "ccn_mean", "ccn_p90", "ccn_max", "over_10", "over_20")])
    with open(out / "languages.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["language", "files", "sloc"])
        for lang, c in sorted(by_lang.items(), key=lambda x: -x[1]["sloc"]):
            w.writerow([lang, c["files"], c["sloc"]])
    cxs = [r["complexity"] for r in rows if r.get("complexity")]
    fn = sum(c["functions"] for c in cxs)
    summary = {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "repositories": len(rows),
               "unique_sloc": T("sloc"), "duplicate_sloc": T("dup_sloc"), "prose_words": T("words"), "figures": T("figures"), "assets": T("assets"),
               "commits": T("commits"), "active_days_sum": T("active_days"), "shallow_repos": sum(1 for r in rows if r.get("shallow")),
               "functions_measured": fn, "functions_over_10": sum(c["over_10"] for c in cxs), "functions_over_20": sum(c["over_20"] for c in cxs),
               "model": mod, "costs": cost, "ai": ai, "ai_output_tokens_once": out_tok, "rates": RATES, "cocomo": model["cocomo"]}
    all_days = sorted({d for r in rows for d in r.get("days", [])})
    ab = RATES["as_built"]
    hpm = RATES["hours_per_person_month"]["value"]
    as_built = {case: len(all_days) * ab["hours_per_active_day"][case] / hpm for case in ("low", "likely", "high")}
    summary["as_built"] = {"distinct_active_days": len(all_days), "first": all_days[0] if all_days else "", "last": all_days[-1] if all_days else "",
                           "person_months": as_built, "ai_spend_usd": ab["ai_spend_usd"]}
    for r in rows:
        r.pop("days", None)
    (out / "report.json").write_text(json.dumps({"summary": summary, "repos": rows}, indent=1, default=str), encoding="utf-8")
    L = []
    w = L.append
    w("# Model-based estimate of the estate's work")
    w("")
    w(f"Generated {summary['generated_utc']} over {len(rows)} repositories. Every figure below is computed from the repositories' tracked files and history and from `rates.json` and `model.json`, which name their sources.")
    w("")
    w("## What was measured")
    w("")
    w("| Measure | Value |")
    w("|:--|--:|")
    w(f"| Repositories | {len(rows)} |")
    w(f"| Source lines of code, each file counted once | {T('sloc'):,} |")
    w(f"| Lines in files repeated across repositories, not counted again | {T('dup_sloc'):,} |")
    w(f"| Words of prose: Markdown, TeX, text, notebooks | {T('words'):,} |")
    w(f"| Figures and images over {RATES['assets']['min_bytes'] // 1000} KB | {T('figures'):,} |")
    w(f"| Commits; sum of distinct active days per repository | {T('commits'):,}; {T('active_days'):,} |")
    w(f"| Files left out as vendored, third-party, generated or minified | {T('skipped_vendored') + T('skipped_excluded') + T('skipped_generated') + T('skipped_minified'):,} |")
    if summary["shallow_repos"]:
        w(f"| Repositories cloned shallow, so their history is not measured | {summary['shallow_repos']} |")
    if fn:
        w(f"| Functions measured for complexity (lizard) | {fn:,} |")
        w(f"| Functions with cyclomatic complexity above 10; above 20 | {summary['functions_over_10']:,}; {summary['functions_over_20']:,} |")
    w("")
    w("| Language | Files | SLOC |")
    w("|:--|--:|--:|")
    for lang, c in sorted(by_lang.items(), key=lambda x: -x[1]["sloc"])[:15]:
        w(f"| {lang} | {c['files']:,} | {c['sloc']:,} |")
    w("")
    w("## Effort, by COCOMO II")
    w("")
    w("Effort in person-months of 152 hours. *Sum of repositories* treats each repository as its own project; *integrated* treats the estate as one system, where the model's diseconomy of scale applies to the whole.")
    w("")
    w("| Case | Sum of repositories | Integrated | Schedule, integrated | Documentation | Figures |")
    w("|:--|--:|--:|--:|--:|--:|")
    for case in ("low", "likely", "high"):
        m = mod[case]
        w(f"| {case} | {m['sum_of_repos_pm']:,.0f} PM | {m['integrated_pm']:,.0f} PM | {m['integrated_tdev_months']:,.1f} months | {m['documentation_pm']:,.0f} PM | {m['figures_pm']:,.0f} PM |")
    w("")
    w("## Cost to rebuild it with a conventional team")
    w("")
    w("Integrated software effort plus documentation and figures, at loaded rates.")
    w("")
    w("| Region | Low | Likely | High |")
    w("|:--|--:|--:|--:|")
    for reg, c in cost.items():
        cells = [money(c[case]["software_integrated"] + c[case]["documentation"] + c[case]["figures"], reg) for case in ("low", "likely", "high")]
        w(f"| {reg} | " + " | ".join(cells) + " |")
    w("")
    w("## The same work with AI in the process")
    w("")
    w(f"The work's own text is about {out_tok / 1e6:,.1f} million tokens. AI cost multiplies it by redrafts and by the context read for each draft; human effort is the likely COCOMO effort times the measured range of time ratios.")
    w("")
    w("| Case | Time with AI over without | Human effort | AI usage | Human cost, India | Human cost, United States |")
    w("|:--|--:|--:|--:|--:|--:|")
    for case in ("low", "likely", "high"):
        s = ai[case]
        w(f"| {case} | {s['time_ratio']:.2f} | {s['human_pm']:,.0f} PM | ${s['api_usd']:,.0f} ({s['model_tier'].replace('_', ' ')}) | {money(s['human_cost']['India'], 'India')} | {money(s['human_cost']['United States'], 'United States')} |")
    w("")
    w("## As built")
    w("")
    sb = summary["as_built"]
    w(f"Git history shows {sb['distinct_active_days']:,} distinct days with at least one commit across all repositories, from {sb['first'] or 'n/a'} to {sb['last'] or 'n/a'}.")
    if summary["shallow_repos"]:
        w(f"{summary['shallow_repos']} of the repositories were cloned shallow, so their history is not counted here; run with `--clone` for full history.")
    w("")
    w("| Hours per active day | Person-months as built | Likely COCOMO effort over this |")
    w("|:--|--:|--:|")
    for case in ("low", "likely", "high"):
        pm = sb["person_months"][case]
        ratio = (mod["likely"]["integrated_pm"] + mod["likely"]["documentation_pm"]) / pm if pm else 0
        w(f"| {ab['hours_per_active_day'][case]} | {pm:,.1f} | {ratio:,.0f} times |")
    w("")
    spend = sb["ai_spend_usd"]
    w(f"AI spend over the period: {'$' + format(spend, ',.0f') if spend is not None else 'not entered; set as_built.ai_spend_usd in rates.json'}.")
    w("")
    w("## What the model cannot see")
    w("")
    w("COCOMO estimates the construction of software of a given size. It does not price invention: the research, the design of the architecture, the formal frameworks, the decades of prior work that made the code possible, or the judgement in what was left out. Lines of code measure size, not novelty. Read every figure here as a floor for the intellectual work, and as a fair estimate only of what it would cost a team to rebuild what is now written down.")
    w("")
    w("## Sources and assumptions")
    w("")
    w(f"- COCOMO II: {model['cocomo']['source']}")
    for reg, r in RATES["regions"].items():
        w(f"- Rates, {reg}: {r['source']}")
    w(f"- Exchange rate: {RATES['currency']['inr_per_usd']} rupees per dollar; {RATES['currency']['source']}")
    w(f"- Loaded cost factor {RATES['loaded_cost_factor']['likely']}: {RATES['loaded_cost_factor']['source']}")
    w(f"- AI prices: {RATES['ai']['prices_usd_per_mtok']['source']}")
    w(f"- Tokens: {RATES['ai']['chars_per_token']['source']}")
    w(f"- AI time ratios: {RATES['ai']['productivity_time_ratio']['source']}")
    w(f"- AI usage: {RATES['ai']['usage']['source']}; text sized at {model['chars_per_sloc']} characters per line and {model['chars_per_word']} per word ({model['chars_source']})")
    w(f"- Left out: directories {', '.join(model['skip_dirs'])}; files that declare themselves generated; word lists; and named paths ({model['exclude_source']})")
    w(f"- Writing: {RATES['writing']['source']}")
    w(f"- Figures: {RATES['assets']['source']}")
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"estimate: {len(rows)} repositories, {T('sloc'):,} unique SLOC, {T('words'):,} words; report in {out}/report.md")


if __name__ == "__main__":
    main()
