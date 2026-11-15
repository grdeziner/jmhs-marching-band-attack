#!/usr/bin/env python3
"""Band Wars — locker-room stage generator (SNES / SF2 Turbo 16-bit look).

640x360 far, 960x360 mid/anim (origin x=-160), 1120x360 near (origin x=-240).
Seeded RNG, hand-pixel, no anti-aliasing, hard alpha only (0 or 255).
Richer-than-32 16-bit palette, ordered Bayer dither, fluorescent lighting.
JMHS navy/gold/white uniforms (verbatim fighter swatches).
Fighters' feet at y=320; floor band y=300..360 stays uncluttered.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

SEED = 19910320
DIR = Path(__file__).resolve().parent
W_FAR, W_MID, W_NEAR, H = 640, 960, 1120, 360
FLOOR_TOP = 300
FLICKER_X, FLICKER_Y, FLICKER_W = 452, 4, 100

# Official JMHS school colors — verbatim from art/characters/tools/pxart/palette.py
NAVY      = (0x17, 0x30, 0x5F)
NAVY_DK   = (0x0C, 0x17, 0x34)
NAVY_LT   = (0x3A, 0x5A, 0x9C)
GOLD      = (0xD4, 0xA0, 0x17)
GOLD_DK   = (0x7A, 0x54, 0x10)
GOLD_LT   = (0xF5, 0xDE, 0x6A)
WHITE     = (0xF6, 0xF2, 0xEA)
WHITE_SH  = (0xB9, 0xB3, 0xA6)
WHITE_DK  = (0x8B, 0x85, 0x78)
SKIN_DK   = (0x8E, 0x4E, 0x2C)
SKIN      = (0xE0, 0x9A, 0x68)
SKIN_LT   = (0xF5, 0xC4, 0x9A)
HAIR      = (0x1A, 0x12, 0x10)
HAIR_BR   = (0x3A, 0x22, 0x18)
HAIR_BL   = (0xC4, 0xA0, 0x56)
SHOE      = (0x14, 0x14, 0x18)

# Scene ramps (16-bit, many shades)
CEIL_DK   = (48, 54, 44)
CEIL      = (86, 94, 78)
CEIL_MD   = (102, 110, 92)
CEIL_LT   = (126, 134, 114)
CEIL_LIT  = (168, 176, 148)
CEIL_GLOW = (210, 220, 170)
WALL_COR  = (74, 68, 54)
WALL_DK   = (96, 90, 74)
WALL_SH   = (128, 120, 98)
WALL      = (166, 158, 134)
WALL_MD   = (184, 176, 150)
WALL_HI   = (202, 194, 166)
WALL_LIT  = (214, 210, 176)
WALL_FLU  = (200, 210, 168)
FLUOR     = (236, 240, 210)
FLUOR_HI  = (255, 255, 240)
FLUOR_DIM = (150, 158, 120)
FLUOR_OFF = (110, 116, 100)
FLUOR_G   = (186, 200, 140)
LOK_SH    = (22, 34, 18)
LOK_DK    = (40, 56, 30)
LOK       = (68, 90, 50)
LOK_MD    = (86, 110, 64)
LOK_LT    = (112, 136, 82)
LOK_HI    = (148, 170, 112)
LOK_SPEC  = (198, 210, 168)
METAL     = (168, 172, 150)
METAL_DK  = (110, 114, 100)
METAL_HI  = (210, 214, 200)
RUST      = (126, 74, 42)
WOOD_DK   = (90, 60, 32)
WOOD      = (148, 102, 56)
WOOD_MD   = (170, 122, 70)
WOOD_LT   = (196, 150, 92)
TILE_DK   = (132, 116, 86)
TILE      = (176, 158, 122)
TILE_MD   = (198, 180, 142)
TILE_HI   = (220, 204, 168)
TILE_LIT  = (230, 222, 180)
GROUT     = (108, 96, 74)
GROUT_DK  = (88, 78, 60)
CASE      = (36, 34, 38)
CASE_MD   = (56, 54, 60)
CASE_HI   = (84, 82, 90)
INK       = (28, 28, 32)
RED       = (168, 36, 38)
RED_DK    = (104, 20, 24)

BRASS, BRASS_DK = GOLD, GOLD_DK

# Fixture positions on mid (also used by lighting + anim)
FIXTURES = [(80, 3, 90), (260, 3, 90), (FLICKER_X, FLICKER_Y, FLICKER_W), (680, 3, 90), (850, 3, 80)]

BAYER4 = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5],
]


def bayer(x, y):
    return BAYER4[y & 3][x & 3]


class Pix:
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        if bg is None:
            self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        else:
            c = bg if len(bg) == 4 else bg + (255,)
            self.im = Image.new("RGBA", (w, h), c)
        self.px = self.im.load()
        self.guard = False
        self._protect = []  # (x0, y0, x1, y1) glyph/label boxes
        self._labels = []

    def reserve(self, x, y, w, h):
        self._protect.append((x, y, x + w, y + h))
        self.guard = True

    def is_reserved(self, x, y):
        for x0, y0, x1, y1 in self._protect:
            if x0 <= x < x1 and y0 <= y < y1:
                return True
        return False

    def p(self, x, y, c):
        if self.guard and self.is_reserved(x, y):
            return
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = c if len(c) == 4 else c + (255,)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[x, y]
        return (0, 0, 0, 0)

    def opaque(self, x, y):
        return self.get(x, y)[3] >= 128

    def rect(self, x, y, w, h, c):
        for j in range(max(0, y), min(self.h, y + h)):
            for i in range(max(0, x), min(self.w, x + w)):
                self.px[i, j] = c if len(c) == 4 else c + (255,)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def outline(self, x, y, w, h, c):
        self.hline(x, y, w, c)
        self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c)

    def bevel(self, x, y, w, h, mid, hi, sh, fill=True):
        if fill:
            self.rect(x, y, w, h, mid)
        self.hline(x, y, w - 1, hi)
        self.vline(x, y, h - 1, hi)
        self.hline(x, y + h - 1, w, sh)
        self.vline(x + w - 1, y, h, sh)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx - dy
        while True:
            self.p(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        rr = r * r
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                d = x * x + y * y
                if fill and d <= rr:
                    self.p(cx + x, cy + y, c)
                elif not fill and abs(d - rr) <= max(r, 1):
                    self.p(cx + x, cy + y, c)

    def dith(self, x, y, w, h, c1, c2, mode="checker"):
        for j in range(max(0, y), min(self.h, y + h)):
            for i in range(max(0, x), min(self.w, x + w)):
                if mode == "checker":
                    use = ((i + j) & 1) == 0
                elif mode == "h":
                    use = (j & 1) == 0
                elif mode == "v":
                    use = (i & 1) == 0
                elif mode == "bayer":
                    use = bayer(i, j) < 8
                else:
                    use = True
                self.p(i, j, c1 if use else c2)

    def vgrad(self, x, y, w, h, colors, transition=5):
        """Solid shade bands with a narrow Bayer transition at each boundary."""
        n = max(1, len(colors) - 1)
        band = max(1.0, h / n)
        for j in range(max(0, y), min(self.h, y + h)):
            rel = j - y
            i0 = min(n, int(rel / band))
            c0 = colors[i0]
            c1 = colors[min(i0 + 1, n)]
            into = rel - i0 * band
            if i0 < n and into >= band - transition:
                thresh = int((into - (band - transition)) / max(1, transition) * 16)
                use_c1 = True
            else:
                thresh = -1
                use_c1 = False
            for i in range(max(0, x), min(self.w, x + w)):
                if thresh >= 0 and bayer(i, j) < thresh:
                    self.p(i, j, c1)
                else:
                    self.p(i, j, c0)

    def hgrad(self, x, y, w, h, colors):
        n = max(1, len(colors) - 1)
        for i in range(max(0, x), min(self.w, x + w)):
            t = ((i - x) * n) / max(1, w - 1)
            i0 = int(t)
            frac = t - i0
            c0 = colors[min(i0, n)]
            c1 = colors[min(i0 + 1, n)]
            thresh = int(frac * 16)
            for j in range(max(0, y), min(self.h, y + h)):
                self.p(i, j, c1 if bayer(i, j) < thresh else c0)

    def tint(self, x, y, w, h, toward, amount16, only_opaque=True):
        """Dithered tint toward `toward` (amount 0-16) on existing pixels."""
        for j in range(max(0, y), min(self.h, y + h)):
            for i in range(max(0, x), min(self.w, x + w)):
                c = self.px[i, j]
                if only_opaque and (len(c) > 3 and c[3] < 128):
                    continue
                if bayer(i, j) < amount16:
                    self.p(i, j, toward)


def mix(c0, c1):
    return ((c0[0] + c1[0]) // 2, (c0[1] + c1[1]) // 2, (c0[2] + c1[2]) // 2)


def light_pool(pix, cx, cy, rx, ry, tint, max_amt=12, y0=None, y1=None, x0=None, x1=None):
    """Elliptical dithered glow: density falls off with distance."""
    y0 = 0 if y0 is None else y0
    y1 = pix.h if y1 is None else y1
    x0 = 0 if x0 is None else x0
    x1 = pix.w if x1 is None else x1
    for y in range(max(y0, cy - ry), min(y1, cy + ry + 1)):
        for x in range(max(x0, cx - rx), min(x1, cx + rx + 1)):
            c = pix.get(x, y)
            if c[3] < 128:
                continue
            dx = (x - cx) / max(1, rx)
            dy = (y - cy) / max(1, ry)
            d = dx * dx + dy * dy
            if d > 1:
                continue
            amt = int((1 - d) * max_amt)
            if bayer(x, y) < amt:
                pix.p(x, y, tint)


def darken_falloff(pix, x, y, w, h, toward, strength=8):
    """Darker toward the bottom and sides of a wall band, Bayer-dithered."""
    for j in range(max(0, y), min(pix.h, y + h)):
        fy = (j - y) / max(1, h - 1)
        for i in range(max(0, x), min(pix.w, x + w)):
            c = pix.get(i, j)
            if c[3] < 128:
                continue
            # extra darkness near left/right of this band
            edge = min(i - x, (x + w - 1) - i) / max(1, w / 2)
            edge_f = 0 if edge > 0.35 else (0.35 - edge) / 0.35
            amt = int(strength * fy + 6 * edge_f)
            if bayer(i, j) < amt:
                pix.p(i, j, toward)


FONT = {
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "B": ["11110","10001","10001","11110","10001","10001","11110"],
    "C": ["01110","10001","10000","10000","10000","10001","01110"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "F": ["11111","10000","10000","11110","10000","10000","10000"],
    "G": ["01110","10001","10000","10111","10001","10001","01110"],
    "H": ["10001","10001","10001","11111","10001","10001","10001"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "J": ["00111","00010","00010","00010","00010","10010","01100"],
    "K": ["10001","10010","10100","11000","10100","10010","10001"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "M": ["10001","11011","10101","10101","10001","10001","10001"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "Q": ["01110","10001","10001","10001","10101","10010","01101"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","10101","01010"],
    "X": ["10001","10001","01010","00100","01010","10001","10001"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "Z": ["11111","00001","00010","00100","01000","10000","11111"],
    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["01110","10001","00001","00110","00001","10001","01110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","11110","00001","00001","10001","01110"],
    "6": ["01110","10001","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","00100","00100","00100"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","10001","01110"],
    " ": ["00000","00000","00000","00000","00000","00000","00000"],
    "!": ["00100","00100","00100","00100","00100","00000","00100"],
    "?": ["01110","10001","00001","00010","00100","00000","00100"],
    ".": ["00000","00000","00000","00000","00000","00000","00100"],
    ":": ["00000","00100","00100","00000","00100","00100","00000"],
    "-": ["00000","00000","00000","11111","00000","00000","00000"],
    "'": ["00100","00100","01000","00000","00000","00000","00000"],
    "/": ["00001","00010","00010","00100","01000","01000","10000"],
    "+": ["00000","00100","00100","11111","00100","00100","00000"],
}

FONT3 = {
    " ": ["000","000","000","000","000"],
    "0": ["010","101","101","101","010"],
    "1": ["010","110","010","010","111"],
    "2": ["110","001","010","100","111"],
    "3": ["110","001","010","001","110"],
    "4": ["101","101","111","001","001"],
    "5": ["111","100","110","001","110"],
    "6": ["010","100","110","101","010"],
    "7": ["111","001","010","010","010"],
    "8": ["010","101","010","101","010"],
    "9": ["010","101","011","001","010"],
    "A": ["010","101","111","101","101"],
    "B": ["110","101","110","101","110"],
    "C": ["011","100","100","100","011"],
    "D": ["110","101","101","101","110"],
    "E": ["111","100","110","100","111"],
    "F": ["111","100","110","100","100"],
    "G": ["011","100","101","101","011"],
    "H": ["101","101","111","101","101"],
    "I": ["111","010","010","010","111"],
    "J": ["001","001","001","101","010"],
    "K": ["101","101","110","101","101"],
    "L": ["100","100","100","100","111"],
    "M": ["101","111","101","101","101"],
    "N": ["101","111","101","101","101"],
    "O": ["010","101","101","101","010"],
    "P": ["110","101","110","100","100"],
    "R": ["110","101","110","101","101"],
    "S": ["011","100","010","001","110"],
    "T": ["111","010","010","010","010"],
    "U": ["101","101","101","101","011"],
    "W": ["101","101","111","111","101"],
    "X": ["101","101","010","101","101"],
    "Y": ["101","101","010","010","010"],
    "Z": ["111","001","010","100","111"],
    "!": ["010","010","010","000","010"],
    ".": ["000","000","000","000","010"],
    "-": ["000","000","111","000","000"],
    ":": ["000","010","000","010","000"],
    "/": ["001","001","010","100","100"],
}


def text_metrics(s, scale=1, font="5"):
    adv = 6 if font != "3" else 4
    gw = 5 if font != "3" else 3
    gh = 7 if font != "3" else 5
    n = len(s)
    w = 0 if n == 0 else ((n - 1) * adv + gw) * scale
    return w, gh * scale


def draw_glyphs(pix, x, y, s, color, scale=1, shadow=None, font="5"):
    """Immediate crisp glyph stamps. Bypasses reserve guard."""
    glyphs = FONT if font != "3" else FONT3
    adv = 6 if font != "3" else 4
    prev = pix.guard
    pix.guard = False
    cx = x
    for ch in s.upper():
        glyph = glyphs.get(ch, glyphs.get("?") or glyphs.get(" "))
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit != "1":
                    continue
                for dy in range(scale):
                    for dx in range(scale):
                        px = cx + col * scale + dx
                        py = y + row * scale + dy
                        if shadow:
                            if 0 <= px + scale < pix.w and 0 <= py + scale < pix.h:
                                pix.px[px + scale, py + scale] = shadow if len(shadow) == 4 else shadow + (255,)
                        if 0 <= px < pix.w and 0 <= py < pix.h:
                            pix.px[px, py] = color if len(color) == 4 else color + (255,)
        cx += adv * scale
    pix.guard = prev
    return cx


def text(pix, x, y, s, color, scale=1, shadow=None, font="5", bg=None, bg_rect=None):
    """Queue lettering, reserve its box from dither/noise/highlight, optional clean bg.

    Glyphs are stamped later by flush_labels() so text is always drawn last and crisp.
    """
    w, h = text_metrics(s, scale, font)
    if shadow:
        w += scale
        h += scale
    if bg_rect is None:
        bx, by, bw, bh = x - 1, y - 1, w + 2, h + 2
    else:
        bx, by, bw, bh = bg_rect
    if bg is not None:
        pix.rect(bx, by, bw, bh, bg)
    pix.reserve(bx, by, bw, bh)
    pix._labels.append((x, y, s, color, scale, shadow, font, bg, (bx, by, bw, bh)))
    return x + w


def flush_labels(pix):
    """Fill clean backgrounds, then stamp every queued string. Call last on a layer."""
    pix.guard = False
    for x, y, s, color, scale, shadow, font, bg, rect in pix._labels:
        if bg is not None:
            bx, by, bw, bh = rect
            pix.rect(bx, by, bw, bh, bg)
        draw_glyphs(pix, x, y, s, color, scale, shadow, font)
    pix._labels.clear()
    pix.guard = bool(pix._protect)


def crunch(img, opaque=False):
    """Hard-alpha only; do not quantize — 16-bit palettes stay intact."""
    if opaque:
        return img.convert("RGB")
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda v: 255 if v >= 128 else 0)
    return Image.merge("RGBA", (r, g, b, a))



# ---------------------------------------------------------------------------
# Props
# ---------------------------------------------------------------------------

def draw_shako(pix, x, y, plume=True, small=False):
    """Navy shako, gold badge, gold/white plume — matches the fighter kit."""
    if small:
        pix.bevel(x, y + 2, 8, 8, NAVY, NAVY_LT, NAVY_DK)
        pix.rect(x + 1, y + 3, 6, 2, NAVY_LT)
        pix.rect(x, y + 9, 8, 2, SHOE)
        pix.hline(x, y + 8, 8, GOLD)
        pix.rect(x + 2, y + 4, 3, 3, GOLD)
        pix.p(x + 3, y + 5, GOLD_LT)
        if plume:
            pix.vline(x + 3, y - 4, 6, GOLD)
            pix.vline(x + 4, y - 5, 7, GOLD_LT)
            pix.p(x + 4, y - 5, WHITE)
        return
    pix.bevel(x, y + 3, 12, 12, NAVY, NAVY_LT, NAVY_DK)
    pix.rect(x + 1, y + 4, 10, 3, NAVY_LT)
    pix.hline(x + 2, y + 5, 8, NAVY)
    pix.hline(x, y + 13, 12, GOLD)
    pix.rect(x, y + 14, 13, 3, SHOE)
    pix.rect(x + 1, y + 14, 11, 1, METAL_DK)
    pix.rect(x + 4, y + 6, 4, 5, GOLD)
    pix.p(x + 5, y + 7, GOLD_DK)
    pix.p(x + 6, y + 8, GOLD_LT)
    pix.p(x + 7, y + 7, WHITE)
    pix.rect(x + 5, y + 1, 3, 3, SHOE)
    if plume:
        pix.vline(x + 5, y - 7, 9, GOLD)
        pix.vline(x + 6, y - 8, 11, GOLD_LT)
        pix.vline(x + 7, y - 7, 9, GOLD_DK)
        pix.p(x + 6, y - 8, WHITE)
        pix.p(x + 5, y - 6, WHITE)


def draw_jacket(pix, x, y, w=16, h=22):
    pix.rect(x + w // 2 - 1, y - 3, 2, 4, METAL)
    pix.hline(x + 1, y, w - 2, METAL_HI)
    pix.vgrad(x, y + 1, w, h, [NAVY_DK, NAVY, NAVY_LT])
    pix.vline(x, y + 1, h, NAVY_DK)
    pix.vline(x + w - 1, y + 1, h, NAVY_DK)
    pix.hline(x, y + h, w, NAVY_DK)
    pix.vline(x + 2, y + 3, h - 5, GOLD)
    pix.vline(x + w - 3, y + 3, h - 5, GOLD)
    pix.vline(x + w // 2, y + 2, h - 4, WHITE)
    for by in range(y + 5, y + h - 2, 4):
        pix.p(x + w // 2 + 1, by, GOLD)
        pix.p(x + w // 2 - 1, by, GOLD_DK)
    pix.hline(x, y + 1, w, NAVY_DK)
    pix.rect(x + 1, y + 2, w - 2, 2, NAVY_LT)
    pix.p(x + 1, y + 3, GOLD_LT)


def draw_pants_fold(pix, x, y):
    pix.rect(x, y, 12, 6, WHITE)
    pix.hline(x, y, 12, WHITE_SH)
    pix.hline(x, y + 5, 12, WHITE_DK)
    pix.vline(x + 6, y, 6, WHITE_SH)
    pix.vline(x + 2, y + 1, 4, GOLD_DK)


def draw_locker(pix, x, y, w, h, rng, state="closed", number="12"):
    # Cabinet body with vertical metal gradient (lit from above)
    pix.vgrad(x, y, w, h, [LOK_LT, LOK, LOK_DK, LOK_SH])
    pix.hline(x, y, w, LOK_HI)
    pix.vline(x, y, h, LOK_LT)
    pix.vline(x + w - 1, y, h, LOK_SH)
    pix.hline(x, y + h - 1, w, LOK_SH)
    # rust flecks near the feet
    for _ in range(rng.randint(0, 4)):
        rx = x + rng.randint(1, max(2, w - 3))
        ry = y + h - rng.randint(2, 12)
        pix.p(rx, ry, RUST)
        if rng.random() < 0.5:
            pix.p(rx + 1, ry, RUST)

    if state == "closed":
        pix.vgrad(x + 1, y + 1, w - 2, h - 2, [LOK_HI, LOK_LT, LOK, LOK_DK])
        pix.hline(x + 1, y + 1, w - 2, LOK_SPEC)
        pix.vline(x + 1, y + 1, h - 2, LOK_HI)
        pix.vline(x + 2, y + 2, 22, LOK_SPEC)
        pix.p(x + 3, y + 3, LOK_SPEC)
        # stamped recessed panel
        pix.outline(x + 4, y + 16, w - 8, h - 30, LOK_DK)
        pix.p(x + 4, y + 16, LOK_HI)
        pix.hline(x + 5, y + 17, w - 10, LOK_SH)
        # top louvers with inner shadow
        for ly in range(y + 4, y + 14, 2):
            pix.hline(x + 5, ly, w - 10, LOK_DK)
            pix.hline(x + 5, ly + 1, w - 10, LOK_SH)
        for ly in range(y + h - 12, y + h - 5, 2):
            pix.hline(x + 5, ly, w - 10, LOK_DK)
        # number plate
        digits = number[-2:] if len(number) >= 2 else number.rjust(2, "0")
        plx, ply = x + w // 2 - 6, y + 18
        pix.bevel(plx, ply, 12, 9, METAL, METAL_HI, LOK_SH)
        pix.rect(plx + 1, ply + 1, 10, 7, WHITE_SH)
        text(pix, plx + 2, ply + 2, digits, INK, font="3", bg=WHITE_SH, bg_rect=(plx + 1, ply + 1, 10, 7))
        # handle + specular
        hx, hy = x + w - 6, y + h // 2 - 2
        pix.rect(hx, hy, 3, 8, GOLD_DK)
        pix.rect(hx, hy, 2, 7, GOLD)
        pix.p(hx + 1, hy + 1, GOLD_LT)
        pix.p(hx, hy, WHITE)
        if rng.random() < 0.45:
            pix.rect(hx - 5, hy + 1, 5, 6, CASE)
            pix.rect(hx - 4, hy + 2, 3, 4, METAL)
            pix.p(hx - 3, hy + 3, INK)
        if rng.random() < 0.55:
            sx = x + rng.randint(6, w - 8)
            sy = y + rng.randint(28, h - 18)
            pix.line(sx, sy, sx + rng.randint(3, 8), sy + rng.randint(-2, 2), LOK_SH)
        if rng.random() < 0.3:
            sx = x + rng.randint(6, max(7, w - 12))
            sy = y + rng.randint(36, h - 32)
            col = rng.choice([NAVY, WHITE, GOLD, WALL_HI])
            pix.rect(sx, sy, 6, 4, col)
            pix.outline(sx, sy, 6, 4, INK)
        # a couple of specular dashes
        if rng.random() < 0.7:
            pix.p(x + 3, y + 20, LOK_SPEC)
            pix.p(x + 4, y + 22, LOK_SPEC)
        return

    # Open / ajar: deep interior with shelf and hanging kit
    pix.rect(x + 2, y + 2, w - 4, h - 4, CASE)
    pix.vgrad(x + 3, y + 3, w - 6, h - 6, [CASE, CASE, CASE_MD])
    pix.vline(x + 2, y + 2, h - 4, INK)
    pix.hline(x + 2, y + 2, w - 4, INK)
    sy = y + 28
    pix.rect(x + 3, sy, w - 6, 3, CASE_HI)
    pix.hline(x + 3, sy, w - 6, METAL)
    pix.hline(x + 3, sy + 3, w - 6, INK)
    draw_jacket(pix, x + 5, y + 38, w=max(12, w - 8), h=min(34, h - 52))
    if state == "open" or rng.random() < 0.7:
        draw_shako(pix, x + w // 2 - 6, y + 8, plume=True)
    else:
        draw_pants_fold(pix, x + 5, y + 10)
    pix.rect(x + 5, y + h - 16, 8, 5, SHOE)
    pix.rect(x + 14, y + h - 16, 8, 5, SHOE)
    pix.p(x + 6, y + h - 15, METAL_DK)
    door_w = 7 if state == "ajar" else 11
    dx = x + w - 1
    pix.vgrad(dx, y + 1, door_w, h - 2, [LOK_HI, LOK_LT, LOK, LOK_DK])
    pix.vline(dx, y + 1, h - 2, LOK_SH)
    pix.hline(dx, y + 1, door_w, LOK_SPEC)
    pix.outline(dx + 2, y + 16, max(3, door_w - 4), h - 32, LOK_DK)
    for ly in range(y + 4, y + 12, 2):
        pix.hline(dx + 1, ly, max(1, door_w - 3), LOK_DK)
    pix.rect(dx + door_w - 3, y + h // 2 - 2, 2, 8, GOLD)
    pix.p(dx + door_w - 3, y + h // 2 - 1, GOLD_LT)


def draw_bench(pix, x, y, w, slats=4):
    pix.vgrad(x, y, w, 7, [WOOD_LT, WOOD, WOOD_DK])
    pix.hline(x, y, w, WOOD_LT)
    pix.hline(x, y + 6, w, WOOD_DK)
    gap = w // slats
    for i in range(1, slats):
        pix.vline(x + i * gap, y + 1, 5, WOOD_DK)
        pix.vline(x + i * gap + 1, y + 1, 4, WOOD_MD)
    for lx in (x + 6, x + w - 10):
        pix.rect(lx, y + 7, 5, FLOOR_TOP - (y + 7), CASE)
        pix.rect(lx + 1, y + 7, 2, FLOOR_TOP - (y + 7), CASE_HI)
        pix.rect(lx - 2, FLOOR_TOP - 3, 9, 3, CASE)
        pix.p(lx, y + 8, METAL_HI)
    pix.hline(x + 2, FLOOR_TOP, w - 4, GROUT_DK)


def draw_case(pix, x, y, w, h, kind="rect"):
    pix.vgrad(x, y, w, h, [CASE_HI, CASE_MD, CASE])
    pix.outline(x, y, w, h, INK)
    pix.hline(x + 1, y + 1, w - 2, CASE_HI)
    pix.vline(x + 1, y + 1, h - 2, CASE_MD)
    for lx in (x + 4, x + w // 2 - 2, x + w - 8):
        if lx > x and lx + 5 < x + w:
            pix.rect(lx, y + h // 2 - 2, 5, 4, GOLD_DK)
            pix.rect(lx + 1, y + h // 2 - 1, 3, 2, GOLD)
            pix.p(lx + 2, y + h // 2, GOLD_LT)
    if kind == "snare":
        pix.outline(x + 3, y + 3, w - 6, h - 6, CASE_HI)
        pix.circle(x + w // 2, y + h // 2, 4, METAL)
        pix.circle(x + w // 2, y + h // 2, 2, GOLD)
        pix.p(x + w // 2, y + h // 2, GOLD_LT)
    elif kind == "trombone":
        pix.rect(x + 4, y + 3, w - 8, 3, CASE_HI)
        pix.rect(x + w - 12, y + 2, 8, h - 4, CASE_MD)
    elif kind == "tuba":
        pix.circle(x + w // 2, y + h // 2, min(w, h) // 3, CASE_HI)
        pix.circle(x + w // 2, y + h // 2, min(w, h) // 3 - 2, CASE)
        pix.p(x + w // 2 - 4, y + h // 2 - 4, CASE_HI)
    pix.rect(x + w // 2 - 4, y - 3, 8, 3, CASE_HI)
    pix.hline(x + w // 2 - 3, y - 3, 6, METAL)
    pix.rect(x + 3, y + h - 8, 9, 4, WHITE_SH)
    pix.rect(x + 4, y + h - 7, 7, 2, WHITE)


def draw_sousaphone(pix, x, y):
    # richer gold ramp + specular
    pix.circle(x + 28, y + 28, 26, GOLD_DK)
    pix.circle(x + 28, y + 28, 24, GOLD)
    pix.circle(x + 28, y + 28, 18, GOLD_DK)
    pix.circle(x + 28, y + 26, 13, INK)
    pix.circle(x + 28, y + 26, 11, CASE)
    for a in range(-10, 8):
        pix.p(x + 28 + a, y + 16, GOLD)
    pix.p(x + 18, y + 20, GOLD_LT)
    pix.p(x + 16, y + 22, WHITE)
    pix.p(x + 36, y + 18, GOLD_LT)
    pix.circle(x + 30, y + 70, 16, GOLD_DK)
    pix.circle(x + 30, y + 70, 14, GOLD)
    pix.circle(x + 30, y + 70, 9, GOLD_DK)
    pix.circle(x + 30, y + 70, 7, WALL_SH)
    pix.p(x + 22, y + 64, GOLD_LT)
    pix.circle(x + 22, y + 78, 12, GOLD)
    pix.circle(x + 22, y + 78, 8, GOLD_DK)
    pix.circle(x + 22, y + 78, 5, WALL)
    pix.rect(x + 50, y + 40, 5, 50, GOLD)
    pix.rect(x + 51, y + 40, 2, 50, GOLD_DK)
    pix.p(x + 50, y + 44, GOLD_LT)
    pix.rect(x + 8, y + 50, 4, 36, GOLD_DK)
    pix.rect(x + 9, y + 50, 2, 36, GOLD)
    pix.rect(x + 52, y + 86, 16, 3, GOLD)
    pix.rect(x + 66, y + 84, 5, 7, GOLD_DK)
    pix.rect(x + 67, y + 85, 3, 5, WHITE_SH)
    pix.rect(x + 34, y + 88, 16, 10, GOLD_DK)
    for i in range(3):
        pix.rect(x + 36 + i * 5, y + 84, 3, 6, METAL)
        pix.p(x + 37 + i * 5, y + 84, METAL_HI)
    pix.rect(x + 18, 292, 20, 8, CASE)
    pix.rect(x + 16, 297, 24, 3, CASE_HI)
    pix.hline(x + 14, 299, 28, INK)


def draw_whiteboard(pix, x, y, w=130, h=96):
    pix.bevel(x, y, w, h, CASE_HI, METAL_HI, INK)
    pix.rect(x + 3, y + 3, w - 6, h - 14, WHITE)
    rng = random.Random(44)
    fx, fy, fw, fh = x + 10, y + 22, w - 20, h - 44
    for _ in range(18):
        pix.p(x + rng.randint(4, w - 6), y + rng.randint(fy + 2, fy + fh - 3), WHITE_SH)
    pix.outline(fx, fy, fw, fh, INK)
    for i in range(1, 8):
        hx = fx + i * fw // 8
        pix.vline(hx, fy + 3, 4, WHITE_DK)
        pix.vline(hx, fy + fh - 7, 4, WHITE_DK)
        if i in (2, 4, 6):
            pix.vline(hx, fy + fh // 2 - 3, 6, WHITE_DK)
    pix.vline(fx + fw // 2, fy, fh, WHITE_DK)
    dots = []
    for i in range(13):
        dots.append((fx + 8 + i * (fw - 16) // 12, fy + fh - 10))
    for i in range(9):
        t = i / 8
        dx = int((fw - 24) * t) + 8
        dy = int(18 * (1 - (2 * t - 1) ** 2))
        dots.append((fx + dx, fy + 14 + (fh // 2 - dy)))
    for i in range(7):
        dots.append((fx + 16 + i * 12, fy + fh // 2 + 8))
    for dx, dy in dots:
        pix.p(dx, dy, INK)
        pix.p(dx + 1, dy, INK)
        pix.p(dx, dy + 1, NAVY)
    # Keep the whole writing surface out of locker-green highlight pools,
    # and give the title / footer bars a continuous clean white field.
    pix.rect(x + 4, y + 4, w - 8, 11, WHITE)
    pix.reserve(x + 3, y + 3, w - 6, h - 14)
    text(pix, x + 8, y + 6, "GAME NIGHT", NAVY, 1, bg=WHITE, bg_rect=(x + 6, y + 4, 64, 11))
    text(pix, x + w - 48, y + 6, "SET 14", INK, 1, bg=WHITE, bg_rect=(x + w - 50, y + 4, 44, 11))
    text(pix, x + 8, y + h - 21, "WARMUP 6:30", INK, font="3", bg=WHITE, bg_rect=(x + 6, y + h - 22, 48, 7))
    text(pix, x + w - 44, y + h - 21, "GO BAND!", NAVY, font="3", bg=WHITE, bg_rect=(x + w - 46, y + h - 22, 38, 7))
    pix.rect(x + 2, y + h - 12, w - 4, 9, METAL)
    pix.hline(x + 2, y + h - 12, w - 4, METAL_HI)
    pix.rect(x + 8, y + h - 10, 3, 7, INK)
    pix.rect(x + 13, y + h - 10, 3, 7, RED)
    pix.rect(x + 18, y + h - 10, 3, 7, LOK)
    pix.rect(x + 23, y + h - 10, 3, 7, GOLD_DK)
    pix.rect(x + w - 30, y + h - 10, 18, 6, CASE)
    pix.rect(x + w - 29, y + h - 9, 16, 4, WHITE_SH)


def draw_uniform_rack(pix, x, y, w=90):
    pix.rect(x + 4, y, 3, FLOOR_TOP - y, METAL_DK)
    pix.rect(x + w - 7, y, 3, FLOOR_TOP - y, METAL_DK)
    pix.rect(x + 5, y, 1, FLOOR_TOP - y, METAL_HI)
    pix.rect(x + 2, y, w - 4, 3, METAL)
    pix.hline(x + 2, y, w - 4, METAL_HI)
    for wx in (x + 3, x + w - 10):
        pix.circle(wx + 3, FLOOR_TOP - 4, 4, CASE)
        pix.circle(wx + 3, FLOOR_TOP - 4, 2, CASE_HI)
        pix.p(wx + 4, FLOOR_TOP - 5, METAL_HI)
    n = 6
    for i in range(n):
        ux = x + 8 + i * ((w - 20) // n)
        draw_jacket(pix, ux, y + 8, w=12, h=26 + (i % 3) * 2)
        ph = 18
        pix.rect(ux + 1, y + 36, 10, ph, WHITE if i % 2 == 0 else NAVY)
        pix.vline(ux + 5, y + 36, ph, GOLD)
        if i % 2 == 0:
            pix.vline(ux + 2, y + 38, ph - 4, GOLD_DK)
        if i in (0, 2, 4):
            draw_shako(pix, ux, y - 18, plume=True, small=True)
    pix.rect(x + 4, FLOOR_TOP - 12, w - 8, 3, METAL)


def draw_fountain(pix, x, y):
    pix.vgrad(x, y, 22, FLOOR_TOP - y, [METAL_HI, METAL, METAL_DK])
    pix.outline(x, y, 22, FLOOR_TOP - y, CASE)
    pix.rect(x + 2, y + 2, 18, 16, CASE_HI)
    pix.rect(x + 3, y + 14, 16, 5, METAL)
    pix.rect(x + 4, y + 15, 14, 3, CEIL_LIT)
    pix.dith(x + 6, y + 16, 8, 2, CEIL_LIT, FLUOR_G, "checker")
    pix.rect(x + 10, y + 8, 3, 7, CASE)
    pix.p(x + 11, y + 8, METAL_HI)
    pix.rect(x + 15, y + 11, 4, 3, GOLD)
    pix.p(x + 10, y + 16, INK)
    pix.p(x + 11, y + 16, INK)


def draw_trash(pix, x, y_bottom):
    h = 36
    y = y_bottom - h
    pix.vgrad(x, y, 20, h, [METAL, CASE_MD, CASE])
    pix.outline(x, y, 20, h, INK)
    pix.rect(x + 1, y, 18, 5, METAL)
    pix.hline(x + 1, y, 18, METAL_HI)
    pix.dith(x + 3, y + 8, 14, h - 14, CASE, CASE_MD, "bayer")
    pix.rect(x + 6, y + 1, 5, 3, WHITE)
    pix.p(x + 8, y, WHITE)


def draw_extinguisher(pix, x, y):
    pix.vgrad(x + 3, y, 8, 22, [RED, RED, RED_DK])
    pix.hline(x + 3, y, 8, (196, 70, 70))
    pix.rect(x + 4, y + 1, 6, 4, METAL)
    pix.hline(x + 4, y + 1, 6, METAL_HI)
    pix.rect(x + 6, y - 4, 2, 5, CASE)
    pix.rect(x + 7, y - 5, 6, 2, CASE_HI)
    pix.rect(x + 11, y - 4, 2, 6, CASE)
    pix.p(x + 5, y + 12, GOLD)
    pix.rect(x + 2, y + 20, 10, 3, RED_DK)


def draw_clock(pix, cx, cy, r=14, hour=19, minute=40):
    pix.circle(cx, cy, r, CASE)
    pix.circle(cx, cy, r - 1, METAL)
    pix.circle(cx, cy, r - 2, WHITE)
    pix.p(cx - 4, cy - 4, WHITE_SH)  # glass highlight
    pix.p(cx, cy - r + 4, INK)
    pix.p(cx, cy + r - 4, INK)
    pix.p(cx - r + 4, cy, INK)
    pix.p(cx + r - 4, cy, INK)
    pix.line(cx, cy, cx + 3, cy + 6, INK)
    pix.line(cx, cy, cx - 8, cy + 2, INK)
    pix.p(cx, cy, GOLD)
    pix.p(cx, cy, GOLD_LT)


def draw_bulletin(pix, x, y, w=44, h=50):
    pix.bevel(x, y, w, h, WOOD, WOOD_LT, WOOD_DK)
    pix.rect(x + 2, y + 2, w - 4, h - 4, RUST)
    pix.dith(x + 2, y + 2, w - 4, h - 4, RUST, WOOD_DK, "bayer")
    flyers = [
        (3, 3, 20, 20, WHITE, "BUS", "6PM"),
        (25, 6, 16, 16, WALL_HI, "TUNE", ""),
        (6, 26, 18, 20, WHITE, "SEC", "TION"),
        (26, 28, 16, 18, NAVY, "GO", ""),
    ]
    for fx, fy, fw, fh, col, label, sub in flyers:
        pix.rect(x + fx, y + fy, fw, fh, col)
        pix.outline(x + fx, y + fy, fw, fh, INK)
        pix.p(x + fx + 2, y + fy + 1, RED if col != NAVY else GOLD)
        if label:
            text(pix, x + fx + 2, y + fy + 5, label, INK if col != NAVY else WHITE, font="3",
                 bg=col, bg_rect=(x + fx + 1, y + fy + 4, fw - 2, 6))
        if sub:
            text(pix, x + fx + 2, y + fy + 11, sub, INK if col != NAVY else GOLD, font="3",
                 bg=col, bg_rect=(x + fx + 1, y + fy + 10, fw - 2, 6))


def draw_backpack(pix, x, y, color=NAVY):
    hi = NAVY_LT if color == NAVY else WALL_HI
    sh = NAVY_DK if color == NAVY else WOOD_DK
    pix.bevel(x, y, 12, 16, color, hi, sh)
    pix.rect(x + 3, y + 4, 6, 7, color)
    pix.outline(x + 3, y + 4, 6, 7, INK)
    pix.vline(x + 2, y - 2, 6, CASE)
    pix.vline(x + 9, y - 2, 6, CASE)
    pix.rect(x + 4, y + 12, 4, 2, GOLD_DK)


def draw_shoes(pix, x, y):
    for i, ox in enumerate((0, 11)):
        pix.rect(x + ox, y, 10, 5, SHOE)
        pix.rect(x + ox + 1, y + 1, 8, 2, CASE)
        pix.p(x + ox + (8 if i == 0 else 1), y, METAL_DK)


def draw_drumsticks(pix, x, y):
    pix.line(x, y, x + 16, y + 2, WOOD)
    pix.line(x, y + 1, x + 16, y + 3, WOOD_DK)
    pix.line(x + 2, y + 3, x + 18, y + 1, WOOD_LT)
    pix.line(x + 2, y + 4, x + 18, y + 2, WOOD)
    pix.p(x + 16, y + 2, WHITE)
    pix.p(x + 18, y + 1, WHITE)


def draw_megaphone(pix, x, y):
    for i in range(14):
        half = 1 + i // 2
        pix.vline(x + i, y + 6 - half, half * 2, NAVY if i > 2 else CASE)
        if i > 2:
            pix.p(x + i, y + 6 - half, NAVY_LT)
    pix.rect(x - 4, y + 4, 6, 5, CASE)
    pix.rect(x - 3, y + 5, 4, 3, CASE_HI)
    pix.p(x + 12, y + 6, GOLD_LT)


def draw_door(pix, x, y, w=44, h=170, lit=True):
    pix.vgrad(x, y, w, h, [WOOD_LT, WOOD, WOOD_DK])
    pix.outline(x, y, w, h, WOOD_DK)
    pix.hline(x, y, w, WOOD_LT)
    gw, gh = w - 14, 48
    gx, gy = x + 7, y + 8
    pix.bevel(gx - 1, gy - 1, gw + 2, gh + 2, WOOD_DK, WOOD, WOOD_DK, fill=False)
    if lit:
        pix.rect(gx, gy, gw, gh, FLUOR_DIM)
        pix.vgrad(gx, gy, gw, gh, [FLUOR, FLUOR_G, FLUOR_DIM])
        for i in range(3):
            pix.rect(gx + 4 + i * 8, gy + 18, 7, gh - 22, LOK_DK)
            pix.rect(gx + 5 + i * 8, gy + 20, 5, gh - 26, LOK)
            pix.p(gx + 6 + i * 8, gy + 22, LOK_LT)
        pix.rect(gx, gy, gw, 6, CEIL)
        pix.rect(gx + gw // 2 - 6, gy + 2, 12, 3, FLUOR_HI)
        pix.outline(gx, gy, gw, gh, INK)
        pix.p(gx + 2, gy + 8, WHITE)  # glass spec
    pix.bevel(x + 7, y + 64, w - 14, h - 88, WOOD, WOOD_LT, WOOD_DK)
    pix.outline(x + 9, y + 66, w - 18, h - 92, WOOD_DK)
    pix.dith(x + 10, y + 68, w - 20, h - 96, WOOD, WOOD_DK, "bayer")
    pix.hline(x + 10, y + 67, w - 20, WOOD_LT)
    pix.rect(x + w - 13, y + 110, 3, 14, GOLD_DK)
    pix.rect(x + w - 16, y + 114, 8, 4, GOLD)
    pix.p(x + w - 13, y + 115, GOLD_LT)
    pix.rect(x + 2, y + h - 14, w - 4, 10, METAL)
    pix.hline(x + 2, y + h - 14, w - 4, METAL_HI)


def draw_shower_door(pix, x, y, w=40, h=170):
    pix.vgrad(x, y, w, h, [METAL_HI, METAL, METAL_DK])
    pix.rect(x + 3, y + 3, w - 6, h - 6, CEIL_LT)
    pix.dith(x + 3, y + 3, w - 6, h - 6, CEIL_LT, METAL, "checker")
    # wet streaks
    for i, sx in enumerate((x + 8, x + 14, x + 22, x + 28)):
        pix.vline(sx, y + 10 + i * 6, 40 + i * 8, CEIL)
    pix.outline(x + 3, y + 3, w - 6, h - 6, CASE)
    pix.rect(x + w - 10, y + h // 2, 5, 3, CASE)
    pix.dith(x + 4, FLOOR_TOP, w - 8, 2, GROUT, TILE_DK, "checker")


def draw_ceiling_grid(pix, x, y, w, h, origin=0):
    pix.vgrad(x, y, w, h, [CEIL_DK, CEIL, CEIL_MD])
    for ty in range(y, y + h, 12):
        pix.hline(x, ty, w, CEIL_DK)
        pix.hline(x, ty + 1, w, CEIL_LT)
    for tx in range(x + (origin % 32), x + w, 32):
        pix.vline(tx, y, h, CEIL_DK)
    rng = random.Random(7 + origin)
    for _ in range(w // 36):
        sx = x + rng.randint(0, max(1, w - 4))
        sy = y + rng.randint(0, max(1, h - 3))
        pix.p(sx, sy, CEIL_DK)
        pix.p(sx + 1, sy, CEIL_DK)


def draw_fixture(pix, x, y, w=96, state="on"):
    pix.bevel(x, y, w, 14, METAL, METAL_HI, CASE)
    pix.rect(x + 2, y + 2, w - 4, 10, CASE)
    colors = {
        "on": (FLUOR, FLUOR_HI),
        "dim": (FLUOR_DIM, FLUOR),
        "surge": (FLUOR_HI, WHITE),
        "off": (METAL_DK, CEIL_LT),
    }
    c1, c2 = colors[state]
    for ty in (y + 3, y + 7):
        pix.rect(x + 6, ty, w - 12, 3, c1)
        pix.hline(x + 6, ty, w - 12, c2 if state != "off" else METAL)
        pix.p(x + 6, ty + 1, WHITE if state != "off" else CASE)
        pix.p(x + w - 7, ty + 1, WHITE if state != "off" else CASE)
        pix.rect(x + 4, ty, 2, 3, METAL)
        pix.rect(x + w - 6, ty, 2, 3, METAL)
    if state == "surge":
        pix.dith(x - 2, y - 2, w + 4, 2, FLUOR_HI, CEIL_GLOW, "bayer")
        pix.dith(x - 2, y + 14, w + 4, 2, FLUOR, CEIL_LIT, "bayer")
    if state == "off":
        pix.p(x + w // 2, y + 4, FLUOR)
        pix.p(x + w // 2 + 1, y + 4, FLUOR_HI)
    if state == "on":
        pix.dith(x + 8, y + 14, w - 16, 3, CEIL_GLOW, CEIL_LIT, "bayer")


def _hair_col(hair):
    return HAIR if hair == "dark" else (HAIR_BR if hair == "brown" else HAIR_BL)


def draw_kid_standing(pix, x, y_feet, facing=1, frame=0, hair="dark", pose="talk"):
    """~70px tall band kid, 8-frame body language, shaded navy kit."""
    head_r = 6
    head_cy = y_feet - 58
    head_cx = x
    bob = (0, 0, 1, 0, 0, 1, 0, 0)[frame & 7]
    if pose == "fidget":
        head_cx += (1, 1, 0, -1, -1, 0, 1, 0)[frame & 7]
        head_cy += bob
    head_cy += bob
    ly = y_feet - 24
    off = (1, 0, 0, -1, 0, 0, 1, 0)[frame & 7] if pose == "fidget" else 0
    pix.rect(head_cx - 7 + off, ly, 6, 22, WHITE)
    pix.rect(head_cx + 1, ly, 6, 22, WHITE)
    pix.vline(head_cx - 3 + off, ly + 3, 16, WHITE_SH)
    pix.vline(head_cx + 5, ly + 3, 16, WHITE_SH)
    pix.hline(head_cx - 7 + off, ly + 20, 6, WHITE_DK)
    pix.hline(head_cx + 1, ly + 20, 6, WHITE_DK)
    pix.vline(head_cx - 6 + off, ly + 1, 18, GOLD)
    pix.vline(head_cx + 4, ly + 1, 18, GOLD)
    pix.rect(head_cx - 8 + off + (0 if facing > 0 else -1), y_feet - 3, 8, 4, SHOE)
    pix.rect(head_cx + 1 + (1 if facing > 0 else -3), y_feet - 3, 8, 4, SHOE)
    # torso with vertical shade
    pix.vgrad(head_cx - 9, y_feet - 46, 18, 23, [NAVY_LT, NAVY, NAVY_DK])
    pix.vline(head_cx - 9, y_feet - 46, 23, NAVY_DK)
    pix.vline(head_cx + 8, y_feet - 46, 23, NAVY_DK)
    pix.vline(head_cx - 7, y_feet - 44, 18, GOLD)
    pix.vline(head_cx + 6, y_feet - 44, 18, GOLD)
    pix.vline(head_cx, y_feet - 44, 20, WHITE)
    for by in range(y_feet - 42, y_feet - 28, 5):
        pix.p(head_cx + 1, by, GOLD)
    pix.p(head_cx - 8, y_feet - 44, NAVY_LT)
    arm_y = y_feet - 44
    f = frame & 7
    if pose == "talk":
        pix.rect(head_cx - 12, arm_y, 4, 16, NAVY)
        pix.rect(head_cx - 12, arm_y + 16, 4, 4, SKIN)
        if f in (0, 1):
            pix.rect(head_cx + 9, arm_y, 4, 12, NAVY)
            pix.rect(head_cx + 10, arm_y + 12, 4, 4, SKIN)
        elif f in (2, 3, 6):
            pix.rect(head_cx + 9, arm_y, 4, 10, NAVY)
            pix.rect(head_cx + 11, arm_y - 2, 4, 4, SKIN)
            pix.rect(head_cx + 14, arm_y - 4, 4, 4, SKIN)
        else:
            pix.rect(head_cx + 9, arm_y - 2, 4, 10, NAVY)
            pix.rect(head_cx + 11, arm_y - 6, 4, 5, SKIN)
            pix.rect(head_cx + 14, arm_y - 8, 4, 4, SKIN)
    elif pose == "reach":
        pix.rect(head_cx - 12, arm_y, 4, 14, NAVY)
        pix.rect(head_cx - 12, arm_y + 14, 4, 4, SKIN)
        lift = (0, 1, 2, 3, 3, 2, 1, 0)[f]
        pix.rect(head_cx + 8, arm_y - 4 - lift, 4, 12, NAVY)
        pix.rect(head_cx + 10, arm_y - 8 - lift, 4, 5, SKIN)
    elif pose == "adjust":
        pix.rect(head_cx - 12, arm_y, 4, 14, NAVY)
        pix.rect(head_cx - 12, arm_y + 14, 4, 4, SKIN)
        lift = (2, 3, 4, 3, 2, 3, 4, 3)[f]
        pix.rect(head_cx + 7, arm_y - 6 - lift, 4, 12, NAVY)
        pix.rect(head_cx + 8, arm_y - 10 - lift, 4, 5, SKIN)
    else:
        pix.rect(head_cx - 12, arm_y, 4, 16, NAVY)
        pix.rect(head_cx - 12, arm_y + 16, 4, 4, SKIN)
        pix.rect(head_cx + 8, arm_y, 4, 16, NAVY)
        pix.rect(head_cx + 8, arm_y + 16, 4, 4, SKIN)
    pix.rect(head_cx - 2, head_cy + 5, 4, 4, SKIN)
    pix.circle(head_cx, head_cy, head_r, SKIN)
    pix.p(head_cx - 3, head_cy - 1, SKIN_LT)
    pix.p(head_cx - 2, head_cy - 2, SKIN_LT)
    hc = _hair_col(hair)
    pix.rect(head_cx - 6, head_cy - 6, 12, 5, hc)
    pix.p(head_cx - 6, head_cy - 1, hc)
    pix.p(head_cx + 6, head_cy - 1, hc)
    if hair == "blond":
        pix.p(head_cx, head_cy - 7, hc)
    eye_x = head_cx + (2 if facing > 0 else -2)
    pix.p(eye_x, head_cy, INK)
    pix.p(head_cx - (2 if facing > 0 else -2), head_cy, INK)
    pix.p(eye_x, head_cy - 1, hc)  # brow
    mouth_y = head_cy + 3
    if pose == "talk" and f in (0, 1, 4, 5):
        pix.p(head_cx, mouth_y, INK)
        pix.p(head_cx + 1, mouth_y, INK)
    else:
        pix.hline(head_cx - 1, mouth_y, 3, INK)


def draw_kid_sitting(pix, x, y_seat, facing=-1, frame=0, hair="brown", pose="sticks"):
    f = frame & 7
    head_cx = x
    head_cy = y_seat - 28 + (1 if f in (2, 3, 6) else 0)
    pix.rect(head_cx - 6, y_seat + 6, 5, 16, WHITE)
    pix.rect(head_cx + 2, y_seat + 6, 5, 16, WHITE)
    pix.vline(head_cx - 3, y_seat + 8, 12, WHITE_SH)
    pix.vline(head_cx + 5, y_seat + 8, 12, WHITE_SH)
    pix.hline(head_cx - 6, y_seat + 20, 5, WHITE_DK)
    pix.hline(head_cx + 2, y_seat + 20, 5, WHITE_DK)
    pix.vline(head_cx - 5, y_seat + 7, 12, GOLD)
    pix.vline(head_cx + 5, y_seat + 7, 12, GOLD)
    pix.rect(head_cx - 7, y_seat + 20, 8, 4, SHOE)
    pix.rect(head_cx + 2, y_seat + 20, 8, 4, SHOE)
    pix.rect(head_cx - 8, y_seat + 1, 16, 6, WHITE)
    pix.vgrad(head_cx - 8, y_seat - 18, 16, 20, [NAVY_LT, NAVY, NAVY_DK])
    pix.vline(head_cx - 6, y_seat - 16, 14, GOLD)
    pix.vline(head_cx + 5, y_seat - 16, 14, GOLD)
    pix.vline(head_cx, y_seat - 16, 16, WHITE)
    pix.rect(head_cx - 11, y_seat - 16, 4, 12, NAVY)
    pix.rect(head_cx - 11, y_seat - 4, 4, 3, SKIN)
    if pose == "sticks":
        if f % 2 == 0:
            pix.rect(head_cx + 8, y_seat - 16, 4, 10, NAVY)
            pix.rect(head_cx + 9, y_seat - 6, 4, 3, SKIN)
            pix.line(head_cx + 12, y_seat - 6, head_cx + 20, y_seat - 14 - (f % 3), WOOD)
        else:
            pix.rect(head_cx + 8, y_seat - 14, 4, 8, NAVY)
            pix.rect(head_cx + 10, y_seat - 8, 4, 3, SKIN)
            pix.line(head_cx + 13, y_seat - 8, head_cx + 22, y_seat - 4 + (f % 3), WOOD)
    elif pose == "tie":
        # leaning, tying a shoe
        dip = (2, 3, 3, 2, 1, 2, 3, 2)[f]
        pix.rect(head_cx + 8, y_seat - 10 + dip, 4, 8, NAVY)
        pix.rect(head_cx + 8, y_seat - 2 + dip, 4, 3, SKIN)
    pix.rect(head_cx - 2, head_cy + 5, 4, 4, SKIN)
    pix.circle(head_cx, head_cy, 6, SKIN)
    pix.p(head_cx - 2, head_cy - 1, SKIN_LT)
    hc = _hair_col(hair)
    pix.rect(head_cx - 6, head_cy - 6, 12, 5, hc)
    pix.p(head_cx - 6, head_cy, hc)
    pix.p(head_cx + 5, head_cy - 1, hc)
    pix.p(head_cx + (2 if facing > 0 else -2), head_cy, INK)
    pix.p(head_cx - (2 if facing > 0 else -2), head_cy, INK)
    pix.hline(head_cx - 1, head_cy + 3, 3, INK)


def draw_pennants(pix, x0, x1, y):
    pix.hline(x0, y, x1 - x0, CASE)
    pix.hline(x0, y + 1, x1 - x0, CASE_HI)
    colors = [NAVY, GOLD, WHITE, NAVY_DK, GOLD_DK, WHITE_SH]
    i = 0
    x = x0 + 2
    while x + 12 < x1:
        col = colors[i % len(colors)]
        shade = NAVY_DK if col in (NAVY, NAVY_DK) else (GOLD_DK if col in (GOLD, GOLD_DK) else WHITE_SH)
        hi = NAVY_LT if col in (NAVY, NAVY_DK) else (GOLD_LT if col in (GOLD, GOLD_DK) else WHITE)
        for dy in range(14):
            half = dy // 3
            pix.hline(x + half, y + 2 + dy, max(1, 12 - half * 2), col if dy < 12 else shade)
        pix.p(x + 2, y + 3, hi)
        i += 1
        x += 14


def draw_poster(pix, x, y, w, h, bg, title, sub=""):
    pix.bevel(x, y, w, h, bg, WHITE if bg != WHITE else WHITE_SH, INK)
    pix.outline(x, y, w, h, INK)
    pix.p(x + 1, y + 1, WHITE_SH)
    pix.p(x + w - 2, y + 1, WHITE_SH)
    if title:
        text(pix, x + 3, y + 4, title, INK if bg != NAVY else WHITE, font="3",
             bg=bg, bg_rect=(x + 2, y + 3, w - 4, 7))
    if sub:
        text(pix, x + 3, y + 12, sub, NAVY if bg != NAVY else GOLD, font="3",
             bg=bg, bg_rect=(x + 2, y + 11, w - 4, 7))


def draw_locker_tops(pix, x, w, rng):
    pix.bevel(x - 1, 134, w + 2, 7, WOOD, WOOD_LT, WOOD_DK)
    pix.hline(x - 1, 134, w + 2, WOOD_DK)
    n = max(3, w // 22)
    for i in range(n):
        sx = x + 4 + i * (w - 8) // n
        kind = (i + x) % 5
        if kind in (0, 2):
            draw_shako(pix, sx, 116, plume=True, small=True)
        elif kind == 1:
            pix.bevel(sx, 122, 12, 12, CASE, CASE_HI, INK)
            pix.rect(sx + 2, 124, 8, 5, WHITE_SH)
        elif kind == 3:
            pix.rect(sx + 2, 120, 6, 14, LOK)
            pix.rect(sx + 3, 122, 4, 8, LOK_LT)
            pix.rect(sx + 3, 118, 4, 3, METAL)
        else:
            pix.rect(sx + 3, 128, 6, 6, GOLD_DK)
            pix.rect(sx + 4, 118, 4, 10, GOLD)
            pix.p(sx + 5, 117, GOLD_LT)
            pix.hline(sx + 2, 124, 8, GOLD_DK)



# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------

def draw_far(rng):
    pix = Pix(W_FAR, H, CEIL_DK)
    draw_ceiling_grid(pix, 0, 0, W_FAR, 56, origin=8)
    for fx in (40, 200, 360, 520):
        draw_fixture(pix, fx, 8, 88, state="on")
        light_pool(pix, fx + 44, 16, 60, 20, CEIL_GLOW, max_amt=8, y0=0, y1=50)
    pix.dith(0, 50, W_FAR, 6, CEIL, WALL_SH, "h")

    pix.vgrad(0, 56, W_FAR, FLOOR_TOP - 56, [WALL_HI, WALL, WALL_SH, WALL_DK])
    pix.rect(0, 56, 8, FLOOR_TOP - 56, WALL_SH)
    pix.rect(W_FAR - 8, 56, 8, FLOOR_TOP - 56, WALL_SH)
    pix.hline(0, 56, W_FAR, WALL_DK)
    pix.hline(0, 57, W_FAR, WALL_HI)
    pix.hline(0, 58, W_FAR, WALL_DK)
    # side falloff only — no all-over wall flecks (keeps SF2 painted-gradient walls)
    darken_falloff(pix, 0, 70, 90, 90, WALL_SH, strength=4)
    darken_falloff(pix, W_FAR - 90, 70, 90, 90, WALL_SH, strength=4)

    for i, wx in enumerate((70, 270, 470)):
        pix.bevel(wx, 70, 90, 50, CASE, METAL, INK)
        for p in range(3):
            px = wx + 4 + p * 28
            pix.vgrad(px, 74, 26, 42, [INK, (20, 22, 40), (36, 32, 40)])
            if i != 1:
                pix.p(px + 8 + i * 3, 80, WHITE)
            if i == 1:
                pix.dith(px + 6, 100, 14, 14, GOLD_DK, CASE, "bayer")
                pix.dith(px + 8, 104, 8, 8, GOLD, GOLD_DK, "bayer")
            # stars
            pix.p(px + 5, 78, WHITE_SH)
        pix.rect(wx + 3, 74, 84, 2, METAL)
        pix.rect(wx + 3, 112, 84, 2, METAL)
        pix.p(wx + 8, 76, METAL_HI)

    pix.bevel(168, 78, 94, 22, NAVY, NAVY_LT, NAVY_DK)
    pix.hline(168, 78, 94, WHITE_SH)
    text(pix, 176, 84, "BAND ROOM", GOLD, 1, shadow=NAVY_DK, bg=NAVY, bg_rect=(174, 82, 56, 11))

    draw_clock(pix, 400, 92, 16)
    pix.bevel(560, 80, 48, 16, METAL, METAL_HI, CASE)
    for vy in range(84, 94, 3):
        pix.hline(564, vy, 40, CASE)
    pix.hline(0, 62, W_FAR, CASE_HI)
    pix.hline(0, 63, W_FAR, CASE)
    pix.hline(0, 64, W_FAR, INK)
    for hx in range(30, W_FAR, 80):
        pix.vline(hx, 56, 8, CASE)
    draw_bulletin(pix, 575, 110, 48, 54)

    pix.rect(0, 200, W_FAR, FLOOR_TOP - 200, WALL_SH)
    pix.rect(0, FLOOR_TOP - 6, W_FAR, 6, WALL_DK)
    pix.hline(0, FLOOR_TOP - 6, W_FAR, WALL_HI)

    # lit hallway
    pix.rect(430, 128, 50, FLOOR_TOP - 128, WALL_DK)
    pix.vgrad(436, 134, 38, FLOOR_TOP - 134, [FLUOR_G, WOOD, WOOD_DK])
    for i in range(3):
        pix.rect(440 + i * 10, 200, 9, 80, LOK_DK)
        pix.vgrad(441 + i * 10, 202, 7, 76, [LOK_LT, LOK, LOK_DK])
    pix.rect(436, 134, 38, 8, CEIL)
    pix.rect(448, 136, 16, 4, FLUOR_HI)
    light_pool(pix, 455, 180, 20, 40, FLUOR_G, max_amt=6, x0=436, x1=474, y0=134, y1=FLOOR_TOP)

    pix.rect(0, FLOOR_TOP, W_FAR, H - FLOOR_TOP, TILE_DK)
    flush_labels(pix)
    return pix


def draw_floor(pix, w, rng):
    pix.rect(0, FLOOR_TOP, w, H - FLOOR_TOP, TILE)
    rows = [300, 307, 316, 327, 340, 360]
    vp = w // 2
    for ri in range(len(rows) - 1):
        y0, y1 = rows[ri], rows[ri + 1]
        t = ri / max(1, (len(rows) - 2))
        tw = int(18 + t * 10)
        offset = int((vp % tw))
        col = 0
        x = -offset
        while x < w:
            even = ((col + ri) % 2 == 0)
            # 16-bit tile: slight inner bevel, not a flat fill
            base = TILE_MD if even else TILE
            dk = TILE if even else TILE_DK
            hi = TILE_HI if even else TILE_MD
            pix.rect(x, y0, tw, y1 - y0, base)
            pix.hline(x + 1, y0 + 1, max(1, tw - 3), hi)
            pix.vline(x + 1, y0 + 1, max(1, y1 - y0 - 2), dk if not even else hi)
            x += tw
            col += 1
        pix.hline(0, y0, w, GROUT)
    pix.hline(0, H - 1, w, GROUT_DK)
    for ri in range(len(rows) - 1):
        y0, y1 = rows[ri], rows[ri + 1]
        t = ri / max(1, (len(rows) - 2))
        tw = int(18 + t * 10)
        offset = int((vp % tw))
        x = -offset
        while x < w:
            pix.vline(x, y0, y1 - y0, GROUT)
            x += tw
    # scuffs — sparse, readable
    for _ in range(70):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(FLOOR_TOP + 2, H - 2)
        pix.p(sx, sy, GROUT if rng.random() < 0.6 else TILE_DK)
    for _ in range(40):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(FLOOR_TOP, FLOOR_TOP + 6)
        pix.p(sx, sy, GROUT_DK)


def apply_fluor_lighting(pix, flicker_state="on"):
    """Fluorescent glow pools + gentle wall/floor falloff. Fight band stays readable."""
    # corner falloff on the lockers only, sides only, so the mid wall doesn't stipple
    darken_falloff(pix, 0, 200, 80, FLOOR_TOP - 200, WALL_DK, strength=5)
    darken_falloff(pix, pix.w - 80, 200, 80, FLOOR_TOP - 200, WALL_DK, strength=5)
    for fx, fy, fw in FIXTURES:
        cx = fx + fw // 2
        state = flicker_state if fx == FLICKER_X else "on"
        if state == "off":
            pix.tint(fx - 6, 0, fw + 12, 28, CEIL_DK, 6)
            continue
        # tight, brighter core + a softer ring (closer tints = less noise)
        ceil_core = CEIL_GLOW if state == "surge" else CEIL_LIT
        ceil_ring = CEIL_LIT if state != "dim" else CEIL_MD
        light_pool(pix, cx, fy + 10, fw // 2 + 6, 12, ceil_core, max_amt=16 if state == "surge" else 13, y0=0, y1=40)
        light_pool(pix, cx, fy + 14, fw // 2 + 22, 22, ceil_ring, max_amt=8, y0=0, y1=50)
        # soft wash + a tight specular kiss on the upper locker faces only
        light_pool(pix, cx, 155, fw // 2 + 2, 28, LOK_HI, max_amt=7, y0=140, y1=200)
        light_pool(pix, cx, 148, fw // 2 - 4, 14, LOK_SPEC, max_amt=5, y0=140, y1=168)
        # floor pool stays in the back strip y=300-314
        light_pool(pix, cx, 305, fw // 2 + 20, 9, TILE_LIT, max_amt=13 if state != "dim" else 7, y0=FLOOR_TOP, y1=314)


def draw_mid(rng):
    pix = Pix(W_MID, H, None)
    for x0, x1 in ((0, 175), (785, 960)):
        draw_ceiling_grid(pix, x0, 0, x1 - x0, 52, origin=x0)
        pix.vgrad(x0, 52, x1 - x0, FLOOR_TOP - 52, [WALL_HI, WALL, WALL_SH])
        pix.hline(x0, 52, x1 - x0, WALL_DK)
        pix.hline(x0, 53, x1 - x0, WALL_HI)

    draw_ceiling_grid(pix, 0, 0, W_MID, 28, origin=0)
    for fx, fy, fw in FIXTURES:
        st = "dim" if fx == 850 else "on"
        draw_fixture(pix, fx, fy, fw, st)

    pix.vgrad(0, 140, W_MID, FLOOR_TOP - 140, [WALL, WALL_SH, WALL_DK])
    pix.rect(0, 260, W_MID, FLOOR_TOP - 260, WALL_SH)
    pix.hline(0, 260, W_MID, WALL_DK)
    pix.rect(0, FLOOR_TOP - 5, W_MID, 5, WALL_DK)
    pix.hline(0, FLOOR_TOP - 5, W_MID, WALL_HI)

    for cx in (170, 400, 640, 790):
        pix.vgrad(cx, 28, 10, FLOOR_TOP - 28, [WALL_MD, WALL_SH, WALL_DK])
        pix.vline(cx, 28, FLOOR_TOP - 28, WALL_HI)
        pix.vline(cx + 9, 28, FLOOR_TOP - 28, WALL_DK)
        pix.rect(cx - 2, 28, 14, 8, WALL_DK)
        pix.rect(cx - 2, FLOOR_TOP - 10, 14, 10, WALL_DK)

    draw_pennants(pix, 185, 395, 72)
    draw_pennants(pix, 650, 820, 72)
    # Mid pennants would otherwise cover the far "BAND ROOM" lettering.
    # Mid is origin x=-160, so far x maps to mid x+160.
    for j in range(82, 94):
        for i in range(174 + 160, 232 + 160):
            pix.px[i, j] = (0, 0, 0, 0)
    draw_poster(pix, 404, 88, 36, 44, WHITE, "DRILL", "CHART")
    draw_poster(pix, 602, 86, 36, 40, NAVY, "GO", "BAND")
    draw_poster(pix, 844, 90, 40, 36, WALL_HI, "NO", "FOOD")

    draw_shower_door(pix, 16, 130, 42, FLOOR_TOP - 130)
    pix.rect(14, 130, 3, FLOOR_TOP - 130, TILE_DK)
    text(pix, 18, 118, "SHOWERS", WALL_DK, 1, bg=None)

    draw_case(pix, 64, 250, 46, 50, "tuba")
    draw_case(pix, 70, 210, 40, 40, "snare")
    draw_case(pix, 108, 268, 58, 32, "trombone")
    draw_case(pix, 112, 236, 28, 32, "sax")

    locker_w = 28
    states_left = ["closed", "closed", "open", "closed", "ajar", "closed", "closed", "open"]
    nums_left = ["12", "13", "14", "15", "16", "17", "18", "19"]
    for i, (st, num) in enumerate(zip(states_left, nums_left)):
        draw_locker(pix, 180 + i * locker_w, 140, locker_w, 160, random.Random(100 + i), st, num)
    draw_locker_tops(pix, 180, 8 * locker_w, random.Random(33))
    draw_backpack(pix, 186, 250, NAVY)
    draw_backpack(pix, 328, 248, WOOD_DK)

    draw_whiteboard(pix, 410, 148, 132, 100)
    pix.rect(408, 146, 136, 2, WALL_DK)
    draw_door(pix, 552, 130, 46, FLOOR_TOP - 130, lit=True)
    pix.bevel(556, 112, 38, 14, LOK_DK, LOK_LT, LOK_SH)
    text(pix, 562, 115, "EXIT", LOK_LT, font="3", bg=LOK_DK, bg_rect=(558, 114, 34, 9))
    pix.rect(558, 113, 34, 1, LOK_LT)
    draw_extinguisher(pix, 600, 230)
    pix.rect(548, FLOOR_TOP, 54, 5, NAVY_DK)
    pix.dith(548, FLOOR_TOP, 54, 5, NAVY, NAVY_DK, "checker")

    draw_uniform_rack(pix, 612, 168, 80)
    states_r = ["closed", "open", "closed", "ajar", "closed"]
    nums_r = ["20", "21", "22", "23", "24"]
    for i, (st, num) in enumerate(zip(states_r, nums_r)):
        draw_locker(pix, 700 + i * locker_w, 140, locker_w, 160, random.Random(200 + i), st, num)
    draw_locker_tops(pix, 700, 5 * locker_w, random.Random(44))
    draw_sousaphone(pix, 718, 188)

    draw_case(pix, 900, 246, 50, 54, "tuba")
    draw_case(pix, 910, 214, 36, 32, "snare")
    draw_case(pix, 868, 272, 36, 28, "rect")
    pix.bevel(880, 250, 50, 8, WOOD, WOOD_LT, WOOD_DK)
    pix.rect(884, 258, 6, FLOOR_TOP - 258, WOOD_DK)
    pix.rect(920, 258, 6, FLOOR_TOP - 258, WOOD_DK)
    pix.rect(886, 244, 16, 8, WHITE)
    pix.rect(888, 246, 12, 5, WHITE_SH)
    pix.rect(906, 246, 10, 5, WHITE)
    pix.rect(908, 247, 6, 2, INK)
    pix.rect(908, 250, 5, 1, INK)
    draw_megaphone(pix, 918, 236)
    pix.rect(884, 247, 6, 3, METAL)
    pix.p(884, 248, METAL_HI)

    draw_fountain(pix, 158, 250)
    draw_trash(pix, 126, FLOOR_TOP)

    draw_bench(pix, 178, 276, 54, slats=2)
    draw_bench(pix, 290, 276, 108, slats=3)
    draw_bench(pix, 700, 276, 130, slats=4)

    draw_shako(pix, 188, 250, plume=True)
    draw_drumsticks(pix, 304, 272)
    draw_shoes(pix, 330, 270)
    pix.rect(360, 270, 8, 5, WHITE)
    pix.rect(362, 271, 3, 3, WHITE_SH)
    pix.rect(370, 270, 8, 5, WHITE)
    pix.rect(382, 262, 6, 14, LOK)
    pix.rect(383, 264, 4, 8, LOK_LT)
    pix.rect(383, 260, 4, 3, METAL)
    pix.rect(384, 258, 2, 3, CASE_HI)
    pix.rect(292, 268, 14, 8, WHITE)
    pix.rect(294, 270, 10, 1, INK)
    pix.rect(294, 272, 8, 1, INK)
    pix.rect(294, 274, 9, 1, INK)
    draw_shako(pix, 780, 252, plume=True)
    draw_drumsticks(pix, 740, 272)
    pix.hline(760, 274, 10, GOLD)
    pix.hline(761, 273, 8, GOLD_LT)
    pix.p(770, 274, WHITE)

    pix.p(812, 230, CASE)
    pix.rect(808, 231, 10, 14, WHITE_SH)
    pix.hline(808, 231, 10, WHITE)
    pix.bevel(542, 210, 8, 12, METAL, METAL_HI, CASE)
    pix.rect(545, 214, 3, 5, WHITE)

    draw_floor(pix, W_MID, rng)
    pix.dith(178, FLOOR_TOP, 54, 3, GROUT_DK, TILE_DK, "h")
    pix.dith(290, FLOOR_TOP, 108, 3, GROUT_DK, TILE_DK, "h")
    pix.dith(700, FLOOR_TOP, 130, 3, GROUT_DK, TILE_DK, "h")
    pix.dith(64, FLOOR_TOP, 100, 3, GROUT_DK, TILE_DK, "h")
    pix.dith(612, FLOOR_TOP, 80, 3, GROUT_DK, TILE_DK, "h")
    pix.dith(718, FLOOR_TOP, 50, 3, GROUT_DK, TILE_DK, "h")
    pix.dith(180, FLOOR_TOP, 224, 2, LOK_SH, GROUT, "h")
    pix.dith(700, FLOOR_TOP, 140, 2, LOK_SH, GROUT, "h")

    pix.hline(0, 26, W_MID, CASE)
    pix.hline(0, 27, W_MID, CASE_HI)

    apply_fluor_lighting(pix, flicker_state="on")
    flush_labels(pix)
    return pix


FLICKER_PATTERN = ["on", "on", "surge", "on", "dim", "on", "on", "off"]


def draw_anim(frame):
    pix = Pix(W_MID, H, None)
    st = FLICKER_PATTERN[frame & 7]
    pix.rect(FLICKER_X - 8, 0, FLICKER_W + 16, 26, CEIL)
    for tx in range(FLICKER_X - 8, FLICKER_X + FLICKER_W + 8, 32):
        pix.vline(tx, 0, 26, CEIL_DK)
    pix.hline(FLICKER_X - 8, 12, FLICKER_W + 16, CEIL_DK)
    draw_fixture(pix, FLICKER_X, FLICKER_Y, FLICKER_W, st)
    if st == "surge":
        pix.dith(FLICKER_X - 16, 26, FLICKER_W + 32, 12, FLUOR, CEIL_LIT, "bayer")
        pix.dith(FLICKER_X - 20, FLOOR_TOP, FLICKER_W + 40, 6, TILE_LIT, TILE_HI, "h")
        light_pool(pix, FLICKER_X + FLICKER_W // 2, 20, 70, 22, CEIL_GLOW, max_amt=10, y0=0, y1=40)
    elif st == "off":
        pix.dith(FLICKER_X - 10, 26, FLICKER_W + 20, 10, CEIL_DK, CEIL, "checker")
    elif st == "dim":
        pix.dith(FLICKER_X - 8, 26, FLICKER_W + 16, 8, CEIL, CEIL_DK, "bayer")

    # steam from showers — denser 8-frame cycle (left margin + a little inward)
    phase = frame & 7
    for i in range(5):
        sx = 30 + (i * 7 + phase * 2) % 22
        sy = 210 - i * 16 - (phase * 3 + i) % 10
        r = 4 + (i + phase) % 4
        col = WHITE_SH if i % 2 == 0 else METAL
        pix.circle(sx, sy, r, col)
        pix.circle(sx - 2, sy - 1, max(2, r - 2), WHITE)

    drip_x = FLICKER_X + 70
    pix.dith(drip_x - 3, 24, 8, 4, CEIL_DK, CEIL, "checker")
    drop_y = 28 + (phase * 16) % 112
    pix.p(drip_x, drop_y, FLUOR_DIM)
    pix.p(drip_x, drop_y + 1, CEIL_LT)
    pix.p(drip_x, drop_y + 2, FLUOR_DIM)
    if phase == 7:
        pix.p(drip_x, 140, FLUOR_DIM)
        pix.p(drip_x - 1, 141, CEIL_LT)
        pix.p(drip_x + 1, 141, CEIL_LT)

    # five background kids, 8-frame acting
    draw_kid_standing(pix, 248, FLOOR_TOP, facing=1, frame=frame, hair="dark", pose="reach")
    draw_kid_sitting(pix, 348, 276, facing=-1, frame=frame, hair="brown", pose="sticks")
    draw_kid_standing(pix, 536, FLOOR_TOP, facing=-1, frame=frame, hair="brown", pose="talk")
    draw_kid_standing(pix, 650, FLOOR_TOP, facing=1, frame=(frame + 3) & 7, hair="blond", pose="adjust")
    draw_kid_sitting(pix, 200, 276, facing=1, frame=(frame + 2) & 7, hair="dark", pose="tie")
    flush_labels(pix)
    return pix


def draw_near():
    """Foreground parallax layer. Transparent in the action box; edge props only."""
    pix = Pix(W_NEAR, H, None)
    # LEFT edge: sit in the -240 margin and peek ~30px into the centered view (x=240)
    # bench end coming toward camera
    bx, by, bw = 188, 248, 70
    pix.vgrad(bx, by, bw, 10, [WOOD_LT, WOOD, WOOD_DK])
    pix.hline(bx, by, bw, WOOD_LT)
    pix.hline(bx, by + 9, bw, WOOD_DK)
    for i in range(1, 3):
        pix.vline(bx + i * 22, by + 1, 8, WOOD_DK)
    # legs — taper toward the "near" end (left)
    pix.rect(bx + 4, by + 10, 8, FLOOR_TOP - (by + 10), CASE)
    pix.rect(bx + 6, by + 10, 3, FLOOR_TOP - (by + 10), CASE_HI)
    pix.rect(bx + 48, by + 10, 6, FLOOR_TOP - (by + 10), CASE)
    pix.rect(bx + 2, FLOOR_TOP - 4, 14, 4, CASE)
    pix.rect(bx + 44, FLOOR_TOP - 4, 12, 4, CASE)
    # a dropped glove + stick on the bench end
    pix.rect(bx + 14, by - 4, 10, 6, WHITE)
    pix.rect(bx + 16, by - 3, 4, 3, WHITE_SH)
    pix.line(bx + 28, by - 2, bx + 50, by + 2, WOOD)
    pix.line(bx + 28, by - 1, bx + 50, by + 3, WOOD_DK)

    # mop bucket at left edge
    bucket_x, bucket_y = 230, 268
    pix.vgrad(bucket_x, bucket_y, 28, 32, [METAL_HI, METAL, METAL_DK])
    pix.outline(bucket_x, bucket_y, 28, 32, INK)
    pix.rect(bucket_x + 2, bucket_y + 2, 24, 8, (70, 90, 80))
    pix.dith(bucket_x + 4, bucket_y + 4, 18, 5, CEIL_LIT, (70, 90, 80), "h")
    pix.rect(bucket_x - 2, bucket_y + 28, 32, 4, METAL_DK)
    # mop handle leaning out
    pix.line(bucket_x + 18, bucket_y - 70, bucket_x + 22, bucket_y + 4, WOOD)
    pix.line(bucket_x + 19, bucket_y - 70, bucket_x + 23, bucket_y + 4, WOOD_LT)
    pix.rect(bucket_x + 14, bucket_y - 78, 14, 10, CASE_MD)
    pix.dith(bucket_x + 14, bucket_y - 78, 14, 10, CASE_MD, CASE, "bayer")
    pix.rect(bucket_x + 16, bucket_y + 6, 8, 4, CASE)  # wringer

    # hanging uniform bag, upper left edge
    bag_x, bag_y = 222, 70
    pix.vline(bag_x + 14, 20, bag_y - 20, CASE)
    pix.p(bag_x + 14, 20, METAL)
    pix.vgrad(bag_x, bag_y, 32, 50, [NAVY_LT, NAVY, NAVY_DK])
    pix.outline(bag_x, bag_y, 32, 50, NAVY_DK)
    pix.hline(bag_x, bag_y, 32, GOLD)
    pix.rect(bag_x + 10, bag_y - 6, 12, 8, WHITE)
    pix.rect(bag_x + 12, bag_y - 4, 8, 4, WHITE_SH)
    text(pix, bag_x + 6, bag_y + 16, "BAND", GOLD, font="3", bg=NAVY, bg_rect=(bag_x + 5, bag_y + 15, 18, 7))
    # zipper
    pix.vline(bag_x + 16, bag_y + 8, 30, METAL)
    pix.p(bag_x + 16, bag_y + 20, GOLD_LT)

    # RIGHT edge
    # bench end
    rbx, rby, rbw = 850, 248, 70
    pix.vgrad(rbx, rby, rbw, 10, [WOOD_LT, WOOD, WOOD_DK])
    pix.hline(rbx, rby, rbw, WOOD_LT)
    pix.hline(rbx, rby + 9, rbw, WOOD_DK)
    pix.rect(rbx + 8, rby + 10, 6, FLOOR_TOP - (rby + 10), CASE)
    pix.rect(rbx + 50, rby + 10, 8, FLOOR_TOP - (rby + 10), CASE)
    pix.rect(rbx + 48, FLOOR_TOP - 4, 14, 4, CASE)
    draw_shako(pix, rbx + 18, rby - 26, plume=True)

    # second mop-less prop: a water crate / cone? Use a folding chair stack? 
    # A traffic-style "wet floor" isn't school-colored. Use a second hanging bag + instrument case corner.
    bag2_x, bag2_y = 844, 80
    pix.vline(bag2_x + 16, 28, bag2_y - 28, CASE)
    pix.vgrad(bag2_x, bag2_y, 30, 48, [NAVY, NAVY_DK, NAVY_DK])
    pix.outline(bag2_x, bag2_y, 30, 48, INK)
    pix.hline(bag2_x, bag2_y, 30, GOLD)
    pix.vline(bag2_x + 15, bag2_y + 6, 28, METAL)
    draw_case(pix, 872, 262, 46, 38, "trombone")

    flush_labels(pix)
    return pix


def compose_preview(far, mid, anim, near):
    preview = far.convert("RGBA")
    mid_c = (W_MID - W_FAR) // 2
    near_c = (W_NEAR - W_FAR) // 2
    preview = Image.alpha_composite(preview, mid.crop((mid_c, 0, mid_c + W_FAR, H)))
    preview = Image.alpha_composite(preview, anim.crop((mid_c, 0, mid_c + W_FAR, H)))
    preview = Image.alpha_composite(preview, near.crop((near_c, 0, near_c + W_FAR, H)))
    return preview.convert("RGB")


def validate_near(im):
    px = im.load()
    bad = 0
    # Center action box of the default view must stay clear.
    # near crop for preview starts at x=240; allow 40px edge peek: forbidden x=280..840, y=200..360.
    for y in range(200, H):
        for x in range(280, 840):
            if px[x, y][3] >= 128:
                bad += 1
    return bad


def main():
    rng = random.Random(SEED)
    far = crunch(draw_far(rng).im, opaque=True)
    mid = crunch(draw_mid(random.Random(SEED + 1)).im, opaque=False)
    anims = [crunch(draw_anim(i).im, opaque=False) for i in range(8)]
    near = crunch(draw_near().im, opaque=False)
    leaks = validate_near(near)
    print("near action-box leaks", leaks)

    far.save(DIR / "far.png")
    mid.save(DIR / "mid.png")
    near.save(DIR / "near.png")
    for i, im in enumerate(anims):
        im.save(DIR / f"anim_{i}.png")

    preview = crunch(compose_preview(far, mid, anims[0], near).convert("RGBA"), opaque=True)
    preview.save(DIR / "preview.png")
    preview.resize((W_FAR * 2, H * 2), Image.Resampling.NEAREST).save(DIR / "preview@2x.png")

    def info(p, im):
        return f"{p.name} {im.size[0]}x{im.size[1]} {im.mode}"

    names = ["far.png", "mid.png", "near.png"] + [f"anim_{i}.png" for i in range(8)] + ["preview.png", "preview@2x.png"]
    for n in names:
        im = Image.open(DIR / n)
        print(info(DIR / n, im))


if __name__ == "__main__":
    main()
