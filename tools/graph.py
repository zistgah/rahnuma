#!/usr/bin/env python3
# tools/graph.py: renders data/graph.json, the estate's dependency graph, to DOT and SVG.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLOURS = {"core": "#d4a843", "identity": "#23408e", "computation": "#2e6b5e", "cognition": "#7a3e65",
           "triad": "#a0522d", "knowledge": "#4a5068", "habitat": "#6b5b2e", "social": "#3f6b2e",
           "provenance": "#555555"}

LINKS = {"core": "#ch-families", "identity": "#ch-11", "computation": "#ch-03", "cognition": "#ch-15",
         "triad": "#ch-families", "knowledge": "#ch-onto", "habitat": "#ch-03", "social": "#ch-families",
         "provenance": "#ch-17"}
NODE_LINKS = {"hps": "#ch-13", "hindawi": "#ch-13", "urdu": "#ch-13", "host": "#ch-13", "humanesque": "#ch-03",
              "qedler": "#ch-onto", "cem": "#ch-onto", "zamin": "#ch-14", "pratik": "#ch-14", "chakra": "#ch-families",
              "jyotish": "#ch-families", "vgc": "#ch-onto", "copa": "#ch-onto", "paniniq": "#ch-15", "pedler": "#ch-15"}

def dot_text(g):
    q = lambda s: '"' + s.replace('"', '\\"').replace("\n", "\\n") + '"'
    out = ['digraph estate {', '  graph [rankdir=LR, newrank=true, nodesep=0.12, ranksep=0.35, fontname="Noto Serif", fontsize=11, bgcolor="transparent", pad=0.2];',
           '  node [shape=box, style="rounded,filled", fillcolor="#fbf6e9", fontname="Noto Serif", fontsize=10, penwidth=1.4, margin="0.08,0.04"];',
           '  edge [fontname="Noto Serif", fontsize=8, color="#4a5068", arrowsize=0.6, fontcolor="#4a5068"];']
    for cid, title in g["clusters"].items():
        out.append(f'  subgraph cluster_{cid} {{ label={q(title)}; color="{COLOURS[cid]}"; fontcolor="{COLOURS[cid]}"; style="rounded"; penwidth=1.2;')
        for nid, label, c in g["nodes"]:
            if c == cid:
                href = NODE_LINKS.get(nid, LINKS[cid])
                tip = label.replace("\n", ", ")
                out.append(f'    {nid} [label={q(label)}, color="{COLOURS[cid]}", href="{href}", tooltip={q(tip)}];')
        out.append('  }')
    for a, b, rel in g["edges"]:
        attrs = f'label={q(rel)}' if rel else ''
        if rel == "triad":
            attrs = 'label="", dir=none, penwidth=1.6, color="#a0522d"'
        out.append(f'  {a} -> {b} [{attrs}];')
    out.append('}')
    return "\n".join(out) + "\n"

def main():
    g = json.loads((ROOT / "data" / "graph.json").read_text(encoding="utf-8"))
    ids = {n[0] for n in g["nodes"]}
    bad = [e for e in g["edges"] if e[0] not in ids or e[1] not in ids]
    if bad:
        sys.exit(f"graph: edges name unknown nodes: {bad}")
    dot = dot_text(g)
    (ROOT / "docs" / "dependency-graph.dot").write_text(dot, encoding="utf-8")
    svg = subprocess.run(["dot", "-Tsvg"], input=dot.encode(), capture_output=True, check=True).stdout
    (ROOT / "docs" / "dependency-graph.svg").write_bytes(svg)
    print(f"graph: {len(g['nodes'])} nodes, {len(g['edges'])} edges")

if __name__ == "__main__":
    main()
