"""Dante 'High C' Reyes — cocky, quick, jabs with the trumpet."""

from __future__ import annotations

import math
from typing import List

from pxart.body import Pose
from pxart.canvas import Canvas, auto_outline
from pxart.compose import STANDARD_ANIMS, bust_portrait, render_character, shift_upper
from pxart.looks import dante
from pxart.palette import (
    GOLD, GOLD_DK, GOLD_LT, NAVY, NAVY_DK, NAVY_LT, OUTLINE, WHITE, rgba, shade,
)

ID = "trumpet"
NAME = 'Dante "High C" Reyes'
INSTRUMENT = "Trumpet"
ANIMATIONS = STANDARD_ANIMS
LOOK = dante()

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 96,
    "frameHeight": 32,
    "frames": 6,
    "fps": 14,
    "loop": False,
    "anchor": {"x": 8, "y": 16},
    "notes": (
        "Blaring high-note sonic beam. Spawn on special frame index 2, "
        "origin at the trumpet bell, travelling right as a gold-orange beam."
    ),
}
NOTES = (
    "Cocky, compact-normal striker. Jabs with a short brass trumpet (bell first). "
    "Special is a gold-orange high-note sonic beam. Orange plume. Left hand often on hip."
)


def _base() -> Pose:
    # Compact, slightly forward-leaning ready stance. Left hand on hip.
    p = Pose(
        face=(49, 36),
        sh_l=(40, 51),
        sh_r=(58, 50),
        el_l=(32, 62),
        el_r=(68, 58),
        hd_l=(34, 72),   # planted on the hip
        hd_r=(66, 56),
        hip=(48, 72),
        hip_l=(43, 72),
        hip_r=(53, 72),
        kn_l=(40, 88),
        kn_r=(56, 86),
        an_l=(38, 104),
        an_r=(56, 104),
        toe_l=(50, 109),
        toe_r=(70, 109),
        inst=(70, 50),
        mal_l=(58, 60),  # mouthpiece
        mal_r=(80, 44),  # bell
        expression="idle",
        hands_over="right",
    )
    p.look = LOOK
    return p


def _brass_bell(c: Canvas, x, y, ux, uy, r=5.6) -> None:
    """Hollow flared bell. Opening stays visible in 3/4, even when pointing right."""
    c.shade_ellipse(x, y, r, r * 0.86, GOLD, GOLD_LT, GOLD_DK)
    ox = x + ux * 1.3 - uy * 0.5
    oy = y + uy * 1.3 + ux * 0.5
    c.shade_ellipse(ox, oy, r * 0.66, r * 0.52, NAVY_DK, OUTLINE, GOLD_DK)
    c.shade_ellipse(ox + ux * 0.7, oy + uy * 0.7, r * 0.30, r * 0.22, OUTLINE, NAVY_DK, GOLD_DK)
    c.set(int(x - uy * 2.6), int(y + ux * 2.6), GOLD_LT)
    c.set(int(x - uy * 2 - ux), int(y + ux * 2 - uy), WHITE)


def draw_trumpet(c: Canvas, p: Pose) -> None:
    a = p.mal_l or p.hd_r
    b = p.mal_r or p.inst
    if a is None or b is None:
        return
    x1, y1 = a
    x2, y2 = b
    vx, vy = x2 - x1, y2 - y1
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    # compact body, flare toward the bell
    c.shade_taper(x1, y1, x2, y2, 1.5, 3.0, GOLD, GOLD_LT, GOLD_DK)
    # mouthpiece cup
    c.shade_disk(x1 - ux * 1.2, y1 - uy * 1.2, 2.0, GOLD_LT, WHITE, GOLD_DK)
    # three valves mid-tube
    mx, my = x1 + ux * leng * 0.42, y1 + uy * leng * 0.42
    px, py = -uy, ux
    for k, off in enumerate((-2.2, 0.0, 2.2)):
        vx_, vy_ = mx + ux * off * 0.2 + px * 0.2, my + uy * off * 0.2 + py * 0.2
        c.shade_taper(vx_ , vy_, vx_ + px * 4.2, vy_ + py * 4.2, 1.1, 1.0, GOLD, GOLD_LT, GOLD_DK)
        c.set(int(vx_ + px * 4.4), int(vy_ + py * 4.4), GOLD_LT)
    # small under-loop so the silhouette reads as a trumpet, not a bat
    lx, ly = x1 + ux * leng * 0.50, y1 + uy * leng * 0.50
    c.shade_taper(lx - ux * 3, ly, lx + px * 5, ly + py * 5, 1.15, 1.15, GOLD, GOLD_LT, GOLD_DK)
    c.shade_taper(lx + px * 5, ly + py * 5, lx + ux * 5 + px * 3.5, ly + uy * 5 + py * 3.5,
                  1.15, 1.15, GOLD, GOLD_LT, GOLD_DK)
    _brass_bell(c, x2, y2, ux, uy, r=5.4)


