"""Shared marching-band body parts and pose helpers.

Fighters reuse these limbs, the shako/head, jacket, pants, gloves and shoes.
A fighter module supplies a pose (joint positions) plus any instrument, and
composites parts back-to-front with per-part 1px outlines.
"""

from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple

from .canvas import Canvas, auto_outline
from .palette import (
    BLUSH,
    DHEAD,
    DHEAD_DK,
    DHEAD_SH,
    GOLD,
    GOLD_DK,
    GOLD_LT,
    HAIR,
    MOUTH,
    NAVY,
    NAVY_DK,
    NAVY_LT,
    OUTLINE,
    SHOE,
    SHOE_LT,
    SKIN,
    SKIN_DK,
    SKIN_LT,
    WHITE,
    WHITE_DK,
    WHITE_SH,
    WOOD,
    WOOD_DK,
    WOOD_LT,
    shade,
)

FRAME_W = 128
FRAME_H = 112
ANCHOR_X = 64
ANCHOR_Y = 111  # ground line / bottom-center of the feet
# Poses were authored in a 96-wide frame (anchor x=48). They are shifted
# into the 128-wide frame so joints sit on the new bottom-center.
POSE_ORIGIN_X = 16
# Opaque pixels must stay this many pixels inside the left, right, and top
# edges (the generator validates this). The bottom is the ground line.
EDGE_MARGIN = 2

# Joint / prop keys that live in frame pixel space (used by the origin shift).
POSE_POINT_KEYS = (
    "face", "sh_l", "sh_r", "el_l", "el_r", "hd_l", "hd_r",
    "hip", "hip_l", "hip_r", "kn_l", "kn_r", "an_l", "an_r",
    "toe_l", "toe_r", "inst", "mal_l", "mal_r",
)


def shift_pose_to_frame(pose: "Pose") -> "Pose":
    """Return a copy of `pose` with joints shifted into 128-wide frame space."""
    p = pose.copy()
    dx = POSE_ORIGIN_X
    if not dx:
        return p
    for k in POSE_POINT_KEYS:
        v = getattr(p, k, None)
        if v is not None:
            setattr(p, k, (v[0] + dx, v[1]))
    return p


def ang(deg: float) -> Tuple[float, float]:
    """Screen-space unit vector. 0° = right, 90° = down, 180° = left, 270° = up."""
    r = math.radians(deg)
    return math.cos(r), math.sin(r)


def off(x, y, deg: float, dist: float) -> Tuple[float, float]:
    vx, vy = ang(deg)
    return x + vx * dist, y + vy * dist


@dataclass
class Pose:
    """Joint positions in frame pixels. Facing right, 3/4 view."""

    face: Tuple[float, float] = (47, 28)
    # shoulders / arms
    sh_l: Tuple[float, float] = (36, 44)
    sh_r: Tuple[float, float] = (58, 44)
    el_l: Tuple[float, float] = (28, 58)
    el_r: Tuple[float, float] = (66, 58)
    hd_l: Tuple[float, float] = (30, 70)
    hd_r: Tuple[float, float] = (68, 70)
    # hips / legs
    hip: Tuple[float, float] = (47, 70)
    hip_l: Tuple[float, float] = (40, 70)
    hip_r: Tuple[float, float] = (54, 70)
    kn_l: Tuple[float, float] = (38, 88)
    kn_r: Tuple[float, float] = (56, 88)
    an_l: Tuple[float, float] = (36, 104)
    an_r: Tuple[float, float] = (58, 104)
    # feet: ankle is the heel area; toe points right by default
    toe_l: Optional[Tuple[float, float]] = None
    toe_r: Optional[Tuple[float, float]] = None
    # instrument hook (optional; fighters fill these in)
    inst: Tuple[float, float] = (56, 62)
    inst_rx: float = 20
    inst_ry: float = 18
    inst_depth: float = 8
    # mallet / prop heads (optional)
    mal_l: Optional[Tuple[float, float]] = (24, 62)
    mal_r: Optional[Tuple[float, float]] = (74, 62)
    expression: str = "idle"
    struck: bool = False
    flash: bool = False
    # which hand is drawn in front of the instrument (both, right, left, none)
    hands_over: str = "both"
    # extra lean / squash
    squash_y: float = 1.0
    # 0, 90, -90, 180 — 90-degree head tilts used by KO / trips
    head_rot: int = 0

    def copy(self, **kw) -> "Pose":
        d = deepcopy(self)
        for k, v in kw.items():
            setattr(d, k, v)
        return d

    look: Optional["Look"] = None

    def toes(self):
        tl = self.toe_l or (self.an_l[0] + 12, self.an_l[1] + 5)
        tr = self.toe_r or (self.an_r[0] + 14, self.an_r[1] + 5)
        return tl, tr


