"""Reusable 16-bit body / uniform / instrument parts.

Drawn in frame space (128x112, anchor 64,111). Light from upper-left.
All colors come from the 15-color palette.
"""

from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple

from pxart.canvas import Canvas

from .draw import (
    LIGHT,
    crease,
    fill_ellipse,
    fill_poly,
    line,
    selective_outline,
    shade_limb,
    specular,
)
from .palette import G1, G2, G3, G4, K, N1, N2, N3, N4, S1, S2, S3, W1, W2, W3, RAMPS

Point = Tuple[float, float]


# ---------------------------------------------------------------------------
# Head, shako, plume
# ---------------------------------------------------------------------------

def draw_head(c: Canvas, fx, fy, expression: str = "idle") -> None:
    """3/4 head, facing right. (fx, fy) is the face center."""
    # skull (slightly shorter so the jaw can be a real chin, not a balloon)
    fill_ellipse(c, fx, fy + 0.2, 11.6, 11.2, RAMPS["skin"])
    # angular 3/4 jaw — a polygon, not a second ellipse
    jaw = [
        (fx - 8.0, fy + 3.0),
        (fx - 7.5, fy + 7.5),
        (fx - 3.5, fy + 10.2),
        (fx + 1.5, fy + 11.0),
        (fx + 6.5, fy + 9.0),
        (fx + 9.0, fy + 5.0),
        (fx + 8.5, fy + 1.5),
        (fx + 6.0, fy - 1.0),
    ]
    fill_poly(c, jaw, RAMPS["skin"], origin=(fx - 2, fy + 2), axis=(fx + 4, fy + 10))
    # far ear, drawn AFTER the skull so it actually shows on the left
    fill_ellipse(c, fx - 12.2, fy + 1.5, 2.4, 3.2, RAMPS["skin"])
    c.set(int(fx - 13), int(fy + 1), S3)
    c.set(int(fx - 11), int(fy + 1), S2)
    # temple / cheek plane
    c.set(int(fx - 5), int(fy + 1), S1)
    c.set(int(fx - 4), int(fy + 2), S1)
    c.set(int(fx - 3), int(fy + 0), S1)
    # hair under the shako (temples + a hairline)
    for dx, dy in ((-9, -4), (-10, -3), (-10, -2), (-9, -1),
                   (-8, -5), (8, -4), (9, -3), (9, -2),
                   (-6, -6), (-4, -6), (3, -6), (5, -6)):
        c.set(int(fx + dx), int(fy + dy), K)
    c.set(int(fx - 9), int(fy + 0), N4)
    c.set(int(fx + 8), int(fy - 1), N4)

    _face_features(c, int(round(fx)), int(round(fy)), expression)

    # chin plane (short, not a hanging oval)
    c.set(int(fx + 1), int(fy + 10), S3)
    c.set(int(fx + 2), int(fy + 9), S3)
    c.set(int(fx + 0), int(fy + 10), S2)


