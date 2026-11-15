"""Maya 'Squeak' Patel — balanced mid-weight, clarinet used as a short baton/sword."""

from __future__ import annotations

import math
from typing import List

from pxart.body import Pose
from pxart.canvas import Canvas, auto_outline
from pxart.compose import STANDARD_ANIMS, bust_portrait, render_character, shift_upper
from pxart.looks import maya
from pxart.palette import (
    GOLD, GOLD_DK, GOLD_LT, NAVY, NAVY_DK, NAVY_LT, OUTLINE, WHITE, WHITE_DK, rgba,
)

ID = "clarinet"
NAME = 'Maya "Squeak" Patel'
INSTRUMENT = "Clarinet"
ANIMATIONS = STANDARD_ANIMS
LOOK = maya()

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 96,
    "frameHeight": 48,
    "frames": 6,
    "fps": 14,
    "loop": False,
    "anchor": {"x": 8, "y": 28},
    "notes": (
        "Squeaky reed note-swarm. Spawn on special frame index 2, "
        "origin at the clarinet bell, scattering right and slightly up."
    ),
}
NOTES = (
    "Balanced medium build. The clarinet is a short dark baton / sword for slashes "
    "and stabs. Special is a lime-gold swarm of squeaky reed notes. Lime plume."
)

LIME = rgba("#8AC926")
LIME_DK = rgba("#4E7A14")


def _base() -> Pose:
    # Medium, balanced stance — between Penny-slim and a standard marcher.
    p = Pose(
        face=(47, 34),
        sh_l=(39, 50),
        sh_r=(57, 50),
        el_l=(32, 62),
        el_r=(68, 58),
        hd_l=(34, 70),
        hd_r=(72, 52),
        hip=(47, 71),
        hip_l=(42, 71),
        hip_r=(52, 71),
        kn_l=(39, 88),
        kn_r=(55, 86),
        an_l=(37, 104),
        an_r=(55, 104),
        toe_l=(49, 109),
        toe_r=(69, 109),
        inst=(62, 56),
        mal_l=(50, 68),  # mouthpiece / hilt
        mal_r=(82, 40),  # bell / tip  — shorter than the flute staff
        expression="idle",
        hands_over="both",
    )
    p.look = LOOK
    return p


def draw_clarinet(c: Canvas, p: Pose) -> None:
    """Short dark woodwind: mouthpiece at mal_l, flared bell at mal_r."""
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
    # body
    c.shade_taper(x1, y1, x2, y2, 2.0, 2.4, body, body_lt, OUTLINE)
    # mouthpiece / reed (lighter, slightly back of mal_l)
    c.shade_taper(x1 - ux * 3, y1 - uy * 3, x1 + ux * 4, y1 + uy * 4,
                  1.3, 1.8, WHITE_DK, WHITE, body)
    # gold barrel rings
    for t in (0.28, 0.55, 0.78):
        kx, ky = x1 + ux * leng * t, y1 + uy * leng * t
        c.shade_taper(kx - ux * 1.1, ky - uy * 1.1, kx + ux * 1.1, ky + uy * 1.1,
                      2.3, 2.3, GOLD, GOLD_LT, GOLD_DK)
    # a few key nubs (gold, keeps the palette tight)
    px, py = -uy, ux
    for t in (0.40, 0.50, 0.62, 0.70):
        kx, ky = x1 + ux * leng * t, y1 + uy * leng * t
        c.set(int(kx + px * 2.2), int(ky + py * 2.2), GOLD)
    # flared bell
    c.shade_ellipse(x2, y2, 3.8, 3.2, body_lt, GOLD, OUTLINE)
    c.shade_ellipse(x2 + ux * 1.2, y2 + uy * 1.2, 2.2, 1.8, OUTLINE, NAVY_DK, body)


def paint_front(c, pose):
    draw_clarinet(c, pose)


def paint_flash(c, pose):
    if pose.mal_r:
        c.shade_disk(pose.mal_r[0], pose.mal_r[1], 4.5, LIME, WHITE, LIME_DK)


def render_pose(pose: Pose) -> Canvas:
    return render_character(pose, clothing="uniform", paint_front=paint_front, paint_flash=paint_flash)


def pose_idle(i):
    p = _base()
    bob = [0, 1, 2, 1][i]
    shift_upper(p, dy=bob)
    tilt = [-1, 0, 1, 0][i]
    p.mal_r = (p.mal_r[0], p.mal_r[1] + tilt)
    p.mal_l = (p.mal_l[0], p.mal_l[1] - tilt * 0.5)
    return p


