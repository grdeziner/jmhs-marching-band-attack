// Keyboard + gamepad input. Each Controller exposes held buttons (.h) and this-frame presses (.p).
import { DEFAULT_KEYS, SOLO_EXTRA } from './config.js';
const BTN = ['up', 'down', 'left', 'right', 'punch', 'kick', 'special', 'super', 'start', 'back'];
const keys = new Set();
let anyPressed = false;
export function initKeyboard(onFirst) {
  addEventListener('keydown', e => { if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) e.preventDefault();
    keys.add(e.code); anyPressed = true; onFirst && onFirst(); });
  addEventListener('keyup', e => keys.delete(e.code));
  addEventListener('blur', () => keys.clear());
  addEventListener('pointerdown', () => onFirst && onFirst());
}
export class Controller {
  constructor(idx) { this.idx = idx; this.map = idx === 0 ? DEFAULT_KEYS.p1 : DEFAULT_KEYS.p2; this.solo = false;
    this.h = {}; this.prev = {}; this.p = {}; this.virtual = null; for (const b of BTN) { this.h[b] = false; this.prev[b] = false; this.p[b] = false; } }
  read() {
    const s = {}; const m = this.map;
    for (const b of BTN) s[b] = !!(m[b] && m[b].some(k => keys.has(k)));
    if (this.solo) for (const b in SOLO_EXTRA) s[b] = s[b] || SOLO_EXTRA[b].some(k => keys.has(k));
    s.back = s.back || keys.has('Escape') || keys.has('Backspace');
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    const gp = pads && pads[this.idx];
    if (gp) { const B = (i) => gp.buttons[i] && gp.buttons[i].pressed, ax = gp.axes || [];
      s.left ||= B(14) || ax[0] < -0.5; s.right ||= B(15) || ax[0] > 0.5; s.up ||= B(12) || ax[1] < -0.5; s.down ||= B(13) || ax[1] > 0.5;
      s.punch ||= B(2); s.kick ||= B(0); s.special ||= B(3) || B(1); s.super ||= B(5) || B(7); s.start ||= B(9); s.back ||= B(8); }
    return s;
  }
  update() {
    const s = this.virtual ? { ...this.virtual } : this.read();
    for (const b of BTN) { this.prev[b] = this.h[b]; this.h[b] = !!s[b]; this.p[b] = this.h[b] && !this.prev[b]; }
  }
  clearVirtual() { this.virtual = null; }
}
export function keyDown(code) { return keys.has(code); }