@dataclass
class Look:
    """Per-fighter colors and body-type scales. Defaults match the drummer uniform."""

    skin: tuple = SKIN
    skin_dk: tuple = SKIN_DK
    skin_lt: tuple = SKIN_LT
    hair: tuple = HAIR
    plume: tuple = GOLD
    plume_lt: tuple = GOLD_LT
    plume_dk: tuple = GOLD_DK
    limb: float = 1.0
    torso: float = 1.0
    shoe: float = 1.0
    head: float = 1.0
    glove: float = 1.0
    jaw: float = 1.0
    neck: float = 1.0
    female: bool = False
    hat: str = "shako"  # "shako" or "none"
    hair_style: str = "temples"  # temples, bun, pony, short
    sleeves: bool = True
    gloves: bool = True
    shoes: str = "marching"  # marching | jazz

    def hair_shade(self):
        return shade(self.hair, 1.35), self.hair, shade(self.hair, 0.55)


DEFAULT_LOOK = Look()


def get_look(pose=None, look=None) -> Look:
    if look is not None:
        return look
    if pose is not None and getattr(pose, "look", None) is not None:
        return pose.look
    return DEFAULT_LOOK


def new_layer() -> Canvas:
    return Canvas(FRAME_W, FRAME_H)


def outlined(layer: Canvas) -> Canvas:
    return auto_outline(layer, OUTLINE, connectivity=8)


# ---------------------------------------------------------------------------
# Shoes
# ---------------------------------------------------------------------------

def draw_shoe(c: Canvas, ankle, toe, near: bool = True, look: Look = None) -> None:
    look = get_look(look=look)
    ax, ay = float(ankle[0]), float(ankle[1])
    tx, ty = float(toe[0]), float(toe[1])
    vx, vy = tx - ax, ty - ay
    leng = math.hypot(vx, vy) or 1.0
    ux, uy = vx / leng, vy / leng
    # perpendicular (screen down-ish for a sole offset)
    px, py = -uy, ux
    if py < 0:
        px, py = -px, -py
    # Heel sits slightly behind the ankle, toe at `toe`.
    hx, hy = ax - ux * 3.0, ay - uy * 0.5
    # Upper
    mid_x = (hx + tx) / 2
    mid_y = (hy + ty) / 2 - (1.0 if near else 0.6)
    sc = look.shoe
    jazz = look.shoes == "jazz"
    rx = max(7.5 if not jazz else 5.5, leng * (0.52 if not jazz else 0.46) + 2.0) * sc
    ry = ((4.4 if near else 3.8) if not jazz else (3.2 if near else 2.8)) * sc
    c.shade_ellipse(mid_x, mid_y, rx, ry, SHOE, SHOE_LT, OUTLINE, light_dir=(-0.5, -0.9))
    # Toe box
    c.shade_disk(tx - ux * 1.2, ty - uy * 1.2 - 0.6, 3.4 if near else 2.9, SHOE, SHOE_LT, OUTLINE, light_dir=(-0.2, -0.95))
    # Heel cap
    c.shade_disk(hx, hy - 0.4, 2.6 if near else 2.2, SHOE, SHOE_LT, OUTLINE)
    # Flat sole: a dark slab along the bottom of the shoe
    sole_hx, sole_hy = hx + px * 2.2, hy + py * 2.2
    sole_tx, sole_ty = tx + px * 2.2, ty + py * 2.2
    c.taper_capsule(sole_hx, sole_hy, sole_tx, sole_ty, 1.6, 1.4, OUTLINE)
    c.taper_capsule(
        hx + px * 1.2, hy + py * 1.2,
        tx + px * 1.2, ty + py * 1.2,
        1.2, 1.0, SHOE,
    )
    # instep highlight + tiny lace
    c.set(int(round(ax + ux * 3)), int(round(ay - 2)), SHOE_LT)
    c.set(int(round(ax + ux * 2)), int(round(ay - 1)), GOLD_DK)


def draw_shoes(c: Canvas, pose: Pose) -> None:
    tl, tr = pose.toes()
    look = get_look(pose)
    draw_shoe(c, pose.an_l, tl, near=False, look=look)
    draw_shoe(c, pose.an_r, tr, near=True, look=look)


# ---------------------------------------------------------------------------
# Legs (navy pants, gold side stripe)
# ---------------------------------------------------------------------------

def _paint_stripe(c: Canvas, x1, y1, x2, y2, r, outward_sign: int) -> None:
    vx, vy = x2 - x1, y2 - y1
    leng = math.hypot(vx, vy) or 1
    # perpendicular, pick the side pointing outward (left = -x, right = +x)
    px, py = -vy / leng, vx / leng
    # choose the perpendicular that points more in outward_sign of X
    if px * outward_sign < 0:
        px, py = -px, -py
    steps = int(leng) + 1
    for i in range(steps):
        t = i / max(1, steps - 1)
        x = x1 + vx * t + px * (r - 1.2)
        y = y1 + vy * t + py * (r - 1.2)
        c.set(int(round(x)), int(round(y)), GOLD)
        c.set(int(round(x + px)), int(round(y + py * 0.3)), GOLD_LT if t < 0.5 else GOLD)


