"""Theo 'Slide' Washington — long-reach pokes with an extending trombone slide."""

from __future__ import annotations

import math
from typing import List

from pxart.body import Pose
from pxart.canvas import Canvas, auto_outline
from pxart.compose import STANDARD_ANIMS, bust_portrait, render_character, shift_upper
from pxart.looks import theo
from pxart.palette import (
    GOLD, GOLD_DK, GOLD_LT, NAVY, NAVY_DK, NAVY_LT, OUTLINE, WHITE, rgba,
)

ID = "trombone"
NAME = 'Theo "Slide" Washington'
INSTRUMENT = "Trombone"
ANIMATIONS = STANDARD_ANIMS
LOOK = theo()

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 96,
    "frameHeight": 40,
    "frames": 6,
    "fps": 12,
    "loop": False,
    "anchor": {"x": 8, "y": 28},
    "notes": (
        "Low brassy blast that rides with the slide thrust. "
        "Spawn on special frame index 3, origin at the extended slide bumper, "
        "travelling right as a short, wide gold woof."
    ),
}
NOTES = (
    "Rangy mid-weight fighter. Punches and kicks are slide-extension pokes; "
    "the special is a full slide-thrust plus a low brassy blast. Terra-cotta plume."
)


def _base() -> Pose:
    # Slightly taller, wider stance; trombone held mid-body, modest slide.
    p = Pose(
        face=(46, 33),
        sh_l=(38, 49),
        sh_r=(58, 49),
        el_l=(32, 60),
        el_r=(70, 58),
        hd_l=(36, 68),   # supports the brace / bell
        hd_r=(72, 60),   # on the slide
        hip=(47, 71),
        hip_l=(41, 71),
        hip_r=(53, 71),
        kn_l=(38, 88),
        kn_r=(56, 86),
        an_l=(36, 104),
        an_r=(56, 104),
        toe_l=(48, 109),
        toe_r=(70, 109),
        inst=(50, 56),   # bell center
        mal_l=(42, 58),  # bell / body
        mal_r=(82, 58),  # slide bumper (extends on attacks)
        expression="idle",
        hands_over="both",
    )
    p.look = LOOK
    return p


def draw_trombone(c: Canvas, p: Pose) -> None:
    """Big bell on the left (near the body), long slide reaching to mal_r."""
    bell = p.mal_l or p.inst
    end = p.mal_r or p.hd_r
    if bell is None or end is None:
        return
    x1, y1 = bell
    x2, y2 = end
    vx, vy = x2 - x1, y2 - y1
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    # two parallel slide tubes
    px, py = -uy, ux
    for side in (-1.6, 1.6):
        sx, sy = x1 + px * side, y1 + py * side
        c.shade_taper(sx, sy, x2 + px * side * 0.4, y2 + py * side * 0.4,
                      1.3, 1.15, GOLD, GOLD_LT, GOLD_DK)
    # U-bend / bumper at the slide end
    c.shade_ellipse(x2, y2, 3.4, 3.8, GOLD, GOLD_LT, GOLD_DK)
    c.shade_taper(x2 - px * 2.2, y2 - py * 2.2, x2 + px * 2.2, y2 + py * 2.2,
                  1.5, 1.5, GOLD, GOLD_LT, GOLD_DK)
    # inner slide (slightly thinner, slightly shorter when not fully out)
    c.taper_capsule(x1 + ux * 6, y1, x2 - ux * 3, y2, 0.8, 0.7, GOLD_LT)
    # body / brace just in front of the bell
    bx, by = x1 + ux * 2, y1
    c.shade_taper(bx, by - 3, bx, by + 5, 2.2, 1.8, GOLD, GOLD_LT, GOLD_DK)
    # hollow bell facing left (back of the horn) so the slide reads as the weapon
    c.shade_ellipse(x1 - ux * 3, y1, 7.0, 6.2, GOLD, GOLD_LT, GOLD_DK)
    c.shade_ellipse(x1 - ux * 5, y1, 4.2, 3.6, GOLD_DK, NAVY_DK, OUTLINE)
    c.set(int(x1 - ux * 3), int(y1 - 3), GOLD_LT)


def paint_front(c, pose):
    draw_trombone(c, pose)


def paint_flash(c, pose):
    if pose.mal_r:
        c.shade_disk(pose.mal_r[0], pose.mal_r[1], 5.5, GOLD_LT, WHITE, rgba("#E76F51"))


def render_pose(pose: Pose) -> Canvas:
    return render_character(pose, clothing="uniform", paint_front=paint_front, paint_flash=paint_flash)


def pose_idle(i):
    p = _base()
    bob = [0, 1, 2, 1][i]
    shift_upper(p, dy=bob)
    # slide eases in and out a few pixels
    ext = [0, 2, 4, 2][i]
    p.mal_r = (p.mal_r[0] + ext, p.mal_r[1])
    p.hd_r = (p.hd_r[0] + ext * 0.4, p.hd_r[1])
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
    swing = [3, 1, -2, -3, -1, 2][i]
    p.mal_r = (p.mal_r[0] + swing, p.mal_r[1])
    p.hd_r = (p.hd_r[0] + swing * 0.5, p.hd_r[1])
    p.leg_over = "right" if i in (0, 1, 5) else "left"
    return p


