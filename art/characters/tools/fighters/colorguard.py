"""Jade 'Banner' Castillo — acrobatic color guard, flag on a pole, no shako."""

from __future__ import annotations

import math
from typing import List

from pxart.body import Pose
from pxart.canvas import Canvas, auto_outline
from pxart.compose import STANDARD_ANIMS, bust_portrait, render_character, shift_upper
from pxart.looks import jade
from pxart.palette import (
    GOLD, GOLD_DK, GOLD_LT, NAVY, NAVY_DK, NAVY_LT, OUTLINE,
    SILVER, SILVER_DK, SILVER_LT, WHITE, WHITE_SH, rgba, shade,
)

ID = "colorguard"
NAME = 'Jade "Banner" Castillo'
INSTRUMENT = "Flag (and the occasional rifle toss)"
ANIMATIONS = STANDARD_ANIMS
LOOK = jade()

MAGENTA = rgba("#FF006E")
MAGENTA_LT = shade(MAGENTA, 1.4)
MAGENTA_DK = shade(MAGENTA, 0.55)

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 64,
    "frameHeight": 48,
    "frames": 6,
    "fps": 12,
    "loop": False,
    "anchor": {"x": 8, "y": 24},
    "notes": (
        "A rippling flag-wave travelling right. Spawn on special frame index 3, "
        "origin at the flag tip."
    ),
}
NOTES = (
    "Acrobatic color-guard costume in navy and gold (sleeveless bodice, short "
    "skirt, hair in a high bun — no shako). Wields a long flag on a pole. "
    "Jump is a flip; special is a spinning flag flourish. She is enabled "
    "in content/roster.json."
)


def _base() -> Pose:
    p = Pose(
        face=(46, 34),
        sh_l=(38, 48),
        sh_r=(56, 48),
        el_l=(32, 60),
        el_r=(68, 50),
        hd_l=(30, 70),
        hd_r=(74, 36),
        hip=(46, 70),
        hip_l=(41, 70),
        hip_r=(51, 70),
        kn_l=(38, 86),
        kn_r=(54, 86),
        an_l=(36, 104),
        an_r=(54, 104),
        toe_l=(48, 109),
        toe_r=(68, 109),
        inst=(80, 16),  # flag tip / fabric center default
        mal_l=(28, 78),  # pole butt
        mal_r=(78, 20),  # pole tip
        expression="idle",
        hands_over="both",
    )
    p.look = LOOK
    return p


def draw_flag(c: Canvas, pose: Pose, spin=0) -> None:
    """Pole from mal_l (butt) to mal_r (tip), silk trailing from the tip."""
    a = pose.mal_l or pose.hd_l
    b = pose.mal_r or pose.hd_r
    if a is None or b is None:
        return
    x1, y1 = a
    x2, y2 = b
    vx, vy = x2 - x1, y2 - y1
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    # pole (silver / dark)
    c.shade_taper(x1, y1, x2, y2, 1.35, 1.05, SILVER, SILVER_LT, SILVER_DK)
    # gold ferrule at the tip
    c.shade_disk(x2, y2, 2.0, GOLD, GOLD_LT, GOLD_DK)

    # Flag silk: a waving trapezoid off the last third of the pole.
    # Perpendicular to the pole, plus a 'spin' offset so special frames rotate it.
    px, py = -uy, ux  # perpendicular
    ang = math.radians(spin)
    # rotate the perpendicular a bit
    rpx = px * math.cos(ang) - py * math.sin(ang)
    rpy = px * math.sin(ang) + py * math.cos(ang)
    # flag attaches near the tip and hangs/streams
    attach = 0.22  # fraction of pole from the tip
    ax = x2 - ux * leng * attach
    ay = y2 - uy * leng * attach
    # four corners of the silk
    w = 16  # width along the pole
    d = 18  # how far the silk stands off the pole
    # wave: bump the free edge
    wave = math.sin(spin * 0.2 + leng) * 3
    p0 = (ax, ay)
    p1 = (x2 + ux * 2, y2 + uy * 2)
    p2 = (x2 + rpx * (d + wave) + ux * 4, y2 + rpy * (d + wave) + uy * 4)
    p3 = (ax + rpx * (d - wave) - ux * 2, ay + rpy * (d - wave) - uy * 2)
    # fill by spraying disks along the quad
    for i in range(12):
        t = i / 11
        # along pole
        sx = ax + (x2 - ax) * t
        sy = ay + (y2 - ay) * t
        for j in range(8):
            u = j / 7
            fx_ = sx + rpx * (d + wave * (0.5 - t)) * u
            fy_ = sy + rpy * (d + wave * (0.5 - t)) * u
            # stripes: navy, gold, magenta, white
            band = int(u * 4) % 4
            col = (NAVY, GOLD, MAGENTA, WHITE)[band]
            col_lt = (NAVY_LT, GOLD_LT, MAGENTA_LT, WHITE)[band]
            c.disk(fx_, fy_, 2.1, col if (i + j) % 3 else col_lt)
    # gold hem tick
    c.shade_taper(p2[0], p2[1], p3[0], p3[1], 0.9, 0.9, GOLD, GOLD_LT, GOLD_DK)


