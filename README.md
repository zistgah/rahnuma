# Rahnuma

A working guide to the ILM, PANINI and Zistgah stack, from bytes and scripts to compilers, Pāṇini and quantum substrates. Read it at [zistgah.github.io/rahnuma](https://zistgah.github.io/rahnuma/), as a PDF in [docs/rahnuma.pdf](docs/rahnuma.pdf), or as one Markdown file in [docs/rahnuma.md](docs/rahnuma.md), which is also the file to give an AI.

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

## What it covers

| Part | Chapters |
|:-----|:---------|
| I. Orientation | How to use the guide; the work, not the worker |
| II. The estate | Architecture; every public repository with its DOI; the dated record |
| III. Setting up | Ubuntu, WSL 2, native Windows and macOS; the baseline environment; a first run of PANINIq; containers and labs |
| IV. Foundations | Numbers; characters and encodings; writing systems and reversible transliteration; Pāṇini as a formal system; compilers; chips, ternary and qubits; quantum computing and PANINIq |
| V. Working with the estate | AI from MYCIN to transformers and how to use any AI here; open source, provenance and contributing; GATE 2027; questions answered technically |
| VI. Status | This release and the next |

## Status

| Piece | Status |
|:------|:-------|
| The examples in `examples/` | **Executed** while the guide was built; `ops/verify.sh` runs them again and compares their output |
| The cover, the cross-script demonstration and the Urdu edition (`examples/hindawi.sh cover`, `scripts`, `urdu`) | **Executed** from `vendor/chintamani` and `vendor/urdu-ilm`; the gate re-runs them |
| Hindawi's C shaili with Romenagri (`examples/hindawi.sh`) | **Executed**: built from `vendor/chintamani` with its own Makefiles, then used to compile and run Hindi programs; the GDB and symbol-table session is **captured**, since addresses depend on the machine |
| The GCC listing in Chapter 13 | **Captured** while the guide was built; it depends on the compiler's version |
| The PANINIq run in Chapter 7 | **Executed** on 29 September 2026 at commit 82a5cf2, recorded in `data/logs/` |
| Commands quoted from other repositories | Quoted from their READMEs, not executed here |
| Facts about the repositories | Retrieved from GitHub and each repository's own files on 29 September 2026, in `data/` |
| Lab launch scripts | **Planned** for the next release |

## Build and check

On Ubuntu:

```bash
sudo apt install -y pandoc nodejs npm gcc make flex libfl-dev gawk gdb python3-venv
python3 -m venv ~/work/venv-rahnuma && . ~/work/venv-rahnuma/bin/activate
pip install playwright pypdf && python3 -m playwright install --with-deps chromium
npm ci --prefix tools
python3 tools/build.py
bash ops/verify.sh
```

`tools/build.py` runs every example, writes its real output into the text and builds `docs/`. `ops/verify.sh` checks every clause of [CONTRACT.md](CONTRACT.md). Where this sits in the estate is in [CONTEXT.md](CONTEXT.md); how any person or AI should work on it is in [AGENTS.md](AGENTS.md); where each fact came from is in [PROVENANCE.md](PROVENANCE.md).

## Licence

The text is licensed CC BY-SA 4.0 ([LICENSE-docs](LICENSE-docs)); the scripts are GPL-3.0-or-later ([LICENSE](LICENSE)). The typefaces in `docs/fonts/` are under the SIL Open Font Licence, with their licences beside them. MathJax is used at build time only. Cite it with [CITATION.cff](CITATION.cff).
