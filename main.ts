// Entry for news-image-20261121 (Node 22+, standard library only, no network).
// The poster is drawn offline by build.py (PIL, via draw.py) into entry.png in this repo; at run time this program
// only copies that file to the output directory. The grader's Python image has no PIL, so the entrypoint must not
// import Python at all. MAKEFUN_OUTPUT_DIR stands in for /output when running outside the grader:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
