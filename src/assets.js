// Asset loader: uses artist PNGs when present, procedural placeholders otherwise.
import { ANIM_ROWS, ANIM_FPS, FRAME_W, FRAME_H, VIEW_H } from './config.js';
import { loadJSON, loadImage, BASE } from './content.js';
import { proceduralFighter, mk } from './procart.js';

const LOOPING = { idle: 1, walk: 1, crouch: 1, block: 1 };

function rel(box, ax, ay) { return box ? { x: box.x - ax, y: box.y - ay, w: box.w, h: box.h } : null; }

// Character Artist sheet.json: frameW/frameH (or frameWidth/frameHeight; default 96x112), anchor (default
// bottom-centre), animations{row, frames, fps, loop, hurtbox, hitbox, spawn_projectile_on}. Frame counts, fps,
// loop and spawn frames always come from the JSON; a row's y comes from `row` or, if absent, its order in the
// JSON. Sheets may be any width. Also accepts TexturePacker-style {frames:{"idle_0":{frame:{x,y,w,h}}}}.
export function parseSheet(img, js) {
  js = js || {};
  const fw = js.frameW || js.frameWidth || FRAME_W, fh = js.frameH || js.frameHeight || FRAME_H;
  const anc = js.anchor || { x: fw / 2, y: fh - 1 };
  const ax = anc.x, ay = anc.y + 1;
  const anims = {}, meta = {};
  const A = js.animations || {};
  const keys = Object.keys(A).length ? Object.keys(A) : ANIM_ROWS.map(r => r[0]);
  const defaults = Object.fromEntries(ANIM_ROWS);
  keys.forEach((name, order) => {
    const a = A[name] || {};
    let frames = [];
    const R = (r) => ({ img, sx: r.x, sy: r.y, sw: r.w, sh: r.h, ax: r.ax ?? ax, ay: r.ay ?? ay });
    if (Array.isArray(a)) frames = a.map(R);
    else if (Array.isArray(a.rects)) frames = a.rects.map(R);
    else { const row = a.row ?? order, n = a.frames ?? defaults[name] ?? 1;
      const perRow = Math.max(1, Math.floor(img.width / fw));
      if ((row + 1) * fh <= img.height) for (let i = 0; i < Math.min(n, perRow); i++) frames.push({ img, sx: i * fw, sy: row * fh, sw: fw, sh: fh, ax, ay }); }
    if (frames.length) anims[name] = frames;
    meta[name] = { fps: a.fps || ANIM_FPS[name] || 10, loop: a.loop ?? !!LOOPING[name], hurtbox: rel(a.hurtbox, ax, ay),
      hitbox: a.hitbox ? { ...rel(a.hitbox, ax, ay), frames: a.hitbox.frames || [] } : null,
      spawn: a.spawn_projectile_on ?? a.spawnProjectileOn ?? a.spawn ?? null, hold: a.hold_frames ?? a.holdFrames ?? null,
      holdPoint: a.hold_point || a.holdPoint ? rel({ ...(a.hold_point || a.holdPoint), w: 0, h: 0 }, ax, ay) : null };
  });
  if (js.frames && !Array.isArray(js.frames)) {
    for (const [key, v] of Object.entries(js.frames)) { const m = /^([a-z]+)[_-]?(\d+)/i.exec(key); if (!m) continue; const r = v.frame || v;
      (anims[m[1]] = anims[m[1]] || [])[+m[2]] = { img, sx: r.x, sy: r.y, sw: r.w, sh: r.h, ax: v.anchor?.x ?? r.w / 2, ay: (v.anchor?.y ?? r.h - 1) + 1 }; }
  }
  return { anims, meta, fw, fh };
}

function procMeta() { const meta = {}; for (const [n] of ANIM_ROWS) meta[n] = { fps: ANIM_FPS[n], loop: !!LOOPING[n], hurtbox: null, hitbox: null, spawn: null }; return meta; }

// Effect strip (projectile.png / super.png) described by a sheet.json block.
function strip(img, spec) {
  spec = spec || {};
  const h = spec.frameH || spec.frameHeight || img.height, w = spec.frameW || spec.frameWidth || h, n = spec.frames || Math.max(1, Math.floor(img.width / w));
  return { img, w, h, n, fps: spec.fps || 12, loop: spec.loop ?? true, ax: spec.anchor?.x ?? w / 2, ay: spec.anchor?.y ?? h / 2,
    spawn: spec.spawn_on ?? spec.spawnOn ?? null, attach: spec.attach || null, boxes: frameBoxes(img, w, h, n), notes: spec.notes || '' };
}

