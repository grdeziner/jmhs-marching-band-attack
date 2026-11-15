// Procedural placeholder art: draws each fighter in "unit" pixels (1 unit = 3 screen px)
// and produces frames in exactly the same shape the PNG loader produces, so the renderer
// does not care which one it gets.
import { FRAME_W, FRAME_H, ANIM_ROWS } from './config.js';

const U = 3;                 // unit -> px
const UW = 32, UH = 37;      // unit canvas (96 x 111 px)
const OUTLINE = '#140c1c';
const GLOVE = '#f4f4f4', SHOE = '#151515', SILVER = '#c9ced6', SILVER_D = '#7d8590',
  BRASS = '#e8b923', BRASS_D = '#9c7412', BRASS_L = '#fff1a8', EBONY = '#23232b', WOOD = '#e8d3a2';

export function mk(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
export function shade(hex, f) {
  const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  if (f < 0) { r *= 1 + f; g *= 1 + f; b *= 1 + f; } else { r += (255 - r) * f; g += (255 - g) * f; b += (255 - b) * f; }
  return '#' + [r, g, b].map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('');
}
function P(ctx) {
  return {
    ctx,
    px(x, y, c) { ctx.fillStyle = c; ctx.fillRect(Math.round(x), Math.round(y), 1, 1); },
    rect(x, y, w, h, c) { ctx.fillStyle = c; ctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); },
    line(x0, y0, x1, y1, t, c) {
      ctx.fillStyle = c; x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
      const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
      const o = Math.floor((t - 1) / 2);
      for (;;) { ctx.fillRect(x0 - o, y0 - o, t, t); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e;
        if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
    },
    ring(cx, cy, r, t, c, from = 0, to = Math.PI * 2) {
      ctx.fillStyle = c;
      for (let a = from; a < to; a += 0.08) for (let k = 0; k < t; k++)
        ctx.fillRect(Math.round(cx + Math.cos(a) * (r - k)), Math.round(cy + Math.sin(a) * (r - k)), 1, 1);
    },
  };
}

// ---------- instruments (units, facing right) ----------
// Each returns hand targets for the pose and draws itself. o: {cx, y (body offset), ext, play, t, mode}
const STRAPPED = { bassdrum: 1, snare: 1, xylophone: 1, tuba: 1 };
export const INSTR_KIND = {
  drummer: 'bassdrum', xylophone: 'xylophone', flute: 'flute', trumpet: 'trumpet', trombone: 'trombone',
  tuba: 'tuba', clarinet: 'clarinet', bassclarinet: 'bassclarinet', colorguard: 'flag',
};
const INSTR = {
  bassdrum: {
    hands: (o) => o.play ? { fh: [o.cx + 9, 12 + o.y - (o.t % 2) * 2], bh: [o.cx + 2, 12 + o.y - ((o.t + 1) % 2) * 2] }
                         : { fh: [o.cx + 9, 18 + o.y], bh: [o.cx + 1, 18 + o.y] },
    front(g, o, h) {
      const x = o.cx + 4, y = 19 + o.y;
      g.ring(x, y, 7, 2, '#d4a017'); for (let r = 5; r >= 0; r--) g.ring(x, y, r, 1, r > 3 ? '#e9e3d2' : '#f6f2ea');
      g.px(x, y, '#d4a017'); g.px(x - 1, y - 1, '#3a5a9c');
      for (const hh of [h.fh, h.bh]) { g.line(hh[0], hh[1], hh[0] + (hh === h.fh ? 2 : -2), hh[1] - 3, 1, WOOD); g.rect(hh[0] + (hh === h.fh ? 1 : -3), hh[1] - 5, 3, 3, '#f4f4f4'); }
    },
  },
  snare: {
    hands: (o) => o.play ? { fh: [o.cx + 7, 16 + o.y - (o.t % 2) * 3], bh: [o.cx + 4, 16 + o.y - ((o.t + 1) % 2) * 3] }
                         : { fh: [o.cx + 6, 19 + o.y], bh: [o.cx + 3, 19 + o.y] },
    front(g, o, h) {
      const x = o.cx + 1, y = 20 + o.y;
      g.rect(x, y, 8, 5, '#f2f2f2'); g.rect(x, y, 8, 1, SILVER_D); g.rect(x, y + 4, 8, 1, SILVER_D);
      g.rect(x, y + 1, 8, 3, '#e6e6e6'); for (let i = 0; i < 8; i += 2) g.px(x + i, y + 2, '#c8202c');
      stick(g, h.fh, o.play ? [-1, -4] : [3, 2]); stick(g, h.bh, o.play ? [1, -4] : [3, 1]);
    },
  },
  xylophone: {
    hands: (o) => o.play ? { fh: [o.cx + 8, 15 + o.y - (o.t % 2) * 3], bh: [o.cx + 5, 15 + o.y - ((o.t + 1) % 2) * 3] }
                         : { fh: [o.cx + 7, 18 + o.y], bh: [o.cx + 4, 18 + o.y] },
    front(g, o, h) {
      const cols = ['#ff595e', '#ff924c', '#ffca3a', '#8ac926', '#52a675', '#1982c4', '#4267ac', '#6a4c93'];
      const x = o.cx + 1, y = 20 + o.y;
      g.rect(x - 1, y + 3, 11, 1, SILVER_D);
      for (let i = 0; i < 8; i++) g.rect(x + i, y + 2 - Math.floor(i / 3), 1, 2 + (i % 2), cols[i]);
      mallet(g, h.fh, o.play ? [0, -4] : [3, 2]); mallet(g, h.bh, o.play ? [0, -4] : [3, 1]);
    },
  },
  tuba: {
    hands: (o) => ({ fh: [o.cx + 6 + o.ext, 18 + o.y], bh: [o.cx + 4, 21 + o.y] }),
    back(g, o) { g.ring(o.cx, 19 + o.y, 7, 2, BRASS_D, Math.PI * 0.5, Math.PI * 1.5);
      // bell over the back shoulder, opening facing forward
      for (let i = 0; i < 7; i++) g.rect(o.cx - 9 + i, 4 + o.y - Math.floor(i * 0.7), 1, 3 + Math.floor(i * 1.4), i === 6 ? BRASS_L : BRASS);
      g.rect(o.cx - 4, 0 + o.y, 1, 12, BRASS_D);
      if (o.play) for (let k = 0; k < 3; k++) g.px(o.cx - 1 + k * 2, 2 + o.y - k + (o.t % 2), '#ffffff');
    },
    front(g, o) { g.ring(o.cx, 19 + o.y, 7, 2, BRASS, -Math.PI * 0.5, Math.PI * 0.5); g.line(o.cx + 3, 11 + o.y, o.cx + 6, 13 + o.y, 1, BRASS_D); },
  },
  flute: {
    hands: (o) => ({ fh: [o.cx + 9 + o.ext, 12 + o.y], bh: [o.cx + 5 + o.ext, 12 + o.y] }),
    front(g, o) { const y = 11 + o.y; g.line(o.cx + 1 + o.ext, y, o.cx + 14 + o.ext, y, 1, SILVER);
      for (let i = 4; i < 13; i += 2) g.px(o.cx + i + o.ext, y, SILVER_D); notes(g, o, o.cx + 15 + o.ext, y - 3); },
  },
  trumpet: {
    hands: (o) => ({ fh: [o.cx + 7 + o.ext, 12 + o.y], bh: [o.cx + 5 + o.ext, 12 + o.y] }),
    front(g, o) { const y = 11 + o.y, x = o.cx + 3 + o.ext;
      g.rect(x, y, 6, 1, BRASS); g.rect(x + 1, y + 1, 5, 1, BRASS_D); g.rect(x + 2, y - 1, 1, 1, BRASS_L); g.rect(x + 3, y - 1, 1, 1, BRASS_L); g.rect(x + 4, y - 1, 1, 1, BRASS_L);
      g.rect(x + 6, y - 1, 1, 3, BRASS); g.rect(x + 7, y - 2, 1, 5, BRASS_L); notes(g, o, x + 9, y - 3); },
  },
  trombone: {
    hands: (o) => ({ fh: [o.cx + 12 + o.ext + (o.play ? 3 : 0), 13 + o.y], bh: [o.cx + 4, 12 + o.y] }),
    front(g, o) { const y = 11 + o.y, x = o.cx + 3, s = o.ext + (o.play ? 3 : 0);
      g.rect(x, y, 9, 1, BRASS); g.rect(x + 5, y - 2, 1, 5, BRASS_D);          // body + brace
      g.rect(x + 7, y - 2, 1, 5, BRASS); g.rect(x + 8, y - 3, 1, 7, BRASS_L);  // bell
      g.rect(x + 1, y + 2, 9 + s, 1, SILVER); g.rect(x + 9 + s, y, 1, 3, SILVER); g.rect(x + 1, y + 1, 1, 1, BRASS_D);
      notes(g, o, x + 10, y - 4); },
  },
  clarinet: {
    hands: (o) => ({ fh: [o.cx + 7 + o.ext, 19 + o.y], bh: [o.cx + 5 + o.ext, 15 + o.y] }),
    front(g, o) { const y = o.y, x = o.cx + o.ext; g.line(x + 3, 12 + y, x + 8, 23 + y, 1, EBONY);
      g.px(x + 5, 16 + y, SILVER); g.px(x + 6, 18 + y, SILVER); g.px(x + 7, 20 + y, SILVER);
      g.rect(x + 8, 23 + y, 2, 1, '#3a3a46'); g.rect(x + 7, 24 + y, 3, 1, EBONY); notes(g, o, x + 11, 20 + y); },
  },
  bassclarinet: {
    hands: (o) => ({ fh: [o.cx + 6 + o.ext, 24 + o.y], bh: [o.cx + 6 + o.ext, 18 + o.y] }),
    front(g, o) { const y = o.y, x = o.cx + o.ext;
      g.line(x + 3, 12 + y, x + 5, 14 + y, 1, SILVER); g.rect(x + 5, 14 + y, 2, 15, EBONY);
      for (let k = 16; k < 28; k += 3) g.px(x + 6, k + y, SILVER);
      g.rect(x + 5, 29 + y, 4, 1, SILVER); g.rect(x + 8, 26 + y, 2, 3, SILVER); g.rect(x + 9, 25 + y, 2, 1, SILVER_D);
      g.line(x + 5, 30 + y, x + 5, 34 + y, 1, SILVER_D); notes(g, o, x + 11, 24 + y, '#a78bfa'); },
  },
  flag: {
    hands: (o) => ({ fh: [o.cx + 7 + o.ext, 14 + o.y], bh: [o.cx + 5 + o.ext, 20 + o.y] }),
    front(g, o) { const x = o.cx + 6 + o.ext, y = o.y; g.line(x, 2 + y, x + 1, 30 + y, 1, SILVER);
      g.rect(x + 1, 2 + y, 8, 6, '#ff006e'); g.rect(x + 1, 5 + y, 8, 1, '#ffd23f'); },
  },
};
function stick(g, h, d) { g.line(h[0], h[1], h[0] + d[0], h[1] + d[1], 1, WOOD); }
function mallet(g, h, d) { g.line(h[0], h[1], h[0] + d[0], h[1] + d[1], 1, WOOD); g.rect(h[0] + d[0] - 1, h[1] + d[1] - 1, 2, 2, '#ff595e'); }
function notes(g, o, x, y, c = '#ffffff') { if (!o.play) return; const k = o.t % 3;
  g.rect(x + k, y - k, 1, 3, c); g.rect(x - 1 + k, y + 2 - k, 2, 1, c); g.px(x + 1 + k, y - k, c); }

// ---------- poses ----------
function basePose(cx) {
  return { y: 0, lean: 0, head: 0, face: 'n', ext: 0, play: false, arms: null,
    legs: { b: { k: [cx - 3, 30], f: [cx - 4, 36] }, f: { k: [cx + 3, 30], f: [cx + 4, 36] } } };
}
function poseFor(anim, i, cx) {
  const p = basePose(cx); const L = p.legs;
  switch (anim) {
    case 'idle': p.y = [0, 0, 1, 1][i]; L.b.k[1] += p.y; L.f.k[1] += p.y; break;
    case 'walk': { const a = (i / 6) * Math.PI * 2, s = Math.sin(a);
      L.b.f = [cx - 1 - Math.round(4 * s), 36 - (s > 0.3 ? 2 : 0)]; L.f.f = [cx + 1 + Math.round(4 * s), 36 - (s < -0.3 ? 2 : 0)];
      L.b.k = [(L.b.f[0] + cx) / 2 + 1, 30 - (s > 0.3 ? 1 : 0)]; L.f.k = [(L.f.f[0] + cx) / 2 + 2, 30 - (s < -0.3 ? 1 : 0)];
      p.y = Math.round(Math.abs(Math.cos(a))) ? 0 : 1; break; }
    case 'jump':
      if (i === 0) { p.y = 3; L.b.k = [cx - 1, 31]; L.f.k = [cx + 5, 31]; }
      else { const tuck = i === 3 ? 0 : (i === 2 ? 4 : 2); p.y = -2;
        L.b.k = [cx - 1, 27 - tuck / 2]; L.b.f = [cx - 4, 33 - tuck]; L.f.k = [cx + 5, 26 - tuck / 2]; L.f.f = [cx + 3, 32 - tuck]; }
      break;
    case 'crouch': p.y = i === 0 ? 4 : 8; L.b.k = [cx - 6, 33 - (i ? 2 : 0)]; L.f.k = [cx + 6, 32 - (i ? 2 : 0)]; L.b.f = [cx - 6, 36]; L.f.f = [cx + 6, 36]; break;
    case 'block': p.lean = -1; p.ext = -2; p.y = i; p.arms = { fh: [cx + 6, 13], bh: [cx + 5, 15] }; break;
    case 'punch': if (i === 0) { p.lean = -1; p.ext = -1; p.arms = { fh: [cx + 2, 17], bh: [cx + 4, 17] }; }
      else if (i === 1) { p.lean = 2; p.ext = 5; L.b.f = [cx - 7, 36]; L.b.k = [cx - 4, 31]; p.arms = { fh: [cx + 14, 15], bh: [cx + 5, 17], punch: true }; p.face = 'y'; }
      else { p.lean = 1; p.ext = 2; p.arms = { fh: [cx + 9, 16], bh: [cx + 4, 17], punch: true }; } break;
    case 'kick': p.lean = [0, -1, -2, -1][i];
      L.f.k = [[cx + 5, 27], [cx + 8, 25], [cx + 10, 24], [cx + 6, 26]][i]; L.f.f = [[cx + 3, 32], [cx + 13, 25], [cx + 16, 23], [cx + 8, 31]][i];
      L.b.f = [cx - 3, 36]; L.b.k = [cx - 2, 30]; if (i === 2) p.face = 'y'; break;
    case 'special': p.play = i >= 2 && i <= 4; p.lean = i < 2 ? -1 : (i === 5 ? 0 : 1); p.ext = i < 2 ? -1 : (p.play ? 1 : 0);
      if (p.play) { p.face = 'y'; L.b.f = [cx - 6, 36]; L.b.k = [cx - 4, 31]; } break;
    case 'hit': p.lean = -2 - i; p.head = -1 - i; p.face = 'h'; p.ext = -1; L.f.f = [cx + 3, 36]; L.b.f = [cx - 6, 36];
      p.arms = { fh: [cx + 7 - i, 13 - i], bh: [cx - 2, 14 - i] }; break;
    case 'ko': p.face = 'h'; p.lean = -2; p.arms = { fh: [cx + 6, 11], bh: [cx - 5, 12] }; break;
  }
  return p;
}

function drawFigure(g, look, id, p, cx) {
  const kind = INSTR_KIND[id] || 'trumpet'; const ins = INSTR[kind] || INSTR.trumpet;
  const big = look.build === 'big', slim = look.build === 'slim', tall = look.build === 'tall';
  const hw = big ? 6 : slim ? 3 : 4; const top = tall ? -1 : 0;
  const y = p.y, sx = cx + p.lean;                         // torso shift
  const jacket = look.jacket, jd = shade(jacket, -0.35), trim = look.trim, pants = look.pants, pd = shade(pants, -0.3);
  const o = { cx: sx, y, ext: p.ext, play: p.play, t: p._t || 0 };
  const hands = p.arms || ins.hands(o);
  if (p.arms && !STRAPPED[kind] && !p.arms.punch && p.ext !== undefined) {} // handheld follows ext
  if (p.arms && p.arms.punch && !STRAPPED[kind]) Object.assign(hands, ins.hands(o)); // instrument jab: hands stay on instrument
  const shB = [sx - hw + 1, 15 + y + top], shF = [sx + hw - 1, 15 + y + top];
  const hipB = [cx - 2, 24 + y], hipF = [cx + 2, 24 + y];
  // back arm
  arm(g, shB, hands.bh, jd);
  if (ins.back) ins.back(g, o);
  // back leg
  leg(g, hipB, p.legs.b, pd);
  // torso
  g.rect(sx - hw, 14 + y + top, hw * 2 + 1, 10 - top, jacket); g.rect(sx - hw, 14 + y + top, 2, 10 - top, jd);
  g.rect(sx - hw, 14 + y + top, hw * 2 + 1, 1, trim);
  g.line(sx - hw + 1, 15 + y + top, sx + hw, 22 + y, 1, '#f4f4f4'); g.line(sx + hw - 1, 15 + y + top, sx - hw + 1, 22 + y, 1, '#e2e2e2');
  g.rect(sx - hw, 23 + y, hw * 2 + 1, 1, '#151515'); g.px(sx + 1, 23 + y, trim);
  g.rect(cx - 3, 24 + y, 7, 2, pants);
  // front leg
  leg(g, hipF, p.legs.f, pants);
  // head
  const hx = sx + p.head, hy = 7 + y + top;
  g.rect(hx - 1, hy + 6, 2, 1, look.skin);
  g.rect(hx - 3, hy, 7, 6, look.skin); g.rect(hx - 3, hy, 2, 4, look.hair); g.px(hx - 3, hy + 4, look.hair);
  g.px(hx + 4, hy + 3, shade(look.skin, -0.15));
  if (p.face === 'h') { g.px(hx + 2, hy + 2, OUTLINE); g.px(hx + 2, hy + 3, OUTLINE); g.rect(hx + 1, hy + 5, 2, 1, '#7a1f1f'); }
  else if (p.face === 'y') { g.px(hx + 2, hy + 2, OUTLINE); g.rect(hx + 2, hy + 4, 2, 2, '#7a1f1f'); }
  else { g.px(hx + 2, hy + 2, OUTLINE); g.px(hx + 2, hy + 4, shade(look.skin, -0.35)); }
  // shako + plume
  g.rect(hx - 3, hy - 5, 7, 5, jacket); g.rect(hx - 3, hy - 5, 2, 5, jd); g.rect(hx - 3, hy - 2, 7, 1, trim);
  g.rect(hx - 3, hy - 1, 8, 1, '#151515'); g.px(hx + 1, hy - 4, trim);
  g.rect(hx - 1, hy - 7, 2, 2, look.plume); g.px(hx - 2, hy - 8 + (p._t % 2), look.plume); g.px(hx, hy - 8, shade(look.plume, -0.15));
  // instrument + front arm
  if (ins.front) ins.front(g, o, hands);
  arm(g, shF, hands.fh, jacket);
}
function arm(g, sh, hand, c) {
  const el = [(sh[0] + hand[0]) / 2 - 1, Math.max(sh[1], hand[1]) + 2 - Math.abs(hand[0] - sh[0]) / 4];
  g.line(sh[0], sh[1], el[0], el[1], 2, c); g.line(el[0], el[1], hand[0], hand[1], 2, c); g.rect(hand[0] - 1, hand[1] - 1, 2, 2, GLOVE);
}
function leg(g, hip, L, c) { g.line(hip[0], hip[1], L.k[0], L.k[1], 3, c); g.line(L.k[0], L.k[1], L.f[0], L.f[1] - 1, 3, c);
  g.rect(L.f[0] - 1, L.f[1] - 1, 4, 2, SHOE); g.px(L.f[0] - 1, L.f[1] - 2, '#f4f4f4'); }

function outline(c) {
  const ctx = c.getContext('2d'); const w = c.width, h = c.height; const d = ctx.getImageData(0, 0, w, h); const a = d.data;
  const out = new Uint8ClampedArray(a);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const i = (y * w + x) * 4; if (a[i + 3]) continue;
    const n = (x > 0 && a[i - 1]) || (x < w - 1 && a[i + 7]) || (y > 0 && a[i - w * 4 + 3]) || (y < h - 1 && a[i + w * 4 + 3]);
    if (n) { out[i] = 20; out[i + 1] = 12; out[i + 2] = 28; out[i + 3] = 255; } }
  d.data.set(out); ctx.putImageData(d, 0, 0);
}
function upscale(src, s) { const c = mk(src.width * s, src.height * s); const x = c.getContext('2d'); x.imageSmoothingEnabled = false;
  x.drawImage(src, 0, 0, c.width, c.height); return c; }

