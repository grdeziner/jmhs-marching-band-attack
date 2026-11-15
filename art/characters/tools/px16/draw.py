"""16-bit drawing: faceted volumes, selective outlines, creases, speculars.

All writes are opaque palette colors — no blending, no new colors.
"""

from __future__ import annotations

import math
from typing import Iterable, Optional, Sequence, Tuple

from pxart.canvas import Canvas

from .palette import Color, K, N4, nearest

Point = Tuple[float, float]
LIGHT = (-0.55, -0.72)  # upper-left, slightly front (SF2 convention)


def _dot_light(nx, ny, light=LIGHT) -> float:
    lx, ly = light
    ln = math.hypot(lx, ly) or 1.0
    return (nx * lx + ny * ly) / ln


def _pick(ramp: Sequence[Color], t: float) -> Color:
    """t in [0, 1], 0 = lightest, 1 = darkest."""
    if len(ramp) == 1:
        return ramp[0]
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    x = t * (len(ramp) - 1)
    i = int(round(x))
    return ramp[max(0, min(len(ramp) - 1, i))]


def _inside_poly(pts: Sequence[Point], x: float, y: float) -> bool:
    # even-odd ray test
    n = len(pts)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y):
            den = (yj - yi) or 1e-9
            xinters = (xj - xi) * (y - yi) / den + xi
            if x < xinters:
                inside = not inside
        j = i
    return inside


def fill_poly(
    c: Canvas,
    pts: Sequence[Point],
    ramp: Sequence[Color],
    light=LIGHT,
    origin: Optional[Point] = None,
    axis: Optional[Point] = None,
) -> None:
    """Fill a polygon with a ramp shaded by a pseudo-normal from `origin`/`axis`.

    If `axis` is given (a second point), shading is cylindrical around that
    spine. Otherwise it's spherical around `origin` (default: polygon centroid).
    """
    if len(pts) < 3:
        return
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = int(math.floor(min(xs))), int(math.ceil(max(xs)))
    y0, y1 = int(math.floor(min(ys))), int(math.ceil(max(ys)))
    if origin is None:
        origin = (sum(xs) / len(xs), sum(ys) / len(ys))
    ox, oy = origin
    if axis is not None:
        ux, uy = axis[0] - ox, axis[1] - oy
        leng = math.hypot(ux, uy) or 1.0
        ux, uy = ux / leng, uy / leng
    else:
        ux = uy = leng = None

    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px, py = x + 0.5, y + 0.5
            if not _inside_poly(pts, px, py):
                continue
            if ux is not None:
                # cylindrical: normal is the perpendicular from the spine
                t = (px - ox) * ux + (py - oy) * uy
                t = 0.0 if t < 0 else leng if t > leng else t
                cx, cy = ox + t * ux, oy + t * uy
                dx, dy = px - cx, py - cy
            else:
                dx, dy = px - ox, py - oy
            dist = math.hypot(dx, dy) or 1.0
            nx, ny = dx / dist, dy / dist
            d = _dot_light(nx, ny, light)  # 1 = fully lit, -1 = fully dark
            # bias slightly toward mid so we use the whole ramp without
            # painting the whole left side as a single highlight
            tshade = 0.5 - 0.5 * d
            c.set(x, y, _pick(ramp, tshade))


