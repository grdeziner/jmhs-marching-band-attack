// Content + asset I/O. Over http it fetches files; in the single-file build it reads
// window.__BAND_BUNDLE__ (made by build.js) so nothing touches the network.
const bundle = () => window.__BAND_BUNDLE__ || null;
export const BASE = { content: 'content/', art: 'art/', music: 'audio/music/' };

// content/files.json lists assets that exist. Missing sheets, portraits and
// songs are skipped so the browser does not log a 404 for procedural fighters.
let fileIndexPromise = null;
function fileIndex() {
  if (bundle()) return Promise.resolve(null);
  if (!fileIndexPromise) {
    fileIndexPromise = fetch(BASE.content + 'files.json', { cache: 'no-cache' })
      .then((response) => (response.ok ? response.json() : null))
      .then((list) => (Array.isArray(list) ? new Set(list) : null))
      .catch(() => null);
  }
  return fileIndexPromise;
}
async function present(path) {
  const packed = bundle();
  if (packed) return Object.prototype.hasOwnProperty.call(packed.files, path) && packed.files[path] != null;
  const index = await fileIndex();
  if (!index) return true;
  return index.has(path);
}

export async function loadJSON(path) {
  const packed = bundle(); if (packed) return packed.files[path] ?? null;
  if (path.startsWith('art/') && !(await present(path))) return null;
  try { const response = await fetch(path, { cache: 'no-cache' }); if (!response.ok) return null; return await response.json(); } catch { return null; }
}
export async function loadImage(path) {
  const packed = bundle();
  const src = packed ? packed.files[path] : path;
  if (!src) return null;
  if (!packed && !(await present(path))) return null;
  return new Promise((resolve) => { const image = new Image(); image.onload = () => resolve(image); image.onerror = () => resolve(null); image.src = src; });
}
export async function loadSong(path) {
  const packed = bundle(); if (packed) return packed.files[path] ?? null;
  if (!(await present(path))) return null;
  try { const mod = await import(new URL(path, document.baseURI).href); return mod.song || mod.default || null; } catch { return null; }
}

// Short display name: the nickname in quotes, else first word.
export function shortName(name) { const m = /"([^"]+)"/.exec(name || ''); return (m ? m[1] : String(name || '?').split(' ')[0]).toUpperCase(); }

const STORY_FIELDS = ['name', 'section', 'instrument', 'fightingStyle', 'personality', 'rivals', 'whyTheyFight', 'taunt', 'winQuote', 'ending'];
export async function loadContent() {
  const roster = await loadJSON(BASE.content + 'roster.json');
  const stages = await loadJSON(BASE.content + 'stages.json');
  if (!roster || !stages) throw new Error('Could not load content/roster.json or content/stages.json. Serve this folder over http (see README) or open dist/index.html.');
  const fighters = roster.fighters.filter(f => f.enabled !== false).sort((a, b) => (a.order || 0) - (b.order || 0));
  await Promise.all(fighters.map(async (f) => {
    const st = await loadJSON(`${BASE.content}characters/${f.id}.json`);
    f.story = st || {};
    if (st) for (const k of STORY_FIELDS) if (st[k] !== undefined && st[k] !== '') f[k === 'name' ? 'fullName' : k] = st[k];
    f.fullName = (f.fullName || f.name || f.id).toUpperCase();
    f.short = shortName(f.fullName);
    f.taunt = f.taunt || ''; f.winQuote = f.winQuote || '';
  }));
  const music = {};
  await Promise.all([
    ...stages.stages.map(async s => { music[s.id] = await loadSong(s.musicFile || `${BASE.music}${s.id}.js`); }),
    ...['title', 'select', 'victory'].map(async j => { music[j] = await loadSong(`${BASE.music}${j}.js`); }),
  ]);
  return { settings: roster.settings || {}, fighters, stages: stages.stages, music };
}
