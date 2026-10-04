<!-- © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI. -->

## F. Formal definitions {#app-math}

This appendix states in symbols what the chapters state in words. Where the record gives a formal object, the PEDLER six-tuple, the CEM kernel or the Triad's tuples, it is reproduced as recorded. Where the record gives only words, the formalisation is this guide's reading, and is said to be.

### The estate as a typed graph

The estate is a typed graph
$$ H = (V,\; E,\; \tau_V,\; \tau_E), \qquad E \subseteq V \times V \times R, $$
where $V$ is the set of components, $R$ the set of relations (projects, script layer, realized by, front end, mounts and the rest), $\tau_V : V \to \mathcal{F}$ assigns each component its family, and $\tau_E$ each edge its relation. The core is described as a typed hypergraph, in which one edge may join several components at once: $E \subseteq 2^{V} \times R$. A traversal is a walk $v_0 \xrightarrow{r_1} v_1 \xrightarrow{r_2} \cdots \xrightarrow{r_k} v_k$; every sequence printed in this guide, and every reading path of the reader views, is one.

In this guide's reading, a projection $p \in \{\text{Kaivalyik}, \text{Zistgah}, \text{Cosmopolis}\}$ is a map $\pi_p : H \to H_p$ that keeps every component's stem and every relation and changes names: $\operatorname{stem}(\pi_p(v)) = \operatorname{stem}(v)$ and $(u,v,r) \in E \Rightarrow (\pi_p(u), \pi_p(v), r) \in E_p$. The Acts are a separate, partial labelling $\alpha : V \rightharpoonup \{\mathrm{I}, \mathrm{I|II}, \mathrm{II}, \mathrm{II|III}, \mathrm{III}\}$, with PANINI in every Act.

### Romenagri as a code

Let $\Sigma$ be the Devanagari alphabet and $\Gamma = \{\texttt{a}, \ldots, \texttt{z}, \texttt{\_}\}$, a subset of the alphabet of C identifiers. Romenagri's compiler form is a map
$$ T : W \to \Gamma^{*}, \qquad W \subseteq \Sigma^{*}, $$
injective on well-formed text $W$, with an inverse $T^{-1}$ on $T(W)$. Text outside $W$ is first brought to its canonical form by $c : \Sigma^{*} \to W$, so that for every string
$$ T^{-1}\bigl(T(s)\bigr) = c(s), \qquad c(s) = s \text{ whenever } s \in W . $$
On the 984 words of the Hindi corpus, $T^{-1}T(w) = w$ for 983; the one exception is a misspelling in the corpus.

For a Brahmi script $\sigma$ whose Unicode block follows the ISCII layout from base $b_\sigma$, the hub map is $h_\sigma(x) = x - b_\sigma + \texttt{0x900}$ on the aligned letters, a bijection onto the corresponding Devanagari letters; `flatten_uni_dev` applies it by table. A word in script $\sigma$ therefore has the identity $T(h_\sigma(w))$, and returns by $h_\sigma^{-1}(T^{-1}(\cdot))$.

Urdu meets the hub through $\varphi : \Sigma_{\text{ur}}^{*} \to \Sigma^{*}$, which is many-to-one on unmarked text: the fibre $\varphi^{-1}(w)$ over a hub word can hold several spoken readings, because the short vowels are not written. With tashkil, the restriction of $\varphi$ to marked text distinguishes them: unmarked ہندوی maps to हनदवी, and marked ہِنْدوی to हिन्दवी. In the corpus, 1 word in 794 carries a vowel mark.

### The symbol bridge

For every name $n$ in a program, the toolchain sees $\operatorname{sym}(n) = T(n) \in \Gamma^{*}$. Each stage $t_k$ between source and debugger (compiler, assembler, linker, ELF writer, DWARF writer, debugger) carries identifiers over $\Gamma$ unchanged: $t_k(\operatorname{sym}(n)) = \operatorname{sym}(n)$. Hence
$$ T^{-1}\bigl(t_m \circ \cdots \circ t_1(\operatorname{sym}(n))\bigr) = c(n), $$
which is the name as written. Chapter [[ch-13]] runs this for every name of a program.

