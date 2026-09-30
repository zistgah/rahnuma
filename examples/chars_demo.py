# examples/chars_demo.py: characters as the machine holds them.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import struct, unicodedata

print("1. The same letter KA in nine Unicode blocks: every block keeps ISCII's order, offset 0x15")
for name, base in [("Devanagari", 0x900), ("Bengali", 0x980), ("Gurmukhi", 0xA00), ("Gujarati", 0xA80),
                   ("Oriya", 0xB00), ("Tamil", 0xB80), ("Telugu", 0xC00), ("Kannada", 0xC80), ("Malayalam", 0xD00)]:
    ka, virama = chr(base + 0x15), chr(base + 0x4D)
    print(f"   {name:11s} block U+{base:04X}  KA U+{ord(ka):04X} {ka}   virama U+{ord(virama):04X}")

print("\n2. UTF-8 by hand for U+0915 (KA): 16 bits split 4 + 6 + 6 into 1110xxxx 10xxxxxx 10xxxxxx")
cp = 0x0915
bits = f"{cp:016b}"
b1, b2, b3 = 0xE0 | (cp >> 12), 0x80 | ((cp >> 6) & 0x3F), 0x80 | (cp & 0x3F)
print(f"   {bits[:4]} {bits[4:10]} {bits[10:]}  ->  {b1:08b} {b2:08b} {b3:08b}  =  {b1:02X} {b2:02X} {b3:02X}")
print(f"   Python agrees: {chr(cp).encode('utf-8').hex(' ').upper()}")
print(f"   the Devanagari block U+0900 to U+097F is {chr(0x900).encode().hex(' ').upper()} to {chr(0x97F).encode().hex(' ').upper()}")

print("\n3. Words are sequences of code points; aksharas are clusters of them")
for w in ["प्रकृति", "पितृ", "क्षि"]:
    cps = " ".join(f"U+{ord(c):04X}" for c in w)
    print(f"   {w}: {len(w)} code points, {len(w.encode('utf-8'))} UTF-8 bytes: {cps}")
print("   categories in क्षि: " + ", ".join(f"U+{ord(c):04X} {unicodedata.category(c)}" for c in "क्षि"))

print("\n4. Normalisation: QA U+0958 decomposes, and composition does not rebuild it")
qa = "\u0958"
nfd = unicodedata.normalize("NFD", qa)
print("   NFD(U+0958) = " + " ".join(f"U+{ord(c):04X}" for c in nfd))
print("   NFC(that)   = " + " ".join(f"U+{ord(c):04X}" for c in unicodedata.normalize("NFC", nfd)))
print(f"   equal as strings before normalising: {qa == nfd}; after NFC on both: {unicodedata.normalize('NFC', qa) == unicodedata.normalize('NFC', nfd)}")
