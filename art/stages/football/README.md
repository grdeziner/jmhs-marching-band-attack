# Football stage — Friday Night Field

SNES / Street Fighter II Turbo-era 16-bit pixel art for Band Wars. The last
home game is over, the clock is at `0:00`, and the finals are fought on the
50-yard line under lights that are still humming. Bleachers are packed with
a leftover crowd and a JMHS band block in navy, gold, and white. School
colors match the fighter palette.

Regenerate with `python3 generate.py` (needs Pillow). Crisp 1px pixels, no
antialiasing, no partial alpha. Gradients, moon glow, and stadium-light
blooms use ordered (Bayer) dithering.

## Delivery contract

| File | Size | Notes |
|---|---|---|
| `far.png` | **640×360** RGB, opaque | Dithered night sky, moon glow, stars, far trees, water tower, distant buildings. Locked to the camera. |
| `mid.png` | **960×360** RGBA | Main stadium. Transparent sky so `far` shows through. Includes the floor, architecture, lamp banks, scoreboard, and static light shafts / turf pool. 160 px of parallax on each side (end zones + goal posts). |
| `anim_0.png` … `anim_7.png` | **960×360** RGBA, transparent bg | Aligned to `mid.png`. Packed crowd bob + cheering, flag waves, lamp flicker, bloom pulse, scoreboard colon blink, press-box beacon. |
| `near.png` | **1120×360** RGBA | Foreground, drawn **in front of fighters**. Origin `x = -240`. Sideline railing ends, camera tripod, generic coolers, pom-poms, a bass drum on a stand — at the far left/right edges only. Fully transparent in the action well (`x = 280..839`, `y = 200..359`). Static. |
| `preview.png` | **640×360** RGB | Composite of `far` + centered `mid` + `anim_0` + centered `near`. |
| `preview@2x.png` | **1280×720** RGB | Nearest-neighbor 2× of `preview.png`, for viewing only. |

Also in this folder (not required by the integrator): `generate.py`,
`football.js`, `preview.html`, this README.

## Layout

- View / camera: **640×360**.
- Mid / anim origin in view space: **x = -160, y = 0**.
- Near origin in view space: **x = -240, y = 0**.
- Draw order, back to front: **far → mid → anim → fighters → near**.
- 50-yard line is at mid `x = 480` = view `x = 320`.
- Scale: 8 px per yard. Goal lines at mid `x = 80` and `x = 880`. Visible
  window at rest is the 10-yard line to the far 10-yard line.
- **Floor line (fighters' feet): y = 320.**
- Floor band **y = 300…360** is lit turf + yard lines only (a dithered brighter
  “pool” under the stadium lights). Numbers sit at the top of the turf
  (`y ≈ 304`). No props, hats, or flags in this band.
- Parallax: `far` stays with the camera; `mid` + `anim` may shift up to ±160 px;
  `near` may shift up to ±240 px.

## Animation

8 frames, recommended **120 ms** per frame (~8 fps).

- Packed crowd: 1 px bob and raised-arm cheers in four staggered groups.
- School and color-guard flags wave (including two handheld flags on the track).
- Stadium lamp banks flicker; dithered bloom/shafts pulse.
- Scoreboard colon on `0:00` blinks; roof beacon blinks.

## Palette

16-bit, well beyond 32 colors on the composite (preview is ~150 unique colors),
still a hand-pixeled limited set with no blended/partial-alpha pixels. Navy /
gold / white / skin / outline swatches match
`art/characters/tools/pxart/palette.py` so uniforms and flags sit next to the
fighters without a color shift.
