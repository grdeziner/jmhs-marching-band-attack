"""Penny 'Mallets' Okafor — nimble dual-stick xylophone / glock striker."""

from __future__ import annotations

import math
from typing import List

from pxart.body import Pose, get_look
from pxart.canvas import Canvas, auto_outline
from pxart.compose import STANDARD_ANIMS, bust_portrait, render_character, shift_upper
from pxart.looks import penny
from pxart.palette import (
    GOLD, GOLD_DK, GOLD_LT, NAVY, NAVY_DK, NAVY_LT, OUTLINE,
    SILVER, SILVER_DK, SILVER_LT, WHITE, WOOD, WOOD_DK, WOOD_LT,
    rgba, shade,
)

ID = "xylophone"
NAME = 'Penny "Mallets" Okafor'
INSTRUMENT = "Xylophone"
ANIMATIONS = STANDARD_ANIMS
LOOK = penny()

# Colored bar-tone notes for the special projectile
NOTE_COLS = [
    rgba("#FF595E"),
    rgba("#FF9F1C"),
    rgba("#8AC926"),
    rgba("#7EF9FF"),
    rgba("#A78BFA"),
]

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 48,
    "frameHeight": 64,
    "frames": 6,
    "fps": 12,
    "loop": False,
    "anchor": {"x": 8, "y": 56},
    "notes": (
        "Rising colored chime-note bars. Spawn on special frame index 3, "
        "origin near the mallets, drifting up and right."
    ),
}
NOTES = (
    "Slim dual-stick striker. A small glockenspiel is slung at the hip. "
    "Special flurries the mallets and launches the chime-note projectile."
)


def _base() -> Pose:
    p = Pose(
        face=(47, 36),
        sh_l=(38, 50),
        sh_r=(58, 50),
        el_l=(30, 62),
        el_r=(68, 60),
        hd_l=(28, 52),
        hd_r=(72, 50),
        hip=(47, 72),
        hip_l=(42, 72),
        hip_r=(52, 72),
        kn_l=(38, 88),
        kn_r=(56, 88),
        an_l=(36, 104),
        an_r=(56, 104),
        toe_l=(48, 109),
        toe_r=(70, 109),
        inst=(36, 78),  # slung glock at left hip
        mal_l=(22, 36),
        mal_r=(82, 34),
        expression="idle",
        hands_over="both",
    )
    p.look = LOOK
    return p


def draw_stick(c: Canvas, hand, tip, head_r=3.0) -> None:
    if hand is None or tip is None:
        return
    hx, hy = hand
    tx, ty = tip
    vx, vy = tx - hx, ty - hy
    leng = math.hypot(vx, vy) or 1
    # longer, thinner concert-mallet shaft
    bx, by = hx - vx / leng * 4, hy - vy / leng * 4
    c.shade_taper(bx, by, tx, ty, 1.15, 0.9, WOOD, WOOD_LT, WOOD_DK)
    # small yarn / plastic head
    c.shade_disk(tx, ty, head_r, rgba("#F6F2EA"), rgba("#FFFFFF"), rgba("#B9B3A6"))
    c.shade_disk(tx, ty, head_r * 0.45, LOOK.plume, LOOK.plume_lt, LOOK.plume_dk)


