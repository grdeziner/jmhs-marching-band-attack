"""Marcus "Thunder" Boone — 16-bit SNES / SF2 Turbo redraw."""

from __future__ import annotations

import math
from typing import List

from pxart.body import FRAME_H, FRAME_W
from pxart.canvas import Canvas, auto_outline
from px16.compose import Pose16, render_pose, shift_upper, shift_all
from px16.draw import fill_ellipse, line, specular
from px16.palette import (
    G1, G2, G3, G4, K, N3, N4, PAL, W1, W2, W3, RAMPS, count_opaque, enforce, hex_list,
)
from px16.parts import finish

ID = "drummer"
NAME = 'Marcus "Thunder" Boone'
INSTRUMENT = "Marching Bass Drum"
# Author in 128-wide frame space; do not apply the legacy +16 box shift.
SHIFT_BOXES = False
BUILD_COMPARE = True
LOOK_16BIT = True

ANIMATIONS = [
    ("idle", 6, 8, True),
    ("walk", 8, 10, True),
    ("jump", 6, 10, False),
    ("crouch", 2, 8, True),
    ("block", 2, 8, True),
    ("punch", 4, 12, False),
    ("kick", 5, 12, False),
    ("special", 8, 10, False),
    ("hit", 3, 10, False),
    ("ko", 6, 8, False),
]

PROJECTILE = {
    "file": "projectile.png",
    "frameWidth": 96,
    "frameHeight": 64,
    "frames": 6,
    "fps": 12,
    "loop": False,
    "anchor": {"x": 8, "y": 32},
    "notes": (
        "16-bit gold shockwave. Spawn on special frame index 4 (the mallet slam), "
        "origin at the front of the bass drum, travelling right."
    ),
}

SUPER = {
    "file": "super.png",
    "frameWidth": 128,
    "frameHeight": 80,
    "frames": 6,
    "fps": 12,
    "loop": False,
    "anchor": {"x": 64, "y": 72},
    "notes": (
        "16-bit thunder super: metallic gold-white shock rings with a dark core, "
        "speculars, and lightning ticks. Anchor is bottom-center of each 128x80 "
        "frame, at the fighter's feet / drum."
    ),
}

NOTES = (
    "16-bit SNES / Street Fighter II Turbo redraw of Marcus \"Thunder\" Boone. "
    "15 opaque colors plus transparent. 128x112 frames, anchor {x:64, y:111}. "
    "Heavy marching bassist; bass drum on a harness, two mallets. "
    "Special slam spawns the shockwave on frame 4. "
    "portrait_large.png is the 128x128 VS-screen bust."
)


def _base() -> Pose16:
    return Pose16()


# ---- poses ----------------------------------------------------------------

def pose_idle(i: int) -> Pose16:
    p = _base()
    bob = [0, 1, 2, 2, 1, 0][i]
    shift_upper(p, dy=bob)
    # mallets breathe opposite the chest
    tilt = [0, 1, 2, 1, 0, -1][i]
    p.mal_l = (p.mal_l[0], p.mal_l[1] - tilt)
    p.mal_r = (p.mal_r[0], p.mal_r[1] + tilt)
    p.folds = "stand"
    return p


