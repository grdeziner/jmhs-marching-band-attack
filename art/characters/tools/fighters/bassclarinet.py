"""Ozzie 'The Deep End' Lindqvist — tall, lanky, bass clarinet as a spear/halberd."""

from __future__ import annotations

import math
from typing import List

from pxart.body import Pose
from pxart.canvas import Canvas, auto_outline
from pxart.compose import STANDARD_ANIMS, bust_portrait, render_character, shift_upper
from pxart.looks import ozzie
from pxart.palette import (
    GOLD, GOLD_DK, GOLD_LT, NAVY, NAVY_DK, NAVY_LT, OUTLINE, WHITE, WHITE_DK, rgba,
)

ID = "bassclarinet"
NAME = 'Ozzie "The Deep End" Lindqvist'
INSTRUMENT = "Bass clarinet"
ANIMATIONS = STANDARD_ANIMS
LOOK = ozzie()

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 96,
    "frameHeight": 32,
    "frames": 6,
    "fps": 10,
    "loop": False,
    "anchor": {"x": 8, "y": 28},
    "notes": (
        "Deep rumbling ground wave. Spawn on special frame index 3, "
        "origin at the grounded bell, travelling right along the floor."
    ),
}
NOTES = (
    "Tall and lanky. Holds a long bass clarinet like a spear / halberd, "
    "with the signature upturned brass bell as the weapon head. "
    "Special is a deep violet ground wave. Violet plume."
)

VIOLET = rgba("#A78BFA")
VIOLET_DK = rgba("#5B4A9A")


def _base() -> Pose:
    # Tall: face higher, longer legs, thinner through the look scales.
    p = Pose(
        face=(47, 26),
        sh_l=(39, 44),
        sh_r=(57, 44),
        el_l=(32, 58),
        el_r=(68, 56),
        hd_l=(34, 70),
        hd_r=(70, 62),
        hip=(47, 66),
        hip_l=(42, 66),
        hip_r=(52, 66),
        kn_l=(39, 84),
        kn_r=(55, 84),
        an_l=(37, 104),
        an_r=(55, 104),
        toe_l=(49, 109),
        toe_r=(69, 109),
        inst=(60, 70),
        mal_l=(36, 96),  # mouthpiece / butt (low, back)
        mal_r=(86, 34),  # upturned bell / spear head (high, forward)
        expression="idle",
        hands_over="both",
    )
    p.look = LOOK
    return p


def draw_bassclarinet(c: Canvas, p: Pose) -> None:
    """Long dark body from mal_l to just shy of mal_r, then an upturned brass bell."""
    a = p.mal_l or p.hd_l
    b = p.mal_r or p.hd_r
    if a is None or b is None:
        return
    x1, y1 = a
    x2, y2 = b
    vx, vy = x2 - x1, y2 - y1
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    body = NAVY_DK
    body_lt = NAVY
    # leave the last ~18% for the curved brass bell
    bx, by = x1 + ux * leng * 0.80, y1 + uy * leng * 0.80
    c.shade_taper(x1, y1, bx, by, 2.2, 2.6, body, body_lt, OUTLINE)
    # mouthpiece
    c.shade_taper(x1 - ux * 3, y1 - uy * 3, x1 + ux * 5, y1 + uy * 5,
                  1.4, 2.0, WHITE_DK, WHITE, body)
    # gold rings along the body
    for t in (0.22, 0.45, 0.68):
        kx, ky = x1 + ux * leng * t, y1 + uy * leng * t
        c.shade_taper(kx - ux, ky - uy, kx + ux, ky + uy, 2.6, 2.6, GOLD, GOLD_LT, GOLD_DK)
    # curved brass neck into an upturned bell (world-up hook, reads at any angle)
    # go forward then bend upward
    mid_x, mid_y = bx + ux * 6, by + uy * 6
    c.shade_taper(bx, by, mid_x, mid_y, 2.4, 2.6, GOLD, GOLD_LT, GOLD_DK)
    # hook up to mal_r
    c.shade_taper(mid_x, mid_y, x2, y2 - 4, 2.6, 3.4, GOLD, GOLD_LT, GOLD_DK)
    # hollow upturned bell — opening faces up, kept large enough to read
    c.shade_ellipse(x2, y2 - 7, 5.8, 5.0, GOLD, GOLD_LT, GOLD_DK)
    c.shade_ellipse(x2, y2 - 10, 3.6, 3.0, NAVY_DK, OUTLINE, GOLD_DK)
    c.set(int(x2 + 2), int(y2 - 7), GOLD_LT)