export function altLook(look) {
  // Player-2 mirror-match palette (SF2 style): swap jacket to a contrasting hue.
  return { ...look, jacket: shade(look.jacket, 0) === '#ffffff' ? '#333' : rotateHue(look.jacket, 150), plume: rotateHue(look.plume, 150) };
}
function rotateHue(hex, deg) {
  const n = parseInt(hex.slice(1), 16); let r = (n >> 16) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b); let h = 0, s = 0, l = (mx + mn) / 2;
  if (mx !== mn) { const d = mx - mn; s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
    h = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h /= 6; }
  h = (h + deg / 360) % 1; if (s < 0.15) { s = 0.6; l = Math.min(0.5, Math.max(0.35, l)); }
  const f = (p, q, t) => { t = (t + 1) % 1; return t < 1 / 6 ? p + (q - p) * 6 * t : t < 0.5 ? q : t < 2 / 3 ? p + (q - p) * (2 / 3 - t) * 6 : p; };
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s, p2 = 2 * l - q;
  return '#' + [f(p2, q, h + 1 / 3), f(p2, q, h), f(p2, q, h - 1 / 3)].map(v => Math.round(v * 255).toString(16).padStart(2, '0')).join('');
}

// Returns { anims: {name: [frame]}, portrait: canvas } with frame = {img, sx, sy, sw, sh, ax, ay}
export function proceduralFighter(def, alt = false) {
  const look = alt ? altLook(def.look) : def.look; const cx = 13;
  const anims = {};
  for (const [name, count] of ANIM_ROWS) {
    anims[name] = [];
    for (let i = 0; i < count; i++) {
      if (name === 'ko') { anims[name].push(koFrame(def, look, i, cx)); continue; }
      const u = mk(UW, UH); const g = P(u.getContext('2d')); const p = poseFor(name, i, cx); p._t = i;
      drawFigure(g, look, def.id, p, cx); outline(u);
      const big = upscale(u, U); const f = mk(FRAME_W, FRAME_H); f.getContext('2d').drawImage(big, 0, FRAME_H - big.height);
      anims[name].push({ img: f, sx: 0, sy: 0, sw: FRAME_W, sh: FRAME_H, ax: cx * U + U / 2, ay: FRAME_H });
    }
  }
  // portrait 64x64: head & shoulders from idle pose at 4x
  const u = mk(UW, UH); const g = P(u.getContext('2d')); const p = poseFor('idle', 0, cx); p._t = 0; p.face = 'y';
  drawFigure(g, look, def.id, p, cx); outline(u);
  const por = mk(64, 64); const pc = por.getContext('2d'); pc.imageSmoothingEnabled = false;
  const grd = pc.createLinearGradient(0, 0, 0, 64); grd.addColorStop(0, shade(look.jacket, 0.25)); grd.addColorStop(1, shade(look.jacket, -0.55));
  pc.fillStyle = grd; pc.fillRect(0, 0, 64, 64);
  pc.drawImage(u, cx - 7, 1, 16, 16, 0, 0, 64, 64);
  return { anims, portrait: por, source: 'procedural' };
}
function koFrame(def, look, i, cx) {
  const u = mk(UW, UH); const g = P(u.getContext('2d')); const p = poseFor('ko', i, cx); p._t = i;
  drawFigure(g, look, def.id, p, cx); outline(u);
  const W = 48, ang = [-0.15, -0.6, -1.2, -1.5][i], lift = [2, 4, 1, 0][i], shift = [0, 6, 14, 20][i];
  const r = mk(W, UH); const c = r.getContext('2d'); c.imageSmoothingEnabled = false;
  c.translate(cx + shift + 6, 36 - lift); c.rotate(ang); c.drawImage(u, -cx, -36);
  const big = upscale(r, U); return { img: big, sx: 0, sy: 0, sw: big.width, sh: big.height, ax: (cx + 6 + shift * 0.5) * U, ay: big.height };
}

