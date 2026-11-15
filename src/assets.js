// Asset loader: uses artist PNGs when present, procedural placeholders otherwise.
import { ANIM_ROWS, ANIM_FPS, FRAME_W, FRAME_H, VIEW_H } from './config.js';
import { loadJSON, loadImage, BASE } from './content.js';
import { proceduralFighter, mk } from './procart.js';

const LOOPING = { idle: 1, walk: 1, crouch: 1, block: 1 };

function rel(box, ax, ay) { return box ? { x: box.x - ax, y: box.y - ay, w: box.w, h: box.h } : null; }

// Accepts the Character Artist sheet.json (animations{row,frames,fps,loop,hurtbox,hitbox}),
// a TexturePacker-style {frames:{"idle_0":{frame:{x,y,w,h}}}} map, or nothing (grid by spec).
function parseSheet(img, js) {
  js = js || {};
  const fw = js.frameWidth || FRAME_W, fh = js.frameHeight || FRAME_H;
  const anc = js.anchor || { x: fw / 2, y: fh - 1 };
  const ax = anc.x, ay = anc.y + 1;
  const anims = {}, meta = {};
  const A = js.animations || {};
  ANIM_ROWS.forEach(([name, count], rowIdx) => {
    const a = A[name] || {};
    let frames = [];
    if (Array.isArray(a)) frames = a.map(r => ({ img, sx: r.x, sy: r.y, sw: r.w, sh: r.h, ax, ay }));
    else if (Array.isArray(a.rects)) frames = a.rects.map(r => ({ img, sx: r.x, sy: r.y, sw: r.w, sh: r.h, ax, ay }));
    else { const row = a.row ?? rowIdx, n = a.frames ?? count;
      if ((row + 1) * fh <= img.height) for (let i = 0; i < n; i++) frames.push({ img, sx: i * fw, sy: row * fh, sw: fw, sh: fh, ax, ay }); }
    if (frames.length) anims[name] = frames;
    meta[name] = { fps: a.fps || ANIM_FPS[name], loop: a.loop ?? !!LOOPING[name], hurtbox: rel(a.hurtbox, ax, ay),
      hitbox: a.hitbox ? { ...rel(a.hitbox, ax, ay), frames: a.hitbox.frames || [] } : null,
      spawn: a.spawn_projectile_on ?? a.spawnProjectileOn ?? null };
  });
  if (js.frames && !Array.isArray(js.frames)) { // texture-packer style
    for (const [key, v] of Object.entries(js.frames)) { const m = /^([a-z]+)[_-]?(\d+)/i.exec(key); if (!m) continue; const r = v.frame || v;
      (anims[m[1]] = anims[m[1]] || [])[+m[2]] = { img, sx: r.x, sy: r.y, sw: r.w, sh: r.h, ax: v.anchor?.x ?? r.w / 2, ay: (v.anchor?.y ?? r.h - 1) + 1 }; }
  }
  return { anims, meta, scale: 1 };
}

function procMeta() { const meta = {}; for (const [n] of ANIM_ROWS) meta[n] = { fps: ANIM_FPS[n], loop: !!LOOPING[n], hurtbox: null, hitbox: null, spawn: null }; return meta; }

