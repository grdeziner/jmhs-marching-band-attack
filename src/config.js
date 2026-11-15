// Core constants. Everything tunable about the roster/stages lives in content/*.json.
export const VIEW_W = 640;
export const VIEW_H = 360;
export const FLOOR_Y = 320;          // feet line in screen px (stage art floor y=160 at 320x180, x2)
export const WORLD_W = 960;          // stage width (mid layer 480 px x2)
export const FPS = 60;
export const FRAME_W = 96;           // character sprite frame (native px)
export const FRAME_H = 112;
export const PORTRAIT = 64;
export const ROUND_TIME = 99;
export const SUPER_MAX = 100;

// Spritesheet row layout (Character Artist spec). Row order matters for grid sheets.
export const ANIM_ROWS = [
  ['idle', 4], ['walk', 6], ['jump', 4], ['crouch', 2], ['block', 2],
  ['punch', 3], ['kick', 4], ['special', 6], ['hit', 2], ['ko', 4],
];
export const ANIM_FPS = { idle: 7, walk: 10, jump: 8, crouch: 8, block: 8, punch: 14, kick: 12, special: 12, hit: 10, ko: 8 };

export const DEFAULT_KEYS = {
  p1: { up: ['KeyW'], down: ['KeyS'], left: ['KeyA'], right: ['KeyD'],
        punch: ['KeyF'], kick: ['KeyG'], special: ['KeyH'], super: ['KeyR'], start: ['Enter', 'Space'] },
  p2: { up: ['ArrowUp'], down: ['ArrowDown'], left: ['ArrowLeft'], right: ['ArrowRight'],
        punch: ['Numpad1', 'Comma'], kick: ['Numpad2', 'Period'], special: ['Numpad3', 'Slash'], super: ['Numpad0', 'Quote'], start: ['NumpadEnter', 'Backslash'] },
};
// In 1-player modes P1 also accepts these (right-hand attack keys + arrows).
export const SOLO_EXTRA = { up: ['ArrowUp'], down: ['ArrowDown'], left: ['ArrowLeft'], right: ['ArrowRight'],
  punch: ['KeyJ'], kick: ['KeyK'], special: ['KeyL'], super: ['KeyI'] };

export function params() {
  const p = new URLSearchParams(location.search);
  const o = {}; for (const [k, v] of p) o[k] = v; return o;
}