def pose_walk(i: int) -> Pose16:
    p = _base()
    bounce = [1, 0, -1, 0, 1, 0, -1, 0][i]
    shift_upper(p, dy=bounce)
    # two-step march, 8 frames (contact on 0 and 4)
    r_kn = [(80, 88), (76, 90), (68, 92), (64, 88), (58, 90), (70, 80), (82, 84), (84, 86)]
    r_an = [(84, 104), (80, 104), (70, 104), (64, 100), (58, 104), (68, 90), (84, 96), (88, 100)]
    r_toe = [(96, 109), (92, 109), (82, 109), (74, 107), (70, 109), (78, 94), (96, 102), (100, 106)]
    l_kn = [(48, 90), (52, 80), (62, 84), (66, 86), (70, 88), (66, 90), (58, 92), (50, 91)]
    l_an = [(42, 104), (50, 90), (64, 96), (70, 102), (74, 104), (70, 104), (58, 104), (46, 104)]
    l_toe = [(54, 109), (58, 94), (76, 102), (82, 107), (86, 109), (82, 109), (70, 109), (58, 109)]
    p.kn_r, p.an_r, p.toe_r = r_kn[i], r_an[i], r_toe[i]
    p.kn_l, p.an_l, p.toe_l = l_kn[i], l_an[i], l_toe[i]
    p.folds_r = "stretch" if i in (0, 1, 7) else ("bend" if i in (4, 5) else "stand")
    p.folds_l = "bend" if i in (1, 2) else ("stretch" if i in (3, 4, 5) else "stand")
    p.leg_over = "right" if i in (0, 1, 6, 7) else "left"
    swing = [3, 2, 0, -2, -3, -2, 0, 2][i]
    p.mal_r = (p.mal_r[0] + swing, p.mal_r[1] - abs(swing) * 0.3)
    p.mal_l = (p.mal_l[0] - swing * 0.5, p.mal_l[1] + swing * 0.2)
    p.folds = "twist" if i in (1, 2, 5, 6) else "stand"
    return p


def pose_jump(i: int) -> Pose16:
    p = _base()
    p.expression = "yell" if i in (2, 3) else ("grit" if i in (1, 4) else "focus")
    if i == 0:  # compress
        shift_upper(p, dy=10)
        p.hip = (64, 86)
        p.hip_l, p.hip_r = (54, 86), (74, 86)
        p.kn_l, p.kn_r = (44, 98), (84, 98)
        p.an_l, p.an_r = (48, 104), (80, 104)
        p.toe_l, p.toe_r = (60, 109), (92, 109)
        p.mal_l, p.mal_r = (24, 80), (108, 76)
        p.folds, p.folds_l, p.folds_r = "compress", "bend", "bend"
    elif i == 1:  # launch
        shift_upper(p, dy=2)
        p.kn_l, p.kn_r = (48, 86), (82, 86)
        p.mal_l, p.mal_r = (20, 48), (112, 44)
        p.folds = "stretch_r"
    elif i == 2:  # rise — feet off the ground; head stays under the plume cap
        shift_all(p, dy=-8)
        p.kn_l, p.kn_r = (46, 78), (84, 76)
        p.an_l, p.an_r = (40, 90), (92, 86)
        p.toe_l, p.toe_r = (52, 96), (104, 90)
        p.el_l, p.el_r = (32, 44), (100, 42)
        p.hd_l, p.hd_r = (26, 36), (108, 34)
        p.mal_l, p.mal_r = (18, 22), (116, 20)
        p.leg_over = "right"
        p.folds, p.folds_l, p.folds_r = "stretch_r", "bend", "bend"
    elif i == 3:  # apex
        shift_all(p, dy=-10)
        p.kn_l, p.kn_r = (44, 72), (86, 70)
        p.an_l, p.an_r = (38, 84), (94, 80)
        p.toe_l, p.toe_r = (50, 90), (106, 84)
        p.el_l, p.el_r = (32, 42), (100, 40)
        p.hd_l, p.hd_r = (26, 34), (108, 32)
        p.mal_l, p.mal_r = (18, 20), (116, 18)
        p.leg_over = "right"
        p.folds_l, p.folds_r = "bend", "bend"
    elif i == 4:  # fall
        shift_all(p, dy=-6)
        p.kn_l, p.kn_r = (46, 84), (84, 86)
        p.an_l, p.an_r = (42, 96), (88, 98)
        p.toe_l, p.toe_r = (54, 102), (100, 104)
        p.mal_l, p.mal_r = (22, 36), (110, 34)
        p.leg_over = "right"
        p.folds_l, p.folds_r = "bend", "bend"
    else:  # pre-land
        shift_upper(p, dy=4)
        p.kn_l, p.kn_r = (48, 90), (80, 90)
        p.an_l, p.an_r = (48, 102), (80, 102)
        p.toe_l, p.toe_r = (60, 108), (92, 108)
        p.mal_l, p.mal_r = (24, 70), (108, 66)
        p.folds, p.folds_l, p.folds_r = "compress", "bend", "bend"
    return p