def fill_ellipse(
    c: Canvas,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    ramp: Sequence[Color],
    light=LIGHT,
    core: Optional[Color] = None,
) -> None:
    """Shaded ellipse (spherical). Optional `core` stamps the darkest recess."""
    x0, x1 = int(math.floor(cx - rx - 1)), int(math.ceil(cx + rx + 1))
    y0, y1 = int(math.floor(cy - ry - 1)), int(math.ceil(cy + ry + 1))
    rx = max(rx, 0.6)
    ry = max(ry, 0.6)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = ((x + 0.5) - cx) / rx
            dy = ((y + 0.5) - cy) / ry
            r2 = dx * dx + dy * dy
            if r2 > 1.0:
                continue
            # normal of a sphere/ellipsoid facing the viewer
            nz = math.sqrt(max(0.0, 1.0 - r2))
            # 2d component
            nx, ny = dx, dy
            nn = math.hypot(nx, ny) or 1.0
            # blend silhouette normal with a facing-z so the center can be lit
            nx, ny = nx / nn * (1 - nz * 0.35), ny / nn * (1 - nz * 0.35)
            d = _dot_light(nx, ny, light) + 0.25 * nz
            tshade = 0.5 - 0.55 * d
            c.set(x, y, _pick(ramp, tshade))
    if core is not None and rx > 3 and ry > 3:
        # dark core slightly down-right of center (away from the light)
        c.set(int(round(cx - light[0] * rx * 0.35)),
              int(round(cy - light[1] * ry * 0.35)), core)


def shade_volume(
    c: Canvas,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    ramp: Sequence[Color],
    light=LIGHT,
) -> None:
    fill_ellipse(c, cx, cy, rx, ry, ramp, light)


def shade_limb(
    c: Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    r1: float,
    r2: float,
    ramp: Sequence[Color],
    light=LIGHT,
    muscle: float = 0.18,
    flatten: float = 0.78,
) -> None:
    """Faceted, tapered limb — not a capsule.

    The silhouette is a polygon with a muscle bulge on the lit side and a
    flattened dark side, plus slightly squared-off joints instead of round caps.
    """
    vx, vy = x2 - x1, y2 - y1
    leng = math.hypot(vx, vy) or 1.0
    ux, uy = vx / leng, vy / leng
    # perpendicular, flipped so it points toward the light when possible
    px, py = -uy, ux
    if _dot_light(px, py, light) < 0:
        px, py = -px, -py

    def rim(t, side, scale):
        # t along the spine, side = +1 lit / -1 dark
        x = x1 + ux * leng * t
        y = y1 + uy * leng * t
        r = r1 + (r2 - r1) * t
        if 0.18 < t < 0.72 and side > 0:
            r *= 1.0 + muscle * math.sin((t - 0.18) / 0.54 * math.pi)
        if side < 0:
            r *= flatten
        # flatten the very ends a little so joints aren't sausages
        if t < 0.08 or t > 0.92:
            r *= 0.92
        return (x + px * r * side, y + py * r * side)

    # build a closed faceted outline (not a smooth capsule)
    ts = (0.0, 0.08, 0.22, 0.4, 0.58, 0.75, 0.92, 1.0)
    lit = [rim(t, +1, 1) for t in ts]
    # squared end cap at b
    cap_b = [
        (x2 + ux * r2 * 0.35 + px * r2 * 0.45, y2 + uy * r2 * 0.35 + py * r2 * 0.45),
        (x2 + ux * r2 * 0.55, y2 + uy * r2 * 0.55),
        (x2 + ux * r2 * 0.35 - px * r2 * flatten * 0.45, y2 + uy * r2 * 0.35 - py * r2 * flatten * 0.45),
    ]
    dark = [rim(t, -1, 1) for t in reversed(ts)]
    cap_a = [
        (x1 - ux * r1 * 0.35 - px * r1 * flatten * 0.45, y1 - uy * r1 * 0.35 - py * r1 * flatten * 0.45),
        (x1 - ux * r1 * 0.5, y1 - uy * r1 * 0.5),
        (x1 - ux * r1 * 0.35 + px * r1 * 0.45, y1 - uy * r1 * 0.35 + py * r1 * 0.45),
    ]
    pts = lit + cap_b + dark + cap_a
    fill_poly(c, pts, ramp, light, origin=(x1, y1), axis=(x2, y2))