def pose_jump(i):
    p = _base()
    p.expression = "yell" if i in (1, 2) else "focus"
    if i == 0:
        shift_upper(p, dy=8)
        p.kn_l, p.kn_r = (38, 94), (56, 94)
        p.mal_l, p.mal_r = (40, 68), (78, 68)
    elif i == 1:
        shift_upper(p, dy=-4)
        p.kn_l, p.kn_r = (32, 76), (66, 74)
        p.an_l, p.an_r = (26, 88), (74, 84)
        p.toe_l, p.toe_r = (38, 94), (86, 88)
        p.mal_l, p.mal_r = (36, 48), (88, 44)
        p.hd_l, p.hd_r = (40, 50), (74, 48)
        p.leg_over = "right"
    elif i == 2:
        p.kn_l, p.kn_r = (34, 72), (68, 70)
        p.an_l, p.an_r = (28, 82), (78, 78)
        p.toe_l, p.toe_r = (40, 86), (88, 80)
        p.mal_l, p.mal_r = (36, 46), (90, 42)
        p.leg_over = "right"
    else:
        shift_upper(p, dy=1)
        p.kn_l, p.kn_r = (36, 86), (58, 86)
        p.an_l, p.an_r = (34, 100), (60, 100)
        p.toe_l, p.toe_r = (46, 106), (74, 106)
        p.mal_l, p.mal_r = (42, 60), (82, 58)
    return p


def pose_crouch(i):
    p = _base()
    p.expression = "focus"
    shift_upper(p, dy=14 + i)
    p.hip, p.hip_l, p.hip_r = (47, 88), (40, 88), (54, 88)
    p.kn_l, p.kn_r = (30, 98), (64, 98)
    p.hd_l, p.hd_r = (38, 82), (70, 76)
    p.mal_l, p.mal_r = (42, 74), (86, 74)
    return p


def pose_block(i):
    p = _base()
    p.expression = "grit"
    shift_upper(p, dy=3 + i)
    p.face = (p.face[0] - 2, p.face[1])
    # trombone raised as a long horizontal guard, clear of the face
    p.el_l, p.el_r = (36, 50), (66, 48)
    p.hd_l, p.hd_r = (44, 46), (70, 44)
    p.mal_l, p.mal_r = (38, 42), (88, 40)
    p.kn_l, p.kn_r = (38, 90), (56, 90)
    return p


def pose_punch(i):
    p = _base()
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-3, dy=1)
        # slide chambers in (short)
        p.el_l, p.el_r = (30, 56), (58, 54)
        p.hd_l, p.hd_r = (36, 62), (62, 56)
        p.mal_l, p.mal_r = (40, 58), (66, 56)
        p.hands_over = "both"
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=4)
        # long slide poke almost to the frame edge
        p.el_l, p.el_r = (40, 54), (74, 54)
        p.hd_l, p.hd_r = (46, 58), (78, 56)
        p.mal_l, p.mal_r = (44, 56), (94, 54)
        p.hands_over = "right"
        p.flash = True
    else:
        p.expression = "focus"
        shift_upper(p, dx=2, dy=1)
        p.el_l, p.el_r = (38, 56), (72, 56)
        p.hd_l, p.hd_r = (44, 60), (76, 58)
        p.mal_l, p.mal_r = (42, 58), (90, 56)
        p.hands_over = "right"
    return p


def pose_kick(i):
    p = _base()
    p.leg_over = "right"
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-2, dy=2)
        p.kn_r, p.an_r, p.toe_r = (60, 70), (68, 58), (80, 54)
        p.mal_l, p.mal_r = (40, 50), (78, 46)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (48, 109)
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=-3)
        # slide AND the kicking foot go out — long reach
        p.kn_r, p.an_r, p.toe_r = (72, 66), (86, 62), (94, 60)
        p.mal_l, p.mal_r = (42, 48), (94, 44)
        p.hd_r = (76, 50)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (50, 109)
        p.flash = True
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=-2, dy=1)
        p.kn_r, p.an_r, p.toe_r = (74, 68), (88, 64), (94, 62)
        p.mal_l, p.mal_r = (42, 50), (92, 46)
        p.kn_l, p.an_l, p.toe_l = (40, 94), (36, 104), (50, 109)
    else:
        p.expression = "focus"
        shift_upper(p, dx=-1, dy=2)
        p.kn_r, p.an_r, p.toe_r = (62, 80), (68, 92), (80, 96)
        p.mal_l, p.mal_r = (42, 60), (82, 58)
        p.kn_l, p.an_l, p.toe_l = (40, 92), (36, 104), (48, 109)
    return p


