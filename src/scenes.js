import { VIEW_W, VIEW_H, FLOOR_Y } from './config.js';
import { drawText, wrapText, textWidth } from './font.js';
import { drawStage } from './stage.js';
import { Fight } from './fight.js';
import { CPU } from './ai.js';
import { audio } from './audio.js';

const TITLE = ['JMHS', 'MARCHING BAND', 'ATTACK!'];
function panel(ctx, x, y, w, h, fill = 'rgba(8,12,40,0.85)', edge = '#d4a017') { ctx.fillStyle = '#000'; ctx.fillRect(x - 2, y - 2, w + 4, h + 4); ctx.fillStyle = edge; ctx.fillRect(x - 1, y - 1, w + 2, h + 2); ctx.fillStyle = fill; ctx.fillRect(x, y, w, h); }
// portraits: the optional 128x128 portrait_large.png is used for anything drawn bigger than 64px, else portrait.png upscaled
function portrait(ctx, art, x, y, size, flip, dim) {
  const img = size > 64 && art.portraitLarge ? art.portraitLarge : art.portrait; if (!img) return;
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(x + (flip ? size : 0), y); ctx.scale(flip ? -1 : 1, 1);
  ctx.drawImage(img, 0, 0, size, size); if (dim) { ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(0, 0, size, size); } ctx.restore(); }
function frame16(ctx, x, y, w, h, glow) { // beveled gold frame (16-bit select style)
  ctx.fillStyle = '#10081c'; ctx.fillRect(x - 5, y - 5, w + 10, h + 10);
  const g = ctx.createLinearGradient(0, y - 4, 0, y + h + 4); g.addColorStop(0, '#fff1a8'); g.addColorStop(0.5, glow || '#d4a017'); g.addColorStop(1, '#5a3c06');
  ctx.fillStyle = g; ctx.fillRect(x - 4, y - 4, w + 8, h + 8); ctx.fillStyle = '#10081c'; ctx.fillRect(x - 1, y - 1, w + 2, h + 2); }
function sprite(ctx, art, anim, t, x, y, scale = 1, flip = false) {
  const fr = art.anims[anim] || art.anims.idle; const f = fr[Math.floor(t / 9) % fr.length];
  ctx.save(); ctx.translate(Math.round(x), Math.round(y)); ctx.scale(flip ? -scale : scale, scale); ctx.drawImage(f.img, f.sx, f.sy, f.sw, f.sh, -f.ax, -f.ay, f.sw, f.sh); ctx.restore(); }
const anyP = (G, b) => G.ctl[0].p[b] || G.ctl[1].p[b];

// ---------------- Title ----------------
export class TitleScene {
  constructor(G) { this.G = G; this.t = 0; this.sel = 0; this.items = [['ARCADE', 'arcade'], ['VS CPU', 'cpu'], ['2P VERSUS', 'versus'], ['CPU VS CPU', 'watch'], ['HOW TO PLAY', 'howto'], ['OPTIONS', 'options']]; audio.play(G.content.music.title || G.content.music.football); }
  update() { const G = this.G; this.t++; for (const c of G.ctl) c.update();
    if (anyP(G, 'up')) { this.sel = (this.sel + this.items.length - 1) % this.items.length; audio.sfx('select'); }
    if (anyP(G, 'down')) { this.sel = (this.sel + 1) % this.items.length; audio.sfx('select'); }
    if (anyP(G, 'start') || anyP(G, 'punch')) { audio.sfx('confirm'); const m = this.items[this.sel][1];
      if (m === 'howto') G.go(new HowToScene(G)); else if (m === 'options') G.go(new OptionsScene(G)); else G.go(new SelectScene(G, m)); } }
  draw(ctx) { const G = this.G; const sa = G.stageArts[G.content.stages[0].id]; drawStage(ctx, sa, 160 + Math.sin(this.t / 200) * 140, this.t);
    ctx.fillStyle = 'rgba(5,8,30,0.55)'; ctx.fillRect(0, 0, VIEW_W, VIEW_H);
    // marching parade across the field
    const n = G.content.fighters.length; G.content.fighters.forEach((d, i) => { const x = ((this.t * 0.8 + i * (VIEW_W + 120) / n) % (VIEW_W + 120)) - 60; sprite(ctx, G.arts[d.id], 'walk', this.t + i * 7, x, FLOOR_Y + 20, 0.8); });
    drawText(ctx, TITLE[0], VIEW_W / 2, 26, { scale: 4, align: 'center', gradient: ['#ffffff', '#d4a017'] });
    drawText(ctx, TITLE[1], VIEW_W / 2, 64, { scale: 6, align: 'center', gradient: ['#ffe14d', '#ff7b00'], outline: '#17305f' });
    drawText(ctx, TITLE[2], VIEW_W / 2 + Math.sin(this.t / 10) * 2, 112, { scale: 9, align: 'center', gradient: ['#ffffff', '#ff3b30'], outline: '#000' });
    panel(ctx, VIEW_W / 2 - 90, 186, 180, 92);
    this.items.forEach(([s], i) => drawText(ctx, (i === this.sel ? '> ' : '  ') + s, VIEW_W / 2 - 74, 194 + i * 14, { scale: 1, color: i === this.sel ? '#ffe14d' : '#ffffff' }));
    if (this.t % 60 < 40) drawText(ctx, 'PRESS START (ENTER)', VIEW_W / 2, 286, { align: 'center', color: '#ffffff' });
    drawText(ctx, 'P1: WASD + F G H, R=SUPER    P2: ARROWS + NUM 1 2 3, NUM0=SUPER', VIEW_W / 2, 348, { align: 'center', color: '#9db4ff' }); }
}

