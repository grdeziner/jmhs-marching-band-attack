"""Percussion / marching bass drummer — first Band Wars fighter.

Big heavy build, bass drum strapped to the front, fights with mallets.
Special: a sound shockwave blast from the drum (see projectile strip).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from PIL import Image

from pxart.body import (
    ANCHOR_X,
    ANCHOR_Y,
    FRAME_H,
    FRAME_W,
    Pose,
    draw_arm,
    draw_glove,
    draw_head,
    draw_legs,
    draw_neck,
    draw_shoes,
    draw_torso,
    layer_and_outline,
    new_layer,
    off,
)
from pxart.canvas import Canvas, auto_outline
from pxart.palette import (
    DHEAD,
    DHEAD_DK,
    DHEAD_SH,
    FLASH,
    GOLD,
    GOLD_DK,
    GOLD_LT,
    NAVY,
    NAVY_DK,
    NAVY_LT,
    OUTLINE,
    UNIFORM,
    WHITE,
    WHITE_SH,
    WOOD,
    WOOD_DK,
    WOOD_LT,
)

ID = "drummer"
NAME = "Marcus \"Thunder\" Boone"
INSTRUMENT = "Marching Bass Drum"

ANIMATIONS = [
    # name, frames, fps, loop
    ("idle", 4, 6, True),
    ("walk", 6, 10, True),
    ("jump", 4, 10, False),
    ("crouch", 2, 8, True),
    ("block", 2, 8, True),
    ("punch", 3, 12, False),
    ("kick", 4, 12, False),
    ("special", 6, 10, False),
    ("hit", 2, 10, False),
    ("ko", 4, 8, False),
]

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 80,
    "frameHeight": 64,
    "frames": 6,
    "fps": 12,
    "loop": False,
    "anchor": {"x": 6, "y": 32},
    "notes": (
        "Expanding sound-shockwave blast. Spawn on special frame index 3 "
        "(the mallet slam), origin at the front of the bass drum, travelling right."
    ),
}


# ---------------------------------------------------------------------------
# Instrument
# ---------------------------------------------------------------------------

def _ring(c: Canvas, cx, cy, rx, ry, inner, mid, light, dark) -> None:
    cx, cy, rx, ry = float(cx), float(cy), float(rx), float(ry)
    x0, x1 = int(cx - rx - 1), int(cx + rx + 1)
    y0, y1 = int(cy - ry - 1), int(cy + ry + 1)
    for y in range(y0, y1 + 1):
        dy = ((y + 0.5) - cy) / (ry + 0.45)
        for x in range(x0, x1 + 1):
            dx = ((x + 0.5) - cx) / (rx + 0.45)
            d = dx * dx + dy * dy
            if inner <= d <= 1.08:
                # shade by light dir
                ndot = dx * (-0.45) + dy * (-0.7)
                if ndot > 0.25:
                    c.set(x, y, light)
                elif ndot < -0.2:
                    c.set(x, y, dark)
                else:
                    c.set(x, y, mid)


def draw_bass_drum(c: Canvas, pose: Pose) -> None:
    cx, cy = pose.inst
    rx, ry = pose.inst_rx, pose.inst_ry
    depth = pose.inst_depth

    # Back / left shell: a slightly smaller ellipse offset to the left,
    # then fill the cylinder wall between back and front.
    back_x = cx - depth
    # wall: for each y of the drum, fill x from back ellipse-left to front.
    x0 = int(back_x - rx - 2)
    x1 = int(cx + rx + 2)
    y0 = int(cy - ry - 2)
    y1 = int(cy + ry + 2)
    for y in range(y0, y1 + 1):
        # find left edge of back ellipse and left edge of front, fill wall
        back_xs = []
        front_xs = []
        for x in range(x0, x1 + 1):
            dyb = ((y + 0.5) - cy) / (ry + 0.45)
            dxb = ((x + 0.5) - back_x) / (rx + 0.45)
            if dxb * dxb + dyb * dyb <= 1.0:
                back_xs.append(x)
            dxf = ((x + 0.5) - cx) / (rx + 0.45)
            if dxf * dxf + dyb * dyb <= 1.0:
                front_xs.append(x)
        if not back_xs or not front_xs:
            continue
        # cylinder wall is the span from the back's leftmost to the front's leftmost
        wall_l = min(back_xs)
        wall_r = min(front_xs)
        for x in range(wall_l, wall_r + 1):
            # shade: top is lighter, bottom darker, mid navy
            t = ((y + 0.5) - (cy - ry)) / (2 * ry + 0.001)
            if t < 0.22:
                col = NAVY_LT
            elif t > 0.78:
                col = NAVY_DK
            else:
                col = NAVY
            c.set(x, y, col)

    # back hoop (visible as a gold ellipse peek on the left)
    _ring(c, back_x, cy, rx, ry, 0.86, GOLD, GOLD_LT, GOLD_DK)

    # front drum head
    if pose.struck:
        c.shade_ellipse(cx, cy, rx, ry, WHITE, FLASH, DHEAD_SH, light_dir=(-0.3, -0.7))
    else:
        c.shade_ellipse(cx, cy, rx, ry, DHEAD, WHITE, DHEAD_SH, light_dir=(-0.4, -0.7))

    # inner concentric rings so it reads as a drum head
    _ring(c, cx, cy, rx * 0.62, ry * 0.62, 0.84, DHEAD_SH, DHEAD, DHEAD_DK)
    # gold front hoop
    _ring(c, cx, cy, rx, ry, 0.86, GOLD, GOLD_LT, GOLD_DK)

    # tension lugs around the hoop
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        lx = cx + math.cos(rad) * (rx - 1.2)
        ly = cy + math.sin(rad) * (ry - 1.2)
        c.disk(lx, ly, 1.35, GOLD_DK)
        c.set(int(round(lx)), int(round(ly)), GOLD_LT)

    # center emblem: gold diamond / lyre hint
    c.shade_ellipse(cx + 0.5, cy, 4.2, 4.2, GOLD, GOLD_LT, GOLD_DK)
    c.shade_ellipse(cx + 0.5, cy, 2.2, 2.2, NAVY, NAVY_LT, NAVY_DK)
    c.set(int(cx), int(cy), GOLD_LT)
    c.set(int(cx + 1), int(cy), GOLD)

    if pose.flash:
        # impact burst at the strike point (slightly right of center)
        c.shade_disk(cx + 4, cy - 2, 6, FLASH, WHITE, GOLD_LT)
        c.shade_disk(cx + 4, cy - 2, 3, WHITE, FLASH, GOLD)


def draw_harness(c: Canvas, pose: Pose) -> None:
    """Shoulder straps from the drum up over each shoulder."""
    cx, cy = pose.inst
    top = cy - pose.inst_ry + 2
    # left strap to left shoulder
    c.shade_taper(
        pose.sh_l[0] + 1,
        pose.sh_l[1] - 3,
        cx - 8,
        top,
        2.1,
        2.3,
        WHITE,
        WHITE,
        WHITE_SH,
    )
    # right strap
    c.shade_taper(
        pose.sh_r[0] - 1,
        pose.sh_r[1] - 3,
        cx + 4,
        top,
        2.1,
        2.3,
        WHITE,
        WHITE,
        WHITE_SH,
    )
    # small gold clips at the drum
    c.disk(cx - 8, top, 1.6, GOLD)
    c.disk(cx + 4, top, 1.6, GOLD)


def draw_mallet(c: Canvas, hand, head, shaft_only: bool = False, head_only: bool = False) -> None:
    if hand is None or head is None:
        return
    hx, hy = hand
    mx, my = head
    vx, vy = mx - hx, my - hy
    leng = math.hypot(vx, vy) or 1
    # extend a short butt past the glove
    bx = hx - vx / leng * 5
    by = hy - vy / leng * 5
    if not head_only:
        c.shade_taper(bx, by, mx, my, 1.7, 1.4, WOOD, WOOD_LT, WOOD_DK)
        # a second darker core so the shaft stays readable against gloves / drum
        c.taper_capsule(bx, by, mx, my, 0.8, 0.7, WOOD_DK)
    if not shaft_only:
        # fluffy bass-mallet head
        c.shade_disk(mx, my, 5.2, WHITE, WHITE, WHITE_SH)
        c.shade_disk(mx, my, 3.0, WHITE_SH, WHITE, WHITE_SH)
        # navy wrapping band
        # a short band perpendicular to the shaft, near the neck of the head
        nx = mx - vx / leng * 3.2
        ny = my - vy / leng * 3.2
        c.shade_disk(nx, ny, 2.4, NAVY, NAVY_LT, NAVY_DK)


# ---------------------------------------------------------------------------
# Base idle pose + animation variants
# ---------------------------------------------------------------------------

def idle_base() -> Pose:
    return Pose(
        face=(47, 36),
        sh_l=(35, 50),
        sh_r=(61, 50),
        el_l=(24, 58),
        el_r=(74, 57),
        hd_l=(32, 62),
        hd_r=(78, 61),
        hip=(47, 74),
        hip_l=(40, 74),
        hip_r=(54, 74),
        kn_l=(36, 90),
        kn_r=(58, 89),
        an_l=(33, 104),
        an_r=(58, 104),
        toe_l=(46, 109),
        toe_r=(74, 109),
        inst=(56, 64),
        inst_rx=20,
        inst_ry=17.5,
        inst_depth=9,
        # keep ~14px of visible wood between glove and mallet head
        mal_l=(22, 48),
        mal_r=(88, 46),
        expression="idle",
        hands_over="both",
    )


def _shift(p: Pose, keys, dx=0, dy=0) -> None:
    for k in keys:
        x, y = getattr(p, k)
        setattr(p, k, (x + dx, y + dy))


def _shift_upper(p: Pose, dx=0, dy=0) -> None:
    _shift(
        p,
        [
            "face",
            "sh_l",
            "sh_r",
            "el_l",
            "el_r",
            "hd_l",
            "hd_r",
            "hip",
            "hip_l",
            "hip_r",
            "inst",
        ],
        dx,
        dy,
    )
    if p.mal_l:
        p.mal_l = (p.mal_l[0] + dx, p.mal_l[1] + dy)
    if p.mal_r:
        p.mal_r = (p.mal_r[0] + dx, p.mal_r[1] + dy)


def pose_idle(i: int) -> Pose:
    p = idle_base()
    # breathing / drum bounce: 0,1,2,3 = up, mid, down, mid
    bob = [0, 1, 2, 1][i]
    mal_bob = [0, -1, 0, 1][i]  # light mallet tap
    _shift_upper(p, dy=bob)
    # slight mallet motion (a soft preparatory bounce)
    p.mal_l = (p.mal_l[0], p.mal_l[1] + mal_bob)
    p.mal_r = (p.mal_r[0], p.mal_r[1] - mal_bob)
    # tiny weight shift
    if i in (1, 2):
        _shift(p, ["an_r", "toe_r"], dx=0, dy=0)
    return p


def pose_walk(i: int) -> Pose:
    p = idle_base()
    # Two-step march. Contact frames 0 and 3 sit lower; passing frames rise.
    # bounce of the whole upper body + drum
    bounce = [1, -1, 0, 1, -1, 0][i]
    _shift_upper(p, dy=bounce)

    # Right leg (forward on 0, passing back on 3)
    # Left leg opposite
    # keypoints relative to idle
    # R: fwd contact, plant, push, back toe-off, passing (knee up), reach
    r_kn = [(62, 86), (58, 88), (50, 90), (48, 92), (54, 78), (64, 84)]
    r_an = [(64, 104), (60, 104), (48, 104), (46, 100), (52, 86), (66, 96)]
    r_toe = [(80, 109), (76, 109), (62, 109), (58, 107), (62, 90), (80, 102)]
    # L opposite phase (shift by 3)
    # L is opposite phase: toe-off, passing, reach, contact, plant, push
    l_kn = [(36, 92), (40, 78), (52, 84), (52, 86), (48, 88), (42, 90)]
    l_an = [(28, 100), (36, 86), (66, 96), (54, 104), (50, 104), (40, 104)]
    l_toe = [(40, 107), (46, 90), (80, 102), (70, 109), (66, 109), (54, 109)]

    p.kn_r, p.an_r, p.toe_r = r_kn[i], r_an[i], r_toe[i]
    p.kn_l, p.an_l, p.toe_l = l_kn[i], l_an[i], l_toe[i]

    # arm swing (limited by the drum) — opposite to legs
    swing = [2, 1, -1, -2, -1, 1][i]
    p.el_r = (p.el_r[0] + swing, p.el_r[1] - abs(swing) * 0.3)
    p.hd_r = (p.hd_r[0] + swing * 1.4, p.hd_r[1] - swing)
    p.mal_r = (p.mal_r[0] + swing * 1.4, p.mal_r[1] - swing * 1.2)
    p.el_l = (p.el_l[0] - swing, p.el_l[1] - abs(swing) * 0.3)
    p.hd_l = (p.hd_l[0] - swing * 1.4, p.hd_l[1] + swing)
    p.mal_l = (p.mal_l[0] - swing * 1.4, p.mal_l[1] + swing * 1.2)

    # passing-leg in front
    p.leg_over = "right" if i in (0, 1, 5) else "left"
    return p


def pose_jump(i: int) -> Pose:
    p = idle_base()
    p.expression = "yell" if i in (1, 2) else "focus"
    if i == 0:
        # compress / launch
        _shift_upper(p, dy=8)
        p.kn_l, p.kn_r = (38, 94), (58, 94)
        p.an_l, p.an_r = (34, 104), (58, 104)
        p.toe_l, p.toe_r = (48, 109), (74, 109)
        p.el_l, p.el_r = (24, 66), (76, 66)
        p.hd_l, p.hd_r = (30, 74), (80, 74)
        p.mal_l, p.mal_r = (22, 66), (88, 66)
    elif i == 1:
        # rising — knees come up, body up a little in-frame (pose only)
        _shift_upper(p, dy=-2)
        p.kn_l, p.kn_r = (34, 80), (64, 78)
        p.an_l, p.an_r = (28, 92), (70, 88)
        p.toe_l, p.toe_r = (40, 98), (82, 92)
        p.el_l, p.el_r = (22, 50), (76, 48)
        p.hd_l, p.hd_r = (22, 40), (82, 40)
        p.mal_l, p.mal_r = (18, 30), (88, 30)
        p.leg_over = "right"
    elif i == 2:
        # apex, tucked
        _shift_upper(p, dy=-1)
        p.kn_l, p.kn_r = (36, 76), (66, 74)
        p.an_l, p.an_r = (30, 86), (74, 82)
        p.toe_l, p.toe_r = (42, 90), (84, 84)
        p.el_l, p.el_r = (24, 46), (74, 46)
        p.hd_l, p.hd_r = (26, 38), (80, 38)
        p.mal_l, p.mal_r = (22, 28), (86, 28)
        p.leg_over = "right"
    else:
        # falling, legs reach down for the landing
        _shift_upper(p, dy=1)
        p.kn_l, p.kn_r = (36, 86), (60, 86)
        p.an_l, p.an_r = (32, 100), (62, 100)
        p.toe_l, p.toe_r = (44, 106), (76, 106)
        p.el_l, p.el_r = (24, 56), (76, 56)
        p.hd_l, p.hd_r = (28, 66), (80, 66)
        p.mal_l, p.mal_r = (22, 56), (86, 56)
    return p


def pose_crouch(i: int) -> Pose:
    p = idle_base()
    p.expression = "focus"
    # Deep squat: hips drop hard, knees splay forward so thighs read horizontal.
    drop = 16 if i == 0 else 18
    _shift_upper(p, dy=drop)
    p.hip, p.hip_l, p.hip_r = (47, 90), (38, 90), (56, 90)
    p.kn_l, p.kn_r = (28, 98), (68, 98)
    p.an_l, p.an_r = (32, 104), (60, 104)
    p.toe_l, p.toe_r = (46, 109), (76, 109)
    # mallets held tight, a little in front
    bob = i  # 1px bob between the two held frames
    p.el_l, p.el_r = (24, 78 + bob), (76, 78 + bob)
    p.hd_l, p.hd_r = (32, 84 + bob), (78, 84 + bob)
    p.mal_l, p.mal_r = (20, 72 + bob), (88, 72 + bob)
    return p


def pose_block(i: int) -> Pose:
    p = idle_base()
    p.expression = "grit"
    # shove the drum forward as a shield, tuck the head behind it
    recede = 0 if i == 0 else 1
    _shift_upper(p, dy=3 + recede)
    p.face = (p.face[0] - 4, p.face[1] + 1)
    p.inst = (p.inst[0] + 10 - recede, p.inst[1] + 1)
    p.sh_l = (p.sh_l[0] + 5, p.sh_l[1] + 2)
    p.sh_r = (p.sh_r[0] + 7, p.sh_r[1] + 2)
    # Guard: one mallet high to the RIGHT of the head (over the drum), one mid-right.
    # Keep the face clear.
    p.el_l, p.el_r = (24, 64), (80, 52)
    p.hd_l, p.hd_r = (26, 66), (82, 50)
    p.mal_l, p.mal_r = (18, 54), (92, 38)
    p.hands_over = "both"
    p.kn_l, p.kn_r = (36, 92), (58, 92)
    return p


def pose_punch(i: int) -> Pose:
    p = idle_base()
    if i == 0:
        # windup: chamber the right mallet UP-BACK, clearly left of the hat, not on the face
        p.expression = "grit"
        _shift_upper(p, dx=-4, dy=1)
        p.sh_r = (p.sh_r[0] - 4, p.sh_r[1] - 2)
        # face is now ~ (43, 37); keep glove and mallet well left of it
        p.el_r, p.hd_r = (36, 48), (22, 30)
        p.mal_r = (16, 16)
        p.el_l, p.hd_l = (22, 66), (28, 72)
        p.mal_l = (16, 62)
        p.hands_over = "right"
    elif i == 1:
        # thrust: long mallet jab past the right edge of the drum
        p.expression = "yell"
        _shift_upper(p, dx=5, dy=0)
        p.sh_r = (p.sh_r[0] + 8, p.sh_r[1] - 3)
        p.el_r, p.hd_r = (78, 50), (88, 46)
        p.mal_r = (94, 40)
        p.el_l, p.hd_l = (24, 66), (30, 72)
        p.mal_l = (20, 62)
        p.hands_over = "right"
        p.flash = True
    else:
        # recover
        p.expression = "focus"
        _shift_upper(p, dx=2, dy=1)
        p.el_r, p.hd_r = (76, 54), (86, 52)
        p.mal_r = (92, 46)
        p.el_l, p.hd_l = (26, 64), (32, 68)
        p.mal_l = (22, 58)
        p.hands_over = "right"
    return p


def pose_kick(i: int) -> Pose:
    p = idle_base()
    p.leg_over = "right"
    if i == 0:
        # chamber
        p.expression = "grit"
        _shift_upper(p, dx=-2, dy=2)
        p.kn_r, p.an_r, p.toe_r = (60, 70), (64, 58), (76, 56)
        p.kn_l, p.an_l, p.toe_l = (38, 94), (34, 104), (48, 109)
        p.el_r, p.hd_r = (70, 56), (76, 60)
        p.mal_r = (82, 54)
    elif i == 1:
        # extend
        p.expression = "yell"
        _shift_upper(p, dx=-4, dy=0)
        p.face = (p.face[0] - 2, p.face[1])
        p.kn_r, p.an_r, p.toe_r = (70, 68), (84, 64), (96, 62)
        # keep toe in frame
        p.toe_r = (93, 62)
        p.an_r = (82, 64)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (50, 109)
        p.el_l, p.hd_l = (24, 58), (28, 50)
        p.mal_l = (24, 40)
    elif i == 2:
        # impact hold, slightly more stretch
        p.expression = "yell"
        _shift_upper(p, dx=-3, dy=1)
        p.kn_r, p.an_r, p.toe_r = (72, 70), (86, 66), (94, 64)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (50, 109)
        p.flash = True
        p.el_l, p.hd_l = (24, 58), (28, 52)
        p.mal_l = (24, 42)
    else:
        # recover
        p.expression = "focus"
        _shift_upper(p, dx=-1, dy=2)
        p.kn_r, p.an_r, p.toe_r = (62, 80), (68, 90), (80, 94)
        p.kn_l, p.an_l, p.toe_l = (38, 92), (34, 104), (48, 109)
    return p


def pose_special(i: int) -> Pose:
    p = idle_base()
    if i == 0:
        p.expression = "focus"
        _shift_upper(p, dy=3)
        p.el_l, p.el_r = (22, 48), (76, 48)
        p.hd_l, p.hd_r = (24, 36), (78, 36)
        p.mal_l, p.mal_r = (20, 20), (84, 20)
        p.kn_l, p.kn_r = (36, 92), (58, 92)
    elif i == 1:
        # mallets high and apart, beside the plume (not covering it)
        p.expression = "grit"
        _shift_upper(p, dy=4)
        p.face = (p.face[0], p.face[1] - 1)
        p.el_l, p.el_r = (22, 38), (76, 38)
        p.hd_l, p.hd_r = (24, 22), (78, 22)
        p.mal_l, p.mal_r = (22, 8), (80, 8)
        p.kn_l, p.kn_r = (36, 92), (58, 92)
    elif i == 2:
        # coming down toward the TOP of the drum
        p.expression = "yell"
        _shift_upper(p, dy=2)
        p.el_l, p.el_r = (28, 44), (74, 44)
        p.hd_l, p.hd_r = (40, 40), (70, 40)
        p.mal_l, p.mal_r = (46, 28), (66, 28)
        p.hands_over = "both"
    elif i == 3:
        # SLAM on the upper-RIGHT of the drum (toward the opponent) so the face stays open
        p.expression = "yell"
        _shift_upper(p, dy=5)
        # face ~ (47, 41), inst ~ (56, 69); hit the front-right quadrant
        p.el_l, p.el_r = (36, 58), (78, 50)
        p.hd_l, p.hd_r = (50, 54), (74, 48)
        p.mal_l, p.mal_r = (60, 50), (74, 42)
        p.flash = True
        p.slam = True
        p.hands_over = "both"
        p.kn_l, p.kn_r = (36, 94), (58, 94)
    elif i == 4:
        # blast — mallets bounce slightly off the top rim, drum ringing
        p.expression = "yell"
        _shift_upper(p, dy=5)
        p.el_l, p.el_r = (28, 48), (76, 46)
        p.hd_l, p.hd_r = (40, 44), (70, 42)
        p.mal_l, p.mal_r = (44, 32), (68, 30)
        p.hands_over = "both"
        p.kn_l, p.kn_r = (36, 93), (58, 93)
    else:
        # proud recover
        p.expression = "focus"
        _shift_upper(p, dy=2)
        p.el_l, p.el_r = (24, 56), (76, 54)
        p.hd_l, p.hd_r = (30, 60), (80, 58)
        p.mal_l, p.mal_r = (20, 48), (90, 44)
        p.hands_over = "both"
    return p


def pose_hit(i: int) -> Pose:
    p = idle_base()
    p.expression = "hit"
    if i == 0:
        # snap back
        _shift_upper(p, dx=-6, dy=-1)
        p.face = (p.face[0] - 2, p.face[1] - 1)
        p.inst = (p.inst[0] - 4, p.inst[1] - 1)
        p.el_l, p.el_r = (20, 56), (70, 52)
        p.hd_l, p.hd_r = (22, 48), (76, 46)
        p.mal_l, p.mal_r = (16, 38), (84, 36)
        p.kn_r, p.an_r, p.toe_r = (58, 88), (60, 104), (74, 109)
        p.kn_l, p.an_l, p.toe_l = (30, 90), (24, 102), (36, 108)
    else:
        _shift_upper(p, dx=-8, dy=2)
        p.face = (p.face[0] - 3, p.face[1] + 1)
        p.inst = (p.inst[0] - 6, p.inst[1] + 1)
        p.el_l, p.el_r = (18, 60), (68, 58)
        p.hd_l, p.hd_r = (18, 52), (74, 52)
        p.mal_l, p.mal_r = (14, 44), (82, 44)
        p.kn_r, p.an_r, p.toe_r = (56, 90), (58, 104), (72, 109)
        p.kn_l, p.an_l, p.toe_l = (28, 92), (20, 104), (32, 109)
    return p


def pose_ko(i: int) -> Pose:
    p = idle_base()
    if i == 0:
        p.expression = "hit"
        _shift_upper(p, dx=-8, dy=-2)
        p.face = (p.face[0] - 4, p.face[1] - 2)
        p.el_l, p.el_r = (16, 50), (64, 48)
        p.hd_l, p.hd_r = (14, 40), (70, 40)
        p.mal_l, p.mal_r = (10, 30), (78, 28)
        p.kn_r, p.an_r, p.toe_r = (60, 86), (66, 100), (78, 108)
        p.kn_l, p.an_l, p.toe_l = (28, 88), (20, 100), (30, 108)
    elif i == 1:
        p.expression = "hit"
        # falling back, rotating
        p.face = (30, 48)
        p.sh_l, p.sh_r = (22, 60), (44, 54)
        p.el_l, p.el_r = (12, 58), (52, 48)
        p.hd_l, p.hd_r = (8, 50), (58, 40)
        p.mal_l, p.mal_r = (6, 40), (66, 30)
        p.hip, p.hip_l, p.hip_r = (40, 72), (34, 74), (48, 68)
        p.kn_l, p.an_l, p.toe_l = (36, 90), (28, 102), (36, 109)
        p.kn_r, p.an_r, p.toe_r = (62, 78), (74, 88), (86, 92)
        p.inst = (40, 64)
        p.leg_over = "right"
    elif i == 2:
        p.expression = "ko"
        p.head_rot = 90
        # almost on the ground, body diagonal
        p.face = (32, 66)
        p.sh_l, p.sh_r = (20, 80), (40, 72)
        p.el_l, p.el_r = (10, 78), (50, 64)
        p.hd_l, p.hd_r = (6, 72), (56, 56)
        p.mal_l, p.mal_r = (4, 64), (64, 46)
        p.hip, p.hip_l, p.hip_r = (44, 84), (38, 86), (52, 80)
        p.kn_l, p.an_l, p.toe_l = (50, 96), (46, 106), (56, 109)
        p.kn_r, p.an_r, p.toe_r = (68, 84), (80, 90), (90, 92)
        p.inst = (36, 82)
        p.leg_over = "right"
    else:
        p.expression = "ko"
        p.head_rot = 90
        # flat on his back, head to the left, drum on the belly, one foot up
        p.face = (30, 88)
        p.sh_l, p.sh_r = (28, 90), (42, 86)
        p.el_l, p.el_r = (16, 96), (50, 80)
        p.hd_l, p.hd_r = (10, 100), (56, 72)
        p.mal_l, p.mal_r = (8, 104), (62, 64)
        p.hip, p.hip_l, p.hip_r = (58, 90), (52, 92), (64, 88)
        p.kn_l, p.an_l, p.toe_l = (70, 94), (80, 98), (90, 100)
        p.kn_r, p.an_r, p.toe_r = (68, 78), (76, 68), (86, 64)
        p.inst = (42, 92)
        p.inst_rx, p.inst_ry = 18, 14
        p.leg_over = "right"
        p.hands_over = "right"
    return p


POSE_FN = {
    "idle": pose_idle,
    "walk": pose_walk,
    "jump": pose_jump,
    "crouch": pose_crouch,
    "block": pose_block,
    "punch": pose_punch,
    "kick": pose_kick,
    "special": pose_special,
    "hit": pose_hit,
    "ko": pose_ko,
}


# ---------------------------------------------------------------------------
# Compose one frame
# ---------------------------------------------------------------------------

def _part(draw_fn) -> Canvas:
    return layer_and_outline(draw_fn)


def _rotate_around(layer: Canvas, pivot, deg: int) -> Canvas:
    """Rotate a frame-sized layer in 90-degree steps about pivot, same canvas size."""
    if not deg:
        return layer
    # pose.head_rot is degrees counter-clockwise. PIL.rotate is also CCW.
    img = layer.to_image()
    rot = img.rotate(int(deg), resample=Image.Resampling.NEAREST, center=pivot, expand=False, fillcolor=(0, 0, 0, 0))
    out = Canvas(layer.w, layer.h)
    px = rot.load()
    for y in range(layer.h):
        for x in range(layer.w):
            r, g, b, a = px[x, y]
            if a:
                out.px[y][x] = (r, g, b, a)
    return out


def render_pose(pose: Pose) -> Canvas:
    """Composite a fully outlined fighter frame from a pose."""
    out = new_layer()

    # flags
    leg_over = getattr(pose, "leg_over", None)
    hands_over = pose.hands_over

    def legs_far(c):
        # far leg + shoe only: draw both then we'll split? Easier: draw both
        # legs in far pass if neither is over, else only the far one.
        draw_legs(c, pose)
        draw_shoes(c, pose)

    # We always draw legs first, then optionally redraw the "over" leg later.
    far_legs = _part(lambda c: (draw_legs(c, pose), draw_shoes(c, pose)))
    out.blit(far_legs)

    torso = _part(lambda c: (draw_neck(c, pose), draw_torso(c, pose)))
    out.blit(torso)

    head = _part(lambda c: draw_head(c, pose))
    if getattr(pose, "head_rot", 0):
        head = _rotate_around(head, pose.face, pose.head_rot)
    head_over = bool(getattr(pose, "head_rot", 0))
    if not head_over:
        out.blit(head)

    # far arm (left) behind the drum unless flagged
    def arm_l(c, glove=True):
        draw_arm(c, pose.sh_l, pose.el_l, pose.hd_l, pose.mal_l, near=False, include_glove=glove)

    def arm_r(c, glove=True):
        draw_arm(c, pose.sh_r, pose.el_r, pose.hd_r, pose.mal_r, near=True, include_glove=glove)

    if hands_over not in ("left", "both"):
        # left arm + mallet fully behind drum
        layer = _part(
            lambda c: (
                arm_l(c, glove=True),
                draw_mallet(c, pose.hd_l, pose.mal_l),
            )
        )
        out.blit(layer)
    else:
        # arm behind, glove/mallet later
        layer = _part(lambda c: arm_l(c, glove=False))
        out.blit(layer)

    if hands_over not in ("right", "both"):
        layer = _part(
            lambda c: (
                arm_r(c, glove=True),
                draw_mallet(c, pose.hd_r, pose.mal_r),
            )
        )
        out.blit(layer)
    else:
        layer = _part(lambda c: arm_r(c, glove=False))
        out.blit(layer)

    harness = _part(lambda c: draw_harness(c, pose))
    out.blit(harness)

    drum = _part(lambda c: draw_bass_drum(c, pose))
    out.blit(drum)

    # hands / mallets in front of the drum
    if hands_over in ("left", "both"):
        # shaft under glove, head in front
        shaft = _part(lambda c: draw_mallet(c, pose.hd_l, pose.mal_l, shaft_only=True))
        glove = _part(lambda c: draw_glove(c, pose.hd_l, pose.mal_l, near=False))
        headm = _part(lambda c: draw_mallet(c, pose.hd_l, pose.mal_l, head_only=True))
        out.blit(shaft)
        out.blit(glove)
        out.blit(headm)
    if hands_over in ("right", "both"):
        shaft = _part(lambda c: draw_mallet(c, pose.hd_r, pose.mal_r, shaft_only=True))
        glove = _part(lambda c: draw_glove(c, pose.hd_r, pose.mal_r, near=True))
        headm = _part(lambda c: draw_mallet(c, pose.hd_r, pose.mal_r, head_only=True))
        out.blit(shaft)
        out.blit(glove)
        out.blit(headm)

    # kicking / passing leg redrawn in front
    if leg_over == "right":
        def only_right(c):
            from pxart.body import draw_leg, draw_shoe

            draw_leg(c, pose.hip_r, pose.kn_r, pose.an_r, near=True, outward=1)
            tl, tr = pose.toes()
            draw_shoe(c, pose.an_r, tr, near=True)

        out.blit(_part(only_right))
    elif leg_over == "left":
        def only_left(c):
            from pxart.body import draw_leg, draw_shoe

            draw_leg(c, pose.hip_l, pose.kn_l, pose.an_l, near=False, outward=-1)
            tl, tr = pose.toes()
            draw_shoe(c, pose.an_l, tl, near=False)

        out.blit(_part(only_left))

    if head_over:
        out.blit(head)

    # un-outlined impact flash on top of the drum (special / punch)
    if pose.flash:
        fx = new_layer()
        cx, cy = pose.inst
        if getattr(pose, "slam", False) and pose.mal_l and pose.mal_r:
            # special slam: burst between the two mallet heads
            bx = (pose.mal_l[0] + pose.mal_r[0]) / 2
            by = (pose.mal_l[1] + pose.mal_r[1]) / 2
            fx.shade_disk(bx, by, 6, FLASH, WHITE, GOLD_LT)
            for deg in range(-150, 30, 25):
                x2, y2 = off(bx, by, deg, 10)
                fx.line(int(bx), int(by), int(x2), int(y2), GOLD_LT)
        elif pose.mal_r:
            # punch: flash at right mallet
            fx.shade_disk(pose.mal_r[0], pose.mal_r[1], 4, FLASH, WHITE, GOLD_LT)
        out.blit(fx)

    return out


def render_frame(animation: str, index: int) -> Canvas:
    fn = POSE_FN[animation]
    return render_pose(fn(index))


# ---------------------------------------------------------------------------
# Portrait (64x64 bust)
# ---------------------------------------------------------------------------

def render_portrait() -> Canvas:
    """SF2-style select-screen bust. Border-friendly navy/gold field."""
    # Render a hero idle pose on the full frame, crop the bust, blit onto
    # a 64x64 card with a flat navy field and a thin gold inner ring so a
    # UI frame can sit on the edge without fighting the art.
    pose = idle_base()
    pose.expression = "focus"
    # slightly more "posed" — right mallet up a touch
    pose.mal_r = (84, 44)
    pose.hd_r = (78, 56)
    pose.el_r = (74, 54)
    body = render_pose(pose)

    port = Canvas(64, 64)
    # background: flat navy, darker at the very edge (border-friendly)
    for y in range(64):
        for x in range(64):
            # soft 2-tone vignette without anti-alias
            edge = x < 2 or y < 2 or x > 61 or y > 61
            if edge:
                port.set(x, y, NAVY_DK)
            else:
                # a cheap radial: darker corners, mid in the center
                dx, dy = (x - 32) / 32, (y - 32) / 32
                if dx * dx + dy * dy > 0.72:
                    port.set(x, y, NAVY)
                else:
                    port.set(x, y, NAVY_LT)
    # gold corner ticks (select-screen flavor) inset by 2px
    for (x, y) in (
        (2, 2), (3, 2), (2, 3),
        (61, 2), (60, 2), (61, 3),
        (2, 61), (3, 61), (2, 60),
        (61, 61), (60, 61), (61, 60),
    ):
        port.set(x, y, GOLD)

    # Find the bust bbox and place it with a 3px top/side margin so the plume
    # and a UI frame don't clip.
    top = body.h
    left, right, bottom = body.w, 0, 0
    for y in range(body.h):
        for x in range(body.w):
            if body.get(x, y) is None:
                continue
            # only consider the upper body (skip legs) for the crop
            if y > 78:
                continue
            if y < top:
                top = y
            if y > bottom:
                bottom = y
            if x < left:
                left = x
            if x > right:
                right = x
    # 64x64 window: center on the bust, pin the plume 3px from the top
    ox = int((left + right) / 2) - 32
    oy = max(0, top - 3)
    # if the crop would run off the bottom of the interesting bust, shift up
    if oy + 64 > body.h:
        oy = body.h - 64
    ox = max(0, min(ox, body.w - 64))
    for y in range(64):
        for x in range(64):
            c = body.get(ox + x, oy + y)
            if c is not None:
                port.px[y][x] = c
    return port


# ---------------------------------------------------------------------------
# Shockwave projectile strip
# ---------------------------------------------------------------------------

def render_projectile_frames() -> List[Canvas]:
    w, h = PROJECTILE["frameWidth"], PROJECTILE["frameHeight"]
    frames = []
    # 6 frames: spark at the origin, then right-opening sound-wave crescents
    # that travel and grow, staying inside the 80x64 box.
    for i in range(PROJECTILE["frames"]):
        c = Canvas(w, h)
        ox = 8 + i * 5          # travels right
        oy = 32
        # leading arc radius; keep right edge inside the frame (ox+r < 78)
        radius = 5 + i * 6
        radius = min(radius, 76 - ox)
        n_rings = 1 + (1 if i >= 1 else 0) + (1 if i >= 3 else 0)
        for r_i in range(n_rings):
            rr = radius - r_i * 6
            if rr < 3:
                continue
            mid = [GOLD_LT, GOLD, WHITE][r_i]
            dark = [GOLD_DK, GOLD_DK, GOLD][r_i]
            light = [FLASH, GOLD_LT, WHITE][r_i]
            # later rings start to break apart
            broken = i >= 5 and r_i == 0
            _shock_arc(c, ox, oy, rr, rr * 0.88, mid, light, dark, broken=broken)
        if i <= 2:
            c.shade_disk(ox, oy, max(2.2, 4.2 - i * 0.7), FLASH, WHITE, GOLD_LT)
            for deg, dist in ((-50, 7 + i * 2), (50, 7 + i * 2), (0, 9 + i * 3)):
                x2, y2 = off(ox, oy, deg, dist)
                c.line(int(ox), int(oy), int(x2), int(y2), WHITE)
        if i == 5:
            # shards flying right
            for deg in range(-65, 70, 16):
                x2, y2 = off(ox, oy, deg, radius + 3)
                if 1 <= x2 < w - 1 and 1 <= y2 < h - 1:
                    c.disk(x2, y2, 1.3, GOLD_LT)
        frames.append(auto_outline(c, OUTLINE))
    return frames


def _shock_arc(c: Canvas, cx, cy, rx, ry, mid, light, dark, broken=False) -> None:
    """Right-opening crescent (a sound-wave slash), not a full circle."""
    cx, cy, rx, ry = float(cx), float(cy), float(rx), float(ry)
    x0, x1 = int(cx - rx - 2), int(cx + rx + 2)
    y0, y1 = int(cy - ry - 2), int(cy + ry + 2)
    for y in range(y0, y1 + 1):
        dy = ((y + 0.5) - cy) / (ry + 0.45)
        for x in range(x0, x1 + 1):
            dx = ((x + 0.5) - cx) / (rx + 0.45)
            d = dx * dx + dy * dy
            if not (0.70 <= d <= 1.10):
                continue
            # Keep only the front ~200 degrees, opening to the right.
            # atan2 in screen space: 0 = right, 90 = down.
            ang = math.degrees(math.atan2((y + 0.5) - cy, (x + 0.5) - cx))
            # drop the back of the wave (left side)
            if ang > 115 or ang < -115:
                continue
            if broken and (abs(ang) % 28) < 7:
                continue
            ndot = dx * (-0.3) + dy * (-0.7)
            if ndot > 0.2:
                c.set(x, y, light)
            elif ndot < -0.2:
                c.set(x, y, dark)
            else:
                c.set(x, y, mid)


# ---------------------------------------------------------------------------
# Hit / hurt box hints (frame-space AABBs: x, y, w, h)
# ---------------------------------------------------------------------------

def animation_boxes(name: str) -> dict:
    """Simple hurtbox / optional hitbox hints for the integrator."""
    # Default standing hurtbox covers body + drum
    stand = {"x": 26, "y": 10, "w": 52, "h": 101}
    boxes = {"hurtbox": stand}
    if name == "idle":
        boxes["hurtbox"] = stand
    elif name == "walk":
        boxes["hurtbox"] = {"x": 20, "y": 10, "w": 58, "h": 101}
    elif name == "jump":
        boxes["hurtbox"] = {"x": 24, "y": 8, "w": 54, "h": 96}
    elif name == "crouch":
        boxes["hurtbox"] = {"x": 24, "y": 22, "w": 54, "h": 89}
    elif name == "block":
        boxes["hurtbox"] = {"x": 28, "y": 14, "w": 56, "h": 97}
        boxes["blockbox"] = {"x": 48, "y": 40, "w": 32, "h": 40}  # the drum
    elif name == "punch":
        boxes["hurtbox"] = {"x": 24, "y": 10, "w": 54, "h": 101}
        boxes["hitbox"] = {"frames": [1], "x": 80, "y": 32, "w": 16, "h": 20}
    elif name == "kick":
        boxes["hurtbox"] = {"x": 22, "y": 12, "w": 50, "h": 99}
        boxes["hitbox"] = {"frames": [1, 2], "x": 72, "y": 52, "w": 22, "h": 18}
    elif name == "special":
        boxes["hurtbox"] = {"x": 26, "y": 10, "w": 54, "h": 101}
        boxes["hitbox"] = {"frames": [3, 4], "x": 54, "y": 28, "w": 34, "h": 40}
        boxes["spawn_projectile_on"] = 3
    elif name == "hit":
        boxes["hurtbox"] = {"x": 16, "y": 10, "w": 56, "h": 101}
    elif name == "ko":
        boxes["hurtbox"] = {"x": 8, "y": 40, "w": 80, "h": 71}
    return boxes
