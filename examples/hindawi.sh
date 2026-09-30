#!/usr/bin/env bash
# examples/hindawi.sh: builds the Romenagri layer, the guru (C) shaili and the hincc driver of the
# Hindawi Programming System from vendor/chintamani, inside .work/, and runs one demonstration.
#
#   bash examples/hindawi.sh words    every Devanagari letter and some names in Romenagri, and back
#   bash examples/hindawi.sh sample   compiles and runs Hindawi's own sample, HindiC.uhin
#   bash examples/hindawi.sh yog      compiles and runs examples/yog.uhin, showing the C given to gcc
#   bash examples/hindawi.sh debug    the same program with debugging information: its ELF symbols,
#                                     DWARF names, a GDB session and addr2line, then all of it again
#                                     rendered through the Romenagri inverse
#   bash examples/hindawi.sh cover    one word through the hub and Romenagri from four scripts (the cover)
#   bash examples/hindawi.sh scripts  the Brahmi hub, any language in any script, and the corpus measurements
#   bash examples/hindawi.sh urdu     the Urdu edition: an Urdu-script C program compiled through the hub
#
# Needs gcc, make, flex with its library (libfl), gawk and iconv; debug also needs gdb and binutils.
# Everything happens under .work/ in this folder, which is removed at the end.
#
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
export LC_ALL=C.UTF-8
cd "$(dirname "$0")"
cd ..
MODE="${1:-words}"
PKG="$PWD"
W="$PKG/.work/hindawi"
rm -rf "$PKG/.work"
mkdir -p "$W/root/usr/bin" "$W/root/usr/lib" "$W/root/usr/include" "$W/run"
trap 'rm -rf "$PKG/.work"' EXIT

quiet() { "$@" > "$W/build.log" 2>&1 || { cat "$W/build.log"; exit 1; }; }
cp -r vendor/chintamani/Romenagri vendor/chintamani/Hindawi vendor/urdu-ilm/ILM "$W/"
quiet make -C "$W/Romenagri" all
quiet flex -8 -o"$W/Romenagri/flat.c" "$W/Romenagri/flatten_uni_dev.lex"
quiet gcc -o "$W/Romenagri/flatten_uni_dev" "$W/Romenagri/flat.c" -lfl
quiet make -C "$W/Romenagri" install INSTROOT="$W/root"
export PATH="$W/root/usr/bin:$PATH"
quiet make -C "$W/Hindawi/guru" all
quiet make -C "$W/Hindawi/guru" install INSTROOT="$W/root"
quiet make -C "$W/Hindawi/hindrv" install INSTROOT="$W/root"

to_rmn() { printf '%s' "$1" | iconv -f utf-8 -t utf-16 | uni2acii | acii2cf; }
from_rmn() { printf '%s' "$1" | rmn2acii | acii2uni | iconv -f utf-16 -t utf-8; }
RM="$W/Romenagri"
hub_of() {   # a word in any supported script, to the Devanagari hub
  case "$1" in
    te|bn) printf '%s\n' "$2" | "$RM/flatten_uni_dev" | tr -d '\r\n' ;;
    ur) printf '%s\n' "$2" | bash "$RM/fltr_ur_hi" | tr -d '\r\n' ;;
    *) printf '%s' "$2" ;;
  esac
}

case "$MODE" in
words)
  total=0; same=0; alphabet=1
  check() { total=$((total + 1)); [ "$1" = "$3" ] && same=$((same + 1)); printf '%s' "$2" | grep -q '^[A-Za-z_]*$' || alphabet=0; }
  echo "Letters, as Devanagari = Romenagri:"
  line=""; n=0
  for w in अ आ इ ई उ ऊ ऋ ए ऐ ओ औ क ख ग घ ङ च छ ज झ ञ ट ठ ड ढ ण त थ द ध न प फ ब भ म य र ल व श ष स ह ळ क़ ज़ फ़ ड़ ढ़ कं कः; do
    r="$(to_rmn "$w")"; b="$(from_rmn "$r")"; check "$w" "$r" "$b"
    line="$line$(printf '%s = %-6s ' "$w" "$r")"; n=$((n + 1))
    if [ "$n" -eq 6 ]; then echo "   $line"; line=""; n=0; fi
  done
  [ -n "$line" ] && echo "   $line"
  echo
  echo "Names, to Romenagri and back through the inverse:"
  for w in योग जोड़ो सीमा गिनती प्रकृति पितृ क्षि ज्ञान हृदय उत्तर क्षेत्रफल त्रिकोण ख कह क्ह; do
    r="$(to_rmn "$w")"; b="$(from_rmn "$r")"; check "$w" "$r" "$b"
    printf '   %s -> %s -> %s\n' "$w" "$r" "$b"
  done
  echo
  echo "$same of $total come back identical; every Romenagri form uses only A-Z, a-z and _: $([ "$alphabet" = 1 ] && echo yes || echo no)"
  ;;
