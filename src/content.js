// Content + asset I/O. Over http it fetches files; in the single-file build it reads
// window.__BAND_BUNDLE__ (made by build.js) so nothing touches the network.
const bundle = () => window.__BAND_BUNDLE__ || null;
export const BASE = { content: 'content/', art: 'art/', music: 'audio/music/' };

export async function loadJSON(path) {
  const b = bundle(); if (b) return b.files[path] ?? null;
  try { const r = await fetch(path, { cache: 'no-cache' }); if (!r.ok) return null; return await r.json(); } catch { return null; }
}
export function loadImage(path) {
  const b = bundle();
  const src = b ? b.files[path] : path; if (!src) return Promise.resolve(null);
  return new Promise((res) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => res(null); im.src = src; });
}
export async function loadSong(path) {
  const b = bundle(); if (b) return b.files[path] ?? null;
  try { const m = await import(new URL(path, document.baseURI).href); return m.song || m.default || null; } catch { return null; }
}
// Composer's format-2 instrument catalog (audio/music/instruments.js). Optional: built-in patches are used if absent.
export async function loadInstruments(path) {
  const b = bundle(); if (b) return b.files[path] ?? null;
  try { const m = await import(new URL(path, document.baseURI).href); return m.INSTRUMENTS || m.default || null; } catch { return null; }
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
  const instruments = await loadInstruments(`${BASE.music}instruments.js`);
  return { settings: roster.settings || {}, fighters, stages: stages.stages, music, instruments };
}
