<!-- © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI. -->

## What the work would cost: a model-based estimate {#ch-estimate}

How much work does the estate represent, and what would it cost a team to rebuild it, with AI in the process or without? The estimate kit in this guide's repository, under `estimate/`, answers with a recognised model rather than an opinion. It counts every tracked file of every repository once, leaving out vendored, generated, minified and third-party material, measures cyclomatic complexity, and applies COCOMO II.2000, then prices the effort with published salary data and the AI scenario with published token prices and the two controlled trials that bound AI's effect on developer speed. Every rate names its source in `estimate/rates.json`.

<!-- estimate -->

To run it on the whole estate: `bash estimate/estimate.sh --clone`, which clones every repository with full history, or `bash estimate/estimate.sh --root <folder of clones>`. The report also sets the model against the estate as it was actually built, from the distinct days in its git history, with hours per day and AI spend that the author sets in `rates.json`.

COCOMO prices the construction of what is written down. It does not price the research, the invention and the judgement behind it, so every figure here is a floor, not a valuation.
