# CONTEXT: Rahnuma

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

Read this first, cold.

**What it is.** One guide to the whole estate, built from one source into a site (`docs/index.html`, served by GitHub Pages from `/docs`), a PDF (`docs/rahnuma.pdf`) and a single Markdown file (`docs/rahnuma.md`), with `docs/llms.txt` as the index for AI readers. Version 2.0.0, 29 September 2026. The name, रहनुमा, رہنما, means the guide; the slug `zistgah/rahnuma` can be renamed without changing anything inside.

**Where it sits.** It documents the Humanesque substrate and its projections, the PANINI stack from the ILM front end to realisation backends such as PANINIq, the cyclers, the habitat elements and the provenance systems, as the author has laid them out. It adds no component of its own; its examples are teaching code.

**How it is made.** `content/*.md` holds the chapters. Directives in them are expanded by `tools/build.py`: `run` executes a command and prints its real output, and the gate runs it again; `capture` records output that depends on the machine, such as a compiler listing; `include`, `log`, `estate`, `records`, `counts` and `md` bring in files and the retrieved data. Mathematics is rendered to SVG at build time; the PDF is printed by Chromium. `vendor/chintamani/` holds Romenagri and Hindawi's C front end exactly as retrieved; `examples/hindawi.sh` builds them inside `.work/` and runs them, so the guide's account of the script layer is the tools' own output.

**State.** Built, gated and ready to seed with `seed_rahnuma.sh`. The next release adds the lab launch scripts, dockerised and retrieved from the existing repositories.

**Open.** The glossary, the architecture and the record follow the author's own files; any correction to them is his call.

**Version policy.** A release that changes how the guide is entered or organised is a new major version. The previous major version moves, unchanged, to `docs/v<N>/`, with its own `MANIFEST.sha256`, and the cover links to it. A frozen version is never edited. Version 1, the edition for advanced readers, is at `docs/v1/`.

**Privacy, stated once for the estate.** Rahnuma keeps only the official address of each syllabus and its own keywords. A syllabus is read in the reader's browser, from a page or a file the reader opens, and is never uploaded, stored or sent. A reader's choices stay in that browser. Other repositories point here rather than repeating it.

**Review marks.** Every chapter, figure, component card, syllabus module and link, edition and proposed name is an object with an identifier in `data/review.json`; the author marks one with `bash ops/review.sh <identifier> [note]`.

**Personal data.** No personal data of the author's beyond what he publishes on purpose, his ORCID and his GitHub handle, may appear in the guide; `tools/pii_scan.py` checks every source and the gate fails on a find.

**Projections.** Kaivalyik, Zistgah and Cosmopolis are established; their names other than Zistgah's, and the Datong and Vaka projections, are proposals for the author's ruling.

**Deposits.** Besides the guide's own record, four document families are deposited as their own records, each a supplement to the guide: the reader editions, the syllabus links with the draft syllabus, the estimate, and the roadmap. Their descriptors are generated in `deposits/` by the build and minted by `bash seed_rahnuma.sh --deposits`.
