"""Pixel canvas and drawing primitives for Band Wars sprites.

All drawing is nearest-neighbor / integer pixel, no antialiasing.
Colors are (r, g, b, a) tuples; None is transparent.
"""

from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple

from PIL import Image

Color = Tuple[int, int, int, int]
Point = Tuple[int, int]

TRANSPARENT: Color = (0, 0, 0, 0)


def _rgba(c) -> Optional[Color]:
    if c is None:
        return None
    if len(c) == 3:
        return (int(c[0]), int(c[1]), int(c[2]), 255)
    return (int(c[0]), int(c[1]), int(c[2]), int(c[3]))


class Canvas:
    def __init__(self, w: int, h: int):
        self.w = int(w)
        self.h = int(h)
        # Row-major list of colors or None
        self.px: list[list[Optional[Color]]] = [
            [None] * self.w for _ in range(self.h)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def get(self, x: int, y: int) -> Optional[Color]:
        if not self.in_bounds(x, y):
            return None
        return self.px[y][x]

    def set(self, x: int, y: int, c) -> None:
        if c is None:
            return
        if not self.in_bounds(int(x), int(y)):
            return
        col = _rgba(c)
        if col is None or col[3] == 0:
            return
        if col[3] == 255 or self.px[y][x] is None:
            self.px[int(y)][int(x)] = col
        else:
            # simple src-over for rare translucent pixels
            dst = self.px[int(y)][int(x)]
            a = col[3] / 255.0
            inv = 1.0 - a
            self.px[int(y)][int(x)] = (
                int(col[0] * a + dst[0] * inv),
                int(col[1] * a + dst[1] * inv),
                int(col[2] * a + dst[2] * inv),
                255,
            )

    def clear(self, x: int, y: int) -> None:
        if self.in_bounds(x, y):
            self.px[y][x] = None

    def fill(self, c) -> None:
        col = _rgba(c)
        for y in range(self.h):
            for x in range(self.w):
                self.px[y][x] = col

    def blit(self, other: "Canvas", ox: int = 0, oy: int = 0, opaque: bool = True) -> None:
        for y in range(other.h):
            for x in range(other.w):
                c = other.px[y][x]
                if c is None:
                    continue
                if opaque or c[3] == 255:
                    if self.in_bounds(x + ox, y + oy):
                        self.px[y + oy][x + ox] = c
                else:
                    self.set(x + ox, y + oy, c)

    def pixels(self) -> Iterable[Tuple[int, int, Color]]:
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c is not None:
                    yield x, y, c

    def bbox(self) -> Optional[Tuple[int, int, int, int]]:
        minx, miny, maxx, maxy = self.w, self.h, -1, -1
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x] is not None:
                    if x < minx:
                        minx = x
                    if y < miny:
                        miny = y
                    if x > maxx:
                        maxx = x
                    if y > maxy:
                        maxy = y
        if maxx < 0:
            return None
        return minx, miny, maxx, maxy

    def clone(self) -> "Canvas":
        c = Canvas(self.w, self.h)
        c.px = [row[:] for row in self.px]
        return c

    def to_image(self, background=None) -> Image.Image:
        img = Image.new("RGBA", (self.w, self.h), background or (0, 0, 0, 0))
        put = img.putpixel
        for y in range(self.h):
            row = self.px[y]
            for x in range(self.w):
                c = row[x]
                if c is not None:
                    put((x, y), c)
        return img

    # --- primitives -------------------------------------------------

    def hline(self, x1: int, x2: int, y: int, c) -> None:
        if x2 < x1:
            x1, x2 = x2, x1
        for x in range(x1, x2 + 1):
            self.set(x, y, c)

    def vline(self, x: int, y1: int, y2: int, c) -> None:
        if y2 < y1:
            y1, y2 = y2, y1
        for y in range(y1, y2 + 1):
            self.set(x, y, c)

    def rect(self, x: int, y: int, w: int, h: int, c, fill: bool = True) -> None:
        if fill:
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    self.set(xx, yy, c)
        else:
            self.hline(x, x + w - 1, y, c)
            self.hline(x, x + w - 1, y + h - 1, c)
            self.vline(x, y, y + h - 1, c)
            self.vline(x + w - 1, y, y + h - 1, c)

    def line(self, x1: int, y1: int, x2: int, y2: int, c) -> None:
        x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            self.set(x1, y1, c)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def thick_line(self, x1, y1, x2, y2, r: float, c) -> None:
        """Disk-swept line (capsule axis). r is radius in pixels."""
        self.capsule(x1, y1, x2, y2, r, c)

    def disk(self, cx: float, cy: float, r: float, c) -> None:
        cx, cy, r = float(cx), float(cy), float(r)
        x0 = int(cx - r - 1)
        x1 = int(cx + r + 1)
        y0 = int(cy - r - 1)
        y1 = int(cy + r + 1)
        r2 = (r + 0.45) ** 2
        for y in range(y0, y1 + 1):
            dy = (y + 0.5) - cy
            for x in range(x0, x1 + 1):
                dx = (x + 0.5) - cx
                if dx * dx + dy * dy <= r2:
                    self.set(x, y, c)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, c, fill: bool = True) -> None:
        cx, cy, rx, ry = float(cx), float(cy), float(rx), float(ry)
        x0 = int(cx - rx - 1)
        x1 = int(cx + rx + 1)
        y0 = int(cy - ry - 1)
        y1 = int(cy + ry + 1)
        if fill:
            for y in range(y0, y1 + 1):
                dy = ((y + 0.5) - cy) / (ry + 0.45)
                for x in range(x0, x1 + 1):
                    dx = ((x + 0.5) - cx) / (rx + 0.45)
                    if dx * dx + dy * dy <= 1.0:
                        self.set(x, y, c)
        else:
            # thin ring
            for y in range(y0, y1 + 1):
                dy = ((y + 0.5) - cy) / (ry + 0.45)
                for x in range(x0, x1 + 1):
                    dx = ((x + 0.5) - cx) / (rx + 0.45)
                    d = dx * dx + dy * dy
                    if 0.72 <= d <= 1.08:
                        self.set(x, y, c)

    def capsule(self, x1, y1, x2, y2, r: float, c) -> None:
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        r = float(r)
        vx, vy = x2 - x1, y2 - y1
        leng = (vx * vx + vy * vy) ** 0.5
        pad = int(r) + 2
        xa, xb = (int(min(x1, x2)) - pad, int(max(x1, x2)) + pad)
        ya, yb = (int(min(y1, y2)) - pad, int(max(y1, y2)) + pad)
        r2 = (r + 0.45) ** 2
        if leng < 0.0001:
            self.disk(x1, y1, r, c)
            return
        inv = 1.0 / leng
        for y in range(ya, yb + 1):
            py = y + 0.5
            for x in range(xa, xb + 1):
                px = x + 0.5
                t = ((px - x1) * vx + (py - y1) * vy) * inv * inv
                if t < 0.0:
                    dx, dy = px - x1, py - y1
                elif t > 1.0:
                    dx, dy = px - x2, py - y2
                else:
                    dx, dy = px - (x1 + t * vx), py - (y1 + t * vy)
                if dx * dx + dy * dy <= r2:
                    self.set(x, y, c)

    def taper_capsule(self, x1, y1, x2, y2, r1: float, r2: float, c) -> None:
        """Capsule with different radii at each end (for tapered limbs)."""
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        r1, r2 = float(r1), float(r2)
        vx, vy = x2 - x1, y2 - y1
        leng = (vx * vx + vy * vy) ** 0.5
        rmax = max(r1, r2)
        pad = int(rmax) + 2
        xa, xb = (int(min(x1, x2)) - pad, int(max(x1, x2)) + pad)
        ya, yb = (int(min(y1, y2)) - pad, int(max(y1, y2)) + pad)
        if leng < 0.0001:
            self.disk(x1, y1, r1, c)
            return
        inv = 1.0 / leng
        for y in range(ya, yb + 1):
            py = y + 0.5
            for x in range(xa, xb + 1):
                px = x + 0.5
                t = ((px - x1) * vx + (py - y1) * vy) * inv * inv
                tclamp = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
                cx = x1 + tclamp * vx
                cy = y1 + tclamp * vy
                rr = r1 + (r2 - r1) * tclamp + 0.45
                dx, dy = px - cx, py - cy
                if dx * dx + dy * dy <= rr * rr:
                    self.set(x, y, c)

    def shade_disk(
        self,
        cx: float,
        cy: float,
        r: float,
        mid,
        light=None,
        dark=None,
        light_dir=(-0.45, -0.7),
    ) -> None:
        """Filled disk with 2-3 tone shading based on a light direction."""
        cx, cy, r = float(cx), float(cy), float(r)
        lx, ly = light_dir
        ln = (lx * lx + ly * ly) ** 0.5 or 1.0
        lx, ly = lx / ln, ly / ln
        x0, x1 = int(cx - r - 1), int(cx + r + 1)
        y0, y1 = int(cy - r - 1), int(cy + r + 1)
        r2 = (r + 0.45) ** 2
        for y in range(y0, y1 + 1):
            dy = (y + 0.5) - cy
            for x in range(x0, x1 + 1):
                dx = (x + 0.5) - cx
                d2 = dx * dx + dy * dy
                if d2 > r2:
                    continue
                # outward normal
                dist = d2 ** 0.5 or 1.0
                ndot = (dx / dist) * lx + (dy / dist) * ly
                if light is not None and ndot > 0.28 and dist < r - 0.2:
                    self.set(x, y, light)
                elif dark is not None and ndot < -0.25:
                    self.set(x, y, dark)
                else:
                    self.set(x, y, mid)

    def shade_ellipse(
        self,
        cx: float,
        cy: float,
        rx: float,
        ry: float,
        mid,
        light=None,
        dark=None,
        light_dir=(-0.45, -0.7),
    ) -> None:
        cx, cy, rx, ry = float(cx), float(cy), float(rx), float(ry)
        lx, ly = light_dir
        ln = (lx * lx + ly * ly) ** 0.5 or 1.0
        lx, ly = lx / ln, ly / ln
        x0, x1 = int(cx - rx - 1), int(cx + rx + 1)
        y0, y1 = int(cy - ry - 1), int(cy + ry + 1)
        for y in range(y0, y1 + 1):
            dy = ((y + 0.5) - cy) / (ry + 0.45)
            for x in range(x0, x1 + 1):
                dx = ((x + 0.5) - cx) / (rx + 0.45)
                d2 = dx * dx + dy * dy
                if d2 > 1.0:
                    continue
                dist = d2 ** 0.5 or 1.0
                ndot = dx * lx + dy * ly
                if light is not None and ndot > 0.28 and dist < 0.92:
                    self.set(x, y, light)
                elif dark is not None and ndot < -0.22:
                    self.set(x, y, dark)
                else:
                    self.set(x, y, mid)

    def shade_capsule(
        self,
        x1,
        y1,
        x2,
        y2,
        r: float,
        mid,
        light=None,
        dark=None,
        light_dir=(-0.45, -0.7),
    ) -> None:
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        r = float(r)
        vx, vy = x2 - x1, y2 - y1
        leng = (vx * vx + vy * vy) ** 0.5
        lx, ly = light_dir
        ln = (lx * lx + ly * ly) ** 0.5 or 1.0
        lx, ly = lx / ln, ly / ln
        pad = int(r) + 2
        xa, xb = int(min(x1, x2)) - pad, int(max(x1, x2)) + pad
        ya, yb = int(min(y1, y2)) - pad, int(max(y1, y2)) + pad
        r2 = (r + 0.45) ** 2
        if leng < 0.0001:
            self.shade_disk(x1, y1, r, mid, light, dark, light_dir)
            return
        inv2 = 1.0 / (leng * leng)
        for y in range(ya, yb + 1):
            py = y + 0.5
            for x in range(xa, xb + 1):
                px = x + 0.5
                t = ((px - x1) * vx + (py - y1) * vy) * inv2
                tclamp = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
                cx = x1 + tclamp * vx
                cy = y1 + tclamp * vy
                dx, dy = px - cx, py - cy
                d2 = dx * dx + dy * dy
                if d2 > r2:
                    continue
                dist = d2 ** 0.5 or 1.0
                ndot = (dx / dist) * lx + (dy / dist) * ly
                if light is not None and ndot > 0.30 and dist < r - 0.15:
                    self.set(x, y, light)
                elif dark is not None and ndot < -0.22:
                    self.set(x, y, dark)
                else:
                    self.set(x, y, mid)

    def shade_taper(
        self,
        x1,
        y1,
        x2,
        y2,
        r1: float,
        r2: float,
        mid,
        light=None,
        dark=None,
        light_dir=(-0.45, -0.7),
    ) -> None:
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        r1, r2 = float(r1), float(r2)
        vx, vy = x2 - x1, y2 - y1
        leng = (vx * vx + vy * vy) ** 0.5
        lx, ly = light_dir
        ln = (lx * lx + ly * ly) ** 0.5 or 1.0
        lx, ly = lx / ln, ly / ln
        rmax = max(r1, r2)
        pad = int(rmax) + 2
        xa, xb = int(min(x1, x2)) - pad, int(max(x1, x2)) + pad
        ya, yb = int(min(y1, y2)) - pad, int(max(y1, y2)) + pad
        if leng < 0.0001:
            self.shade_disk(x1, y1, r1, mid, light, dark, light_dir)
            return
        inv2 = 1.0 / (leng * leng)
        for y in range(ya, yb + 1):
            py = y + 0.5
            for x in range(xa, xb + 1):
                px = x + 0.5
                t = ((px - x1) * vx + (py - y1) * vy) * inv2
                tclamp = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
                cx = x1 + tclamp * vx
                cy = y1 + tclamp * vy
                rr = r1 + (r2 - r1) * tclamp
                dx, dy = px - cx, py - cy
                d2 = dx * dx + dy * dy
                if d2 > (rr + 0.45) ** 2:
                    continue
                dist = d2 ** 0.5 or 1.0
                ndot = (dx / dist) * lx + (dy / dist) * ly
                if light is not None and ndot > 0.30 and dist < rr - 0.15:
                    self.set(x, y, light)
                elif dark is not None and ndot < -0.22:
                    self.set(x, y, dark)
                else:
                    self.set(x, y, mid)


