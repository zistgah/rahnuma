<!-- © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI. -->

## Architecture: core, projections, layers {#ch-03}

### One core, three projections

Humanesque is the core: one shared, multidimensional, executable typed hypergraph, with a federated ontology of 26 positions, $O_0$ to $O_{25}$, a common execution and evidence spine, and components that can be implemented independently. Its GitHub organisation is hmnsq, where every core stem repository is to live.

Kaivalyik, Zistgah and Cosmopolis are three projections over it, running in parallel: the Indic, including the Advaita framing; the Persian and Islamicate; and the Greek, Western and classical. A projection is a domain-specific view and traversal of the whole architecture, with its own culturally sensitive naming and branding. The projections are not stages, not levels of a hierarchy and not versions of one another; they intersect, diverge and reconverge, and none completes another. Zistgah is not the parent of the other two. Their organisations are kaivalyik, zistgah and c-polis; today zistgah carries the working repositories.

### The PANINI stack

| Layer | What it holds | Where to look |
|:------|:--------------------------------------|:---------------|
| Front end | The languages a program or a prompt can arrive in, Sanskrit first: ILM and the language parsers | project-ilm/ilm.codes, zistgah/tajziya |
| Middleware | PANINI's own front ends, from `ada.pni` to `zig.pni` and `sysml.pni`, and the PANINI language itself | zistgah/panini, zistgah/humanesque |
| Core PANINI | The construct model: common semantics plus decorators | zistgah/humanesque, `ilm/constructs.csv` and `ilm/decorators.csv` |
| Realization backends | Where a program meets a substrate: host toolchains for code; PANINIq for oscillator and quantum substrates; PANINIb for biology; PANINIphy for physical systems | zistgah/paniniq, zistgah/paninib, zistgah/paniniphy |

Beneath every front end lies the script layer, Romenagri. Every keyword and every name of a program becomes a word over A to Z, a to z and the underscore, reversibly, so that the whole existing toolchain, from lexer to linker to debugger, carries it unchanged, and the inverse renders it back in the script wherever a person reads it. Chapters [[ch-10]], [[ch-11]] and [[ch-13]] explain it and run it.

A construct such as a counted loop is defined once in the core and translated once per human language. A decorator carries what a particular host language drags in with it, such as `stdio.h` for printing in C. Core PANINI, in his words, "does not violate anything"; the front ends and the realization backends are all projections of it.

### How the parts compose

```text
Humanesque    the core; Kaivalyik, Zistgah and Cosmopolis project it in parallel;
              everything below lives in it, nothing below leads to it

front end     ILM (script | language | standard) and tajziya, Sanskrit first
                the script axis is Romenagri, which persists as the symbol bridge
                through compiler, linker, ELF, DWARF and debugger
middleware    PANINI's own front ends and the PANINI language
core          core PANINI: construct model = common semantics + decorators
realization   host toolchains for code; PANINIq (oscillator, quantum);
              PANINIb (biology, down to sequence IR); PANINIphy (physical systems);
              PRATIK and Zamin as a balanced-ternary substrate
```

Around the stack: the cyclers are written in PANINI and run by one engine; GENIE composes and runs research cycles; AAB paints tasks and runs the process cyclers; FAKIR, UKOP and Dhancha supply the domain lattice and its invariants; Mez, the Cognitive Workbench, composes any of them for an exercise without absorbing them; the provenance systems seal every artifact; VGC gates the work between people and AI. Two readings must be kept apart. As genealogy, the order is Romenagri, Hindawi, ILM, PANINI and the realization arms. As architecture, Romenagri sits inside ILM's script axis, the cyclers are written in PANINI rather than downstream of it, and Humanesque is the core that contains the whole, not its end point.

### The realization spine

The realization repositories state the spine they share. PANINI lowers declarative intent through language, semantic IR, a realization requirement, domain resolution and a domain IR, and then a common layer of geometry, trajectory, animation, observation, verification and an ArtifactGraph. PANINIb lowers biological intent through semantic, resolution, CISC, RISC and sequence IRs and emits two coupled artifacts, a physical realization plan and a digital execution run; PANINIphy lowers physical intent through a physical IR and physical-domain engines. "IR contracts are the product. Laboratories and machines are external adapters." And the same repositories keep the states of a result apart: desired, predicted, observed and validated phenotype are four different things, as are compilation success, execution success, target satisfaction and biological validation.

### The habitat elements

Zamin is the ground: the balanced-ternary hardware of PRATIK. AAB is the water: the paint program for systems, from painted intent to verified, sealed artifact, where the verification-gated quests run. Fiza is the air: the environmental replica. Chakra is the turning sky: the observatory and its calendars. All of them mount in one shared virtual dome, which the habitats on the Moon and Mars replicate.

### The cyclers

A cycler is a sequence of prompts and the outputs they produce, written down so that it can be edited, shared and run with any AI. Six are classified by what they produce: matba (print), khwab (visual), awaz (audio), tilasm (immersive), pench (embodied) and yadein (the record); genie runs research cycles. Each has its own purpose, contract, context, state model, invariants, failure modes, evidence requirements, workflow and artifact model; only the engine is shared. The protocol behind every cycle, in the author's words: intent, then context, then a meaningful prompt; any AI answers and the human inspects; the artifacts and responses are kept under configuration management; the next prompt follows, until a final artifact that the human authored with intention.

### Provenance, in a fixed order

Four systems, never collapsed into one. **Tok DOI** proves that a thing existed by a given time. **spiguard** is the disclosure gate, which fails closed. **Candor** records signed intent as in-toto statements. **Misty DOI** is the one that reaches the world, through Zenodo. The order is always seal, clear, attest, mint. Chapter [[ch-17]] explains the machinery.