def _face_features(c: Canvas, ix: int, iy: int, expression: str) -> None:
    # 3/4: left (far) eye smaller, right eye more open
    lx, rx, ey = ix - 5, ix + 4, iy - 1

    def brow(x, y, shape="flat"):
        if shape == "flat":
            line(c, x - 2, y, x + 2, y, K)
            c.set(x - 2, y + 1, K)
        elif shape == "down":
            c.set(x - 2, y - 1, K)
            c.set(x - 1, y, K)
            c.set(x, y, K)
            c.set(x + 1, y + 1, K)
            c.set(x + 2, y + 1, K)
        elif shape == "up":
            c.set(x - 2, y + 1, K)
            c.set(x - 1, y, K)
            c.set(x, y - 1, K)
            c.set(x + 1, y, K)
            c.set(x + 2, y + 1, K)
        else:
            line(c, x - 2, y, x + 2, y, K)

    def eye_open(x, y, wide=False):
        c.set(x - 1, y, W1)
        c.set(x, y, W1)
        c.set(x + 1, y, W1)
        c.set(x - 1, y + 1, W2)
        c.set(x, y + 1, K)       # pupil
        c.set(x + 1, y + 1, K)
        c.set(x - 1, y, W1)
        c.set(x, y, K)
        c.set(x + 1, y, W1)
        if wide:
            c.set(x, y - 1, W1)
            c.set(x - 1, y - 1, W1)
        # lower lid
        c.set(x - 1, y + 1, S3)
        c.set(x + 1, y + 1, S3)
        # catchlight
        c.set(x - 1, y, W1)

    def eye_shut(x, y):
        line(c, x - 2, y + 1, x + 2, y + 1, K)

    def eye_x(x, y):
        c.set(x - 1, y, K)
        c.set(x + 1, y, K)
        c.set(x, y - 1, K)
        c.set(x, y + 1, K)
        c.set(x - 1, y - 1, K)
        c.set(x + 1, y + 1, K)

    # brows + eyes
    if expression in ("idle", "focus"):
        brow(lx, ey - 3, "flat")
        brow(rx, ey - 3, "flat")
        eye_open(lx, ey, wide=False)
        eye_open(rx, ey, wide=expression == "focus")
    elif expression in ("yell", "grit"):
        brow(lx, ey - 3, "down")
        brow(rx, ey - 3, "down")
        eye_open(lx, ey, wide=expression == "yell")
        eye_open(rx, ey, wide=True)
    elif expression == "hit":
        brow(lx, ey - 2, "up")
        brow(rx, ey - 2, "up")
        eye_shut(lx, ey)
        eye_shut(rx, ey)
    elif expression == "ko":
        brow(lx, ey - 2, "ko")
        brow(rx, ey - 2, "ko")
        eye_x(lx, ey)
        eye_x(rx, ey)

    # nose (3/4, a small plane)
    c.set(ix + 1, iy + 2, S3)
    c.set(ix + 2, iy + 3, S3)
    c.set(ix + 1, iy + 3, S2)
    c.set(ix + 2, iy + 2, S1)

    # mouth
    if expression == "idle":
        c.set(ix, iy + 6, S3)
        c.set(ix + 1, iy + 6, S3)
        c.set(ix + 2, iy + 6, S3)
    elif expression == "focus":
        line(c, ix - 1, iy + 6, ix + 2, iy + 6, S3)
    elif expression == "yell":
        c.set(ix, iy + 6, K)
        c.set(ix + 1, iy + 6, K)
        c.set(ix + 2, iy + 6, K)
        c.set(ix + 1, iy + 7, K)
        c.set(ix, iy + 7, S3)
        c.set(ix + 2, iy + 7, S3)
    elif expression == "grit":
        line(c, ix - 1, iy + 6, ix + 2, iy + 7, S3)
        c.set(ix + 1, iy + 6, K)
    elif expression == "hit":
        c.set(ix, iy + 7, S3)
        c.set(ix + 1, iy + 6, S3)
        c.set(ix + 2, iy + 7, S3)
    elif expression == "ko":
        c.set(ix, iy + 7, S3)
        c.set(ix + 1, iy + 8, S3)
        c.set(ix + 2, iy + 7, S3)


