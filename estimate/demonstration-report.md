# Model-based estimate of the estate's work

Generated 2026-10-04T04:24:50Z over 38 repositories. Every figure below is computed from the repositories' tracked files and history and from `rates.json` and `model.json`, which name their sources.

## What was measured

| Measure | Value |
|:--|--:|
| Repositories | 38 |
| Source lines of code, each file counted once | 243,719 |
| Lines in files repeated across repositories, not counted again | 341,227 |
| Words of prose: Markdown, TeX, text, notebooks | 368,689 |
| Figures and images over 150 KB | 99 |
| Commits; sum of distinct active days per repository | 382; 110 |
| Files left out as vendored, third-party, generated or minified | 7,444 |
| Repositories cloned shallow, so their history is not measured | 35 |
| Functions measured for complexity (lizard) | 9,288 |
| Functions with cyclomatic complexity above 10; above 20 | 546; 191 |

| Language | Files | SLOC |
|:--|--:|--:|
| JavaScript | 377 | 55,148 |
| HTML | 321 | 52,291 |
| PANINI | 246 | 37,340 |
| Python | 327 | 36,487 |
| C | 262 | 24,935 |
| Hindawi | 205 | 18,700 |
| TypeScript | 24 | 6,529 |
| Shell | 56 | 3,358 |
| Notebook | 24 | 2,268 |
| Assembly | 9 | 1,098 |
| Makefile | 46 | 1,057 |
| C header | 13 | 914 |
| BASIC | 21 | 691 |
| CSS | 14 | 652 |
| C++ | 49 | 614 |

## Effort, by COCOMO II

Effort in person-months of 152 hours. *Sum of repositories* treats each repository as its own project; *integrated* treats the estate as one system, where the model's diseconomy of scale applies to the whole.

| Case | Sum of repositories | Integrated | Schedule, integrated | Documentation | Figures |
|:--|--:|--:|--:|--:|--:|
| low | 645 PM | 701 PM | 27.1 months | 13 PM | 1 PM |
| likely | 997 PM | 1,239 PM | 35.3 months | 19 PM | 2 PM |
| high | 1,616 PM | 2,279 PM | 47.3 months | 39 PM | 5 PM |

## Cost to rebuild it with a conventional team

Integrated software effort plus documentation and figures, at loaded rates.

| Region | Low | Likely | High |
|:--|--:|--:|--:|
| India | ₹12.85 crore | ₹40.97 crore | ₹130.68 crore |
| United States | $7.51 million | $18.57 million | $49.94 million |

## The same work with AI in the process

The work's own text is about 3.0 million tokens. AI cost multiplies it by redrafts and by the context read for each draft; human effort is the likely COCOMO effort times the measured range of time ratios.

| Case | Time with AI over without | Human effort | AI usage | Human cost, India | Human cost, United States |
|:--|--:|--:|--:|--:|--:|
| low | 0.44 | 554 PM | $140 (sonnet class) | ₹18.00 crore | $8.16 million |
| likely | 0.75 | 944 PM | $578 (sonnet class) | ₹30.68 crore | $13.91 million |
| high | 1.19 | 1,498 PM | $5,861 (opus class) | ₹48.68 crore | $22.07 million |

## As built

Git history shows 54 distinct days with at least one commit across all repositories, from 2016-09-16 to 2026-09-28.
35 of the repositories were cloned shallow, so their history is not counted here; run with `--clone` for full history.

| Hours per active day | Person-months as built | Likely COCOMO effort over this |
|:--|--:|--:|
| 4 | 1.4 | 886 times |
| 8 | 2.8 | 443 times |
| 12 | 4.3 | 295 times |

AI spend over the period: not entered; set as_built.ai_spend_usd in rates.json.

## What the model cannot see

COCOMO estimates the construction of software of a given size. It does not price invention: the research, the design of the architecture, the formal frameworks, the decades of prior work that made the code possible, or the judgement in what was left out. Lines of code measure size, not novelty. Read every figure here as a floor for the intellectual work, and as a fair estimate only of what it would cost a team to rebuild what is now written down.

## Sources and assumptions

- COCOMO II: COCOMO II.2000 post-architecture model (Boehm et al., Software Cost Estimation with COCOMO II, 2000): PM = A x KSLOC^E x product(EM), E = B + 0.01 x sum(SF), TDEV = C x PM^F, F = D + 0.2 x (E - B). Scale-factor sums: all High 12.65, all Nominal 18.97, all Low 25.28.
- Rates, India: Senior developer and architect bands for 2026: senior developers about 18 to 45 lakh a year (futurense.com, August 2026); software architects 28.5 to 38.8 lakh (AmbitionBox via wisemonk.io, August 2026)
- Rates, United States: BLS OEWS May 2025, Software Developers, SOC 15-1252: median 135,980 USD; quartile band 105,210 to 171,980 USD (as republished by hyring.com)
- Exchange rate: 96.0 rupees per dollar; USD/INR about 95.95 on 16 September 2026 (longforecast.com, 'USD to INR today'); set to the day's rate before use
- Loaded cost factor 1.3: assumption: employer overheads over salary; set to your own figure
- AI prices: Anthropic list prices per million tokens, Opus, Sonnet and Haiku tiers, as published mid-2026 (fast.io and finout.io summaries of the official page); cache reads at one tenth of input. Check anthropic.com/pricing for the models you use.
- Tokens: Anthropic's tokenizer averages about one token per four characters (lmmarketcap.com)
- AI time ratios: Time with AI over time without. 0.44: Peng et al. 2023, Copilot RCT, a greenfield task done 55.8% faster (161 to 71 minutes). 1.19: METR RCT, July 2025, experienced developers on their own mature repositories, 19% slower. 0.75 is an assumption between the two; METR notes developers in 2026 are likely faster than its early-2025 estimate.
- AI usage: assumption: drafts produced per final token, input tokens read per output token, model tier, and share of input served from the prompt cache; text sized at 40 characters per line and 6 per word (assumption: average characters per source line and per word of prose, used only to size the AI scenario)
- Left out: directories .git, .venv, __pycache__, build, corpora, corpus, dist, extern, external, generated, node_modules, retrieved, site-packages, third_party, thirdparty, vendor, venv; files that declare themselves generated; word lists; and named paths (generated output, third-party specifications and tools, and machine conversions of third-party code (humanesque's retrieved/ holds the ECMA-262, Go, Zig and Lua specifications and a Hindawi conversion of SeaBIOS) found on inspection, 3 October 2026; add any others in your estate; humanesque's hindawi/<script>/<language>/ trees are, in its README's words, generated from one CSV by one generator)
- Writing: assumption: finished technical prose per writer-day; set to your own figure
- Figures: assumption: hours per finished figure or poster image above the size threshold; set to your own figure
