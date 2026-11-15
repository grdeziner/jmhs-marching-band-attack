import { FLOOR_Y, SUPER_MAX } from './config.js';
import { makeMove } from './moves.js';
import { flashOf } from './assets.js';

const GRAV = 0.62;
// Normal attacks. Boxes are anchor-relative (feet = 0,0), facing right, y up is negative.
const NORMALS = {
  punch:  { anim: 'punch', startup: 4, active: 4, recovery: 9,  dmg: 45, stun: 15, bstun: 10, push: 3, box: { x: 14, y: -80, w: 46, h: 22 }, af: [1] },
  kick:   { anim: 'kick',  startup: 7, active: 5, recovery: 14, dmg: 65, stun: 18, bstun: 12, push: 4, box: { x: 16, y: -64, w: 54, h: 22 }, af: [2], sound: 'heavy' },
  cpunch: { anim: 'punch', crouch: 1, startup: 4, active: 4, recovery: 9, dmg: 35, stun: 13, bstun: 9, push: 3, low: 1, box: { x: 12, y: -54, w: 46, h: 20 }, af: [1] },
  sweep:  { anim: 'kick',  crouch: 1, startup: 8, active: 5, recovery: 20, dmg: 60, stun: 18, bstun: 12, push: 3, low: 1, knockdown: 1, box: { x: 14, y: -26, w: 62, h: 24 }, af: [2], sound: 'heavy' },
  jpunch: { anim: 'punch', air: 1, startup: 3, active: 9, recovery: 4, dmg: 50, stun: 16, bstun: 10, push: 2, overhead: 1, box: { x: 8, y: -74, w: 46, h: 32 }, af: [1] },
  jkick:  { anim: 'kick',  air: 1, startup: 5, active: 10, recovery: 4, dmg: 70, stun: 18, bstun: 12, push: 3, overhead: 1, box: { x: 8, y: -52, w: 54, h: 32 }, af: [2], sound: 'heavy' },
};
const CROUCH_SQUASH = 0.72;
const NEUTRAL = { idle: 1, walk: 1, crouch: 1 };