def auto_outline(
    src: Canvas,
    outline_color,
    connectivity: int = 8,
    only_silhouette: bool = False,
) -> Canvas:
    """Return a new canvas with a 1px dark outline around opaque pixels."""
    out = src.clone()
    oc = _rgba(outline_color)
    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if connectivity == 8:
        neigh += [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    to_paint = []
    for y in range(src.h):
        for x in range(src.w):
            if src.px[y][x] is not None:
                continue
            hit = False
            for dx, dy in neigh:
                nx, ny = x + dx, y + dy
                if 0 <= nx < src.w and 0 <= ny < src.h and src.px[ny][nx] is not None:
                    hit = True
                    break
            if hit:
                to_paint.append((x, y))
    for x, y in to_paint:
        out.px[y][x] = oc
    return out


def composite(*layers: Canvas, w: int = None, h: int = None) -> Canvas:
    if not layers and (w is None or h is None):
        raise ValueError("composite needs layers or a size")
    if w is None:
        w = layers[0].w
    if h is None:
        h = layers[0].h
    out = Canvas(w, h)
    for layer in layers:
        out.blit(layer)
    return out


def stamp(dest: Canvas, ox: int, oy: int, rows: Sequence[str], mapping: dict) -> None:
    """Stamp a string-art pixel map. 'mapping' maps characters to colors.
    Spaces and '.' are transparent unless mapped.
    """
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in (" ",) and ch not in mapping:
                continue
            if ch == "." and "." not in mapping:
                continue
            c = mapping.get(ch)
            if c is not None:
                dest.set(ox + i, oy + j, c)


def nearest_scale(img: Image.Image, factor: int) -> Image.Image:
    w, h = img.size
    return img.resize((w * factor, h * factor), Image.Resampling.NEAREST)


def unique_colors(img: Image.Image) -> list:
    colors = set()
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    for r, g, b, a in img.getdata():
        if a == 0:
            continue
        colors.add((r, g, b, a))
    return sorted(colors)