def paint_front(c, pose):
    draw_bassclarinet(c, pose)


def paint_flash(c, pose):
    if pose.mal_r:
        c.shade_disk(pose.mal_r[0], pose.mal_r[1], 5.5, VIOLET, WHITE, VIOLET_DK)


def render_pose(pose: Pose) -> Canvas:
    return render_character(pose, clothing="uniform", paint_front=paint_front, paint_flash=paint_flash)


def pose_idle(i):
    p = _base()
    bob = [0, 1, 2, 1][i]
    shift_upper(p, dy=bob)
    tilt = [-1, 0, 1, 0][i]
    p.mal_r = (p.mal_r[0], p.mal_r[1] + tilt)
    p.mal_l = (p.mal_l[0], p.mal_l[1] - tilt)
    return p


def pose_walk(i):
    p = _base()
    bounce = [1, -1, 0, 1, -1, 0][i]
    shift_upper(p, dy=bounce)
    # slightly longer stride to sell the height
    r_kn = [(60, 82), (56, 84), (48, 86), (46, 88), (52, 74), (62, 80)]
    r_an = [(62, 104), (58, 104), (46, 104), (44, 100), (50, 86), (64, 96)]
    r_toe = [(76, 109), (72, 109), (60, 109), (56, 107), (60, 90), (78, 102)]
    l_kn = [(36, 88), (40, 74), (50, 80), (50, 82), (46, 84), (40, 86)]
    l_an = [(28, 100), (36, 86), (64, 96), (52, 104), (48, 104), (38, 104)]
    l_toe = [(40, 107), (46, 90), (78, 102), (66, 109), (62, 109), (52, 109)]
    p.kn_r, p.an_r, p.toe_r = r_kn[i], r_an[i], r_toe[i]
    p.kn_l, p.an_l, p.toe_l = l_kn[i], l_an[i], l_toe[i]
    swing = [2, 1, -1, -2, -1, 1][i]
    p.mal_r = (p.mal_r[0] + swing, p.mal_r[1] - swing)
    p.mal_l = (p.mal_l[0] - swing * 0.4, p.mal_l[1] + swing * 0.3)
    p.leg_over = "right" if i in (0, 1, 5) else "left"
    return p


def pose_jump(i):
    p = _base()
    p.expression = "yell" if i in (1, 2) else "focus"
    if i == 0:
        shift_upper(p, dy=8)
        p.kn_l, p.kn_r = (38, 94), (56, 94)
        p.mal_l, p.mal_r = (30, 100), (80, 50)
    elif i == 1:
        shift_upper(p, dy=-4)
        p.kn_l, p.kn_r = (30, 72), (66, 70)
        p.an_l, p.an_r = (24, 84), (74, 80)
        p.toe_l, p.toe_r = (36, 90), (86, 84)
        p.hd_l, p.hd_r = (28, 40), (66, 36)
        p.mal_l, p.mal_r = (18, 70), (90, 18)
        p.leg_over = "right"
    elif i == 2:
        p.kn_l, p.kn_r = (32, 68), (68, 66)
        p.an_l, p.an_r = (26, 78), (78, 74)
        p.toe_l, p.toe_r = (38, 82), (88, 76)
        p.mal_l, p.mal_r = (16, 66), (90, 16)
        p.leg_over = "right"
    else:
        shift_upper(p, dy=1)
        p.kn_l, p.kn_r = (36, 84), (58, 84)
        p.an_l, p.an_r = (34, 100), (60, 100)
        p.toe_l, p.toe_r = (46, 106), (74, 106)
        p.mal_l, p.mal_r = (34, 96), (84, 40)
    return p


def pose_crouch(i):
    p = _base()
    p.expression = "focus"
    shift_upper(p, dy=16 + i)
    p.hip, p.hip_l, p.hip_r = (47, 86), (40, 86), (54, 86)
    p.kn_l, p.kn_r = (28, 98), (64, 98)
    p.hd_l, p.hd_r = (32, 84), (68, 70)
    # spear held low and ready
    p.mal_l, p.mal_r = (24, 100), (86, 52)
    return p


def pose_block(i):
    p = _base()
    p.expression = "grit"
    shift_upper(p, dy=3 + i)
    p.face = (p.face[0] - 2, p.face[1])
    # long pole held as a vertical / diagonal guard, off the face
    p.el_l, p.el_r = (36, 50), (64, 46)
    p.hd_l, p.hd_r = (48, 62), (60, 36)
    p.mal_l, p.mal_r = (50, 96), (68, 8)
    p.kn_l, p.kn_r = (38, 88), (56, 88)
    return p