### The construct model

Let $C$ be the constructs (39), $\mathcal{L}$ the languages (27) and $\mathcal{H}$ the host languages (8). Each language $\ell$ has a keyword map $\kappa_\ell : C \to W_\ell$, and each host $h$ a realisation $\rho_h : C \rightharpoonup W_h$, partial because not every host has every construct. Translation from $\ell$ to $h$ is
$$ \tau_{\ell \to h} = \rho_h \circ \kappa_\ell^{-1}, $$
defined when $\kappa_\ell$ is injective, which is the reversibility check ILM runs on every keyword table. Direct pairings of a language with a host would number $|\mathcal{L}| \cdot |\mathcal{H}| = 27 \times 8 = 216$ tables; the construct model needs $|\mathcal{L}| + |\mathcal{H}| = 35$.

### PEDLER, as PANINIq implements it

PANINIq implements PEDLER as the six-tuple
$$ P = (I,\; G,\; U,\; S,\; F,\; \ast), $$
with events $U \subset \mathbb{R}^{3}$, states $S$, a feature map $F : S \to \mathbb{R}^{3}$, and the resolution kernel
$$ G(v, r) = e^{-\gamma \lVert F(v) - r \rVert}. $$
The inclination of a state is its historical prior plus the weighted match, $I(v) = \eta(v) + w\, G(v, r)$. The operator $\ast$ grows and prunes the state set: a new state is spawned when the relaxed network's order parameter falls below a novelty threshold, $R < \theta$. The Act is the transition $A(I, S_t) \to S_{t+1}$. In this guide's reading, Natural Justice is an admissibility predicate on the passage from intent to Act: a transition fires only if $\mathrm{NJ}(\text{intent}, S_t)$ holds.

### Kernels and closures, as recorded

The record gives the CEM kernel and the AyeAI Triad's closure as tuples, and they are reproduced here as given; the expansions of their letters are not part of the retrieved record:
$$ \mathcal{E} = (E,\; \mathcal{C},\; \Pi,\; W), \qquad \text{AyeAM} = \langle S, R, C \rangle, \quad \text{AyeAI} = \langle M, I, G \rangle, \quad \text{AyeCNSe} = \langle T, Ch, \Sigma \rangle . $$

### Gates and evidence

A gate is a function $g : \mathcal{A} \to \{\text{pass}, \text{fail}, \text{unjudged}\}$ on artifacts, computed by running it. An issue is done exactly when
$$ g(a) = \text{pass} \;\wedge\; \text{merged}(a) \;\wedge\; \bigl(\text{published}(a) \Rightarrow \text{receipt}(a)\bigr). $$
VGC's rule is that a worker's report $r(a)$ is not an argument of $g$: the gate is computed from the artifact, never read from the claim.

### Provenance

A repository's manifest is the list $m = \bigl[(p_i, H(f_i))\bigr]_i$ of every tracked path with the SHA-256 of its file. Sealing commits the digest $d = H(m)$ to OpenTimestamps, whose calendars aggregate many digests in a Merkle tree anchored in a Bitcoin block; the proof for one digest among $N$ is a path of length $\lceil \log_2 N \rceil$, and verifying it recomputes the root. The four systems are ordered by implication:
$$ \text{mint}(a) \Rightarrow \text{attest}(a) \Rightarrow \text{clear}(a) \Rightarrow \text{seal}(a). $$

### The seed space and the reading paths

FAKIR seeds a task from a domain node, an AGI layer and a language: $S = D \times L \times \Lambda$, with $|D| = 1{,}505$ nodes across ISIC, ISCO and ISCED, $|L| = 10$ layers and $|\Lambda| = 7{,}867$ languages, so
$$ |S| = 1{,}505 \times 10 \times 7{,}867 = 118{,}398{,}350 . $$
A cross-domain task is seeded from a set of nodes, a subset of $D$, rather than one.

A reader view is a sequence of chapters $(c_1, \ldots, c_k)$, a walk on the chapters. A chapter of $w$ words is estimated at $t(c) = \max\bigl(1, \operatorname{round}(w / 200)\bigr)$ minutes, and a path at $\sum_j t(c_j)$.