def draw_shako(c: Canvas, fx, fy) -> Tuple[float, float]:
    """Tall navy shako. Returns the plume socket."""
    hx = fx
    bottom = fy - 8
    top = bottom - 16
    # Crown ellipse sits at (hx, top+1) with ry=3, plus a 1px outline,
    # so keep top >= 5 or the hat clips the 2px top margin on jumps.
    if top < 5:
        top = 5
    # body: trapezoid (slightly narrower at the crown)
    pts = [
        (hx - 9.0, top + 1),
        (hx + 9.0, top + 1),
        (hx + 11.2, bottom),
        (hx - 11.2, bottom),
    ]
    fill_poly(c, pts, RAMPS["navy"], origin=(hx, (top + bottom) / 2))
    # rounded crown
    fill_ellipse(c, hx, top + 1.0, 9.2, 3.0, RAMPS["navy"])
    # gold top rim (thin, metallic)
    line(c, hx - 7, top, hx + 7, top, G2)
    c.set(int(hx - 6), int(top), G1)
    c.set(int(hx - 5), int(top), G1)
    c.set(int(hx + 6), int(top), G4)
    c.set(int(hx + 7), int(top + 1), G3)
    # gold band at the brim
    by = int(round(bottom))
    line(c, hx - 11, by, hx + 11, by, G2)
    line(c, hx - 10, by - 1, hx + 10, by - 1, G1)
    line(c, hx - 10, by + 1, hx + 11, by + 1, G3)
    c.set(int(hx - 10), by - 1, G1)
    c.set(int(hx + 10), by + 1, G4)
    # dark visor jutting forward-right
    line(c, hx - 1, by + 2, hx + 11, by + 2, N4)
    line(c, hx + 3, by + 3, hx + 10, by + 3, K)
    # badge — small metallic shield, not a blob
    bx, by = hx + 1.0, (top + bottom) / 2 + 0.5
    badge = [
        (bx, by - 4),
        (bx + 3, by - 2),
        (bx + 3, by + 1),
        (bx, by + 4),
        (bx - 3, by + 1),
        (bx - 3, by - 2),
    ]
    fill_poly(c, badge, RAMPS["gold"], origin=(bx - 1, by - 2), axis=(bx + 2, by + 3))
    c.set(int(bx - 1), int(by - 2), G1)
    c.set(int(bx), int(by - 3), G1)
    c.set(int(bx + 1), int(by + 2), G4)
    c.set(int(bx), int(by), G3)
    # chin-strap clips on the band, a thin curve under the chin
    c.set(int(hx - 11), by, G2)
    c.set(int(hx + 11), by, G3)
    # strap under the chin (1 px)
    c.set(int(fx - 7), int(fy + 8), G4)
    c.set(int(fx - 4), int(fy + 10), G3)
    c.set(int(fx + 2), int(fy + 11), G3)
    c.set(int(fx + 6), int(fy + 9), G4)
    return (hx + 0.5, top - 0.4)


def draw_plume(c: Canvas, sx, sy) -> None:
    """Gold feather plume with a dark core and a specular tip. Stays below y=2."""
    tip = 12
    if sy - tip < 3:
        sy = 3 + tip
    # quill (dark core up the middle)
    line(c, sx, sy + 1, sx + 1, sy - tip + 2, G4)
    line(c, sx - 1, sy, sx, sy - tip + 4, G3)
    # layered barbs: left = lit, right = core
    for dy, spread in ((-1, 3), (-3, 4), (-5, 4), (-7, 3), (-9, 3), (-11, 2)):
        c.set(int(round(sx - spread)), int(round(sy + dy)), G1)
        c.set(int(round(sx - spread + 1)), int(round(sy + dy)), G2)
        c.set(int(round(sx + 1)), int(round(sy + dy)), G2)
        c.set(int(round(sx + spread - 1)), int(round(sy + dy + 1)), G3)
        c.set(int(round(sx + spread)), int(round(sy + dy + 1)), G4)
    c.set(int(round(sx)), int(round(sy - tip)), G1)
    c.set(int(round(sx + 1)), int(round(sy - tip + 1)), G2)
    c.set(int(round(sx - 1)), int(round(sy - tip + 2)), G1)
    fill_ellipse(c, sx, sy + 1.2, 1.8, 1.6, RAMPS["gold"])
    specular(c, sx - 0.5, sy + 0.6, G1, n=1)


def draw_head_full(c: Canvas, fx, fy, expression="idle") -> None:
    draw_head(c, fx, fy, expression)
    sock = draw_shako(c, fx, fy)
    draw_plume(c, sock[0], sock[1])