// ---------------- Character select ----------------
export class SelectScene {
  constructor(G, mode) { this.G = G; this.mode = mode; this.t = 0; const F = G.content.fighters;
    this.cols = Math.ceil(F.length / 2); this.cur = [0, Math.min(F.length - 1, this.cols - 1)]; this.done = [false, mode === 'arcade'];
    this.picking = mode === 'cpu' || mode === 'watch' ? 0 : -1; // single-controller picks both in order
    G.ctl[0].solo = mode !== 'versus'; audio.play(G.content.music.select || G.content.music.lockerroom); }
  cellPos(i) { const F = this.G.content.fighters, row = i < this.cols ? 0 : 1, inRow = row ? F.length - this.cols : this.cols, col = row ? i - this.cols : i;
    const S = 66, x0 = VIEW_W / 2 - (inRow * S) / 2; return [x0 + col * S, 212 + row * S]; }
  move(i, dx, dy) { const F = this.G.content.fighters; let row = i < this.cols ? 0 : 1, col = row ? i - this.cols : i;
    const rows = [this.cols, F.length - this.cols]; if (dy) { row = 1 - row; col = Math.min(col, rows[row] - 1); } col = (col + dx + rows[row]) % rows[row]; return row ? this.cols + col : col; }
  update() { const G = this.G; this.t++; for (const c of G.ctl) c.update();
    const F = G.content.fighters;
    const handle = (ci, pi) => { const c = G.ctl[ci]; if (this.done[pi]) { if (c.p.back) { this.done[pi] = false; audio.sfx('select'); } return; }
      let i = this.cur[pi]; if (c.p.left) i = this.move(i, -1, 0); if (c.p.right) i = this.move(i, 1, 0); if (c.p.up || c.p.down) i = this.move(i, 0, 1);
      if (i !== this.cur[pi]) audio.sfx('select'); this.cur[pi] = i;
      if (c.p.punch || c.p.kick || c.p.start) { this.done[pi] = true; audio.sfx('confirm'); audio.sfx(F[i].special.sound); } };
    if (this.picking >= 0) { const pi = this.done[0] ? 1 : 0; handle(0, pi); if (!this.done[0] && G.ctl[0].p.back) G.go(new TitleScene(G)); }
    else { handle(0, 0); if (this.mode === 'versus') handle(1, 1); if (!this.done[0] && G.ctl[0].p.back) G.go(new TitleScene(G)); }
    if (this.done[0] && this.done[1]) { if (!this.wait) this.wait = 40; else if (--this.wait === 0) {
      const p1 = F[this.cur[0]];
      if (this.mode === 'arcade') { const others = F.filter(f => f.id !== p1.id).sort(() => Math.random() - 0.5); G.arcade = { p1, ladder: others, idx: 0, continues: 0 }; G.startArcadeMatch(); }
      else G.go(new StageSelectScene(G, this.mode, p1, F[this.cur[1]])); } } }
  draw(ctx) { const G = this.G, F = G.content.fighters;
    const g = ctx.createLinearGradient(0, 0, 0, VIEW_H); g.addColorStop(0, '#0c1734'); g.addColorStop(1, '#3a0c4a'); ctx.fillStyle = g; ctx.fillRect(0, 0, VIEW_W, VIEW_H);
    for (let y = 0; y < VIEW_H; y += 4) { ctx.fillStyle = 'rgba(255,255,255,0.03)'; ctx.fillRect(0, y, VIEW_W, 1); }
    drawText(ctx, 'PLAYER SELECT', VIEW_W / 2, 10, { scale: 3, align: 'center', gradient: ['#ffffff', '#d4a017'] });
    // big portraits (SF2 Turbo style): 1P left, 2P/CPU right
    const side = (pi) => { const d = F[this.cur[pi]], a = G.arts[d.id], alt = pi === 1 && this.cur[0] === this.cur[1] && a.alt;
      const x = pi ? VIEW_W - 20 - 128 : 20, y = 44, cx = x + 64, done = this.done[pi];
      frame16(ctx, x, y, 128, 128, done && this.t % 8 < 4 ? '#ffffff' : pi ? '#4a8cff' : '#ff4a3a');
      const bg = ctx.createLinearGradient(0, y, 0, y + 128); bg.addColorStop(0, pi ? '#16307a' : '#7a1620'); bg.addColorStop(1, '#0a0618'); ctx.fillStyle = bg; ctx.fillRect(x, y, 128, 128);
      portrait(ctx, alt || a, x, y, 128, pi === 1, false);
      if (done) { ctx.fillStyle = 'rgba(255,255,255,' + Math.max(0, 0.6 - (this.t % 30) / 30) + ')'; ctx.fillRect(x, y, 128, 128); }
      const lbl = this.mode === 'arcade' && pi === 1 ? null : (pi === 1 && this.mode !== 'versus' ? 'CPU' : pi ? '2P' : '1P');
      if (!lbl) { drawText(ctx, '?', cx, y + 40, { scale: 8, align: 'center', color: '#ffffff' }); return; }
      drawText(ctx, lbl, pi ? x + 122 : x + 6, y + 6, { scale: 2, align: pi ? 'right' : 'left', color: pi ? '#7ab8ff' : '#ff6b6b' });
      drawText(ctx, d.short, cx, 180, { scale: 3, align: 'center', gradient: pi ? ['#ffffff', '#7ab8ff', '#2a5ad0'] : ['#ffffff', '#ffb0a0', '#e0302a'], italic: true });
      drawText(ctx, d.instrument.toUpperCase(), cx, 206, { align: 'center', color: '#ffe14d' });
      wrapText(d.special.name, 22).slice(0, 2).forEach((l, i) => drawText(ctx, l, cx, 218 + i * 10, { align: 'center', color: '#ffffff' }));
      wrapText('SUPER: ' + d.super.name, 22).slice(0, 2).forEach((l, i) => drawText(ctx, l, cx, 240 + i * 10, { align: 'center', color: '#7ef9ff' }));
      sprite(ctx, alt ? { ...a, anims: a.alt.anims } : a, done ? 'special' : 'idle', this.t, cx, 340, 0.75, pi === 1); };
    side(0); side(1);
    // centre info box
    const d = F[this.cur[this.picking >= 0 && this.done[0] ? 1 : 0]];
    panel(ctx, 172, 44, 296, 156); drawText(ctx, d.fullName, 320, 52, { align: 'center', color: '#ffe14d', italic: true });
    drawText(ctx, (d.section || '').toUpperCase(), 320, 64, { align: 'center', color: '#9db4ff' });
    wrapText(d.fightingStyle || '', 46).slice(0, 8).forEach((l, i) => drawText(ctx, l, 180, 80 + i * 10, { color: '#ffffff', outline: null, shadow: null }));
    if (d.taunt) wrapText('"' + d.taunt + '"', 46).slice(0, 2).forEach((l, i) => drawText(ctx, l, 180, 176 + i * 10, { color: '#ffd23f', outline: null, shadow: null }));
    // grid
    F.forEach((f, i) => { const [x, y] = this.cellPos(i); ctx.fillStyle = '#10081c'; ctx.fillRect(x - 1, y - 1, 66, 66);
      const cg = ctx.createLinearGradient(0, y, 0, y + 64); cg.addColorStop(0, '#2a3a8a'); cg.addColorStop(1, '#0a0a2a'); ctx.fillStyle = cg; ctx.fillRect(x, y, 64, 64);
      portrait(ctx, G.arts[f.id], x, y, 64, false, false); ctx.fillStyle = 'rgba(255,255,255,0.18)'; ctx.fillRect(x, y, 64, 1); });
    const cursor = (pi, col, lbl) => { const [x, y] = this.cellPos(this.cur[pi]); const on = this.done[pi] || this.t % 20 < 14; if (!on) return;
      ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.strokeRect(x - 2.5 + pi, y - 2.5 + pi, 68 - pi * 2, 68 - pi * 2);
      ctx.fillStyle = col; ctx.fillRect(x + (pi ? 44 : 0), y + (pi ? 0 : 52), 20, 12); drawText(ctx, lbl, x + (pi ? 46 : 2), y + (pi ? 3 : 55), { color: '#fff', outline: null }); };
    if (this.mode === 'arcade') cursor(0, '#ff3b30', '1P');
    else { cursor(0, '#ff3b30', '1P'); if (this.picking < 0 || this.done[0]) cursor(1, '#3a86ff', this.mode === 'versus' ? '2P' : 'CPU'); }
    drawText(ctx, this.mode === 'versus' ? 'P1 + P2 CHOOSE' : this.picking >= 0 && this.done[0] ? 'NOW CHOOSE YOUR OPPONENT' : 'CHOOSE YOUR FIGHTER', VIEW_W / 2, 350, { align: 'center', color: '#ffffff' }); }
}

