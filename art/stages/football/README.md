# Football stage — Friday Night Field

Pixel-art stage for Band Wars. The last home game is over, the clock is at
`0:00`, and the finals are fought on the 50-yard line under lights that are
still humming. Bleachers are mostly empty, with a leftover JMHS band block and
a few fans. School colors are navy + gold + white trim.

Regenerate with `python3 generate.py` (needs Pillow).

## Delivery contract

| File | Size | Notes |
|---|---|---|
| `far.png` | **640×360** RGB, opaque | Night sky, moon, stars, far trees, water tower, distant buildings. Locked to the camera. |
| `mid.png` | **960×360** RGBA | Main stadium. Transparent sky so `far` shows through. Includes the floor. 160 px of parallax on each side (end zones + goal posts). |
| `anim_0.png` … `anim_3.png` | **960×360** RGBA, transparent bg | Aligned to `mid.png`. Crowd bob, flag wave, lamp flicker, scoreboard colon blink, press-box beacon. |
| `preview.png` | **640×360** RGB | Composite of `far` + centered `mid` + `anim_0`. |
| `preview@2x.png` | **1280×720** RGB | Nearest-neighbor 2× of `preview.png`, for viewing only. |

Also in this folder (not required by the integrator): `generate.py`,
`football.js`, `preview.html`, this README.

## Layout

- View / camera: **640×360**.
- Mid origin in view space: **x = -160, y = 0** (center the 960-wide layer).
- 50-yard line is at mid `x = 480` = view `x = 320`.
- Scale: 8 px per yard. Goal lines at mid `x = 80` and `x = 880`. Visible
  window at rest is the 10-yard line to the far 10-yard line.
- **Floor line (fighters' feet): y = 320.**
- Floor band **y = 300…360** is simple lit turf + yard lines only. Numbers sit
  at the top of the turf (`y ≈ 304`). No props, hats, or flags in this band.
- Parallax: `far` stays with the camera; `mid` + `anim` may shift up to ±160 px.

## Animation

4 frames, recommended **140 ms** per frame (~7 fps).

- Band / crowd: 1 px bob in alternating groups.
- School and color-guard flags wave (including two handheld flags on the track).
- Stadium lamp banks flicker (a few lamps dim or run hot each frame).
- Scoreboard colon on `0:00` blinks; roof beacon blinks.

## Palette

Limited, hard-edged pixels. No antialiasing, no partial alpha (only 0 or 255).
Navy / gold / white / skin / outline swatches match
`art/characters/tools/pxart/palette.py` so uniforms and flags sit next to the
fighters without a color shift.