sample)
  cp "$PKG/vendor/chintamani/Hindawi/samples/HindiC.uhin" "$W/run/"
  cd "$W/run"
  echo "\$ hincc HindiC.uhin"
  hincc HindiC.uhin
  echo
  echo "The C that gurucc handed to gcc:"
  tr -d '\r' < tempfil0123.tmphin.c
  echo
  echo "\$ ./hin.exe, with राम typed at both prompts"
  printf 'राम\nराम\n' | ./hin.exe
  ;;
yog|debug)
  cp "$PKG/examples/yog.uhin" "$W/run/"
  cd "$W/run"
  if [ "$MODE" = yog ]; then
    echo "\$ hincc yog.uhin"
    hincc yog.uhin
    echo
    echo "The C that gurucc handed to gcc:"
    tr -d '\r' < tempfil0123.tmphin.c
    echo
    echo "\$ ./hin.exe"
    ./hin.exe
    exit 0
  fi
  hincc yog.uhin > /dev/null
  gcc -g -O0 -fdebug-prefix-map="$PWD"=. -o yog-g tempfil0123.tmphin.c
  {
    echo "\$ nm --defined-only yog-g, the program's own symbols"
    nm --defined-only yog-g | awk '$2 ~ /^[TBD]$/ && $3 !~ /^(_start|_init|_fini|_edata|_end|__bss_start|__data_start|data_start|_IO_stdin_used|__dso_handle|__TMC_END__)$/ {print "   " $0}'
    echo
    echo "\$ readelf --debug-dump=info yog-g, the names DWARF records"
    readelf --debug-dump=info yog-g 2>/dev/null | awk '
      /DW_TAG_/ { tag = $0; sub(/.*DW_TAG_/, "", tag); sub(/[^a-z_].*/, "", tag) }
      /DW_AT_name/ && (tag == "subprogram" || tag == "variable" || tag == "formal_parameter") { n = $NF; print "   " tag " " n }'
    echo
    echo "\$ gdb -batch: break joa_rdoa, run, backtrace, info args, finish, print yoaga"
    gdb -q -nx -batch -ex 'break joa_rdoa' -ex 'run' -ex 'bt' -ex 'info args' -ex 'finish' -ex 'print yoaga' ./yog-g 2>&1 \
      | grep -v -E '^\[(Thread|Inferior)|libthread_db|^Using host|^Download|debuginfod' | sed 's/^/   /'
    echo
    addr="$(nm yog-g | awk '$3 == "joa_rdoa" {print $1}')"
    echo "\$ addr2line -f -s -e yog-g 0x$addr"
    addr2line -f -s -e yog-g "0x$addr" | sed 's/^/   /'
  } > transcript.txt
  cat transcript.txt
  echo
  echo "The same, rendered through the Romenagri inverse; the binary is unchanged:"
  python3 - transcript.txt "$W/Hindawi/guru/h2c.lex" <<'PY'
import re, subprocess, sys
text = open(sys.argv[1], encoding="utf-8").read()
# the C words the guru shaili has Hindi words for, read from its own lexer, the one gcc's input came from
lexer = open(sys.argv[2], encoding="latin-1").read()
c_words = set(re.findall(r'^\S+\s+\{printf\("([A-Za-z_][A-Za-z0-9_]*)"\);\}', lexer, re.M))
names = set(re.findall(r"^\s+[0-9a-f]+ [TBD] (\S+)$", text, re.M))
names |= set(re.findall(r"^\s+(?:subprogram|variable|formal_parameter) (\S+)$", text, re.M))
def sh(cmd, data):
    return subprocess.run(cmd, input=data, shell=True, capture_output=True).stdout
render = {}
for n in names:
    if n in c_words:               # a C name Hindawi has a word for: back through c2h, as std2hin does
        out = sh("c2h | sed 's/_/__/g' | rmn2acii | acii2uni | iconv -f utf-16 -t utf-8", n.encode())
    else:                          # a program's own name: straight back through the Romenagri inverse
        out = sh("rmn2acii | acii2uni | iconv -f utf-16 -t utf-8", n.encode())
    render[n] = out.decode("utf-8")
for n in sorted(render, key=len, reverse=True):
    text = re.sub(r"(?<![A-Za-z0-9_])" + re.escape(n) + r"(?![A-Za-z0-9_])", render[n], text)
print(text, end="")
PY
  ;;