// ---------------- Stage select ----------------
export class StageSelectScene {
  constructor(G, mode, p1, p2) { Object.assign(this, { G, mode, p1, p2, t: 0, sel: 0 }); }
  update() { const G = this.G, S = G.content.stages; this.t++; for (const c of G.ctl) c.update();
    if (anyP(G, 'left')) { this.sel = (this.sel + S.length) % (S.length + 1); audio.sfx('select'); }
    if (anyP(G, 'right')) { this.sel = (this.sel + 1) % (S.length + 1); audio.sfx('select'); }
    if (anyP(G, 'back')) G.go(new SelectScene(G, this.mode));
    if (anyP(G, 'start') || anyP(G, 'punch')) { audio.sfx('confirm'); const st = this.sel === S.length ? S[(Math.random() * S.length) | 0] : S[this.sel];
      G.go(new VSScene(G, { mode: this.mode, p1: this.p1, p2: this.p2, stage: st })); } }
  draw(ctx) { const G = this.G, S = G.content.stages; ctx.fillStyle = '#0c1734'; ctx.fillRect(0, 0, VIEW_W, VIEW_H);
    const cur = S[this.sel] || null; if (cur) { drawStage(ctx, G.stageArts[cur.id], 160, this.t); ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(0, 0, VIEW_W, VIEW_H); }
    drawText(ctx, 'STAGE SELECT', VIEW_W / 2, 14, { scale: 3, align: 'center', gradient: ['#ffffff', '#d4a017'] });
    const W = 140, H = 79, n = S.length + 1, x0 = VIEW_W / 2 - (n * (W + 10)) / 2 + 5;
    for (let i = 0; i < n; i++) { const x = x0 + i * (W + 10), y = 230; panel(ctx, x, y, W, H, '#000', i === this.sel ? '#ffe14d' : '#555');
      if (i < S.length) { const a = G.stageArts[S[i].id]; for (const L of [a.far, a.mid, a.anims && a.anims[0]]) if (L) ctx.drawImage(L, 0, 0, L.height * 16 / 9, L.height, x, y, W, H);
        drawText(ctx, S[i].name, x + W / 2, y + H + 6, { align: 'center', color: i === this.sel ? '#ffe14d' : '#fff' }); }
      else drawText(ctx, '?', x + W / 2, y + 26, { scale: 5, align: 'center', color: '#fff' }), drawText(ctx, 'RANDOM', x + W / 2, y + H + 6, { align: 'center', color: i === this.sel ? '#ffe14d' : '#fff' }); }
    if (cur) { drawText(ctx, cur.name, VIEW_W / 2, 60, { scale: 4, align: 'center', gradient: ['#ffe14d', '#ff7b00'] }); drawText(ctx, (cur.subtitle || '').toUpperCase(), VIEW_W / 2, 96, { align: 'center', color: '#fff' }); } }
}

