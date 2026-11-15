"""Gus 'Sousa-Mountain' Romero — huge grappler, sousaphone wrapped around him."""

from __future__ import annotations

import math
from typing import List

from pxart.body import Pose
from pxart.canvas import Canvas, auto_outline
from pxart.compose import STANDARD_ANIMS, bust_portrait, render_character, shift_upper
from pxart.looks import gus
from pxart.palette import (
    GOLD, GOLD_DK, GOLD_LT, NAVY, NAVY_DK, NAVY_LT, OUTLINE,
    UNIFORM, WHITE, rgba, shade,
)

FLASH = UNIFORM["flash"]

ID = "tuba"
NAME = 'Gus "Sousa-Mountain" Romero'
INSTRUMENT = "Tuba (sousaphone)"
ANIMATIONS = STANDARD_ANIMS
LOOK = gus()

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 96,
    "frameHeight": 48,
    "frames": 6,
    "fps": 12,
    "loop": False,
    "anchor": {"x": 48, "y": 40},
    "notes": (
        "Low-brass BWAAMP ground shock on the body-slam landing. "
        "Spawn on special frame index 4, origin at the feet, expanding outward."
    ),
}
NOTES = (
    "Widest silhouette in the roster: a sousaphone bell on the right and tubing "
    "looping over the left shoulder. Special is a command-grab / body slam; "
    "the projectile is the landing shock, not a traveling fireball."
)


def _base() -> Pose:
    # Wide, low, heavy. Uses almost the full 96px width.
    p = Pose(
        face=(44, 36),
        sh_l=(26, 50),
        sh_r=(62, 50),
        el_l=(16, 64),
        el_r=(74, 62),
        hd_l=(18, 76),
        hd_r=(78, 74),
        hip=(46, 74),
        hip_l=(34, 74),
        hip_r=(58, 74),
        kn_l=(28, 90),
        kn_r=(62, 90),
        an_l=(20, 104),
        an_r=(64, 104),
        toe_l=(34, 109),
        toe_r=(84, 109),
        inst=(76, 58),  # bell center
        inst_rx=20,
        inst_ry=18,
        mal_l=None,
        mal_r=None,
        expression="idle",
        hands_over="both",
    )
    p.look = LOOK
    return p


def draw_sousaphone(c: Canvas, pose: Pose, stage="full") -> None:
    """Bell on the right, tubing looping over the left shoulder to a mouthpiece."""
    bx, by = pose.inst
    rx, ry = pose.inst_rx, pose.inst_ry
    fx, fy = pose.face
    # Back / left loop of tubing (over the far shoulder)
    # Goes from mouthpiece (near the face, left) up over left shoulder, around the back,
    # down and across to the bell.
    mp = (fx - 8, fy + 8)  # mouthpiece at the lips, slightly left
    # mouthpiece
    c.shade_disk(mp[0], mp[1], 2.2, GOLD, GOLD_LT, GOLD_DK)
    # lead pipe
    c.shade_taper(mp[0], mp[1], pose.sh_l[0] - 2, pose.sh_l[1] - 6, 1.6, 2.2, GOLD, GOLD_LT, GOLD_DK)
    # large over-shoulder loop (left)
    # a thick brass capsule arching over the left shoulder and down the left side
    c.shade_taper(pose.sh_l[0] - 2, pose.sh_l[1] - 6, pose.sh_l[0] - 10, pose.sh_l[1] + 8, 2.6, 3.2, GOLD, GOLD_LT, GOLD_DK)
    c.shade_taper(pose.sh_l[0] - 10, pose.sh_l[1] + 8, pose.hip_l[0] - 8, pose.hip_l[1] + 2, 3.2, 3.4, GOLD, GOLD_LT, GOLD_DK)
    # lower loop across the belly to the bell
    c.shade_taper(pose.hip_l[0] - 8, pose.hip_l[1] + 2, pose.hip[0] + 4, pose.hip[1] + 6, 3.4, 3.6, GOLD, GOLD_LT, GOLD_DK)
    c.shade_taper(pose.hip[0] + 4, pose.hip[1] + 6, bx - 12, by + 8, 3.6, 4.0, GOLD, GOLD_LT, GOLD_DK)

    # A second parallel tube for that "stack of brass" sousaphone look
    c.shade_taper(pose.sh_l[0] + 2, pose.sh_l[1] - 2, pose.hip_l[0] - 2, pose.hip_l[1] - 4, 2.2, 2.4, GOLD, GOLD_LT, GOLD_DK)

    if stage == "back":
        return

    # THE BELL — a hollow horn, not a gold sack. Dark throat, gold rim.
    c.shade_ellipse(bx, by, rx, ry, shade(GOLD_DK, 0.45), GOLD_DK, OUTLINE)
    c.shade_ellipse(bx - 2, by + 1, rx * 0.62, ry * 0.62, OUTLINE, shade(GOLD_DK, 0.55), OUTLINE)
    c.shade_ellipse(bx - 3, by + 1, rx * 0.38, ry * 0.38, shade(OUTLINE, 1.4), OUTLINE, OUTLINE)
    # gold rim
    # ring
    x0, x1 = int(bx - rx - 1), int(bx + rx + 1)
    y0, y1 = int(by - ry - 1), int(by + ry + 1)
    for y in range(y0, y1 + 1):
        dy = ((y + 0.5) - by) / (ry + 0.45)
        for x in range(x0, x1 + 1):
            dx = ((x + 0.5) - bx) / (rx + 0.45)
            d = dx * dx + dy * dy
            if 0.78 <= d <= 1.08:
                ndot = dx * (-0.45) + dy * (-0.7)
                c.set(x, y, GOLD_LT if ndot > 0.2 else (GOLD_DK if ndot < -0.2 else GOLD))
    # highlight on the upper-left of the rim
    c.set(int(bx - 8), int(by - 12), WHITE)
    c.set(int(bx - 6), int(by - 13), GOLD_LT)

    # short flare from the belly-tube into the bell throat
    c.shade_taper(bx - 14, by + 6, bx - 6, by + 2, 3.5, 5.0, GOLD, GOLD_LT, GOLD_DK)