# ---------------------------------------------------------------------------
# Torso (jacket) and cloth folds
# ---------------------------------------------------------------------------

def draw_torso(c: Canvas, sh_l: Point, sh_r: Point, hip: Point, folds: str = "stand") -> None:
    shx = (sh_l[0] + sh_r[0]) / 2
    shy = (sh_l[1] + sh_r[1]) / 2
    hx, hy = hip
    # heavy chest, nipped waist, slightly wider hips
    chest_r = max(13.0, abs(sh_r[0] - sh_l[0]) * 0.48)
    waist_r = chest_r * 0.78
    hip_r = chest_r * 0.92
    mid_y = (shy + hy) / 2
    pts = [
        (sh_l[0] - 3, shy - 2),
        (shx, shy - 4),              # collar base
        (sh_r[0] + 3, shy - 2),
        (sh_r[0] + 5, shy + 8),      # right chest
        (shx + waist_r, mid_y),
        (hx + hip_r, hy + 2),
        (hx, hy + 5),
        (hx - hip_r, hy + 2),
        (shx - waist_r, mid_y),
        (sh_l[0] - 5, shy + 8),
    ]
    fill_poly(c, pts, RAMPS["navy"], origin=(shx - 4, shy + 6))

    # high gold collar
    col = [
        (shx - 6, shy - 4),
        (shx + 5, shy - 4),
        (shx + 7, shy + 2),
        (shx + 2, shy + 5),
        (shx - 3, shy + 5),
        (shx - 8, shy + 2),
    ]
    fill_poly(c, col, RAMPS["gold"], origin=(shx - 2, shy - 1))
    specular(c, shx - 3, shy - 3, G1, n=2)

    # epaulets
    fill_ellipse(c, sh_l[0] - 1, shy, 5.0, 3.0, RAMPS["gold"], core=G4)
    fill_ellipse(c, sh_r[0] + 1, shy, 5.0, 3.0, RAMPS["gold"], core=G4)
    specular(c, sh_l[0] - 2, shy - 1, G1, n=2)
    # reflected rim on the far epaulet
    c.set(int(sh_r[0] + 5), int(shy), G3)
    c.set(int(sh_r[0] + 4), int(shy - 1), G2)

    # white cross-belt (baldric) from left shoulder to right hip
    belt = [
        (sh_l[0] + 2, shy + 2),
        (sh_l[0] + 7, shy + 2),
        (hx + 6, hy + 1),
        (hx + 1, hy + 3),
    ]
    fill_poly(c, belt, RAMPS["white"], origin=(shx - 2, mid_y))

    # gold buttons down the front (right of center, 3/4)
    for i, yoff in enumerate((6, 12, 18)):
        bx, by = shx + 2, shy + yoff
        c.set(int(bx), int(by), G2)
        c.set(int(bx - 1), int(by), G1)
        c.set(int(bx + 1), int(by), G4)

    # pose-specific folds
    _jacket_folds(c, sh_l, sh_r, hip, folds)


