# Contributing

Three people can work in parallel without waiting on the fight engine. Stay in your lane's folders. The ids in [`content/roster.json`](content/roster.json) are the join key between the roster, the backstory files, and the art folders.

| Lane | Put files here | Do not edit |
| --- | --- | --- |
| Stage art | `art/stages/<id>/` and new entries in `content/stages.json` | `src/`, character folders |
| Character art | `art/characters/<id>/` | `src/`, backstory JSON |
| Character backstories | `content/characters/<id>.json` | `src/`, sprite sheets |

The engine will land later in `src/engine/` (with scenes, fighters, audio, and input). The placeholder in `src/main.js` does not import those stubs, so art and story commits will not break the title screen.

Run the page while you work. From the repo root: `python3 -m http.server 8000` or `npx serve . -p 8000`, then open <http://localhost:8000>. Adding a fighter to the roster shows them on the select grid after a reload.

## Shared rules

- PNG only for art. No PSD, no JPEG, no anti-aliasing. Draw with the pencil, nearest neighbor.
- One id, spelled the same everywhere: `drummer`, `xylophone`, `flute`, `tuba`, `trumpet`, `trombone`, `clarinet`, `bassclarinet`, `colorguard`.
- Stages: `football`, `lockerroom`, `fastfood`.
- `.gitkeep` files exist so Git keeps an empty folder. Leave the file in place until a real asset is in that folder. You can delete the `.gitkeep` in the same commit that adds the asset.

## Stage art

Each stage is a folder, `art/stages/<id>/`.

| File | Role |
| --- | --- |
| `far.png` | Opaque backdrop. Covers the whole frame. |
| `mid.png` | Ground and set dressing. Transparency shows `far.png`. |
| `anim_0.png`, `anim_1.png`, … | Optional. Same size as the other layers, transparent, drawn in front of the fighters. Number from 0. |

Native size is **640×360**. The game canvas is **320×180** and the page scales that canvas up with `image-rendering: pixelated`. Stage layers are drawn into the canvas at half size, nearest neighbor, so two stage pixels become one canvas pixel. Paint on a 2×2 grid if a mark has to survive that reduction.

The fighters' floor line is **y=320** in the stage file (canvas y=160). A standing fighter's feet bottom-center sit on that line. The 40 pixels below y=320 are ground in front of the heels. Draw order, back to front: `far.png`, `mid.png`, fighters, then `anim_N.png`.

`football` is the football field at night. `lockerroom` is the locker room. `fastfood` is a generic fast food restaurant. To add a stage, add an object with `id`, `name`, and `description` to the `stages` array in [`content/stages.json`](content/stages.json) and create the matching folder. Leave `native`, `floorY`, and `drawOrder` alone unless the engine contract changes.

## Character art

Each fighter is a folder, `art/characters/<id>/`.

| File | Size | Notes |
| --- | --- | --- |
| `sheet.png` | 576×1120 | Transparent PNG. See the rows below. |
| `sheet.json` | — | Frame map. Already filled in. Keep the names, rows, and frame counts. |
| `portrait.png` | 64×64 | Transparent PNG. Bust for the select screen. |

Frames are **96×112**, **facing right**. Feet (the point that would touch the ground) sit on the **bottom center** of every cell, including jump and KO. Do not leave empty space under the feet. The engine places that point on the floor, or in the air while jumping, and it mirrors the sheet for the left-facing player. Keep poses inside the cell.

The sheet is 6 columns by 10 rows. Shorter moves leave the leftover cells in that row fully transparent.

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

`special` is that fighter's signature. The roster line is the hint: the drummer's shockwave, the xylophone's mallets, the flute as a bash, the color guard's flag, and the horn each brass or woodwind player actually carries.

## Character backstories

Edit the scaffold at `content/characters/<id>.json`. The field list, types, and what to leave blank are in [`content/characters/README.md`](content/characters/README.md). Story fields are empty on purpose. Identity fields (`id`, `name`, `section`, `instrument`) are filled so they match the roster. Change a display name only if you also change `name` in `content/roster.json`. Do not rename an `id`.