// Projectiles: drawn live (no sheet). kind: note|bars|squeak|drone|quake|wave|chime|beam
export function drawProjectile(ctx, pr, t) {
  const x = Math.round(pr.x), y = Math.round(pr.y), d = pr.dir; ctx.save();
  switch (pr.kind) {
    case 'note': for (let k = 0; k < 3; k++) { ctx.fillStyle = k ? 'rgba(220,255,250,' + (0.5 - k * 0.15) + ')' : '#e9fffb';
      ctx.fillRect(x - d * k * 12 - 9, y - 3, 18, 6); } ctx.fillStyle = '#2a9d8f'; ctx.fillRect(x - 3, y - 9, 3, 12); ctx.fillRect(x - 9, y + 0, 9, 6); break;
    case 'bars': { const cols = ['#ff595e', '#ffca3a', '#8ac926', '#1982c4', '#6a4c93'];
      for (let k = 0; k < 5; k++) { ctx.fillStyle = cols[k]; ctx.fillRect(x - 15 + k * 6, y - 12 + ((t / 3 + k) % 4 | 0) * 3, 5, 18 - k * 2); } break; }
    case 'squeak': ctx.strokeStyle = '#fffb8f'; ctx.lineWidth = 3;
      for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.arc(x - d * k * 6, y, 6 + k * 5 + (t % 6), -1, 1); if (d < 0) { ctx.beginPath(); ctx.arc(x - d * k * 6, y, 6 + k * 5 + (t % 6), Math.PI - 1, Math.PI + 1); } ctx.stroke(); } break;
    case 'drone': { const s = pr.h / 2; ctx.fillStyle = 'rgba(90,40,180,0.45)'; ctx.fillRect(x - s, y - s, s * 2, s * 2);
      ctx.fillStyle = '#a78bfa'; for (let k = 0; k < 4; k++) ctx.fillRect(x - s + k * (s / 2) + (t % 8), y - s + ((k + t / 4) % 3 | 0) * s * 0.6, 6, s * 0.8);
      ctx.fillStyle = '#ffffff'; ctx.fillRect(x - 3, y - 3, 6, 6); break; }
    case 'quake': ctx.fillStyle = '#c9a227'; for (let k = 0; k < 5; k++) { const hgt = 6 + ((k * 7 + t) % 14); ctx.fillRect(x - 24 + k * 10, y - hgt, 8, hgt); }
      ctx.fillStyle = '#7a5c12'; ctx.fillRect(x - 26, y - 3, 52, 3); break;
    case 'wave': ctx.strokeStyle = pr.color || '#ffffff'; ctx.lineWidth = 4;
      for (let k = 0; k < 3; k++) { ctx.beginPath(); const r = 10 + k * 8 + (t % 6); ctx.arc(x - d * 18, y, r, d > 0 ? -0.9 : Math.PI - 0.9, d > 0 ? 0.9 : Math.PI + 0.9); ctx.stroke(); } break;
    case 'chime': ctx.fillStyle = pr.color || '#ffca3a'; ctx.fillRect(x - 15, y - 4, 30, 9); ctx.fillStyle = '#fff'; ctx.fillRect(x - 13, y - 3, 26, 2);
      ctx.fillStyle = SILVER_D; ctx.fillRect(x - 3, y - 18, 3, 14); break;
    case 'tornado': for (let k = 0; k < 7; k++) { ctx.fillStyle = k % 2 ? '#bff7ef' : '#e9fffb'; const w = 14 + k * 5;
      ctx.fillRect(x - w / 2 + Math.sin(t / 3 + k) * 6, y + 40 - k * 12, w, 8); } break;
    case 'flag': { const a = t / 3; ctx.translate(x, y); ctx.rotate(a); ctx.fillStyle = '#c9ced6'; ctx.fillRect(-20, -2, 40, 4);
      ctx.fillStyle = '#ff006e'; ctx.fillRect(4, -14, 16, 12); ctx.fillStyle = '#ffd23f'; ctx.fillRect(4, -9, 16, 2); break; }
    default: ctx.fillStyle = '#fff'; ctx.fillRect(x - 8, y - 8, 16, 16);
  }
  ctx.restore();
}