def paint_front(c, pose):
    draw_trumpet(c, pose)


def paint_flash(c, pose):
    if pose.mal_r:
        x, y = pose.mal_r
        c.ellipse(x, y, 4.2, 3.4, rgba("#FF9F1C"), fill=False)
        c.ellipse(x, y, 3.2, 2.5, WHITE, fill=False)


def render_pose(pose: Pose) -> Canvas:
    return render_character(pose, clothing="uniform", paint_front=paint_front, paint_flash=paint_flash)


def pose_idle(i):
    p = _base()
    bob = [0, 1, 2, 1][i]
    shift_upper(p, dy=bob)
    # trumpet bobs, slight cocky tilt
    tilt = [0, -1, 0, 1][i]
    p.mal_r = (p.mal_r[0], p.mal_r[1] + tilt)
    p.mal_l = (p.mal_l[0], p.mal_l[1] - tilt)
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
    p.mal_l = (p.mal_l[0] + swing * 0.4, p.mal_l[1] - swing * 0.2)
    p.hd_l = (p.hd_l[0], p.hd_l[1] + bounce)  # keep hip-hand
    p.leg_over = "right" if i in (0, 1, 5) else "left"
    return p


def pose_jump(i):
    p = _base()
    p.expression = "yell" if i in (1, 2) else "focus"
    if i == 0:
        shift_upper(p, dy=8)
        p.kn_l, p.kn_r = (40, 94), (56, 94)
        p.mal_l, p.mal_r = (54, 70), (76, 58)
        p.hd_l = (36, 80)
    elif i == 1:
        shift_upper(p, dy=-4)
        p.kn_l, p.kn_r = (34, 76), (64, 74)
        p.an_l, p.an_r = (28, 88), (72, 84)
        p.toe_l, p.toe_r = (40, 94), (84, 88)
        p.hd_l, p.hd_r = (36, 50), (68, 44)
        p.mal_l, p.mal_r = (62, 40), (84, 26)
        p.leg_over = "right"
    elif i == 2:
        p.kn_l, p.kn_r = (34, 72), (66, 70)
        p.an_l, p.an_r = (28, 82), (76, 78)
        p.toe_l, p.toe_r = (40, 86), (86, 80)
        p.mal_l, p.mal_r = (60, 36), (84, 22)
        p.leg_over = "right"
    else:
        shift_upper(p, dy=1)
        p.kn_l, p.kn_r = (38, 86), (58, 86)
        p.an_l, p.an_r = (36, 100), (60, 100)
        p.toe_l, p.toe_r = (48, 106), (74, 106)
        p.mal_l, p.mal_r = (58, 62), (80, 48)
        p.hd_l = (34, 74)
    return p


def pose_crouch(i):
    p = _base()
    p.expression = "focus"
    shift_upper(p, dy=14 + i)
    p.hip, p.hip_l, p.hip_r = (48, 88), (41, 88), (55, 88)
    p.kn_l, p.kn_r = (32, 98), (64, 98)
    p.hd_l, p.hd_r = (36, 86), (66, 72)
    p.mal_l, p.mal_r = (58, 76), (80, 64)
    return p


def pose_block(i):
    p = _base()
    p.expression = "grit"
    shift_upper(p, dy=3 + i)
    p.face = (p.face[0] - 2, p.face[1])
    # trumpet raised as a short guard, off the face
    p.el_l, p.el_r = (38, 54), (64, 48)
    p.hd_l, p.hd_r = (50, 58), (62, 42)
    p.mal_l, p.mal_r = (54, 50), (76, 28)
    p.kn_l, p.kn_r = (40, 90), (56, 90)
    p.hands_over = "both"
    return p