def paint_front(c, pose):
    spin = getattr(pose, "flag_spin", 0) or 0
    draw_flag(c, pose, spin=spin)


def paint_flash(c, pose):
    if pose.mal_r and pose.flash:
        c.shade_disk(pose.mal_r[0], pose.mal_r[1], 5, MAGENTA_LT, WHITE, MAGENTA)


def render_pose(pose: Pose) -> Canvas:
    return render_character(pose, clothing="guard", paint_front=paint_front, paint_flash=paint_flash)


def pose_idle(i):
    p = _base()
    bob = [0, 1, 2, 1][i]
    shift_upper(p, dy=bob)
    # flag gently sways
    p.mal_r = (p.mal_r[0] + [0, 1, 0, -1][i], p.mal_r[1] + [0, -1, 0, 1][i])
    p.flag_spin = [-8, 0, 8, 0][i]
    return p


def pose_walk(i):
    p = _base()
    bounce = [1, -1, 0, 1, -1, 0][i]
    shift_upper(p, dy=bounce)
    r_kn = [(58, 84), (54, 86), (48, 88), (46, 90), (52, 76), (62, 82)]
    r_an = [(60, 104), (56, 104), (46, 104), (44, 100), (50, 86), (64, 96)]
    r_toe = [(74, 109), (70, 109), (60, 109), (56, 107), (60, 90), (78, 102)]
    l_kn = [(36, 90), (40, 76), (50, 82), (50, 84), (46, 86), (40, 88)]
    l_an = [(28, 100), (36, 86), (64, 96), (52, 104), (48, 104), (38, 104)]
    l_toe = [(40, 107), (46, 90), (78, 102), (66, 109), (62, 109), (52, 109)]
    p.kn_r, p.an_r, p.toe_r = r_kn[i], r_an[i], r_toe[i]
    p.kn_l, p.an_l, p.toe_l = l_kn[i], l_an[i], l_toe[i]
    swing = [2, 1, -1, -2, -1, 1][i]
    p.mal_r = (p.mal_r[0] + swing, p.mal_r[1] - swing)
    p.flag_spin = swing * 6
    p.leg_over = "right" if i in (0, 1, 5) else "left"
    return p


def pose_jump(i):
    """Acrobatic flip: coil, tuck, invert suggestion, land."""
    p = _base()
    p.expression = "yell" if i in (1, 2) else "focus"
    if i == 0:
        # coil
        shift_upper(p, dy=8)
        p.kn_l, p.kn_r = (36, 94), (56, 94)
        p.mal_l, p.mal_r = (24, 86), (70, 50)
        p.flag_spin = 20
    elif i == 1:
        # tucked flip, mid-air, flag sweeping
        shift_upper(p, dy=-2)
        p.face = (50, 50)
        p.sh_l, p.sh_r = (40, 58), (58, 46)
        p.kn_l, p.kn_r = (44, 70), (62, 56)
        p.an_l, p.an_r = (40, 80), (72, 64)
        p.toe_l, p.toe_r = (50, 86), (84, 66)
        p.el_l, p.el_r = (34, 50), (70, 36)
        p.hd_l, p.hd_r = (30, 60), (80, 24)
        p.mal_l, p.mal_r = (22, 72), (90, 8)
        p.hip, p.hip_l, p.hip_r = (50, 62), (44, 64), (56, 58)
        p.flag_spin = 80
        p.leg_over = "right"
    elif i == 2:
        # coming over — almost inverted feel, legs up, flag around
        p.face = (48, 58)
        p.head_rot = 180
        p.sh_l, p.sh_r = (42, 48), (58, 52)
        p.hip, p.hip_l, p.hip_r = (50, 42), (44, 42), (56, 44)
        p.kn_l, p.kn_r = (40, 28), (64, 26)
        p.an_l, p.an_r = (36, 16), (70, 14)
        p.toe_l, p.toe_r = (46, 10), (82, 8)
        p.el_l, p.el_r = (32, 56), (68, 60)
        p.hd_l, p.hd_r = (26, 66), (76, 70)
        p.mal_l, p.mal_r = (18, 80), (90, 86)
        p.flag_spin = 160
        p.leg_over = "right"
    else:
        # land
        shift_upper(p, dy=2)
        p.kn_l, p.kn_r = (36, 88), (58, 88)
        p.an_l, p.an_r = (34, 104), (58, 104)
        p.toe_l, p.toe_r = (46, 109), (72, 109)
        p.mal_l, p.mal_r = (26, 80), (80, 30)
        p.flag_spin = -20
    return p