def line(c: Canvas, x1, y1, x2, y2, col: Color) -> None:
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        c.set(x1, y1, col)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def crease(c: Canvas, x1, y1, x2, y2, dark: Color, lite: Optional[Color] = None, light=LIGHT) -> None:
    """A 1 px fold: dark line with an optional lit pixel on the light side."""
    line(c, x1, y1, x2, y2, dark)
    if lite is None:
        return
    lx, ly = light
    # offset one pixel toward the light
    ox = -1 if lx < 0 else 1
    oy = -1 if ly < 0 else 0
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    first = True
    while True:
        if not first:
            c.set(x1 + ox, y1 + oy, lite)
        first = False
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def specular(c: Canvas, cx, cy, col: Color, n: int = 3, dx=-1, dy=-1) -> None:
    """A tight cluster of highlight pixels (metallic shine)."""
    spots = [(0, 0), (dx, 0), (0, dy), (dx, dy), (dx * 2, dy)]
    for i, (ox, oy) in enumerate(spots[:n]):
        c.set(int(round(cx + ox)), int(round(cy + oy)), col)


def stamp(c: Canvas, ox: int, oy: int, pixels: Iterable[Tuple[int, int, Color]]) -> None:
    for x, y, col in pixels:
        c.set(ox + x, oy + y, col)


def selective_outline(
    c: Canvas,
    default_dark: Color = N4,
    near_black: Color = K,
    light=LIGHT,
    skip: Optional[set] = None,
) -> None:
    """Outline opaque shapes with ramp-aware edge colors.

    Lit edges (toward the light) keep a softer outline (the pixel's own
    darker-adjacent neighbor if we can find one, else default_dark).
    Dark edges use default_dark. Near-black is used only at tight
    cavities / self-overlaps (2+ opaque neighbors of very different materials
    is approximated as: a pixel with 3+ transparent 4-neighbors in a corner
    that also faces away from the light).
    """
    w, h = c.w, c.h
    # snapshot
    src = [row[:] for row in c.px]
    lx, ly = light
    for y in range(h):
        for x in range(w):
            if src[y][x] is not None:
                continue
            # is this a transparent pixel adjacent to an opaque one?
            neigh = []
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    if ox == 0 and oy == 0:
                        continue
                    nx, ny = x + ox, y + oy
                    if 0 <= nx < w and 0 <= ny < h and src[ny][nx] is not None:
                        neigh.append((ox, oy, src[ny][nx]))
            if not neigh:
                continue
            # pick the "owning" neighbor: the one most toward the interior
            # (average of neighbor offsets)
            ax = sum(n[0] for n in neigh) / len(neigh)
            ay = sum(n[1] for n in neigh) / len(neigh)
            # edge normal pointing outward (toward this transparent pixel,
            # i.e. opposite the interior)
            nx, ny = -ax, -ay
            nn = math.hypot(nx, ny) or 1.0
            nx, ny = nx / nn, ny / nn
            d = _dot_light(nx, ny, light)
            owner = neigh[0][2]
            # lit edge: use a darker step of whatever the owner is, not black
            if d > 0.15:
                col = _softer_outline(owner, default_dark)
            elif d < -0.35 and len(neigh) >= 3:
                col = near_black
            else:
                col = default_dark
            c.set(x, y, col)


def _softer_outline(owner: Color, fallback: Color) -> Color:
    """A darker-but-same-family outline for a lit edge."""
    from .palette import G3, G4, N3, N4, S3, W3
    # map owner to a same-ramp darker outline
    table = {
        # navy
        (74, 106, 181, 255): N3,
        (40, 68, 140, 255): N4,
        (22, 40, 84, 255): N4,
        (12, 20, 44, 255): N4,
        # gold
        (255, 241, 160, 255): G3,
        (212, 160, 24, 255): G4,
        (150, 96, 16, 255): G4,
        (80, 52, 10, 255): G4,
        # skin
        (243, 201, 160, 255): S3,
        (196, 138, 88, 255): S3,
        (122, 74, 40, 255): S3,
        # white
        (255, 251, 240, 255): W3,
        (200, 192, 176, 255): W3,
        (122, 114, 104, 255): W3,
    }
    return table.get(tuple(owner), fallback)
