import { VIEW_W, VIEW_H, FLOOR_Y, WORLD_W, SUPER_MAX } from './config.js';
import { Fighter } from './fighter.js';
import { drawStageBack, drawStageFront } from './stage.js';
import { FX, drawSuperBG } from './fx.js';
import { drawHUD } from './hud.js';
import { drawProjectile } from './procart.js';
import { drawText, textWidth } from './font.js';
import { audio } from './audio.js';

let fxSeed = 99; const fxRand = () => (fxSeed = (fxSeed * 1103515245 + 12345) >>> 0) / 4294967296;
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
  get effects() { return this.fx ? this.fx.list : []; }
  dust(x, n, dir, big) { this.fx.dust(x, n, dir, big); }
  shake(n) { this.shakeT = Math.max(this.shakeT || 0, n); }
  startRound() {
    const [a, b] = this.f; a.reset(WORLD_W / 2 - 110, 1); b.reset(WORLD_W / 2 + 110, -1);
    this.projectiles = []; this.fx = new FX(fxRand); this.phase = 'intro'; this.phaseT = 0; this.timer = this.settings.roundTime; this.timerT = 0;
    this.hitstop = 0; this.freeze = null; this.shakeT = 0; this.cam = (WORLD_W - VIEW_W) / 2; this.banner = null; this.result = null;
    audio.announce(this.isFinal() ? 'Final round' : 'Round ' + this.round);
  }
  isFinal() { return this.f[0].wins === this.settings.roundsToWin - 1 && this.f[1].wins === this.settings.roundsToWin - 1; }
  superFreeze(f, mv) { this.freeze = { f, t: 40, name: mv.name }; audio.sfx('superflash'); }
  spawnProjectile(owner, p) {
    if (p.usePng && !this.projArt({ ...p, owner })) p.usePng = false;
    this.projectiles.push({ owner, dir: Math.sign(p.vx) || owner.facing, vy: 0, life: 260, hits: 1, interval: 8, hitCount: 0, lastHit: -99, age: 0, ...p });
  }
  projArt(p) { return p.usePng === 'super' ? p.owner.art.super : p.usePng ? p.owner.art.projectile : null; }
  projFrame(p) { const a = this.projArt(p); return a.loop ? Math.floor(p.age * a.fps / 60) % a.n : Math.min(a.n - 1, Math.floor(p.age * a.fps / 60)); }
  // collision box in world/screen space. PNG projectiles: opaque bbox of the current frame around the sheet.json anchor.
  projBox(p) {
    const sy = FLOOR_Y - p.y;
    if (p.usePng) { const a = this.projArt(p), i = this.projFrame(p), bb = (a.boxes && a.boxes[i]) || { x: 0, y: 0, w: a.w, h: a.h };
      const rx = bb.x - a.ax, pad = Math.min(6, bb.w / 4); const w = Math.max(8, bb.w - pad * 2);
      return { l: p.dir > 0 ? p.x + rx + pad : p.x - rx - bb.w + pad, t: sy + bb.y - a.ay, w, h: Math.max(8, bb.h) }; }
    return { l: p.x - p.w / 2, t: sy - p.h / 2, w: p.w, h: p.h };
  }
  hitDirect(att, def, props) { return this.resolveHit(att, def, props, def.x, FLOOR_Y - 60); }
  resolveHit(att, def, props, hx, hy) {
    if (def.invuln > 0 || def.state === 'ko' || (def.state === 'down' && def.y <= 0)) return null;
    const holdingBack = def.wantBlock && def.grounded && (def.state === 'block' || ['idle', 'walk', 'crouch'].includes(def.state));
    const crouch = def.crouching || def.state === 'crouch';
    const block = holdingBack && !props.unblockable && !(props.low && !crouch) && !(props.overhead && crouch);
    const wasStun = def.state === 'hit' || def.state === 'down';
    const dmg = def.takeHit(this, att, props, block);
    if (block) { audio.sfx('block'); this.fx.spark(hx, hy, { block: true, dir: att.facing }); this.hitstop = 4; return 'block'; }
    att.combo = wasStun ? att.combo + 1 : 1; if (att.combo >= 2) this.banner = { side: att.side, text: att.combo + ' HIT COMBO!', t: 80 };
    audio.sfx(props.sound || 'hit'); this.fx.spark(hx, hy, { big: dmg > 60, dir: att.facing }); if (props.knockdown) this.fx.ring(hx, hy, '#ffffff', 46);
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
    this.fx.update();
    for (const f of this.f) { if (f.hp < (f.lastHp ?? f.hp)) f.trailDelay = 34; f.lastHp = f.hp;
      if (f.dispHp < f.hp) f.dispHp = f.hp; else if (f.trailDelay > 0) f.trailDelay--; else if (f.dispHp > f.hp) f.dispHp = Math.max(f.hp, f.dispHp - Math.max(1.5, (f.dispHp - f.hp) * 0.08)); }
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
      if (p.falls && p.y <= 8) { p.dead = true; this.fx.dust(p.x, 3); this.fx.spark(p.x, FLOOR_Y - 8, { block: true }); }
      if (--p.life <= 0 || p.x < this.cam - 120 || p.x > this.cam + VIEW_W + 120) p.dead = true;
    }
    // clashes
    for (const p of this.projectiles) for (const q of this.projectiles) {
      if (p.dead || q.dead || p.owner === q.owner || p.falls || q.falls) continue;
      if (overlap(this.projBox(p), this.projBox(q))) {
        this.fx.spark((p.x + q.x) / 2, FLOOR_Y - p.y, { big: true }); audio.sfx('block');
        const ps = p.hits - p.hitCount, qs = q.hits - q.hitCount; if (ps <= qs) p.dead = true; if (qs <= ps) q.dead = true; if (ps > qs) p.hitCount += qs; if (qs > ps) q.hitCount += ps;
      } }
    for (const p of this.projectiles) {
      if (p.dead) continue; const def = this.opponent(p.owner);
      if (p.age - p.lastHit < p.interval && p.hitCount > 0) continue;
      if (p.harmless) continue; const box = this.projBox(p);
      if (overlap(box, def.hurtbox())) {
        const isLast = p.hitCount === p.hits - 1; const props = isLast && p.last ? { ...p.props, ...p.last } : p.props;
        const r = this.resolveHit(p.owner, def, props, p.dir > 0 ? box.l + box.w : box.l, box.t + box.h / 2);
        if (r === null) continue; p.hitCount++; p.lastHit = p.age; if (p.hitCount >= p.hits) p.dead = true;
      }
    }
    this.projectiles = this.projectiles.filter(p => !p.dead);
  }
  // ---------------- drawing ----------------
  draw(ctx) {
    const st = this.shakeT, sh = st > 0 ? ((this.frame % 2) * 2 - 1) * Math.min(5, st) : 0, sv = st > 4 ? ((this.frame >> 1) % 2 * 2 - 1) * Math.min(3, st >> 2) : 0;
    ctx.save(); ctx.translate(sh, sv);
    drawStageBack(ctx, this.o.stageArt, this.cam, this.frame);
    if (this.freeze) drawSuperBG(ctx, this.freeze, this.cam, this.frame);
    // the attacker draws on top; a fighter carried overhead draws above everyone
    const pri = f => f.state === 'held' ? 2 : f.state === 'move' || f.state === 'attack' ? 1 : 0;
    const order = [...this.f].sort((x, y) => pri(x) - pri(y));
    for (const f of order) f.draw(ctx, this.cam, this);
    for (const p of this.projectiles) this.drawProj(ctx, p);
    this.fx.draw(ctx, this.cam);
    if (!this.freeze) drawStageFront(ctx, this.o.stageArt, this.cam, this.frame);
    if (this.o.debug) this.drawBoxes(ctx);
    ctx.restore();
    this.drawHUD(ctx);
  }
  drawProj(ctx, p) {
    const art = this.projArt(p); const x = p.x - this.cam, y = FLOOR_Y - p.y;
    if (art && p.usePng) { const i = this.projFrame(p);
      ctx.save(); ctx.translate(Math.round(x), Math.round(y)); ctx.scale(p.dir, 1);
      ctx.drawImage(art.img, i * art.w, 0, art.w, art.h, -art.ax, -art.ay, art.w, art.h); ctx.restore(); return; }
    drawProjectile(ctx, { ...p, x, y }, p.age);
  }
  drawBoxes(ctx) {
    ctx.lineWidth = 1;
    for (const f of this.f) { const h = f.hurtbox(); ctx.strokeStyle = '#00ff66'; ctx.strokeRect(h.l - this.cam + 0.5, h.t + 0.5, h.w, h.h);
      if (f.activeHit) { const b = f.toWorld(f.activeHit.box); ctx.strokeStyle = '#ff2040'; ctx.strokeRect(b.l - this.cam + 0.5, b.t + 0.5, b.w, b.h); } }
    for (const p of this.projectiles) { const b = this.projBox(p); ctx.strokeStyle = '#ffcc00'; ctx.strokeRect(b.l - this.cam + 0.5, b.t + 0.5, b.w, b.h); }
  }
  drawHUD(ctx) {
    drawHUD(ctx, this);
    // callouts (special names) + combo banner
    for (const f of this.f) if (f.callout && !f.callout.big) { const x = f.side ? VIEW_W - 24 : 24;
      drawText(ctx, f.callout.text, x, 82, { scale: 2, color: '#ffe066', align: f.side ? 'right' : 'left' }); }
    if (this.banner) { const x = this.banner.side ? VIEW_W - 24 : 24; drawText(ctx, this.banner.text, x, 102, { scale: 2, gradient: ['#ffffff', '#ff7b00'], align: this.banner.side ? 'right' : 'left' }); }
    if (this.freeze) { const s = 4; const g = ctx.createLinearGradient(0, 138, 0, 194); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.5, 'rgba(0,0,0,0.75)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 138, VIEW_W, 56);
      drawText(ctx, this.freeze.name, VIEW_W / 2, 150, { scale: s, align: 'center', gradient: ['#ffffff', '#ffe14d', '#ff3b30'] }); }
    // big round callouts
    const big = (s, scale, grad) => drawText(ctx, s, VIEW_W / 2, 140 - scale * 3.5, { scale, align: 'center', gradient: grad, outline: '#10081c', italic: true });
    if (this.phase === 'intro') {
      if (this.phaseT < 70) big(this.isFinal() ? 'FINAL ROUND' : 'ROUND ' + this.round, 7, ['#ffffff', '#ffe14d', '#ff9a1f']);
      else big('FIGHT!', 10, ['#ffffff', '#ffe14d', '#ff3b30', '#8a0610']);
    } else if (this.phase === 'ko' || this.phase === 'timeup') {
      const r = this.result;
      if (this.phaseT < 110) { if (r.why === 'ko') big(r.double ? 'DOUBLE K.O.' : 'K.O.', r.double ? 8 : 14, ['#ffffff', '#ff9a8a', '#ff1f1f', '#6a0408']); else big('TIME OVER', 9, ['#ffffff', '#ffb000']); }
      else { const t = r.winner ? (r.winner.def.short + ' WINS') : 'DRAW GAME'; big(t, 6, ['#ffffff', '#3a86ff']);
        if (r.perfect) drawText(ctx, 'PERFECT!', VIEW_W / 2, 170, { scale: 5, align: 'center', gradient: ['#fff6c8', '#ff9f1c'] }); }
    }
  }
  snapshot() { return { phase: this.phase, round: this.round, timer: this.timer, frame: this.frame, projectiles: this.projectiles.length,
    fighters: this.f.map(f => ({ id: f.def.id, hp: f.hp, maxHp: f.maxHp, wins: f.wins, state: f.state, x: Math.round(f.x), y: Math.round(f.y), meter: Math.round(f.meter), facing: f.facing })) }; }
}