def _jacket_folds(c, sh_l, sh_r, hip, folds: str) -> None:
    shx = (sh_l[0] + sh_r[0]) / 2
    shy = (sh_l[1] + sh_r[1]) / 2
    hx, hy = hip
    mid_y = (shy + hy) / 2
    if folds == "stand":
        # a long fold under the left pec, a shorter one at the right waist
        crease(c, sh_l[0] + 4, shy + 10, shx - 2, mid_y + 2, N3, N1)
        crease(c, shx + 7, mid_y, hx + 6, hy - 1, N4, None)
        # armpit wrinkles
        crease(c, sh_l[0] + 1, shy + 6, sh_l[0] + 5, shy + 10, N4, N2)
        crease(c, sh_r[0] - 1, shy + 6, sh_r[0] - 5, shy + 10, N3, None)
    elif folds == "compress":
        # bunched (crouch / sit): horizontal creases
        crease(c, shx - 8, mid_y - 2, shx + 8, mid_y, N4, N1)
        crease(c, shx - 7, mid_y + 4, shx + 6, mid_y + 6, N3, N1)
        crease(c, sh_l[0] + 2, shy + 8, shx - 1, shy + 12, N4, N2)
    elif folds == "stretch_r":
        # punching / reaching right: stretched right, bunched left
        crease(c, sh_l[0] + 2, shy + 8, shx - 3, mid_y, N4, N1)
        crease(c, sh_l[0] + 4, shy + 12, shx - 1, mid_y + 4, N3, None)
        crease(c, shx + 4, shy + 8, sh_r[0] - 2, shy + 14, N3, N1)
    elif folds == "stretch_l":
        crease(c, sh_r[0] - 2, shy + 8, shx + 3, mid_y, N4, None)
        crease(c, sh_l[0] + 3, shy + 8, shx - 4, shy + 16, N3, N1)
    elif folds == "twist":
        crease(c, sh_l[0] + 6, shy + 6, shx + 4, mid_y + 2, N3, N1)
        crease(c, shx - 2, mid_y, hx + 4, hy, N4, None)
    elif folds == "windup":
        crease(c, sh_l[0] + 3, shy + 6, shx - 4, mid_y + 2, N4, N1)
        crease(c, shx + 6, shy + 10, hx + 8, hy - 2, N3, None)
    else:
        crease(c, sh_l[0] + 4, shy + 10, shx - 2, mid_y + 2, N3, N1)


def draw_neck(c: Canvas, face: Point, sh_l: Point, sh_r: Point) -> None:
    shx = (sh_l[0] + sh_r[0]) / 2
    shy = (sh_l[1] + sh_r[1]) / 2
    fx, fy = face
    pts = [
        (fx - 4, fy + 10),
        (fx + 5, fy + 10),
        (shx + 5, shy - 2),
        (shx - 5, shy - 2),
    ]
    fill_poly(c, pts, RAMPS["skin"], origin=(fx - 1, fy + 12))


# ---------------------------------------------------------------------------
# Arms, gloves, legs, shoes
# ---------------------------------------------------------------------------

def draw_shoulder(c: Canvas, sh, near=True) -> None:
    """Deltoid cap so the arm doesn't sprout out of a sausage stub."""
    r = 7.2 if near else 6.4
    fill_ellipse(c, sh[0], sh[1] + 1, r, r * 0.78, RAMPS["navy"])


def draw_arm(c: Canvas, sh, el, hd, near=True, muscle=0.2) -> None:
    draw_shoulder(c, sh, near=near)
    # upper arm
    r1 = 6.0 if near else 5.4
    r2 = 4.8 if near else 4.3
    shade_limb(c, sh[0], sh[1], el[0], el[1], r1, r2, RAMPS["navy"],
               muscle=muscle, flatten=0.76)
    # forearm (slightly slimmer)
    shade_limb(c, el[0], el[1], hd[0], hd[1], 4.4 if near else 4.0,
               3.6 if near else 3.3, RAMPS["navy"],
               muscle=muscle * 0.7, flatten=0.8)
    # elbow crease
    crease(c, el[0] - 2, el[1], el[0] + 2, el[1] + 1, N4, N2 if near else None)
    # cuff gold
    vx, vy = hd[0] - el[0], hd[1] - el[1]
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    cx, cy = hd[0] - ux * 5, hd[1] - uy * 5
    fill_ellipse(c, cx, cy, 3.2, 2.2, RAMPS["gold"], core=G4)
    if near:
        specular(c, cx - 1, cy - 1, G1, n=1)