def draw_glock(c: Canvas, pose: Pose) -> None:
    """A small marching glockenspiel slung at the hip."""
    cx, cy = pose.inst
    # rectangular glockenspiel frame, slightly tilted
    c.rect(int(cx - 11), int(cy - 6), 22, 12, SILVER_DK, fill=True)
    c.rect(int(cx - 10), int(cy - 5), 20, 10, SILVER, fill=True)
    c.rect(int(cx - 9), int(cy - 4), 18, 8, SILVER_LT, fill=True)
    # graded bars, taller on the left (typical glock / xylo)
    for i, dx in enumerate(range(-8, 9, 2)):
        h = 7 - i // 2
        col = (GOLD_LT, GOLD, GOLD, GOLD_DK, GOLD, GOLD_LT, GOLD, GOLD_DK, GOLD)[i]
        c.vline(int(cx + dx), int(cy - h // 2), int(cy + h // 2), col)
        c.vline(int(cx + dx) + 1, int(cy - h // 2 + 1), int(cy + h // 2 - 1), GOLD_LT if col != GOLD_LT else WHITE)
    # strap up to the left shoulder
    c.shade_taper(pose.sh_l[0], pose.sh_l[1], cx - 6, cy - 5, 1.4, 1.4, SILVER, SILVER_LT, SILVER_DK)


def paint_mid(c, pose):
    draw_glock(c, pose)


def paint_front(c, pose):
    draw_stick(c, pose.hd_l, pose.mal_l)
    draw_stick(c, pose.hd_r, pose.mal_r)


def paint_flash(c, pose):
    if pose.mal_r:
        c.shade_disk(pose.mal_r[0], pose.mal_r[1], 4, rgba("#FFF6C8"), rgba("#FFFFFF"), GOLD_LT)


def render_pose(pose: Pose) -> Canvas:
    return render_character(
        pose, clothing="uniform",
        paint_mid=paint_mid, paint_front=paint_front, paint_flash=paint_flash,
    )


def pose_idle(i):
    p = _base()
    bob = [0, 1, 2, 1][i]
    shift_upper(p, dy=bob)
    # light stick twirl / ready bounce
    p.mal_l = (p.mal_l[0] - (i % 2), p.mal_l[1] + [0, -2, 0, 2][i])
    p.mal_r = (p.mal_r[0] + (i % 2), p.mal_r[1] + [0, 2, 0, -2][i])
    return p


def pose_walk(i):
    p = _base()
    bounce = [1, -1, 0, 1, -1, 0][i]
    shift_upper(p, dy=bounce)
    r_kn = [(60, 86), (56, 88), (48, 90), (46, 92), (52, 78), (62, 84)]
    r_an = [(62, 104), (58, 104), (46, 104), (44, 100), (50, 86), (64, 96)]
    r_toe = [(76, 109), (72, 109), (60, 109), (56, 107), (60, 90), (78, 102)]
    l_kn = [(36, 92), (40, 78), (50, 84), (50, 86), (46, 88), (40, 90)]
    l_an = [(28, 100), (36, 86), (64, 96), (52, 104), (48, 104), (38, 104)]
    l_toe = [(40, 107), (46, 90), (78, 102), (66, 109), (62, 109), (52, 109)]
    p.kn_r, p.an_r, p.toe_r = r_kn[i], r_an[i], r_toe[i]
    p.kn_l, p.an_l, p.toe_l = l_kn[i], l_an[i], l_toe[i]
    swing = [2, 1, -1, -2, -1, 1][i]
    p.hd_r = (p.hd_r[0] + swing, p.hd_r[1] - swing)
    p.mal_r = (p.mal_r[0] + swing * 1.3, p.mal_r[1] - swing * 1.4)
    p.hd_l = (p.hd_l[0] - swing, p.hd_l[1] + swing * 0.5)
    p.mal_l = (p.mal_l[0] - swing * 1.3, p.mal_l[1] + swing * 1.2)
    p.leg_over = "right" if i in (0, 1, 5) else "left"
    return p


def pose_jump(i):
    p = _base()
    p.expression = "yell" if i in (1, 2) else "focus"
    if i == 0:
        shift_upper(p, dy=8)
        p.kn_l, p.kn_r = (38, 94), (56, 94)
        p.el_l, p.el_r = (26, 66), (70, 66)
        p.hd_l, p.hd_r = (24, 58), (74, 58)
        p.mal_l, p.mal_r = (16, 46), (84, 46)
    elif i == 1:
        shift_upper(p, dy=-2)
        p.kn_l, p.kn_r = (34, 78), (64, 76)
        p.an_l, p.an_r = (28, 90), (72, 86)
        p.toe_l, p.toe_r = (40, 96), (84, 90)
        p.hd_l, p.hd_r = (22, 36), (76, 34)
        p.mal_l, p.mal_r = (14, 22), (88, 20)
        p.leg_over = "right"
    elif i == 2:
        p.kn_l, p.kn_r = (36, 74), (66, 72)
        p.an_l, p.an_r = (30, 84), (76, 80)
        p.toe_l, p.toe_r = (42, 88), (86, 82)
        p.hd_l, p.hd_r = (24, 32), (76, 32)
        p.mal_l, p.mal_r = (16, 18), (88, 18)
        p.leg_over = "right"
    else:
        shift_upper(p, dy=1)
        p.kn_l, p.kn_r = (36, 86), (58, 86)
        p.an_l, p.an_r = (34, 100), (60, 100)
        p.toe_l, p.toe_r = (46, 106), (74, 106)
        p.hd_l, p.hd_r = (26, 60), (74, 60)
        p.mal_l, p.mal_r = (18, 48), (84, 48)
    return p


def pose_crouch(i):
    p = _base()
    p.expression = "focus"
    drop = 14 + i
    shift_upper(p, dy=drop)
    p.hip, p.hip_l, p.hip_r = (47, 88), (40, 88), (54, 88)
    p.kn_l, p.kn_r = (30, 98), (64, 98)
    p.hd_l, p.hd_r = (26, 78 + i), (74, 76 + i)
    p.mal_l, p.mal_r = (16, 66 + i), (86, 64 + i)
    return p


def pose_block(i):
    p = _base()
    p.expression = "grit"
    shift_upper(p, dy=3 + i)
    p.face = (p.face[0] - 3, p.face[1])
    # sticks crossed in a high guard, off the face
    p.el_l, p.el_r = (30, 54), (70, 52)
    p.hd_l, p.hd_r = (34, 46), (74, 44)
    p.mal_l, p.mal_r = (48, 28), (88, 30)
    p.kn_l, p.kn_r = (38, 92), (56, 92)
    return p


def pose_punch(i):
    p = _base()
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-3, dy=1)
        p.el_r, p.hd_r, p.mal_r = (50, 44), (38, 28), (28, 12)
        p.el_l, p.hd_l, p.mal_l = (28, 64), (26, 56), (18, 44)
        p.hands_over = "right"
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=5)
        p.el_r, p.hd_r, p.mal_r = (76, 50), (88, 44), (94, 36)
        p.el_l, p.hd_l, p.mal_l = (26, 66), (24, 58), (16, 46)
        p.hands_over = "right"
        p.flash = True
    else:
        p.expression = "focus"
        shift_upper(p, dx=2, dy=1)
        p.el_r, p.hd_r, p.mal_r = (74, 54), (84, 50), (92, 42)
        p.hands_over = "right"
    return p


def pose_kick(i):
    p = _base()
    p.leg_over = "right"
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-2, dy=2)
        p.kn_r, p.an_r, p.toe_r = (60, 70), (66, 58), (78, 54)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (48, 109)
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=-4)
        p.kn_r, p.an_r, p.toe_r = (72, 66), (86, 62), (94, 60)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (50, 109)
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=-3, dy=1)
        p.kn_r, p.an_r, p.toe_r = (74, 68), (88, 64), (94, 62)
        p.flash = True
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (50, 109)
    else:
        p.expression = "focus"
        shift_upper(p, dx=-1, dy=2)
        p.kn_r, p.an_r, p.toe_r = (62, 80), (68, 92), (80, 96)
        p.kn_l, p.an_l, p.toe_l = (40, 92), (36, 104), (48, 109)
    return p