def pose_crouch(i: int) -> Pose16:
    p = _base()
    p.expression = "focus"
    shift_upper(p, dy=14 + i)
    p.hip, p.hip_l, p.hip_r = (64, 90), (54, 90), (74, 90)
    p.kn_l, p.kn_r = (42, 100), (86, 100)
    p.an_l, p.an_r = (46, 104), (84, 104)
    p.toe_l, p.toe_r = (58, 109), (96, 109)
    p.el_l, p.el_r = (36, 80), (96, 78)
    p.hd_l, p.hd_r = (30, 86), (104, 84)
    p.mal_l, p.mal_r = (22, 78), (114, 74)
    p.inst = (70, 82 + i)
    p.folds, p.folds_l, p.folds_r = "compress", "bend", "bend"
    return p


def pose_block(i: int) -> Pose16:
    p = _base()
    p.expression = "grit"
    shift_upper(p, dy=3 + i, dx=-2)
    p.face = (p.face[0] - 2, p.face[1])
    # drum shoved forward as a shield
    p.inst = (84, 66 + i)
    p.el_l, p.el_r = (44, 64), (100, 52)
    p.hd_l, p.hd_r = (58, 70), (110, 46)
    p.mal_l, p.mal_r = (50, 58), (116, 28)
    p.kn_l, p.kn_r = (50, 92), (76, 92)
    p.folds = "stretch_r"
    p.hands_over = "both"
    return p


def pose_punch(i: int) -> Pose16:
    p = _base()
    if i == 0:  # chamber, mallet up beside the shako (not over the face)
        p.expression = "grit"
        shift_upper(p, dx=-4, dy=1)
        p.el_l, p.el_r = (28, 60), (86, 42)
        p.hd_l, p.hd_r = (22, 66), (90, 26)
        p.mal_l, p.mal_r = (14, 58), (86, 10)
        p.folds = "windup"
        p.hands_over = "right"
    elif i == 1:  # extend
        p.expression = "yell"
        shift_upper(p, dx=4)
        p.el_l, p.el_r = (56, 58), (94, 54)
        p.hd_l, p.hd_r = (68, 58), (108, 50)
        p.mal_l, p.mal_r = (54, 62), (118, 42)
        p.folds = "stretch_r"
        p.hands_over = "right"
        p.flash = True
    elif i == 2:  # active / hold
        p.expression = "yell"
        shift_upper(p, dx=3, dy=1)
        p.el_l, p.el_r = (54, 60), (92, 56)
        p.hd_l, p.hd_r = (66, 60), (106, 52)
        p.mal_l, p.mal_r = (52, 64), (116, 44)
        p.folds = "stretch_r"
        p.hands_over = "right"
    else:  # recover
        p.expression = "focus"
        shift_upper(p, dx=2, dy=1)
        p.el_l, p.el_r = (40, 64), (96, 62)
        p.hd_l, p.hd_r = (36, 72), (106, 66)
        p.mal_l, p.mal_r = (26, 66), (114, 56)
        p.folds = "stand"
        p.hands_over = "right"
    return p