def pose_punch(i):
    p = _base()
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-4, dy=1)
        # spear chambers back, high end stays off the face
        p.el_l, p.el_r = (24, 54), (40, 44)
        p.hd_l, p.hd_r = (18, 62), (30, 30)
        p.mal_l, p.mal_r = (10, 86), (24, 8)
        p.hands_over = "both"
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=6)
        # long halberd thrust, hooked bell leading
        p.el_l, p.el_r = (48, 52), (76, 48)
        p.hd_l, p.hd_r = (58, 54), (82, 46)
        p.mal_l, p.mal_r = (40, 64), (94, 28)
        p.hands_over = "right"
        p.flash = True
    else:
        p.expression = "focus"
        shift_upper(p, dx=2, dy=1)
        p.el_l, p.el_r = (46, 54), (74, 50)
        p.hd_l, p.hd_r = (56, 56), (80, 48)
        p.mal_l, p.mal_r = (38, 66), (92, 32)
        p.hands_over = "right"
    return p


def pose_kick(i):
    p = _base()
    p.leg_over = "right"
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-2, dy=2)
        p.kn_r, p.an_r, p.toe_r = (60, 64), (66, 52), (78, 48)
        p.mal_l, p.mal_r = (22, 50), (50, 12)
        p.kn_l, p.an_l, p.toe_l = (40, 92), (36, 104), (48, 109)
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=-5)
        p.kn_r, p.an_r, p.toe_r = (74, 62), (88, 58), (94, 56)
        p.mal_l, p.mal_r = (20, 46), (48, 10)
        p.kn_l, p.an_l, p.toe_l = (40, 92), (36, 104), (50, 109)
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=-4, dy=1)
        p.kn_r, p.an_r, p.toe_r = (76, 64), (90, 60), (94, 58)
        p.flash = True
        p.kn_l, p.an_l, p.toe_l = (40, 92), (36, 104), (50, 109)
    else:
        p.expression = "focus"
        shift_upper(p, dx=-1, dy=2)
        p.kn_r, p.an_r, p.toe_r = (62, 78), (68, 92), (80, 96)
        p.mal_l, p.mal_r = (34, 94), (84, 40)
        p.kn_l, p.an_l, p.toe_l = (40, 90), (36, 104), (48, 109)
    return p


def pose_special(i):
    p = _base()
    if i == 0:
        p.expression = "focus"
        # raise the spear, bell high
        shift_upper(p, dy=1)
        p.el_l, p.el_r = (34, 46), (60, 40)
        p.hd_l, p.hd_r = (40, 34), (64, 28)
        p.mal_l, p.mal_r = (32, 70), (78, 8)
        p.hands_over = "both"
    elif i == 1:
        p.expression = "grit"
        # start the downward slam
        p.el_l, p.el_r = (36, 52), (64, 50)
        p.hd_l, p.hd_r = (44, 48), (70, 52)
        p.mal_l, p.mal_r = (24, 40), (90, 64)
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=2, dy=3)
        # slam — bell hits the ground at the right edge
        p.el_l, p.el_r = (40, 60), (68, 62)
        p.hd_l, p.hd_r = (48, 66), (74, 70)
        p.mal_l, p.mal_r = (30, 50), (90, 100)
        p.kn_l, p.kn_r = (36, 90), (58, 90)
        p.flash = True
        p.hands_over = "right"
    elif i == 3:
        p.expression = "yell"
        shift_upper(p, dx=1, dy=3)
        p.el_l, p.el_r = (40, 62), (68, 64)
        p.hd_l, p.hd_r = (48, 68), (74, 72)
        p.mal_l, p.mal_r = (30, 52), (90, 102)
        p.flash = True
        p.hands_over = "right"
    elif i == 4:
        p.expression = "yell"
        shift_upper(p, dy=2)
        p.mal_l, p.mal_r = (32, 56), (88, 96)
        p.hands_over = "right"
    else:
        p.expression = "focus"
        p.mal_l, p.mal_r = (36, 96), (86, 40)
    return p


def pose_hit(i):
    p = _base()
    p.expression = "hit"
    shift_upper(p, dx=-6 if i == 0 else -9, dy=-1 if i == 0 else 2)
    p.mal_l, p.mal_r = (18, 70), (70, 30)
    p.kn_l, p.an_l, p.toe_l = (30, 90), (22, 104), (34, 109)
    return p