def draw_leg(c: Canvas, hip, knee, ankle, near: bool, outward: int, look: Look = None) -> None:
    look = get_look(look=look)
    s = look.limb
    r_hip = (8.2 if near else 7.4) * s
    r_knee = (6.6 if near else 6.0) * s
    r_ank = (4.8 if near else 4.4) * s
    c.shade_taper(hip[0], hip[1], knee[0], knee[1], r_hip, r_knee, NAVY, NAVY_LT, NAVY_DK)
    c.shade_taper(knee[0], knee[1], ankle[0], ankle[1], r_knee, r_ank, NAVY, NAVY_LT, NAVY_DK)
    # knee volume
    c.shade_disk(knee[0], knee[1], r_knee - 0.4, NAVY, NAVY_LT, NAVY_DK)
    _paint_stripe(c, hip[0], hip[1], knee[0], knee[1], r_hip * 0.85, outward)
    _paint_stripe(c, knee[0], knee[1], ankle[0], ankle[1], r_knee * 0.85, outward)


def draw_legs(c: Canvas, pose: Pose) -> None:
    look = get_look(pose)
    draw_leg(c, pose.hip_l, pose.kn_l, pose.an_l, near=False, outward=-1, look=look)
    draw_leg(c, pose.hip_r, pose.kn_r, pose.an_r, near=True, outward=1, look=look)


# ---------------------------------------------------------------------------
# Torso / jacket, collar, epaulets, cross-belt
# ---------------------------------------------------------------------------

def draw_neck(c: Canvas, pose: Pose) -> None:
    look = get_look(pose)
    fx, fy = pose.face
    n = 4.2 * look.neck * look.head
    nx, ny = fx - 0.5, fy + 10
    c.shade_taper(fx - 0.5, fy + 6, nx, ny + 4, n, n + 0.8, look.skin, look.skin_lt, look.skin_dk)


def draw_torso(c: Canvas, pose: Pose) -> None:
    """High-collar navy jacket, gold braid, white cross-belt. Heavy build."""
    shx = (pose.sh_l[0] + pose.sh_r[0]) / 2
    shy = (pose.sh_l[1] + pose.sh_r[1]) / 2
    hx, hy = pose.hip
    # torso as a thick tapered capsule from mid-shoulder to hips, plus chest volume
    look = get_look(pose)
    shoulder_w = abs(pose.sh_r[0] - pose.sh_l[0])
    r_sh = max(14.0, shoulder_w * 0.42) * look.torso
    r_hip = 12.0 * look.torso
    c.shade_taper(shx, shy + 1, hx, hy + 2, r_sh, r_hip, NAVY, NAVY_LT, NAVY_DK)
    # chest fill (wider oval)
    c.shade_ellipse(shx + 1, shy + 10, r_sh + 1, 11, NAVY, NAVY_LT, NAVY_DK)

    # epaulets (gold pads on each shoulder)
    for (sx, sy), sign in ((pose.sh_l, -1), (pose.sh_r, 1)):
        c.shade_ellipse(sx + sign * 1, sy - 1, 7.5, 3.6, GOLD, GOLD_LT, GOLD_DK)
        # fringe ticks
        for k in range(-3, 4):
            c.set(int(sx + k * 1.6 + sign), int(sy + 2), GOLD_DK)
            c.set(int(sx + k * 1.6 + sign), int(sy + 3), GOLD)

    # high collar — two wing shapes around the neck, gold inner edge
    fx, fy = pose.face
    collar_y = fy + 11
    # left wing
    c.shade_ellipse(fx - 6, collar_y, 5.5, 5.0, NAVY, NAVY_LT, NAVY_DK)
    c.shade_ellipse(fx + 5.5, collar_y, 5.5, 5.0, NAVY, NAVY_LT, NAVY_DK)
    # gold inner trim
    c.ellipse(fx - 4.2, collar_y - 0.5, 3.2, 3.2, GOLD, fill=True)
    c.ellipse(fx + 3.8, collar_y - 0.5, 3.2, 3.2, GOLD, fill=True)
    # skin hole already drawn by neck; punch a little skin so collar looks open at the front
    c.shade_ellipse(fx + 0.2, collar_y - 1, 2.4, 2.8, look.skin, look.skin_lt, look.skin_dk)

    # white cross-belt (baldric) from left shoulder to right hip
    c.shade_taper(
        pose.sh_l[0] + 2,
        pose.sh_l[1] - 1,
        hx + 8,
        hy + 2,
        2.4,
        2.6,
        WHITE,
        WHITE,
        WHITE_SH,
    )
    # belt plate
    c.shade_ellipse(shx + 2, shy + 12, 3.2, 2.6, GOLD, GOLD_LT, GOLD_DK)

    # a couple of gold buttons peeking on the left chest (right side covered by drum)
    for i, (bx, by) in enumerate(((shx - 6, shy + 8), (shx - 5, shy + 14))):
        c.disk(bx, by, 1.3, GOLD)
        c.set(int(bx), int(by), GOLD_LT)