cover)
  row() {
    hub="$(hub_of "$1" "$3")"; r="$(to_rmn "$hub")"; inv="$(from_rmn "$r" | tr -d '\r')"; back="$inv"
    [ "$1" = te ] && back="$(printf '%s\n' "$inv" | bash "$RM/fltr_hi_te" | tr -d '\r\n')"
    [ "$1" = bn ] && back=""
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$2" "$3" "$hub" "$r" "$inv" "$back"
  }
  row hi "Devanagari" "प्रकृति"
  row te "Telugu" "ప్రకృతి"
  row bn "Bengali" "প্রকৃতি"
  row ur "Urdu, as usually written" "ہندوی"
  row ur "Urdu, with zer and sukun" "ہِنْدوی"
  ;;
scripts)
  echo "1. The Brahmi hub: a word in Telugu or Bengali goes to Devanagari, to Romenagri, and back"
  for pair in "te ప్రకృతి" "te తెలుగు" "bn প্রকৃতি" "bn বাংলা"; do
    set -- $pair; hub="$(hub_of "$1" "$2")"; r="$(to_rmn "$hub")"; inv="$(from_rmn "$r" | tr -d '\r')"
    back="$inv"; [ "$1" = te ] && back="$(printf '%s\n' "$inv" | bash "$RM/fltr_hi_te" | tr -d '\r\n')"
    printf '   %s -> %s -> %s -> %s\n' "$2" "$hub" "$r" "$back"
  done
  echo
  echo "2. Any language in any script"
  printf '   Hindi written in Telugu script:    %s -> %s\n' "हिंदी भाषा" "$(printf '%s\n' 'हिंदी भाषा' | bash "$RM/fltr_hi_te" | tr -d '\r\n')"
  printf '   Telugu written in Devanagari:      %s -> %s\n' "తెలుగు భాష" "$(hub_of te 'తెలుగు భాష')"
  printf '   Urdu written in Devanagari:        %s -> %s\n' "ہندوی کتاب" "$(hub_of ur 'ہندوی کتاب')"
  printf '   the same, with zer and sukun:      %s -> %s\n' "ہِنْدوی کِتاب" "$(hub_of ur 'ہِنْدوی کِتاب')"
  echo
  echo "3. Measured on the corpora in this tree"
  python3 - "$RM" <<'PY'
import re, subprocess, sys
R = sys.argv[1]
def sh(cmd, s):
    return subprocess.run(cmd, input=s.encode(), shell=True, capture_output=True, cwd=R).stdout.decode("utf-8", "replace").replace("\r", "")
kernel = "iconv -f utf-8 -t utf-16 | uni2acii | acii2cf | rmn2acii | acii2uni | iconv -f utf-16 -t utf-8"
hi = sorted(set(re.findall(r"[\u0900-\u0963\u0971-\u097F]+", open(R + "/corp_hi.txt", encoding="utf-8").read())))
back = sh(kernel, "\n".join(hi) + "\n").split("\n")
same = sum(1 for w, x in zip(hi, back) if w == x)
print(f"   Hindi, words of letters and vowel signs: {len(hi)} distinct, {same} identical after Romenagri and back")
te = sorted(set(re.findall(r"[\u0C00-\u0C7F]+", open(R + "/corp_te.txt", encoding="utf-8").read())))
back = sh("./flatten_uni_dev | " + kernel + " | bash fltr_hi_te", "\n".join(te) + "\n").split("\n")
diff = [(w, x) for w, x in zip(te, back) if w != x]
uu = sum(1 for w, x in diff if "\u0C42" in w and "\u0942" in x)
print(f"   Telugu, through the hub and back: {len(te)} distinct, {len(te) - len(diff)} identical; of the {len(diff)} others, {uu} carry the long-u sign U+0C42, which fltr_hi_te returns as U+0942")
ur = re.findall(r"[\u0600-\u06FF]+", open(R + "/corp_ur.txt", encoding="utf-8").read())
marks = set("\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652")
print(f"   Urdu: {sum(1 for w in ur if any(c in marks for c in w))} of {len(ur)} words carry any zabar, zer, pesh, sukun, shadda or tanwin")
PY
  ;;
urdu)
  quiet make -C "$W/ILM/guru" all
  cp "$W/ILM/samples/UrduC.uhin" "$W/run/"
  cd "$W/run"
  echo "\$ urducc UrduC.uhin"
  bash "$W/ILM/urducc" UrduC.uhin
  echo
  echo "The C that reached gcc:"
  tr -d '\r' < tempfil0123.tmphin.c
  echo
  echo "\$ ./hin.exe, with Ali typed at the prompt"
  printf 'Ali\n' | ./hin.exe
  ;;
*)
  echo "usage: bash examples/hindawi.sh words|sample|yog|debug|cover|scripts|urdu"
  exit 2
  ;;
esac
