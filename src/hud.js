// 16-bit HUD: beveled gradient health bars with a draining red damage trail, timer, KO emblem, round medals, super meters.
import { VIEW_W, SUPER_MAX } from './config.js';
import { drawText } from './font.js';

function bevel(ctx, x, y, w, h) { // gold-edged frame with highlight + shadow
  ctx.fillStyle = '#10081c'; ctx.fillRect(x - 3, y - 3, w + 6, h + 6);
  const g = ctx.createLinearGradient(0, y - 2, 0, y + h + 2); g.addColorStop(0, '#fff1a8'); g.addColorStop(0.5, '#d4a017'); g.addColorStop(1, '#6b4a08');
  ctx.fillStyle = g; ctx.fillRect(x - 2, y - 2, w + 4, h + 4); ctx.fillStyle = '#10081c'; ctx.fillRect(x - 1, y - 1, w + 2, h + 2);
}
function barFill(ctx, x, y, w, h, stops) { if (w <= 0) return; const g = ctx.createLinearGradient(0, y, 0, y + h); stops.forEach((c, i) => g.addColorStop(i / (stops.length - 1), c)); ctx.fillStyle = g; ctx.fillRect(x, y, w, h); }

export function healthBar(ctx, f, x, y, w, h, leftSide, frame) {
  bevel(ctx, x, y, w, h);
  barFill(ctx, x, y, w, h, ['#3a0a10', '#22040a']);
  const hw = Math.round(w * f.hp / f.maxHp), tw = Math.round(w * Math.max(f.hp, f.dispHp) / f.maxHp);
  const at = (ww) => leftSide ? x : x + w - ww;            // SF2: bars empty from the KO emblem outward
  barFill(ctx, at(tw), y, tw, h, ['#ff6a5a', '#e01818', '#8a0610']);   // damage trail
  const danger = f.hp / f.maxHp < 0.25, blink = danger && frame % 16 < 8;
  barFill(ctx, at(hw), y, hw, h, blink ? ['#fff4c0', '#ffb000', '#c05a00'] : ['#fffbd0', '#ffe14d', '#f0b400', '#b07800']);
  ctx.fillStyle = 'rgba(255,255,255,0.5)'; if (hw > 2) ctx.fillRect(at(hw) + 1, y + 1, hw - 2, 1);
  for (let k = 1; k < 10; k++) { ctx.fillStyle = 'rgba(0,0,0,0.12)'; ctx.fillRect(x + Math.round(w * k / 10), y, 1, h); }
}
export function superBar(ctx, f, x, y, w, rightAlign, frame) {
  const full = f.meter >= SUPER_MAX, h = 7; bevel(ctx, x, y, w, h); barFill(ctx, x, y, w, h, ['#0c1238', '#060a20']);
  const mw = Math.round(w * Math.min(1, Math.max(0, f.meter / SUPER_MAX))), at = rightAlign ? x + w - mw : x;
  if (full) { const hue = (frame * 6) % 360; barFill(ctx, at, y, mw, h, [`hsl(${hue},100%,85%)`, `hsl(${hue},100%,55%)`, `hsl(${(hue + 40) % 360},100%,35%)`]); }
  else barFill(ctx, at, y, mw, h, ['#bfe0ff', '#3a86ff', '#1838a8']);
  ctx.fillStyle = 'rgba(255,255,255,0.45)'; if (mw > 2) ctx.fillRect(at + 1, y + 1, mw - 2, 1);
  drawText(ctx, full ? 'SUPER!' : 'SUPER', rightAlign ? x + w : x, y - 11, { color: full ? '#9ff7ff' : '#9db4ff', align: rightAlign ? 'right' : 'left' });
}
export function medal(ctx, x, y, on) {
  ctx.fillStyle = '#10081c'; ctx.beginPath(); ctx.arc(x + 6, y + 6, 7, 0, Math.PI * 2); ctx.fill();
  const g = ctx.createRadialGradient(x + 4, y + 4, 1, x + 6, y + 6, 7);
  if (on) { g.addColorStop(0, '#ffffff'); g.addColorStop(0.35, '#ffe14d'); g.addColorStop(1, '#a06a00'); } else { g.addColorStop(0, '#666'); g.addColorStop(1, '#222'); }
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x + 6, y + 6, 6, 0, Math.PI * 2); ctx.fill();
  if (on) drawText(ctx, 'V', x + 6, y + 3, { align: 'center', color: '#c8202c', outline: null, shadow: null, flat: true });
}
export function drawHUD(ctx, F) {
  const [a, b] = F.f, BW = 246, BH = 13, Y = 14, fr = F.frame;
  healthBar(ctx, a, 26, Y, BW, BH, true, fr); healthBar(ctx, b, VIEW_W - 26 - BW, Y, BW, BH, false, fr);
  // KO emblem
  const kx = VIEW_W / 2 - 22, ky = Y - 6; bevel(ctx, kx, ky, 44, 24);
  const lowAny = Math.min(a.hp / a.maxHp, b.hp / b.maxHp) < 0.25 && fr % 20 < 10;
  barFill(ctx, kx, ky, 44, 24, lowAny ? ['#ffffff', '#ffb0a0', '#ff3b30'] : ['#ff7060', '#d01818', '#6a0408']);
  drawText(ctx, 'KO', VIEW_W / 2, ky + 5, { scale: 2, align: 'center', gradient: ['#ffffff', '#ffe14d'], outline: '#3a0408', italic: true });
  // timer
  const tt = F.settings.roundTime > 0 ? String(Math.max(0, F.timer)).padStart(2, '0') : '--';
  drawText(ctx, tt, VIEW_W / 2, Y + 24, { scale: 4, align: 'center', gradient: ['#ffffff', '#ffe14d', '#ff7b00'], italic: true });
  // names + medals
  drawText(ctx, a.def.fullName, 26, Y + 20, { color: '#ffffff', italic: true });
  drawText(ctx, b.def.fullName, VIEW_W - 26, Y + 20, { color: '#ffffff', align: 'right', italic: true });
  for (let i = 0; i < F.settings.roundsToWin; i++) { medal(ctx, 26 + i * 16, Y + 31, i < a.wins); medal(ctx, VIEW_W - 38 - i * 16, Y + 31, i < b.wins); }
  superBar(ctx, a, 26, 340, 150, false, fr); superBar(ctx, b, VIEW_W - 26 - 150, 340, 150, true, fr);
}