# ---------------------------------------------------------------------------
# Arms, gloves
# ---------------------------------------------------------------------------

def draw_upper_arm(c: Canvas, sh, el, near: bool, look: Look = None) -> None:
    look = get_look(look=look)
    s = look.limb
    r1 = (6.4 if near else 5.8) * s
    r2 = (5.4 if near else 5.0) * s
    if look.sleeves:
        mid, lt, dk = NAVY, NAVY_LT, NAVY_DK
    else:
        mid, lt, dk = look.skin, look.skin_lt, look.skin_dk
    c.shade_taper(sh[0], sh[1], el[0], el[1], r1, r2, mid, lt, dk)
    c.shade_disk(el[0], el[1], r2 - 0.2, mid, lt, dk)
    if not look.sleeves:
        # gold cap-sleeve / armband at the shoulder
        c.shade_disk(sh[0], sh[1] + 1, r1 * 0.85, GOLD, GOLD_LT, GOLD_DK)


def draw_forearm(c: Canvas, el, hand, near: bool, look: Look = None) -> None:
    look = get_look(look=look)
    s = look.limb
    r1 = (5.2 if near else 4.8) * s
    r2 = (4.4 if near else 4.0) * s
    if look.sleeves:
        mid, lt, dk = NAVY, NAVY_LT, NAVY_DK
    else:
        mid, lt, dk = look.skin, look.skin_lt, look.skin_dk
    c.shade_taper(el[0], el[1], hand[0], hand[1], r1, r2, mid, lt, dk)
    # gold cuff just before the glove
    vx, vy = hand[0] - el[0], hand[1] - el[1]
    leng = math.hypot(vx, vy) or 1
    # cuff center is ~8px back from the hand
    t = max(0.0, 1.0 - 8.0 / leng)
    cx = el[0] + vx * t
    cy = el[1] + vy * t
    c.shade_disk(cx, cy, r2 + 0.6, GOLD, GOLD_LT, GOLD_DK)
    # white pip on cuff
    c.set(int(cx), int(cy - 1), WHITE)


def draw_glove(c: Canvas, hand, mallet_head, near: bool = True, look: Look = None) -> None:
    look = get_look(look=look)
    hx, hy = hand
    r = (5.6 if near else 5.1) * look.glove
    if look.gloves:
        mid, lt, dk = WHITE, WHITE, WHITE_SH
    else:
        mid, lt, dk = look.skin, look.skin_lt, look.skin_dk
        r *= 0.85
    c.shade_disk(hx, hy, r, mid, lt, dk)
    # thumb — toward the mallet or slightly up-right
    if mallet_head is not None:
        mx, my = mallet_head
        vx, vy = mx - hx, my - hy
        leng = math.hypot(vx, vy) or 1
        # perpendicular thumb
        tx, ty = -vy / leng, vx / leng
        # pick the upward-ish side
        if ty > 0:
            tx, ty = -tx, -ty
        c.shade_disk(hx + tx * 4.2 * look.glove, hy + ty * 4.2 * look.glove, 2.4 * look.glove, mid, lt, dk)
    else:
        c.shade_disk(hx + 3, hy - 3, 2.4 * look.glove, mid, lt, dk)
    # simple knuckle dents
    c.set(int(hx + 1), int(hy + 1), dk)
    c.set(int(hx - 1), int(hy + 2), dk)
    if not look.gloves:
        # gold wrist cuff already painted on the forearm; a thin gold band on the wrist
        c.shade_ellipse(hx, hy + r * 0.6, r * 0.7, 1.4, GOLD, GOLD_LT, GOLD_DK)


def draw_arm(
    c: Canvas,
    sh,
    el,
    hand,
    mallet_head,
    near: bool,
    include_glove: bool = True,
    look: Look = None,
) -> None:
    look = get_look(look=look)
    draw_upper_arm(c, sh, el, near, look=look)
    draw_forearm(c, el, hand, near, look=look)
    if include_glove:
        draw_glove(c, hand, mallet_head, near, look=look)


# ---------------------------------------------------------------------------
# Head, face, shako, plume
# ---------------------------------------------------------------------------