// ---------------- VS screen ----------------
export class VSScene {
  constructor(G, m) { this.G = G; this.m = m; this.t = 0; audio.stop(); audio.sfx('heavy'); audio.announce(m.p1.short + ' versus ' + m.p2.short); }
  update() { const G = this.G; this.t++; for (const c of G.ctl) c.update(); if (this.t > 200 || (this.t > 30 && anyP(G, 'start'))) G.startFight(this.m); }
  draw(ctx) { const G = this.G, { p1, p2, stage } = this.m; const k = Math.min(1, this.t / 20);
    ctx.fillStyle = '#7a0d12'; ctx.fillRect(0, 0, VIEW_W / 2, VIEW_H); ctx.fillStyle = '#0c2a6b'; ctx.fillRect(VIEW_W / 2, 0, VIEW_W / 2, VIEW_H);
    for (let y = 0; y < VIEW_H; y += 6) { ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fillRect(0, y + (this.t % 6), VIEW_W, 2); }
    const a1 = G.arts[p1.id], a2 = G.arts[p2.id]; const same = p1.id === p2.id;
    portrait(ctx, a1, -200 + k * 236, 40, 192, false); portrait(ctx, same && a2.alt ? a2.alt : a2, VIEW_W + 8 - k * 236, 40, 192, true);
    drawText(ctx, 'VS', VIEW_W / 2, 100 + Math.sin(this.t / 6) * 3, { scale: 12, align: 'center', gradient: ['#ffffff', '#ffd23f'], outline: '#000' });
    drawText(ctx, p1.fullName, 132, 240, { scale: 1, align: 'center', color: '#fff' }); drawText(ctx, p2.fullName, VIEW_W - 132, 240, { scale: 1, align: 'center', color: '#fff' });
    drawText(ctx, p1.short, 132, 252, { scale: 3, align: 'center', color: '#ffe14d' }); drawText(ctx, p2.short, VIEW_W - 132, 252, { scale: 3, align: 'center', color: '#ffe14d' });
    const q = (d, x) => wrapText('"' + d.taunt + '"', 34).slice(0, 3).forEach((l, i) => drawText(ctx, l, x, 284 + i * 11, { align: 'center', color: '#ffffff' }));
    if (this.t > 30) { if (p1.taunt) q(p1, 160); if (p2.taunt) q(p2, VIEW_W - 160); }
    drawText(ctx, 'STAGE: ' + stage.name, VIEW_W / 2, 344, { align: 'center', color: '#ffd23f' }); }
}