def pose_punch(i):
    p = _base()
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-5, dy=1)
        # chamber the horn beside the shako, not over the face
        p.el_l, p.el_r = (30, 54), (42, 46)
        p.hd_l, p.hd_r = (26, 62), (36, 36)
        p.mal_l, p.mal_r = (30, 44), (22, 22)
        p.hands_over = "both"
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=7)
        # short, snappy jab — bell first to the right
        p.el_l, p.el_r = (50, 54), (76, 50)
        p.hd_l, p.hd_r = (60, 54), (84, 48)
        p.mal_l, p.mal_r = (72, 52), (94, 44)
        p.hands_over = "right"
        p.flash = True
    else:
        p.expression = "focus"
        shift_upper(p, dx=3, dy=1)
        p.el_l, p.el_r = (48, 56), (74, 52)
        p.hd_l, p.hd_r = (58, 56), (80, 50)
        p.mal_l, p.mal_r = (68, 54), (90, 46)
        p.hands_over = "right"
    return p


def pose_kick(i):
    p = _base()
    p.leg_over = "right"
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-2, dy=2)
        p.kn_r, p.an_r, p.toe_r = (60, 68), (66, 56), (78, 52)
        p.mal_l, p.mal_r = (40, 44), (58, 28)
        p.hd_l = (32, 64)
        p.kn_l, p.an_l, p.toe_l = (42, 94), (38, 104), (50, 109)
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=-5)
        p.kn_r, p.an_r, p.toe_r = (74, 64), (88, 60), (94, 58)
        p.mal_l, p.mal_r = (38, 40), (56, 24)
        p.kn_l, p.an_l, p.toe_l = (42, 94), (38, 104), (50, 109)
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=-4, dy=1)
        p.kn_r, p.an_r, p.toe_r = (76, 66), (90, 62), (94, 60)
        p.flash = True
        p.kn_l, p.an_l, p.toe_l = (42, 94), (38, 104), (50, 109)
    else:
        p.expression = "focus"
        shift_upper(p, dx=-1, dy=2)
        p.kn_r, p.an_r, p.toe_r = (62, 80), (68, 92), (80, 96)
        p.mal_l, p.mal_r = (56, 62), (78, 48)
        p.hd_l = (34, 74)
        p.kn_l, p.an_l, p.toe_l = (42, 92), (38, 104), (50, 109)
    return p


def pose_special(i):
    p = _base()
    if i == 0:
        p.expression = "focus"
        shift_upper(p, dy=1)
        # mouthpiece at the lips; BOTH gloves stay on the valves, right of the face
        p.el_l, p.el_r = (40, 46), (64, 42)
        p.hd_l, p.hd_r = (58, 44), (70, 40)
        p.mal_l, p.mal_r = (54, 38), (82, 36)
        p.hands_over = "both"
    elif i == 1:
        p.expression = "grit"
        p.el_l, p.el_r = (42, 44), (68, 42)
        p.hd_l, p.hd_r = (60, 44), (74, 40)
        p.mal_l, p.mal_r = (54, 38), (88, 36)
        p.hands_over = "both"
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=3)
        p.el_l, p.el_r = (44, 44), (72, 42)
        p.hd_l, p.hd_r = (62, 44), (78, 40)
        p.mal_l, p.mal_r = (56, 38), (92, 36)
        p.flash = True
        p.hands_over = "right"
    elif i == 3:
        p.expression = "yell"
        shift_upper(p, dx=2, dy=1)
        p.el_l, p.el_r = (42, 46), (72, 44)
        p.hd_l, p.hd_r = (60, 46), (78, 42)
        p.mal_l, p.mal_r = (56, 40), (92, 38)
        p.flash = True
        p.hands_over = "right"
    elif i == 4:
        p.expression = "yell"
        p.hd_l, p.hd_r = (58, 48), (74, 44)
        p.mal_l, p.mal_r = (54, 42), (86, 40)
        p.hands_over = "right"
    else:
        p.expression = "idle"
        p.mal_l, p.mal_r = (58, 60), (80, 46)
        p.hd_l = (34, 72)
        p.hands_over = "right"
    return p


