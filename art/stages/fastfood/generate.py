#!/usr/bin/env python3
"""Band Wars — generic fast-food restaurant stage (SNES / SF2 Turbo 16-bit look).

640x360 far, 960x360 mid/anim (origin x=-160), 1120x360 near (origin x=-240).
Seeded RNG, hand-pixel, no anti-aliasing, hard alpha only (0 or 255).
Richer-than-32 16-bit palette, ordered Bayer dither, neon + menu-board glow.
JMHS navy/gold/white uniforms (verbatim fighter swatches). Fictional BURGER SPOT only.
Fighters' feet at y=320; floor band y=300..360 stays uncluttered.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

SEED = 19920910
DIR = Path(__file__).resolve().parent
W_FAR, W_MID, W_NEAR, H = 640, 960, 1120, 360
FLOOR_TOP = 300
MENU_X, MENU_Y = 548, 36
NEON_X, NEON_Y = 210, 14
OPEN_X, OPEN_Y = 488, 86
FOUNTAIN_X = 730

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

# 16-bit scene ramps
SKY0, SKY1, SKY2, SKY3 = (10, 12, 28), (16, 18, 38), (24, 28, 58), (32, 36, 70)
LOT, LOT_MD, LOT_LINE = (36, 34, 40), (46, 44, 50), (80, 78, 70)
CAR = (24, 26, 32)
GLASS, GLASS_HI, GLASS_NEON = (42, 54, 74), (86, 110, 140), (90, 50, 80)
WALL_DK, WALL_SH, WALL = (122, 102, 76), (174, 152, 116), (214, 194, 154)
WALL_HI, WALL_WARM = (232, 214, 176), (236, 210, 170)
RED_DK, RED, RED_MD, RED_HI, RED_SPEC = (104, 20, 24), (168, 36, 38), (188, 48, 48), (208, 64, 58), (230, 120, 110)
CREAM, CREAM_SH, CREAM_LT = (236, 224, 194), (204, 186, 152), (246, 236, 214)
CHROME_DK, CHROME, CHROME_HI = (112, 116, 124), (196, 200, 204), (234, 236, 238)
COUNTER_DK, COUNTER, COUNTER_HI = (134, 102, 70), (180, 142, 98), (206, 170, 120)
MENU_BG, GLOW, GLOW_MD, GLOW_DIM, GLOW_HOT = (24, 26, 30), (255, 198, 64), (230, 170, 48), (186, 132, 36), (255, 230, 140)
NEON_P, NEON_P2, NEON_P3 = (255, 82, 148), (255, 130, 180), (255, 190, 210)
NEON_C, NEON_C2, NEON_C3 = (64, 216, 200), (120, 230, 220), (180, 240, 235)
TILE_W, TILE_W_HI, TILE_R, TILE_R_HI = (224, 214, 192), (240, 232, 214), (148, 34, 38), (180, 60, 60)
TILE_NEON_P, TILE_NEON_C, TILE_WARM = (200, 120, 140), (140, 180, 170), (236, 210, 160)
INK = (28, 26, 30)
SODIUM, SODIUM_HI = GOLD, GOLD_LT

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

    def p(self, x, y, c):
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


def text(pix, x, y, s, color, scale=1, shadow=None, font="5"):
    glyphs = FONT if font != "3" else FONT3
    adv = 6 if font != "3" else 4
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
                            pix.p(px + scale, py + scale, shadow)
                        pix.p(px, py, color)
        cx += adv * scale
    return cx


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

MENU_ICON_W = 16
MENU_TEXT_GAP = 2


def icon_burger(pix, x, y):
    pix.rect(x + 2, y + 1, 10, 3, SODIUM)
    pix.p(x + 1, y + 2, SODIUM)
    pix.p(x + 12, y + 2, SODIUM)
    pix.hline(x + 3, y + 1, 8, SODIUM_HI)
    pix.rect(x + 2, y + 4, 10, 2, SODIUM_HI)
    pix.rect(x + 2, y + 6, 10, 2, WALL_DK)
    pix.rect(x + 2, y + 8, 10, 3, SODIUM)
    pix.hline(x + 2, y + 10, 10, GLOW_DIM)


def icon_fries(pix, x, y):
    pix.rect(x + 3, y + 6, 8, 6, RED)
    pix.rect(x + 4, y + 7, 6, 4, RED_HI)
    for i, ox in enumerate((4, 6, 8, 10, 12)):
        hgt = 7 + (i % 3)
        pix.vline(x + ox, y + 6 - hgt, hgt, SODIUM_HI if i % 2 == 0 else SODIUM)
        pix.p(x + ox, y + 6 - hgt, CREAM)


def icon_drink(pix, x, y):
    pix.rect(x + 4, y + 3, 7, 9, RED)
    pix.rect(x + 5, y + 4, 5, 6, RED_HI)
    pix.hline(x + 3, y + 3, 9, CHROME)
    pix.rect(x + 7, y + 0, 2, 4, CHROME_DK)
    pix.p(x + 8, y, NEON_C)
    pix.rect(x + 5, y + 5, 3, 3, CHROME_HI)


def icon_combo(pix, x, y):
    pix.rect(x + 1, y + 2, 7, 2, SODIUM)
    pix.hline(x + 2, y + 2, 5, SODIUM_HI)
    pix.rect(x + 1, y + 4, 7, 1, SODIUM_HI)
    pix.rect(x + 1, y + 5, 7, 2, WALL_DK)
    pix.rect(x + 1, y + 7, 7, 2, SODIUM)
    pix.rect(x + 9, y + 7, 6, 5, RED)
    pix.rect(x + 10, y + 8, 4, 3, RED_HI)
    for i, ox in enumerate((10, 12, 14)):
        pix.vline(x + ox, y + 2, 6, SODIUM_HI if i % 2 == 0 else SODIUM)
        pix.p(x + ox, y + 2, CREAM)


def draw_shako(pix, x, y, small=True):
    pix.bevel(x, y + 2, 9, 8, NAVY, NAVY_LT, NAVY_DK)
    pix.rect(x + 1, y + 3, 7, 2, NAVY_LT)
    pix.rect(x, y + 9, 10, 2, SHOE)
    pix.hline(x, y + 8, 9, GOLD)
    pix.rect(x + 3, y + 4, 3, 3, GOLD)
    pix.p(x + 4, y + 5, GOLD_LT)
    pix.vline(x + 4, y - 5, 7, GOLD)
    pix.vline(x + 5, y - 6, 8, GOLD_LT)
    pix.p(x + 5, y - 6, WHITE)


def draw_fry_box(pix, x, y):
    pix.rect(x, y + 6, 10, 8, RED)
    pix.rect(x + 1, y + 7, 8, 5, RED_HI)
    pix.outline(x, y + 6, 10, 8, RED_DK)
    pix.p(x + 1, y + 7, RED_SPEC)
    for i, ox in enumerate((1, 3, 5, 7, 9)):
        pix.vline(x + ox, y + (2 if i % 2 else 1), 6 if i % 2 else 7, SODIUM if i % 2 else SODIUM_HI)


def draw_cup(pix, x, y, lid=True):
    pix.rect(x, y + 3, 7, 10, RED)
    pix.rect(x + 1, y + 4, 5, 7, RED_HI)
    pix.p(x + 2, y + 5, RED_SPEC)
    pix.hline(x, y + 3, 7, CHROME)
    if lid:
        pix.rect(x - 1, y + 1, 9, 3, CHROME)
        pix.hline(x - 1, y + 1, 9, CHROME_HI)
        pix.rect(x + 2, y - 2, 2, 4, CHROME_DK)
        pix.p(x + 3, y - 2, NEON_C)


def draw_tray(pix, x, y, w=28):
    pix.bevel(x, y, w, 8, RED, RED_HI, RED_DK)
    pix.rect(x + 2, y + 2, w - 4, 4, RED_DK)
    pix.p(x + 3, y + 1, RED_SPEC)


def draw_ketchup(pix, x, y, mustard=False):
    col, col2 = (SODIUM, SODIUM_HI) if mustard else (RED, RED_HI)
    pix.rect(x, y + 4, 6, 10, col)
    pix.rect(x + 1, y + 5, 4, 7, col2)
    pix.rect(x + 1, y, 4, 5, CHROME)
    pix.p(x + 2, y, CHROME_HI)
    pix.p(x + 3, y + 2, INK)


def draw_register(pix, x, y):
    pix.bevel(x, y + 8, 22, 14, CHROME_DK, CHROME, CAR)
    pix.rect(x + 2, y, 18, 12, MENU_BG)
    pix.outline(x + 2, y, 18, 12, CHROME)
    pix.rect(x + 4, y + 2, 14, 8, GLASS)
    pix.dith(x + 4, y + 2, 14, 8, NEON_C, GLASS, "bayer")
    pix.rect(x + 5, y + 3, 6, 2, NEON_C)
    pix.rect(x + 5, y + 6, 8, 1, CHROME)
    for r in range(2):
        for c in range(3):
            pix.p(x + 5 + c * 4, y + 11 + r * 4, CHROME)
    pix.rect(x + 1, y + 20, 20, 5, CHROME)
    pix.hline(x + 1, y + 20, 20, CHROME_HI)
    pix.rect(x + 9, y + 21, 6, 2, CHROME_DK)


def draw_soda_fountain(pix, x, y):
    pix.bevel(x, y, 54, 36, CHROME, CHROME_HI, CHROME_DK)
    pix.rect(x + 2, y + 2, 50, 8, MENU_BG)
    text(pix, x + 6, y + 3, "FOUNTAIN", GLOW, font="3")
    for i in range(6):
        sx = x + 5 + i * 8
        colors = [RED, SODIUM, NEON_C, RED_HI, GLOW, GLASS_HI]
        pix.rect(sx, y + 12, 6, 8, colors[i])
        pix.p(sx + 1, y + 13, CHROME_HI)
        pix.rect(sx + 1, y + 20, 3, 5, CHROME_DK)
        pix.p(sx + 2, y + 25, CHROME)
    pix.rect(x + 2, y + 28, 50, 6, CHROME_DK)
    pix.dith(x + 4, y + 29, 46, 4, CAR, CHROME_DK, "h")
    draw_cup(pix, x + 14, y + 22, lid=False)


def draw_pendant(pix, x, y, length=28):
    pix.vline(x, 0, length, CHROME_DK)
    pix.vline(x + 1, 0, length, CHROME)
    pix.circle(x, y + length + 5, 7, GOLD)
    pix.circle(x, y + length + 5, 5, GOLD_LT)
    pix.p(x - 2, y + length + 3, CREAM_LT)
    pix.p(x - 1, y + length + 2, WHITE)


def draw_booth_seat(pix, x, y, w, h, facing="front"):
    # vinyl with a highlight band at the top, mid body, dark tuck at the bottom
    pix.vgrad(x, y, w, h, [RED_HI, RED, RED_MD, RED_DK], transition=4)
    pix.hline(x, y, w, RED_SPEC)
    pix.hline(x, y + 1, w, RED_HI)
    pix.hline(x + 2, y + 3, max(1, w - 4), RED_SPEC)
    for i in range(1, w // 12):
        pix.vline(x + i * 12, y + 2, h - 4, RED_DK)
        pix.vline(x + i * 12 + 1, y + 3, h - 8, RED_HI)
        pix.p(x + i * 12 + 2, y + 6, RED_SPEC)
        pix.p(x + i * 12 + 2, y + 14, RED_HI)
    # diagonal vinyl sheen
    for i in range(4, w - 6, 3):
        sy = y + 8 + (i % 7)
        if sy < y + h - 4:
            pix.p(x + i, sy, RED_SPEC)
    sh = 14
    pix.vgrad(x - 2, y + h - 2, w + 4, sh, [RED_HI, RED, RED_DK], transition=3)
    pix.hline(x - 2, y + h - 2, w + 4, RED_SPEC)
    pix.dith(x, y + h, w, 3, RED_HI, RED, "h")
    pix.hline(x, y + h - 1, w, RED_DK)


def draw_table(pix, x, y, w, d=20):
    pix.bevel(x, y, w, 5, CREAM, CREAM_LT, CREAM_SH)
    pix.hline(x, y, w, CHROME_HI)
    pix.hline(x, y + 4, w, CHROME_DK)
    pix.rect(x + w // 2 - 3, y + 5, 6, FLOOR_TOP - (y + 5) - 2, CHROME_DK)
    pix.vline(x + w // 2 - 2, y + 5, FLOOR_TOP - (y + 5) - 2, CHROME)
    pix.rect(x + w // 2 - 8, FLOOR_TOP - 4, 16, 4, CHROME)


def draw_car(pix, x, y, w=48, h=22, body=RED, facing=1):
    pix.rect(x + 6, y, w - 14, 10, body)
    pix.rect(x, y + 8, w, 12, body)
    pix.hline(x + 6, y, w - 14, CHROME if body != CAR else LOT_LINE)
    pix.rect(x + 8, y + 2, 12, 7, GLASS)
    pix.rect(x + 22, y + 2, 12, 7, GLASS)
    pix.dith(x + 8, y + 2, 12, 7, GLASS_HI, GLASS, "bayer")
    pix.p(x + 10, y + 3, CHROME)
    pix.circle(x + 10, y + h - 2, 5, INK)
    pix.circle(x + 10, y + h - 2, 2, CHROME_DK)
    pix.circle(x + w - 12, y + h - 2, 5, INK)
    pix.circle(x + w - 12, y + h - 2, 2, CHROME_DK)
    if facing > 0:
        pix.rect(x + w - 3, y + 12, 3, 4, GOLD_LT)
        pix.rect(x, y + 12, 3, 4, RED_HI)
    else:
        pix.rect(x, y + 12, 3, 4, GOLD_LT)
        pix.rect(x + w - 3, y + 12, 3, 4, RED_HI)


def draw_bus(pix, x, y):
    w, h = 110, 40
    pix.vgrad(x, y + 6, w, h - 6, [GOLD_LT, GOLD, GOLD_DK], transition=4)
    pix.rect(x, y, w - 16, 8, GOLD)
    pix.hline(x, y, w - 16, GOLD_LT)
    pix.rect(x, y + 6, w, 4, GOLD_DK)
    pix.rect(x, y + 22, w, 4, NAVY)
    pix.hline(x, y + 22, w, NAVY_LT)
    for i in range(6):
        wx = x + 8 + i * 14
        pix.rect(wx, y + 8, 12, 10, GLASS)
        pix.dith(wx, y + 8, 12, 10, GLASS_HI, SKY2, "bayer")
        pix.outline(wx, y + 8, 12, 10, INK)
        pix.p(wx + 2, y + 9, CHROME)
    pix.rect(x + w - 18, y + 8, 12, h - 14, GLASS)
    pix.outline(x + w - 18, y + 8, 12, h - 14, INK)
    for wx in (x + 16, x + 44, x + 80):
        pix.circle(wx, y + h - 2, 7, INK)
        pix.circle(wx, y + h - 2, 3, CHROME_DK)
    text(pix, x + 30, y + 28, "BAND", WHITE, font="5")
    pix.rect(x + w - 4, y + 26, 4, 5, GOLD_LT)
    pix.rect(x, y + 26, 3, 5, RED)


def draw_lamppost(pix, x, y_top, y_ground, glow=True):
    pix.vline(x, y_top, y_ground - y_top, CHROME_DK)
    pix.vline(x + 1, y_top, y_ground - y_top, LOT_LINE)
    pix.rect(x - 6, y_top, 14, 5, CAR)
    pix.rect(x - 5, y_top + 1, 12, 3, GOLD_LT if glow else CHROME_DK)
    if glow:
        light_pool(pix, x, y_top + 16, 22, 20, GOLD, max_amt=7, y0=y_top, y1=y_top + 50)
        pix.dith(x - 16, y_top + 5, 34, 18, GOLD, SKY2, "bayer")


def neon_halo(pix, cx, cy, rx, ry, color, max_amt=10, y0=None, y1=None, x0=None, x1=None):
    light_pool(pix, cx, cy, rx, ry, color, max_amt=max_amt, y0=y0, y1=y1, x0=x0, x1=x1)


def radial_glow(pix, cx, cy, rx, ry, colors, y0=None, y1=None, x0=None, x1=None, seam=5):
    """Concentric glow bands; Bayer only at seams / the outer fringe."""
    n = max(1, len(colors))
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
            d = (dx * dx + dy * dy) ** 0.5
            if d >= 1:
                continue
            t = d * n
            i0 = min(n - 1, int(t))
            frac = t - i0
            if i0 >= n - 1:
                if bayer(x, y) < int((1 - frac) * 12):
                    pix.p(x, y, colors[i0])
            elif frac * seam > (seam - 1) and i0 + 1 < n and bayer(x, y) < int((frac * seam - (seam - 1)) * 16):
                pix.p(x, y, colors[i0 + 1])
            else:
                pix.p(x, y, colors[i0])


def floor_reflect(pix, cx, y0, half_w, color, rows=6):
    """Structured horizontal reflection smear, back-strip only."""
    for row in range(rows):
        y = y0 + row
        if y >= 314 or y >= pix.h:
            break
        w = int(half_w * (1 - row / max(1, rows)))
        thresh = 13 - row * 2
        for x in range(max(0, cx - w), min(pix.w, cx + w + 1)):
            if pix.get(x, y)[3] < 128:
                continue
            if bayer(x, y) < thresh:
                pix.p(x, y, color)


def draw_night_scene(pix, w, h, rng, xoff=0):
    # banded night sky — dither only at the band seams (SF2 sunset/night skies)
    pix.rect(0, 0, w, 40, SKY0)
    pix.vgrad(0, 30, w, 50, [SKY0, SKY1, SKY2], transition=8)
    pix.vgrad(0, 70, w, 50, [SKY2, SKY3], transition=8)
    rng2 = random.Random(77)
    for _ in range(80):
        sx = rng2.randint(0, w - 1)
        sy = rng2.randint(4, 95)
        pix.p(sx, sy, CREAM if rng2.random() < 0.25 else CHROME)
        if rng2.random() < 0.12:
            pix.p(sx + 1, sy, GLASS_HI)
    mx, my = w - 90 - xoff // 4, 28
    pix.circle(mx, my, 11, CREAM)
    pix.circle(mx + 4, my - 3, 11, SKY0)
    pix.p(mx - 4, my + 1, CHROME_HI)
    rng3 = random.Random(91)
    horizon = 118
    for bx in range(-10, w, 26):
        bh = 16 + rng3.randint(0, 28)
        bw = 18 + rng3.randint(0, 10)
        pix.rect(bx, horizon - bh, bw, bh, CAR)
        if rng3.random() < 0.55 and bh > 18:
            pix.rect(bx + 4, horizon - bh + 5, 4, 4, GOLD)
            if rng3.random() < 0.5:
                pix.rect(bx + 11, horizon - bh + 10, 3, 3, GOLD_LT)
    pix.hline(0, horizon, w, INK)
    pix.rect(0, horizon + 1, w, h - (horizon + 1), LOT)
    for _ in range(280):
        pix.p(rng3.randint(0, w - 1), rng3.randint(horizon + 2, min(h - 1, 260)), CAR)
    for row, y in enumerate((128, 150, 174)):
        tw = 32 + row * 8
        x = 6 + row * 5
        while x < w:
            pix.hline(x, y, tw - 8, LOT_LINE)
            pix.vline(x, y, 8 + row * 2, LOT_LINE)
            x += tw
    draw_lamppost(pix, 60, 42, 175, glow=True)
    draw_lamppost(pix, 240, 36, 180, glow=True)
    draw_lamppost(pix, 420, 44, 176, glow=True)
    px = 28
    pix.rect(px, 50, 6, 128, CHROME_DK)
    pix.bevel(px - 16, 100, 40, 36, MENU_BG, CHROME, INK)
    text(pix, px - 14, 104, "BURGER", NEON_P, font="3")
    text(pix, px - 10, 112, "SPOT", NEON_C, font="3")
    pix.rect(px - 12, 124, 32, 4, NEON_P)
    neon_halo(pix, px + 4, 118, 28, 22, NEON_P2, max_amt=8, y0=96, y1=148)
    neon_halo(pix, px + 4, 118, 16, 12, NEON_P3, max_amt=6, y0=100, y1=140)
    pix.dith(px - 18, 136, 44, 16, GOLD, LOT, "bayer")
    draw_car(pix, 40, 132, 46, 20, RED, 1)
    draw_car(pix, 120, 128, 44, 20, CREAM_SH, 1)
    draw_car(pix, 80, 154, 48, 20, CAR, -1)
    draw_car(pix, 200, 150, 46, 20, NAVY, 1)
    draw_car(pix, 360, 134, 44, 20, WALL_DK, 1)
    draw_car(pix, 480, 152, 48, 20, RED_DK, -1)
    draw_bus(pix, 165, 142)
    for fx in range(0, w, 8):
        pix.vline(fx, horizon - 2, 10, CHROME_DK)
    pix.hline(0, horizon + 2, w, CHROME_DK)
    for sx, sy in ((16, 168), (300, 170), (560, 166)):
        pix.circle(sx, sy, 7, CAR)
        pix.circle(sx + 5, sy + 2, 5, INK)


def draw_window_frame(pix, x, y, w, h, panes=3, fill_night=False, rng=None, neon_reflect=False):
    pix.bevel(x, y, w, h, CHROME_DK, CHROME, INK)
    pix.hline(x, y, w, CHROME_HI)
    pix.rect(x + 3, y + 3, w - 6, h - 6, INK if fill_night else (0, 0, 0, 0))
    inner_w = w - 6
    pw = inner_w // panes
    for i in range(panes):
        px = x + 3 + i * pw
        if fill_night and rng is not None:
            pix.vgrad(px, y + 3, pw - 1, h - 6, [SKY1, SKY3, LOT], transition=6)
            if rng.random() < 0.7:
                pix.p(px + 4, y + 10, CREAM)
        if i:
            pix.rect(px - 1, y, 3, h, CHROME_DK)
            pix.vline(px, y, h, CHROME)
    pix.rect(x, y + h // 3, w, 3, CHROME_DK)
    pix.hline(x, y + h // 3, w, CHROME)
    pix.rect(x - 2, y + h - 2, w + 4, 5, WALL_DK)
    pix.hline(x - 2, y + h - 2, w + 4, CREAM_SH)
    # sparse glass reflections (interior + neon)
    rng2 = random.Random(12 + x)
    for _ in range((w * h) // 200):
        rx = x + 5 + rng2.randint(0, max(1, w - 12))
        ry = y + 5 + rng2.randint(0, max(1, h - 14))
        pix.p(rx, ry, CREAM_SH if rng2.random() < 0.4 else CHROME)
    if neon_reflect:
        # diagonal glass gleams + a pink/teal wash in the upper panes
        neon_halo(pix, x + w // 2, y + 16, w // 2 - 4, 18, NEON_P2, max_amt=7, y0=y + 3, y1=y + 36, x0=x + 3, x1=x + w - 3)
        neon_halo(pix, x + w - 16, y + 14, 18, 12, NEON_C2, max_amt=6, y0=y + 3, y1=y + 30, x0=x + 3, x1=x + w - 3)
        for k in range(0, min(w, h) - 12, 5):
            pix.p(x + 8 + k, y + 8 + k // 2, CREAM if k % 10 == 0 else NEON_P3)
            if k + 1 < w:
                pix.p(x + 9 + k, y + 8 + k // 2, GLASS_HI)


def draw_neon_sign(pix, x, y, on=True, buzz_mask=None):
    w, h = 168, 28
    pix.bevel(x, y, w, h, MENU_BG, CHROME_DK, INK)
    pix.outline(x, y, w, h, CHROME)
    word = "BURGER SPOT"
    cx = x + 8
    spot_from = word.index(" ") + 1
    for i, ch in enumerate(word):
        if ch == " ":
            cx += 4
            continue
        dim = (not on) or (buzz_mask and i in buzz_mask)
        is_spot = i >= spot_from
        main = NEON_C if is_spot else NEON_P
        shade = NEON_P3 if is_spot else NEON_C
        color = CHROME_DK if dim else main
        if not dim:
            text(pix, cx + 1, y + 6, ch, shade, scale=2)
        text(pix, cx, y + 5, ch, color, scale=2)
        cx += 14 if ch != "I" else 12
    if not on:
        pix.p(x + 20, y + 4, NEON_P)
        pix.p(x + 80, y + 10, NEON_C)


def draw_open_sign(pix, x, y, on=True):
    pix.bevel(x, y, 36, 16, MENU_BG, CHROME, INK)
    col = NEON_C if on else CHROME_DK
    text(pix, x + 6, y + 5, "OPEN", col, font="3")
    if on:
        pix.outline(x + 1, y + 1, 34, 14, NEON_C)


def draw_menu_board(pix, x, y, title, rows, glow=True):
    w, h = 92, 96
    g = GLOW if glow else GLOW_DIM
    g2 = SODIUM_HI if glow else SODIUM
    pix.bevel(x, y, w, h, MENU_BG, CHROME_DK, INK)
    pix.rect(x + 2, y + 2, w - 4, 12, CAR)
    text(pix, x + 6, y + 4, title, g, font="3")
    pix.hline(x + 2, y + 14, w - 4, g if glow else GLOW_DIM)
    icons = {"burger": icon_burger, "fries": icon_fries, "drink": icon_drink, "combo": icon_combo}
    for i, (kind, name, price) in enumerate(rows):
        ry = y + 18 + i * 24
        ix = x + 4
        tx = ix + MENU_ICON_W + MENU_TEXT_GAP
        icons.get(kind, icon_burger)(pix, ix, ry)
        text(pix, tx, ry + 2, name, g2, font="3")
        text(pix, tx, ry + 9, price, CREAM if glow else CHROME, font="3")
    if glow:
        pix.dith(x - 2, y - 2, w + 4, 3, GLOW_HOT, g, "h")
        pix.dith(x - 2, y - 1, 3, h + 2, GLOW, GLOW_MD, "v")
        pix.dith(x + w - 1, y - 1, 3, h + 2, GLOW_MD, GLOW_DIM, "v")
        pix.outline(x, y, w, h, GLOW_MD)


def draw_counter(pix, x, y, w):
    pix.bevel(x, y, w, 10, COUNTER, COUNTER_HI, COUNTER_DK)
    pix.hline(x, y, w, CHROME)
    pix.vgrad(x, y + 10, w, FLOOR_TOP - (y + 10), [COUNTER, COUNTER_DK], transition=6)
    pix.rect(x, y + 16, w, 10, RED)
    pix.hline(x, y + 16, w, RED_HI)
    pix.hline(x, y + 25, w, RED_DK)
    pw = 40
    for i, px in enumerate(range(x + 4, x + w - 8, pw)):
        pix.bevel(px, y + 30, pw - 6, FLOOR_TOP - (y + 34), COUNTER, COUNTER_HI, COUNTER_DK)
        # wood grain
        for gx in range(px + 3, px + pw - 10, 5):
            pix.vline(gx, y + 34, FLOOR_TOP - (y + 42), COUNTER_DK)
            pix.p(gx + 1, y + 36, COUNTER_HI)
    pix.rect(x, FLOOR_TOP - 6, w, 6, CHROME_DK)
    pix.hline(x, FLOOR_TOP - 6, w, CHROME)


def _hair_col(hair):
    return HAIR if hair == "dark" else (HAIR_BR if hair == "brown" else HAIR_BL)


def draw_kid_booth(pix, x, y_table, facing=1, frame=0, hair="dark", action="eat"):
    f = frame & 7
    bob = (0, 0, 1, 0, 0, 1, 0, 0)[f]
    head_cx = x
    head_cy = y_table - 22 + bob
    pix.vgrad(head_cx - 8, y_table - 16 + bob, 16, 18, [NAVY_LT, NAVY, NAVY_DK], transition=3)
    pix.vline(head_cx - 8, y_table - 16 + bob, 18, NAVY_DK)
    pix.vline(head_cx + 7, y_table - 16 + bob, 18, NAVY_DK)
    pix.vline(head_cx - 6, y_table - 14 + bob, 12, GOLD)
    pix.vline(head_cx + 5, y_table - 14 + bob, 12, GOLD)
    pix.vline(head_cx, y_table - 14 + bob, 14, WHITE)
    pix.rect(head_cx - 2, head_cy + 5, 4, 4, SKIN)
    pix.circle(head_cx, head_cy, 6, SKIN)
    pix.p(head_cx - 2, head_cy - 1, SKIN_LT)
    hc = _hair_col(hair)
    pix.rect(head_cx - 6, head_cy - 6, 12, 5, hc)
    pix.p(head_cx - 6, head_cy - 1, hc)
    pix.p(head_cx + 5, head_cy - 1, hc)
    if hair == "blond":
        pix.p(head_cx, head_cy - 7, hc)
    pix.p(head_cx - 2, head_cy, INK)
    pix.p(head_cx + 2, head_cy, INK)
    if action == "eat" and f in (1, 2, 5, 6):
        pix.p(head_cx, head_cy + 3, INK)
        pix.p(head_cx + 1, head_cy + 3, INK)
    else:
        pix.hline(head_cx - 1, head_cy + 3, 3, INK)
    if action == "eat":
        if f in (1, 2, 5, 6):
            pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 14 + bob, 4, 6, NAVY)
            pix.rect(head_cx + (8 if facing > 0 else -10), head_cy + 2, 3, 3, SKIN)
            pix.p(head_cx + (7 if facing > 0 else -6), head_cy + 2, SODIUM_HI)
        else:
            pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 10 + bob, 4, 8, NAVY)
            pix.rect(head_cx + (7 if facing > 0 else -9), y_table - 2, 4, 3, SKIN)
            pix.p(head_cx + (10 if facing > 0 else -6), y_table - 1, SODIUM_HI)
    elif action == "drink":
        if f in (1, 2, 5, 6):
            pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 16 + bob, 4, 8, NAVY)
            draw_cup(pix, head_cx + (8 if facing > 0 else -12), head_cy - 2, lid=True)
        else:
            pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 10 + bob, 4, 8, NAVY)
            pix.rect(head_cx + (7 if facing > 0 else -9), y_table - 2, 4, 3, SKIN)
            draw_cup(pix, head_cx + (10 if facing > 0 else -14), y_table - 8, lid=True)
    else:
        pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 12 + bob, 4, 10, NAVY)
        pix.rect(head_cx + (7 if facing > 0 else -9), y_table - 2, 4, 3, SKIN)
        if f % 2 == 0:
            pix.rect(head_cx + (10 if facing > 0 else -12), y_table - 16 + bob, 3, 6, SKIN)


def draw_kid_standing(pix, x, y_feet, facing=1, frame=0, hair="dark", pose="wait"):
    f = frame & 7
    bob = (0, 0, 1, 0, 0, 1, 0, 0)[f]
    head_cx, head_cy = x, y_feet - 54 + bob
    pix.rect(head_cx - 7, y_feet - 22, 6, 20, WHITE)
    pix.rect(head_cx + 1, y_feet - 22, 6, 20, WHITE)
    pix.vline(head_cx - 3, y_feet - 20, 14, WHITE_SH)
    pix.vline(head_cx + 5, y_feet - 20, 14, WHITE_SH)
    pix.hline(head_cx - 7, y_feet - 5, 6, WHITE_DK)
    pix.hline(head_cx + 1, y_feet - 5, 6, WHITE_DK)
    pix.vline(head_cx - 6, y_feet - 20, 16, GOLD)
    pix.vline(head_cx + 4, y_feet - 20, 16, GOLD)
    pix.rect(head_cx - 8, y_feet - 3, 8, 4, SHOE)
    pix.rect(head_cx + 1, y_feet - 3, 8, 4, SHOE)
    pix.vgrad(head_cx - 9, y_feet - 42, 18, 21, [NAVY_LT, NAVY, NAVY_DK], transition=3)
    pix.vline(head_cx - 7, y_feet - 40, 16, GOLD)
    pix.vline(head_cx + 6, y_feet - 40, 16, GOLD)
    pix.vline(head_cx, y_feet - 40, 18, WHITE)
    pix.rect(head_cx - 12, y_feet - 40, 4, 14, NAVY)
    pix.rect(head_cx - 12, y_feet - 26, 4, 3, SKIN)
    if pose == "wait":
        # arms crossed or at sides, slight shift
        ox = (0, 0, 1, 1, 0, 0, -0, 0)[f]
        pix.rect(head_cx + 8, y_feet - 40 + ox, 4, 12, NAVY)
        pix.rect(head_cx + 8, y_feet - 28 + ox, 4, 3, SKIN)
    else:
        # jukebox — one hand on the machine
        pix.rect(head_cx + 8, y_feet - 38, 4, 10, NAVY)
        pix.rect(head_cx + 10, y_feet - 28, 4, 3, SKIN)
    pix.rect(head_cx - 2, head_cy + 5, 4, 3, SKIN)
    pix.circle(head_cx, head_cy, 6, SKIN)
    pix.p(head_cx - 2, head_cy - 1, SKIN_LT)
    hc = _hair_col(hair)
    pix.rect(head_cx - 6, head_cy - 6, 12, 5, hc)
    pix.p(head_cx - 2, head_cy, INK)
    pix.p(head_cx + 2, head_cy, INK)
    pix.hline(head_cx - 1, head_cy + 3, 3, INK)


def draw_cashier(pix, x, y_counter, frame=0, facing=-1):
    f = frame & 7
    bob = (0, 0, 1, 0, 0, 0, 1, 0)[f]
    head_cx = x + (1 if f in (4, 5, 6) else 0) * facing
    head_cy = y_counter - 26 + bob
    pix.rect(head_cx - 8, y_counter - 18 + bob, 16, 20, CREAM)
    pix.rect(head_cx - 8, y_counter - 8 + bob, 16, 4, RED)
    pix.hline(head_cx - 8, y_counter - 8 + bob, 16, RED_HI)
    pix.rect(head_cx - 2, head_cy + 5, 4, 4, SKIN)
    pix.circle(head_cx, head_cy, 6, SKIN)
    pix.p(head_cx - 2, head_cy - 1, SKIN_LT)
    pix.rect(head_cx - 7, head_cy - 4, 14, 3, RED)
    pix.rect(head_cx - 6, head_cy - 7, 12, 4, RED_DK)
    pix.p(head_cx, head_cy - 6, CREAM)
    pix.rect(head_cx - 5, head_cy - 8, 10, 2, INK)
    pix.p(head_cx - 2, head_cy, INK)
    pix.p(head_cx + 2, head_cy, INK)
    pix.hline(head_cx - 1, head_cy + 3, 3, INK)
    if f in (0, 1, 2, 3):
        pix.rect(head_cx - 14, y_counter - 14, 6, 8, CREAM)
        pix.rect(head_cx - 16, y_counter - 8, 5, 3, SKIN)
        pix.rect(head_cx + 8, y_counter - 12, 4, 8, CREAM)
        pix.rect(head_cx + 8, y_counter - 5, 4, 3, SKIN)
    else:
        pix.rect(head_cx - 16, y_counter - 18, 6, 8, CREAM)
        pix.rect(head_cx - 20, y_counter - 14, 6, 5, SKIN)
        pix.rect(head_cx - 22, y_counter - 16, 8, 8, CREAM_SH)
        pix.outline(head_cx - 22, y_counter - 16, 8, 8, WALL_DK)
        pix.rect(head_cx + 8, y_counter - 12, 4, 8, CREAM)
        pix.rect(head_cx + 8, y_counter - 5, 4, 3, SKIN)


def draw_jukebox(pix, x, y_bottom):
    h = 110
    y = y_bottom - h
    w = 52
    pix.bevel(x, y, w, h, MENU_BG, CHROME, INK)
    pix.rect(x + 2, y + 2, w - 4, 28, CAR)
    pix.dith(x + 4, y + 4, w - 8, 24, NEON_P, NEON_C, "bayer")
    pix.circle(x + w // 2, y + 16, 10, MENU_BG)
    pix.circle(x + w // 2, y + 16, 8, GLOW)
    pix.circle(x + w // 2, y + 16, 4, GOLD_LT)
    pix.p(x + w // 2 - 2, y + 14, WHITE)
    pix.rect(x + 4, y + 32, w - 8, 10, RED)
    text(pix, x + 8, y + 34, "TUNES", CREAM, font="3")
    for r in range(3):
        for c in range(4):
            col = GOLD_LT if (r + c) % 2 == 0 else NEON_C
            pix.rect(x + 6 + c * 10, y + 46 + r * 8, 8, 6, col)
            pix.p(x + 7 + c * 10, y + 47 + r * 8, CREAM)
    pix.rect(x + 6, y + 72, w - 12, 28, CHROME_DK)
    for gy in range(y + 74, y + 98, 3):
        pix.hline(x + 8, gy, w - 16, CAR)
    pix.rect(x - 2, y_bottom - 6, w + 4, 6, CHROME)
    pix.hline(x - 2, y_bottom - 6, w + 4, CHROME_HI)
    pix.vline(x + 1, y + 6, h - 16, NEON_P)
    pix.vline(x + w - 2, y + 6, h - 16, NEON_C)
    neon_halo(pix, x + w // 2, y + 16, 24, 18, NEON_P2, max_amt=6, y0=y, y1=y + 40, x0=x - 6, x1=x + w + 6)


def draw_trash(pix, x, y_bottom):
    h = 32
    y = y_bottom - h
    pix.vgrad(x, y, 18, h, [CHROME, CHROME_DK, CAR], transition=4)
    pix.outline(x, y, 18, h, INK)
    pix.rect(x + 2, y + 8, 14, h - 12, CAR)
    pix.rect(x + 1, y, 16, 8, CHROME)
    pix.hline(x + 1, y, 16, CHROME_HI)
    pix.rect(x + 5, y + 2, 8, 5, CAR)
    pix.p(x + 8, y + 4, CHROME)


def draw_planter(pix, x, y_bottom):
    h = 28
    y = y_bottom - h
    pix.vgrad(x, y + 10, 24, h - 10, [COUNTER, COUNTER_DK], transition=3)
    pix.outline(x, y + 10, 24, h - 10, INK)
    # foliage
    pix.circle(x + 8, y + 8, 8, (36, 90, 48))
    pix.circle(x + 16, y + 6, 7, (28, 70, 40))
    pix.circle(x + 12, y + 10, 6, (48, 110, 58))
    pix.p(x + 10, y + 2, (80, 140, 70))


def draw_napkin_stand(pix, x, y_bottom):
    # chrome stand with napkin dispenser, sits on the floor at an edge
    y = y_bottom - 40
    pix.rect(x + 6, y + 16, 5, y_bottom - (y + 16) - 2, CHROME_DK)
    pix.vline(x + 7, y + 16, y_bottom - (y + 16) - 2, CHROME)
    pix.rect(x, y_bottom - 4, 18, 4, CHROME)
    pix.bevel(x, y, 18, 18, CHROME, CHROME_HI, CHROME_DK)
    pix.rect(x + 3, y + 4, 12, 10, CREAM)
    pix.hline(x + 3, y + 4, 12, WHITE)
    pix.rect(x + 4, y + 6, 10, 2, CREAM_SH)


# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------

def draw_far(rng):
    pix = Pix(W_FAR, H, SKY0)
    draw_night_scene(pix, W_FAR, H, rng, xoff=0)
    return pix


def draw_checkered_floor(pix, w, rng):
    pix.rect(0, FLOOR_TOP, w, H - FLOOR_TOP, TILE_W)
    rows = [300, 308, 318, 330, 344, 360]
    vp = w // 2
    for ri in range(len(rows) - 1):
        y0, y1 = rows[ri], rows[ri + 1]
        t = ri / max(1, (len(rows) - 2))
        tw = int(16 + t * 10)
        offset = vp % tw
        col = 0
        x = -offset
        while x < w:
            even = ((col + ri) % 2 == 0)
            if even:
                pix.rect(x, y0, tw, y1 - y0, TILE_W)
                pix.hline(x + 1, y0 + 1, max(1, tw - 3), TILE_W_HI)
            else:
                pix.rect(x, y0, tw, y1 - y0, TILE_R)
                pix.hline(x + 1, y0 + 1, max(1, tw - 3), TILE_R_HI)
            x += tw
            col += 1
        pix.hline(0, y0, w, COUNTER_DK)
        x = -offset
        while x < w:
            pix.vline(x, y0, y1 - y0, COUNTER_DK)
            x += tw
    for _ in range(50):
        pix.p(rng.randint(0, w - 1), rng.randint(FLOOR_TOP + 2, H - 2), COUNTER_DK)


def apply_interior_lighting(pix):
    """Pink/teal neon halos, warm menu glow, pendant pools. Floor glow only y=300-314."""
    # Soft neon halo — dithered fringe, no rectangular bumper
    cx, cy = NEON_X + 84, NEON_Y + 14
    radial_glow(pix, cx, cy, 86, 24, [NEON_P2, (232, 176, 192)], y0=0, y1=62)
    radial_glow(pix, cx + 40, cy + 2, 36, 16, [NEON_C2], y0=0, y1=52)
    # redraw the sign so the core glow doesn't chew the lettering
    draw_neon_sign(pix, NEON_X, NEON_Y, on=True)
    # 1px tube glow + a short soft fringe above/below (not a solid bar)
    pix.outline(NEON_X, NEON_Y, 168, 28, NEON_P)
    neon_halo(pix, cx, NEON_Y - 1, 86, 7, NEON_P3, max_amt=8, y0=max(0, NEON_Y - 8), y1=NEON_Y + 2)
    neon_halo(pix, cx, NEON_Y + 28, 90, 8, NEON_P2, max_amt=8, y0=NEON_Y + 26, y1=NEON_Y + 40)
    neon_halo(pix, cx + 40, NEON_Y + 28, 36, 6, NEON_C2, max_amt=6, y0=NEON_Y + 26, y1=NEON_Y + 38)
    # structured floor reflections, back strip only
    floor_reflect(pix, cx, FLOOR_TOP, 70, TILE_NEON_P, rows=7)
    floor_reflect(pix, cx + 36, FLOOR_TOP + 1, 36, TILE_NEON_C, rows=5)
    # OPEN sign small halo
    radial_glow(pix, OPEN_X + 18, OPEN_Y + 8, 22, 14, [NEON_C3, NEON_C2], y0=OPEN_Y - 8, y1=OPEN_Y + 28)
    # warm menu-board glow onto backsplash + counter top
    mcx = MENU_X + 150
    mcy = MENU_Y + 50
    radial_glow(pix, mcx, mcy + 36, 140, 34, [WALL_WARM, (228, 198, 150)], y0=128, y1=210)
    neon_halo(pix, mcx, 200, 150, 10, COUNTER_HI, max_amt=10, y0=196, y1=214)
    floor_reflect(pix, mcx, FLOOR_TOP, 80, TILE_WARM, rows=6)
    # pendant warm pools on tables / back floor
    for px in (80, 200, 330, 460, 700, 860):
        floor_reflect(pix, px, FLOOR_TOP, 22, TILE_WARM, rows=5)
    # ceiling wash only over the open cream ceiling (not over the menu boards)
    for px in (80, 200, 330, 460):
        neon_halo(pix, px, 22, 16, 10, WALL_WARM, max_amt=7, y0=0, y1=36)


def draw_mid(rng):
    pix = Pix(W_MID, H, None)
    pix.vgrad(0, 0, W_MID, FLOOR_TOP, [WALL_HI, WALL, WALL_SH], transition=8)
    pix.rect(0, 220, W_MID, FLOOR_TOP - 220, WALL_SH)
    pix.hline(0, 220, W_MID, RED_DK)
    pix.rect(0, 220, W_MID, 6, RED)
    pix.hline(0, 220, W_MID, RED_HI)
    pix.rect(0, FLOOR_TOP - 5, W_MID, 5, WALL_DK)
    pix.hline(0, FLOOR_TOP - 5, W_MID, CREAM_SH)

    pix.rect(0, 0, W_MID, 22, WALL_DK)
    pix.dith(0, 0, W_MID, 22, WALL_DK, COUNTER_DK, "h")
    pix.hline(0, 22, W_MID, WALL_SH)
    for tx in range(0, W_MID, 40):
        pix.vline(tx, 0, 22, COUNTER_DK)
    for px in (80, 200, 330, 460, 700, 860):
        draw_pendant(pix, px, 0, length=20 + (px % 16) // 4)

    windows = [
        (16, 48, 120, 150, 2, True, False),
        (148, 48, 150, 150, 3, False, True),
        (310, 48, 160, 150, 3, False, True),
    ]
    for wx, wy, ww, wh, panes, fill, refl in windows:
        draw_window_frame(pix, wx, wy, ww, wh, panes=panes, fill_night=fill, rng=rng, neon_reflect=refl)

    for tx in range(20, 560, 16):
        pix.outline(tx, 200, 14, 14, WALL_DK)
        pix.p(tx + 7, 207, CREAM_SH)

    draw_neon_sign(pix, NEON_X, NEON_Y, on=True)
    pix.vline(NEON_X + 10, 0, NEON_Y, CHROME_DK)
    pix.vline(NEON_X + 158, 0, NEON_Y, CHROME_DK)
    draw_open_sign(pix, OPEN_X, OPEN_Y, on=True)

    pix.bevel(8, 140, 40, FLOOR_TOP - 140, RED_DK, RED, INK)
    pix.rect(12, 146, 32, FLOOR_TOP - 154, RED)
    pix.vgrad(16, 150, 24, 70, [SKY1, LOT], transition=6)
    pix.outline(16, 150, 24, 70, INK)
    pix.rect(18, 260, 20, 8, CHROME)
    text(pix, 14, 128, "IN", CREAM, font="3")

    draw_booth_seat(pix, 150, 200, 70, 70)
    draw_table(pix, 168, 248, 44)
    draw_booth_seat(pix, 220, 200, 70, 70)
    draw_fry_box(pix, 176, 236)
    draw_cup(pix, 190, 236)
    draw_tray(pix, 200, 243, 22)
    draw_ketchup(pix, 172, 234, mustard=False)
    draw_ketchup(pix, 180, 234, mustard=True)

    draw_booth_seat(pix, 310, 200, 70, 70)
    draw_table(pix, 328, 248, 44)
    draw_booth_seat(pix, 380, 200, 70, 70)
    draw_fry_box(pix, 336, 236)
    draw_fry_box(pix, 348, 236)
    draw_cup(pix, 362, 234)
    draw_tray(pix, 330, 243, 26)
    draw_shako(pix, 350, 224)
    pix.bevel(372, 240, 12, 8, CHROME, CHROME_HI, CHROME_DK)
    pix.rect(374, 242, 8, 4, CREAM)

    draw_booth_seat(pix, 20, 210, 56, 60)
    draw_table(pix, 36, 254, 36)
    draw_booth_seat(pix, 80, 210, 56, 60)
    draw_fry_box(pix, 42, 242)
    draw_cup(pix, 56, 242)

    rows1 = [("combo", "COMBO A", "5.99"), ("combo", "COMBO B", "6.49"), ("burger", "BIG BURGER", "4.79")]
    rows2 = [("burger", "BURGER", "3.49"), ("fries", "FRIES", "1.99"), ("fries", "LG FRIES", "2.49")]
    rows3 = [("drink", "SODA", "1.49"), ("drink", "SHAKE", "2.29"), ("fries", "PIE", "1.79")]
    draw_menu_board(pix, MENU_X, MENU_Y, "COMBOS", rows1, glow=True)
    draw_menu_board(pix, MENU_X + 96, MENU_Y, "MAINS", rows2, glow=True)
    draw_menu_board(pix, MENU_X + 192, MENU_Y, "SIDES", rows3, glow=True)
    pix.bevel(MENU_X - 8, MENU_Y - 14, 300, 14, CHROME_DK, CHROME, CAR)
    pix.rect(MENU_X - 6, MENU_Y - 12, 296, 8, MENU_BG)
    text(pix, MENU_X + 70, MENU_Y - 11, "BURGER SPOT MENU", GLOW, font="3")

    # tile backsplash
    pix.rect(548, 136, 300, 64, RED_DK)
    for ty in range(136, 200, 16):
        for tx in range(548, 848, 16):
            col = CREAM if ((tx + ty) // 16) % 2 == 0 else RED
            pix.rect(tx, ty, 15, 15, col)
            pix.outline(tx, ty, 15, 15, RED_DK)
            if col == CREAM:
                pix.p(tx + 2, ty + 2, CREAM_LT)
            else:
                pix.p(tx + 2, ty + 2, RED_HI)
    pix.hline(548, 136, 300, CHROME)
    pix.hline(548, 199, 300, CHROME_DK)

    draw_counter(pix, 560, 200, 390)
    pix.bevel(620, 236, 70, 28, RED_DK, RED, INK)
    pix.rect(624, 240, 62, 20, NAVY_DK)
    pix.hline(624, 240, 62, NAVY_LT)
    text(pix, 630, 242, "BURGER", GOLD_LT, font="3")
    text(pix, 636, 250, "SPOT", GOLD, font="3")
    pix.outline(620, 236, 70, 28, CHROME)

    draw_register(pix, 580, 176)
    draw_register(pix, 670, 176)
    pix.bevel(578, 164, 50, 10, RED, RED_HI, RED_DK)
    text(pix, 582, 166, "ORDER", CREAM, font="3")
    pix.bevel(668, 164, 50, 10, RED, RED_HI, RED_DK)
    text(pix, 674, 166, "PICK UP", CREAM, font="3")
    draw_soda_fountain(pix, FOUNTAIN_X, 164)

    pix.bevel(880, 186, 50, 16, CREAM, CREAM_LT, CREAM_SH)
    draw_ketchup(pix, 886, 178, False)
    draw_ketchup(pix, 896, 178, True)
    draw_ketchup(pix, 906, 178, False)
    pix.bevel(916, 180, 12, 10, CHROME, CHROME_HI, CHROME_DK)
    pix.rect(918, 182, 8, 6, CREAM)
    for i in range(4):
        pix.vline(926, 176 + i, 6, CHROME_HI if i % 2 == 0 else RED)

    pix.rect(786, 186, 12, 14, RED)
    pix.rect(787, 184, 10, 3, CHROME)
    pix.rect(787, 181, 10, 3, CHROME)
    pix.rect(802, 186, 12, 14, RED_DK)
    pix.rect(803, 184, 10, 3, CHROME)
    pix.rect(850, 176, 20, 16, CREAM_SH)
    pix.outline(850, 176, 20, 16, WALL_DK)
    pix.rect(852, 178, 16, 4, WALL_SH)
    pix.rect(872, 176, 16, 16, CREAM)
    pix.outline(872, 176, 16, 16, WALL_DK)
    pix.rect(640, 188, 6, 12, CHROME)
    pix.p(643, 186, CHROME_HI)
    pix.rect(636, 190, 5, 6, CREAM)
    pix.circle(720, 192, 6, CHROME)
    pix.circle(720, 192, 4, GOLD_LT)
    pix.p(718, 190, GOLD)

    draw_trash(pix, 544, FLOOR_TOP)
    pix.rect(760, 230, 36, 10, INK)
    pix.outline(760, 230, 36, 10, CHROME_DK)
    text(pix, 766, 232, "TRAYS", CHROME, font="3")

    pix.bevel(900, 48, 44, 60, CREAM, CREAM_LT, CREAM_SH)
    icon_burger(pix, 914, 58)
    text(pix, 908, 80, "EAT", RED, font="3")
    text(pix, 906, 88, "UP", RED, font="3")

    pix.bevel(476, 48, 26, 14, CHROME_DK, CHROME, INK)
    pix.circle(489, 55, 5, CAR)
    pix.circle(489, 55, 2, CHROME)
    pix.circle(510, 58, 14, CHROME)
    pix.circle(510, 58, 12, CREAM)
    pix.line(510, 58, 510, 50, INK)
    pix.line(510, 58, 518, 60, INK)
    pix.p(510, 58, RED)
    pix.bevel(476, 70, 72, 14, RED, RED_HI, RED_DK)
    text(pix, 480, 73, "GAME NIGHT", CREAM, font="3")
    draw_jukebox(pix, 478, FLOOR_TOP)

    draw_checkered_floor(pix, W_MID, rng)
    pix.dith(560, FLOOR_TOP, 390, 3, COUNTER_DK, INK, "h")
    pix.dith(20, FLOOR_TOP, 120, 2, INK, TILE_R, "h")
    pix.rect(8, FLOOR_TOP, 44, 5, RED_DK)
    pix.dith(8, FLOOR_TOP, 44, 5, RED, RED_DK, "checker")

    apply_interior_lighting(pix)
    return pix


def draw_anim(frame):
    pix = Pix(W_MID, H, None)
    f = frame & 7
    buzz_sets = [set(), {2}, {8}, set(), {5}, {1, 9}, set(), {2, 10}]
    on = f not in (7,)
    # halo first, then letters, so the glow never overwrites the tube
    if on:
        cols = [NEON_P3, NEON_P2] if f % 2 == 0 else [NEON_P2, NEON_P]
        if f not in (1, 5):
            radial_glow(pix, NEON_X + 84, NEON_Y + 14, 88, 22, cols, y0=0, y1=55)
        else:
            neon_halo(pix, NEON_X + 84, NEON_Y + 14, 70, 18, NEON_P2, max_amt=5, y0=0, y1=50)
    draw_neon_sign(pix, NEON_X, NEON_Y, on=on, buzz_mask=buzz_sets[f])
    if on:
        pix.outline(NEON_X - 1, NEON_Y - 1, 170, 30, NEON_P2 if f % 2 == 0 else NEON_P)
    draw_open_sign(pix, OPEN_X, OPEN_Y, on=f not in (3, 6))

    glow = f not in (7,)
    rows1 = [("combo", "COMBO A", "5.99"), ("combo", "COMBO B", "6.49"), ("burger", "BIG BURGER", "4.79")]
    rows2 = [("burger", "BURGER", "3.49"), ("fries", "FRIES", "1.99"), ("fries", "LG FRIES", "2.49")]
    rows3 = [("drink", "SODA", "1.49"), ("drink", "SHAKE", "2.29"), ("fries", "PIE", "1.79")]
    draw_menu_board(pix, MENU_X, MENU_Y, "COMBOS", rows1, glow=glow or f == 1)
    draw_menu_board(pix, MENU_X + 96, MENU_Y, "MAINS", rows2, glow=f not in (6, 7))
    draw_menu_board(pix, MENU_X + 192, MENU_Y, "SIDES", rows3, glow=f in (0, 1, 2, 4, 5))
    if f in (1, 2):
        pix.dith(MENU_X - 4, MENU_Y - 4, 292, 3, GLOW_HOT, GLOW, "h")

    # booth kids
    draw_kid_booth(pix, 186, 248, facing=1, frame=f, hair="dark", action="eat")
    draw_kid_booth(pix, 246, 248, facing=-1, frame=f, hair="blond", action="drink")
    draw_kid_booth(pix, 346, 248, facing=1, frame=(f + 3) & 7, hair="brown", action="eat")
    draw_kid_booth(pix, 406, 248, facing=-1, frame=(f + 1) & 7, hair="dark", action="talk")
    draw_kid_booth(pix, 50, 254, facing=1, frame=f, hair="brown", action="drink")
    # standing kids: pickup line + jukebox
    draw_kid_standing(pix, 700, FLOOR_TOP, facing=-1, frame=f, hair="brown", pose="wait")
    draw_kid_standing(pix, 454, FLOOR_TOP, facing=1, frame=(f + 4) & 7, hair="dark", pose="jukebox")
    draw_cashier(pix, 610, 200, frame=f, facing=-1)

    drop_y = 190 + (f % 4) * 4
    pix.p(FOUNTAIN_X + 16, drop_y, NEON_C)
    pix.p(FOUNTAIN_X + 16, drop_y + 1, GLASS_HI)
    if f in (1, 5):
        pix.dith(200, 108, 28, 18, GOLD, GLASS, "bayer")
    if f == 2:
        pix.dith(168, 118, 20, 14, GOLD_LT, GLASS, "bayer")
    return pix


def draw_near():
    pix = Pix(W_NEAR, H, None)
    # LEFT: booth end-cap peeking into the centered view (near crop starts at 240)
    # body lives in the margin; the chrome-piped end cap sits just inside x=240
    by, bh = 198, 92
    pix.vgrad(196, by, 48, bh, [RED, RED_DK, (80, 16, 18)], transition=3)
    pix.hline(196, by, 48, RED_HI)
    cap_x = 244
    pix.vgrad(cap_x, by, 22, bh, [RED_HI, RED, RED_DK], transition=3)
    pix.hline(cap_x, by, 22, RED_SPEC)
    pix.vline(cap_x, by, bh, CHROME_HI)
    pix.vline(cap_x + 1, by, bh, CHROME)
    pix.vline(cap_x + 21, by, bh, RED_DK)
    pix.vline(cap_x + 3, by + 4, bh - 10, RED_SPEC)
    # seat cushion coming toward camera
    pix.vgrad(200, by + bh - 6, 72, 16, [RED_HI, RED, RED_DK], transition=3)
    pix.hline(200, by + bh - 6, 72, RED_SPEC)
    # chrome feet
    pix.rect(210, by + bh + 10, 6, FLOOR_TOP - (by + bh + 10), CHROME_DK)
    pix.rect(cap_x + 6, by + bh + 10, 6, FLOOR_TOP - (by + bh + 10), CHROME_DK)
    pix.rect(206, FLOOR_TOP - 4, 14, 4, CHROME)
    pix.rect(cap_x + 2, FLOOR_TOP - 4, 14, 4, CHROME)
    # planter just inside the peek
    draw_planter(pix, 232, FLOOR_TOP)

    # RIGHT: trash + napkin stand peeking from x=840+
    draw_trash(pix, 848, FLOOR_TOP)
    draw_napkin_stand(pix, 876, FLOOR_TOP)
    # a little chrome railing stump
    pix.rect(840, 250, 6, FLOOR_TOP - 250, CHROME_DK)
    pix.vline(841, 250, FLOOR_TOP - 250, CHROME)
    pix.rect(840, 246, 14, 6, CHROME)
    pix.hline(840, 246, 14, CHROME_HI)
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
    print("near action-box leaks", validate_near(near))

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

    for n in ["far.png", "mid.png", "near.png"] + [f"anim_{i}.png" for i in range(8)] + ["preview.png", "preview@2x.png"]:
        print(info(DIR / n, Image.open(DIR / n)))


if __name__ == "__main__":
    main()