def _face_features(c: Canvas, fx: float, fy: float, expression: str, look: Look = None) -> None:
    """Pixel-level features. (fx, fy) is the face center."""
    look = get_look(look=look)
    brow_c = look.hair
    ix, iy = int(round(fx)), int(round(fy))

    # brows + eyes + mouth change with expression
    # 3/4 view: right eye a little more visible, left slightly smaller / back
    lx, rx = ix - 5, ix + 4
    ey = iy - 1

    def brow(x, y, shape="flat"):
        col = brow_c
        if shape == "flat":
            c.hline(x - 2, x + 2, y, col)
            c.set(x - 2, y + 1, col)
        elif shape == "down":  # angry / grit / yell
            c.set(x - 2, y - 1, col)
            c.set(x - 1, y, col)
            c.set(x, y, col)
            c.set(x + 1, y + 1, col)
            c.set(x + 2, y + 1, col)
        elif shape == "up":  # hit / surprise
            c.set(x - 2, y + 1, col)
            c.set(x - 1, y, col)
            c.set(x, y - 1, col)
            c.set(x + 1, y, col)
            c.set(x + 2, y + 1, col)
        elif shape == "ko":
            c.hline(x - 2, x + 2, y, col)

    def eye_open(x, y, wide=False):
        # white + dark iris + highlight
        c.set(x - 1, y, WHITE)
        c.set(x, y, WHITE)
        c.set(x + 1, y, WHITE)
        if wide:
            c.set(x - 1, y - 1, WHITE)
            c.set(x, y - 1, WHITE)
            c.set(x + 1, y - 1, WHITE)
        c.set(x, y, HAIR)
        c.set(x + 1, y, HAIR)
        c.set(x - 1, y, NAVY_DK)  # iris hint
        c.set(x, y - 1 if wide else y, WHITE)  # catchlight reused if needed
        c.set(x - 1, y, WHITE)
        c.set(x, y, HAIR)
        c.set(x + 1, y, HAIR)
        c.set(x + 1, y - 1, WHITE) if wide else None

    def eye_open2(x, y, wide=False):
        # clearer 2-row eye
        c.set(x - 1, y, WHITE)
        c.set(x, y, WHITE)
        c.set(x + 1, y, WHITE)
        c.set(x - 1, y + 1, WHITE_SH)
        c.set(x, y + 1, HAIR)
        c.set(x + 1, y + 1, HAIR)
        if wide:
            c.set(x, y - 1, WHITE)
            c.set(x - 1, y - 1, WHITE)
        c.set(x - 1, y, WHITE)
        c.set(x, y, HAIR)  # pupil
        c.set(x + 1, y, WHITE)
        # lower lid
        c.set(x - 1, y + 1, SKIN_DK)
        c.set(x + 1, y + 1, SKIN_DK)

    def eye_shut(x, y):
        c.set(x - 2, y, HAIR)
        c.set(x - 1, y + 1, HAIR)
        c.set(x, y + 1, HAIR)
        c.set(x + 1, y + 1, HAIR)
        c.set(x + 2, y, HAIR)

    def eye_x(x, y):
        c.set(x - 1, y - 1, HAIR)
        c.set(x, y, HAIR)
        c.set(x + 1, y + 1, HAIR)
        c.set(x + 1, y - 1, HAIR)
        c.set(x - 1, y + 1, HAIR)

    brow_y = ey - 3
    if expression in ("idle", "focus"):
        brow(lx, brow_y, "flat")
        brow(rx, brow_y, "flat")
        eye_open2(lx, ey)
        eye_open2(rx, ey, wide=False)
    elif expression in ("yell", "grit"):
        brow(lx, brow_y + 1, "down")
        brow(rx, brow_y + 1, "down")
        eye_open2(lx, ey, wide=True)
        eye_open2(rx, ey, wide=True)
    elif expression == "hit":
        brow(lx, brow_y, "up")
        brow(rx, brow_y, "up")
        eye_shut(lx, ey)
        eye_shut(rx, ey)
    elif expression == "ko":
        brow(lx, brow_y, "ko")
        brow(rx, brow_y, "ko")
        eye_x(lx, ey)
        eye_x(rx, ey)
    else:
        brow(lx, brow_y, "flat")
        brow(rx, brow_y, "flat")
        eye_open2(lx, ey)
        eye_open2(rx, ey)

    # nose (3/4, toward the right)
    nx, ny = ix + 2, iy + 3
    c.set(nx, ny, SKIN_DK)
    c.set(nx + 1, ny, SKIN_DK)
    c.set(nx + 1, ny + 1, SKIN_DK)
    c.set(nx, ny - 1, SKIN_LT)

    # blush — one muted pixel per cheek (darker skin, not a bright pink blob)
    if expression not in ("ko",):
        blush = shade(look.skin, 0.78)
        c.set(ix - 6, iy + 3, blush)
        c.set(ix + 6, iy + 3, blush)

    # mouth
    mx, my = ix + 1, iy + 7
    if expression == "idle":
        # confident slight smirk to the right
        c.set(mx - 1, my, SKIN_DK)
        c.set(mx, my, MOUTH)
        c.set(mx + 1, my, MOUTH)
        c.set(mx + 2, my - 1, MOUTH)
    elif expression == "focus":
        c.hline(mx - 1, mx + 2, my, HAIR)
    elif expression == "yell":
        # open shout
        c.set(mx - 2, my - 1, MOUTH)
        c.hline(mx - 2, mx + 3, my, HAIR)
        c.hline(mx - 1, mx + 2, my + 1, HAIR)
        c.hline(mx - 1, mx + 2, my, WHITE)  # teeth
        c.set(mx - 1, my + 1, MOUTH)
        c.set(mx, my + 1, MOUTH)
        c.set(mx + 1, my + 1, MOUTH)
        c.set(mx + 2, my, HAIR)
    elif expression == "grit":
        c.hline(mx - 2, mx + 3, my, HAIR)
        c.hline(mx - 1, mx + 2, my, WHITE)
        c.hline(mx - 2, mx + 3, my + 1, MOUTH)
    elif expression == "hit":
        c.set(mx - 1, my, MOUTH)
        c.set(mx, my + 1, MOUTH)
        c.set(mx + 1, my + 1, MOUTH)
        c.set(mx + 2, my, MOUTH)
    elif expression == "ko":
        c.ellipse(mx + 0.5, my + 1, 3.2, 2.4, HAIR, fill=True)
        c.ellipse(mx + 0.5, my + 1, 2.0, 1.3, MOUTH, fill=True)