def pose_hit(i):
    p = _base()
    p.expression = "hit"
    shift_upper(p, dx=-6 if i == 0 else -9, dy=-1 if i == 0 else 2)
    p.mal_l, p.mal_r = (36, 50), (58, 34)
    p.hd_l = (24, 66)
    p.kn_l, p.an_l, p.toe_l = (32, 90), (24, 104), (36, 109)
    return p


def pose_ko(i):
    p = _base()
    if i == 0:
        p.expression = "hit"
        shift_upper(p, dx=-8, dy=-2)
        p.mal_l, p.mal_r = (30, 44), (52, 28)
        p.hd_l = (22, 58)
    elif i == 1:
        p.expression = "hit"
        p.face = (30, 48)
        p.sh_l, p.sh_r = (22, 60), (44, 54)
        p.el_l, p.el_r = (14, 58), (52, 48)
        p.hd_l, p.hd_r = (10, 50), (58, 40)
        p.mal_l, p.mal_r = (48, 36), (70, 22)
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
        p.mal_l, p.mal_r = (50, 58), (72, 46)
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
        p.mal_l, p.mal_r = (54, 78), (74, 68)
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
    p.expression = "idle"
    # horn across the bust, bell out
    p.el_l, p.el_r = (36, 54), (64, 48)
    p.hd_l, p.hd_r = (40, 62), (66, 46)
    p.mal_l, p.mal_r = (56, 50), (86, 32)
    p.hands_over = "right"
    return bust_portrait(render_pose(p), NAVY, NAVY_LT, NAVY_DK, GOLD)


def render_projectile_frames() -> List[Canvas]:
    w, h = 96, 32
    frames = []
    orange = rgba("#FF9F1C")
    for i in range(6):
        c = Canvas(w, h)
        length = 28 + i * 11
        length = min(length, 90)
        y = 16
        # pointed scanline beam (no rounded taper caps — those read as a baseball bat)
        for x in range(6, 6 + length):
            tfrac = (x - 6) / max(length, 1)
            half = max(0, int(round(4.2 * (1.0 - tfrac) + 0.4)))
            for dy in range(-half, half + 1):
                ad = abs(dy)
                if ad == 0:
                    col = WHITE
                elif ad == 1:
                    col = GOLD_LT
                elif ad >= half:
                    col = orange
                else:
                    col = GOLD
                c.set(x, y + dy, col)
        c.set(6 + length, y, WHITE)
        c.set(6 + length + 1, y, GOLD_LT)
        c.set(6 + length + 2, y, orange)
        for k in range(1, 2 + i):
            px = 12 + k * 11
            if px >= 6 + length - 5:
                break
            c.set(px, y - 4, WHITE)
            c.set(px + 1, y - 3, GOLD_LT)
            c.set(px + 2, y - 2, orange)
            c.set(px, y + 4, WHITE)
            c.set(px + 1, y + 3, GOLD_LT)
            c.set(px + 2, y + 2, orange)
        c.ellipse(7, y, 3.5, 6.0 + i * 0.4, orange, fill=False)
        c.ellipse(7, y, 2.2, 4.0, GOLD_LT, fill=False)
        frames.append(auto_outline(c, OUTLINE))
    return frames


def animation_boxes(name: str) -> dict:
    stand = {"x": 30, "y": 12, "w": 40, "h": 99}
    boxes = {"hurtbox": stand}
    if name == "crouch":
        boxes["hurtbox"] = {"x": 28, "y": 28, "w": 42, "h": 83}
    elif name == "punch":
        boxes["hitbox"] = {"frames": [1], "x": 78, "y": 36, "w": 18, "h": 18}
    elif name == "kick":
        boxes["hitbox"] = {"frames": [1, 2], "x": 72, "y": 50, "w": 22, "h": 18}
    elif name == "special":
        boxes["hitbox"] = {"frames": [2, 3], "x": 80, "y": 32, "w": 16, "h": 18}
        boxes["spawn_projectile_on"] = 2
    elif name == "ko":
        boxes["hurtbox"] = {"x": 8, "y": 40, "w": 80, "h": 71}
    return boxes
