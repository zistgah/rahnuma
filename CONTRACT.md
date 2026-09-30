# CONTRACT: Rahnuma

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

Each clause is checked by `bash ops/verify.sh`, which prints PASS, FAIL or UNJUDGED for each and exits non-zero when anything fails. UNJUDGED means a tool the check needs is absent, for example flex or gawk for the Hindawi build; it is reported and never counted as a pass.

| Clause | Rule |
|:-------|:-----|
| R01 | Every source file carries the copyright line; every script also carries its SPDX licence line. Files under `vendor/` are retrieved verbatim and keep their own notices, and Hindawi programs (`*.uhin`) are exempt because their ISCII script layer has no code for ©. |
| R02 | No affiliation other than AyeAI is claimed. |
| R03 | Every example the guide shows as executed produces, when run again, exactly the output printed in the guide. |
| R04 | The published guide was built from the sources in this repository: every input's hash matches `docs/BUILD.json`. |
| R05 | No em dash appears anywhere; an en dash appears only inside the copyright line. Verbatim files under `vendor/chintamani/` are not rewritten. |
| R06 | `CITATION.cff` and `misty.json` agree on title, version and licence, and no placeholder DOI appears. |
| R07 | `LICENSE` is the FSF's verbatim GPL-3.0 text and `LICENSE-docs` is the CC BY-SA 4.0 legal code. |
| R08 | No build artefacts are committed: no caches, compiled files, archives, `node_modules` or work folders. |
| R09 | No script names a path outside this folder. |
| R10 | Every internal link in the site resolves to an anchor that exists. |
| R11 | Every estate repository the guide links to is in the retrieved listing, `data/estate-snapshot.json`. |
| R12 | The site, the Markdown file and the PDF are present and match the hashes recorded in `docs/BUILD.json`. |