def pose_kick(i: int) -> Pose16:
    p = _base()
    p.leg_over = "right"
    p.folds_r = "stretch"
    p.folds_l = "bend"
    # keep the right mallet up and back so the shaft never crosses the kicking leg
    if i == 0:
        p.expression = "grit"
        shift_upper(p, dx=-3, dy=2)
        p.kn_r, p.an_r, p.toe_r = (78, 70), (86, 56), (98, 50)
        p.el_l, p.el_r = (30, 60), (78, 42)
        p.hd_l, p.hd_r = (22, 70), (60, 28)
        p.mal_l, p.mal_r = (16, 58), (46, 14)
        p.folds = "windup"
        p.hands_over = "right"
    elif i == 1:
        p.expression = "yell"
        shift_upper(p, dx=-6)
        p.kn_r, p.an_r, p.toe_r = (90, 66), (108, 60), (118, 56)
        p.el_l, p.el_r = (28, 58), (76, 40)
        p.hd_l, p.hd_r = (20, 68), (58, 26)
        p.mal_l, p.mal_r = (14, 56), (44, 12)
        p.folds = "stretch_l"
        p.hands_over = "right"
    elif i == 2:
        p.expression = "yell"
        shift_upper(p, dx=-5, dy=1)
        p.kn_r, p.an_r, p.toe_r = (90, 68), (108, 62), (118, 58)
        p.el_l, p.el_r = (28, 60), (76, 42)
        p.hd_l, p.hd_r = (20, 70), (58, 28)
        p.mal_l, p.mal_r = (14, 58), (44, 14)
        p.flash = True
        p.folds = "stretch_l"
        p.hands_over = "right"
    elif i == 3:
        p.expression = "grit"
        shift_upper(p, dx=-3, dy=2)
        p.kn_r, p.an_r, p.toe_r = (86, 74), (102, 70), (114, 66)
        p.el_l, p.el_r = (32, 62), (80, 46)
        p.hd_l, p.hd_r = (24, 72), (64, 34)
        p.mal_l, p.mal_r = (16, 62), (48, 20)
        p.folds = "stretch_l"
        p.hands_over = "right"
    else:
        p.expression = "focus"
        shift_upper(p, dx=-1, dy=2)
        p.kn_r, p.an_r, p.toe_r = (80, 84), (86, 96), (98, 102)
        p.el_l, p.el_r = (34, 66), (96, 62)
        p.hd_l, p.hd_r = (28, 74), (106, 68)
        p.mal_l, p.mal_r = (20, 66), (114, 56)
        p.folds, p.folds_r = "stand", "stand"
        p.leg_over = "right"
        p.hands_over = "right"
    return p



def pose_special(i: int) -> Pose16:
    p = _base()
    if i == 0:
        p.expression = "focus"
        shift_upper(p, dy=2)
        p.el_l, p.el_r = (32, 52), (96, 50)
        p.hd_l, p.hd_r = (30, 40), (100, 38)
        p.mal_l, p.mal_r = (24, 24), (110, 20)
        p.folds = "windup"
    elif i == 1:
        p.expression = "grit"
        shift_upper(p, dy=3)
        p.el_l, p.el_r = (30, 48), (98, 46)
        p.hd_l, p.hd_r = (28, 32), (102, 30)
        p.mal_l, p.mal_r = (22, 16), (112, 14)
        p.folds = "windup"
    elif i == 2:
        p.expression = "grit"
        shift_upper(p, dy=2)
        p.el_l, p.el_r = (36, 50), (96, 50)
        p.hd_l, p.hd_r = (44, 42), (96, 42)
        p.mal_l, p.mal_r = (40, 26), (104, 24)
        p.folds = "compress"
    elif i == 3:
        p.expression = "yell"
        shift_upper(p, dy=3)
        p.el_l, p.el_r = (44, 58), (94, 56)
        p.hd_l, p.hd_r = (56, 62), (90, 58)
        p.mal_l, p.mal_r = (62, 54), (92, 50)
        p.hands_over = "both"
        p.folds = "compress"
    elif i == 4:  # SLAM — spawn projectile
        p.expression = "yell"
        shift_upper(p, dy=6)
        p.el_l, p.el_r = (48, 62), (100, 56)
        p.hd_l, p.hd_r = (62, 58), (96, 52)
        p.mal_l, p.mal_r = (68, 52), (96, 44)
        p.flash = True
        p.slam = True
        p.hands_over = "both"
        p.folds = "compress"
        p.kn_l, p.kn_r = (50, 94), (78, 94)
    elif i == 5:  # blast hold
        p.expression = "yell"
        shift_upper(p, dy=5)
        p.el_l, p.el_r = (46, 60), (98, 56)
        p.hd_l, p.hd_r = (58, 54), (94, 50)
        p.mal_l, p.mal_r = (64, 42), (94, 38)
        p.flash = True
        p.hands_over = "both"
        p.folds = "stretch_r"
    elif i == 6:
        p.expression = "yell"
        shift_upper(p, dy=4)
        p.mal_l, p.mal_r = (50, 48), (100, 42)
        p.hands_over = "both"
        p.folds = "stretch_r"
    else:
        p.expression = "focus"
        shift_upper(p, dy=1)
        p.mal_l, p.mal_r = (24, 64), (112, 56)
        p.hands_over = "both"
        p.folds = "stand"
    return p


