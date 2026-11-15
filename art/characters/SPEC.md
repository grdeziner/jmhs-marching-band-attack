# Band Wars — Character Sprite Spec

Shared art contract for all nine fighters. Drop files in `art/characters/<id>/`.
The running game draws each frame at its native **96×112** on the **640×360**
canvas. The page scales that canvas up with nearest-neighbor filtering.
`scale: 3` in `sheet.json` is preview metadata; the engine does not multiply
the sprite by 3. Feet sit on the stage floor at **y=320**.

School colors are **navy + gold with white trim** unless a fighter brief says
otherwise.


## Frame & space

| Property        | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| Native frame    | **96 × 112 px**                                                       |
| On-screen size  | Native 96×112 on the 640×360 canvas. The page scales the canvas.     |
| Background      | Fully transparent                                                     |
| Facing          | **Right**. The game flips the sprite horizontally for the left side.  |
| Feet / anchor   | Bottom-center of the frame. See `anchor` in each `sheet.json`.        |
| Default anchor  | `{ "x": 48, "y": 111 }` — last row of the frame is the ground line.   |
| Outline         | Dark 1 px outline around each major form                              |
| Shading         | Simple 2–3 tone, no antialiasing, no dither                           |
| Palette size    | About 16–24 colors per fighter, NES/SNES-inspired                     |

Jump, hit and KO frames **stay in the same 96×112 box**. The feet may leave
the ground line in those poses; the game moves the entity (jump arc, knockback,
fall). Do not bake a jump-height offset into the sprite that would double up
with gameplay motion.

Authoring previews (the `preview.gif` and `preview_sheet_4x.png` next to each
fighter) are scaled **4×** nearest-neighbor for review only. They are not used
in-game.


## Uniform base

Every fighter starts from the same marching-band uniform, built so later
characters can reuse body parts and palette-swap:

- Shako (tall hat) with a gold plume
- High-collar navy jacket with gold braid / epaulets
- White cross-belt (baldric) and white gloves
- Navy pants with a gold side stripe
- Black shoes

Colorguard may later drop or restyle parts of this base if a brief says so;
until then, use the same uniform.

The shared palette lives in `tools/pxart/palette.py` (`UNIFORM`). Fighters
may add a few instrument-specific colors but should stay in the 16–24 range.


## Roster

Files for each fighter live in `art/characters/<id>/`.

| id             | Planned role                                              |
|----------------|-----------------------------------------------------------|
| `drummer`      | Percussion / marching bass drum. Heavy. Mallets + shockwave special. |
| `xylophone`    | Marching xylophone / bells.                               |
| `flute`        | Flute.                                                    |
| `tuba`         | Tuba. Heaviest brass.                                     |
| `trumpet`      | Trumpet.                                                  |
| `trombone`     | Trombone.                                                 |
| `clarinet`     | Clarinet.                                                 |
| `bassclarinet` | Bass clarinet.                                            |
| `colorguard`   | Color guard (flag / rifle). Same uniform base until told otherwise. |


## Per-fighter files

```
characters/<id>/
  sheet.png              sprite sheet, one row per animation
  sheet.json             frame map + metadata (see below)
  portrait.png           64 × 64 select-screen bust, native
  projectile.png         optional effect / projectile strip
  preview.gif            review only: all anims cycling at 4× on a neutral bg
  preview_sheet_4x.png   review only: the whole sheet at 4× nearest-neighbor
```

`projectile.png` is omitted only if the fighter has no projectile or spawned
effect. When it exists, describe it in `sheet.json` under `projectile`.


## Animation sheet layout

One **row per animation**, in this exact order. Rows with fewer frames leave
the unused cells on the right **transparent**. Sheet width is
`max(frame counts) × 96` (currently 6 × 96 = 576). Sheet height is
`10 × 112 = 1120`.

| Row | Name      | Frames | Suggested fps | Loop   | Notes                                      |
|-----|-----------|--------|---------------|--------|--------------------------------------------|
| 0   | `idle`    | 4      | 6             | yes    | Breathing / weight shift                   |
| 1   | `walk`    | 6      | 10            | yes    | March step; contact on frames 0 and 3      |
| 2   | `jump`    | 4      | 10            | no     | Crouch-launch, rise, apex, fall            |
| 3   | `crouch`  | 2      | 8             | yes    | Held crouch; loop as a crouch idle         |
| 4   | `block`   | 2      | 8             | yes    | Held block; loop as a block idle           |
| 5   | `punch`   | 3      | 12            | no     | Windup, active, recover                    |
| 6   | `kick`    | 4      | 12            | no     | Chamber, extend, active, recover           |
| 7   | `special` | 6      | 10            | no     | Fighter-specific super                     |
| 8   | `hit`     | 2      | 10            | no     | Reaction, stumble                          |
| 9   | `ko`      | 4      | 8             | no     | Knockback through lying on the ground      |