export async function loadFighterArt(def) {
  const dir = `${BASE.art}characters/${def.id}/`;
  const sheetJson = await loadJSON(dir + 'sheet.json');
  const files = (sheetJson && sheetJson.files) || {};
  const superSpec = sheetJson && (sheetJson.super || sheetJson.superEffect);
  const [sheet, portrait, portraitL, proj, sup] = await Promise.all([
    loadImage(dir + (files.sheet || 'sheet.png')), loadImage(dir + (files.portrait || 'portrait.png')),
    loadImage(dir + (files.portraitLarge || files.portrait_large || 'portrait_large.png')),
    loadImage(dir + ((sheetJson && sheetJson.projectile && sheetJson.projectile.file) || files.projectile || 'projectile.png')),
    superSpec || files.super ? loadImage(dir + ((superSpec && superSpec.file) || files.super || 'super.png')) : Promise.resolve(null)]);
  const proc = proceduralFighter(def, false);
  const out = { id: def.id, source: sheet ? 'png' : 'procedural', anims: {}, meta: procMeta(), portrait: portrait || proc.portrait,
    portraitLarge: portraitL || null, portraitSource: portrait ? 'png' : 'procedural', projectile: null, super: null, alt: null, frameW: FRAME_W, frameH: FRAME_H };
  if (sheet) {
    const p = parseSheet(sheet, sheetJson); out.frameW = p.fw; out.frameH = p.fh;
    for (const n of new Set([...ANIM_ROWS.map(r => r[0]), ...Object.keys(p.anims)])) {
      out.anims[n] = p.anims[n] && p.anims[n].length ? p.anims[n] : proc.anims[n]; out.meta[n] = p.meta[n] || out.meta[n]; }
    out.sheet = sheet;
  } else out.anims = proc.anims;
  if (proj) out.projectile = strip(proj, sheetJson && sheetJson.projectile);
  if (sup) out.super = strip(sup, superSpec);
  // Alternate palette for mirror matches.
  if (sheet) out.alt = { anims: recolorAnims(out.anims, 'hue-rotate(170deg) saturate(1.3)'), portrait: recolor(out.portrait, 'hue-rotate(170deg) saturate(1.3)'),
    portraitLarge: portraitL ? recolor(portraitL, 'hue-rotate(170deg) saturate(1.3)') : null };
  else { const a = proceduralFighter(def, true); out.alt = { anims: a.anims, portrait: portrait ? recolor(portrait, 'hue-rotate(170deg)') : a.portrait }; }
  return out;
}

// Opaque-pixel bounding box of each projectile frame (frame space) -> used as the collision box.
function frameBoxes(img, w, h, n) {
  const c = mk(img.width, img.height), x = c.getContext('2d'); x.drawImage(img, 0, 0); let d;
  try { d = x.getImageData(0, 0, img.width, img.height).data; } catch { return null; }
  const out = [];
  for (let i = 0; i < n; i++) { let l = w, r = -1, t = h, b = -1;
    for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) if (d[(yy * img.width + i * w + xx) * 4 + 3] > 40) { if (xx < l) l = xx; if (xx > r) r = xx; if (yy < t) t = yy; if (yy > b) b = yy; }
    out.push(r < 0 ? null : { x: l, y: t, w: r - l + 1, h: b - t + 1 }); }
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

// Stage art (Stage Artist): far.png 640x360 (fixed), mid.png 960x360 (160 px parallax margin each side),
// optional near.png 1120x360 foreground (240 px margin, drawn in front of the fighters), and up to
// anim_0..7.png overlays. Each overlay joins the layer whose width it matches (640 far / 960 mid / 1120 near).
// Missing far/mid draw a plain stand-in; everything optional is simply skipped.
export async function loadStageArt(stage) {
  const dir = `${BASE.art}stages/${stage.id}/`;
  const [far, mid, near, ...first] = await Promise.all([loadImage(dir + 'far.png'), loadImage(dir + 'mid.png'), loadImage(dir + 'near.png'),
    ...[0, 1, 2, 3].map(i => loadImage(`${dir}anim_${i}.png`))]);
  let anims = first;
  if (first.every(Boolean)) anims = anims.concat(await Promise.all([4, 5, 6, 7].map(i => loadImage(`${dir}anim_${i}.png`))));
  const seq = []; for (const im of anims) { if (!im) break; seq.push(im); }   // contiguous anim_0..N
  const m = mid || blankMid(), f = far || blankFar();
  const layerOf = (im) => near && im.width === near.width && im.width !== m.width ? 'near' : im.width === m.width ? 'mid' : im.width === f.width ? 'far' : 'mid';
  const layers = { far: [], mid: [], near: [] }; for (const im of seq) layers[layerOf(im)].push(im);
  return { far: f, mid: m, near: near || null, anims: seq, animLayers: layers, animFps: stage.animFps || (stage.animMs ? 1000 / stage.animMs : 1000 / 120),
    animLayer: seq.length ? layerOf(seq[0]) : 'mid', source: far && mid ? 'png' : (far || mid ? 'partial' : 'missing') };
}
function blankFar() { const c = mk(640, 360), x = c.getContext('2d'); const g = x.createLinearGradient(0, 0, 0, 360); g.addColorStop(0, '#070b1e'); g.addColorStop(1, '#2a1b4a'); x.fillStyle = g; x.fillRect(0, 0, 640, 360); return c; }
function blankMid() { const c = mk(960, 360), x = c.getContext('2d'); x.fillStyle = '#2b2b33'; x.fillRect(0, 320, 960, 40); x.fillStyle = '#4a4a55'; x.fillRect(0, 320, 960, 2); return c; }
export const layerScale = (img) => VIEW_H / img.height;
