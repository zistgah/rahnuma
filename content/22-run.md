<!-- © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI. -->

## Running every component {#ch-run}

Every repository can be cloned with `git clone https://github.com/<organisation>/<repository>.git` and read, and most have a live page. This chapter gives the commands to run each component. The first four were executed for this guide and their output appears in these pages; the rest are quoted from each repository's README as retrieved on 29 September 2026. Set up the machine first (Chapters [[ch-06]] and [[ch-07]]); for Hindawi also install `flex`, `libfl-dev` and `gawk`.

### Hindawi and Romenagri

The repository's own `install` script installs the whole system into `/usr/bin`, including its KDE-era interfaces. These lines build only the command-line toolchain, into a folder inside the clone:

```bash
git clone https://github.com/hindawiai/chintamani.git && cd chintamani
mkdir -p .root/usr/bin .root/usr/lib .root/usr/include
make -C Romenagri all && make -C Romenagri install INSTROOT="$PWD/.root"
export PATH="$PWD/.root/usr/bin:$PATH"
make -C Hindawi/guru all && make -C Hindawi/guru install INSTROOT="$PWD/.root"
make -C Hindawi/hindrv install INSTROOT="$PWD/.root"
cp Hindawi/samples/HindiC.uhin . && hincc HindiC.uhin && ./hin.exe
```

To see a word in Romenagri and back:

```bash
printf 'प्रकृति' | iconv -f utf-8 -t utf-16 | uni2acii | acii2cf; echo
printf 'prak_ri_ti' | rmn2acii | acii2uni | iconv -f utf-16 -t utf-8; echo
```

To bring a Telugu, Bengali or other Brahmi-script word to the Devanagari hub, build the flattening lexer, and use the filters beside it for other directions:

```bash
flex -8 -oRomenagri/flat.c Romenagri/flatten_uni_dev.lex
gcc -o Romenagri/flatten_uni_dev Romenagri/flat.c -lfl
echo 'ప్రకృతి' | Romenagri/flatten_uni_dev          # Telugu to the hub
echo 'प्रकृति' | bash Romenagri/fltr_hi_te           # the hub to Telugu
echo 'ہِنْدوی' | bash Romenagri/fltr_ur_hi           # Urdu to the hub
```

### The Urdu edition

zistgah/urdu-ilm (default branch `master`) carries the Urdu shailis and the driver `urducc`, which sends an Urdu-script program through the Devanagari hub and Romenagri. It uses the standard Hindawi driver from the build above:

```bash
git clone https://github.com/zistgah/urdu-ilm.git && cd urdu-ilm
mkdir -p .root/usr/bin .root/usr/lib .root/usr/include
make -C Romenagri all && make -C Romenagri install INSTROOT="$PWD/.root"
export PATH="$PWD/.root/usr/bin:$PATH:<path to chintamani>/.root/usr/bin"
make -C ILM/guru all
bash ILM/urducc -s ILM/samples/UrduC.uhin     # show the C it generates
bash ILM/urducc ILM/samples/UrduC.uhin && ./hin.exe
```

Replace `<path to chintamani>` with the folder of the clone above.

### PANINIq

Chapter [[ch-07]] gives the commands and the recorded run: tests, the demonstration and the repository's own gate.

### This guide

```bash
git clone https://github.com/zistgah/rahnuma.git && cd rahnuma
bash ops/verify.sh                         # the twelve clauses, re-running every example
bash examples/hindawi.sh words             # also: sample, yog, debug, cover, scripts, urdu
python3 tools/build.py                     # rebuild the site, the Markdown and the PDF
```

### Components run from the command line