Active frames (the ones that should deal hit) are marked in `sheet.json` with
an optional `hitbox` (`frames` is a list of **0-based** indices in that row).


## `sheet.json` format

```json
{
  "id": "drummer",
  "name": "Marcus \"Thunder\" Boone",
  "instrument": "Marching Bass Drum",
  "frameWidth": 96,
  "frameHeight": 112,
  "anchor": { "x": 48, "y": 111 },
  "facing": "right",
  "scale": 3,
  "scaleFilter": "nearest",
  "background": "transparent",
  "palette": ["#0A0B10", "#0C1734", "#17305F"],
  "animations": {
    "idle": {
      "row": 0,
      "frames": 4,
      "fps": 6,
      "loop": true,
      "hurtbox": { "x": 26, "y": 10, "w": 52, "h": 101 }
    },
    "punch": {
      "row": 5,
      "frames": 3,
      "fps": 12,
      "loop": false,
      "hurtbox": { "x": 24, "y": 10, "w": 54, "h": 101 },
      "hitbox": { "frames": [1], "x": 78, "y": 36, "w": 16, "h": 18 }
    }
  },
  "projectile": {
    "file": "projectile.png",
    "frameWidth": 80,
    "frameHeight": 64,
    "frames": 6,
    "fps": 12,
    "loop": false,
    "anchor": { "x": 6, "y": 32 },
    "notes": "Spawn on special frame index 3, origin at the instrument, travelling right."
  },
  "notes": "Free-form production notes for the integrator.",
  "files": {
    "sheet": "sheet.png",
    "portrait": "portrait.png",
    "projectile": "projectile.png"
  }
}
```

Conventions:

- Boxes are `{x, y, w, h}` in **frame pixel** space, top-left origin.
- `hurtbox` is a single AABB that covers the body for that animation (good
  enough to start; per-frame boxes can be added later).
- `hitbox.frames` lists the active frame indices of that animation.
- `projectile.anchor` is the registration point of **each projectile frame**
  (for the drummer, left-center, so it can be placed on the front of the drum).
- `palette` is the hex list of colors actually used, outline first.


## Portrait

- **64 × 64 px** native, no upscale.
- Bust shot: head, shako, shoulders, a hint of the instrument.
- Street Fighter II select-screen flavor: readable face, chunky silhouette.
- Border-friendly background: a flat navy field with a darker 2 px edge and
  inset gold corner ticks, so a UI frame can sit on the edge without clipping
  important pixels. Leave a 2 px margin around the bust.


## Style notes

- Street Fighter II proportions: big hands and feet, strong silhouettes,
  readable poses even at a glance.
- 3/4 view, not a strict side profile, so faces and instruments stay clear.
- Chunky shapes over thin lines. No stick figures, no antialiased edges.
- Instruments should read as part of the silhouette (the drummer’s bass drum
  is a shield as much as a weapon).
- Light comes from the upper left. Highlights are one step up, shadows one
  step down, plus the shared dark outline.


## Generator

Procedural, reusable, pixel-by-pixel / layered parts:

```
characters/tools/generate.py          CLI
characters/tools/pxart/canvas.py      pixel canvas, capsules, ellipses, outline
characters/tools/pxart/palette.py     shared UNIFORM palette
characters/tools/pxart/body.py        shako, head, jacket, limbs, gloves, shoes
characters/tools/fighters/<id>.py     instrument + all animation poses
```

```bash
cd /workspace/band-wars/art/characters/tools
python generate.py drummer
python generate.py --list
```

Requires Pillow. New fighters should add a module under `fighters/`, register
it in `generate.py`’s `FIGHTERS` dict, and reuse `pxart.body` parts plus a
palette swap or a new instrument drawer.


## Judgment calls (this pass)

- 3/4 view rather than a flat side-view, following SF2’s readable faces.
- Anchor sits on the last pixel row (`y: 111`) just under the soles, so the
  integrator can plant the sprite on a ground line without a 1 px sink.
- Crouch and block **loop**; they are held states. Attacks, jump, hit, and KO
  do not.
- The drummer’s bass drum is navy with gold hoops and a white head (uniform-
  coordinated, not a bare brass shell).
- The drummer’s display name in `sheet.json` is the official roster name,
  Marcus "Thunder" Boone. The folder/id stays `drummer`.
- Colorguard is listed with the same uniform base until a later brief says
  otherwise.
