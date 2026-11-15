# Contributing

Three lanes can move without rewriting the fight. The ids in [`content/roster.json`](content/roster.json) are the join key between the roster, the backstory files, and the art folders.

| Lane | Put files here | Leave alone |
| --- | --- | --- |
| Stage art | `art/stages/<id>/` and, for a new stage, an entry in `content/stages.json` plus `audio/music/<id>.js` | `src/`, character folders |
| Character art | `art/characters/<id>/` | `src/`, backstory JSON |
| Character backstories | `content/characters/<id>.json` | `src/`, sprite sheets |

The engine lives in `src/` (`fight.js`, `fighter.js`, `moves.js`, `ai.js`, `scenes.js`, and the rest). Art and story files are data. After you add or replace an asset, run `node build.js` from the repo root. That refreshes `dist/index.html` and `content/files.json`. The dev page only requests files named in `content/files.json`, so a new PNG is invisible until that rebuild.

Run the page while you work. From the repo root: `python3 -m http.server 8000` or `npx serve . -p 8000`, then open <http://localhost:8000>. `dist/index.html` also opens straight from disk.

## Shared rules

- PNG only for art that ships in the game. No PSD, no JPEG, no anti-aliasing. Draw with the pencil, nearest neighbor. Partial alpha is not used (0 or 255).
- One id, spelled the same everywhere: `drummer`, `xylophone`, `flute`, `tuba`, `trumpet`, `trombone`, `clarinet`, `bassclarinet`, `colorguard`.
- Stages: `football`, `lockerroom`, `fastfood`.
- `.gitkeep` holds a fighter folder that has no sprites yet. Leave it until the same commit adds `sheet.png`. Do not commit `audio/music/previews/` or any `.wav` / `.ogg`. Songs ship as JS modules.
- The canvas is **640×360** and the page scales it up. Fighter feet stand on **y=320**.

## Stage art

Each stage is `art/stages/<id>/`. [`art/stages/football/README.md`](art/stages/football/README.md) is the worked example. `python3 generate.py` in a stage folder redraws that stage when Pillow is installed.

| File | Size | Role |
| --- | --- | --- |
| `far.png` | 640×360, opaque | Backdrop, locked to the camera. |
| `mid.png` | 960×360 | Ground and set. Transparent sky shows `far.png`. 160 px of parallax on each side. |
| `anim_0.png` … `anim_3.png` | 960×360, transparent | Overlays aligned to `mid.png`. They cycle at about 7 fps and are drawn in front of the fighters. |

The floor line, where a standing fighter's feet bottom-center sit, is **y=320**. Keep the band from y=300 to y=360 as simple ground. Draw order, back to front: `far.png`, `mid.png`, fighters, then the anim frames.

`football` is the football field at night. `lockerroom` is the locker room. `fastfood` is a generic fast food restaurant. To add a stage, add `{ id, name, subtitle, musicFile }` to `content/stages.json`, create the art folder, and add `audio/music/<id>.js` in the same shape as the existing songs (`bpm`, `loop`, `channels`).

## Character art

Each fighter is `art/characters/<id>/`. The full contract is [`art/characters/SPEC.md`](art/characters/SPEC.md). `art/characters/drummer/` is the painted reference. Everyone else is procedural until `sheet.png` exists, and a missing animation row falls back the same way.

| File | Size | Notes |
| --- | --- | --- |
| `sheet.png` | 576×1120 | Transparent. One row per move, 6 columns, 96×112 cells. |
| `sheet.json` | — | Frame map. Copy the drummer file and edit it. |
| `portrait.png` | 64×64 | Transparent bust for the select and VS screens. |
| `projectile.png` | — | Optional strip. Describe it under `projectile` in `sheet.json`. |

Frames face **right**. The anchor is the bottom center of the cell, default `{ "x": 48, "y": 111 }`. The engine mirrors the sheet for the left-facing player and moves the whole sprite for jumps and knockback, so do not leave empty space under the feet and do not bake jump height into the cell.

| Row | Name | Frames |
| --- | --- | --- |
| 0 | idle | 4 |
| 1 | walk | 6 |
| 2 | jump | 4 |
| 3 | crouch | 2 |
| 4 | block | 2 |
| 5 | punch | 3 |
| 6 | kick | 4 |
| 7 | special | 6 |
| 8 | hit | 2 |
| 9 | ko | 4 |

`special` is that fighter's signature (the drummer's shockwave, the xylophone's mallets, the flute as a bash, the color guard's flag, and the horn each player carries). Gameplay supers are tuned in `content/roster.json`, not as an extra sheet row.

## Character backstories

Edit `content/characters/<id>.json`. The field list is in [`content/characters/README.md`](content/characters/README.md). Those files are already written; change the prose there, and keep [`content/story.md`](content/story.md) in step if you want the readable copy to match. Display names in the story file override the roster. Do not rename an `id`.

`boss.json` (Major Discord) is not on the select grid. Nothing loads it yet.