def pose_crouch(i):
    p = _base()
    p.expression = "focus"
    shift_upper(p, dy=14 + i)
    p.hip, p.hip_l, p.hip_r = (46, 88), (40, 88), (52, 88)
    p.kn_l, p.kn_r = (30, 98), (64, 98)
    # flag still high, planted
    p.hd_l, p.hd_r = (30, 84), (70, 50)
    p.mal_l, p.mal_r = (26, 94), (78, 24)
    p.flag_spin = 10
    return p


def pose_block(i):
    p = _base()
    p.expression = "grit"
    shift_upper(p, dy=3 + i)
    p.face = (p.face[0] - 2, p.face[1])
    # pole vertical as a guard, flag to the right of the head
    p.el_l, p.el_r = (36, 56), (62, 46)
    p.hd_l, p.hd_r = (48, 62), (58, 34)
    p.mal_l, p.mal_r = (50, 86), (64, 8)
    p.flag_spin = 15
    p.kn_l, p.kn_r = (38, 90), (54, 90)
    return p


def pose_punch(i):
    p = _base()
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-3, dy=1)
        p.el_r, p.hd_r = (48, 40), (36, 22)
        p.mal_l, p.mal_r = (22, 70), (28, 4)
        p.hands_over = "right"
        p.flag_spin = -30
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=6)
        # long pole jab
        p.el_l, p.el_r = (44, 54), (78, 48)
        p.hd_l, p.hd_r = (56, 52), (88, 46)
        p.mal_l, p.mal_r = (36, 58), (94, 40)
        p.hands_over = "right"
        p.flash = True
        p.flag_spin = 10
    else:
        p.expression = "focus"
        shift_upper(p, dx=2, dy=1)
        p.el_r, p.hd_r = (76, 52), (86, 48)
        p.mal_l, p.mal_r = (34, 60), (92, 44)
        p.hands_over = "right"
        p.flag_spin = 0
    return p


def pose_kick(i):
    p = _base()
    p.leg_over = "right"
    # long-reach: high kick, flag held back for balance then sweep
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-2, dy=2)
        p.kn_r, p.an_r, p.toe_r = (60, 66), (68, 52), (80, 48)
        p.mal_l, p.mal_r = (22, 44), (50, 8)
        p.flag_spin = 40
        p.kn_l, p.an_l, p.toe_l = (38, 94), (34, 104), (46, 109)
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=-5)
        p.kn_r, p.an_r, p.toe_r = (74, 62), (90, 56), (94, 54)
        p.mal_l, p.mal_r = (18, 40), (44, 6)
        p.flag_spin = 50
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (48, 109)
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=-4, dy=1)
        p.kn_r, p.an_r, p.toe_r = (76, 64), (92, 58), (94, 56)
        p.flash = True
        p.flag_spin = 30
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (48, 109)
    else:
        p.expression = "focus"
        shift_upper(p, dx=-1, dy=2)
        p.kn_r, p.an_r, p.toe_r = (62, 80), (68, 92), (80, 96)
        p.mal_l, p.mal_r = (26, 76), (80, 24)
        p.flag_spin = 0
        p.kn_l, p.an_l, p.toe_l = (38, 92), (34, 104), (46, 109)
    return p


def pose_special(i):
    """Spinning flag flourish around the body."""
    p = _base()
    p.expression = "yell" if i in (2, 3, 4) else "focus"
    # flag tip orbits around the body
    cx, cy = 48, 50
    angles = [50, 110, 180, 250, 320, 20]  # degrees, 0 = right
    radii = [34, 36, 32, 36, 34, 32]
    ang = angles[i]
    rad = math.radians(ang)
    tip = (cx + math.cos(rad) * radii[i], cy + math.sin(rad) * radii[i] * 0.85)
    # hands stay near the body, pole runs through them toward the tip
    p.el_r, p.hd_r = (58, 50), (62, 46)
    p.el_l, p.hd_l = (38, 56), (42, 54)
    p.mal_r = tip
    # butt opposite the tip
    p.mal_l = (cx - math.cos(rad) * 22, cy - math.sin(rad) * 18)
    p.flag_spin = ang
    if i == 3:
        p.flash = True
    if i in (1, 2):
        # slight squat / spin body
        shift_upper(p, dy=3)
        p.kn_l, p.kn_r = (36, 90), (56, 90)
    return p


def pose_hit(i):
    p = _base()
    p.expression = "hit"
    shift_upper(p, dx=-6 if i == 0 else -9, dy=-1 if i == 0 else 2)
    p.mal_l, p.mal_r = (12, 60), (64, 20)
    p.flag_spin = -40
    p.kn_l, p.an_l, p.toe_l = (30, 90), (22, 104), (34, 109)
    return p