// ---------------- Fight wrapper (pause) ----------------
export class FightScene {
  constructor(G, m) { this.G = G; this.m = m; this.paused = false; this.psel = 0; this.fight = G.makeFight(m, (res) => G.afterFight(m, res)); }
  update() { const G = this.G;
    if (this.paused) { for (const c of G.ctl) c.update();
      if (anyP(G, 'up') || anyP(G, 'down')) this.psel = (this.psel + (anyP(G, 'up') ? 2 : 1)) % 3;
      if (anyP(G, 'back')) this.paused = false;
      if (anyP(G, 'start') || anyP(G, 'punch')) { if (this.psel === 0) this.paused = false; else if (this.psel === 1) G.startFight(this.m); else G.go(new TitleScene(G)); }
      return; }
    const p = G.ctl[0].p; if ((G.ctl[0].h.back && !G.ctl[0].prev.back) || (G.ctl[1].h.back && !G.ctl[1].prev.back)) { this.paused = true; this.psel = 0; return; }
    this.fight.update(G.ctl, G.cpus); }
  draw(ctx) { this.fight.draw(ctx);
    if (this.paused) { ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0, 0, VIEW_W, VIEW_H); panel(ctx, 240, 120, 160, 100);
      drawText(ctx, 'PAUSE', 320, 130, { scale: 3, align: 'center', color: '#ffe14d' });
      ['RESUME', 'RESTART', 'QUIT'].forEach((s, i) => drawText(ctx, (i === this.psel ? '> ' : '  ') + s, 270, 164 + i * 14, { color: i === this.psel ? '#ffe14d' : '#fff' })); } }
}

