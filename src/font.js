// 5x7 bitmap font for crisp arcade text.
const G = {
  A:[14,17,17,31,17,17,17],B:[30,17,17,30,17,17,30],C:[14,17,16,16,16,17,14],D:[30,17,17,17,17,17,30],
  E:[31,16,16,30,16,16,31],F:[31,16,16,30,16,16,16],G:[14,17,16,23,17,17,15],H:[17,17,17,31,17,17,17],
  I:[14,4,4,4,4,4,14],J:[7,2,2,2,2,18,12],K:[17,18,20,24,20,18,17],L:[16,16,16,16,16,16,31],
  M:[17,27,21,21,17,17,17],N:[17,17,25,21,19,17,17],O:[14,17,17,17,17,17,14],P:[30,17,17,30,16,16,16],
  Q:[14,17,17,17,21,18,13],R:[30,17,17,30,20,18,17],S:[15,16,16,14,1,1,30],T:[31,4,4,4,4,4,4],
  U:[17,17,17,17,17,17,14],V:[17,17,17,17,17,10,4],W:[17,17,17,21,21,21,10],X:[17,17,10,4,10,17,17],
  Y:[17,17,17,10,4,4,4],Z:[31,1,2,4,8,16,31],
  0:[14,17,19,21,25,17,14],1:[4,12,4,4,4,4,14],2:[14,17,1,2,4,8,31],3:[31,2,4,2,1,17,14],
  4:[2,6,10,18,31,2,2],5:[31,16,30,1,1,17,14],6:[6,8,16,30,17,17,14],7:[31,1,2,4,8,8,8],
  8:[14,17,17,14,17,17,14],9:[14,17,17,15,1,2,12],
  ' ':[0,0,0,0,0,0,0],'.':[0,0,0,0,0,12,12],'!':[4,4,4,4,4,0,4],'?':[14,17,1,2,4,0,4],
  '-':[0,0,0,31,0,0,0],':':[0,12,12,0,12,12,0],',':[0,0,0,0,12,4,8],"'":[4,4,8,0,0,0,0],
  '"':[10,10,0,0,0,0,0],'/':[1,1,2,4,8,16,16],'&':[12,18,20,8,21,18,13],'(':[2,4,8,8,8,4,2],
  ')':[8,4,2,2,2,4,8],'+':[0,4,4,31,4,4,0],'%':[24,25,2,4,8,19,3],'#':[10,10,31,10,31,10,10],
  '>':[8,4,2,1,2,4,8],'<':[2,4,8,16,8,4,2],'*':[0,4,21,14,21,4,0],'=':[0,0,31,0,31,0,0],
  ';':[0,12,12,0,12,4,8],'_':[0,0,0,0,0,0,31],
};
export function textWidth(s, scale = 1) { return s.length * 6 * scale - scale; }
function glyphs(ctx, s, x, y, scale, color) {
  ctx.fillStyle = color;
  for (let i = 0; i < s.length; i++) {
    const g = G[s[i].toUpperCase()] || G['?'];
    for (let r = 0; r < 7; r++) { const row = g[r]; if (!row) continue;
      for (let c = 0; c < 5; c++) if (row & (16 >> c)) ctx.fillRect(x + (i * 6 + c) * scale, y + r * scale, scale, scale); }
  }
}
// 16-bit text (SF2 Turbo flavour): glyphs rendered once into an offscreen canvas with an italic shear on big
// sizes, a vertical gradient fill, thick dark outline and drop shadow, then cached.
// opts: {scale, color, gradient:[top,(mid),bottom], align, outline:color|null, shadow:color|null|false, italic:bool, flat:bool}
const cache = new Map();
function shadeHex(hex, f) {
  if (!/^#[0-9a-f]{6}$/i.test(hex)) return hex; const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  if (f < 0) { r *= 1 + f; g *= 1 + f; b *= 1 + f; } else { r += (255 - r) * f; g += (255 - g) * f; b += (255 - b) * f; }
  return '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
}
function cv(w, h) { const c = document.createElement('canvas'); c.width = Math.max(1, w); c.height = Math.max(1, h); return c; }
function tint(src, color) { const c = cv(src.width, src.height), x = c.getContext('2d'); x.drawImage(src, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = color; x.fillRect(0, 0, c.width, c.height); return c; }
function render(s, scale, opts) {
  const italic = opts.italic ?? scale >= 2, sh = italic ? 0.3 : 0, ow = opts.outline === null ? 0 : Math.max(1, Math.round(scale * 0.45)), pad = ow + Math.ceil(scale / 2) + 2;
  const tw = textWidth(s, scale), ext = Math.ceil(7 * scale * sh);
  const M = cv(tw + ext + pad * 2, 7 * scale + pad * 2), m = M.getContext('2d'); m.fillStyle = '#fff';
  for (let i = 0; i < s.length; i++) { const g = G[s[i].toUpperCase()] || G['?'];
    for (let r = 0; r < 7; r++) { const row = g[r]; if (!row) continue; const off = Math.round((6 - r) * scale * sh);
      for (let c = 0; c < 5; c++) if (row & (16 >> c)) m.fillRect(pad + off + (i * 6 + c) * scale, pad + r * scale, scale + (scale >= 3 ? 1 : 0), scale); } }
  const cols = opts.gradient || (opts.flat ? [opts.color, opts.color] : [shadeHex(opts.color, 0.45), opts.color, shadeHex(opts.color, -0.25)]);
  const F = tint(M, '#fff'), f = F.getContext('2d'); f.globalCompositeOperation = 'source-in';
  const gr = f.createLinearGradient(0, pad, 0, pad + 7 * scale); cols.forEach((c, i) => gr.addColorStop(i / (cols.length - 1), c)); f.fillStyle = gr; f.fillRect(0, 0, F.width, F.height);
  const out = cv(M.width, M.height), o = out.getContext('2d');
  const shadow = opts.shadow === undefined ? (scale >= 2 ? 'rgba(0,0,0,0.55)' : null) : opts.shadow;
  if (shadow) o.drawImage(tint(M, shadow), Math.ceil(scale / 2) + 1, Math.ceil(scale / 2) + 1);
  if (ow) { const O = tint(M, opts.outline || '#10081c'); for (let dy = -ow; dy <= ow; dy++) for (let dx = -ow; dx <= ow; dx++) if (dx || dy) o.drawImage(O, dx, dy); }
  o.drawImage(F, 0, 0);
  if (scale >= 3) { o.globalCompositeOperation = 'source-atop'; o.fillStyle = 'rgba(255,255,255,0.35)'; o.fillRect(0, pad, out.width, Math.max(1, scale * 0.6)); }
  return { c: out, pad, w: tw };
}
export function drawText(ctx, s, x, y, opts = {}) {
  s = String(s); const scale = opts.scale || 1; opts.color = opts.color || '#ffffff';
  const key = s + '|' + scale + '|' + JSON.stringify([opts.color, opts.gradient, opts.outline, opts.shadow, opts.italic, opts.flat]);
  let r = cache.get(key); if (!r) { r = render(s, scale, opts); cache.set(key, r); if (cache.size > 600) cache.delete(cache.keys().next().value); }
  if (opts.align === 'center') x -= r.w / 2; else if (opts.align === 'right') x -= r.w;
  ctx.drawImage(r.c, Math.round(x - r.pad), Math.round(y - r.pad)); return r.w;
}
export function wrapText(s, maxChars) {
  const words = String(s).split(/\s+/); const lines = []; let cur = '';
  for (const w of words) { if ((cur + ' ' + w).trim().length > maxChars && cur) { lines.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); }
  if (cur) lines.push(cur); return lines;
}
