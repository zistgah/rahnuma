// tools/mathjax_page.mjs: renders every \( \) and \[ \] in a page to SVG, once, at build time,
// so the published page and the PDF carry their mathematics without loading anything.
// © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
// SPDX-License-Identifier: GPL-3.0-or-later
import fs from 'fs';
import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {SVG} from 'mathjax-full/js/output/svg.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';
import {AllPackages} from 'mathjax-full/js/input/tex/AllPackages.js';

const [, , input, output] = process.argv;
const adaptor = liteAdaptor({fontSize: 17});
RegisterHTMLHandler(adaptor);
const tex = new TeX({packages: AllPackages.filter((p) => p !== 'bussproofs'),
  inlineMath: [['\\(', '\\)']], displayMath: [['\\[', '\\]']], processEscapes: false});
const svg = new SVG({fontCache: 'global'});
const doc = mathjax.document(fs.readFileSync(input, 'utf8'), {InputJax: tex, OutputJax: svg});
doc.render();
const errors = Array.from(doc.math).filter((m) => /merror/.test(adaptor.outerHTML(m.typesetRoot)));
if (errors.length) {
  for (const m of errors) console.error('TeX error in: ' + m.math);
  process.exit(1);
}
fs.writeFileSync(output, adaptor.doctype(doc.document) + '\n' + adaptor.outerHTML(adaptor.root(doc.document)));
console.log('mathematics rendered: ' + Array.from(doc.math).length);