def paint_back(c, pose):
    # nothing extra — tubing is mid/front so it reads on top of the jacket
    pass


def paint_mid(c, pose):
    draw_sousaphone(c, pose, stage="full")


def paint_flash(c, pose):
    if pose.flash or getattr(pose, "slam", False):
        # landing shock at the feet / belly
        hx, hy = pose.hip
        c.shade_ellipse(hx, hy + 28, 22, 6, FLASH, WHITE, GOLD_LT)
        for deg in range(180, 361, 20):
            rad = math.radians(deg)
            c.line(int(hx), int(hy + 28), int(hx + math.cos(rad) * 24), int(hy + 28 + math.sin(rad) * 8), GOLD_LT)


def render_pose(pose: Pose) -> Canvas:
    return render_character(
        pose, clothing="uniform",
        paint_mid=paint_mid, paint_flash=paint_flash,
    )


def pose_idle(i):
    p = _base()
    bob = [0, 1, 2, 1][i]
    shift_upper(p, dy=bob)
    # heavy breathing — arms rest on the tubing
    return p


def pose_walk(i):
    p = _base()
    bounce = [2, 0, 1, 2, 0, 1][i]  # heavier stomp
    shift_upper(p, dy=bounce)
    # wide march
    r_kn = [(68, 86), (64, 88), (56, 90), (50, 92), (58, 78), (70, 84)]
    r_an = [(70, 104), (66, 104), (54, 104), (48, 100), (56, 86), (74, 96)]
    r_toe = [(90, 109), (86, 109), (72, 109), (64, 107), (70, 90), (90, 102)]
    l_kn = [(24, 92), (30, 78), (40, 84), (36, 86), (30, 88), (26, 90)]
    l_an = [(14, 100), (24, 86), (48, 96), (22, 104), (18, 104), (16, 104)]
    l_toe = [(28, 107), (34, 90), (62, 102), (36, 109), (32, 109), (28, 109)]
    p.kn_r, p.an_r, p.toe_r = r_kn[i], r_an[i], r_toe[i]
    p.kn_l, p.an_l, p.toe_l = l_kn[i], l_an[i], l_toe[i]
    p.leg_over = "right" if i in (0, 1, 5) else "left"
    return p


def pose_jump(i):
    p = _base()
    p.expression = "yell" if i in (1, 2) else "focus"
    if i == 0:
        shift_upper(p, dy=8)
        p.kn_l, p.kn_r = (28, 94), (64, 94)
        p.el_l, p.el_r = (14, 70), (76, 70)
        p.hd_l, p.hd_r = (16, 80), (80, 80)
    elif i == 1:
        shift_upper(p, dy=-1)
        p.kn_l, p.kn_r = (24, 80), (70, 78)
        p.an_l, p.an_r = (16, 92), (78, 88)
        p.toe_l, p.toe_r = (28, 98), (90, 92)
        p.leg_over = "right"
    elif i == 2:
        p.kn_l, p.kn_r = (26, 78), (72, 76)
        p.an_l, p.an_r = (18, 88), (80, 84)
        p.toe_l, p.toe_r = (30, 94), (90, 88)
        p.leg_over = "right"
    else:
        shift_upper(p, dy=2)
        p.kn_l, p.kn_r = (28, 88), (64, 88)
        p.an_l, p.an_r = (20, 102), (66, 102)
        p.toe_l, p.toe_r = (34, 108), (84, 108)
    return p