def draw_glove(c: Canvas, hd: Point, aim: Optional[Point] = None, near=True) -> None:
    """A volume glove with a thumb and knuckle highlights — not a disk."""
    hx, hy = hd
    if aim is None:
        ux, uy = 1, 0
    else:
        vx, vy = aim[0] - hx, aim[1] - hy
        leng = math.hypot(vx, vy) or 1
        ux, uy = vx / leng, vy / leng
    px, py = -uy, ux
    # compact fist / palm — a mittened box, not a disk
    palm = [
        (hx + px * 2.6 - ux * 1.2, hy + py * 2.6 - uy * 1.2),
        (hx + px * 2.8 + ux * 3.2, hy + py * 2.8 + uy * 3.2),
        (hx + px * 0.4 + ux * 4.6, hy + py * 0.4 + uy * 4.6),
        (hx - px * 2.2 + ux * 4.0, hy - py * 2.2 + uy * 4.0),
        (hx - px * 2.8 + ux * 0.4, hy - py * 2.8 + uy * 0.4),
        (hx - px * 1.2 - ux * 1.6, hy - py * 1.2 - uy * 1.6),
    ]
    fill_poly(c, palm, RAMPS["white"], origin=(hx - 1, hy - 1), axis=(hx + ux * 4, hy + uy * 4))
    # four knuckle / fingertip bumps along the far edge
    for k, pr in ((0.15, -1.6), (0.42, -0.5), (0.68, 0.6), (0.90, 1.6)):
        fx_ = hx + ux * 4.4 + px * pr
        fy_ = hy + uy * 4.4 + py * pr
        c.set(int(round(fx_)), int(round(fy_)), W1 if near else W2)
        c.set(int(round(fx_ + ux)), int(round(fy_ + uy)), W2)
    # thumb, shorter, off the top side
    tx, ty = hx + px * 3.0 + ux * 0.4, hy + py * 3.0 + uy * 0.4
    fill_ellipse(c, tx, ty, 1.7, 1.4, RAMPS["white"])
    c.set(int(tx + px), int(ty + py), W3)
    # knuckles
    if near:
        for k in (0.25, 0.5, 0.75):
            specular(c, hx + px * 1.6 + ux * (1.6 + k * 2.4), hy + py * 1.6 + uy * (1.6 + k * 2.4), W1, n=1)
    # cuff edge already drawn as gold on the arm; a white wrinkle
    crease(c, hx - ux * 2 - px * 2, hy - uy * 2 - py * 2,
           hx - ux * 2 + px * 2, hy - uy * 2 + py * 2, W3, W1)


def draw_leg(c: Canvas, hip, kn, an, near=True, folds: str = "stand") -> None:
    shade_limb(c, hip[0], hip[1], kn[0], kn[1],
               6.6 if near else 6.0, 5.2 if near else 4.8,
               RAMPS["navy"], muscle=0.22 if near else 0.12, flatten=0.8)
    shade_limb(c, kn[0], kn[1], an[0], an[1],
               4.8 if near else 4.4, 3.6 if near else 3.3,
               RAMPS["navy"], muscle=0.1, flatten=0.82)
    # gold side stripe on the near (or both) pant
    vx, vy = kn[0] - hip[0], kn[1] - hip[1]
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    px, py = -uy, ux
    # stripe along the outer side
    s1x, s1y = hip[0] + px * 5, hip[1] + py * 5
    s2x, s2y = kn[0] + px * 4, kn[1] + py * 4
    line(c, s1x, s1y, s2x, s2y, G2)
    c.set(int(s1x), int(s1y), G1)
    # lower stripe
    vx, vy = an[0] - kn[0], an[1] - kn[1]
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    px, py = -uy, ux
    line(c, kn[0] + px * 3.5, kn[1] + py * 3.5,
         an[0] + px * 2.5, an[1] + py * 2.5, G2)
    # folds
    if folds == "stand":
        crease(c, hip[0] - 2, hip[1] + 6, kn[0] - 1, kn[1] - 4, N3, N1)
    elif folds == "bend":
        crease(c, kn[0] - 4, kn[1] - 2, kn[0] + 4, kn[1] + 1, N4, N1)
        crease(c, kn[0] - 3, kn[1] + 3, kn[0] + 2, kn[1] + 5, N3, None)
        crease(c, hip[0] - 3, hip[1] + 4, hip[0] + 3, hip[1] + 8, N4, N2)
    elif folds == "stretch":
        crease(c, hip[0] - 1, hip[1] + 5, kn[0], kn[1] - 3, N3, N1)


