// Special / super move behaviours. content/roster.json picks a `type` and tunes it.
// A move is { startup, active, recovery, anim, onStart?, onTick?(f,F,t,phase,pt), draw?(ctx,f,F,cam) }.
// Melee moves set f.activeHit = { box:{x,y,w,h} (anchor-relative, facing right), props, hits, interval }.

const P = (m, extra = {}) => ({ dmg: m.damage || 50, stun: 18, bstun: 14, push: 4, chip: 0.25, sound: 'heavy', special: true, ...extra });
const sec = (m) => (m.super ? 'super' : 'special');

export const MOVE_TYPES = {
  projectile: (m) => ({ startup: 14, active: 10, recovery: 16,
    canStart: (f, F) => !F.projectiles.some(p => p.owner === f && !p.dead && !p.isSuper),
    onTick(f, F, t, ph, pt) { if (ph === 'active' && pt === 0) {
      const big = m.kind === 'drone' ? 56 : m.kind === 'wave' ? 44 : 34;
      F.spawnProjectile(f, { kind: m.kind || 'note', x: f.x + f.facing * 46, y: m.kind === 'drone' ? 34 : m.kind === 'wave' ? 46 : 62,
        vx: (m.speed || 5) * f.facing, w: big, h: m.kind === 'drone' ? 56 : 30, color: m.color, usePng: true,
        props: P(m, { stunExtra: m.stun || 0, knockdown: !!m.knockdown, low: !!m.low }) }); } } }),

  rush: (m) => ({ startup: 8, active: m.frames || 26, recovery: 16, onTick(f, F, t, ph, pt) {
    if (ph === 'active') { f.vx = (m.speed || 7) * f.facing; f.spin = !!m.super;
      if (pt === 0) f.activeHit = { box: { x: 0, y: -92, w: 58, h: 82 }, props: P(m, { stun: 14, push: 1.5, chip: 0.2, sound: 'hit' }),
        hits: m.hits || 4, interval: Math.max(3, Math.floor((m.frames || 26) / (m.hits || 4))), last: { knockdown: true, push: 6 } }; }
    else if (ph === 'recovery' && pt === 0) { f.activeHit = null; f.spin = false; f.vx *= 0.3; } } }),

  poke: (m) => ({ startup: 9, active: m.frames || 14, recovery: 18, onTick(f, F, t, ph, pt) {
    if (ph === 'active' && pt === 0) f.activeHit = { box: { x: 18, y: -78, w: m.reach || 140, h: 24 }, props: P(m, { push: 6 }), hits: 1 };
    if (ph === 'recovery' && pt === 0) f.activeHit = null; } }),

  blast: (m) => ({ startup: 10, active: 8, recovery: 20, onTick(f, F, t, ph, pt) {
    if (ph === 'active' && pt === 0) { F.shake(6); f.activeHit = { box: { x: 20, y: -96, w: m.range || 110, h: 74 }, props: P(m, { push: m.knockback || 9, knockdown: true }), hits: 1 }; }
    if (ph === 'recovery' && pt === 0) f.activeHit = null; },
    draw(ctx, f, F, sx, sy, ph, pt) { if (ph !== 'active') return; ctx.fillStyle = 'rgba(255,230,120,0.5)';
      for (let k = 0; k < 4; k++) { const r = 20 + k * 16 + pt * 3; ctx.fillRect(sx + f.facing * (30 + k * 18) - (f.facing < 0 ? 8 : 0), sy - 70 - r / 2, 8, r); } } }),

  grab: (m) => ({ startup: 5, active: 3, recovery: 26, onTick(f, F, t, ph, pt) {
    if (ph !== 'active' || pt !== 0) return; const o = F.opponent(f);
    if (Math.abs(o.x - f.x) < (m.range || 70) && o.y === 0 && o.throwable()) {
      F.shake(10); F.hitDirect(f, o, P(m, { unblockable: true, knockdown: true, push: 7, sound: 'heavy' }));
      o.x = f.x + f.facing * 30; o.vx = f.facing * 6; o.vy = 9; } } }),

  boomerang: (m) => ({ startup: 12, active: 6, recovery: 16,
    canStart: (f, F) => !F.projectiles.some(p => p.owner === f && !p.dead),
    onTick(f, F, t, ph, pt) { if (ph === 'active' && pt === 0) F.spawnProjectile(f, { kind: m.kind || 'flag', x: f.x + f.facing * 40, y: 70,
      vx: (m.speed || 6) * f.facing, w: 40, h: 26, returnAt: 42, usePng: true, props: P(m, { sound: 'hit' }) }); } }),

  // ---------------- supers ----------------
  barrage: (m) => ({ startup: 10, active: (m.count || 6) * (m.interval || 7), recovery: 14, onTick(f, F, t, ph, pt) {
    if (ph === 'active' && pt % (m.interval || 7) === 0) F.spawnProjectile(f, { kind: 'wave', x: f.x + f.facing * 46, y: 40 + ((pt / (m.interval || 7)) % 2) * 34,
      vx: (m.speed || 8) * f.facing, w: 44, h: 30, color: '#f5de6a', usePng: true, isSuper: true, props: P(m, { stun: 16, push: 2, chip: 0.2, sound: 'hit', knockdown: pt >= ((m.count || 6) - 1) * (m.interval || 7) }) }); } }),

  rain: (m) => ({ startup: 10, active: (m.count || 8) * (m.interval || 8), recovery: 12, onTick(f, F, t, ph, pt) {
    const cols = ['#ff595e', '#ff924c', '#ffca3a', '#8ac926', '#1982c4', '#6a4c93'];
    if (ph === 'active' && pt % (m.interval || 8) === 0) { const o = F.opponent(f);
      F.spawnProjectile(f, { kind: 'chime', x: o.x + (F.rand() * 60 - 30), y: 300, vx: 0, vy: -7, w: 30, h: 16, color: cols[(pt / 8 | 0) % cols.length], isSuper: true, falls: true,
        props: P(m, { stun: 16, push: 1, chip: 0.2, sound: 'hit', overhead: true }) }); } } }),

  tornado: (m) => ({ startup: 12, active: 16, recovery: 18, onTick(f, F, t, ph, pt) {
    if (ph === 'active' && pt === 0) F.spawnProjectile(f, { kind: 'tornado', x: f.x + f.facing * 50, y: 60, vx: (m.speed || 3) * f.facing, w: 56, h: 120,
      hits: m.hits || 8, interval: 7, isSuper: true, life: 220, props: P(m, { stun: 14, push: 0.5, chip: 0.15, sound: 'hit' }), last: { knockdown: true, push: 5 } }); } }),

  beam: (m) => ({ startup: 12, active: m.frames || 48, recovery: 20, onTick(f, F, t, ph, pt) {
    if (ph === 'active' && pt === 0) { F.shake(4); f.activeHit = { box: { x: 34, y: -92, w: 760, h: 40 }, props: P(m, { stun: 12, push: m.push || 4, chip: 0.2, sound: 'hit' }),
      hits: m.hits || 9, interval: Math.floor((m.frames || 48) / (m.hits || 9)), last: { knockdown: true, push: 8 } }; }
    if (ph === 'recovery' && pt === 0) f.activeHit = null; },
    draw(ctx, f, F, sx, sy, ph, pt) { if (ph !== 'active') return; const h = 30 + Math.sin(pt) * 6, x0 = sx + f.facing * 34;
      ctx.fillStyle = 'rgba(255,220,90,0.55)'; ctx.fillRect(f.facing > 0 ? x0 : x0 - 760, sy - 72 - h / 2, 760, h);
      ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.fillRect(f.facing > 0 ? x0 : x0 - 760, sy - 72 - h / 5, 760, h / 2.5); } }),

  spin: (m) => ({ startup: 8, active: m.frames || 56, recovery: 18, onTick(f, F, t, ph, pt) {
    if (ph === 'active') { f.vx = (m.speed || 3) * f.facing; f.spin = true;
      if (pt === 0) f.activeHit = { box: { x: -30, y: -96, w: 100, h: 86 }, props: P(m, { stun: 14, push: 1, chip: 0.2, sound: 'hit' }),
        hits: m.hits || 7, interval: Math.floor((m.frames || 56) / (m.hits || 7)), last: { knockdown: true, push: 7 } }; }
    if (ph === 'recovery' && pt === 0) { f.activeHit = null; f.spin = false; f.vx = 0; } } }),

  avalanche: (m) => ({ startup: 14, active: (m.count || 5) * (m.interval || 10), recovery: 18, onTick(f, F, t, ph, pt) {
    if (ph === 'active' && pt % (m.interval || 10) === 0) { F.shake(8); const last = pt >= ((m.count || 5) - 1) * (m.interval || 10);
      for (const d of [1, -1]) F.spawnProjectile(f, { kind: 'quake', x: f.x + d * 40, y: 12, vx: d * 6, w: 52, h: 24, isSuper: true,
        props: P(m, { stun: 16, low: true, push: 2, chip: 0.2, sound: 'hit', knockdown: last }) }); } } }),

  vacuum: (m) => ({ startup: 10, active: m.frames || 70, recovery: 24, onTick(f, F, t, ph, pt) {
    const o = F.opponent(f), A = m.frames || 70;
    if (ph === 'active' && pt < A - 6 && o.y === 0 && o.state !== 'down' && o.state !== 'ko' && Math.abs(o.x - f.x) > 56) o.x -= Math.sign(o.x - f.x) * (m.pull || 3);
    if (ph === 'active' && pt === A - 6) { F.shake(14); f.activeHit = { box: { x: -20, y: -112, w: 160, h: 112 }, props: P(m, { knockdown: true, push: 9, chip: 0.3, sound: 'heavy' }), hits: 1 }; }
    if (ph === 'recovery' && pt === 0) f.activeHit = null; },
    draw(ctx, f, F, sx, sy, ph, pt) { if (ph !== 'active') return; ctx.strokeStyle = 'rgba(167,139,250,0.8)'; ctx.lineWidth = 3;
      for (let k = 0; k < 4; k++) { const r = 140 - ((pt * 4 + k * 35) % 140); ctx.beginPath(); ctx.arc(sx + f.facing * 30, sy - 56, r, 0, Math.PI * 2); ctx.stroke(); } } }),
};

export function makeMove(m, isSuper) {
  const mk = MOVE_TYPES[m.type] || MOVE_TYPES.projectile;
  const mv = mk({ ...m, super: m.super || isSuper });
  mv.anim = 'special'; mv.name = m.name; mv.isSuper = isSuper; mv.sound = m.sound; return mv;
}
