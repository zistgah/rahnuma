#!/usr/bin/env bash
# ops/review.sh: mark one object of the guide as reviewed by the author. Run it in the repository.
#   bash ops/review.sh <object-id> [note]        e.g.  bash ops/review.sh ch-11 checked the Urdu examples
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: bash ops/review.sh <object-id> [note]; the identifiers are listed in Appendix G"; exit 2; }
python3 tools/review.py mark "$@"