def draw_shoe(c: Canvas, an: Point, toe: Point, near=True) -> None:
    """Compact marching shoe: black upper, thick sole, short toe, defined heel."""
    ax, ay = an
    tx, ty = toe
    vx, vy = tx - ax, ty - ay
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    px, py = -uy, ux
    # short toe box (8px), heel 3px behind the ankle
    toe_len = min(leng, 8)
    tx = ax + ux * toe_len
    ty = ay + uy * toe_len
    hx, hy = ax - ux * 3.2, ay - uy * 3.2
    # if the foot is planted (toe near the ground line), flatten the sole
    planted = ty >= 106 or ay >= 102
    sole_drop = 2.0 if planted else 1.2
    # sole slab
    sole = [
        (hx - px * 0.5, hy + sole_drop + 1.5),
        (hx + px * 2.0, hy + sole_drop + 0.5),
        (tx + ux * 1.6 + px * 1.5, ty + sole_drop + 0.4),
        (tx + ux * 2.0 - px * 0.8, ty + sole_drop + 1.6),
        (hx - ux * 0.4 - px * 1.5, hy + sole_drop + 2.0),
    ]
    fill_poly(c, sole, (K, K, N4), origin=(ax, ay + 3), axis=(tx, ty + 3))
    # upper
    upper = [
        (hx + px * 4.2, hy + py * 0.2),
        (hx - px * 0.6, hy - 0.2),
        (tx + ux * 0.6 - px * 0.4, ty - 0.2),
        (tx + ux * 1.2 + px * 3.2, ty + py * 0.4),
        (ax + ux * 1.0 + px * 5.2, ay + py * 0.6),
    ]
    fill_poly(c, upper, (N4, K, K), origin=(ax, ay - 2), axis=(tx, ty - 1))
    # heel counter
    fill_ellipse(c, hx + px * 1.2, hy - 0.6, 2.2, 2.4, (N4, K, K))
    c.set(int(round(hx)), int(round(hy + sole_drop + 1)), K)
    # single-pixel toe-cap sheen (never a white blob)
    if near:
        c.set(int(round(tx + px * 2)), int(round(ty - 1)), W3)


# ---------------------------------------------------------------------------
# Bass drum + harness + mallets
# ---------------------------------------------------------------------------

def draw_harness(c: Canvas, sh_l: Point, sh_r: Point, inst: Point) -> None:
    # two gold straps from shoulders to the drum
    for sh in (sh_l, sh_r):
        pts = [
            (sh[0] - 2, sh[1] - 1),
            (sh[0] + 2, sh[1] - 1),
            (inst[0] + 3, inst[1] - 10),
            (inst[0] - 3, inst[1] - 10),
        ]
        fill_poly(c, pts, RAMPS["gold"], origin=((sh[0] + inst[0]) / 2, (sh[1] + inst[1]) / 2))
        specular(c, sh[0] - 1, sh[1], G1, n=1)