def pose_hit(i: int) -> Pose16:
    p = _base()
    p.expression = "hit"
    if i == 0:
        shift_upper(p, dx=-8, dy=-1)
        p.face = (p.face[0] - 2, p.face[1] - 1)
        p.mal_l, p.mal_r = (14, 44), (96, 36)
        p.kn_l, p.an_l, p.toe_l = (44, 92), (36, 104), (48, 109)
        p.folds = "twist"
    elif i == 1:
        shift_upper(p, dx=-10, dy=1)
        p.mal_l, p.mal_r = (12, 48), (92, 40)
        p.kn_l, p.an_l, p.toe_l = (42, 92), (34, 104), (46, 109)
        p.folds = "twist"
    else:
        shift_upper(p, dx=-6, dy=2)
        p.expression = "grit"
        p.mal_l, p.mal_r = (18, 56), (100, 48)
        p.folds = "stand"
    return p


def pose_ko(i: int) -> Pose16:
    p = _base()
    if i == 0:
        p.expression = "hit"
        shift_upper(p, dx=-10, dy=-2)
        p.face = (p.face[0] - 4, p.face[1] - 2)
        p.mal_l, p.mal_r = (12, 36), (90, 28)
    elif i == 1:
        p.expression = "hit"
        p.face = (40, 48)
        p.sh_l, p.sh_r = (30, 62), (56, 56)
        p.el_l, p.el_r = (20, 60), (66, 50)
        p.hd_l, p.hd_r = (14, 52), (74, 42)
        p.mal_l, p.mal_r = (8, 60), (90, 32)
        p.inst = (58, 70)
        p.hip, p.hip_l, p.hip_r = (52, 76), (44, 78), (60, 72)
        p.kn_l, p.an_l, p.toe_l = (44, 92), (36, 104), (48, 109)
        p.kn_r, p.an_r, p.toe_r = (78, 80), (92, 90), (106, 94)
        p.leg_over = "right"
        p.folds = "twist"
    elif i == 2:
        p.expression = "ko"
        p.head_rot = 55
        p.face = (42, 64)
        p.sh_l, p.sh_r = (32, 80), (54, 72)
        p.el_l, p.el_r = (20, 78), (66, 64)
        p.hd_l, p.hd_r = (14, 72), (74, 56)
        p.mal_l, p.mal_r = (8, 80), (88, 50)
        p.inst = (58, 82)
        p.hip, p.hip_l, p.hip_r = (56, 86), (48, 88), (64, 82)
        p.kn_l, p.an_l, p.toe_l = (58, 98), (54, 106), (66, 109)
        p.kn_r, p.an_r, p.toe_r = (80, 86), (96, 92), (110, 94)
        p.leg_over = "right"
        p.folds = "compress"
    elif i == 3:
        p.expression = "ko"
        p.head_rot = 90
        p.face = (46, 80)
        p.sh_l, p.sh_r = (42, 88), (62, 84)
        p.el_l, p.el_r = (28, 94), (74, 76)
        p.hd_l, p.hd_r = (22, 100), (82, 68)
        p.mal_l, p.mal_r = (18, 104), (98, 64)
        p.inst = (70, 90)
        p.hip, p.hip_l, p.hip_r = (74, 90), (66, 92), (82, 88)
        p.kn_l, p.an_l, p.toe_l = (88, 96), (100, 100), (114, 102)
        p.kn_r, p.an_r, p.toe_r = (86, 80), (98, 70), (112, 66)
        p.leg_over = "right"
        p.hands_over = "right"
        p.folds = "compress"
    elif i == 4:  # bounce
        p.expression = "ko"
        p.head_rot = 90
        p.face = (44, 76)
        p.sh_l, p.sh_r = (40, 86), (60, 82)
        p.el_l, p.el_r = (28, 92), (72, 74)
        p.hd_l, p.hd_r = (22, 98), (80, 66)
        p.mal_l, p.mal_r = (18, 102), (96, 62)
        p.inst = (68, 86)
        p.hip, p.hip_l, p.hip_r = (72, 88), (64, 90), (80, 86)
        p.kn_l, p.an_l, p.toe_l = (86, 94), (98, 98), (112, 100)
        p.kn_r, p.an_r, p.toe_r = (84, 78), (96, 68), (110, 64)
        p.leg_over = "right"
        p.folds = "compress"
    else:  # down
        p.expression = "ko"
        p.head_rot = 90
        p.face = (44, 88)
        p.sh_l, p.sh_r = (42, 92), (62, 88)
        p.el_l, p.el_r = (28, 98), (74, 80)
        p.hd_l, p.hd_r = (22, 104), (82, 72)
        p.mal_l, p.mal_r = (18, 106), (98, 70)
        p.inst = (72, 94)
        p.hip, p.hip_l, p.hip_r = (78, 92), (70, 94), (86, 90)
        p.kn_l, p.an_l, p.toe_l = (92, 96), (104, 100), (118, 102)
        p.kn_r, p.an_r, p.toe_r = (84, 80), (96, 70), (110, 66)
        p.leg_over = "right"
        p.hands_over = "right"
        p.folds = "compress"
    return p


