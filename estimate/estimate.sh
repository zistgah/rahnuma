#!/usr/bin/env bash
# estimate.sh: model-based size, complexity and cost estimate of the estate. Run it in any folder.
#
#   bash estimate.sh --clone                 clone every repository of the organisations below into ./estate,
#                                            with full history, then estimate
#   bash estimate.sh --root ~/shared/estate  estimate the repositories already under a folder (read only)
#   bash estimate.sh --root PATH --out DIR   choose the output folder (default ./estimate-out)
#
# Writes only inside this folder: ./estate, ./.estimate-venv and the output folder.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ORGS="${ORGS:-zistgah project-ilm hindawiai pvjournal ayeai obonac hmnsq kaivalyik c-polis}"
ROOT="" ; OUT="./estimate-out" ; CLONE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --clone) CLONE=1; ROOT="./estate" ;;
    --root) ROOT="${2:-}"; shift ;;
    --out) OUT="${2:-}"; shift ;;
    *) echo "usage: bash estimate.sh --clone | --root PATH [--out DIR]"; exit 2 ;;
  esac
  shift
done
[ -n "$ROOT" ] || { echo "usage: bash estimate.sh --clone | --root PATH [--out DIR]"; exit 2; }
for t in python3 git; do command -v "$t" >/dev/null || { echo "$t is not installed. Next: sudo apt install -y $t"; exit 1; }; done
for f in estimator.py rates.json model.json; do [ -f "$HERE/$f" ] || { echo "missing $f beside estimate.sh"; exit 1; }; done

if ! command -v lizard >/dev/null; then
  if [ ! -x ./.estimate-venv/bin/lizard ]; then
    echo "installing lizard, for cyclomatic complexity, into ./.estimate-venv"
    python3 -m venv ./.estimate-venv >/dev/null 2>&1 && ./.estimate-venv/bin/pip install -q lizard >/dev/null 2>&1 \
      || echo "note: lizard could not be installed; the estimate runs without complexity figures"
  fi
  [ -x ./.estimate-venv/bin/lizard ] && export PATH="$PWD/.estimate-venv/bin:$PATH"
fi

if [ "$CLONE" = 1 ]; then
  command -v gh >/dev/null || { echo "gh is not installed. Next: sudo apt install -y gh && gh auth login"; exit 1; }
  mkdir -p ./estate
  for org in $ORGS; do
    for repo in $(gh repo list "$org" --limit 1000 --json name,isEmpty -q '.[] | select(.isEmpty | not) | .name' 2>/dev/null); do
      d="./estate/$org/$repo"
      if [ -d "$d/.git" ]; then
        git -C "$d" fetch --quiet origin 2>/dev/null && git -C "$d" merge --ff-only --quiet 2>/dev/null
      else
        mkdir -p "./estate/$org"
        echo "cloning $org/$repo"
        git clone --quiet --filter=blob:none "https://github.com/$org/$repo.git" "$d" 2>/dev/null || echo "note: $org/$repo could not be cloned"
      fi
    done
  done
fi

[ -d "$ROOT" ] || { echo "no folder $ROOT"; exit 1; }
mapfile -t REPOS < <(find -L "$ROOT" -maxdepth 4 -type d -name .git -prune -printf '%h\n' | sort -u)
[ "${#REPOS[@]}" -gt 0 ] || { echo "no git repositories under $ROOT"; exit 1; }
echo "estimating ${#REPOS[@]} repositories under $ROOT"
python3 "$HERE/estimator.py" --repos "${REPOS[@]}" --out "$OUT" || exit 1
if command -v pandoc >/dev/null; then pandoc "$OUT/report.md" -o "$OUT/report.docx" && echo "also $OUT/report.docx"; fi
echo "Next: read $OUT/report.md; edit rates.json and model.json to your own figures and rerun"
