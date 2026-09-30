# examples/numbers_demo.py: integers and reals as the machine holds them.
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import struct, unicodedata

print("Integers and reals")
v = 0x0A0B0C0D
print(f"   0x0A0B0C0D little-endian bytes: {struct.pack('<I', v).hex(' ')}   big-endian: {struct.pack('>I', v).hex(' ')}")
print(f"   -5 in 8-bit two's complement: {-5 & 0xFF:08b}   (256 - 5 = {256 - 5})")
print(f"   0.1 as an IEEE 754 double: {struct.pack('>d', 0.1).hex()} = {float.hex(0.1)}")
print(f"   0.1 + 0.2 == 0.3 is {0.1 + 0.2 == 0.3}; the sum is {0.1 + 0.2!r}")
