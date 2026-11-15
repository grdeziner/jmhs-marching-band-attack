// Band Wars — football stage contract (Friday Night Field).
// SNES / Street Fighter II Turbo-era 16-bit pixel art.
// Native view 640x360.
//   far:  640x360, camera-locked, opaque
//   mid:  960x360, origin x=-160 (50-yard line at view x=320)
//   anim: 960x360, aligned to mid, 8 frames
//   near: 1120x360, origin x=-240, drawn IN FRONT of fighters
// School colors: navy + gold + white trim (same swatches as the fighter palette).

export const footballStage = {
  id: 'football',
  title: 'Friday Night Field',
  view: { w: 640, h: 360 },
  worldW: 960,
  floorY: 320,             // fighters' feet
  floorBand: { top: 300, bottom: 360 },
  far: { src: './far.png', w: 640, h: 360, opaque: true },
  mid: { src: './mid.png', w: 960, h: 360, opaqueSky: false },
  anim: {
    frames: [
      './anim_0.png', './anim_1.png', './anim_2.png', './anim_3.png',
      './anim_4.png', './anim_5.png', './anim_6.png', './anim_7.png',
    ],
    w: 960,
    h: 360,
    frameDurationMs: 120,
  },
  near: { src: './near.png', w: 1120, h: 360, opaqueSky: false, static: true },
  // Draw mid/anim at this origin in view space so the 50-yard line sits at x=320.
  midOriginInView: { x: -160, y: 0 },
  // Near is wider; keep it centered the same way. Foreground, in front of fighters.
  nearOriginInView: { x: -240, y: 0 },
  // Draw order (back to front): far, mid, fighters, anim? No: far, mid, anim, fighters, near.
  // Anim is a mid-aligned overlay (crowd / flags / light flicker) and sits with the mid layer,
  // behind the fighters. Near is the only layer in front of the fighters.
  drawOrder: ['far', 'mid', 'anim', 'fighters', 'near'],
};

export default footballStage;
