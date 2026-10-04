#!/usr/bin/env python3
# tools/diagrams.py: renders data/diagrams.json, the guide's diagrams, to SVG with Graphviz.
# Every node and edge is a relation recorded in the estate; captions say where one is the write-ups' reading.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAL = ["#23408e", "#2e6b5e", "#7a3e65", "#a0522d", "#6b5b2e", "#3f6b2e", "#4a5068"]

def q(s):
    return '"' + s.replace('"', '\\"').replace("\n", "\\n") + '"'

def dot(spec):
    out = ["digraph g {", f'  graph [rankdir={spec["rankdir"]}, nodesep=0.3, ranksep=0.35, fontname="Noto Serif", fontsize=11, bgcolor="transparent", pad=0.15];',
           '  node [shape=box, style="rounded,filled", fillcolor="#fbf6e9", color="#d4a843", fontname="Noto Serif", fontsize=11, penwidth=1.3, margin="0.1,0.05"];',
           '  edge [fontname="Noto Serif", fontsize=9, color="#4a5068", fontcolor="#4a5068", arrowsize=0.7];']
    clusters = list(spec["clusters"].items())
    for k, (cid, label) in enumerate(clusters):
        col = PAL[k % len(PAL)]
        out.append(f'  subgraph cluster_{cid} {{ label={q(label)}; color="{col}"; fontcolor="{col}"; style="rounded";')
        for nid, lab, c, _ in spec["nodes"]:
            if c == cid:
                out.append(f'    {nid} [label={q(lab)}];')
        out.append("  }")
    for nid, lab, c, _ in spec["nodes"]:
        if not c:
            out.append(f'  {nid} [label={q(lab)}];')
    for same in spec.get("same", []):
        out.append("  { rank=same; " + "; ".join(same) + "; }")
    for a, b, lab, style in spec["edges"]:
        attrs = []
        if lab:
            attrs.append(f"label={q(lab)}")
        if style == "dashed":
            attrs.append("style=dashed")
        if style == "triad":
            attrs += ["dir=none", 'color="#a0522d"', "penwidth=1.8"]
        out.append(f'  {a} -> {b} [{", ".join(attrs)}];')
    out.append("}")
    return "\n".join(out) + "\n"

def main():
    specs = json.loads((ROOT / "data" / "diagrams.json").read_text(encoding="utf-8"))
    for fid, spec in specs.items():
        svg = subprocess.run(["dot", "-Tsvg"], input=dot(spec).encode(), capture_output=True, check=True).stdout
        (ROOT / "docs" / f"fig-{fid}.svg").write_bytes(svg)
    print(f"diagrams: {len(specs)} rendered")

if __name__ == "__main__":
    main()