def draw_plume(c: Canvas, top_x: float, top_y: float, look: Look = None) -> None:
    """A small feather plume — a stem with offset barbs, not a gold spike."""
    look = get_look(look=look)
    mid, lt, dk = look.plume, look.plume_lt, look.plume_dk
    # socket + quill
    c.shade_disk(top_x, top_y + 1.2, 1.7, GOLD, GOLD_LT, GOLD_DK)
    # Tip sits this many pixels above the socket. Clamp also accounts for
    # barb radii, the raster pad, and a 1px auto_outline so the plume
    # stays inside EDGE_MARGIN when a pose lifts the head.
    tip = 8
    clearance = 11  # tip + barb + outline
    if top_y - clearance < EDGE_MARGIN:
        top_y = top_y + (EDGE_MARGIN - (top_y - clearance))
    c.taper_capsule(top_x, top_y + 1, top_x + 1.4, top_y - tip + 2, 0.7, 0.5, dk)
    # paired barbs left and right of the quill, tapering toward the tip
    barbs = [
        # (dx, dy, rx, ry)
        (-2.2, -1.2, 2.4, 1.6),
        ( 2.4, -1.5, 2.2, 1.5),
        (-2.4, -2.8, 2.2, 1.6),
        ( 2.6, -3.1, 2.2, 1.5),
        (-2.0, -4.4, 1.9, 1.5),
        ( 2.8, -4.7, 1.8, 1.4),
        (-1.6, -5.8, 1.5, 1.3),
        ( 2.6, -6.1, 1.4, 1.2),
        ( 0.4, -7.2, 1.2, 1.1),
        ( 2.0, -7.8, 1.0, 1.0),
    ]
    for dx, dy, rx, ry in barbs:
        c.shade_ellipse(top_x + dx, top_y + dy, rx, ry, mid, lt, dk, light_dir=(-0.65, -0.35))
    # a couple of separated tip wisps
    c.set(int(round(top_x + 0.0)), int(round(top_y - tip)), lt)
    c.set(int(round(top_x + 2.0)), int(round(top_y - tip)), mid)
    c.set(int(round(top_x - 1.0)), int(round(top_y - tip + 1)), mid)
    c.set(int(round(top_x + 3.0)), int(round(top_y - tip + 1)), lt)


