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
// opts: {scale, color, align:'left'|'center'|'right', shadow:color|null, outline:color|null}
export function drawText(ctx, s, x, y, opts = {}) {
  s = String(s);
  const scale = opts.scale || 1, color = opts.color || '#fff';
  const w = textWidth(s, scale);
  if (opts.align === 'center') x -= w / 2; else if (opts.align === 'right') x -= w;
  x = Math.round(x); y = Math.round(y);
  const o = opts.outline === undefined ? '#000' : opts.outline;
  if (o) { const d = Math.max(1, Math.round(scale / 2));
    for (const [dx, dy] of [[-d,0],[d,0],[0,-d],[0,d],[d,d],[-d,d],[d,-d],[-d,-d]]) glyphs(ctx, s, x + dx, y + dy, scale, o); }
  if (opts.shadow) glyphs(ctx, s, x + scale, y + scale, scale, opts.shadow);
  if (opts.gradient) { // two-tone SF2-style: top color / bottom color
    ctx.save(); glyphs(ctx, s, x, y, scale, opts.gradient[1]);
    ctx.beginPath(); ctx.rect(x - 2, y - 2, w + 4, 3.5 * scale + 2); ctx.clip();
    glyphs(ctx, s, x, y, scale, opts.gradient[0]); ctx.restore();
  } else glyphs(ctx, s, x, y, scale, color);
  return w;
}
export function wrapText(s, maxChars) {
  const words = String(s).split(/\s+/); const lines = []; let cur = '';
  for (const w of words) { if ((cur + ' ' + w).trim().length > maxChars && cur) { lines.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); }
  if (cur) lines.push(cur); return lines;
}