def draw_bass_drum(c: Canvas, inst: Point, rx: float = 18, ry: float = 15.5) -> None:
    """3/4 marching bass drum: brass shell, white head, metallic rim."""
    cx, cy = inst
    # shell (gold volume) — slightly bigger, peeking on the right and bottom
    fill_ellipse(c, cx + 2, cy + 1, rx + 3.5, ry + 2.5, RAMPS["gold"], core=G4)
    # reflected-light rim on the far right of the shell
    for i in range(-int(ry), int(ry) + 1):
        # right edge of the gold shell
        y = int(cy + i)
        # approximate x of the right rim
        t = 1 - (i / (ry + 2.5)) ** 2
        if t <= 0:
            continue
        x = int(round(cx + 2 + (rx + 3.5) * math.sqrt(t)))
        if abs(i) < ry * 0.7:
            c.set(x, y, G3)
            if abs(i) < ry * 0.35:
                c.set(x, y, G2)
    # dark core inside the shell lip (lower right)
    fill_ellipse(c, cx + 6, cy + 4, 6, 5, (G4, G4, G3))
    # front head (white) — force a 3-step volume: highlight, mid, shadow crescent
    fill_ellipse(c, cx - 1, cy - 0.5, rx, ry, RAMPS["white"], core=None)
    # upper-left specular patch
    for ox, oy in ((-8, -7), (-7, -8), (-6, -7), (-9, -5), (-5, -8), (-8, -5), (-4, -6)):
        c.set(int(cx - 1 + ox), int(cy - 0.5 + oy), W1)
    # lower-right form shadow
    for ox, oy in ((7, 6), (8, 4), (6, 8), (9, 2), (5, 9), (8, 7), (4, 8), (10, 0), (3, 9)):
        c.set(int(cx - 1 + ox), int(cy - 0.5 + oy), W3)
    # brass hoop around the head
    # draw as a thin ring by stamping gold on the ellipse edge
    _gold_hoop(c, cx - 1, cy - 0.5, rx, ry)
    # center cap
    fill_ellipse(c, cx + 1, cy + 1, 2.6, 2.4, RAMPS["gold"], core=G4)
    specular(c, cx, cy, G1, n=2)
    # tension rods (a few gold ticks around the hoop)
    for deg in range(-60, 240, 32):
        a = math.radians(deg)
        x = cx - 1 + math.cos(a) * (rx - 0.5)
        y = cy - 0.5 + math.sin(a) * (ry - 0.5)
        col = G1 if deg < 40 else G3
        c.set(int(round(x)), int(round(y)), col)


def _gold_hoop(c, cx, cy, rx, ry) -> None:
    x0, x1 = int(cx - rx - 1), int(cx + rx + 1)
    y0, y1 = int(cy - ry - 1), int(cy + ry + 1)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = ((x + 0.5) - cx) / rx
            dy = ((y + 0.5) - cy) / ry
            r2 = dx * dx + dy * dy
            if 0.86 <= r2 <= 1.08:
                # lit upper-left, dark lower-right
                col = G1 if (dx + dy) < -0.3 else (G2 if (dx + dy) < 0.4 else G4)
                c.set(x, y, col)


def draw_mallet(c: Canvas, hand: Point, head: Point) -> None:
    """Wooden shaft + white felt head + gold ferrule."""
    x1, y1 = hand
    x2, y2 = head
    vx, vy = x2 - x1, y2 - y1
    leng = math.hypot(vx, vy) or 1
    ux, uy = vx / leng, vy / leng
    # shaft as a thin faceted limb in the wood ramp
    shade_limb(c, x1, y1, x2 - ux * 4, y2 - uy * 4, 2.1, 1.7, RAMPS["wood"],
               muscle=0.0, flatten=0.88)
    # ferrule
    fx, fy = x2 - ux * 4.2, y2 - uy * 4.2
    fill_ellipse(c, fx, fy, 2.0, 1.7, RAMPS["gold"], core=G4)
    specular(c, fx - 0.5, fy - 0.5, G1, n=1)
    # felt head
    fill_ellipse(c, x2, y2, 5.2, 4.8, RAMPS["white"], core=None)
    specular(c, x2 - 2, y2 - 2, W1, n=3)
    c.set(int(x2 + 2), int(y2 + 2), W3)


# ---------------------------------------------------------------------------
# Full-body compose helper
# ---------------------------------------------------------------------------

def finish(c: Canvas) -> Canvas:
    """Selective outline, then enforce the 15-color palette."""
    from .palette import enforce
    selective_outline(c, default_dark=N4, near_black=K)
    enforce(c)
    return c
