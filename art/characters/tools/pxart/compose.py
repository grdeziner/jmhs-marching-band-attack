"""Shared pose helpers and a generic fighter compositor."""

from __future__ import annotations

from typing import Callable, Optional

from PIL import Image

from .body import (
    FRAME_H,
    FRAME_W,
    Look,
    Pose,
    draw_arm,
    draw_glove,
    draw_guard_torso,
    draw_head,
    draw_leg,
    draw_legs,
    draw_neck,
    draw_shoe,
    draw_shoes,
    draw_torso,
    get_look,
    layer_and_outline,
    new_layer,
)
from .canvas import Canvas

STANDARD_ANIMS = [
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

UPPER_KEYS = [
    "face", "sh_l", "sh_r", "el_l", "el_r", "hd_l", "hd_r",
    "hip", "hip_l", "hip_r", "inst",
]


def shift(p: Pose, keys, dx=0, dy=0) -> None:
    for k in keys:
        x, y = getattr(p, k)
        setattr(p, k, (x + dx, y + dy))
    if "mal_l" in keys or "inst" in keys:
        pass
    if p.mal_l and ("mal_l" in keys or any(k in UPPER_KEYS for k in keys) and "mal_l" not in keys):
        # handled below by shift_upper
        pass


def shift_pts(p: Pose, keys, dx=0, dy=0) -> None:
    for k in keys:
        v = getattr(p, k)
        if v is not None:
            setattr(p, k, (v[0] + dx, v[1] + dy))


def shift_upper(p: Pose, dx=0, dy=0) -> None:
    shift_pts(p, UPPER_KEYS + ["mal_l", "mal_r"], dx, dy)


def _part(draw_fn) -> Canvas:
    return layer_and_outline(draw_fn)


def rotate_around(layer: Canvas, pivot, deg: int) -> Canvas:
    if not deg:
        return layer
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


Paint = Optional[Callable[[Canvas, Pose], None]]


def render_character(
    pose: Pose,
    *,
    clothing: str = "uniform",
    paint_back: Paint = None,
    paint_mid: Paint = None,
    paint_front: Paint = None,
    paint_flash: Paint = None,
) -> Canvas:
    """Composite a fighter. Clothing is 'uniform' (marching jacket) or 'guard'.

    paint_back  — behind the body (far tubing, trail)
    paint_mid   — after torso/head, before or with arms (instrument body)
    paint_front — weapons, flag, bell, mallets in front of the hands
    paint_flash — un-outlined impact flashes on top
    """
    look = get_look(pose)
    out = new_layer()
    leg_over = getattr(pose, "leg_over", None)
    hands_over = getattr(pose, "hands_over", "both") or "both"
    head_over = bool(getattr(pose, "head_rot", 0))

    if paint_back:
        out.blit(_part(lambda c: paint_back(c, pose)))

    out.blit(_part(lambda c: (draw_legs(c, pose), draw_shoes(c, pose))))

    def torso_fn(c):
        draw_neck(c, pose)
        if clothing == "guard":
            draw_guard_torso(c, pose)
        else:
            draw_torso(c, pose)

    out.blit(_part(torso_fn))

    head = _part(lambda c: draw_head(c, pose))
    if getattr(pose, "head_rot", 0):
        head = rotate_around(head, pose.face, pose.head_rot)
    if not head_over:
        out.blit(head)

    def arm_l(c, glove=True):
        draw_arm(c, pose.sh_l, pose.el_l, pose.hd_l, pose.mal_l, near=False, include_glove=glove, look=look)

    def arm_r(c, glove=True):
        draw_arm(c, pose.sh_r, pose.el_r, pose.hd_r, pose.mal_r, near=True, include_glove=glove, look=look)

    # Far (left) arm
    if hands_over not in ("left", "both"):
        out.blit(_part(lambda c: arm_l(c, glove=True)))
    else:
        out.blit(_part(lambda c: arm_l(c, glove=False)))

    if paint_mid:
        out.blit(_part(lambda c: paint_mid(c, pose)))

    # Near (right) arm
    if hands_over not in ("right", "both"):
        out.blit(_part(lambda c: arm_r(c, glove=True)))
    else:
        out.blit(_part(lambda c: arm_r(c, glove=False)))

    # Gloves in front when flagged
    if hands_over in ("left", "both"):
        out.blit(_part(lambda c: draw_glove(c, pose.hd_l, pose.mal_l, near=False, look=look)))
    if hands_over in ("right", "both"):
        out.blit(_part(lambda c: draw_glove(c, pose.hd_r, pose.mal_r, near=True, look=look)))

    if paint_front:
        out.blit(_part(lambda c: paint_front(c, pose)))

    if leg_over == "right":
        def only_right(c):
            draw_leg(c, pose.hip_r, pose.kn_r, pose.an_r, near=True, outward=1, look=look)
            _, tr = pose.toes()
            draw_shoe(c, pose.an_r, tr, near=True, look=look)
        out.blit(_part(only_right))
    elif leg_over == "left":
        def only_left(c):
            draw_leg(c, pose.hip_l, pose.kn_l, pose.an_l, near=False, outward=-1, look=look)
            tl, _ = pose.toes()
            draw_shoe(c, pose.an_l, tl, near=False, look=look)
        out.blit(_part(only_left))

    if head_over:
        out.blit(head)

    if paint_flash and (pose.flash or getattr(pose, "slam", False) or pose.struck):
        fx = new_layer()
        paint_flash(fx, pose)
        out.blit(fx)

    return out


def bust_portrait(body: Canvas, bg_mid, bg_lt, bg_dk, gold, margin=3) -> Canvas:
    """64x64 select-screen bust from a full-frame render, navy field + gold corners."""
    from .palette import NAVY, NAVY_DK, NAVY_LT, GOLD
    bg_mid = bg_mid or NAVY
    bg_lt = bg_lt or NAVY_LT
    bg_dk = bg_dk or NAVY_DK
    gold = gold or GOLD
    port = Canvas(64, 64)
    for y in range(64):
        for x in range(64):
            edge = x < 2 or y < 2 or x > 61 or y > 61
            if edge:
                port.set(x, y, bg_dk)
            else:
                dx, dy = (x - 32) / 32, (y - 32) / 32
                port.set(x, y, bg_mid if dx * dx + dy * dy > 0.72 else bg_lt)
    for (x, y) in (
        (2, 2), (3, 2), (2, 3),
        (61, 2), (60, 2), (61, 3),
        (2, 61), (3, 61), (2, 60),
        (61, 61), (60, 61), (61, 60),
    ):
        port.set(x, y, gold)

    top, left, right, bottom = body.h, body.w, 0, 0
    for y in range(body.h):
        for x in range(body.w):
            if body.get(x, y) is None or y > 80:
                continue
            top = min(top, y)
            bottom = max(bottom, y)
            left = min(left, x)
            right = max(right, x)
    ox = int((left + right) / 2) - 32
    oy = max(0, top - margin)
    if oy + 64 > body.h:
        oy = max(0, body.h - 64)
    ox = max(0, min(ox, body.w - 64))
    for y in range(64):
        for x in range(64):
            col = body.get(ox + x, oy + y)
            if col is not None:
                port.px[y][x] = col
    return port
