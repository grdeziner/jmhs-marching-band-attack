// Band Wars — football stage contract (Friday Night Field).
// Native view 640x360. Mid/anim are 960x360 for parallax (centered at x=-160).
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
    frames: ['./anim_0.png', './anim_1.png', './anim_2.png', './anim_3.png'],
    w: 960,
    h: 360,
    frameDurationMs: 140,
  },
  // Draw mid/anim at this origin in view space so the 50-yard line sits at x=320.
  midOriginInView: { x: -160, y: 0 },
};

export default footballStage;