POSE_FN = {
    "idle": pose_idle, "walk": pose_walk, "jump": pose_jump, "crouch": pose_crouch,
    "block": pose_block, "punch": pose_punch, "kick": pose_kick, "special": pose_special,
    "hit": pose_hit, "ko": pose_ko,
}


def render_frame(animation, index):
    return render_pose(POSE_FN[animation](index))


# ---- portraits ------------------------------------------------------------

def _bust_card(body: Canvas, size: int, dramatic: bool = False) -> Canvas:
    """Crop the head / shoulders / upper drum and scale into a square bust."""
    from PIL import Image as PILImage
    from px16.palette import N2, N3, N4
    from pxart.canvas import nearest_scale

    # bbox of the bust: keep the plume, cut below mid-drum
    top, left, right, bottom = body.h, body.w, 0, 0
    for y in range(body.h):
        for x in range(body.w):
            if body.get(x, y) is None:
                continue
            if y > 78:
                continue
            top = min(top, y)
            bottom = max(bottom, y)
            left = min(left, x)
            right = max(right, x)
    # Head-centered square crop so both portraits are busts, not full-body shrinks.
    # Use the plume/shako (topmost pixels) as the horizontal center.
    top_xs = [x for x in range(body.w) if body.get(x, top) is not None
              or (top + 1 < body.h and body.get(x, top + 1) is not None)]
    cx = int(sum(top_xs) / len(top_xs)) if top_xs else int((left + right) / 2)
    side = 56 if size == 64 else 64
    left = max(0, cx - side // 2)
    if left + side > body.w:
        left = max(0, body.w - side)
    top = max(0, top - 2)
    if top + side > body.h:
        top = max(0, body.h - side)

    crop = PILImage.new("RGBA", (side, side), (0, 0, 0, 0))
    px = crop.load()
    for y in range(side):
        for x in range(side):
            col = body.get(left + x, top + y)
            if col is not None:
                px[x, y] = col
    scaled = crop.resize((size, size), PILImage.Resampling.NEAREST)

    port = Canvas(size, size)
    cx = cy = size / 2
    for y in range(size):
        for x in range(size):
            edge = x < 2 or y < 2 or x > size - 3 or y > size - 3
            if edge:
                port.set(x, y, N4)
                continue
            dx, dy = (x - cx) / cx, (y - cy) / cy
            r2 = dx * dx + dy * dy
            if dramatic:
                lit = (dx + 0.4) ** 2 + (dy + 0.5) ** 2
                if lit < 0.38:
                    port.set(x, y, N2)
                elif lit < 0.85:
                    port.set(x, y, N3)
                else:
                    port.set(x, y, N4)
            else:
                port.set(x, y, N3 if r2 > 0.72 else N2)
    # gold corner ticks
    tick = G1 if dramatic else G2
    for (x, y) in (
        (2, 2), (3, 2), (2, 3),
        (size - 3, 2), (size - 4, 2), (size - 3, 3),
        (2, size - 3), (3, size - 3), (2, size - 4),
        (size - 3, size - 3), (size - 4, size - 3), (size - 3, size - 4),
    ):
        port.set(x, y, tick)

    sp = scaled.load()
    for y in range(size):
        for x in range(size):
            r, g, b, a = sp[x, y]
            if a:
                port.px[y][x] = (r, g, b, a)

    # dramatic: a few extra speculars on the upper-left of gold/white pixels
    if dramatic:
        for y in range(4, size - 4):
            for x in range(4, size - 4):
                col = port.get(x, y)
                if col is None:
                    continue
                # rim light on the far-left silhouette
                if port.get(x - 1, y) is None or (x > 2 and port.px[y][x - 2] is None):
                    if col in (N3, N4, N2):
                        port.set(x, y, N1 if col != N4 else N3)
                    elif col == G3:
                        port.set(x, y, G2)
                    elif col == G2:
                        port.set(x, y, G1)
    enforce(port)
    return port


def render_portrait() -> Canvas:
    p = _base()
    p.expression = "focus"
    p.mal_r = (112, 48)
    p.hd_r = (100, 62)
    p.el_r = (94, 58)
    return _bust_card(render_pose(p), 64, dramatic=False)


def render_portrait_large() -> Canvas:
    """128x128 SF2 Turbo VS-screen bust with a spotlight from upper-left."""
    p = _base()
    p.expression = "grit"
    p.mal_l, p.mal_r = (18, 70), (118, 40)
    p.hd_l, p.hd_r = (28, 78), (104, 54)
    p.el_l, p.el_r = (36, 66), (96, 52)
    body = render_pose(p)
    return _bust_card(body, 128, dramatic=True)


# ---- projectile / super (16-bit metallic shock) ---------------------------

def _arc(c, cx, cy, rx, ry, ramp, opening=115, broken=False):
    """Right-opening crescent using the gold (or given) ramp, metallic."""
    x0, x1 = int(cx - rx - 2), int(cx + rx + 2)
    y0, y1 = int(cy - ry - 2), int(cy + ry + 2)
    lite, mid, sh, core = (ramp + (ramp[-1],))[:4] if len(ramp) >= 3 else (G1, G2, G3, G4)
    if len(ramp) == 3:
        lite, mid, sh, core = ramp[0], ramp[1], ramp[2], ramp[2]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = ((x + 0.5) - cx) / (rx or 1)
            dy = ((y + 0.5) - cy) / (ry or 1)
            r2 = dx * dx + dy * dy
            if not (0.72 <= r2 <= 1.05):
                continue
            ang = math.degrees(math.atan2((y + 0.5) - cy, (x + 0.5) - cx))
            if ang > opening or ang < -opening:
                continue
            if broken and (abs(ang) % 26) < 7:
                continue
            # metallic: highlight upper-left of the ring, dark core lower-right
            if (dx + dy) < -0.35:
                col = lite
            elif (dx + dy) < 0.15:
                col = mid
            elif (dx + dy) < 0.7:
                col = sh
            else:
                col = core
            c.set(x, y, col)


def render_projectile_frames() -> List[Canvas]:
    w, h = PROJECTILE["frameWidth"], PROJECTILE["frameHeight"]
    frames = []
    for i in range(PROJECTILE["frames"]):
        c = Canvas(w, h)
        ox = 10 + i * 6
        oy = 32
        radius = 8 + i * 7
        radius = min(radius, 86 - ox)
        n_rings = 1 + (1 if i >= 1 else 0) + (1 if i >= 3 else 0)
        for r_i in range(n_rings):
            rr = radius - r_i * 7
            if rr < 4:
                continue
            _arc(c, ox, oy, rr, rr * 0.86, RAMPS["gold"],
                 opening=120, broken=(i >= 5 and r_i == 0))
        if i <= 2:
            fill_ellipse(c, ox, oy, max(3, 6 - i), max(3, 6 - i), RAMPS["gold"], core=G4)
            specular(c, ox - 1, oy - 1, G1, n=2)
        if i == 5:
            for deg in range(-70, 75, 14):
                x2 = ox + math.cos(math.radians(deg)) * (radius + 4)
                y2 = oy + math.sin(math.radians(deg)) * (radius * 0.86 + 3)
                if 2 <= x2 < w - 2 and 2 <= y2 < h - 2:
                    c.set(int(x2), int(y2), G1 if deg < 0 else G2)
        enforce(c)
        # a dark selective outline around the wave
        frames.append(c)
    return frames


def render_super_frames() -> List[Canvas]:
    w, h = SUPER["frameWidth"], SUPER["frameHeight"]
    frames = []
    cx, cy = 64, 64
    for i in range(SUPER["frames"]):
        c = Canvas(w, h)
        rad = 7 + i * 5
        core_r = max(3, 8 - i)
        if i <= 3:
            fill_ellipse(c, cx, cy, core_r, core_r * 0.85, RAMPS["gold"], core=G4)
            specular(c, cx - 2, cy - 2, G1, n=2)
        n_rings = 1 + (1 if i >= 1 else 0) + (1 if i >= 2 else 0) + (1 if i >= 4 else 0)
        for r_i in range(n_rings):
            rr = 10 + i * 7 - r_i * 7
            if rr < 6:
                continue
            _arc(c, cx, cy, rr, rr * 0.72, RAMPS["gold"],
                 opening=140, broken=(i >= 5 and r_i == 0))
        if i >= 1:
            # short lightning ticks from the outer ring, not through the core
            outer = 10 + i * 7
            for deg, extra in ((-80, 6), (-100, 4), (80, 6), (100, 4),
                               (-20, 8), (20, 8), (-50, 5), (50, 5)):
                x1 = cx + math.cos(math.radians(deg)) * (outer - 2)
                y1 = cy + math.sin(math.radians(deg)) * (outer * 0.72 - 2)
                x2 = cx + math.cos(math.radians(deg)) * (outer + extra)
                y2 = cy + math.sin(math.radians(deg)) * (outer * 0.72 + extra)
                if 2 <= x2 < w - 2 and 2 <= y2 < h - 2:
                    line(c, x1, y1, x2, y2, G1 if i < 4 else G2)
                    c.set(int(x2), int(y2), W1)
        if i == 5:
            for deg in range(-120, 130, 16):
                x2 = cx + math.cos(math.radians(deg)) * 38
                y2 = cy + math.sin(math.radians(deg)) * 28
                if 2 <= x2 < w - 2 and 2 <= y2 < h - 2:
                    c.set(int(x2), int(y2), G1 if deg < 0 else G3)
        enforce(c)
        frames.append(c)
    return frames


def animation_boxes(name: str) -> dict:
    """AABBs in 128-wide frame space (SHIFT_BOXES is False)."""
    stand = {"x": 42, "y": 8, "w": 56, "h": 103}
    boxes = {"hurtbox": stand}
    if name == "crouch":
        boxes["hurtbox"] = {"x": 40, "y": 28, "w": 58, "h": 83}
    elif name == "block":
        boxes["hurtbox"] = {"x": 44, "y": 16, "w": 60, "h": 95}
        boxes["blockbox"] = {"x": 64, "y": 44, "w": 36, "h": 40}
    elif name == "punch":
        boxes["hitbox"] = {"frames": [1, 2], "x": 108, "y": 34, "w": 18, "h": 22}
    elif name == "kick":
        boxes["hitbox"] = {"frames": [1, 2, 3], "x": 100, "y": 48, "w": 26, "h": 22}
    elif name == "special":
        boxes["hitbox"] = {"frames": [4, 5], "x": 70, "y": 36, "w": 36, "h": 40}
        boxes["spawn_projectile_on"] = 4
    elif name == "jump":
        boxes["hurtbox"] = {"x": 40, "y": 8, "w": 58, "h": 96}
    elif name == "ko":
        boxes["hurtbox"] = {"x": 16, "y": 40, "w": 96, "h": 71}
    elif name == "hit":
        boxes["hurtbox"] = {"x": 28, "y": 10, "w": 60, "h": 101}
    return boxes