def pose_walk(i):
    p = _base()
    bounce = [1, -1, 0, 1, -1, 0][i]
    shift_upper(p, dy=bounce)
    r_kn = [(60, 84), (56, 86), (48, 88), (46, 90), (52, 76), (62, 82)]
    r_an = [(62, 104), (58, 104), (46, 104), (44, 100), (50, 86), (64, 96)]
    r_toe = [(76, 109), (72, 109), (60, 109), (56, 107), (60, 90), (78, 102)]
    l_kn = [(36, 90), (40, 76), (50, 82), (50, 84), (46, 86), (40, 88)]
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
        p.mal_l, p.mal_r = (44, 78), (74, 58)
    elif i == 1:
        shift_upper(p, dy=-3)
        p.kn_l, p.kn_r = (32, 76), (66, 74)
        p.an_l, p.an_r = (26, 88), (74, 84)
        p.toe_l, p.toe_r = (38, 94), (86, 88)
        p.hd_l, p.hd_r = (30, 40), (64, 36)
        p.mal_l, p.mal_r = (36, 52), (80, 24)
        p.leg_over = "right"
    elif i == 2:
        p.kn_l, p.kn_r = (34, 72), (68, 70)
        p.an_l, p.an_r = (28, 82), (78, 78)
        p.toe_l, p.toe_r = (40, 86), (88, 80)
        p.mal_l, p.mal_r = (34, 48), (80, 22)
        p.leg_over = "right"
    else:
        shift_upper(p, dy=1)
        p.kn_l, p.kn_r = (36, 86), (58, 86)
        p.an_l, p.an_r = (34, 100), (60, 100)
        p.toe_l, p.toe_r = (46, 106), (74, 106)
        p.mal_l, p.mal_r = (48, 70), (80, 46)
    return p


def pose_crouch(i):
    p = _base()
    p.expression = "focus"
    shift_upper(p, dy=14 + i)
    p.hip, p.hip_l, p.hip_r = (47, 88), (40, 88), (54, 88)
    p.kn_l, p.kn_r = (30, 98), (64, 98)
    p.hd_l, p.hd_r = (34, 84), (70, 70)
    p.mal_l, p.mal_r = (44, 88), (80, 62)
    return p


def pose_block(i):
    p = _base()
    p.expression = "grit"
    shift_upper(p, dy=3 + i)
    p.face = (p.face[0] - 2, p.face[1])
    # short baton held as a high guard, to the right of the face
    p.el_l, p.el_r = (38, 54), (64, 48)
    p.hd_l, p.hd_r = (50, 58), (60, 40)
    p.mal_l, p.mal_r = (52, 70), (66, 20)
    p.kn_l, p.kn_r = (38, 90), (56, 90)
    return p


def pose_punch(i):
    p = _base()
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-4, dy=1)
        # chamber the baton back and up, beside the shako
        p.el_l, p.el_r = (26, 54), (42, 46)
        p.hd_l, p.hd_r = (22, 50), (34, 32)
        p.mal_l, p.mal_r = (16, 62), (28, 16)
        p.hands_over = "both"
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=6)
        # short sword thrust / slash to the right
        p.el_l, p.el_r = (48, 54), (76, 50)
        p.hd_l, p.hd_r = (58, 52), (84, 46)
        p.mal_l, p.mal_r = (52, 58), (94, 38)
        p.hands_over = "right"
        p.flash = True
    else:
        p.expression = "focus"
        shift_upper(p, dx=2, dy=1)
        p.el_l, p.el_r = (46, 56), (74, 52)
        p.hd_l, p.hd_r = (56, 54), (80, 48)
        p.mal_l, p.mal_r = (50, 60), (90, 42)
        p.hands_over = "right"
    return p


def pose_kick(i):
    p = _base()
    p.leg_over = "right"
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-2, dy=2)
        p.kn_r, p.an_r, p.toe_r = (60, 68), (66, 56), (78, 52)
        p.mal_l, p.mal_r = (30, 48), (52, 24)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (48, 109)
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=-5)
        p.kn_r, p.an_r, p.toe_r = (74, 64), (88, 60), (94, 58)
        p.mal_l, p.mal_r = (28, 44), (50, 20)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (50, 109)
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=-4, dy=1)
        p.kn_r, p.an_r, p.toe_r = (76, 66), (90, 62), (94, 60)
        p.flash = True
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (50, 109)
    else:
        p.expression = "focus"
        shift_upper(p, dx=-1, dy=2)
        p.kn_r, p.an_r, p.toe_r = (62, 80), (68, 92), (80, 96)
        p.mal_l, p.mal_r = (48, 70), (80, 48)
        p.kn_l, p.an_l, p.toe_l = (40, 92), (36, 104), (48, 109)
    return p


def pose_special(i):
    p = _base()
    if i == 0:
        p.expression = "focus"
        shift_upper(p, dy=2)
        # clarinet rises toward the mouth, held clear of the face
        p.el_l, p.el_r = (36, 48), (62, 44)
        p.hd_l, p.hd_r = (42, 42), (66, 40)
        p.mal_l, p.mal_r = (48, 44), (80, 34)
        p.hands_over = "both"
    elif i == 1:
        p.expression = "grit"
        p.el_l, p.el_r = (40, 46), (66, 44)
        p.hd_l, p.hd_r = (48, 42), (70, 40)
        p.mal_l, p.mal_r = (52, 44), (86, 36)
        p.hands_over = "both"
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=3)
        p.el_l, p.el_r = (42, 46), (70, 44)
        p.hd_l, p.hd_r = (50, 42), (76, 40)
        p.mal_l, p.mal_r = (54, 44), (92, 36)
        p.flash = True
        p.hands_over = "right"
    elif i == 3:
        p.expression = "yell"
        shift_upper(p, dx=2, dy=1)
        p.el_l, p.el_r = (40, 48), (70, 46)
        p.hd_l, p.hd_r = (48, 44), (76, 42)
        p.mal_l, p.mal_r = (52, 46), (92, 38)
        p.flash = True
        p.hands_over = "right"
    elif i == 4:
        p.expression = "yell"
        p.mal_l, p.mal_r = (50, 48), (86, 40)
        p.hands_over = "right"
    else:
        p.expression = "focus"
        p.mal_l, p.mal_r = (50, 68), (82, 42)
    return p