def pose_crouch(i):
    p = _base()
    p.expression = "focus"
    shift_upper(p, dy=12 + i)
    p.hip, p.hip_l, p.hip_r = (46, 88), (32, 88), (60, 88)
    p.kn_l, p.kn_r = (22, 98), (68, 98)
    return p


def pose_block(i):
    p = _base()
    p.expression = "grit"
    shift_upper(p, dy=3 + i)
    p.face = (p.face[0] - 2, p.face[1])
    # bell shoved forward as a shield — move inst right
    p.inst = (p.inst[0] + 6 - i, p.inst[1])
    p.el_l, p.el_r = (20, 58), (70, 58)
    p.hd_l, p.hd_r = (28, 68), (72, 66)
    p.kn_l, p.kn_r = (28, 92), (62, 92)
    return p


def pose_punch(i):
    p = _base()
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-4, dy=1)
        p.el_r, p.hd_r = (58, 48), (52, 40)
        p.hands_over = "right"
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=6)
        p.el_r, p.hd_r = (80, 54), (90, 50)
        p.hands_over = "right"
        p.flash = True
    else:
        p.expression = "focus"
        shift_upper(p, dx=2, dy=1)
        p.el_r, p.hd_r = (78, 58), (86, 56)
        p.hands_over = "right"
    return p


def pose_kick(i):
    p = _base()
    p.leg_over = "right"
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-2, dy=3)
        p.kn_r, p.an_r, p.toe_r = (66, 72), (72, 60), (86, 58)
        p.kn_l, p.an_l, p.toe_l = (28, 94), (20, 104), (34, 109)
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=-4, dy=1)
        p.kn_r, p.an_r, p.toe_r = (74, 70), (88, 66), (94, 64)
        p.kn_l, p.an_l, p.toe_l = (28, 94), (20, 104), (34, 109)
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=-3, dy=2)
        p.kn_r, p.an_r, p.toe_r = (76, 72), (90, 68), (94, 66)
        p.flash = True
        p.kn_l, p.an_l, p.toe_l = (28, 94), (20, 104), (34, 109)
    else:
        p.expression = "focus"
        shift_upper(p, dx=-1, dy=3)
        p.kn_r, p.an_r, p.toe_r = (68, 82), (74, 94), (86, 98)
        p.kn_l, p.an_l, p.toe_l = (28, 92), (20, 104), (34, 109)
    return p


def pose_special(i):
    """Command grab: reach, clinch, lift, come down, SLAM, recover."""
    p = _base()
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=4, dy=2)
        # both arms reach forward
        p.el_l, p.el_r = (40, 58), (80, 56)
        p.hd_l, p.hd_r = (56, 58), (90, 56)
        p.hands_over = "both"
    elif i == 1:
        p.expression = "grit"
        shift_upper(p, dx=6, dy=4)
        # clinch — arms wrap in front
        p.el_l, p.el_r = (50, 58), (78, 56)
        p.hd_l, p.hd_r = (64, 60), (80, 58)
        p.kn_l, p.kn_r = (28, 94), (64, 94)
        p.hands_over = "both"
    elif i == 2:
        p.expression = "yell"
        # lift — straighten, arms high
        shift_upper(p, dy=-2)
        p.el_l, p.el_r = (36, 36), (70, 34)
        p.hd_l, p.hd_r = (40, 20), (72, 18)
        p.hands_over = "both"
    elif i == 3:
        p.expression = "yell"
        # coming down
        shift_upper(p, dy=6)
        p.el_l, p.el_r = (30, 58), (70, 56)
        p.hd_l, p.hd_r = (34, 70), (74, 68)
        p.kn_l, p.kn_r = (26, 94), (66, 94)
        p.hands_over = "both"
    elif i == 4:
        p.expression = "yell"
        # SLAM
        shift_upper(p, dy=10)
        p.el_l, p.el_r = (28, 70), (72, 68)
        p.hd_l, p.hd_r = (32, 84), (76, 82)
        p.kn_l, p.kn_r = (24, 98), (68, 98)
        p.flash = True
        p.slam = True
        p.hands_over = "both"
    else:
        p.expression = "focus"
        shift_upper(p, dy=2)
        p.el_l, p.el_r = (18, 64), (74, 62)
        p.hd_l, p.hd_r = (20, 76), (78, 74)
    return p


def pose_hit(i):
    p = _base()
    p.expression = "hit"
    shift_upper(p, dx=-6 if i == 0 else -8, dy=-1 if i == 0 else 2)
    p.el_l, p.el_r = (12, 58), (70, 56)
    p.hd_l, p.hd_r = (10, 50), (76, 52)
    p.kn_l, p.an_l, p.toe_l = (22, 92), (12, 104), (24, 109)
    return p