| Component | Commands, from its README | What you get |
|:----------|:---------------------------------|:-------------------|
| zistgah/panini | `python3 panini.py check cyclers/pench.pni`; `python3 panini.py stages cyclers/yadein.pni`; `python3 panini.py prompt cyclers/matba.pni`; `python3 panini.py serve` | static checks, the stages at each resolution, a cycle's first prompt, the studio on 127.0.0.1:8717 |
| zistgah/panini_by_claude | `node bin/panini.mjs conformance`; `npm test` | the conformance report; 145 assertions |
| zistgah/panini_by_grok | `node src/cli.js run examples/hello.pni`; `node tests/run.mjs`; `node scripts/bootstrap.mjs` | a PANINI program run; the tests; the bootstrap |
| zistgah/humanesque | `bash VERIFY.sh` | 36 checks on the merged release |
| zistgah/paninib | `python3 panini compile examples/replace.panini -o out`; `python3 panini inspect out --stage sequence-ir`; `python3 panini verify out` | a biological intent lowered to sequence IR, inspected and verified |
| zistgah/paniniphy | `python3 panini compile examples/modular_block.panini -o out`; `python3 panini parts --category actuator --force 50N --stroke 20mm --voltage 12V` | a physical intent compiled; parts selected by requirement |
| zistgah/matba | `python3 matba.py serve` | the press on 127.0.0.1:8710 |
| zistgah/khwab | `python3 khwab.py serve` | the cutting room on 127.0.0.1:8711 |
| zistgah/awaz | `python3 awaz.py serve` | the listening room on 127.0.0.1:8712 |
| zistgah/mez | `./mez doctor`; `./mez bearings`; `./mez serve` | what is built and installed; where you are; the desk on 127.0.0.1:7373 |
| zistgah/alam | `node test/alam-test.js`; `node test/dom-test.js` | the engine and its vendor-neutrality gate; a full cycle driven in the real page |
| zistgah/tajziya | `python3 -m tajziya commonalities`; `make check` | the commonality computation; the gate |
| project-ilm/chakra | `node test/run.js` | 10 suites and 115 assertions; open `index.html` for the observatory |
| zistgah/jyotish | open `index.html`; `bash ops/verify.sh` | the panchang, offline; its gate |
| zistgah/transeg | `./scripts/bootstrap.sh --dry-run`; `./scripts/bootstrap.sh`; `docker compose -f compose/docker-compose.yml --profile tts up -d --build` | the stand-up plan; the stand-up; the services with speech |
| zistgah/transeg-idgov | `python3 tools/idgov_validate.py policies`; `python3 -m pytest tests/` | the eight stage policies checked; the tests |
| project-ilm/qedler | `bash ops/verify.sh`; `bash ops/resume.sh && cat RESUME.md` | the contract check; the generated state |
| zistgah/jugaad28, zistgah/ertabat | `bash ops/verify.sh` | each repository's gate |
| zistgah/zamin | `cd spice && ngspice sign_frustration_tb.sp`; `python layout/pratik_fluidic_interposer.py` | a SPICE testbench of the ternary cells; the microfluidic interposer layout |
| zistgah/pratik_core_mvp | `./build.sh cuda` | the kernel built for CPU and CUDA |
| project-ilm/research-kundali | `python3 kundali/kundali.py <ORCID, lab name or DOI> --out out` | a research map of a person, a lab or a paper |
| project-ilm/misty-doi | `pip install misty-doi`; `misty init`; `misty publish -m misty.json -f artifact.zip --output result.json` | the DOI tool, a metadata file, a deposit |
| project-ilm/linguistics-labs | `docker build -t ilm-lab .`; `docker run --rm -p 8888:8888 -v "$PWD":/lab ilm-lab` | the starter linguistics lab on localhost:8888 |
| zistgah/estate | `bash seed_estate.sh` | the inventory of the estate |

### Components you open in a browser

| Component | Page |
|:----------|:-----|
| FAKIR's explorer, the domain lattice | [zistgah.github.io/fakir](https://zistgah.github.io/fakir/) |
| The shared dome | [zistgah.github.io/dome](https://zistgah.github.io/dome/) |
| GENIE | [zistgah.github.io/genie](https://zistgah.github.io/genie/) |
| AAB | [zistgah.github.io/aab](https://zistgah.github.io/aab/) |
| The cycler studios: tilasm, pench, yadein | [tilasm](https://zistgah.github.io/tilasm/), [pench](https://zistgah.github.io/pench/), [yadein](https://zistgah.github.io/yadein/) |
| Dhancha, the domain spine | [zistgah.github.io/dhancha](https://zistgah.github.io/dhancha/) |
| Tok DOI, the registrar | [project-ilm.github.io/tok-doi](https://project-ilm.github.io/tok-doi/) |
| CHAKRA and Jyotish | [project-ilm.github.io/chakra](https://project-ilm.github.io/chakra/), [zistgah.github.io/jyotish](https://zistgah.github.io/jyotish/) |
| ILM, with its explorer and registry | [ilm.codes](https://ilm.codes/) |
| PANINI's studio | [zistgah.github.io/panini](https://zistgah.github.io/panini/) |
| The estate index | [zistgah.org](https://zistgah.org/) |