def pose_hit(i):
    p = _base()
    p.expression = "hit"
    shift_upper(p, dx=-6 if i == 0 else -9, dy=-1 if i == 0 else 2)
    p.mal_l, p.mal_r = (22, 52), (56, 32)
    p.kn_l, p.an_l, p.toe_l = (30, 90), (22, 104), (34, 109)
    return p


def pose_ko(i):
    p = _base()
    if i == 0:
        p.expression = "hit"
        shift_upper(p, dx=-8, dy=-2)
        p.mal_l, p.mal_r = (18, 46), (54, 28)
    elif i == 1:
        p.expression = "hit"
        p.face = (30, 48)
        p.sh_l, p.sh_r = (22, 60), (44, 54)
        p.el_l, p.el_r = (14, 58), (52, 48)
        p.hd_l, p.hd_r = (10, 50), (58, 40)
        p.mal_l, p.mal_r = (16, 56), (52, 32)
        p.hip, p.hip_l, p.hip_r = (42, 72), (36, 74), (50, 68)
        p.kn_l, p.an_l, p.toe_l = (36, 90), (28, 102), (38, 109)
        p.kn_r, p.an_r, p.toe_r = (64, 78), (76, 88), (88, 92)
        p.leg_over = "right"
    elif i == 2:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (32, 68)
        p.sh_l, p.sh_r = (22, 80), (42, 72)
        p.el_l, p.el_r = (12, 78), (52, 64)
        p.hd_l, p.hd_r = (8, 72), (58, 56)
        p.mal_l, p.mal_r = (14, 78), (50, 52)
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
        p.mal_l, p.mal_r = (16, 102), (52, 78)
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
    p.el_l, p.el_r = (34, 54), (64, 48)
    p.hd_l, p.hd_r = (40, 60), (70, 44)
    p.mal_l, p.mal_r = (44, 68), (88, 28)
    return bust_portrait(render_pose(p), NAVY, NAVY_LT, NAVY_DK, GOLD)


def _note(c: Canvas, x, y, col, stem=6):
    """Tiny eighth-note: oval head + stem + optional flag."""
    c.shade_ellipse(x, y, 2.4, 1.8, col, WHITE, LIME_DK)
    c.vline(int(x + 2), int(y - stem), int(y), col)
    # flag
    c.set(int(x + 3), int(y - stem), col)
    c.set(int(x + 4), int(y - stem + 1), col)
    c.set(int(x + 5), int(y - stem + 2), col)


def render_projectile_frames() -> List[Canvas]:
    w, h = 96, 48
    frames = []
    # pre-planned note paths (x, y, delay)
    paths = [
        (0, 28, 0),
        (4, 20, 0),
        (2, 34, 1),
        (8, 16, 1),
        (6, 38, 2),
        (10, 24, 2),
        (12, 12, 3),
        (14, 32, 3),
    ]
    colors = [LIME, GOLD, WHITE, LIME, GOLD, LIME, GOLD_LT, LIME]
    for i in range(6):
        c = Canvas(w, h)
        for n, (x0, y0, delay) in enumerate(paths):
            if i < delay:
                continue
            t = i - delay
            x = 8 + x0 + t * 14
            y = y0 + int(math.sin((t + n) * 0.9) * 4) - t  # slight rise
            if 2 <= x < w - 2 and 4 <= y < h - 2:
                _note(c, x, y, colors[n], stem=5 + (n % 3))
        frames.append(auto_outline(c, OUTLINE))
    return frames


def animation_boxes(name: str) -> dict:
    stand = {"x": 30, "y": 10, "w": 40, "h": 101}
    boxes = {"hurtbox": stand}
    if name == "crouch":
        boxes["hurtbox"] = {"x": 28, "y": 26, "w": 42, "h": 85}
    elif name == "punch":
        boxes["hitbox"] = {"frames": [1], "x": 78, "y": 34, "w": 18, "h": 18}
    elif name == "kick":
        boxes["hitbox"] = {"frames": [1, 2], "x": 72, "y": 50, "w": 22, "h": 18}
    elif name == "special":
        boxes["hitbox"] = {"frames": [2, 3], "x": 80, "y": 28, "w": 16, "h": 22}
        boxes["spawn_projectile_on"] = 2
    elif name == "ko":
        boxes["hurtbox"] = {"x": 8, "y": 40, "w": 80, "h": 71}
    return boxes
