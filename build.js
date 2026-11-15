#!/usr/bin/env node
// Builds dist/index.html: one self-contained file (all ES modules, content JSON, songs and art PNGs inlined).
// Usage: node build.js        (re-run whenever art/content/music changes)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const ROOT = path.dirname(fileURLToPath(import.meta.url));
const rel = (p) => path.join(ROOT, p);
const exists = (p) => fs.existsSync(rel(p));

// ---- 1. bundle src/*.js (each module wrapped in its own scope) ----
const order = []; const seen = new Set();
function visit(file) {
  if (seen.has(file)) return; seen.add(file);
  const src = fs.readFileSync(rel('src/' + file), 'utf8');
  for (const m of src.matchAll(/^import\s+\{[^}]*\}\s+from\s+'\.\/([^']+)';/mg)) visit(m[1]);
  order.push(file);
}
visit('main.js');
let js = 'const __M = {};\n';
for (const file of order) {
  let src = fs.readFileSync(rel('src/' + file), 'utf8');
  const exportsList = [...src.matchAll(/^export\s+(?:async\s+)?(?:function|class|const|let)\s+([A-Za-z_$][\w$]*)/mg)].map(m => m[1]);
  src = src.replace(/^import\s+\{([^}]*)\}\s+from\s+'\.\/([^']+)';/mg, (_, names, f) => `const {${names.replace(/\s+as\s+/g, ': ')}} = __M['${f}'];`);
  src = src.replace(/^export\s+/mg, '');
  js += `__M['${file}'] = (() => {\n${src}\nreturn { ${exportsList.join(', ')} };\n})();\n`;
}

// ---- 2. inline content, art and music ----
const files = {};
const addJSON = (p) => { if (exists(p)) files[p] = JSON.parse(fs.readFileSync(rel(p), 'utf8')); };
const addPNG = (p) => { if (exists(p)) files[p] = 'data:image/png;base64,' + fs.readFileSync(rel(p)).toString('base64'); };
addJSON('content/roster.json'); addJSON('content/stages.json');
const roster = files['content/roster.json'], stages = files['content/stages.json'];
for (const f of roster.fighters) {
  addJSON(`content/characters/${f.id}.json`);
  const d = `art/characters/${f.id}/`; addJSON(d + 'sheet.json');
  const sj = files[d + 'sheet.json'] || {}, fl = sj.files || {};
  // same file names the runtime loader asks for (src/assets.js loadFighterArt); optional ones are skipped when absent
  [fl.sheet || 'sheet.png', fl.portrait || 'portrait.png', fl.portraitLarge || fl.portrait_large || 'portrait_large.png',
   (sj.projectile && sj.projectile.file) || fl.projectile || 'projectile.png'].forEach(n => addPNG(d + n));
  if (sj.super || fl.super) addPNG(d + ((sj.super && sj.super.file) || fl.super || 'super.png'));
}
for (const s of stages.stages) { const d = `art/stages/${s.id}/`;
  ['far.png', 'mid.png', 'near.png', 'anim_0.png', 'anim_1.png', 'anim_2.png', 'anim_3.png'].forEach(n => addPNG(d + n));
  if ([0, 1, 2, 3].every(i => exists(`${d}anim_${i}.png`))) [4, 5, 6, 7].forEach(i => addPNG(`${d}anim_${i}.png`)); }
const songs = [...stages.stages.map(s => s.musicFile || `audio/music/${s.id}.js`), 'audio/music/title.js', 'audio/music/select.js', 'audio/music/victory.js'];
for (const s of songs) if (exists(s)) { const m = await import(pathToFileURL(rel(s)).href); files[s] = m.song || m.default; }
if (exists('audio/music/instruments.js')) { const m = await import(pathToFileURL(rel('audio/music/instruments.js')).href); files['audio/music/instruments.js'] = m.INSTRUMENTS || m.default; }

// ---- 3. write ----
const html = fs.readFileSync(rel('index.html'), 'utf8')
  .replace(/<script type="module" src="src\/main.js"><\/script>/,
    `<script>window.__BAND_BUNDLE__ = ${JSON.stringify({ built: new Date().toISOString(), files })};</script>\n<script>\n${js.replace(/<\/script/gi, '<\\/script')}\n</script>`);
fs.mkdirSync(rel('dist'), { recursive: true }); fs.writeFileSync(rel('dist/index.html'), html);
const inlined = Object.keys(files);
console.log(`dist/index.html ${(html.length / 1024).toFixed(0)} KB | modules: ${order.length} | files inlined: ${inlined.length}`);
console.log('  art: ' + inlined.filter(f => f.startsWith('art/')).join(', '));
console.log('  music: ' + inlined.filter(f => f.startsWith('audio/')).join(', '));