def pose_ko(i):
    p = _base()
    if i == 0:
        p.expression = "hit"
        shift_upper(p, dx=-8, dy=-2)
        p.mal_l, p.mal_r = (14, 60), (66, 24)
    elif i == 1:
        p.expression = "hit"
        p.face = (30, 42)
        p.sh_l, p.sh_r = (22, 56), (44, 50)
        p.el_l, p.el_r = (14, 56), (52, 44)
        p.hd_l, p.hd_r = (10, 50), (58, 36)
        p.mal_l, p.mal_r = (8, 72), (70, 28)
        p.hip, p.hip_l, p.hip_r = (42, 68), (36, 70), (50, 64)
        p.kn_l, p.an_l, p.toe_l = (36, 88), (28, 102), (38, 109)
        p.kn_r, p.an_r, p.toe_r = (64, 76), (76, 88), (88, 92)
        p.leg_over = "right"
    elif i == 2:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (32, 64)
        p.sh_l, p.sh_r = (22, 78), (42, 70)
        p.el_l, p.el_r = (12, 76), (52, 62)
        p.hd_l, p.hd_r = (8, 70), (58, 54)
        p.mal_l, p.mal_r = (6, 88), (68, 50)
        p.hip, p.hip_l, p.hip_r = (46, 84), (40, 86), (54, 80)
        p.kn_l, p.an_l, p.toe_l = (52, 96), (48, 106), (58, 109)
        p.kn_r, p.an_r, p.toe_r = (68, 84), (80, 90), (90, 92)
        p.leg_over = "right"
    else:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (30, 88)
        p.sh_l, p.sh_r = (28, 90), (44, 86)
        p.el_l, p.el_r = (16, 96), (52, 80)
        p.hd_l, p.hd_r = (10, 100), (58, 72)
        p.mal_l, p.mal_r = (8, 104), (70, 70)
        p.hip, p.hip_l, p.hip_r = (58, 90), (52, 92), (64, 88)
        p.kn_l, p.an_l, p.toe_l = (70, 94), (80, 98), (90, 100)
        p.kn_r, p.an_r, p.toe_r = (68, 78), (76, 68), (86, 64)
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
    # hook in the blue field to the right of the face, opening visible
    p.el_l, p.el_r = (32, 52), (54, 48)
    p.hd_l, p.hd_r = (36, 62), (56, 50)
    p.mal_l, p.mal_r = (22, 76), (66, 36)
    return bust_portrait(render_pose(p), NAVY, NAVY_LT, NAVY_DK, GOLD)


def render_projectile_frames() -> List[Canvas]:
    w, h = 96, 32
    frames = []
    for i in range(6):
        c = Canvas(w, h)
        # rumbling ground WAVE: travelling upper-half shock arcs on the floor
        origin = 6 + i * 10
        for k in range(2 + min(i, 3)):
            cx = origin + k * 16
            if cx > w - 6:
                break
            rx = 9 + k * 2 + i * 0.8
            ry = 6 + (k % 2) * 2
            col = VIOLET if k % 2 == 0 else GOLD
            dk = VIOLET_DK if k % 2 == 0 else GOLD_DK
            lt = WHITE if k == 0 else GOLD_LT
            c.shade_ellipse(cx, 28, rx, ry, col, lt, dk)
            for x in range(int(cx - rx - 2), int(cx + rx + 3)):
                for yy in range(28, h):
                    c.clear(x, yy)
            c.hline(int(cx - rx + 1), int(cx + rx - 1), 28, dk)
        frames.append(auto_outline(c, OUTLINE))
    return frames


def animation_boxes(name: str) -> dict:
    stand = {"x": 30, "y": 6, "w": 40, "h": 105}
    boxes = {"hurtbox": stand}
    if name == "crouch":
        boxes["hurtbox"] = {"x": 26, "y": 28, "w": 44, "h": 83}
    elif name == "punch":
        boxes["hitbox"] = {"frames": [1], "x": 78, "y": 20, "w": 18, "h": 24}
    elif name == "kick":
        boxes["hitbox"] = {"frames": [1, 2], "x": 72, "y": 48, "w": 22, "h": 18}
    elif name == "special":
        boxes["hitbox"] = {"frames": [2, 3], "x": 70, "y": 88, "w": 24, "h": 20}
        boxes["spawn_projectile_on"] = 3
    elif name == "ko":
        boxes["hurtbox"] = {"x": 8, "y": 40, "w": 80, "h": 71}
    return boxes
