# examples/ternary.py: balanced ternary, the number system of Zamin and PRATIK.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import math

def to_bt(n):
    """Digits in {-1, 0, +1}, written 1, 0, T (T stands for -1), most significant first."""
    if n == 0:
        return "0"
    digits = []
    while n:
        r = n % 3
        if r == 2:
            r, n = -1, n + 1
        digits.append({1: "1", 0: "0", -1: "T"}[r])
        n //= 3
    return "".join(reversed(digits))

def from_bt(s):
    return sum({"1": 1, "0": 0, "T": -1}[c] * 3 ** i for i, c in enumerate(reversed(s)))

def negate(s):
    return s.translate(str.maketrans("1T", "T1"))

for n in [5, -5, 13, 40, -121, 2026]:
    s = to_bt(n)
    assert from_bt(s) == n and from_bt(negate(s)) == -n
    print(f"{n:6d} = {s:>9s}   negated by flipping every digit: {negate(s):>9s} = {from_bt(negate(s))}")
print()
for b in [2, math.e, 3, 4, 10]:
    print(f"radix economy b/ln b for b = {b:.3f}: {b / math.log(b):.4f}")
