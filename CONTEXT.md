# CONTEXT: Rahnuma

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

Read this first, cold.

**What it is.** One guide to the whole estate, built from one source into a site (`docs/index.html`, served by GitHub Pages from `/docs`), a PDF (`docs/rahnuma.pdf`) and a single Markdown file (`docs/rahnuma.md`), with `docs/llms.txt` as the index for AI readers. Version 1.0.0, 29 September 2026. The name, रहनुमा, رہنما, means the guide; the slug `zistgah/rahnuma` can be renamed without changing anything inside.

**Where it sits.** It documents the Humanesque substrate and its projections, the PANINI stack from the ILM front end to realisation backends such as PANINIq, the cyclers, the habitat elements and the provenance systems, as the author has laid them out. It adds no component of its own; its examples are teaching code.

**How it is made.** `content/*.md` holds the chapters. Directives in them are expanded by `tools/build.py`: `run` executes a command and prints its real output, and the gate runs it again; `capture` records output that depends on the machine, such as a compiler listing; `include`, `log`, `estate`, `records`, `counts` and `md` bring in files and the retrieved data. Mathematics is rendered to SVG at build time; the PDF is printed by Chromium. `vendor/chintamani/` holds Romenagri and Hindawi's C front end exactly as retrieved; `examples/hindawi.sh` builds them inside `.work/` and runs them, so the guide's account of the script layer is the tools' own output.

**State.** Built, gated and ready to seed with `seed_rahnuma.sh`. The next release adds the lab launch scripts, dockerised and retrieved from the existing repositories.

**Open.** The glossary, the architecture and the record follow the author's own files; any correction to them is his call.
