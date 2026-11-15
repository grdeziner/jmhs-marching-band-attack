// CPU opponent. Produces a virtual controller state each frame. level 1 (easy) .. 5 (brutal).
export class CPU {
  constructor(level = 2, rand = Math.random) { this.level = level; this.rand = rand; this.hold = {}; this.holdT = 0; this.react = 0; this.state = {}; }
  think(me, F) {
    const o = F.opponent(me), L = this.level, r = this.rand;
    const d = Math.abs(o.x - me.x), toward = o.x > me.x ? 'right' : 'left', away = toward === 'right' ? 'left' : 'right';
    const s = { up: false, down: false, left: false, right: false, punch: false, kick: false, special: false, super: false };
    if (F.phase !== 'fight') return s;
    // continue a held plan
    if (this.holdT > 0) { this.holdT--; return { ...s, ...this.hold }; }
    const set = (k, frames) => { this.hold = k; this.holdT = frames; return { ...s, ...k }; };
    const reactChance = [0, 0.15, 0.35, 0.55, 0.75, 0.92][L];
    // threats: incoming projectile or opponent attacking nearby
    const proj = F.projectiles.find(p => p.owner === o && !p.dead && Math.sign(p.vx || 0) === Math.sign(me.x - p.x) && Math.abs(p.x - me.x) < 170);
    const attacking = (o.state === 'attack' || o.state === 'move' || (o.state === 'jump' && o.act)) && d < 190;
    if ((proj || attacking) && r() < reactChance) {
      if (proj && !proj.props.low && r() < 0.4 && L >= 2) return set({ up: true, [toward]: true }, 6);
      const low = (o.act && o.act.low) || (proj && proj.props.low);
      return set({ [away]: true, down: !!low }, 10 + (r() * 8 | 0));
    }
    if (me.state !== 'idle' && me.state !== 'walk' && me.state !== 'crouch') return s;
    if (me.meter >= 100 && d < 300 && r() < 0.04 * L) return set({ super: true }, 1);
    const type = me.def.special.type;
    const ranged = ['projectile', 'boomerang'].includes(type);
    const act = r();
    if (d > 230) {
      if (ranged && act < 0.012 * L + 0.01) return set({ special: true }, 1);
      if (act < 0.02) return set({ up: true, [toward]: true }, 4);
      return set({ [toward]: true }, 8 + (r() * 10 | 0));
    }
    if (d > 110) {
      if (ranged && act < 0.02 * L) return set({ special: true }, 1);
      if (['poke', 'rush', 'blast', 'spin'].includes(type) && d < (type === 'poke' ? 170 : 140) && act < 0.025 * L) return set({ special: true }, 1);
      if (act < 0.03) return set({ up: true, [toward]: true }, 4);
      if (act < 0.08) return set({ [away]: true }, 10);
      return set({ [toward]: true }, 6 + (r() * 8 | 0));
    }
    // close range
    if (o.state === 'jump' && o.y > 40 && r() < reactChance * 0.4) return set({ punch: true }, 1);
    if (type === 'grab' && d < 70 && act < 0.05 * L) return set({ special: true }, 1);
    if (act < 0.035 * L + 0.02) return set({ punch: true }, 1);
    if (act < 0.06 * L + 0.03) return set({ kick: true, down: r() < 0.35 }, 1);
    if (act < 0.06 * L + 0.06) return set({ down: true, kick: true }, 1);
    if (act < 0.06 * L + 0.10) return set({ [away]: true }, 12);
    if (act < 0.06 * L + 0.12) return set({ up: true }, 4);
    return set({}, 4 + (r() * 6 | 0));
  }
}
