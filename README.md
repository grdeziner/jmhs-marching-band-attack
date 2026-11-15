# JMHS MARCHING BAND ATTACK

A Street Fighter II-style 1v1 fighting game starring the JMHS marching band. It's plain HTML5 canvas and ES modules with a Web Audio chip synth, and has no dependencies.

## Play on GitHub Pages

<https://grdeziner.github.io/jmhs-marching-band-attack/>

Every push to `main` runs [`.github/workflows/pages.yml`](.github/workflows/pages.yml), which uploads the repository root. The single-file build is at <https://grdeziner.github.io/jmhs-marching-band-attack/dist/index.html>.

One-time setup: set **Settings > Pages > Source** to **GitHub Actions** once.

## Play
* **Single file:** open `dist/index.html` straight from disk. Everything (code, content, art, music) is inlined.
* **Dev (multi-file):** `python3 -m http.server 8080`, then open http://localhost:8080/. ES modules need http, so a `file://` URL won't work for the root `index.html`.
* **Rebuild the single file** after any art, content or music change: `node build.js` (writes `dist/index.html`).

Modes: Arcade (1P ladder against every other fighter, with continues and the fighter's story ending), VS CPU (pick both fighters and the stage), 2P Versus (local), CPU vs CPU (watch), How to Play, and Options (CPU level 1-5, rounds, timer, music, SFX, announcer voice, hitbox view).

### Controls
| | P1 | P2 |
|---|---|---|
| Move / jump / crouch | W A S D | Arrow keys |
| Punch / Kick / Special | F / G / H | Num1 / Num2 / Num3 (or `,` `.` `/`) |
| Super (meter full) | R | Num0 (or `'`) |
In 1-player modes P1 can also use the arrows plus J/K/L/I. Gamepads work too. Esc pauses.
* Hold back to block. Crouch-block stops lows and sweeps. Jump-ins have to be blocked standing.
* Down+Kick is a sweep (knockdown). Down+Punch is a low jab.
* Quarter-circle-forward + Punch also does your special, and Special+Kick does your super.

## Project layout
```
index.html              dev entry (loads src/main.js)
src/                    ES modules: main, config, content, assets, procart, stage, fight, fighter, moves, ai, audio (SNES synth), hud, fx, input, font, scenes
content/roster.json     EDITABLE roster: enabled/order, stats, placeholder look, special/super type + numbers
content/stages.json     stages (id, name, subtitle, musicFile)
content/characters/*.json  story text (Story Writer): name, taunt, winQuote, ending ... shown in game
art/characters/<id>/    sheet.png + sheet.json + portrait.png + projectile.png, optional portrait_large.png / super.png (Character Artist)
art/stages/<id>/        far.png 640x360, mid.png 960x360, optional near.png 1120x360, anim_0..7.png (Stage Artist)
audio/music/            instruments.js (patch catalog) + <id>.js / title / select / victory song modules, format 2 (Composer)
build.js                single-file builder -> dist/index.html
tests/                  headless Playwright tests (run_tests.py, fallback_test.py, sixteen_bit_test.py, smoke.py) + make_fixtures.py / fixtures/
screenshots/            output of the test run
```

## Asset pipeline (16-bit)
* **Characters:** `sheet.json` is the source of truth. Frame size comes from `frameW`/`frameH` (or `frameWidth`/`frameHeight`), defaulting to 96x112 for older sheets; the current 16-bit size is 128x112 with the anchor at 64,111. Frame counts, fps, loop, hurtbox/hitbox (`hitbox.frames` = active frames), `spawn_projectile_on`, `hold_frames` and `hold_point` are read per animation. A row's y position comes from its `row` (or its order in `animations`), and the sheet may be as wide as the longest animation. `projectile.png` is described by `sheet.json.projectile`. Optional: `portrait_large.png` (128x128) is used on the select, VS and result screens, and otherwise `portrait.png` is upscaled. Optional: `super.png`, listed under `sheet.json.super`, is used for the super effect, and otherwise the effects are code-drawn. Tuba's special carries the opponent overhead on its `hold_frames` (2-3), and the ground shock spawns on frame 4. A fighter with no sheet gets procedural placeholder art. `art/characters_8bit_backup/` is not used at runtime.
* **Stages:** `far.png` is fixed. `mid.png` (960) sits at x=-160 when the camera is centred. `near.png` (1120, 240 px margin each side) sits at x=-240 and is drawn **in front of** the fighters. `anim_0..3` (and `anim_4..7` when 0-3 all exist) are overlaid on the far, mid or near layer according to their width, at 120 ms per frame. The floor is y=320. Missing files fall back to a stand-in.
* **Music / SNES synth (`src/audio.js`):**
  * Up to 8 voices, each with its own patch, volume, pan and echo send. An echo bus has a 4 kHz low-pass inside the feedback loop, plus a short reverb.
  * Patches come from `audio/music/instruments.js` (`INSTRUMENTS[id].recipe`: trumpet-lead, brass-section, horn, trombone, tuba-bass, glockenspiel, snare, bass-drum, cymbals, quad-toms, clarinet, flute, organ). They are merged over built-in copies, and unknown ids fall back to a muted saw.
  * Format 2: `{format:2, bpm, loop, instruments:{voice:id}, channels:{voice:[[note|null|[chord], 16ths, velocity?]]}, mix:{voice:{volume,pan}}, echo:{delay,feedback,mix}}`. A channel may also be `{instrument, volume, pan, echo, notes}`.
  * Drum articulations: snare hit/rim/roll/flam; bass drum hit or a pitch; cymbals hit/crash/choke/ride; toms take pitches.
  * Old 4-channel songs still play: pulse1→trumpet-lead, pulse2→brass-section, triangle→tuba-bass, noise→drum kit.
  * BPM is authoritative. `loop` is true, false or a sixteenth index. `title.js` plays on the title screen, `select.js` on character select and `victory.js` (one-shot) on the win screen.
* **HUD / FX:**
  * Beveled gradient health bars that empty from the KO emblem outward, with a red damage trail that holds about half a second and then drains.
  * Italic gradient SF2 Turbo-style text, medal round markers and rainbow super meters.
  * Starburst hit sparks, block sparks, landing and knockdown dust, screen shake, a radial super-flash background and shadows under the fighters.
* **Story:** `content/characters/<id>.json` overrides name, instrument, section, taunt, winQuote and ending. `boss.json` isn't loaded yet because the boss isn't implemented.

## Editing the roster
In `content/roster.json` you can set `enabled:false` to hide a fighter, change `order` to move it on the grid, tune `stats` (health, walk, jump, power), or edit `special` / `super`. Each move has a `type` from `src/moves.js` (projectile, rush, poke, blast, grab, boomerang, barrage, rain, tornado, beam, spin, avalanche, vacuum) plus its numbers (damage, speed, hits, frames…).

## Tests
```
python3 -m http.server 8731 &           # from this folder
python3 tests/run_tests.py              # menus, 6 full CPU-vs-CPU matches on all stages, every special+super, audio, screenshots
python3 tests/fallback_test.py          # all placeholder art (?art=__missing__/)
python3 tests/sixteen_bit_test.py       # 16-bit contract on generated fixtures: 128x112 sheets, portrait_large, super.png, near/anim_0..7, format-2 + legacy songs
python3 tests/run_tests.py file://$PWD/dist/index.html   # same suite on the single-file build
```
URL hooks: `?fight=1&p1=drummer&p2=tuba&stage=football&cpu1=1`, `?mute=1`, `?manual=1` (test stepping), `?speed=4`, `?art=<dir>/`, `?scene=select`. `window.BAND` exposes the game for tests.