def draw_shako(c: Canvas, fx: float, fy: float) -> Tuple[float, float]:
    """Tall navy shako with a thin gold band. Face stays visible under the brim.

    Returns the plume socket (x, y).
    """
    hx = fx + 0.0
    # Keep the hat ABOVE the brows (brows sit near fy-4).
    bottom = fy - 8          # underside of the gold band
    top = bottom - 15        # crown

    def _half_w(y: float) -> float:
        # slight taper: 11.4 at the brim, 9.4 at the crown
        t = 0.0 if bottom == top else (bottom - y) / (bottom - top)
        return 11.4 - 2.0 * max(0.0, min(1.0, t))

    # Navy cylinder, pixel-shaded, left side lighter
    y0, y1 = int(round(top)), int(round(bottom))
    for y in range(y0, y1 + 1):
        hw = _half_w(y)
        x0 = int(round(hx - hw))
        x1 = int(round(hx + hw))
        width = max(1, x1 - x0)
        for x in range(x0, x1 + 1):
            u = (x - x0) / width  # 0 left .. 1 right
            if u < 0.22:
                col = NAVY_LT
            elif u > 0.78:
                col = NAVY_DK
            else:
                col = NAVY
            c.set(x, y, col)

    # Rounded crown cap
    c.shade_ellipse(hx, top + 1.2, 9.6, 3.2, NAVY, NAVY_LT, NAVY_DK)
    # Flat top + thin gold rim
    c.shade_ellipse(hx, top + 0.6, 9.2, 2.2, NAVY_LT, GOLD_LT, NAVY)
    c.ellipse(hx, top + 0.8, 9.2, 2.0, GOLD, fill=False)
    c.hline(int(hx - 6), int(hx + 6), int(top), GOLD_LT)

    # Thin gold brim-band (2 px, not a visor plate)
    band_y = int(round(bottom))
    hw_b = _half_w(bottom)
    x0 = int(round(hx - hw_b))
    x1 = int(round(hx + hw_b))
    c.hline(x0, x1, band_y - 1, GOLD_LT)
    c.hline(x0 - 1, x1 + 1, band_y, GOLD)
    c.hline(x0, x1, band_y + 1, GOLD_DK)

    # Small dark visor / brim jutting forward-right, under the band
    visor_y = band_y + 2
    c.hline(int(hx - 2), int(hx + 11), visor_y, NAVY_DK)
    c.hline(int(hx + 2), int(hx + 10), visor_y + 1, OUTLINE)
    # just a couple of pixels of thickness on the right
    c.set(int(hx + 11), visor_y, OUTLINE)
    c.set(int(hx + 10), visor_y + 1, NAVY_DK)

    # Front badge on the navy body, well above the band
    bx, by = hx + 2, (top + bottom) / 2 + 0.5
    c.shade_ellipse(bx, by, 2.8, 3.2, GOLD, GOLD_LT, GOLD_DK)
    c.set(int(round(bx)), int(round(by - 1)), WHITE)
    c.set(int(round(bx)), int(round(by)), GOLD_LT)
    # tiny chevron
    c.set(int(round(bx)), int(round(by + 1)), NAVY_DK)
    c.set(int(round(bx - 1)), int(round(by)), NAVY_DK)
    c.set(int(round(bx + 1)), int(round(by)), NAVY_DK)

    return (hx + 0.5, top - 0.2)


def draw_hair(c: Canvas, fx, fy, look: Look, hs: float) -> None:
    """Hair that is visible without a shako, or temple hair under a shako.

    For bun / pony (hair up) the hair stays on the crown and back so the
    3/4 face — forehead, brows, eyes, nose, mouth — stays clearly visible.
    """
    h_lt, h_mid, h_dk = look.hair_shade()
    style = look.hair_style
    if look.hat == "shako" or style == "temples":
        # solid hair color under a shako (no extra shade tones)
        c.shade_ellipse(fx - 9 * hs, fy - 2, 2.8 * hs, 4.0 * hs, h_mid, h_mid, h_mid)
        c.shade_ellipse(fx + 9 * hs, fy - 1, 2.2 * hs, 3.2 * hs, h_mid, h_mid, h_mid)
        if look.hat == "shako":
            return
    if style == "short":
        c.shade_ellipse(fx, fy - 7 * hs, 10.5 * hs, 5.5 * hs, h_mid, h_lt, h_dk)
        c.shade_ellipse(fx - 10 * hs, fy - 2, 3.0 * hs, 4.0 * hs, h_mid, h_lt, h_dk)
        c.shade_ellipse(fx + 10 * hs, fy - 2, 2.6 * hs, 3.6 * hs, h_mid, h_lt, h_dk)
        return
    if style in ("bun", "pony"):
        # Crown / back only. Hairline sits ABOVE the brows (brows are at fy-4).
        # Do not cover the forehead or the eye line.
        c.shade_ellipse(fx - 1 * hs, fy - 9.5 * hs, 10.2 * hs, 5.2 * hs, h_mid, h_lt, h_dk)
        # volume behind the far ear (left), not over the cheek
        c.shade_ellipse(fx - 11 * hs, fy - 3, 3.2 * hs, 4.4 * hs, h_mid, h_lt, h_dk)
        # a slim temple tick on the right, above the eye
        c.shade_ellipse(fx + 10 * hs, fy - 5, 2.2 * hs, 2.6 * hs, h_mid, h_lt, h_dk)
        # high bun on top / slightly back
        bx, by = fx - 1 * hs, fy - 16 * hs
        c.shade_ellipse(bx, by, 6.2 * hs, 5.6 * hs, h_mid, h_lt, h_dk)
        # gold scrunchie at the bun base (still above the forehead)
        c.shade_ellipse(fx - 0.5 * hs, fy - 11.5 * hs, 3.4 * hs, 1.6 * hs, GOLD, GOLD_LT, GOLD_DK)
        if style == "pony":
            c.shade_taper(bx + 2, by - 3, bx + 6, by - 10, 3.0 * hs, 1.6 * hs, h_mid, h_lt, h_dk)
        return
    # default loose cap (shouldn't cover the face plate; draw_head clears it)
    c.shade_ellipse(fx, fy - 7 * hs, 10.5 * hs, 6.0 * hs, h_mid, h_lt, h_dk)