def pose_special(i):
    p = _base()
    if i == 0:
        p.expression = "focus"
        shift_upper(p, dy=2)
        p.hd_l, p.hd_r = (30, 40), (70, 40)
        p.mal_l, p.mal_r = (24, 22), (80, 22)
    elif i == 1:
        p.expression = "grit"
        shift_upper(p, dy=2)
        p.hd_l, p.hd_r = (28, 30), (72, 30)
        p.mal_l, p.mal_r = (22, 12), (82, 12)
    elif i == 2:
        # flurry start — sticks crossing in front
        p.expression = "yell"
        p.hd_l, p.hd_r = (42, 56), (66, 52)
        p.mal_l, p.mal_r = (60, 40), (48, 36)
        p.flash = True
    elif i == 3:
        # opposite flurry + notes launch
        p.expression = "yell"
        p.hd_l, p.hd_r = (40, 54), (72, 56)
        p.mal_l, p.mal_r = (52, 38), (88, 42)
        p.flash = True
    elif i == 4:
        p.expression = "yell"
        p.hd_l, p.hd_r = (36, 40), (74, 40)
        p.mal_l, p.mal_r = (28, 22), (88, 20)
    else:
        p.expression = "focus"
        p.hd_l, p.hd_r = (30, 50), (72, 50)
        p.mal_l, p.mal_r = (22, 36), (82, 34)
    return p


def pose_hit(i):
    p = _base()
    p.expression = "hit"
    dx = -6 if i == 0 else -9
    shift_upper(p, dx=dx, dy=-1 if i == 0 else 2)
    p.hd_l, p.hd_r = (18, 44), (70, 42)
    p.mal_l, p.mal_r = (10, 30), (80, 28)
    p.kn_l, p.an_l, p.toe_l = (30, 90), (22, 104), (34, 109)
    return p


