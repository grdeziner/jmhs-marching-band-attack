# JMHS Marching Band Attack

Working title: **Band Wars**. A Street Fighter II-style 1v1 fighting game starring the JMHS marching band. Plain HTML5 canvas and ES modules, with a Web Audio chip synth and no dependencies.

Arcade mode walks one fighter through the rest of the roster, with continues and that fighter's ending. There is also VS CPU, local 2P, CPU vs CPU, How to Play, and Options (CPU level 1–5, rounds, timer, music, SFX, announcer, hitbox view).

## Play on GitHub Pages

<https://grdeziner.github.io/jmhs-marching-band-attack/>

Every push to `main` runs [`.github/workflows/pages.yml`](.github/workflows/pages.yml), which uploads the repository root and deploys it with GitHub Pages. The single-file build is on that same site at <https://grdeziner.github.io/jmhs-marching-band-attack/dist/index.html> and can be saved and opened from disk.

One-time setup: the owner must set **Settings > Pages > Source** to **GitHub Actions** once. Until that source is selected, the workflow has nowhere to publish.

## Run locally

**Single file:** open `dist/index.html` straight from disk. Code, content, art, and music are inlined.

**Dev (multi-file):** ES modules need HTTP, so a `file://` URL will not run the root `index.html`. From the repository root:

```
python3 -m http.server 8000
```

or:

```
npx serve . -p 8000
```

Then open <http://localhost:8000>. `npx serve .` on its own prints the address it picked (port 3000 when that port is free). `npm run serve` uses port 8080.

**Rebuild the single file** after any art, content, or music change:

```
node build.js
```

That rewrites `dist/index.html` and `content/files.json`. The dev page uses `content/files.json` so it does not request art or songs that are not in the repo yet.

## Controls

| | P1 | P2 |
| --- | --- | --- |
| Move / jump / crouch | W A S D | Arrow keys |
| Punch / Kick / Special | F / G / H | Num1 / Num2 / Num3 (or `,` `.` `/`) |
| Super (meter full) | R | Num0 (or `'`) |

In 1-player modes P1 can also use the arrows plus J / K / L / I. Gamepads work too. Esc pauses.

Hold back to block. Crouch-block stops lows and sweeps. Jump-ins have to be blocked standing. Down+Kick is a sweep. Down+Punch is a low jab. Quarter-circle-forward + Punch also does the special, and Special+Kick does the super.

URL hooks for testing: `?fight=1&p1=drummer&p2=tuba&stage=football&cpu1=1`, `?mute=1`, `?manual=1`, `?speed=4`, `?scene=select`. `window.BAND` is the running game.

## Layout

```
index.html                 dev entry (loads src/main.js)
dist/index.html            single-file build (committed, downloadable)
src/                       engine: fight, fighter, moves, ai, scenes, audio, input
content/roster.json        enabled/order, stats, placeholder look, special/super
content/stages.json        stage names and music files
content/characters/*.json  backstories
content/story.md           the same stories, readable
content/files.json         assets that exist (rewritten by build.js)
art/characters/<id>/       sheet.png, sheet.json, portrait.png, optional projectile.png
art/stages/<id>/           far.png, mid.png, anim_0..3.png
audio/music/<id>.js        stage songs
build.js                   writes dist/index.html
tests/                     headless Playwright tests
```

Stage art, character art, and backstories each have a lane. See [CONTRIBUTING.md](CONTRIBUTING.md). The story schema is in [content/characters/README.md](content/characters/README.md). The sprite contract is in [art/characters/SPEC.md](art/characters/SPEC.md). The football stage README is the worked example for stage layers.

Only the drummer has painted sprites so far. The other eight fighters draw procedural placeholders in the same frame format until `sheet.png` lands. Their folders are kept with `.gitkeep`. `content/characters/boss.json` is a future boss and is not on the select grid.

## Tests

```
python3 -m http.server 8731
python3 tests/run_tests.py
python3 tests/fallback_test.py
python3 tests/run_tests.py file://$PWD/dist/index.html
```

`tests/run_tests.py` walks the menus and plays CPU-vs-CPU matches. It needs Playwright and Chrome.
