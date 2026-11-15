// 16-bit effects: hit sparks, block sparks, dust, rings, super-flash backgrounds.
import { VIEW_W, VIEW_H, FLOOR_Y } from './config.js';

export class FX {
  constructor(rand) { this.list = []; this.rand = rand || Math.random; }
  spark(x, y, o = {}) {
    const r = this.rand, big = !!o.big, block = !!o.block;
    const hot = block ? ['#ffffff', '#bdf3ff', '#46b4ff'] : big ? ['#ffffff', '#fff3a0', '#ff9a1f', '#ff3b1f'] : ['#ffffff', '#ffe27a', '#ff8a1f'];
    this.list.push({ k: 'flash', x, y, t: 0, life: big ? 9 : 6, r: big ? 26 : 16, cols: hot });
    this.list.push({ k: 'ring', x, y, t: 0, life: big ? 14 : 10, r: big ? 34 : 22, col: block ? '#8fe3ff' : '#fff2b0' });
    const n = big ? 12 : block ? 6 : 8;
    for (let i = 0; i < n; i++) { const a = r() * Math.PI * 2, s = (big ? 4.5 : 3) * (0.5 + r());
      this.list.push({ k: 'shard', x, y, vx: Math.cos(a) * s + (o.dir || 0) * 1.2, vy: Math.sin(a) * s - 0.6, t: 0, life: 10 + (r() * 8 | 0), col: hot[1 + (i % (hot.length - 1))], sz: big ? 3 : 2 }); }
  }
  dust(x, n = 6, dir = 0, big = false) {
    const r = this.rand;
    for (let i = 0; i < n; i++) this.list.push({ k: 'dust', x: x + (r() - 0.5) * (big ? 70 : 34), y: FLOOR_Y - 2, vx: (r() - 0.5) * 1.6 + dir * 1.2, vy: -0.3 - r() * 0.7,
      t: 0, life: 22 + (r() * 14 | 0), r0: big ? 5 : 3, r1: big ? 16 : 10, col: i % 2 ? '#c9b99a' : '#a8977a' });
  }
  ring(x, y, col = '#ffffff', r = 40) { this.list.push({ k: 'ring', x, y, t: 0, life: 16, r, col }); }
  update() { for (const e of this.list) { e.t++; if (e.vx !== undefined) { e.x += e.vx; e.y += e.vy; if (e.k === 'shard') { e.vy += 0.25; e.vx *= 0.93; } else { e.vx *= 0.94; e.vy *= 0.97; } } }
    this.list = this.list.filter(e => e.t < e.life); }
  draw(ctx, cam) {
    for (const e of this.list) { const x = Math.round(e.x - cam), y = Math.round(e.y), p = e.t / e.life;
      ctx.save();
      if (e.k === 'flash') { const r = e.r * (0.6 + p * 0.6); const g = ctx.createRadialGradient(x, y, 0, x, y, r);
        g.addColorStop(0, e.cols[0]); g.addColorStop(0.35, e.cols[1]); g.addColorStop(0.7, e.cols[2] + 'aa'); g.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.globalAlpha = 1 - p * 0.6; ctx.fillStyle = g; ctx.beginPath();
        for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 + e.t * 0.2, rr = i % 2 ? r * 0.45 : r; ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
        ctx.closePath(); ctx.fill(); }
      else if (e.k === 'ring') { ctx.globalAlpha = 1 - p; ctx.strokeStyle = e.col; ctx.lineWidth = 3 * (1 - p) + 1; ctx.beginPath(); ctx.ellipse(x, y, e.r * p + 4, (e.r * p + 4) * 0.8, 0, 0, Math.PI * 2); ctx.stroke(); }
      else if (e.k === 'shard') { ctx.globalAlpha = 1 - p * 0.7; ctx.fillStyle = e.col; ctx.fillRect(x - e.sz / 2, y - e.sz / 2, e.sz, e.sz); ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.fillRect(x - e.vx | 0, y - e.vy | 0, 1, 1); }
      else if (e.k === 'dust') { const r = e.r0 + (e.r1 - e.r0) * p; ctx.globalAlpha = 0.55 * (1 - p); ctx.fillStyle = e.col; ctx.beginPath(); ctx.arc(x, y - r * 0.5, r, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.beginPath(); ctx.arc(x - r * 0.3, y - r * 0.8, r * 0.45, 0, Math.PI * 2); ctx.fill(); }
      ctx.restore(); }
  }
}

// SF2 Turbo-style super flash: the stage blacks out behind a strobing radial burst from the fighter.
export function drawSuperBG(ctx, freeze, cam, frame) {
  const f = freeze.f, t = 40 - freeze.t, x = f.x - cam, y = FLOOR_Y - f.y - 60;
  ctx.save();
  ctx.fillStyle = t < 3 ? 'rgba(255,255,255,0.85)' : 'rgba(6,2,22,0.86)'; ctx.fillRect(-10, 0, VIEW_W + 20, VIEW_H);
  const cols = f.side ? ['rgba(70,140,255,0.55)', 'rgba(150,90,255,0.35)'] : ['rgba(255,80,40,0.55)', 'rgba(255,200,40,0.35)'];
  for (let i = 0; i < 18; i++) { const a0 = i * Math.PI / 9 + t * 0.05 * (f.side ? -1 : 1), a1 = a0 + Math.PI / 22;
    ctx.fillStyle = cols[i % 2]; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(a0) * 900, y + Math.sin(a0) * 900); ctx.lineTo(x + Math.cos(a1) * 900, y + Math.sin(a1) * 900); ctx.closePath(); ctx.fill(); }
  const g = ctx.createRadialGradient(x, y, 0, x, y, 120); g.addColorStop(0, 'rgba(255,255,255,0.9)'); g.addColorStop(0.3, 'rgba(255,240,180,0.4)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(x - 120, y - 120, 240, 240);
  ctx.restore();
}