// ---------------- Result / win quote ----------------
export class ResultScene {
  constructor(G, m, res, next) { Object.assign(this, { G, m, res, next, t: 0 }); if (G.content.music.victory) audio.play(G.content.music.victory, { loop: false }); else audio.stop(); }
  update() { const G = this.G; this.t++; for (const c of G.ctl) c.update(); if (this.t > 60 && (anyP(G, 'start') || anyP(G, 'punch') || this.t > 600)) this.next(); }
  draw(ctx) { const G = this.G, { p1, p2 } = this.m, w = this.res.winner;
    ctx.fillStyle = '#05081e'; ctx.fillRect(0, 0, VIEW_W, VIEW_H);
    if (w < 0) { drawText(ctx, 'DRAW GAME', VIEW_W / 2, 150, { scale: 7, align: 'center', gradient: ['#fff', '#ffb000'] }); return; }
    const W = w === 0 ? p1 : p2, L = w === 0 ? p2 : p1; const wa = G.arts[W.id], la = G.arts[L.id];
    const walt = w === 1 && p1.id === p2.id && wa.alt ? wa.alt : wa;
    portrait(ctx, walt, 30, 40, 192, false); portrait(ctx, la, VIEW_W - 30 - 96, 40, 96, true, true);
    drawText(ctx, 'WINNER', 126, 20, { scale: 2, align: 'center', color: '#ffe14d' });
    drawText(ctx, W.fullName, 126, 240, { align: 'center', color: '#fff' });
    panel(ctx, 240, 160, 370, 110); const quote = W.winQuote || 'Victory!';
    wrapText('"' + quote + '"', 28).slice(0, 6).forEach((l, i) => drawText(ctx, l, 256, 172 + i * 16, { scale: 2, color: '#ffffff' }));
    drawText(ctx, 'PRESS START', VIEW_W / 2, 330, { align: 'center', color: this.t % 40 < 26 ? '#fff' : '#666' }); }
}
export class ContinueScene {
  constructor(G) { this.G = G; this.t = 0; }
  update() { const G = this.G; this.t++; for (const c of G.ctl) c.update(); const n = 9 - Math.floor(this.t / 60);
    if (anyP(G, 'start') || anyP(G, 'punch')) { G.arcade.continues++; G.startArcadeMatch(); } else if (n < 0) G.go(new TitleScene(G)); }
  draw(ctx) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, VIEW_W, VIEW_H); const n = Math.max(0, 9 - Math.floor(this.t / 60));
    portrait(ctx, this.G.arts[this.G.arcade.p1.id], VIEW_W / 2 - 64, 40, 128, false, true);
    drawText(ctx, 'CONTINUE?', VIEW_W / 2, 190, { scale: 5, align: 'center', color: '#fff' });
    drawText(ctx, String(n), VIEW_W / 2, 240, { scale: 8, align: 'center', gradient: ['#ffe14d', '#ff3b30'] }); }
}
export class EndingScene {
  constructor(G, d) { this.G = G; this.d = d; this.t = 0; audio.play(G.content.music.victory || G.content.music.football); }
  update() { const G = this.G; this.t++; for (const c of G.ctl) c.update(); if (this.t > 90 && (anyP(G, 'start') || this.t > 1500)) G.go(new TitleScene(G)); }
  draw(ctx) { const G = this.G; drawStage(ctx, G.stageArts[G.content.stages[0].id], 160, this.t); ctx.fillStyle = 'rgba(0,0,0,0.65)'; ctx.fillRect(0, 0, VIEW_W, VIEW_H);
    drawText(ctx, 'CONGRATULATIONS!', VIEW_W / 2, 16, { scale: 4, align: 'center', gradient: ['#fff', '#d4a017'] });
    portrait(ctx, G.arts[this.d.id], 24, 70, 128, false);
    wrapText(this.d.ending || 'The band marches on. Thanks for playing!', 40).slice(0, 14).forEach((l, i) => drawText(ctx, l, 170, 72 + i * 16, { scale: 1, color: '#fff' }));
    drawText(ctx, 'THANKS FOR PLAYING JMHS MARCHING BAND ATTACK', VIEW_W / 2, 330, { align: 'center', color: '#ffe14d' }); }
}

