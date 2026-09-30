# examples/ud_check.py: is a transliteration code reversible? The Sardinas-Patterson test and
# the Kraft-McMillan sum, on four small codes.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
from fractions import Fraction

def dangling(a_set, b_set):
    """Suffixes left over when a word of a_set is a proper prefix of a word of b_set."""
    return {b[len(a):] for a in a_set for b in b_set if b.startswith(a) and len(b) > len(a)}

def uniquely_decodable(code):
    """Sardinas-Patterson (1953): the code is uniquely decodable iff no dangling suffix,
    at any stage, is itself a codeword."""
    code = set(code)
    s, seen = dangling(code, code), set()
    while s:
        if s & code:
            return False
        key = frozenset(s)
        if key in seen:
            return True
        seen.add(key)
        s = dangling(code, s) | dangling(s, code)
    return True

def kraft(code):
    alphabet = {ch for w in code for ch in w}
    return len(alphabet), sum(Fraction(1, len(alphabet) ** len(w)) for w in code)

def parses(text, code):
    if not text:
        return [[]]
    return [[w] + rest for w in sorted(code) if text.startswith(w) for rest in parses(text[len(w):], code)]

CODES = {
    "naive: k, h, kh": ["k", "h", "kh"],
    "Romenagri's choice: k, _h, kh": ["k", "_h", "kh"],
    "not prefix-free: a, ab, bb": ["a", "ab", "bb"],
    "prefix code: 0, 10, 110, 111": ["0", "10", "110", "111"],
}
for name, code in CODES.items():
    d, s = kraft(code)
    print(f"{name:30s} D={d}  Kraft sum={str(s):6s} ({float(s):.3f})  uniquely decodable: {uniquely_decodable(code)}")
print()
for text in ["kh", "khk"]:
    ps = parses(text, CODES["naive: k, h, kh"])
    print(f'"{text}" under the naive code has {len(ps)} readings: ' + "; ".join(" + ".join(p) for p in ps))
ps = parses("abbb", CODES["not prefix-free: a, ab, bb"])
print(f'"abbb" under a, ab, bb has {len(ps)} reading: ' + "; ".join(" + ".join(p) for p in ps))