def pose_ko(i):
    p = _base()
    if i == 0:
        p.expression = "hit"
        shift_upper(p, dx=-8, dy=-2)
        p.mal_l, p.mal_r = (10, 50), (60, 16)
        p.flag_spin = -50
    elif i == 1:
        p.expression = "hit"
        p.face = (30, 48)
        p.sh_l, p.sh_r = (22, 60), (44, 54)
        p.el_l, p.el_r = (14, 58), (52, 48)
        p.hd_l, p.hd_r = (10, 50), (58, 40)
        p.mal_l, p.mal_r = (6, 62), (70, 28)
        p.hip, p.hip_l, p.hip_r = (42, 72), (36, 74), (50, 68)
        p.kn_l, p.an_l, p.toe_l = (36, 90), (28, 102), (38, 109)
        p.kn_r, p.an_r, p.toe_r = (64, 78), (76, 88), (88, 92)
        p.flag_spin = 70
        p.leg_over = "right"
    elif i == 2:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (32, 68)
        p.sh_l, p.sh_r = (22, 80), (42, 72)
        p.el_l, p.el_r = (12, 78), (52, 64)
        p.hd_l, p.hd_r = (8, 72), (58, 56)
        p.mal_l, p.mal_r = (6, 86), (72, 50)
        p.hip, p.hip_l, p.hip_r = (46, 84), (40, 86), (54, 80)
        p.kn_l, p.an_l, p.toe_l = (52, 96), (48, 106), (58, 109)
        p.kn_r, p.an_r, p.toe_r = (68, 84), (80, 90), (90, 92)
        p.flag_spin = 100
        p.leg_over = "right"
    else:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (30, 88)
        p.sh_l, p.sh_r = (28, 90), (44, 86)
        p.el_l, p.el_r = (16, 96), (52, 80)
        p.hd_l, p.hd_r = (10, 100), (58, 72)
        p.mal_l, p.mal_r = (8, 104), (70, 78)
        p.hip, p.hip_l, p.hip_r = (58, 90), (52, 92), (64, 88)
        p.kn_l, p.an_l, p.toe_l = (70, 94), (80, 98), (90, 100)
        p.kn_r, p.an_r, p.toe_r = (68, 78), (76, 68), (86, 64)
        p.flag_spin = 20
        p.leg_over = "right"
        p.hands_over = "right"
    return p


POSE_FN = {
    "idle": pose_idle, "walk": pose_walk, "jump": pose_jump, "crouch": pose_crouch,
    "block": pose_block, "punch": pose_punch, "kick": pose_kick, "special": pose_special,
    "hit": pose_hit, "ko": pose_ko,
}


def render_frame(animation, index):
    return render_pose(POSE_FN[animation](index))


def render_portrait() -> Canvas:
    p = _base()
    p.expression = "focus"
    # flag over the shoulder in the bust
    p.mal_l, p.mal_r = (22, 78), (82, 8)
    p.hd_l, p.hd_r = (36, 60), (68, 32)
    p.flag_spin = 25
    return bust_portrait(render_pose(p), NAVY, NAVY_LT, NAVY_DK, GOLD, margin=4)


def render_projectile_frames() -> List[Canvas]:
    w, h = 64, 48
    frames = []
    for i in range(6):
        c = Canvas(w, h)
        # a rippling flag / wave travelling right
        ox = 6 + i * 6
        oy = 24
        length = 16 + i * 6
        for t in range(length):
            wave = math.sin((t + i * 8) * 0.35) * (5 + i)
            x = ox + t
            y = oy + wave
            band = (t // 4) % 4
            col = (NAVY, GOLD, MAGENTA, WHITE)[band]
            c.disk(x, y, 2.4, col)
            c.disk(x, y - 1, 1.4, shade(col, 1.3))
        frames.append(auto_outline(c, OUTLINE))
    return frames


def animation_boxes(name: str) -> dict:
    stand = {"x": 28, "y": 8, "w": 42, "h": 103}
    boxes = {"hurtbox": stand}
    if name == "crouch":
        boxes["hurtbox"] = {"x": 26, "y": 26, "w": 44, "h": 85}
    elif name == "punch":
        boxes["hitbox"] = {"frames": [1], "x": 80, "y": 32, "w": 16, "h": 22}
    elif name == "kick":
        boxes["hitbox"] = {"frames": [1, 2], "x": 72, "y": 48, "w": 22, "h": 18}
    elif name == "special":
        boxes["hitbox"] = {"frames": [1, 2, 3, 4], "x": 16, "y": 16, "w": 68, "h": 80}
        boxes["spawn_projectile_on"] = 3
    elif name == "ko":
        boxes["hurtbox"] = {"x": 8, "y": 40, "w": 80, "h": 71}
    return boxes