// ---------------- How to play / options ----------------
export class HowToScene {
  constructor(G) { this.G = G; this.page = 0; }
  update() { const G = this.G; for (const c of G.ctl) c.update();
    if (anyP(G, 'right') || anyP(G, 'down')) this.page = (this.page + 1) % 2; if (anyP(G, 'left') || anyP(G, 'up')) this.page = (this.page + 1) % 2;
    if (anyP(G, 'back') || anyP(G, 'start')) G.go(new TitleScene(G)); }
  draw(ctx) { ctx.fillStyle = '#0c1734'; ctx.fillRect(0, 0, VIEW_W, VIEW_H); drawText(ctx, 'HOW TO PLAY', VIEW_W / 2, 12, { scale: 3, align: 'center', color: '#ffe14d' });
    const L = this.page === 0 ? [
      'MOVE / JUMP / CROUCH ...... P1: W A S D    P2: ARROWS', 'PUNCH ..................... P1: F        P2: NUM1 OR ,', 'KICK ...................... P1: G        P2: NUM2 OR .',
      'SPECIAL ................... P1: H        P2: NUM3 OR /', 'SUPER (METER FULL) ........ P1: R        P2: NUM0 OR \'', '1-PLAYER MODES ALSO TAKE ARROWS + J K L I',
      '', 'HOLD BACK TO BLOCK. CROUCH-BLOCK LOW HITS AND SWEEPS.', 'JUMP ATTACKS MUST BE BLOCKED STANDING.', 'DOWN + KICK = SWEEP (KNOCKDOWN). DOWN + PUNCH = LOW JAB.',
      'QUARTER-CIRCLE FORWARD + PUNCH ALSO FIRES YOUR SPECIAL.', 'SPECIAL + KICK TOGETHER ALSO FIRES YOUR SUPER.', 'FILL THE SUPER METER BY LANDING AND TAKING HITS.', 'GAMEPADS WORK TOO. ESC = PAUSE.',
      '', 'RIGHT: SPECIAL MOVE LIST'] : this.G.content.fighters.map(d => `${d.short.padEnd(12)} ${d.special.name} / ${d.super.name}`);
    L.forEach((l, i) => drawText(ctx, l, 30, 50 + i * 17, { color: '#fff' })); drawText(ctx, 'ESC: BACK', VIEW_W / 2, 346, { align: 'center', color: '#9db4ff' }); }
}
export class OptionsScene {
  constructor(G) { this.G = G; this.sel = 0; }
  rows() { const s = this.G.settings; return [
    ['CPU LEVEL', s.cpuDifficulty, v => { s.cpuDifficulty = (v % 5) + 1; }],
    ['ROUNDS TO WIN', s.roundsToWin, v => { s.roundsToWin = (v % 3) + 1; }],
    ['ROUND TIME', s.roundTime || 'INFINITE', () => { s.roundTime = s.roundTime === 99 ? 60 : s.roundTime === 60 ? 0 : 99; }],
    ['MUSIC', s.music ? 'ON' : 'OFF', () => { s.music = !s.music; audio.setOption('music', s.music); }],
    ['SOUND FX', s.sfx ? 'ON' : 'OFF', () => { s.sfx = !s.sfx; audio.setOption('sfx', s.sfx); }],
    ['ANNOUNCER VOICE', s.announcer ? 'ON' : 'OFF', () => { s.announcer = !s.announcer; audio.setOption('announcer', s.announcer); }],
    ['HITBOX VIEW', s.debug ? 'ON' : 'OFF', () => { s.debug = !s.debug; }], ['BACK', '', null]]; }
  update() { const G = this.G; for (const c of G.ctl) c.update(); const R = this.rows();
    if (anyP(G, 'up')) this.sel = (this.sel + R.length - 1) % R.length; if (anyP(G, 'down')) this.sel = (this.sel + 1) % R.length;
    if (anyP(G, 'start') || anyP(G, 'punch') || anyP(G, 'right') || anyP(G, 'left')) { const r = R[this.sel]; if (!r[2]) { G.saveSettings(); G.go(new TitleScene(G)); } else { r[2](r[1]); audio.sfx('select'); } }
    if (anyP(G, 'back')) { G.saveSettings(); G.go(new TitleScene(G)); } }
  draw(ctx) { ctx.fillStyle = '#0c1734'; ctx.fillRect(0, 0, VIEW_W, VIEW_H); drawText(ctx, 'OPTIONS', VIEW_W / 2, 20, { scale: 4, align: 'center', color: '#ffe14d' });
    this.rows().forEach(([k, v], i) => { const c = i === this.sel ? '#ffe14d' : '#fff'; drawText(ctx, (i === this.sel ? '> ' : '  ') + k, 150, 90 + i * 24, { scale: 2, color: c }); drawText(ctx, String(v), 490, 90 + i * 24, { scale: 2, color: c, align: 'right' }); }); }
}
