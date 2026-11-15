#!/usr/bin/env python3
"""Band Wars — locker-room stage generator.

640x360 far, 960x360 mid/anim, preview 640x360 + preview@2x.
Seeded RNG, 32-color palette, nearest-neighbor only, no anti-aliasing.
Fighters' feet at y=320; floor band y=300..360 stays uncluttered.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

SEED = 19910320
DIR = Path(__file__).resolve().parent
W_FAR, W_MID, H = 640, 960, 360
FLOOR_TOP = 300

# 32-color palette
# Official JMHS school colors, copied verbatim from
# art/characters/tools/pxart/palette.py (and the football stage).
NAVY      = (0x17, 0x30, 0x5F)  # #17305F
NAVY_DK   = (0x0C, 0x17, 0x34)  # #0C1734
NAVY_LT   = (0x3A, 0x5A, 0x9C)  # #3A5A9C
GOLD      = (0xD4, 0xA0, 0x17)  # #D4A017
GOLD_DK   = (0x7A, 0x54, 0x10)  # #7A5410
WHITE     = (0xF6, 0xF2, 0xEA)  # #F6F2EA
WHITE_SH  = (0xB9, 0xB3, 0xA6)  # #B9B3A6
BRASS, BRASS_DK = GOLD, GOLD_DK  # metal / braid / tuba
RED       = (168, 36, 38)        # extinguisher + red marker only
CEIL_DK   = (58, 64, 54)
CEIL      = (90, 96, 82)
CEIL_LT   = (120, 126, 108)
WALL      = (166, 158, 134)
WALL_SH   = (130, 122, 100)
WALL_DK   = (96, 90, 74)
WALL_HI   = (192, 184, 158)
FLUOR     = (236, 240, 210)
FLUOR_HI  = (255, 255, 236)
FLUOR_DIM = CEIL_LT
LOK       = (76, 96, 56)
LOK_LT    = (108, 128, 80)
LOK_DK    = (46, 62, 36)
LOK_SH    = (28, 40, 24)
LOK_HI    = (140, 158, 108)
METAL     = (168, 172, 150)
WOOD      = (150, 104, 58)
WOOD_DK   = (104, 70, 38)
RUST      = WOOD_DK
TILE      = (190, 172, 134)
TILE_DK   = (150, 134, 102)
GROUT     = (118, 106, 84)
CASE      = (38, 36, 40)
CASE_HI   = (78, 76, 84)
INK       = (32, 32, 36)
SKIN      = (210, 166, 126)

PALETTE = [
    CEIL_DK, CEIL, CEIL_LT, WALL, WALL_SH, WALL_DK, WALL_HI,
    FLUOR, FLUOR_HI, LOK, LOK_LT, LOK_DK, LOK_SH, LOK_HI,
    METAL, NAVY, NAVY_DK, NAVY_LT, GOLD, GOLD_DK, WHITE, WHITE_SH,
    WOOD, WOOD_DK, TILE, TILE_DK, GROUT, CASE, CASE_HI, INK, SKIN, RED,
]

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
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                d = x * x + y * y
                if fill and d <= r * r:
                    self.p(cx + x, cy + y, c)
                elif not fill and abs(d - r * r) <= r:
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
                    use = (i & 1) == 0 and (j & 1) == 0
                else:
                    use = True
                self.p(i, j, c1 if use else c2)


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
    pal_img = Image.new("P", (1, 1))
    flat = []
    for c in PALETTE:
        flat.extend(c)
    flat.extend([0, 0, 0] * (256 - len(PALETTE)))
    pal_img.putpalette(flat)
    if opaque:
        return img.convert("RGB").quantize(palette=pal_img, dither=Image.Dither.NONE).convert("RGB")
    alpha = img.split()[-1].point(lambda a: 255 if a >= 128 else 0)
    rgb = img.convert("RGB").quantize(palette=pal_img, dither=Image.Dither.NONE).convert("RGBA")
    rgb.putalpha(alpha)
    return rgb


# ---------------------------------------------------------------------------
# Props
# ---------------------------------------------------------------------------

def draw_shako(pix, x, y, plume=True, small=False):
    """Navy shako, gold badge, gold/white plume — matches the fighter kit."""
    if small:
        pix.bevel(x, y + 2, 8, 8, NAVY, NAVY_LT, NAVY_DK)
        pix.rect(x, y + 9, 8, 2, INK)
        pix.hline(x, y + 8, 8, GOLD)
        pix.rect(x + 2, y + 4, 3, 3, GOLD)
        pix.p(x + 3, y + 5, WHITE)
        if plume:
            pix.vline(x + 3, y - 4, 6, GOLD)
            pix.vline(x + 4, y - 5, 7, GOLD)
            pix.p(x + 4, y - 5, WHITE)
        return
    pix.bevel(x, y + 3, 12, 12, NAVY, NAVY_LT, NAVY_DK)
    pix.rect(x + 1, y + 4, 10, 1, NAVY_LT)
    pix.hline(x, y + 13, 12, GOLD)
    pix.rect(x, y + 14, 13, 3, INK)  # visor
    pix.rect(x + 1, y + 14, 11, 1, CASE_HI)
    pix.rect(x + 4, y + 6, 4, 5, GOLD)
    pix.p(x + 5, y + 7, GOLD_DK)
    pix.p(x + 6, y + 8, WHITE)
    pix.rect(x + 5, y + 1, 3, 3, INK)  # top button
    if plume:
        pix.vline(x + 5, y - 7, 9, GOLD)
        pix.vline(x + 6, y - 8, 11, GOLD)
        pix.vline(x + 7, y - 7, 9, GOLD_DK)
        pix.p(x + 6, y - 8, WHITE)
        pix.p(x + 5, y - 6, WHITE)


def draw_jacket(pix, x, y, w=16, h=22):
    """Hanging marching jacket, top-left at hanger neck."""
    pix.rect(x + w // 2 - 1, y - 3, 2, 4, METAL)  # hanger hook
    pix.hline(x + 1, y, w - 2, METAL)
    pix.rect(x, y + 1, w, h, NAVY)
    pix.vline(x, y + 1, h, NAVY_DK)
    pix.vline(x + w - 1, y + 1, h, NAVY_DK)
    pix.hline(x, y + h, w, NAVY_DK)
    # gold braid / buttons + white baldric
    pix.vline(x + 2, y + 3, h - 5, GOLD)
    pix.vline(x + w - 3, y + 3, h - 5, GOLD)
    pix.vline(x + w // 2, y + 2, h - 4, WHITE)
    for by in range(y + 5, y + h - 2, 4):
        pix.p(x + w // 2 + 1, by, GOLD)
        pix.p(x + w // 2 - 1, by, GOLD_DK)
    # shoulders
    pix.hline(x, y + 1, w, NAVY_DK)
    pix.rect(x + 1, y + 2, w - 2, 2, NAVY_LT)
    pix.p(x + 1, y + 3, GOLD)


def draw_pants_fold(pix, x, y):
    pix.rect(x, y, 12, 6, WHITE)
    pix.hline(x, y, 12, WHITE_SH)
    pix.hline(x, y + 5, 12, WHITE_SH)
    pix.vline(x + 6, y, 6, WHITE_SH)
    pix.rect(x + 1, y + 1, 2, 4, WHITE_SH)


def draw_locker(pix, x, y, w, h, rng, state="closed", number="12"):
    """Draw one metal locker. state: closed, open, ajar."""
    # cabinet body always
    pix.bevel(x, y, w, h, LOK_DK, LOK, LOK_SH)
    pix.rect(x + 1, y + 1, w - 2, h - 2, LOK_DK)

    rust_n = rng.randint(0, 3)
    for _ in range(rust_n):
        rx = x + rng.randint(1, max(2, w - 3))
        ry = y + h - rng.randint(2, 10)
        pix.p(rx, ry, RUST)
        if rng.random() < 0.5:
            pix.p(rx + 1, ry, RUST)

    if state == "closed":
        pix.bevel(x + 1, y + 1, w - 2, h - 2, LOK, LOK_HI, LOK_DK)
        # stamped panel
        pix.outline(x + 4, y + 14, w - 8, h - 28, LOK_DK)
        pix.p(x + 4, y + 14, LOK_HI)
        # louvers top
        for ly in range(y + 4, y + 12, 2):
            pix.hline(x + 5, ly, w - 10, LOK_DK)
            pix.hline(x + 5, ly + 1, w - 10, LOK_SH)
        # bottom vents
        for ly in range(y + h - 10, y + h - 4, 2):
            pix.hline(x + 5, ly, w - 10, LOK_DK)
        # number plate (3x5 digits so they stay readable)
        digits = number[-2:] if len(number) >= 2 else number.rjust(2, "0")
        plx, ply = x + w // 2 - 6, y + 16
        pix.bevel(plx, ply, 12, 9, METAL, WHITE, LOK_SH)
        pix.rect(plx + 1, ply + 1, 10, 7, WHITE_SH)
        text(pix, plx + 2, ply + 2, digits, INK, font="3")
        # handle (right side)
        hx, hy = x + w - 6, y + h // 2 - 2
        pix.rect(hx, hy, 3, 8, BRASS_DK)
        pix.rect(hx, hy, 2, 7, BRASS)
        pix.p(hx + 1, hy + 1, FLUOR)
        if rng.random() < 0.45:
            # combo lock
            pix.rect(hx - 5, hy + 1, 5, 6, CASE)
            pix.rect(hx - 4, hy + 2, 3, 4, METAL)
            pix.p(hx - 3, hy + 3, INK)
        # scratches
        if rng.random() < 0.55:
            sx = x + rng.randint(6, w - 8)
            sy = y + rng.randint(24, h - 16)
            pix.line(sx, sy, sx + rng.randint(3, 8), sy + rng.randint(-2, 2), LOK_SH)
        if rng.random() < 0.3:
            # sticker rectangle (generic)
            sx = x + rng.randint(6, max(7, w - 12))
            sy = y + rng.randint(30, h - 30)
            col = rng.choice([NAVY, WHITE, GOLD, WALL_HI])
            pix.rect(sx, sy, 6, 4, col)
            pix.outline(sx, sy, 6, 4, INK)
        return

    # open / ajar: dark interior
    pix.rect(x + 2, y + 2, w - 4, h - 4, CASE)
    pix.vline(x + 2, y + 2, h - 4, INK)
    pix.hline(x + 2, y + 2, w - 4, INK)
    # back wall of locker slightly lighter
    pix.rect(x + 5, y + 5, w - 10, h - 10, LOK_SH)
    # shelf
    sy = y + 28
    pix.rect(x + 3, sy, w - 6, 3, CASE_HI)
    pix.hline(x + 3, sy, w - 6, METAL)
    # hook + hanging jacket — keep these bold and readable
    draw_jacket(pix, x + 5, y + 38, w=max(12, w - 8), h=min(34, h - 52))
    if state == "open" or rng.random() < 0.7:
        draw_shako(pix, x + w // 2 - 6, y + 8, plume=True)
    else:
        draw_pants_fold(pix, x + 5, y + 10)
    # shoes at the bottom of the locker
    pix.rect(x + 5, y + h - 16, 8, 5, INK)
    pix.rect(x + 14, y + h - 16, 8, 5, INK)
    # door swung open to the right, foreshortened face
    door_w = 7 if state == "ajar" else 11
    dx = x + w - 1
    pix.bevel(dx, y + 1, door_w, h - 2, LOK, LOK_HI, LOK_DK)
    pix.vline(dx, y + 1, h - 2, LOK_SH)
    pix.outline(dx + 2, y + 16, max(3, door_w - 4), h - 32, LOK_DK)
    for ly in range(y + 4, y + 12, 2):
        pix.hline(dx + 1, ly, max(1, door_w - 3), LOK_DK)
    pix.rect(dx + door_w - 3, y + h // 2 - 2, 2, 8, BRASS)
    pix.p(dx + door_w - 3, y + h // 2 - 1, BRASS_DK)


def draw_bench(pix, x, y, w, slats=4):
    """Wooden bench; y is the top of the seat; legs go down to FLOOR_TOP."""
    seat_h = 7
    pix.rect(x, y, w, seat_h, WOOD)
    pix.hline(x, y, w, WOOD)
    # highlight on front edge? top is lit
    pix.hline(x, y, w, BRASS_DK)  # slightly lighter wood edge, reuse
    pix.hline(x, y, w, TILE)  # closest light wood we have... actually TILE is floor. Use a wood highlight via dither
    pix.dith(x, y, w, 2, WOOD, TILE, "h")
    pix.hline(x, y + seat_h - 1, w, WOOD_DK)
    # slat gaps
    gap = w // slats
    for i in range(1, slats):
        pix.vline(x + i * gap, y + 1, seat_h - 2, WOOD_DK)
    # iron legs
    for lx in (x + 6, x + w - 10):
        pix.rect(lx, y + seat_h, 5, FLOOR_TOP - (y + seat_h), CASE)
        pix.rect(lx + 1, y + seat_h, 3, FLOOR_TOP - (y + seat_h), CASE_HI)
        pix.rect(lx - 2, FLOOR_TOP - 3, 9, 3, CASE)
    # shadow under bench on the back of floor (just at the junction, not into fight zone)
    pix.hline(x + 2, FLOOR_TOP, w - 4, GROUT)


def draw_case(pix, x, y, w, h, kind="rect"):
    """Instrument case sitting on something; bottom at y+h."""
    pix.bevel(x, y, w, h, CASE, CASE_HI, INK)
    pix.rect(x + 2, y + 2, w - 4, h - 4, CASE)
    # edge highlight
    pix.hline(x + 2, y + 2, w - 4, CASE_HI)
    # latches
    for lx in (x + 4, x + w // 2 - 2, x + w - 8):
        if lx > x and lx + 5 < x + w:
            pix.rect(lx, y + h // 2 - 2, 5, 4, BRASS_DK)
            pix.rect(lx + 1, y + h // 2 - 1, 3, 2, BRASS)
    if kind == "snare":
        # slightly rounded look via corner bites
        pix.p(x, y, (0, 0, 0, 0))
        pix.p(x + w - 1, y, (0, 0, 0, 0))
        pix.outline(x + 3, y + 3, w - 6, h - 6, CASE_HI)
        # center badge
        pix.circle(x + w // 2, y + h // 2, 3, METAL)
        pix.p(x + w // 2, y + h // 2, BRASS)
    elif kind == "trombone":
        pix.rect(x + 4, y + 3, w - 8, 3, CASE_HI)
        pix.rect(x + w - 12, y + 2, 8, h - 4, CASE_HI)
    elif kind == "tuba":
        pix.circle(x + w // 2, y + h // 2, min(w, h) // 3, CASE_HI)
        pix.circle(x + w // 2, y + h // 2, min(w, h) // 3 - 2, CASE)
    elif kind == "sax":
        # curved silhouette along the right
        for i in range(h):
            flare = 0 if i < h // 2 else (i - h // 2) // 3
            pix.p(x + w - 1 + flare, y + i, CASE)
        pix.outline(x, y, w, h, INK)
    # small handle
    pix.rect(x + w // 2 - 4, y - 3, 8, 3, CASE_HI)
    pix.hline(x + w // 2 - 3, y - 3, 6, METAL)
    # tiny label
    pix.rect(x + 3, y + h - 8, 9, 4, WHITE_SH)
    pix.rect(x + 4, y + h - 7, 7, 2, WHITE)


def draw_sousaphone(pix, x, y):
    """Upright sousaphone, bell up. (x,y) is top-left of bell box. ~70x110."""
    # bell
    pix.circle(x + 28, y + 28, 26, BRASS_DK)
    pix.circle(x + 28, y + 28, 24, BRASS)
    pix.circle(x + 28, y + 28, 16, BRASS_DK)
    pix.circle(x + 28, y + 26, 13, INK)  # opening
    pix.circle(x + 28, y + 26, 11, CASE)
    # inner rim highlight
    for a in range(-10, 8):
        pix.p(x + 28 + a, y + 16, BRASS)
    pix.p(x + 18, y + 20, FLUOR)
    # body coils
    pix.circle(x + 30, y + 70, 16, BRASS_DK)
    pix.circle(x + 30, y + 70, 14, BRASS)
    pix.circle(x + 30, y + 70, 9, BRASS_DK)
    pix.circle(x + 30, y + 70, 7, WALL_DK)  # hole shows wall-ish
    pix.circle(x + 22, y + 78, 12, BRASS)
    pix.circle(x + 22, y + 78, 8, BRASS_DK)
    pix.circle(x + 22, y + 78, 5, WALL_SH)
    # vertical tubes
    pix.rect(x + 50, y + 40, 5, 50, BRASS)
    pix.rect(x + 51, y + 40, 2, 50, BRASS_DK)
    pix.rect(x + 8, y + 50, 4, 36, BRASS_DK)
    pix.rect(x + 9, y + 50, 2, 36, BRASS)
    # lead pipe + mouthpiece to the right
    pix.rect(x + 52, y + 86, 16, 3, BRASS)
    pix.rect(x + 66, y + 84, 5, 7, BRASS_DK)
    pix.rect(x + 67, y + 85, 3, 5, WHITE_SH)
    # valve block
    pix.rect(x + 34, y + 88, 16, 10, BRASS_DK)
    for i in range(3):
        pix.rect(x + 36 + i * 5, y + 84, 3, 6, METAL)
        pix.p(x + 37 + i * 5, y + 84, WHITE_SH)
    # stand / floor contact at y=300
    by = 300
    pix.rect(x + 18, 292, 20, 8, CASE)
    pix.rect(x + 16, 297, 24, 3, CASE_HI)
    pix.hline(x + 14, 299, 28, INK)


def draw_whiteboard(pix, x, y, w=130, h=96):
    pix.bevel(x, y, w, h, CASE_HI, METAL, INK)
    pix.rect(x + 3, y + 3, w - 6, h - 14, WHITE)
    # slight board tint / wear
    rng = random.Random(44)
    for _ in range(40):
        pix.p(x + rng.randint(4, w - 6), y + rng.randint(4, h - 16), WHITE_SH)
    # field outline (drill chart)
    fx, fy, fw, fh = x + 10, y + 22, w - 20, h - 44
    pix.outline(fx, fy, fw, fh, INK)
    # hashes
    for i in range(1, 8):
        hx = fx + i * fw // 8
        pix.vline(hx, fy + 3, 4, WHITE_SH)
        pix.vline(hx, fy + fh - 7, 4, WHITE_SH)
        if i in (2, 4, 6):
            pix.vline(hx, fy + fh // 2 - 3, 6, WHITE_SH)
    # yard-ish mid line
    pix.vline(fx + fw // 2, fy, fh, WHITE_SH)
    # formation dots — a curve / company front + an arc
    dots = []
    for i in range(13):
        dots.append((fx + 8 + i * (fw - 16) // 12, fy + fh - 10))
    for i in range(9):
        # arc
        t = i / 8
        dx = int((fw - 24) * t) + 8
        dy = int(18 * (1 - (2 * t - 1) ** 2))  # parabola
        dots.append((fx + dx, fy + 14 + (fh // 2 - dy)))
    for i in range(7):
        dots.append((fx + 16 + i * 12, fy + fh // 2 + 8))
    for dx, dy in dots:
        pix.p(dx, dy, INK)
        pix.p(dx + 1, dy, INK)
        pix.p(dx, dy + 1, INK)
    # title
    text(pix, x + 8, y + 6, "GAME NIGHT", NAVY, 1)
    text(pix, x + w - 48, y + 6, "SET 14", INK, 1)
    # caption lives inside the board, above the tray
    text(pix, x + 8, y + h - 22, "WARMUP 6:30", INK, font="3")
    text(pix, x + w - 44, y + h - 22, "GO BAND!", NAVY, font="3")
    # tray
    pix.rect(x + 2, y + h - 12, w - 4, 9, METAL)
    pix.hline(x + 2, y + h - 12, w - 4, WHITE_SH)
    pix.rect(x + 8, y + h - 10, 3, 7, INK)
    pix.rect(x + 13, y + h - 10, 3, 7, RED)
    pix.rect(x + 18, y + h - 10, 3, 7, LOK)
    pix.rect(x + 23, y + h - 10, 3, 7, BRASS_DK)
    pix.rect(x + w - 30, y + h - 10, 18, 6, CASE)
    pix.rect(x + w - 29, y + h - 9, 16, 4, WHITE_SH)


def draw_uniform_rack(pix, x, y, w=90):
    """Rolling wardrobe rack with hanging uniforms. Top bar at y, wheels at floor."""
    # uprights
    pix.rect(x + 4, y, 3, FLOOR_TOP - y, METAL)
    pix.rect(x + w - 7, y, 3, FLOOR_TOP - y, METAL)
    pix.rect(x + 5, y, 1, FLOOR_TOP - y, WHITE_SH)
    # top bar
    pix.rect(x + 2, y, w - 4, 3, METAL)
    pix.hline(x + 2, y, w - 4, WHITE_SH)
    # wheels
    for wx in (x + 3, x + w - 10):
        pix.circle(wx + 3, FLOOR_TOP - 4, 4, CASE)
        pix.circle(wx + 3, FLOOR_TOP - 4, 2, CASE_HI)
    # hanging uniforms
    n = 6
    for i in range(n):
        ux = x + 8 + i * ((w - 20) // n)
        draw_jacket(pix, ux, y + 8, w=12, h=26 + (i % 3) * 2)
        # pants below jacket
        ph = 18
        pix.rect(ux + 1, y + 36, 10, ph, WHITE if i % 2 == 0 else NAVY)
        pix.vline(ux + 5, y + 36, ph, GOLD if i % 2 == 0 else GOLD)
        if i % 2 == 0:
            pix.vline(ux + 2, y + 38, ph - 4, BRASS_DK)
        # shako on a shelf above? or perched
        if i in (0, 2, 4):
            draw_shako(pix, ux, y - 18, plume=True, small=True)
    # bottom rail
    pix.rect(x + 4, FLOOR_TOP - 12, w - 8, 3, METAL)


def draw_fountain(pix, x, y):
    """Water fountain; basin bottom near y, feet at FLOOR_TOP. x,y top-left of back plate."""
    pix.bevel(x, y, 22, FLOOR_TOP - y, METAL, WHITE_SH, CASE)
    pix.rect(x + 2, y + 2, 18, 16, CASE_HI)
    # basin
    pix.rect(x + 3, y + 14, 16, 5, METAL)
    pix.rect(x + 4, y + 15, 14, 3, CEIL_LT)  # water-ish, reuse
    pix.dith(x + 6, y + 16, 8, 2, CEIL_LT, FLUOR_DIM, "checker")
    # spout + button
    pix.rect(x + 10, y + 8, 3, 7, CASE)
    pix.p(x + 11, y + 8, METAL)
    pix.rect(x + 15, y + 11, 4, 3, BRASS)
    # drain
    pix.p(x + 10, y + 16, INK)
    pix.p(x + 11, y + 16, INK)


def draw_trash(pix, x, y_bottom):
    h = 36
    y = y_bottom - h
    pix.bevel(x, y, 20, h, CASE_HI, METAL, INK)
    pix.rect(x + 2, y + 2, 16, h - 4, CASE)
    pix.rect(x + 1, y, 18, 5, METAL)  # rim
    pix.dith(x + 3, y + 8, 14, h - 14, CASE, CASE_HI, "bayer")
    # a bit of paper peeking
    pix.rect(x + 6, y + 1, 5, 3, WHITE)
    pix.p(x + 8, y, WHITE)


def draw_extinguisher(pix, x, y):
    pix.rect(x + 3, y, 8, 22, RED)
    pix.bevel(x + 3, y, 8, 22, RED, RED, INK)
    pix.rect(x + 4, y + 1, 6, 4, METAL)
    pix.rect(x + 6, y - 4, 2, 5, CASE)
    pix.rect(x + 7, y - 5, 6, 2, CASE_HI)  # hose
    pix.rect(x + 11, y - 4, 2, 6, CASE)
    pix.p(x + 5, y + 12, BRASS)
    pix.rect(x + 2, y + 20, 10, 3, INK)


def draw_clock(pix, cx, cy, r=14, hour=19, minute=40):
    pix.circle(cx, cy, r, CASE)
    pix.circle(cx, cy, r - 2, WHITE)
    pix.circle(cx, cy, r - 2, WHITE, fill=False)
    # ticks
    pix.p(cx, cy - r + 4, INK)
    pix.p(cx, cy + r - 4, INK)
    pix.p(cx - r + 4, cy, INK)
    pix.p(cx + r - 4, cy, INK)
    # hands — 7:40-ish
    pix.line(cx, cy, cx + 3, cy + 6, INK)  # hour
    pix.line(cx, cy, cx - 8, cy + 2, INK)  # minute
    pix.p(cx, cy, BRASS)


def draw_bulletin(pix, x, y, w=44, h=50):
    pix.bevel(x, y, w, h, WOOD, WOOD, WOOD_DK)
    pix.rect(x + 2, y + 2, w - 4, h - 4, RUST)  # cork, reuse rust-brown
    # flyers
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
            text(pix, x + fx + 2, y + fy + 5, label, INK if col != NAVY else WHITE, font="3")
        if sub:
            text(pix, x + fx + 2, y + fy + 11, sub, INK if col != NAVY else GOLD, font="3")


def draw_backpack(pix, x, y, color=NAVY):
    pix.bevel(x, y, 12, 16, color, NAVY_LT if color == NAVY else WALL_HI, NAVY_DK if color == NAVY else WOOD_DK)
    pix.rect(x + 3, y + 4, 6, 7, color)
    pix.outline(x + 3, y + 4, 6, 7, INK)
    # straps
    pix.vline(x + 2, y - 2, 6, CASE)
    pix.vline(x + 9, y - 2, 6, CASE)
    pix.rect(x + 4, y + 12, 4, 2, BRASS_DK)


def draw_shoes(pix, x, y):
    # pair of black marching shoes
    for i, ox in enumerate((0, 11)):
        pix.rect(x + ox, y, 10, 5, INK)
        pix.rect(x + ox + 1, y + 1, 8, 2, CASE)
        pix.p(x + ox + (8 if i == 0 else 1), y, CASE_HI)  # toe highlight


def draw_drumsticks(pix, x, y):
    pix.line(x, y, x + 16, y + 2, WOOD)
    pix.line(x, y + 1, x + 16, y + 3, WOOD_DK)
    pix.line(x + 2, y + 3, x + 18, y + 1, WOOD)
    pix.line(x + 2, y + 4, x + 18, y + 2, WOOD_DK)
    pix.p(x + 16, y + 2, WHITE)
    pix.p(x + 18, y + 1, WHITE)


def draw_megaphone(pix, x, y):
    # cone pointing right
    for i in range(14):
        half = 1 + i // 2
        pix.vline(x + i, y + 6 - half, half * 2, NAVY if i > 2 else CASE)
    pix.rect(x - 4, y + 4, 6, 5, CASE)
    pix.rect(x - 3, y + 5, 4, 3, CASE_HI)
    pix.p(x + 12, y + 6, BRASS)


def draw_door(pix, x, y, w=44, h=170, lit=True):
    pix.bevel(x, y, w, h, WOOD, TILE, WOOD_DK)
    pix.rect(x + 2, y + 2, w - 4, h - 4, WOOD)
    # upper glass pane — shows the lit hallway
    gw, gh = w - 14, 48
    gx, gy = x + 7, y + 8
    pix.bevel(gx - 1, gy - 1, gw + 2, gh + 2, WOOD_DK, WOOD, WOOD_DK, fill=False)
    if lit:
        pix.rect(gx, gy, gw, gh, FLUOR_DIM)
        pix.dith(gx, gy, gw, gh, FLUOR, FLUOR_DIM, "v")
        # distant hall lockers visible through the glass
        for i in range(3):
            pix.rect(gx + 4 + i * 8, gy + 18, 7, gh - 22, LOK)
            pix.rect(gx + 5 + i * 8, gy + 20, 5, gh - 26, LOK_LT)
        pix.rect(gx, gy, gw, 6, CEIL)
        pix.rect(gx + gw // 2 - 6, gy + 2, 12, 3, FLUOR_HI)
        pix.outline(gx, gy, gw, gh, INK)
    # lower recessed panel
    pix.bevel(x + 7, y + 64, w - 14, h - 88, WOOD, WOOD, WOOD_DK)
    pix.outline(x + 9, y + 66, w - 18, h - 92, WOOD_DK)
    pix.hline(x + 10, y + 67, w - 20, TILE)
    # handle
    pix.rect(x + w - 13, y + 110, 3, 14, BRASS_DK)
    pix.rect(x + w - 16, y + 114, 8, 4, BRASS)
    pix.p(x + w - 13, y + 115, FLUOR)
    # kick plate
    pix.rect(x + 2, y + h - 14, w - 4, 10, METAL)
    pix.hline(x + 2, y + h - 14, w - 4, WHITE_SH)


def draw_shower_door(pix, x, y, w=40, h=170):
    # tiled jamb + frosted door, steam comes from anim
    pix.rect(x, y, w, h, WALL_SH)
    pix.bevel(x, y, w, h, METAL, WHITE_SH, CASE)
    pix.rect(x + 3, y + 3, w - 6, h - 6, CEIL_LT)
    pix.dith(x + 3, y + 3, w - 6, h - 6, CEIL_LT, METAL, "checker")
    pix.outline(x + 3, y + 3, w - 6, h - 6, CASE)
    # handle
    pix.rect(x + w - 10, y + h // 2, 5, 3, CASE)
    # wet floor mark just at threshold (on floor junction)
    pix.dith(x + 4, FLOOR_TOP, w - 8, 2, GROUT, TILE_DK, "checker")


def draw_ceiling_grid(pix, x, y, w, h, origin=0):
    pix.rect(x, y, w, h, CEIL)
    # tiles ~32x12
    for ty in range(y, y + h, 12):
        pix.hline(x, ty, w, CEIL_DK)
        pix.hline(x, ty + 1, w, CEIL_LT)
    for tx in range(x + (origin % 32), x + w, 32):
        pix.vline(tx, y, h, CEIL_DK)
    # stains
    rng = random.Random(7 + origin)
    for _ in range(w // 40):
        sx = x + rng.randint(0, max(1, w - 4))
        sy = y + rng.randint(0, max(1, h - 3))
        pix.p(sx, sy, CEIL_DK)
        pix.p(sx + 1, sy, CEIL_DK)


def draw_fixture(pix, x, y, w=96, state="on"):
    """Fluorescent 2-tube fixture. state: on, dim, surge, off."""
    pix.bevel(x, y, w, 14, CASE_HI, METAL, CASE)
    pix.rect(x + 2, y + 2, w - 4, 10, CASE)
    # two tubes
    colors = {
        "on": (FLUOR, FLUOR_HI),
        "dim": (FLUOR_DIM, FLUOR),
        "surge": (FLUOR_HI, FLUOR_HI),
        "off": (METAL, CEIL_LT),
    }
    c1, c2 = colors[state]
    for i, ty in enumerate((y + 3, y + 7)):
        pix.rect(x + 6, ty, w - 12, 3, c1)
        pix.hline(x + 6, ty, w - 12, c2 if state != "off" else METAL)
        pix.p(x + 6, ty + 1, WHITE if state != "off" else CASE)
        pix.p(x + w - 7, ty + 1, WHITE if state != "off" else CASE)
        # end caps
        pix.rect(x + 4, ty, 2, 3, METAL)
        pix.rect(x + w - 6, ty, 2, 3, METAL)
    if state == "surge":
        # extra glow around fixture
        pix.dith(x - 2, y - 2, w + 4, 2, FLUOR, FLUOR_HI, "checker")
        pix.dith(x - 2, y + 14, w + 4, 2, FLUOR, CEIL_LT, "checker")
    if state == "off":
        # one tube with a tiny spark
        pix.p(x + w // 2, y + 4, FLUOR)
        pix.p(x + w // 2 + 1, y + 4, FLUOR_HI)


def draw_kid_standing(pix, x, y_feet, facing=1, frame=0, hair="dark", pose="talk"):
    """~70px tall band kid. x is center, y_feet is ground contact (~300)."""
    # body proportions
    head_r = 6
    head_cy = y_feet - 58
    head_cx = x
    # slight bounce / shift
    if pose == "fidget":
        head_cx += (1, 0, -1, 0)[frame]
        head_cy += (0, 1, 0, 0)[frame]
    # legs
    leg_c = WHITE
    stripe = BRASS
    ly = y_feet - 24
    off = 0
    if pose == "fidget":
        off = (1, 0, -1, 0)[frame]
    pix.rect(head_cx - 7 + off, ly, 6, 22, leg_c)
    pix.rect(head_cx + 1, ly, 6, 22, leg_c)
    pix.vline(head_cx - 6 + off, ly + 1, 18, stripe)
    pix.vline(head_cx + 4, ly + 1, 18, stripe)
    # shoes
    shx = 1 if facing > 0 else -3
    pix.rect(head_cx - 8 + off + (0 if facing > 0 else -1), y_feet - 3, 8, 4, INK)
    pix.rect(head_cx + 1 + shx, y_feet - 3, 8, 4, INK)
    # torso jacket
    pix.rect(head_cx - 9, y_feet - 46, 18, 23, NAVY)
    pix.vline(head_cx - 9, y_feet - 46, 23, NAVY_DK)
    pix.vline(head_cx + 8, y_feet - 46, 23, NAVY_DK)
    pix.vline(head_cx - 7, y_feet - 44, 18, GOLD)
    pix.vline(head_cx + 6, y_feet - 44, 18, GOLD)
    pix.vline(head_cx, y_feet - 44, 20, WHITE)
    for by in range(y_feet - 42, y_feet - 28, 5):
        pix.p(head_cx, by, BRASS)
    # arms
    arm_y = y_feet - 44
    if pose == "talk":
        # far arm
        pix.rect(head_cx - 12, arm_y, 4, 16, NAVY)
        pix.rect(head_cx - 12, arm_y + 16, 4, 4, SKIN)
        # gesturing arm
        if frame % 2 == 0:
            pix.rect(head_cx + 9, arm_y, 4, 10, NAVY)
            pix.rect(head_cx + 11, arm_y - 2, 4, 4, SKIN)
            pix.rect(head_cx + 14, arm_y - 6, 4, 5, SKIN)  # hand up
        else:
            pix.rect(head_cx + 9, arm_y, 4, 12, NAVY)
            pix.rect(head_cx + 10, arm_y + 12, 4, 4, SKIN)
            pix.rect(head_cx + 13, arm_y + 8, 5, 4, SKIN)
    elif pose == "reach":
        pix.rect(head_cx - 12, arm_y, 4, 14, NAVY)
        pix.rect(head_cx - 12, arm_y + 14, 4, 4, SKIN)
        # reaching into locker (up-right)
        lift = (0, 1, 2, 1)[frame]
        pix.rect(head_cx + 8, arm_y - 4 - lift, 4, 12, NAVY)
        pix.rect(head_cx + 10, arm_y - 8 - lift, 4, 5, SKIN)
    else:
        pix.rect(head_cx - 12, arm_y, 4, 16, NAVY)
        pix.rect(head_cx - 12, arm_y + 16, 4, 4, SKIN)
        pix.rect(head_cx + 8, arm_y, 4, 16, NAVY)
        pix.rect(head_cx + 8, arm_y + 16, 4, 4, SKIN)
    # neck
    pix.rect(head_cx - 2, head_cy + 5, 4, 4, SKIN)
    # head
    pix.circle(head_cx, head_cy, head_r, SKIN)
    # hair
    hc = INK if hair == "dark" else (WOOD_DK if hair == "brown" else RUST)
    pix.rect(head_cx - 6, head_cy - 6, 12, 5, hc)
    pix.p(head_cx - 6, head_cy - 1, hc)
    pix.p(head_cx + 6, head_cy - 1, hc)
    if hair == "brown":
        pix.p(head_cx, head_cy - 7, hc)
    # face
    eye_x = head_cx + (2 if facing > 0 else -2)
    pix.p(eye_x, head_cy, INK)
    pix.p(head_cx - (2 if facing > 0 else -2), head_cy, INK)
    mouth_y = head_cy + 3
    if pose == "talk" and frame % 2 == 0:
        pix.p(head_cx, mouth_y, INK)
        pix.p(head_cx + 1, mouth_y, INK)
    else:
        pix.hline(head_cx - 1, mouth_y, 3, INK)
    # no shako (they're chatting after pulling gear) — a shako sits nearby on mid


def draw_kid_sitting(pix, x, y_seat, facing=-1, frame=0, hair="brown"):
    """Kid sitting on a bench. y_seat is bench top. Head above."""
    head_cx = x
    head_cy = y_seat - 28
    if frame in (1, 2):
        head_cy += 1
    # legs hanging
    pix.rect(head_cx - 6, y_seat + 6, 5, 16, WHITE)
    pix.rect(head_cx + 2, y_seat + 6, 5, 16, WHITE)
    pix.vline(head_cx - 5, y_seat + 7, 12, BRASS)
    pix.vline(head_cx + 5, y_seat + 7, 12, BRASS)
    pix.rect(head_cx - 7, y_seat + 20, 8, 4, INK)
    pix.rect(head_cx + 2, y_seat + 20, 8, 4, INK)
    # thighs
    pix.rect(head_cx - 8, y_seat + 1, 16, 6, WHITE)
    # torso
    pix.rect(head_cx - 8, y_seat - 18, 16, 20, NAVY)
    pix.vline(head_cx - 6, y_seat - 16, 14, GOLD)
    pix.vline(head_cx + 5, y_seat - 16, 14, GOLD)
    pix.vline(head_cx, y_seat - 16, 16, WHITE)
    # arms — one holds drumsticks that twirl slightly
    pix.rect(head_cx - 11, y_seat - 16, 4, 12, NAVY)
    pix.rect(head_cx - 11, y_seat - 4, 4, 3, SKIN)
    if frame % 2 == 0:
        pix.rect(head_cx + 8, y_seat - 16, 4, 10, NAVY)
        pix.rect(head_cx + 9, y_seat - 6, 4, 3, SKIN)
        pix.line(head_cx + 12, y_seat - 6, head_cx + 20, y_seat - 14, WOOD)
    else:
        pix.rect(head_cx + 8, y_seat - 14, 4, 8, NAVY)
        pix.rect(head_cx + 10, y_seat - 8, 4, 3, SKIN)
        pix.line(head_cx + 13, y_seat - 8, head_cx + 22, y_seat - 4, WOOD)
    # neck + head
    pix.rect(head_cx - 2, head_cy + 5, 4, 4, SKIN)
    pix.circle(head_cx, head_cy, 6, SKIN)
    hc = WOOD_DK if hair == "brown" else INK
    pix.rect(head_cx - 6, head_cy - 6, 12, 5, hc)
    pix.p(head_cx - 6, head_cy, hc)
    pix.p(head_cx + 5, head_cy - 1, hc)
    pix.p(head_cx + (2 if facing > 0 else -2), head_cy, INK)
    pix.p(head_cx - (2 if facing > 0 else -2), head_cy, INK)
    pix.hline(head_cx - 1, head_cy + 3, 3, INK)



def draw_pennants(pix, x0, x1, y):
    """High-school string of maroon/gold/white pennants."""
    pix.hline(x0, y, x1 - x0, CASE)
    pix.hline(x0, y + 1, x1 - x0, CASE_HI)
    colors = [NAVY, GOLD, WHITE, NAVY_DK, GOLD_DK, WHITE_SH]
    i = 0
    x = x0 + 2
    while x + 12 < x1:
        col = colors[i % len(colors)]
        shade = NAVY_DK if col in (NAVY, NAVY_DK) else (GOLD_DK if col in (GOLD, GOLD_DK) else WHITE_SH)
        for dy in range(14):
            half = dy // 3
            pix.hline(x + half, y + 2 + dy, max(1, 12 - half * 2), col if dy < 12 else shade)
        i += 1
        x += 14


def draw_poster(pix, x, y, w, h, bg, title, sub=""):
    pix.bevel(x, y, w, h, bg, WHITE if bg != WHITE else WHITE_SH, INK)
    pix.outline(x, y, w, h, INK)
    # tape corners
    pix.p(x + 1, y + 1, WHITE_SH)
    pix.p(x + w - 2, y + 1, WHITE_SH)
    if title:
        text(pix, x + 3, y + 4, title, INK if bg != NAVY else WHITE, font="3")
    if sub:
        text(pix, x + 3, y + 12, sub, NAVY if bg != NAVY else GOLD, font="3")


def draw_locker_tops(pix, x, w, rng):
    """Shelf of shakos, boxes, and bottles sitting on a locker bank."""
    pix.bevel(x - 1, 134, w + 2, 7, WOOD, TILE, WOOD_DK)
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
            # trophy
            pix.rect(sx + 3, 128, 6, 6, BRASS_DK)
            pix.rect(sx + 4, 118, 4, 10, BRASS)
            pix.p(sx + 5, 117, BRASS)
            pix.hline(sx + 2, 124, 8, BRASS_DK)


# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------

# Flicker fixture in mid coordinates (also drawn on far for the ones further back)
FLICKER_X, FLICKER_Y, FLICKER_W = 452, 4, 100


def draw_far(rng):
    """640x360 opaque — ceiling, upper wall, windows, banner, clock, hallway."""
    pix = Pix(W_FAR, H, CEIL_DK)
    # ceiling occupies top 56 px, slightly receding color
    draw_ceiling_grid(pix, 0, 0, W_FAR, 56, origin=8)
    # far (receded) fixtures
    for fx in (40, 200, 360, 520):
        draw_fixture(pix, fx, 8, 88, state="on")
    # dimmer ambient under ceiling
    pix.dith(0, 50, W_FAR, 6, CEIL, WALL_SH, "h")

    # upper wall
    pix.rect(0, 56, W_FAR, FLOOR_TOP - 56, WALL)
    # vertical wear / corners
    pix.rect(0, 56, 8, FLOOR_TOP - 56, WALL_SH)
    pix.rect(W_FAR - 8, 56, 8, FLOOR_TOP - 56, WALL_SH)
    # crown molding
    pix.hline(0, 56, W_FAR, WALL_DK)
    pix.hline(0, 57, W_FAR, WALL_HI)
    pix.hline(0, 58, W_FAR, WALL_DK)

    # wall stains / dirt near top and bottom of visible band
    for _ in range(80):
        wx = rng.randint(10, W_FAR - 10)
        wy = rng.randint(70, 140)
        pix.p(wx, wy, WALL_SH if rng.random() < 0.7 else WALL_HI)

    # high windows — night outside (3 panes)
    for i, wx in enumerate((70, 270, 470)):
        pix.bevel(wx, 70, 90, 50, CASE, METAL, INK)
        # three vertical panes
        for p in range(3):
            px = wx + 4 + p * 28
            pix.rect(px, 74, 26, 42, INK)
            # night sky gradient-ish via dither bands
            pix.rect(px, 74, 26, 20, INK)
            pix.dith(px, 90, 26, 16, INK, CASE, "h")
            pix.dith(px, 104, 26, 12, CASE, CASE_HI, "bayer")
            # a star
            if i != 1:
                pix.p(px + 8 + i * 3, 80, WHITE)
            # sodium glow from a lot light
            if i == 1:
                pix.dith(px + 6, 100, 14, 14, BRASS_DK, CASE, "bayer")
        # muntins
        pix.rect(wx + 3, 74, 84, 2, METAL)
        pix.rect(wx + 3, 112, 84, 2, METAL)

    # banner sits in the clear wall between window 1 (70-160) and window 2 (270-360)
    pix.bevel(168, 78, 94, 22, NAVY, NAVY_LT, NAVY_DK)
    pix.hline(168, 78, 94, WHITE_SH)
    text(pix, 176, 84, "BAND ROOM", GOLD, 1, shadow=NAVY_DK)

    # clock
    draw_clock(pix, 400, 92, 16)

    # HVAC vent
    pix.bevel(560, 80, 48, 16, METAL, WHITE_SH, CASE)
    for vy in range(84, 94, 3):
        pix.hline(564, vy, 40, CASE)

    # pipes along ceiling-wall corner
    pix.hline(0, 62, W_FAR, CASE_HI)
    pix.hline(0, 63, W_FAR, CASE)
    pix.hline(0, 64, W_FAR, INK)
    # hangers
    for hx in range(30, W_FAR, 80):
        pix.vline(hx, 56, 8, CASE)

    # bulletin far-right upper
    draw_bulletin(pix, 575, 110, 48, 54)

    # a bit of lower wall (will be mostly covered by mid lockers) — paint it so gaps work
    pix.rect(0, 200, W_FAR, FLOOR_TOP - 200, WALL_SH)
    # baseboard
    pix.rect(0, FLOOR_TOP - 6, W_FAR, 6, WALL_DK)
    pix.hline(0, FLOOR_TOP - 6, W_FAR, WALL_HI)

    # hallway through where mid will cut a door (approx preview-center-right)
    # far is 640; mid crop starts at mid x=160, so far x = mid x - 160
    # mid door will be around mid x=590-636 → far x=430-476
    pix.rect(430, 128, 50, FLOOR_TOP - 128, WALL_DK)
    # lit hallway
    pix.rect(436, 134, 38, FLOOR_TOP - 134, WOOD_DK)
    pix.dith(436, 134, 38, 40, FLUOR_DIM, WOOD, "v")
    # far lockers in hall (tiny)
    for i in range(3):
        pix.rect(440 + i * 10, 200, 9, 80, LOK_DK)
        pix.rect(441 + i * 10, 202, 7, 76, LOK)
    pix.rect(436, 134, 38, 8, CEIL)  # hall ceiling
    pix.rect(448, 136, 16, 4, FLUOR)  # distant light

    # floor (only visible in gaps; mid covers this)
    pix.rect(0, FLOOR_TOP, W_FAR, H - FLOOR_TOP, TILE_DK)
    return pix


def draw_floor(pix, w, rng):
    """Perspective tile floor, y=300..360, kept readable."""
    pix.rect(0, FLOOR_TOP, w, H - FLOOR_TOP, TILE)
    # horizontal grout — spacing grows toward camera
    rows = [300, 307, 316, 327, 340, 360]
    # vertical lines with slight flare from a vanishing point
    vp = w // 2
    # paint row by row
    for ri in range(len(rows) - 1):
        y0, y1 = rows[ri], rows[ri + 1]
        # tile width grows
        t = ri / (len(rows) - 2)
        tw = int(18 + t * 10)
        # shift so columns stay coherent
        offset = int((vp % tw))
        col = 0
        x = -offset
        while x < w:
            # alternate
            even = ((col + ri) % 2 == 0)
            color = TILE if even else TILE_DK
            pix.rect(x, y0, tw, y1 - y0, color)
            # subtle highlight on top of each tile (lit from ceiling)
            if even:
                pix.hline(x + 1, y0 + 1, max(1, tw - 3), TILE if not even else (WALL_HI if ri == 0 else TILE))
            x += tw
            col += 1
        pix.hline(0, y0, w, GROUT)
    pix.hline(0, H - 1, w, GROUT)

    # redraw vertical grout more cleanly
    for ri in range(len(rows) - 1):
        y0, y1 = rows[ri], rows[ri + 1]
        t = ri / (len(rows) - 2)
        tw = int(18 + t * 10)
        offset = int((vp % tw))
        x = -offset
        while x < w:
            pix.vline(x, y0, y1 - y0, GROUT)
            x += tw

    # light reflections (lighter tiles) under fixtures — sharp, not blurry
    for lx in (80, 260, 500, 720, 880):
        # a short run of lighter pixels near mid-depth of floor
        pix.dith(lx, 308, 70, 6, WALL_HI, TILE, "h")

    # scuffs / wear, mostly traffic paths but not noisy in the fight band
    for _ in range(90):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(FLOOR_TOP + 2, H - 2)
        pix.p(sx, sy, GROUT if rng.random() < 0.6 else TILE_DK)

    # stronger wear near furniture line
    for _ in range(40):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(FLOOR_TOP, FLOOR_TOP + 6)
        pix.p(sx, sy, GROUT)


def draw_mid(rng):
    pix = Pix(W_MID, H, None)  # transparent

    # Opaque walls on the parallax margins (and a lower wall band)
    # Left margin 0..170 and right 790..960 get full wall+ceiling so panning doesn't hole out.
    for x0, x1 in ((0, 175), (785, 960)):
        draw_ceiling_grid(pix, x0, 0, x1 - x0, 52, origin=x0)
        pix.rect(x0, 52, x1 - x0, FLOOR_TOP - 52, WALL)
        pix.hline(x0, 52, x1 - x0, WALL_DK)
        pix.hline(x0, 53, x1 - x0, WALL_HI)

    # A thin ceiling strip across the whole mid (closer fixtures)
    draw_ceiling_grid(pix, 0, 0, W_MID, 28, origin=0)
    # closer fixtures (one is the dying flicker light)
    draw_fixture(pix, 80, 3, 90, "on")
    draw_fixture(pix, 260, 3, 90, "on")
    draw_fixture(pix, FLICKER_X, FLICKER_Y, FLICKER_W, "on")
    draw_fixture(pix, 680, 3, 90, "on")
    draw_fixture(pix, 850, 3, 80, "dim")

    # Lower wall behind lockers (opaque, y=140..300) across full width
    pix.rect(0, 140, W_MID, FLOOR_TOP - 140, WALL)
    # a slightly darker wainscot / lower wall
    pix.rect(0, 260, W_MID, FLOOR_TOP - 260, WALL_SH)
    pix.hline(0, 260, W_MID, WALL_DK)
    # baseboard
    pix.rect(0, FLOOR_TOP - 5, W_MID, 5, WALL_DK)
    pix.hline(0, FLOOR_TOP - 5, W_MID, WALL_HI)

    # wall between ceiling gap (y=28..140) is left TRANSPARENT in the center so far shows
    # (banner, clock, windows). Fill nothing there for x=175..785.

    # columns / pilasters
    for cx in (170, 400, 640, 790):
        pix.rect(cx, 28, 10, FLOOR_TOP - 28, WALL_SH)
        pix.vline(cx, 28, FLOOR_TOP - 28, WALL_HI)
        pix.vline(cx + 9, 28, FLOOR_TOP - 28, WALL_DK)
        pix.rect(cx - 2, 28, 14, 8, WALL_DK)  # capital
        pix.rect(cx - 2, FLOOR_TOP - 10, 14, 10, WALL_DK)

    # --- LEFT: shower / restroom door + stacked cases ---
    draw_shower_door(pix, 16, 130, 42, FLOOR_TOP - 130)
    # tile jamb hint
    pix.rect(14, 130, 3, FLOOR_TOP - 130, TILE_DK)
    text(pix, 18, 118, "SHOWERS", WALL_DK, 1)

    # cases stacked left
    draw_case(pix, 64, 250, 46, 50, "tuba")
    draw_case(pix, 70, 210, 40, 40, "snare")
    draw_case(pix, 108, 268, 58, 32, "trombone")
    draw_case(pix, 112, 236, 28, 32, "sax")

    # pennants strung in the mid layer so they parallax against the far wall
    draw_pennants(pix, 185, 395, 72)
    draw_pennants(pix, 650, 820, 72)

    # wall posters in the mid gap above / beside furniture
    draw_poster(pix, 404, 88, 36, 44, WHITE, "DRILL", "CHART")
    # GO BAND hangs on the wall between the door and the rack, under the pennants
    draw_poster(pix, 602, 86, 36, 40, NAVY, "GO", "BAND")
    draw_poster(pix, 844, 90, 40, 36, WALL_HI, "NO", "FOOD")

    # --- LEFT-CENTER locker bank ---
    # lockers from x=180 to x=398, height 160, top at y=140
    locker_w = 28
    states_left = ["closed", "closed", "open", "closed", "ajar", "closed", "closed", "open"]
    nums_left = ["12", "13", "14", "15", "16", "17", "18", "19"]
    for i, (st, num) in enumerate(zip(states_left, nums_left)):
        lx = 180 + i * locker_w
        draw_locker(pix, lx, 140, locker_w, 160, random.Random(100 + i), st, num)
    draw_locker_tops(pix, 180, 8 * locker_w, random.Random(33))

    # backpacks hanging on some closed lockers
    draw_backpack(pix, 186, 250, NAVY)
    draw_backpack(pix, 328, 248, WOOD_DK)

    # --- CENTER: whiteboard + hall door ---
    draw_whiteboard(pix, 410, 148, 132, 100)
    pix.rect(408, 146, 136, 2, WALL_DK)

    draw_door(pix, 552, 130, 46, FLOOR_TOP - 130, lit=True)
    # exit plate above door
    pix.bevel(556, 112, 38, 14, LOK_DK, LOK_LT, LOK_SH)
    text(pix, 562, 115, "EXIT", LOK_LT, font="3")
    pix.rect(558, 113, 34, 1, LOK_LT)

    # extinguisher to the right of the door, still visible
    draw_extinguisher(pix, 600, 230)

    # floor mat at the door (stays in the y=300-306 strip)
    pix.rect(548, FLOOR_TOP, 54, 5, NAVY_DK)
    pix.dith(548, FLOOR_TOP, 54, 5, NAVY, NAVY_DK, "checker")

    # --- uniform rack IN FRAME, in the former empty gap ---
    draw_uniform_rack(pix, 612, 168, 80)

    # --- RIGHT-CENTER lockers + sousaphone ---
    states_r = ["closed", "open", "closed", "ajar", "closed"]
    nums_r = ["20", "21", "22", "23", "24"]
    for i, (st, num) in enumerate(zip(states_r, nums_r)):
        lx = 700 + i * locker_w
        draw_locker(pix, lx, 140, locker_w, 160, random.Random(200 + i), st, num)
    draw_locker_tops(pix, 700, 5 * locker_w, random.Random(44))

    # sousaphone in front of right lockers, fully inside the preview crop (160-800)
    draw_sousaphone(pix, 718, 188)

    # --- RIGHT margin: more cases, a director corner (desk, megaphone) ---
    draw_case(pix, 900, 246, 50, 54, "tuba")
    draw_case(pix, 910, 214, 36, 32, "snare")
    draw_case(pix, 868, 272, 36, 28, "rect")

    # small desk
    pix.bevel(880, 250, 50, 8, WOOD, TILE, WOOD_DK)
    pix.rect(884, 258, 6, FLOOR_TOP - 258, WOOD_DK)
    pix.rect(920, 258, 6, FLOOR_TOP - 258, WOOD_DK)
    pix.rect(886, 244, 16, 8, WHITE)
    pix.rect(888, 246, 12, 5, WHITE_SH)
    pix.rect(906, 246, 10, 5, WHITE)
    pix.rect(908, 247, 6, 2, INK)
    pix.rect(908, 250, 5, 1, INK)
    draw_megaphone(pix, 918, 236)
    pix.rect(884, 247, 6, 3, METAL)
    pix.p(884, 248, WHITE_SH)

    # water fountain pulled into the preview's left edge (preview starts at mid x=160)
    draw_fountain(pix, 158, 250)
    draw_trash(pix, 126, FLOOR_TOP)

    # --- benches: split the left bench so a kid can stand at locker 14 ---
    draw_bench(pix, 178, 276, 54, slats=2)   # left sliver
    draw_bench(pix, 290, 276, 108, slats=3)  # gap at the open locker
    draw_bench(pix, 700, 276, 130, slats=4)

    # props on benches
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
    # right bench props
    draw_shako(pix, 780, 252, plume=True)
    draw_drumsticks(pix, 740, 272)
    pix.hline(760, 274, 10, GOLD)
    pix.hline(761, 273, 8, GOLD)
    pix.p(770, 274, WHITE)

    # lost metronome on desk already; a tuner? skip

    # hanging hooks with a towel / extra hat on right wall
    pix.p(812, 230, CASE)
    pix.rect(808, 231, 10, 14, WHITE_SH)
    pix.hline(808, 231, 10, WHITE)

    # light switch near door
    pix.bevel(542, 210, 8, 12, METAL, WHITE_SH, CASE)
    pix.rect(545, 214, 3, 5, WHITE)

    # floor last (so it's on top of any leaked wall, but furniture feet should already end at 300)
    # Wait — if I draw floor last it covers nothing important below 300, good.
    # Furniture was drawn with legs to 300, so draw floor now.
    draw_floor(pix, W_MID, rng)

    # Re-draw shadows at the furniture line so they sit on the floor (top 3-4 px only)
    pix.dith(178, FLOOR_TOP, 54, 3, GROUT, TILE_DK, "h")
    pix.dith(290, FLOOR_TOP, 108, 3, GROUT, TILE_DK, "h")
    pix.dith(700, FLOOR_TOP, 130, 3, GROUT, TILE_DK, "h")
    pix.dith(180, FLOOR_TOP, 224, 2, LOK_SH, GROUT, "h")
    pix.dith(700, FLOOR_TOP, 140, 2, LOK_SH, GROUT, "h")
    pix.dith(64, FLOOR_TOP, 100, 3, GROUT, TILE_DK, "h")
    pix.dith(612, FLOOR_TOP, 80, 3, GROUT, TILE_DK, "h")
    pix.dith(718, FLOOR_TOP, 50, 3, GROUT, TILE_DK, "h")
    pix.dith(548, FLOOR_TOP + 4, 54, 2, GROUT, TILE_DK, "h")

    # pipes along mid ceiling front
    pix.hline(0, 26, W_MID, CASE)
    pix.hline(0, 27, W_MID, CASE_HI)

    return pix


def draw_anim(frame, mid_ref):
    """Transparent overlay aligned to mid. frame 0..3."""
    pix = Pix(W_MID, H, None)
    states = ["on", "surge", "dim", "off"]
    st = states[frame]
    # Overpaint the dying fixture + a little surrounding ceiling
    # sample mid ceiling color already there; just redraw tiles + fixture
    pix.rect(FLICKER_X - 8, 0, FLICKER_W + 16, 26, CEIL)
    for tx in range(FLICKER_X - 8, FLICKER_X + FLICKER_W + 8, 32):
        pix.vline(tx, 0, 26, CEIL_DK)
    pix.hline(FLICKER_X - 8, 12, FLICKER_W + 16, CEIL_DK)
    draw_fixture(pix, FLICKER_X, FLICKER_Y, FLICKER_W, st)
    # light spill on nearby wall/ceiling when surge, or dimming dither when off
    if st == "surge":
        pix.dith(FLICKER_X - 16, 26, FLICKER_W + 32, 10, FLUOR, CEIL_LT, "bayer")
        # slight floor brightening under the light (only at back of floor, y=300-307)
        pix.dith(FLICKER_X - 20, FLOOR_TOP, FLICKER_W + 40, 5, WALL_HI, TILE, "h")
    elif st == "off":
        pix.dith(FLICKER_X - 10, 26, FLICKER_W + 20, 8, CEIL_DK, CEIL, "checker")
    elif st == "dim":
        pix.dith(FLICKER_X - 8, 26, FLICKER_W + 16, 6, CEIL, CEIL_DK, "bayer")

    # steam puffs from shower door (left). Positions bob per frame.
    steam_ys = [
        [(36, 200), (44, 180), (30, 160), (40, 145)],
        [(38, 190), (42, 168), (32, 150), (36, 138)],
        [(34, 184), (46, 172), (28, 154), (42, 142)],
        [(40, 196), (40, 176), (34, 158), (38, 148)],
    ]
    for i, (sx, sy) in enumerate(steam_ys[frame]):
        r = 5 + (i % 3)
        col = WHITE_SH if i % 2 == 0 else METAL
        pix.circle(sx, sy, r, col)
        pix.circle(sx - 2, sy - 1, max(2, r - 2), WHITE)

    # drip from a ceiling stain near the flicker light
    drip_x = FLICKER_X + 70
    # stain is on mid already? add a small stain + falling drop
    pix.dith(drip_x - 3, 24, 8, 4, CEIL_DK, CEIL, "checker")
    drop_y = 28 + frame * 18
    pix.p(drip_x, drop_y, FLUOR_DIM)
    pix.p(drip_x, drop_y + 1, CEIL_LT)
    pix.p(drip_x, drop_y + 2, FLUOR_DIM)
    if frame == 3:
        # splash on locker top (y=140)
        pix.p(drip_x, 140, FLUOR_DIM)
        pix.p(drip_x - 1, 141, CEIL_LT)
        pix.p(drip_x + 1, 141, CEIL_LT)

    # kids
    # standing kid at open locker #14, in the bench gap
    draw_kid_standing(pix, 248, FLOOR_TOP, facing=1, frame=frame, hair="dark", pose="reach")
    # sitting kid on the right bench (starts at x=700), twirling sticks
    draw_kid_sitting(pix, 348, 276, facing=-1, frame=frame, hair="brown")
    # talking kid in the open floor near the door / whiteboard
    draw_kid_standing(pix, 536, FLOOR_TOP, facing=-1, frame=frame, hair="brown", pose="talk")

    return pix


def compose_preview(far, mid, anim):
    preview = far.convert("RGBA")
    crop = (W_MID - W_FAR) // 2
    mid_c = mid.crop((crop, 0, crop + W_FAR, H))
    anim_c = anim.crop((crop, 0, crop + W_FAR, H))
    preview = Image.alpha_composite(preview, mid_c)
    preview = Image.alpha_composite(preview, anim_c)
    return preview.convert("RGB")


def main():
    rng = random.Random(SEED)
    far = crunch(draw_far(rng).im, opaque=True)
    mid = crunch(draw_mid(random.Random(SEED + 1)).im, opaque=False)
    anims = []
    for i in range(4):
        anims.append(crunch(draw_anim(i, mid).im, opaque=False))

    far.save(DIR / "far.png")
    mid.save(DIR / "mid.png")
    for i, im in enumerate(anims):
        im.save(DIR / f"anim_{i}.png")

    preview = compose_preview(far, mid, anims[0])
    # also crunch preview to palette
    preview = crunch(preview.convert("RGBA"), opaque=True)
    preview.save(DIR / "preview.png")
    preview.resize((W_FAR * 2, H * 2), Image.Resampling.NEAREST).save(DIR / "preview@2x.png")

    def info(p, im):
        return f"{p.name} {im.size[0]}x{im.size[1]} {im.mode}"

    files = [far, mid, *anims, preview]
    names = ["far.png", "mid.png", "anim_0.png", "anim_1.png", "anim_2.png", "anim_3.png", "preview.png"]
    for n, im in zip(names, files):
        print(info(DIR / n, im))
    p2 = Image.open(DIR / "preview@2x.png")
    print(info(DIR / "preview@2x.png", p2))
    print("palette", len(PALETTE))


if __name__ == "__main__":
    main()