export class Fighter {
  constructor(def, art, side, alt) {
    this.def = def; this.art = alt && art.alt ? { ...art, anims: art.alt.anims, portrait: art.alt.portrait } : art;
    this.side = side; this.alt = alt;
    const s = def.stats || {}; this.maxHp = s.health || 1000; this.walkSpd = s.walk || 2.6; this.jumpV = s.jump || 11.5; this.power = s.power || 1;
    this.special = makeMove(def.special, false); this.superMove = makeMove(def.super, true);
    this.meter = 0; this.wins = 0; this.reset(side ? 620 : 340, side ? -1 : 1);
  }
  reset(x, facing) {
    Object.assign(this, { x, y: 0, vx: 0, vy: 0, facing, hp: this.maxHp, dispHp: this.maxHp, state: 'intro', t: 0, act: null, activeHit: null,
      hitCount: 0, lastHitT: -99, airAttacked: false, stun: 0, invuln: 0, flash: 0, combo: 0, hist: [], crouching: false, blocking: false,
      spin: false, callout: null, perfect: true, landLag: 0 });
  }
  get grounded() { return this.y <= 0 && this.vy <= 0; }
  throwable() { return !this.invuln && !['down', 'ko', 'getup', 'jump'].includes(this.state) && this.y === 0; }
  meta(anim) { return (this.art.meta && this.art.meta[anim]) || {}; }
  hurtbox() {
    const anim = this.state === 'crouch' || (this.state === 'block' && this.crouching) ? 'crouch' : this.anim();
    const m = this.meta(anim).hurtbox;
    let b = m ? { ...m } : anim === 'crouch' ? { x: -24, y: -70, w: 48, h: 70 } : ['ko'].includes(anim) ? { x: -40, y: -40, w: 80, h: 40 } : { x: -24, y: -100, w: 48, h: 100 };
    if (this.act && this.act.crouch) { b.y = Math.round(b.y * CROUCH_SQUASH); b.h = Math.round(b.h * CROUCH_SQUASH); }
    return this.toWorld(b);
  }
  toWorld(b) { const ax = this.x, ay = FLOOR_Y - this.y;
    return { l: this.facing > 0 ? ax + b.x : ax - b.x - b.w, t: ay + b.y, w: b.w, h: b.h }; }
  anim() {
    switch (this.state) {
      case 'walk': return 'walk'; case 'crouch': return 'crouch'; case 'jump': return 'jump'; case 'block': return this.crouching ? 'crouch' : 'block';
      case 'attack': return this.act.anim; case 'move': return 'special'; case 'hit': return 'hit';
      case 'down': case 'ko': case 'getup': return 'ko'; case 'win': return 'special'; default: return 'idle';
    }
  }
  // ---------- per-frame ----------
  update(F, c) {
    const o = F.opponent(this); this.t++;
    if (this.invuln > 0) this.invuln--; if (this.flash > 0) this.flash--;
    const back = this.facing > 0 ? c.h.left : c.h.right, fwd = this.facing > 0 ? c.h.right : c.h.left;
    // motion history for quarter-circle-forward specials (2 3 6)
    const dir = c.h.down ? (fwd ? 3 : back ? 1 : 2) : fwd ? 6 : back ? 4 : 5; if (this.hist[this.hist.length - 1] !== dir) this.hist.push(dir); if (this.hist.length > 8) this.hist.shift();
    if (dir !== 5) this.histT = F.frame;
    const qcf = this.hist.slice(-3).join('') === '236' && F.frame - (this.histT || 0) < 12;
    this.blocking = false;
    const canAct = F.phase === 'fight';
    if (NEUTRAL[this.state] || (this.state === 'intro' && canAct) || (this.state === 'block' && this.stun <= 0)) {
      if (this.grounded) this.facing = o.x >= this.x ? 1 : -1;
      if (this.landLag > 0) { this.landLag--; this.setState('idle'); }
      else if (!canAct) this.setState('idle');
      else if ((c.p.super || (c.p.special && c.h.kick)) && this.meter >= SUPER_MAX) this.startMove(F, this.superMove);
      else if ((c.p.special || (qcf && c.p.punch)) && (!this.special.canStart || this.special.canStart(this, F))) this.startMove(F, this.special);
      else if (c.p.punch) this.startAttack(c.h.down ? 'cpunch' : 'punch');
      else if (c.p.kick) this.startAttack(c.h.down ? 'sweep' : 'kick');
      else if (c.h.up) { this.setState('jump'); this.vy = this.jumpV; this.vx = (fwd ? 1 : back ? -1 : 0) * this.facing * this.walkSpd * 1.35; this.y = 0.1; this.airAttacked = false; F.sfx('jump'); }
      else if (c.h.down) { this.setState('crouch'); this.vx = 0; this.crouching = true; this.blocking = back; }
      else if (fwd || back) { this.setState('walk'); this.crouching = false; this.vx = (fwd ? 1 : -0.8) * this.facing * this.walkSpd; this.walkBack = back; this.blocking = back; }
      else { this.setState('idle'); this.crouching = false; this.vx = 0; }
      if (this.state !== 'crouch') this.crouching = false;
      this.wantBlock = back && canAct;
    } else this.wantBlock = false;
    if (this.state === 'block') { this.stun--; this.wantBlock = true; }
    if (this.state === 'jump') {
      if (!this.act && !this.airAttacked && canAct && (c.p.punch || c.p.kick)) { this.airAttacked = true; this.act = { ...NORMALS[c.p.punch ? 'jpunch' : 'jkick'] }; this.actT = 0; this.prepAct(); }
    }
    if (this.act && (this.state === 'attack' || this.state === 'jump')) this.tickAttack(F);
    if (this.state === 'move') this.tickMove(F);
    if (this.state === 'hit') { if (--this.stun <= 0) this.setState('idle'); }
    if (this.state === 'down' || this.state === 'ko') { if (this.grounded && this.y <= 0 && this.downT++ > (this.state === 'ko' ? 1e9 : 34)) { this.setState('getup'); } }
    if (this.state === 'getup') { this.invuln = 12; if (this.t > 18) { this.setState('idle'); this.invuln = 10; } }
    // physics
    this.x += this.vx;
    if (this.y > 0 || this.vy > 0) { this.y += this.vy; this.vy -= GRAV;
      if (this.y <= 0) { this.y = 0; this.vy = 0; F.sfx('land');
        if (this.state === 'jump') { this.act = null; this.activeHit = null; this.setState('idle'); this.landLag = 3; this.vx = 0; }
        if (this.state === 'down' || this.state === 'ko') { this.vx *= 0.3; F.shake(3); } } }
    else if (!['walk', 'move'].includes(this.state)) this.vx *= 0.78;
    if (this.state === 'move' && !this.spin && !this.act?.keepVx) this.vx *= 0.85;
    if (this.dispHp > this.hp) this.dispHp = Math.max(this.hp, this.dispHp - 6);
  }
  setState(s) { if (this.state !== s) { this.state = s; this.t = 0; if (s !== 'jump') { if (s !== 'attack') this.act = null; } if (s !== 'move' && s !== 'attack' && s !== 'jump') { this.activeHit = null; this.spin = false; } } }
  prepAct() { // use art hitbox if the sheet provides one
    const a = this.act, m = this.meta(a.anim).hitbox;
    if (m && !a.air && !a.crouch) a.box = { x: m.x, y: m.y, w: m.w, h: m.h };
    if (m && m.frames && m.frames.length) a.af = m.frames;
  }
  startAttack(name) { this.setState('attack'); this.act = { ...NORMALS[name] }; this.actT = 0; this.vx = 0; this.prepAct(); this.crouching = !!this.act.crouch; }
  tickAttack(F) {
    const a = this.act, t = this.actT++;
    if (t === a.startup) { this.activeHit = { box: a.box, props: { dmg: a.dmg, stun: a.stun, bstun: a.bstun, push: a.push, low: a.low, overhead: a.overhead, knockdown: a.knockdown, sound: a.sound || 'hit' }, hits: 1 }; this.hitCount = 0; F.sfx('whiff'); }
    if (t === a.startup + a.active) this.activeHit = null;
    if (t >= a.startup + a.active + a.recovery) { this.act = null; this.activeHit = null; if (this.state === 'attack') this.setState(this.crouching ? 'crouch' : 'idle'); }
  }
  startMove(F, mv) {
    this.setState('move'); this.mv = mv; this.mvT = 0; this.vx = 0; this.hitCount = 0; this.lastHitT = -99; this.activeHit = null;
    this.callout = { text: mv.name, t: 70, big: mv.isSuper };
    if (mv.isSuper) { this.meter = 0; F.superFreeze(this, mv); } else this.meter = Math.min(SUPER_MAX, this.meter + 3);
    F.sfx(mv.sound || 'special'); if (mv.onStart) mv.onStart(this, F);
  }
  movePhase() { const m = this.mv, t = this.mvT; if (t < m.startup) return ['startup', t]; if (t < m.startup + m.active) return ['active', t - m.startup]; return ['recovery', t - m.startup - m.active]; }
  tickMove(F) {
    const m = this.mv; const [ph, pt] = this.movePhase();
    if (m.onTick) m.onTick(this, F, this.mvT, ph, pt);
    if (ph === 'active' && m.sound && pt % 24 === 12) F.sfx(m.sound);
    this.mvT++;
    if (this.mvT >= m.startup + m.active + m.recovery) { this.activeHit = null; this.spin = false; this.setState('idle'); }
  }
  // ---------- getting hit ----------
  takeHit(F, att, p, isBlock) {
    const dir = Math.sign(this.x - att.x) || -att.facing;
    if (isBlock) { const chip = p.special ? Math.round(p.dmg * (p.chip ?? 0.25) * att.power) : 0;
      this.hp = Math.max(this.hp > 1 && chip ? 1 : 0, this.hp - chip); this.setState('block'); this.stun = p.bstun || 10; this.vx = dir * (p.push || 3) * 0.9; this.blocking = true;
      this.meter = Math.min(SUPER_MAX, this.meter + 2); return; }
    const dmg = Math.round(p.dmg * att.power * (this.state === 'hit' || this.state === 'down' ? 0.9 : 1));
    this.hp = Math.max(0, this.hp - dmg); this.perfect = false; this.flash = 3;
    this.meter = Math.min(SUPER_MAX, this.meter + dmg * 0.06);
    if (!p.isSuperDmg) att.meter = Math.min(SUPER_MAX, att.meter + dmg * 0.1);
    this.act = null; this.activeHit = null; this.mv = null;
    if (this.hp <= 0) { this.setState('ko'); this.downT = 0; this.vy = 7; this.y = Math.max(this.y, 0.1); this.vx = dir * 4; return dmg; }
    if (p.knockdown || this.y > 0) { this.setState('down'); this.downT = 0; this.vy = Math.max(this.vy, p.knockdown ? 6.5 : 4); this.y = Math.max(this.y, 0.1); this.vx = dir * (p.push || 3) * 0.8; this.invuln = 0; return dmg; }
    this.setState('hit'); this.stun = (p.stun || 16) + (p.stunExtra || 0); this.vx = dir * (p.push || 3);
    return dmg;
  }
  // ---------- drawing ----------
  frame() {
    const name = this.anim(); const fr = this.art.anims[name] || this.art.anims.idle; const n = fr.length; const meta = this.meta(name); const fps = meta.fps || 8;
    let i = 0, t = this.t;
    switch (this.state) {
      case 'idle': case 'intro': i = Math.floor(t * fps / 60) % n; break;
      case 'walk': i = Math.floor(t * fps / 60) % n; if (this.walkBack) i = n - 1 - i; break;
      case 'crouch': i = Math.min(n - 1, Math.floor(t / 4)); break;
      case 'block': i = this.crouching ? n - 1 : Math.min(n - 1, Math.floor(t / 4)); break;
      case 'jump': if (this.act) return this.attackFrame(); i = this.vy > 4 ? 1 : this.vy > -3 ? 2 : 3; if (this.t < 3) i = 0; i = Math.min(n - 1, i); break;
      case 'attack': return this.attackFrame();
      case 'move': { const [ph, pt] = this.movePhase(), m = this.mv; const sp = meta.spawn ?? 3;
        if (ph === 'startup') i = Math.min(sp - 1, Math.floor(pt / Math.max(1, m.startup) * sp));
        else if (ph === 'active') i = this.spin ? 2 + (Math.floor(pt / 4) % 3) : Math.min(n - 2, sp + Math.floor(pt / 6) % 2);
        else i = Math.min(n - 1, sp + 2); break; }
      case 'hit': i = t < 6 ? 0 : Math.min(n - 1, 1); break;
      case 'down': case 'ko': i = this.y > 30 ? 1 : this.y > 0 ? 2 : (this.downT > 4 ? n - 1 : 2); if (this.t < 4) i = 0; break;
      case 'getup': i = Math.max(0, n - 1 - Math.floor(t / 5)); break;
      case 'win': i = 2 + (Math.floor(t / 14) % 3); break;
    }
    return fr[Math.max(0, Math.min(n - 1, i))];
  }
  attackFrame() {
    const a = this.act; const fr = this.art.anims[a.anim]; const n = fr.length; const af = a.af || [1];
    const t = this.actT, first = af[0], last = af[af.length - 1]; let i;
    if (t < a.startup) i = first === 0 ? 0 : Math.min(first - 1, Math.floor(t / Math.max(1, a.startup) * first));
    else if (t < a.startup + a.active) i = first + Math.min(last - first, Math.floor((t - a.startup) / Math.max(1, a.active) * (last - first + 1)));
    else i = last + 1 < n ? last + 1 + Math.min(n - last - 2, Math.floor((t - a.startup - a.active) / Math.max(1, a.recovery) * (n - last - 1))) : last;
    return fr[Math.max(0, Math.min(n - 1, i))];
  }
  draw(ctx, cam, F) {
    const f = this.frame(); if (!f) return;
    const sx = Math.round(this.x - cam), sy = Math.round(FLOOR_Y - this.y);
    // shadow
    ctx.fillStyle = 'rgba(0,0,0,0.35)'; const sw = Math.max(20, 56 - this.y * 0.2); ctx.fillRect(sx - sw / 2, FLOOR_Y - 3, sw, 5);
    if (this.state === 'move' && this.mv && this.mv.draw) { const [ph, pt] = this.movePhase(); this.mv.draw(ctx, this, F, sx, sy, ph, pt); }
    let face = this.facing; if (this.spin && (Math.floor(this.t / 4) % 2)) face = -face;
    const sq = this.act && this.act.crouch ? CROUCH_SQUASH : 1;
    const img = this.flash > 0 ? flashOf(f.img) : f.img;
    ctx.save(); ctx.translate(sx, sy); ctx.scale(face, sq);
    if (this.invuln > 0 && this.state !== 'getup' && (this.t % 4 < 2)) ctx.globalAlpha = 0.6;
    ctx.drawImage(img, f.sx, f.sy, f.sw, f.sh, -f.ax, -f.ay, f.sw, f.sh);
    ctx.restore();
  }
}
