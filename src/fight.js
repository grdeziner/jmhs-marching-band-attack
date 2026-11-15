import { VIEW_W, VIEW_H, FLOOR_Y, WORLD_W, SUPER_MAX } from './config.js';
import { Fighter } from './fighter.js';
import { drawStage } from './stage.js';
import { drawProjectile } from './procart.js';
import { drawText, textWidth } from './font.js';
import { audio } from './audio.js';

const overlap = (a, b) => a.l < b.l + b.w && a.l + a.w > b.l && a.t < b.t + b.h && a.t + a.h > b.t;

export class Fight {
  // opts: { p1:def, p2:def, art1, art2, stage, stageArt, ctl:[c1,c2], cpu:[cpu|null,cpu|null], settings, onEnd(result) }
  constructor(opts) {
    this.o = opts; const same = opts.p1.id === opts.p2.id;
    this.f = [new Fighter(opts.p1, opts.art1, 0, false), new Fighter(opts.p2, opts.art2, 1, same)];
    this.round = 1; this.frame = 0; this.seed = opts.seed || 12345; this.settings = { roundsToWin: 2, roundTime: 99, ...opts.settings };
    this.log = []; this.startRound();
  }
  rand() { this.seed = (this.seed * 1664525 + 1013904223) >>> 0; return this.seed / 4294967296; }
  opponent(f) { return f === this.f[0] ? this.f[1] : this.f[0]; }
  sfx(n) { audio.sfx(n); }
  shake(n) { this.shakeT = Math.max(this.shakeT || 0, n); }
  startRound() {
    const [a, b] = this.f; a.reset(WORLD_W / 2 - 110, 1); b.reset(WORLD_W / 2 + 110, -1);
    this.projectiles = []; this.effects = []; this.phase = 'intro'; this.phaseT = 0; this.timer = this.settings.roundTime; this.timerT = 0;
    this.hitstop = 0; this.freeze = null; this.shakeT = 0; this.cam = (WORLD_W - VIEW_W) / 2; this.banner = null; this.result = null;
    audio.announce(this.isFinal() ? 'Final round' : 'Round ' + this.round);
  }
  isFinal() { return this.f[0].wins === this.settings.roundsToWin - 1 && this.f[1].wins === this.settings.roundsToWin - 1; }
  superFreeze(f, mv) { this.freeze = { f, t: 40, name: mv.name }; audio.sfx('superflash'); }
  spawnProjectile(owner, p) {
    const art = owner.art.projectile; if (art && p.usePng) { p.w = Math.round(art.w * 0.7); p.h = Math.round(art.h * 0.75); }
    this.projectiles.push({ owner, dir: Math.sign(p.vx) || owner.facing, vy: 0, life: 260, hits: 1, interval: 8, hitCount: 0, lastHit: -99, age: 0, ...p });
  }
  hitDirect(att, def, props) { return this.resolveHit(att, def, props, def.x, FLOOR_Y - 60); }
  resolveHit(att, def, props, hx, hy) {
    if (def.invuln > 0 || def.state === 'ko' || (def.state === 'down' && def.y <= 0)) return null;
    const holdingBack = def.wantBlock && def.grounded && (def.state === 'block' || ['idle', 'walk', 'crouch'].includes(def.state));
    const crouch = def.crouching || def.state === 'crouch';
    const block = holdingBack && !props.unblockable && !(props.low && !crouch) && !(props.overhead && crouch);
    const wasStun = def.state === 'hit' || def.state === 'down';
    const dmg = def.takeHit(this, att, props, block);
    if (block) { audio.sfx('block'); this.effects.push({ kind: 'block', x: hx, y: hy, t: 10 }); this.hitstop = 4; return 'block'; }
    att.combo = wasStun ? att.combo + 1 : 1; if (att.combo >= 2) this.banner = { side: att.side, text: att.combo + ' HIT COMBO!', t: 80 };
    audio.sfx(props.sound || 'hit'); this.effects.push({ kind: 'spark', x: hx, y: hy, t: 12, big: dmg > 60 });
    this.hitstop = dmg > 60 ? 8 : 5; if (dmg > 80) this.shake(6);
    this.log.push({ f: this.frame, att: att.side, dmg, hp: def.hp });
    return 'hit';
  }
  update(ctls, cpus) {
    this.frame++; this.phaseT++;
    const [a, b] = this.f;
    const inputs = [0, 1].map(i => { const c = ctls[i]; if (cpus[i]) { c.virtual = cpus[i].think(this.f[i], this); } return c; });
    for (const c of inputs) c.update();
    if (this.shakeT > 0) this.shakeT--;
    if (this.freeze) { if (--this.freeze.t <= 0) this.freeze = null; return; }
    if (this.hitstop > 0) { this.hitstop--; return; }
    // phase flow
    if (this.phase === 'intro') { if (this.phaseT === 70) audio.announce('Fight!'); if (this.phaseT >= 110) { this.phase = 'fight'; this.phaseT = 0; } }
    if (this.phase === 'fight' && this.settings.roundTime > 0 && ++this.timerT >= 60) { this.timerT = 0; if (--this.timer <= 0) this.endRound('time'); }
    const slow = this.phase === 'ko' && this.phaseT < 50 && this.phaseT % 3 !== 0;
    if (!slow) {
      a.update(this, inputs[0]); b.update(this, inputs[1]);
      this.physics(); this.combat(); this.updateProjectiles();
    }
    for (const e of this.effects) e.t--; this.effects = this.effects.filter(e => e.t > 0);
    for (const f of this.f) if (f.callout && --f.callout.t <= 0) f.callout = null;
    if (this.banner && --this.banner.t <= 0) this.banner = null;
    if (this.phase === 'fight') {
      if (a.hp <= 0 || b.hp <= 0) this.endRound('ko');
    } else if (this.phase === 'ko' || this.phase === 'timeup') {
      if (this.phaseT === 110) { const w = this.result.winner; if (w) { w.setState('win'); } }
      if (this.phaseT > 250) this.nextRound();
    }
  }
  endRound(why) {
    const [a, b] = this.f; let winner = null;
    if (a.hp !== b.hp) winner = a.hp > b.hp ? a : b;
    this.result = { why, winner, perfect: winner && winner.hp === winner.maxHp, double: why === 'ko' && a.hp <= 0 && b.hp <= 0 };
    if (winner) winner.wins++; else { a.wins++; b.wins++; }
    this.phase = why === 'ko' ? 'ko' : 'timeup'; this.phaseT = 0;
    audio.sfx('ko'); audio.announce(why === 'ko' ? 'K.O.' : 'Time');
    this.roundLog = (this.roundLog || []).concat([{ round: this.round, why, winner: winner ? winner.side : -1, hp: [a.hp, b.hp] }]);
  }
  nextRound() {
    const [a, b] = this.f, R = this.settings.roundsToWin;
    if (a.wins >= R || b.wins >= R || this.round >= R * 2 + 1) {
      const winner = a.wins === b.wins ? null : a.wins > b.wins ? a : b;
      this.phase = 'over'; this.o.onEnd && this.o.onEnd({ winner: winner ? winner.side : -1, rounds: this.roundLog }); return;
    }
    this.round++; this.startRound();
  }
  physics() {
    const [a, b] = this.f;
    // push boxes
    const dx = b.x - a.x, min = 44;
    if (Math.abs(dx) < min && Math.abs(a.y - b.y) < 70) { const push = (min - Math.abs(dx)) / 2, s = Math.sign(dx) || 1; a.x -= push * s; b.x += push * s; }
    // camera follows midpoint
    const mid = (a.x + b.x) / 2; this.cam = Math.max(0, Math.min(WORLD_W - VIEW_W, mid - VIEW_W / 2));
    for (const f of this.f) f.x = Math.max(this.cam + 22, Math.min(this.cam + VIEW_W - 22, Math.max(22, Math.min(WORLD_W - 22, f.x))));
  }
  combat() {
    for (const att of this.f) {
      const ah = att.activeHit; if (!ah) continue; const def = this.opponent(att);
      const hits = ah.hits || 1; if (att.hitCount >= hits) continue;
      const t = att.state === 'move' ? att.mvT : att.actT; if (hits > 1 && t - att.lastHitT < (ah.interval || 6)) continue;
      const box = att.toWorld(ah.box), hb = def.hurtbox();
      if (overlap(box, hb)) {
        const isLast = att.hitCount === hits - 1; const props = isLast && ah.last ? { ...ah.props, ...ah.last } : ah.props;
        const hx = att.facing > 0 ? Math.max(box.l, hb.l) : Math.min(box.l + box.w, hb.l + hb.w);
        const r = this.resolveHit(att, def, props, hx, Math.max(box.t, hb.t) + Math.min(box.h, hb.h) / 2);
        att.hitCount++; att.lastHitT = t; if (r === null) att.hitCount = hits;
      }
    }
  }
  updateProjectiles() {
    for (const p of this.projectiles) {
      if (p.dead) continue; p.age++; p.x += p.vx; p.y += p.vy;
      if (p.returnAt && p.age === p.returnAt) p.vx = -p.vx;
      if (p.returnAt && p.age > p.returnAt && Math.abs(p.x - p.owner.x) < 30) p.dead = true;
      if (p.falls && p.y <= 8) { p.dead = true; this.effects.push({ kind: 'block', x: p.x, y: FLOOR_Y - 8, t: 8 }); }
      if (--p.life <= 0 || p.x < this.cam - 120 || p.x > this.cam + VIEW_W + 120) p.dead = true;
    }
    // clashes
    for (const p of this.projectiles) for (const q of this.projectiles) {
      if (p.dead || q.dead || p.owner === q.owner || p.falls || q.falls) continue;
      if (Math.abs(p.x - q.x) < (p.w + q.w) / 2 && Math.abs(p.y - q.y) < (p.h + q.h) / 2) {
        this.effects.push({ kind: 'spark', x: (p.x + q.x) / 2 - 0, y: FLOOR_Y - p.y, t: 12, big: true }); audio.sfx('block');
        const ps = p.hits - p.hitCount, qs = q.hits - q.hitCount; if (ps <= qs) p.dead = true; if (qs <= ps) q.dead = true; if (ps > qs) p.hitCount += qs; if (qs > ps) q.hitCount += ps;
      } }
    for (const p of this.projectiles) {
      if (p.dead) continue; const def = this.opponent(p.owner);
      if (p.age - p.lastHit < p.interval && p.hitCount > 0) continue;
      const box = { l: p.x - p.w / 2, t: FLOOR_Y - p.y - p.h / 2, w: p.w, h: p.h };
      if (overlap(box, def.hurtbox())) {
        const isLast = p.hitCount === p.hits - 1; const props = isLast && p.last ? { ...p.props, ...p.last } : p.props;
        const r = this.resolveHit(p.owner, def, props, p.x, FLOOR_Y - p.y);
        if (r === null) continue; p.hitCount++; p.lastHit = p.age; if (p.hitCount >= p.hits) p.dead = true;
      }
    }
    this.projectiles = this.projectiles.filter(p => !p.dead);
  }
  // ---------------- drawing ----------------
  draw(ctx) {
    const sh = this.shakeT > 0 ? ((this.frame % 2) * 2 - 1) * Math.min(4, this.shakeT) : 0;
    ctx.save(); ctx.translate(sh, 0);
    drawStage(ctx, this.o.stageArt, this.cam, this.frame);
    if (this.freeze) { ctx.fillStyle = 'rgba(10,0,30,0.6)'; ctx.fillRect(-10, 0, VIEW_W + 20, VIEW_H); }
    // draw the attacker on top
    const order = this.f[0].state === 'move' || this.f[0].state === 'attack' ? [this.f[1], this.f[0]] : [this.f[0], this.f[1]];
    for (const f of order) f.draw(ctx, this.cam, this);
    for (const p of this.projectiles) this.drawProj(ctx, p);
    for (const e of this.effects) this.drawEffect(ctx, e);
    if (this.o.debug) this.drawBoxes(ctx);
    ctx.restore();
    this.drawHUD(ctx);
  }
  drawProj(ctx, p) {
    const art = p.owner.art.projectile; const x = p.x - this.cam, y = FLOOR_Y - p.y;
    if (art && p.usePng) { const i = art.loop ? Math.floor(p.age * art.fps / 60) % art.n : Math.min(art.n - 1, Math.floor(p.age * art.fps / 60));
      ctx.save(); ctx.translate(Math.round(x), Math.round(y)); ctx.scale(p.dir, 1);
      ctx.drawImage(art.img, i * art.w, 0, art.w, art.h, -art.w / 2, -art.ay, art.w, art.h); ctx.restore(); return; }
    drawProjectile(ctx, { ...p, x, y }, p.age);
  }
  drawEffect(ctx, e) {
    const x = e.x - this.cam, y = e.y;
    if (e.kind === 'spark') { const r = (e.big ? 26 : 16) * (1 - e.t / 14) + 4; ctx.fillStyle = e.t % 4 < 2 ? '#fff6c8' : '#ffb000';
      for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4; ctx.fillRect(Math.round(x + Math.cos(a) * r) - 3, Math.round(y + Math.sin(a) * r) - 3, 6, 6); }
      ctx.fillStyle = '#ffffff'; ctx.fillRect(x - 5, y - 5, 10, 10); }
    else if (e.kind === 'block') { ctx.strokeStyle = '#7ef9ff'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x, y, 18 - e.t, 0, Math.PI * 2); ctx.stroke(); }
  }
  drawBoxes(ctx) {
    ctx.lineWidth = 1;
    for (const f of this.f) { const h = f.hurtbox(); ctx.strokeStyle = '#00ff66'; ctx.strokeRect(h.l - this.cam + 0.5, h.t + 0.5, h.w, h.h);
      if (f.activeHit) { const b = f.toWorld(f.activeHit.box); ctx.strokeStyle = '#ff2040'; ctx.strokeRect(b.l - this.cam + 0.5, b.t + 0.5, b.w, b.h); } }
    for (const p of this.projectiles) { ctx.strokeStyle = '#ffcc00'; ctx.strokeRect(p.x - p.w / 2 - this.cam, FLOOR_Y - p.y - p.h / 2, p.w, p.h); }
  }
  drawHUD(ctx) {
    const [a, b] = this.f, BW = 252, BH = 12, Y = 16;
    const bar = (f, x, flip) => {
      ctx.fillStyle = '#000'; ctx.fillRect(x - 2, Y - 2, BW + 4, BH + 4);
      ctx.fillStyle = '#d01818'; ctx.fillRect(x, Y, BW, BH);
      const w = Math.round(BW * f.hp / f.maxHp), dw = Math.round(BW * f.dispHp / f.maxHp);
      ctx.fillStyle = '#ffffff'; ctx.fillRect(flip ? x : x + BW - dw, Y, dw, BH);
      const low = f.hp / f.maxHp < 0.25 && this.frame % 20 < 10;
      ctx.fillStyle = low ? '#ff8c00' : '#ffd800'; ctx.fillRect(flip ? x : x + BW - w, Y, w, BH);
      ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.fillRect(flip ? x : x + BW - w, Y + 1, w, 2);
      ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(flip ? x : x + BW - w, Y + BH - 3, w, 3);
    };
    bar(a, 24, false); bar(b, VIEW_W - 24 - BW, true);
    // KO emblem
    ctx.fillStyle = '#000'; ctx.fillRect(VIEW_W / 2 - 20, Y - 5, 40, 20); ctx.fillStyle = '#c8202c'; ctx.fillRect(VIEW_W / 2 - 18, Y - 3, 36, 16);
    drawText(ctx, 'KO', VIEW_W / 2, Y - 0.5, { scale: 2, align: 'center', color: '#fff', outline: '#5a0d12' });
    // timer
    const tt = this.settings.roundTime > 0 ? String(Math.max(0, this.timer)).padStart(2, '0') : '--';
    drawText(ctx, tt, VIEW_W / 2, Y + 20, { scale: 4, align: 'center', gradient: ['#ffffff', '#ffb000'], outline: '#000' });
    // names + round medals
    drawText(ctx, a.def.fullName, 24, Y + 18, { color: '#fff', outline: '#000' });
    drawText(ctx, b.def.fullName, VIEW_W - 24, Y + 18, { color: '#fff', outline: '#000', align: 'right' });
    for (let i = 0; i < this.settings.roundsToWin; i++) { this.medal(ctx, 24 + i * 16, Y + 30, i < a.wins); this.medal(ctx, VIEW_W - 36 - i * 16, Y + 30, i < b.wins); }
    // super meters
    const meter = (f, x, flip) => { const W = 150, full = f.meter >= SUPER_MAX;
      ctx.fillStyle = '#000'; ctx.fillRect(x - 2, 336, W + 4, 10); ctx.fillStyle = '#1b1b3a'; ctx.fillRect(x, 338, W, 6);
      const w = Math.round(W * f.meter / SUPER_MAX); ctx.fillStyle = full ? (this.frame % 10 < 5 ? '#7ef9ff' : '#ffffff') : '#3a86ff'; ctx.fillRect(flip ? x + W - w : x, 338, w, 6);
      drawText(ctx, full ? 'SUPER READY!' : 'SUPER', flip ? x + W : x, 326, { color: full ? '#7ef9ff' : '#9db4ff', align: flip ? 'right' : 'left' }); };
    meter(a, 24, false); meter(b, VIEW_W - 24 - 150, true);
    // callouts (special names) + combo banner
    for (const f of this.f) if (f.callout && !f.callout.big) { const x = f.side ? VIEW_W - 24 : 24;
      drawText(ctx, f.callout.text, x, 76, { scale: 2, color: '#ffe066', align: f.side ? 'right' : 'left' }); }
    if (this.banner) { const x = this.banner.side ? VIEW_W - 24 : 24; drawText(ctx, this.banner.text, x, 96, { scale: 2, gradient: ['#ffffff', '#ff7b00'], align: this.banner.side ? 'right' : 'left' }); }
    if (this.freeze) { const s = 4; ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0, 140, VIEW_W, 52);
      drawText(ctx, this.freeze.name, VIEW_W / 2, 150, { scale: s, align: 'center', gradient: ['#fff6c8', '#ff3b30'] }); }
    // big round callouts
    const big = (s, scale, grad) => drawText(ctx, s, VIEW_W / 2, 140 - scale * 3.5, { scale, align: 'center', gradient: grad, outline: '#000' });
    if (this.phase === 'intro') {
      if (this.phaseT < 70) big(this.isFinal() ? 'FINAL ROUND' : 'ROUND ' + this.round, 7, ['#ffffff', '#ffd23f']);
      else big('FIGHT!', 10, ['#ffe14d', '#ff3b30']);
    } else if (this.phase === 'ko' || this.phase === 'timeup') {
      const r = this.result;
      if (this.phaseT < 110) { if (r.why === 'ko') big(r.double ? 'DOUBLE K.O.' : 'K.O.', r.double ? 8 : 14, ['#ffffff', '#ff3b30']); else big('TIME OVER', 9, ['#ffffff', '#ffb000']); }
      else { const t = r.winner ? (r.winner.def.short + ' WINS') : 'DRAW GAME'; big(t, 6, ['#ffffff', '#3a86ff']);
        if (r.perfect) drawText(ctx, 'PERFECT!', VIEW_W / 2, 170, { scale: 5, align: 'center', gradient: ['#fff6c8', '#ff9f1c'] }); }
    }
  }
  medal(ctx, x, y, on) { ctx.fillStyle = '#000'; ctx.fillRect(x - 1, y - 1, 12, 12); ctx.fillStyle = on ? '#ffd23f' : '#333'; ctx.fillRect(x, y, 10, 10);
    if (on) { ctx.fillStyle = '#c8202c'; ctx.fillRect(x + 3, y + 3, 4, 4); } }
  snapshot() { return { phase: this.phase, round: this.round, timer: this.timer, frame: this.frame, projectiles: this.projectiles.length,
    fighters: this.f.map(f => ({ id: f.def.id, hp: f.hp, maxHp: f.maxHp, wins: f.wins, state: f.state, x: Math.round(f.x), y: Math.round(f.y), meter: Math.round(f.meter), facing: f.facing })) }; }
}
