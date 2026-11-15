"""Compose a 16-bit fighter pose into a 128x112 frame."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from PIL import Image

from pxart.body import ANCHOR_X, ANCHOR_Y, FRAME_H, FRAME_W
from pxart.canvas import Canvas

from .draw import fill_ellipse
from .palette import G1, W1, enforce
from .parts import (
    draw_arm,
    draw_bass_drum,
    draw_glove,
    draw_harness,
    draw_head_full,
    draw_leg,
    draw_mallet,
    draw_neck,
    draw_shoe,
    draw_torso,
    finish,
)

Point = Tuple[float, float]


@dataclass
class Pose16:
    face: Point = (62, 36)
    sh_l: Point = (47, 54)
    sh_r: Point = (80, 54)
    el_l: Point = (34, 66)
    el_r: Point = (98, 64)
    hd_l: Point = (28, 74)
    hd_r: Point = (106, 70)
    hip: Point = (64, 76)
    hip_l: Point = (56, 76)
    hip_r: Point = (72, 76)
    kn_l: Point = (52, 90)
    kn_r: Point = (76, 90)
    an_l: Point = (50, 104)
    an_r: Point = (76, 104)
    toe_l: Point = (62, 109)
    toe_r: Point = (88, 109)
    inst: Point = (70, 68)
    mal_l: Point = (22, 64)
    mal_r: Point = (114, 58)
    expression: str = "idle"
    folds: str = "stand"          # jacket
    folds_l: str = "stand"        # left leg
    folds_r: str = "stand"
    hands_over: str = "both"      # both, right, left, none
    leg_over: Optional[str] = None
    flash: bool = False
    slam: bool = False
    head_rot: int = 0
    drum_rx: float = 18
    drum_ry: float = 15.5


def shift_upper(p: Pose16, dx=0, dy=0) -> None:
    keys = (
        "face", "sh_l", "sh_r", "el_l", "el_r", "hd_l", "hd_r",
        "hip", "hip_l", "hip_r", "inst", "mal_l", "mal_r",
    )
    for k in keys:
        x, y = getattr(p, k)
        setattr(p, k, (x + dx, y + dy))


def shift_all(p: Pose16, dx=0, dy=0) -> None:
    """Move every joint, including legs and feet (jump / launch)."""
    shift_upper(p, dx, dy)
    for k in ("kn_l", "kn_r", "an_l", "an_r", "toe_l", "toe_r"):
        x, y = getattr(p, k)
        setattr(p, k, (x + dx, y + dy))


def _rotate_around(layer: Canvas, pivot, deg: int) -> Canvas:
    if not deg:
        return layer
    img = layer.to_image()
    rot = img.rotate(int(deg), resample=Image.Resampling.NEAREST,
                     center=pivot, expand=False, fillcolor=(0, 0, 0, 0))
    out = Canvas(layer.w, layer.h)
    px = rot.load()
    for y in range(layer.h):
        for x in range(layer.w):
            r, g, b, a = px[x, y]
            if a:
                out.px[y][x] = (r, g, b, a)
    return out


def render_pose(p: Pose16) -> Canvas:
    c = Canvas(FRAME_W, FRAME_H)

    def legs_and_shoes(which=None):
        if which in (None, "left"):
            draw_leg(c, p.hip_l, p.kn_l, p.an_l, near=False, folds=p.folds_l)
            draw_shoe(c, p.an_l, p.toe_l, near=False)
        if which in (None, "right"):
            draw_leg(c, p.hip_r, p.kn_r, p.an_r, near=True, folds=p.folds_r)
            draw_shoe(c, p.an_r, p.toe_r, near=True)

    # far leg first, then near (right) unless a kick needs the far leg over
    if p.leg_over == "left":
        legs_and_shoes("right")
        legs_and_shoes("left")
    else:
        legs_and_shoes("left")
        legs_and_shoes("right")
        if p.leg_over == "right":
            legs_and_shoes("right")

    draw_neck(c, p.face, p.sh_l, p.sh_r)
    draw_torso(c, p.sh_l, p.sh_r, p.hip, folds=p.folds)

    head = Canvas(FRAME_W, FRAME_H)
    draw_head_full(head, p.face[0], p.face[1], p.expression)
    if p.head_rot:
        head = _rotate_around(head, p.face, p.head_rot)
    if not p.head_rot:
        c.blit(head)

    # far arm behind the drum
    draw_arm(c, p.sh_l, p.el_l, p.hd_l, near=False)
    if p.hands_over not in ("left", "both"):
        draw_mallet(c, p.hd_l, p.mal_l)
        draw_glove(c, p.hd_l, p.mal_l, near=False)

    draw_harness(c, p.sh_l, p.sh_r, p.inst)
    draw_bass_drum(c, p.inst, p.drum_rx, p.drum_ry)

    if p.hands_over in ("left", "both"):
        draw_mallet(c, p.hd_l, p.mal_l)
        draw_glove(c, p.hd_l, p.mal_l, near=False)

    draw_arm(c, p.sh_r, p.el_r, p.hd_r, near=True)
    draw_mallet(c, p.hd_r, p.mal_r)
    draw_glove(c, p.hd_r, p.mal_r, near=True)

    if p.head_rot:
        c.blit(head)

    if p.flash:
        if p.slam:
            bx = (p.mal_l[0] + p.mal_r[0]) / 2
            by = (p.mal_l[1] + p.mal_r[1]) / 2
            fill_ellipse(c, bx, by, 7, 6, (G1, W1, G1))
        elif p.mal_r:
            fill_ellipse(c, p.mal_r[0], p.mal_r[1], 5, 4.5, (G1, W1, G1))

    return finish(c)