export async function loadFighterArt(def) {
  const dir = `${BASE.art}characters/${def.id}/`;
  const [sheet, sheetJson, portrait, proj] = await Promise.all([
    loadImage(dir + 'sheet.png'), loadJSON(dir + 'sheet.json'), loadImage(dir + 'portrait.png'), loadImage(dir + 'projectile.png')]);
  const proc = proceduralFighter(def, false);
  const out = { id: def.id, source: sheet ? 'png' : 'procedural', anims: {}, meta: procMeta(), portrait: portrait || proc.portrait,
    portraitSource: portrait ? 'png' : 'procedural', projectile: null, alt: null };
  if (sheet) {
    const p = parseSheet(sheet, sheetJson);
    for (const [n] of ANIM_ROWS) { out.anims[n] = p.anims[n] && p.anims[n].length ? p.anims[n] : proc.anims[n]; out.meta[n] = p.meta[n]; }
    out.sheet = sheet;
  } else out.anims = proc.anims;
  if (proj) {
    const pj = (sheetJson && sheetJson.projectile) || {};
    const h = pj.frameHeight || proj.height, w = pj.frameWidth || h, n = pj.frames || Math.max(1, Math.floor(proj.width / w));
    out.projectile = { img: proj, w, h, n, fps: pj.fps || 12, loop: pj.loop ?? true, ax: pj.anchor?.x ?? w / 2, ay: pj.anchor?.y ?? h / 2 };
  }
  // Alternate palette for mirror matches.
  if (sheet) out.alt = { anims: recolorAnims(out.anims, 'hue-rotate(170deg) saturate(1.3)'), portrait: recolor(out.portrait, 'hue-rotate(170deg) saturate(1.3)') };
  else { const a = proceduralFighter(def, true); out.alt = { anims: a.anims, portrait: portrait ? recolor(portrait, 'hue-rotate(170deg)') : a.portrait }; }
  return out;
}

const recolorCache = new Map();
function recolor(img, filter) {
  const key = img; if (recolorCache.has(key) && recolorCache.get(key).f === filter) return recolorCache.get(key).c;
  const c = mk(img.width, img.height); const x = c.getContext('2d'); x.filter = filter; x.drawImage(img, 0, 0);
  recolorCache.set(key, { f: filter, c }); return c;
}
function recolorAnims(anims, filter) {
  const o = {}; for (const [n, fr] of Object.entries(anims)) o[n] = fr.map(f => ({ ...f, img: recolor(f.img, filter) })); return o;
}
// White hit-flash version of any image (cached).
const flashCache = new WeakMap();
export function flashOf(img) {
  let c = flashCache.get(img); if (c) return c;
  c = mk(img.width, img.height); const x = c.getContext('2d'); x.drawImage(img, 0, 0);
  x.globalCompositeOperation = 'source-atop'; x.fillStyle = '#ffffff'; x.fillRect(0, 0, c.width, c.height);
  flashCache.set(img, c); return c;
}

// Stage art (Stage Artist): far.png 640x360 opaque, mid.png + anim_0..3.png 960x360 aligned to mid
// (drawn at x=-160 when the camera is centred). If a file is missing we draw a plain night-sky/floor
// stand-in so the game still runs; there are no procedural stage placeholders any more.
export async function loadStageArt(stage) {
  const dir = `${BASE.art}stages/${stage.id}/`;
  const [far, mid, ...anims] = await Promise.all([loadImage(dir + 'far.png'), loadImage(dir + 'mid.png'),
    ...[0, 1, 2, 3].map(i => loadImage(`${dir}anim_${i}.png`))]);
  const got = anims.filter(Boolean);
  const m = mid || blankMid();
  return { far: far || blankFar(), mid: m, anims: got, animLayer: got.length && got[0].width !== m.width && got[0].width === (far && far.width) ? 'far' : 'mid',
    source: far && mid ? 'png' : (far || mid ? 'partial' : 'missing') };
}
function blankFar() { const c = mk(640, 360), x = c.getContext('2d'); const g = x.createLinearGradient(0, 0, 0, 360); g.addColorStop(0, '#070b1e'); g.addColorStop(1, '#2a1b4a'); x.fillStyle = g; x.fillRect(0, 0, 640, 360); return c; }
function blankMid() { const c = mk(960, 360), x = c.getContext('2d'); x.fillStyle = '#2b2b33'; x.fillRect(0, 320, 960, 40); x.fillStyle = '#4a4a55'; x.fillRect(0, 320, 960, 2); return c; }
export const layerScale = (img) => VIEW_H / img.height;