def pose_ko(i):
    p = _base()
    if i == 0:
        p.expression = "hit"
        shift_upper(p, dx=-8, dy=-2)
        p.hd_l, p.hd_r = (16, 36), (68, 36)
        p.mal_l, p.mal_r = (8, 24), (78, 22)
    elif i == 1:
        p.expression = "hit"
        p.face = (30, 48)
        p.sh_l, p.sh_r = (22, 60), (44, 54)
        p.el_l, p.el_r = (14, 58), (52, 48)
        p.hd_l, p.hd_r = (10, 50), (58, 40)
        p.mal_l, p.mal_r = (4, 38), (68, 28)
        p.hip, p.hip_l, p.hip_r = (42, 72), (36, 74), (50, 68)
        p.kn_l, p.an_l, p.toe_l = (36, 90), (28, 102), (38, 109)
        p.kn_r, p.an_r, p.toe_r = (64, 78), (76, 88), (88, 92)
        p.inst = (32, 70)
        p.leg_over = "right"
    elif i == 2:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (32, 68)
        p.sh_l, p.sh_r = (22, 80), (42, 72)
        p.el_l, p.el_r = (12, 78), (52, 64)
        p.hd_l, p.hd_r = (8, 72), (58, 56)
        p.mal_l, p.mal_r = (4, 64), (66, 46)
        p.hip, p.hip_l, p.hip_r = (46, 84), (40, 86), (54, 80)
        p.kn_l, p.an_l, p.toe_l = (52, 96), (48, 106), (58, 109)
        p.kn_r, p.an_r, p.toe_r = (68, 84), (80, 90), (90, 92)
        p.inst = (36, 84)
        p.leg_over = "right"
    else:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (30, 88)
        p.sh_l, p.sh_r = (28, 90), (44, 86)
        p.el_l, p.el_r = (16, 96), (52, 80)
        p.hd_l, p.hd_r = (10, 100), (58, 72)
        p.mal_l, p.mal_r = (6, 104), (64, 64)
        p.hip, p.hip_l, p.hip_r = (58, 90), (52, 92), (64, 88)
        p.kn_l, p.an_l, p.toe_l = (70, 94), (80, 98), (90, 100)
        p.kn_r, p.an_r, p.toe_r = (68, 78), (76, 68), (86, 64)
        p.inst = (44, 94)
        p.leg_over = "right"
        p.hands_over = "right"
    return p


POSE_FN = {
    "idle": pose_idle, "walk": pose_walk, "jump": pose_jump, "crouch": pose_crouch,
    "block": pose_block, "punch": pose_punch, "kick": pose_kick, "special": pose_special,
    "hit": pose_hit, "ko": pose_ko,
}


def render_frame(animation: str, index: int) -> Canvas:
    return render_pose(POSE_FN[animation](index))


def render_portrait() -> Canvas:
    p = _base()
    p.expression = "focus"
    p.mal_r = (86, 28)
    p.hd_r = (74, 46)
    return bust_portrait(render_pose(p), NAVY, NAVY_LT, NAVY_DK, GOLD)


def render_projectile_frames() -> List[Canvas]:
    w, h = 48, 64
    frames = []
    for i in range(6):
        c = Canvas(w, h)
        # several colored bars / note-heads rising and drifting right
        for k, col in enumerate(NOTE_COLS):
            ox = 8 + i * 4 + k * 5
            oy = 56 - i * 8 - (k % 3) * 6
            # bar
            c.rect(int(ox), int(oy - 8 - k), 4, 10 + (k % 3) * 2, col, fill=True)
            c.rect(int(ox) + 1, int(oy - 7 - k), 2, 3, shade(col, 1.4), fill=True)
            # little note head
            c.shade_disk(ox + 5, oy + 2, 2.4, col, shade(col, 1.4), shade(col, 0.6))
        frames.append(auto_outline(c, OUTLINE))
    return frames


def animation_boxes(name: str) -> dict:
    stand = {"x": 28, "y": 12, "w": 44, "h": 99}
    boxes = {"hurtbox": stand}
    if name == "crouch":
        boxes["hurtbox"] = {"x": 26, "y": 28, "w": 46, "h": 83}
    elif name == "punch":
        boxes["hitbox"] = {"frames": [1], "x": 80, "y": 28, "w": 16, "h": 20}
    elif name == "kick":
        boxes["hitbox"] = {"frames": [1, 2], "x": 72, "y": 50, "w": 22, "h": 18}
    elif name == "special":
        boxes["hitbox"] = {"frames": [2, 3], "x": 50, "y": 24, "w": 36, "h": 36}
        boxes["spawn_projectile_on"] = 3
    elif name == "ko":
        boxes["hurtbox"] = {"x": 8, "y": 40, "w": 80, "h": 71}
    return boxes