def pose_special(i):
    p = _base()
    if i == 0:
        p.expression = "focus"
        shift_upper(p, dy=1)
        # slide pulls all the way in
        p.el_l, p.el_r = (32, 54), (60, 52)
        p.hd_l, p.hd_r = (38, 60), (62, 54)
        p.mal_l, p.mal_r = (40, 56), (64, 54)
    elif i == 1:
        p.expression = "grit"
        # aiming, still short
        p.el_l, p.el_r = (36, 52), (66, 52)
        p.hd_l, p.hd_r = (42, 56), (70, 54)
        p.mal_l, p.mal_r = (42, 54), (72, 52)
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=4)
        # full slide thrust
        p.el_l, p.el_r = (40, 52), (76, 52)
        p.hd_l, p.hd_r = (46, 56), (80, 54)
        p.mal_l, p.mal_r = (44, 54), (94, 52)
        p.hands_over = "right"
        p.flash = True
    elif i == 3:
        p.expression = "yell"
        shift_upper(p, dx=3, dy=1)
        p.el_l, p.el_r = (40, 54), (76, 54)
        p.hd_l, p.hd_r = (46, 58), (80, 56)
        p.mal_l, p.mal_r = (44, 56), (94, 54)
        p.flash = True
        p.hands_over = "right"
    elif i == 4:
        p.expression = "yell"
        p.mal_l, p.mal_r = (44, 58), (90, 56)
        p.hands_over = "right"
    else:
        p.expression = "focus"
        p.mal_l, p.mal_r = (42, 58), (82, 58)
    return p


def pose_hit(i):
    p = _base()
    p.expression = "hit"
    shift_upper(p, dx=-6 if i == 0 else -9, dy=-1 if i == 0 else 2)
    p.mal_l, p.mal_r = (28, 50), (70, 42)
    p.kn_l, p.an_l, p.toe_l = (30, 90), (22, 104), (34, 109)
    return p


def pose_ko(i):
    p = _base()
    if i == 0:
        p.expression = "hit"
        shift_upper(p, dx=-8, dy=-2)
        p.mal_l, p.mal_r = (22, 46), (66, 36)
    elif i == 1:
        p.expression = "hit"
        p.face = (30, 48)
        p.sh_l, p.sh_r = (22, 60), (44, 54)
        p.el_l, p.el_r = (14, 58), (52, 48)
        p.hd_l, p.hd_r = (10, 50), (58, 40)
        p.mal_l, p.mal_r = (20, 52), (68, 36)
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
        p.mal_l, p.mal_r = (18, 74), (70, 58)
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
        p.mal_l, p.mal_r = (20, 94), (72, 78)
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
    p.el_l, p.el_r = (32, 54), (66, 50)
    p.hd_l, p.hd_r = (40, 60), (70, 52)
    p.mal_l, p.mal_r = (36, 52), (92, 48)
    return bust_portrait(render_pose(p), NAVY, NAVY_LT, NAVY_DK, GOLD)


def render_projectile_frames() -> List[Canvas]:
    w, h = 96, 40
    frames = []
    terra = rgba("#E76F51")
    for i in range(6):
        c = Canvas(w, h)
        y = 28
        # short, fat, low 'BWAAMP' that grows and drifts right
        cx = 14 + i * 12
        rx = 10 + i * 5
        ry = 5 + i * 1.4
        c.shade_ellipse(cx, y, rx, ry, GOLD, GOLD_LT, terra)
        c.shade_ellipse(cx + 2, y, rx * 0.55, ry * 0.5, GOLD_LT, WHITE, GOLD)
        c.ellipse(cx, y, rx + 2.5, ry + 2.0, terra, fill=False)
        if i >= 2:
            c.ellipse(cx, y, rx + 5.0, ry + 3.2, GOLD_DK, fill=False)
        # trailing puffs
        if i >= 1:
            c.shade_ellipse(cx - 12, y + 2, 6 + i, 3.2, GOLD_DK, GOLD, terra)
        if i >= 3:
            c.shade_ellipse(cx - 22, y + 3, 5, 2.4, terra, GOLD_DK, GOLD_DK)
        frames.append(auto_outline(c, OUTLINE))
    return frames


def animation_boxes(name: str) -> dict:
    stand = {"x": 28, "y": 10, "w": 44, "h": 101}
    boxes = {"hurtbox": stand}
    if name == "crouch":
        boxes["hurtbox"] = {"x": 26, "y": 28, "w": 46, "h": 83}
    elif name == "punch":
        boxes["hitbox"] = {"frames": [1], "x": 70, "y": 46, "w": 26, "h": 16}
    elif name == "kick":
        boxes["hitbox"] = {"frames": [1, 2], "x": 70, "y": 42, "w": 26, "h": 22}
    elif name == "special":
        boxes["hitbox"] = {"frames": [2, 3], "x": 70, "y": 44, "w": 26, "h": 18}
        boxes["spawn_projectile_on"] = 3
    elif name == "ko":
        boxes["hurtbox"] = {"x": 8, "y": 40, "w": 80, "h": 71}
    return boxes