def pose_ko(i):
    p = _base()
    if i == 0:
        p.expression = "hit"
        shift_upper(p, dx=-8, dy=-2)
        p.el_l, p.el_r = (10, 50), (66, 48)
        p.hd_l, p.hd_r = (8, 40), (72, 40)
    elif i == 1:
        p.expression = "hit"
        p.face = (28, 50)
        p.sh_l, p.sh_r = (16, 62), (48, 54)
        p.el_l, p.el_r = (8, 64), (56, 50)
        p.hd_l, p.hd_r = (6, 72), (62, 44)
        p.hip, p.hip_l, p.hip_r = (44, 74), (30, 76), (56, 70)
        p.kn_l, p.an_l, p.toe_l = (32, 90), (18, 102), (30, 109)
        p.kn_r, p.an_r, p.toe_r = (66, 78), (80, 88), (90, 92)
        p.inst = (70, 62)
        p.leg_over = "right"
    elif i == 2:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (28, 70)
        p.sh_l, p.sh_r = (18, 82), (44, 72)
        p.el_l, p.el_r = (8, 84), (54, 64)
        p.hd_l, p.hd_r = (6, 90), (60, 58)
        p.hip, p.hip_l, p.hip_r = (48, 86), (34, 88), (60, 80)
        p.kn_l, p.an_l, p.toe_l = (52, 96), (46, 106), (58, 109)
        p.kn_r, p.an_r, p.toe_r = (70, 84), (84, 90), (94, 92)
        p.inst = (68, 78)
        p.leg_over = "right"
    else:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (26, 88)
        p.sh_l, p.sh_r = (24, 92), (46, 86)
        p.el_l, p.el_r = (12, 98), (56, 80)
        p.hd_l, p.hd_r = (8, 102), (62, 74)
        p.hip, p.hip_l, p.hip_r = (56, 92), (42, 94), (68, 88)
        p.kn_l, p.an_l, p.toe_l = (70, 96), (80, 100), (90, 102)
        p.kn_r, p.an_r, p.toe_r = (68, 78), (78, 68), (88, 64)
        p.inst = (64, 90)
        p.inst_rx, p.inst_ry = 16, 14
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
    return bust_portrait(render_pose(p), NAVY, NAVY_LT, NAVY_DK, GOLD)


def render_projectile_frames() -> List[Canvas]:
    w, h = 96, 48
    frames = []
    for i in range(6):
        c = Canvas(w, h)
        # ground-hugging expanding shock, opening left AND right from center
        cx, cy = 48, 40
        rx = 10 + i * 7
        ry = 4 + i * 1.4
        # two-tone ring
        x0, x1 = int(cx - rx - 2), int(cx + rx + 2)
        y0, y1 = int(cy - ry - 2), int(cy + ry + 2)
        for y in range(y0, y1 + 1):
            dy = ((y + 0.5) - cy) / (ry + 0.45)
            for x in range(x0, x1 + 1):
                dx = ((x + 0.5) - cx) / (rx + 0.45)
                d = dx * dx + dy * dy
                if 0.70 <= d <= 1.08:
                    # drop the top of the ellipse so it reads as a ground burst
                    if (y + 0.5) < cy - ry * 0.35:
                        continue
                    ndot = dx * (-0.3) + dy * (-0.7)
                    if ndot > 0.2:
                        c.set(x, y, FLASH)
                    elif ndot < -0.2:
                        c.set(x, y, GOLD_DK)
                    else:
                        c.set(x, y, GOLD)
        if i == 0:
            c.shade_ellipse(cx, cy, 8, 3, FLASH, WHITE, GOLD_LT)
        if i >= 4:
            for deg in range(200, 341, 20):
                rad = math.radians(deg)
                c.disk(cx + math.cos(rad) * (rx + 3), cy + math.sin(rad) * (ry + 2), 1.4, GOLD_LT)
        frames.append(auto_outline(c, OUTLINE))
    return frames


def animation_boxes(name: str) -> dict:
    stand = {"x": 12, "y": 12, "w": 78, "h": 99}
    boxes = {"hurtbox": stand}
    if name == "crouch":
        boxes["hurtbox"] = {"x": 12, "y": 26, "w": 78, "h": 85}
    elif name == "block":
        boxes["blockbox"] = {"x": 60, "y": 36, "w": 30, "h": 36}
    elif name == "punch":
        boxes["hitbox"] = {"frames": [1], "x": 78, "y": 40, "w": 16, "h": 22}
    elif name == "kick":
        boxes["hitbox"] = {"frames": [1, 2], "x": 72, "y": 52, "w": 22, "h": 20}
    elif name == "special":
        boxes["hitbox"] = {"frames": [0, 1, 4], "x": 54, "y": 30, "w": 36, "h": 70}
        boxes["spawn_projectile_on"] = 4
    elif name == "ko":
        boxes["hurtbox"] = {"x": 6, "y": 42, "w": 86, "h": 69}
    return boxes
