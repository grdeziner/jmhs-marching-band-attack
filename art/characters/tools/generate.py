#!/usr/bin/env python3
"""Generate Band Wars character sheets from procedural pixel-art parts.

Usage:
    python generate.py drummer
    python generate.py --list
    python generate.py drummer --out /path/to/characters

Later fighters register themselves in FIGHTERS and reuse pxart.body parts
plus a palette swap or a new instrument module.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

# Allow running this file from any cwd
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from pxart.body import ANCHOR_X, ANCHOR_Y, FRAME_H, FRAME_W  # noqa: E402
from pxart.canvas import Canvas, nearest_scale, unique_colors  # noqa: E402
from pxart.palette import UNIFORM, hex_list  # noqa: E402
from fighters import drummer as fighter_drummer  # noqa: E402

FIGHTERS = {
    "drummer": fighter_drummer,
}

# Official roster (only drummer is implemented in this pass)
ROSTER = [
    "drummer",
    "xylophone",
    "flute",
    "tuba",
    "trumpet",
    "trombone",
    "clarinet",
    "bassclarinet",
    "colorguard",
]

PREVIEW_BG = (90, 92, 104, 255)  # neutral mid gray-blue, navy and gold both read
PREVIEW_SCALE = 4


def build_sheet(mod) -> tuple[Image.Image, dict, list]:
    anims = mod.ANIMATIONS
    max_frames = max(a[1] for a in anims)
    sheet_w = max_frames * FRAME_W
    sheet_h = len(anims) * FRAME_H
    sheet = Canvas(sheet_w, sheet_h)

    used_colors = []
    anim_map = {}
    for row, (name, nframes, fps, loop) in enumerate(anims):
        for i in range(nframes):
            frame = mod.render_frame(name, i)
            sheet.blit(frame, i * FRAME_W, row * FRAME_H)
            used_colors.extend(c for _, _, c in frame.pixels())
        entry = {
            "row": row,
            "frames": nframes,
            "fps": fps,
            "loop": loop,
        }
        entry.update(mod.animation_boxes(name))
        anim_map[name] = entry

    img = sheet.to_image()
    palette = hex_list(used_colors)
    # Prefer the official uniform order, then any extras actually used
    official = UNIFORM.hex_list()
    ordered = [h for h in official if h in palette]
    ordered += [h for h in palette if h not in ordered]

    meta = {
        "id": mod.ID,
        "name": mod.NAME,
        "instrument": mod.INSTRUMENT,
        "frameWidth": FRAME_W,
        "frameHeight": FRAME_H,
        "anchor": {"x": ANCHOR_X, "y": ANCHOR_Y},
        "facing": "right",
        "scale": 3,
        "scaleFilter": "nearest",
        "background": "transparent",
        "palette": ordered,
        "animations": anim_map,
        "notes": getattr(mod, "NOTES", (
            "3/4 view, facing right. Game flips the sprite for the left side. "
            "Feet sit on the bottom of the frame; anchor is bottom-center "
            f"({ANCHOR_X}, {ANCHOR_Y}). Jump / KO poses stay in the same frame "
            "space — the game moves the entity. Palette is navy + gold + white trim."
        )),
    }
    if getattr(mod, "PROJECTILE", None):
        meta["projectile"] = dict(mod.PROJECTILE)
    return img, meta, ordered


def build_projectile_sheet(mod) -> Image.Image:
    frames = mod.render_projectile_frames()
    fw = mod.PROJECTILE["frameWidth"]
    fh = mod.PROJECTILE["frameHeight"]
    n = len(frames)
    sheet = Canvas(fw * n, fh)
    for i, fr in enumerate(frames):
        sheet.blit(fr, i * fw, 0)
    return sheet.to_image()


def build_preview_gif(mod, path: Path) -> None:
    frames_out = []
    # Brief hold between animations so a reviewer can see the cut
    for name, nframes, fps, loop in mod.ANIMATIONS:
        duration = max(1, int(round(1000 / fps)))
        for i in range(nframes):
            fr = mod.render_frame(name, i).to_image(background=PREVIEW_BG)
            scaled = nearest_scale(fr, PREVIEW_SCALE)
            # PIL GIFs want P mode; keep a consistent palette
            frames_out.append((scaled.convert("RGBA"), duration))
        # one-beat pause on the last frame of each anim
        if frames_out:
            last, d = frames_out[-1]
            frames_out[-1] = (last, d + 120)

    # Convert to palette images with a shared adaptive palette + reserved bg
    # Build a reference image to quantize against
    first = frames_out[0][0]
    # Use a single adaptive palette from the first few frames composited
    sample = Image.new("RGBA", first.size, PREVIEW_BG)
    sample.paste(first, (0, 0))
    pal = sample.convert("P", palette=Image.Palette.ADAPTIVE, colors=48)

    pil_frames = []
    durations = []
    for im, dur in frames_out:
        # composite on solid bg (already done) and quantize to the same pal
        q = im.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE)
        pil_frames.append(q)
        durations.append(dur)

    pal_img = pal.convert("P")
    pil_frames[0].save(
        path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )


def generate(fid: str, out_root: Path) -> Path:
    if fid not in FIGHTERS:
        implemented = ", ".join(FIGHTERS) or "(none)"
        raise SystemExit(
            f"Fighter '{fid}' is not implemented yet. Implemented: {implemented}. "
            f"Full roster: {', '.join(ROSTER)}"
        )
    mod = FIGHTERS[fid]
    dest = out_root / fid
    dest.mkdir(parents=True, exist_ok=True)

    sheet, meta, palette = build_sheet(mod)
    sheet_path = dest / "sheet.png"
    sheet.save(sheet_path)

    portrait = mod.render_portrait().to_image()
    portrait.save(dest / "portrait.png")

    proj = None
    if getattr(mod, "PROJECTILE", None) and hasattr(mod, "render_projectile_frames"):
        proj = build_projectile_sheet(mod)
        proj.save(dest / "projectile.png")

    # 4x nearest-neighbor review sheet
    preview_sheet = nearest_scale(sheet, PREVIEW_SCALE)
    preview_sheet.save(dest / "preview_sheet_4x.png")

    build_preview_gif(mod, dest / "preview.gif")

    meta["files"] = {
        "sheet": "sheet.png",
        "portrait": "portrait.png",
        "preview": "preview.gif",
        "previewSheet4x": "preview_sheet_4x.png",
    }
    if proj is not None:
        meta["files"]["projectile"] = "projectile.png"
    (dest / "sheet.json").write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Wrote {dest}")
    print(f"  sheet {sheet.size[0]}x{sheet.size[1]}  palette {len(palette)} colors")
    print(f"  portrait {portrait.size[0]}x{portrait.size[1]}")
    if proj is not None:
        print(f"  projectile {proj.size[0]}x{proj.size[1]}")
    print(f"  colors: {', '.join(palette)}")
    return dest


def main():
    ap = argparse.ArgumentParser(description="Generate Band Wars character art")
    ap.add_argument("fighter", nargs="?", help="fighter id, e.g. drummer")
    ap.add_argument("--list", action="store_true", help="list roster")
    ap.add_argument(
        "--out",
        type=Path,
        default=TOOLS.parent,
        help="characters/ output root (default: ../)",
    )
    args = ap.parse_args()
    if args.list or not args.fighter:
        print("Roster:")
        for fid in ROSTER:
            flag = "ready" if fid in FIGHTERS else "planned"
            print(f"  {fid:16} {flag}")
        if not args.fighter:
            if args.list:
                return
            ap.error("fighter id required (try: python3 generate.py drummer)")
    if args.fighter == "all":
        for fid in FIGHTERS:
            generate(fid, args.out)
        return
    generate(args.fighter, args.out)


if __name__ == "__main__":
    main()
