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

from pxart.body import (  # noqa: E402
    ANCHOR_X,
    ANCHOR_Y,
    EDGE_MARGIN,
    FRAME_H,
    FRAME_W,
    POSE_ORIGIN_X,
)
from pxart.canvas import Canvas, nearest_scale, unique_colors  # noqa: E402
from pxart.palette import UNIFORM, hex_list  # noqa: E402
from px16.palette import PAL as PAL16, hex_list as hex_list16, hex_of as hex_of16  # noqa: E402
from fighters import drummer as fighter_drummer  # noqa: E402
from fighters import xylophone as fighter_xylophone  # noqa: E402
from fighters import flute as fighter_flute  # noqa: E402
from fighters import tuba as fighter_tuba  # noqa: E402
from fighters import colorguard as fighter_colorguard  # noqa: E402
from fighters import trumpet as fighter_trumpet  # noqa: E402
from fighters import trombone as fighter_trombone  # noqa: E402
from fighters import clarinet as fighter_clarinet  # noqa: E402
from fighters import bassclarinet as fighter_bassclarinet  # noqa: E402

FIGHTERS = {
    "drummer": fighter_drummer,
    "xylophone": fighter_xylophone,
    "flute": fighter_flute,
    "tuba": fighter_tuba,
    "trumpet": fighter_trumpet,
    "trombone": fighter_trombone,
    "clarinet": fighter_clarinet,
    "bassclarinet": fighter_bassclarinet,
    "colorguard": fighter_colorguard,
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


def shift_anim_boxes(entry: dict, dx: int) -> dict:
    """Move hurt/hit/block boxes from 96-wide authoring space into frame space."""
    if not dx:
        return entry
    out = dict(entry)
    for key in ("hurtbox", "hitbox", "blockbox"):
        box = out.get(key)
        if isinstance(box, dict) and "x" in box:
            box = dict(box)
            box["x"] = int(box["x"]) + dx
            out[key] = box
    return out


def scan_frame_margins(frame: Canvas, margin: int = EDGE_MARGIN) -> dict:
    """Count opaque pixels on the left/right/top edges and inside the margin.

    The bottom of the frame is the ground line and is not checked.
    Returns {edge: {side: count}, margin: {side: count}}.
    """
    edge = {"left": 0, "right": 0, "top": 0}
    pad = {"left": 0, "right": 0, "top": 0}
    w, h = frame.w, frame.h
    for y in range(h):
        for x in range(w):
            if margin <= x < w - margin and y >= margin:
                continue
            col = frame.get(x, y)
            if col is None or col[3] == 0:
                continue
            if x == 0:
                edge["left"] += 1
            elif x < margin:
                pad["left"] += 1
            if x == w - 1:
                edge["right"] += 1
            elif x >= w - margin:
                pad["right"] += 1
            if y == 0:
                edge["top"] += 1
            elif y < margin:
                pad["top"] += 1
    return {"edge": edge, "margin": pad}


def format_margin_report(violations: list) -> str:
    lines = []
    for anim, i, kind, side, count in violations:
        lines.append(f"  {anim}[{i}]  {kind} {side}: {count} px")
    return "\n".join(lines)


def validate_fighter_frames(mod, margin: int = EDGE_MARGIN) -> list:
    """Render every animation frame and record margin/edge violations."""
    found = []
    for name, nframes, _fps, _loop in mod.ANIMATIONS:
        for i in range(nframes):
            frame = mod.render_frame(name, i)
            if frame.w != FRAME_W or frame.h != FRAME_H:
                found.append((name, i, "size", f"{frame.w}x{frame.h}", 1))
                continue
            result = scan_frame_margins(frame, margin)
            for kind in ("edge", "margin"):
                for side, count in result[kind].items():
                    if count:
                        found.append((name, i, kind, side, count))
    return found


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
        # 16-bit modules are authored in 128-wide frame space already.
        dx = 0 if getattr(mod, "SHIFT_BOXES", True) is False else POSE_ORIGIN_X
        entry = shift_anim_boxes(entry, dx)
        anim_map[name] = entry

    img = sheet.to_image()
    palette = hex_list(used_colors)
    if getattr(mod, "LOOK_16BIT", False):
        # Official 15-color order, then any stray extras (should be none after enforce)
        used = set(palette)
        official16 = [hex_of16(c) for c in PAL16]
        ordered = [h for h in official16 if h in used]
        ordered += [h for h in palette if h not in ordered]
    else:
        # Prefer the official uniform order, then any extras actually used
        official = UNIFORM.hex_list()
        ordered = [h for h in official if h in palette]
        ordered += [h for h in palette if h not in official]

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
    if getattr(mod, "SUPER", None):
        meta["super"] = dict(mod.SUPER)
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


def build_super_sheet(mod) -> Image.Image:
    frames = mod.render_super_frames()
    fw = mod.SUPER["frameWidth"]
    fh = mod.SUPER["frameHeight"]
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



def count_opaque_image(img: Image.Image) -> int:
    """Exact unique opaque RGB count on a PIL image (alpha > 0)."""
    seen = set()
    px = img.convert("RGBA").load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a:
                seen.add((r, g, b))
    return len(seen)


def build_compare_image(mod, dest: Path, sheet: Image.Image, portrait: Image.Image, path: Path) -> None:
    """4x side-by-side of 8-bit backup idle 0 + portrait vs the new 16-bit ones."""
    from PIL import ImageDraw, ImageFont

    backup_root = TOOLS.parent.parent / "characters_8bit_backup" / mod.ID
    old_sheet_path = backup_root / "sheet.png"
    old_port_path = backup_root / "portrait.png"
    if not old_sheet_path.exists():
        print(f"  compare skipped: no backup sheet at {old_sheet_path}")
        return

    fw, fh = FRAME_W, FRAME_H
    old_sheet = Image.open(old_sheet_path).convert("RGBA")
    old_idle = old_sheet.crop((0, 0, fw, fh))
    new_idle = sheet.crop((0, 0, fw, fh))
    old_port = Image.open(old_port_path).convert("RGBA") if old_port_path.exists() else Image.new("RGBA", (64, 64))

    scale = PREVIEW_SCALE
    bg = PREVIEW_BG
    pad = 16
    label_h = 28
    idle_w, idle_h = fw * scale, fh * scale
    # portraits at 4x too (64*4 = 256)
    port_w, port_h = old_port.size[0] * scale, old_port.size[1] * scale
    col_w = max(idle_w, port_w)
    # two columns (8-bit | 16-bit), two rows (idle | portrait)
    canvas_w = pad * 3 + col_w * 2
    canvas_h = label_h + pad * 3 + idle_h + port_h
    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg)
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
        font_s = font

    def paste_scaled(src, x, y, tw, th):
        scaled = src.resize((tw, th), Image.Resampling.NEAREST)
        canvas.paste(scaled, (x, y), scaled)

    x8 = pad
    x16 = pad * 2 + col_w
    draw.text((x8, 6), "8-bit (backup)", fill=(230, 230, 236, 255), font=font)
    draw.text((x16, 6), "16-bit (SF2 Turbo)", fill=(255, 241, 160, 255), font=font)

    y_idle = label_h + pad
    paste_scaled(old_idle, x8, y_idle, idle_w, idle_h)
    paste_scaled(new_idle, x16, y_idle, idle_w, idle_h)
    draw.text((x8, y_idle + idle_h - 18), "idle[0]  4x", fill=(200, 200, 208, 255), font=font_s)
    draw.text((x16, y_idle + idle_h - 18), "idle[0]  4x", fill=(200, 200, 208, 255), font=font_s)

    y_port = y_idle + idle_h + pad
    # center portraits in the column
    paste_scaled(old_port, x8 + (col_w - port_w) // 2, y_port, port_w, port_h)
    new_port = portrait.convert("RGBA")
    nw, nh = new_port.size[0] * scale, new_port.size[1] * scale
    paste_scaled(new_port, x16 + (col_w - nw) // 2, y_port, nw, nh)
    draw.text((x8 + (col_w - port_w) // 2, y_port + port_h + 2), "portrait  4x", fill=(200, 200, 208, 255), font=font_s)
    draw.text((x16 + (col_w - nw) // 2, y_port + nh + 2), "portrait  4x", fill=(200, 200, 208, 255), font=font_s)

    canvas.save(path)
    print(f"  compare {canvas.size[0]}x{canvas.size[1]} -> {path.name}")


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

    violations = validate_fighter_frames(mod)
    edges = [v for v in violations if v[2] == "edge"]
    margins = [v for v in violations if v[2] == "margin"]
    sizes = [v for v in violations if v[2] == "size"]
    if violations:
        print(f"MARGIN VALIDATION  {fid}  {FRAME_W}x{FRAME_H}  margin={EDGE_MARGIN}px")
        if edges:
            print(f"  EDGE TOUCHES ({len(edges)} frames) — opaque pixels on left/right/top edge:")
            print(format_margin_report(edges))
        if margins:
            print(f"  MARGIN ({len(margins)} frames) — opaque pixels inside the {EDGE_MARGIN}px pad:")
            print(format_margin_report(margins))
        if sizes:
            print("  FRAME SIZE mismatches:")
            print(format_margin_report(sizes))
    else:
        print(f"MARGIN VALIDATION  {fid}  {FRAME_W}x{FRAME_H}  margin={EDGE_MARGIN}px  OK")

    sheet, meta, palette = build_sheet(mod)
    sheet_path = dest / "sheet.png"
    sheet.save(sheet_path)

    portrait = mod.render_portrait().to_image()
    portrait.save(dest / "portrait.png")

    portrait_large = None
    if hasattr(mod, "render_portrait_large"):
        portrait_large = mod.render_portrait_large().to_image()
        portrait_large.save(dest / "portrait_large.png")

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
    if portrait_large is not None:
        meta["files"]["portraitLarge"] = "portrait_large.png"
    if proj is not None:
        meta["files"]["projectile"] = "projectile.png"

    super_img = None
    if getattr(mod, "SUPER", None) and hasattr(mod, "render_super_frames"):
        super_img = build_super_sheet(mod)
        super_img.save(dest / "super.png")
        meta["files"]["super"] = "super.png"

    if getattr(mod, "BUILD_COMPARE", False):
        cmp_path = dest / "compare_8bit_vs_16bit.png"
        build_compare_image(mod, dest, sheet, portrait, cmp_path)
        meta["files"]["compare8bitVs16bit"] = "compare_8bit_vs_16bit.png"

    opaque_count = count_opaque_image(sheet)
    meta["opaqueColorCount"] = opaque_count

    (dest / "sheet.json").write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Wrote {dest}")
    print(f"  sheet {sheet.size[0]}x{sheet.size[1]}  unique opaque colors: {opaque_count}  palette list {len(palette)}")
    print(f"  portrait {portrait.size[0]}x{portrait.size[1]}")
    if portrait_large is not None:
        print(f"  portrait_large {portrait_large.size[0]}x{portrait_large.size[1]}")
    if proj is not None:
        print(f"  projectile {proj.size[0]}x{proj.size[1]}")
    if super_img is not None:
        print(f"  super {super_img.size[0]}x{super_img.size[1]}")
    print(f"  colors: {', '.join(palette)}")
    if edges or sizes:
        # Edge touches mean the sheet would clip in-engine. Warn loudly.
        # --strict turns this into a hard failure after the files are written
        # so the report is still on disk for review.
        print(f"  WARNING: {len(edges)+len(sizes)} frame(s) have pixels on the frame edge (or a size mismatch).")
        if getattr(generate, "_strict", False):
            raise SystemExit(f"strict margin check failed for {fid}")
    return dest


def main():
    ap = argparse.ArgumentParser(description="Generate Band Wars character art")
    ap.add_argument("fighter", nargs="?", help="fighter id, e.g. drummer")
    ap.add_argument("--list", action="store_true", help="list roster")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero if any opaque pixel touches a frame edge",
    )
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
    generate._strict = bool(args.strict)
    if args.fighter == "all":
        for fid in FIGHTERS:
            generate(fid, args.out)
        return
    generate(args.fighter, args.out)


if __name__ == "__main__":
    main()