def draw_head(c: Canvas, pose: Pose) -> None:
    look = get_look(pose)
    fx, fy = pose.face
    hs = look.head
    # ear (left / far side)
    c.shade_ellipse(fx - 11 * hs, fy + 1, 2.6 * hs, 3.4 * hs, look.skin, look.skin_lt, look.skin_dk)
    # skull
    c.shade_ellipse(fx, fy + 1, 11.0 * hs, 12.0 * hs, look.skin, look.skin_lt, look.skin_dk)
    # jaw — heavier for tuba, softer for female
    j = look.jaw
    c.shade_ellipse(fx + 0.5, fy + 6 * hs, 9.5 * hs * (0.92 if look.female else 1.0) * j,
                    7.5 * hs * j, look.skin, look.skin_lt, look.skin_dk)

    if look.hat == "shako":
        draw_hair(c, fx, fy, look, hs)
        socket = draw_shako(c, fx, fy)
        draw_plume(c, socket[0], socket[1], look=look)
        by = int(fy - 7)
        c.set(int(fx - 11), by, GOLD)
        c.set(int(fx - 10), by + 1, GOLD_DK)
        c.set(int(fx + 11), by, GOLD)
        c.set(int(fx + 10), by + 1, GOLD_DK)
    else:
        # hair first (crown / bun / back), then re-stamp the face so the
        # forehead and features are never buried in a hair mass.
        draw_hair(c, fx, fy, look, hs)
        c.shade_ellipse(fx, fy + 1, 10.2 * hs, 11.0 * hs, look.skin, look.skin_lt, look.skin_dk)
        c.shade_ellipse(fx + 0.5, fy + 6 * hs,
                        9.2 * hs * (0.92 if look.female else 1.0) * look.jaw,
                        7.2 * hs * look.jaw,
                        look.skin, look.skin_lt, look.skin_dk)
        # keep the far ear on top of the side hair
        c.shade_ellipse(fx - 11 * hs, fy + 1, 2.6 * hs, 3.4 * hs, look.skin, look.skin_lt, look.skin_dk)

    _face_features(c, fx, fy, pose.expression, look=look)


# ---------------------------------------------------------------------------
# Composite a standard uniform body (no instrument). Depth order is the
# caller's responsibility; these helpers each paint onto a provided canvas
# or return an outlined layer.
# ---------------------------------------------------------------------------


def draw_guard_torso(c: Canvas, pose: Pose) -> None:
    """Sleek color-guard costume: sleeveless navy bodice, gold V-sash, short skirt."""
    look = get_look(pose)
    shx = (pose.sh_l[0] + pose.sh_r[0]) / 2
    shy = (pose.sh_l[1] + pose.sh_r[1]) / 2
    hx, hy = pose.hip
    r_sh = max(11.0, abs(pose.sh_r[0] - pose.sh_l[0]) * 0.38) * look.torso
    r_waist = 8.5 * look.torso
    r_hip = 11.0 * look.torso
    # fitted bodice, slightly nipped at the waist
    mid_y = (shy + hy) / 2
    c.shade_taper(shx, shy + 1, shx, mid_y, r_sh, r_waist, NAVY, NAVY_LT, NAVY_DK)
    c.shade_taper(shx, mid_y, hx, hy + 3, r_waist, r_hip, NAVY, NAVY_LT, NAVY_DK)
    # gold V-sash from left shoulder to right hip
    c.shade_taper(pose.sh_l[0] + 2, pose.sh_l[1], hx + 7, hy + 1, 2.0, 2.4, GOLD, GOLD_LT, GOLD_DK)
    # gold waistband
    c.shade_ellipse(shx, mid_y + 2, r_waist + 1.5, 2.0, GOLD, GOLD_LT, GOLD_DK)
    # short skirt flare over the hips
    c.shade_ellipse(shx, hy + 4, r_hip + 4, 6.5, NAVY, NAVY_LT, NAVY_DK)
    c.hline(int(shx - r_hip - 3), int(shx + r_hip + 3), int(hy + 8), GOLD)
    # neckline — scoop, skin showing
    c.shade_ellipse(shx, shy + 3, 5.0, 4.0, look.skin, look.skin_lt, look.skin_dk)
    # gold neck trim
    c.ellipse(shx, shy + 3, 5.4, 4.4, GOLD, fill=False)


def layer_and_outline(draw_fn) -> Canvas:
    c = new_layer()
    draw_fn(c)
    return outlined(c)
