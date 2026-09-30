<!-- © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI. -->

# Part IV: Foundations {#part-iv}

## Numbers inside the machine {#ch-09}

A processor holds voltages that stand for bits. Everything else on this page, including the hexadecimal digits, is notation for people.

### Positional notation

A number written with digits $d_i$ in base $b$ is

$$ n = \sum_{i=0}^{k-1} d_i\, b^{i}, \qquad 0 \le d_i < b . $$

So $42 = 101010_2 = 2\mathrm{A}_{16}$: the letters A to F are simply names for the values ten to fifteen, chosen so that one hexadecimal digit covers exactly four bits. The machine never sees the letter A, any more than it sees the letters of a keyword in a program.

### Signed integers: two's complement

With $n$ bits $b_{n-1}\dots b_0$, the value is

$$ v = -\,b_{n-1}\,2^{n-1} + \sum_{i=0}^{n-2} b_i\, 2^{i}, \qquad -2^{n-1} \le v \le 2^{n-1}-1 . $$

Negative $x$ is therefore stored as $2^n - |x|$. The payoff is that one adder serves signed and unsigned arithmetic alike, which is why every processor in use works this way.

### Reals: IEEE 754

A double-precision number has a sign bit $s$, eleven exponent bits $e$ and fifty-two fraction bits $f$, and for normal numbers

$$ v = (-1)^{s} \times (1.f)_2 \times 2^{\,e-1023}. $$

One tenth has no finite binary expansion, so it is stored rounded, and sums of rounded values are rounded again.

### Byte order and bit order

A 32-bit value occupies four bytes. A little-endian machine (x86, and ARM as usually configured) stores the least significant byte at the lowest address; a big-endian machine stores the most significant byte first, and network protocols use big-endian, which is why C has `htonl` and `ntohl`. That is endianness, and it concerns bytes.

Bit numbering is a separate convention: whether bit 0 is the least or the most significant bit. The hexadecimal digit E is $1110$ when written most significant bit first and $0111$ when written least significant bit first, and a serial line such as a UART sends the least significant bit first. Both conventions are representations. The circuit has only the wires.

<!-- run: python3 examples/numbers_demo.py -->

These are the facts the GATE syllabus asks for under number representation and computer arithmetic, fixed and floating point (Chapter [[ch-18]]).
