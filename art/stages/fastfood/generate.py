#!/usr/bin/env python3
"""Band Wars — generic fast-food restaurant stage generator.

640x360 far, 960x360 mid/anim, preview 640x360 + preview@2x.
Seeded RNG, 32-color palette, nearest-neighbor only, no anti-aliasing.
Fighters' feet at y=320; floor band y=300..360 stays uncluttered.
Fictional shop name only: BURGER SPOT. No real brands.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

SEED = 19920910
DIR = Path(__file__).resolve().parent
W_FAR, W_MID, H = 640, 960, 360
FLOOR_TOP = 300

# 32-color palette
# Official JMHS school colors, copied verbatim from
# art/characters/tools/pxart/palette.py (and the football stage).
NAVY       = (0x17, 0x30, 0x5F)  # #17305F
NAVY_DK    = (0x0C, 0x17, 0x34)  # #0C1734
GOLD       = (0xD4, 0xA0, 0x17)  # #D4A017
GOLD_LT    = (0xF5, 0xDE, 0x6A)  # #F5DE6A
WHITE      = (0xF6, 0xF2, 0xEA)  # #F6F2EA
SODIUM, SODIUM_HI = GOLD, GOLD_LT  # lamps / fries share official gold
SKY        = (16, 18, 38)
SKY2       = SKY
LOT        = (36, 34, 40)
LOT_LINE   = (80, 78, 70)
CAR        = (24, 26, 32)
GLASS      = (42, 54, 74)
GLASS_HI   = GLASS
WALL       = (214, 194, 154)
WALL_SH    = (174, 152, 116)
WALL_DK    = (122, 102, 76)
RED        = (168, 36, 38)
RED_DK     = (104, 20, 24)
RED_HI     = (208, 64, 58)
CREAM      = (236, 224, 194)
CREAM_SH   = (204, 186, 152)
CHROME     = (196, 200, 204)
CHROME_DK  = (112, 116, 124)
CHROME_HI  = (234, 236, 238)
COUNTER    = (180, 142, 98)
COUNTER_DK = (134, 102, 70)
MENU_BG    = (24, 26, 30)
GLOW       = (255, 198, 64)
GLOW_DIM   = (186, 132, 36)
NEON_P     = (255, 82, 148)
NEON_C     = (64, 216, 200)
TILE_W     = (224, 214, 192)
TILE_R     = (148, 34, 38)
SKIN       = (210, 166, 126)
INK        = (28, 26, 30)

# Unique 32: dropped former NAVY, unique GLASS_HI, and unique SKY2;
# added NAVY, NAVY_DK, WHITE. GOLD/GOLD_LT share SODIUM/SODIUM_HI tuples.
PALETTE = [
    SKY, LOT, LOT_LINE, SODIUM, SODIUM_HI, CAR, GLASS,
    WALL, WALL_SH, WALL_DK, RED, RED_DK, RED_HI, CREAM, CREAM_SH,
    CHROME, CHROME_DK, CHROME_HI, COUNTER, COUNTER_DK, MENU_BG, GLOW,
    GLOW_DIM, NEON_P, NEON_C, TILE_W, TILE_R, NAVY, NAVY_DK, WHITE, SKIN, INK,
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
    "$": ["01110","10101","10100","01110","00101","10101","01110"],
}

FONT3 = {
    " ": ["000","000","000","000","000"],
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
    "Q": ["010","101","101","111","011"],
    "R": ["110","101","110","101","101"],
    "S": ["011","100","010","001","110"],
    "T": ["111","010","010","010","010"],
    "U": ["101","101","101","101","011"],
    "V": ["101","101","101","101","010"],
    "W": ["101","101","111","111","101"],
    "X": ["101","101","010","101","101"],
    "Y": ["101","101","010","010","010"],
    "Z": ["111","001","010","100","111"],
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
    "$": ["010","111","110","011","010"],
    ".": ["000","000","000","000","010"],
    ":": ["000","010","000","010","000"],
    "-": ["000","000","111","000","000"],
    "!": ["010","010","010","000","010"],
    "/": ["001","001","010","100","100"],
    "'": ["010","010","000","000","000"],
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
                elif not fill and abs(d - r * r) <= max(r, 1):
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
    glyphs = FONT if font == "5" else FONT3
    adv = 6 if font == "5" else 4
    cx = x
    for ch in s.upper():
        glyph = glyphs.get(ch, glyphs.get("?"))
        if glyph is None:
            glyph = glyphs.get(" ")
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
# Icons & props
# ---------------------------------------------------------------------------

# Menu-row layout: icon in a 16px-wide slot, then >=2px gap, then text.
MENU_ICON_W = 16
MENU_TEXT_GAP = 2


def icon_burger(pix, x, y):
    """Fits in a 16px-wide slot (pixels x .. x+15)."""
    pix.rect(x + 2, y + 1, 10, 3, SODIUM)
    pix.p(x + 1, y + 2, SODIUM)
    pix.p(x + 12, y + 2, SODIUM)
    pix.hline(x + 3, y + 1, 8, SODIUM_HI)
    pix.rect(x + 2, y + 4, 10, 2, SODIUM_HI)  # cheese
    pix.rect(x + 2, y + 6, 10, 2, WALL_DK)    # patty
    pix.rect(x + 2, y + 8, 10, 3, SODIUM)
    pix.hline(x + 2, y + 10, 10, GLOW_DIM)


def icon_fries(pix, x, y):
    """Fits in a 16px-wide slot (pixels x .. x+15)."""
    pix.rect(x + 3, y + 6, 8, 6, RED)
    pix.rect(x + 4, y + 7, 6, 4, RED_HI)
    for i, ox in enumerate((4, 6, 8, 10, 12)):
        h = 7 + (i % 3)
        pix.vline(x + ox, y + 6 - h, h, SODIUM_HI if i % 2 == 0 else SODIUM)
        pix.p(x + ox, y + 6 - h, CREAM)


def icon_drink(pix, x, y):
    """Fits in a 16px-wide slot (pixels x .. x+15)."""
    pix.rect(x + 4, y + 3, 7, 9, RED)
    pix.rect(x + 5, y + 4, 5, 6, RED_HI)
    pix.hline(x + 3, y + 3, 9, CHROME)
    pix.rect(x + 7, y + 0, 2, 4, CHROME_DK)  # straw
    pix.p(x + 8, y, NEON_C)
    pix.rect(x + 5, y + 5, 3, 3, CHROME_HI)  # ice highlight


def icon_combo(pix, x, y):
    """Compact burger + fries, strictly inside a 16px-wide slot."""
    # mini burger on the left (x .. x+8)
    pix.rect(x + 1, y + 2, 7, 2, SODIUM)
    pix.hline(x + 2, y + 2, 5, SODIUM_HI)
    pix.rect(x + 1, y + 4, 7, 1, SODIUM_HI)
    pix.rect(x + 1, y + 5, 7, 2, WALL_DK)
    pix.rect(x + 1, y + 7, 7, 2, SODIUM)
    # mini fries on the right (x+9 .. x+15)
    pix.rect(x + 9, y + 7, 6, 5, RED)
    pix.rect(x + 10, y + 8, 4, 3, RED_HI)
    for i, ox in enumerate((10, 12, 14)):
        pix.vline(x + ox, y + 2, 6, SODIUM_HI if i % 2 == 0 else SODIUM)
        pix.p(x + ox, y + 2, CREAM)


def draw_shako(pix, x, y, small=True):
    pix.bevel(x, y + 2, 9, 8, NAVY, NAVY, NAVY_DK)
    pix.rect(x + 1, y + 3, 7, 2, NAVY)
    pix.rect(x, y + 9, 10, 2, INK)
    pix.hline(x, y + 8, 9, GOLD)
    pix.rect(x + 3, y + 4, 3, 3, GOLD)
    pix.p(x + 4, y + 5, WHITE)
    pix.vline(x + 4, y - 5, 7, GOLD)
    pix.vline(x + 5, y - 6, 8, GOLD_LT)
    pix.p(x + 5, y - 6, WHITE)


def draw_fry_box(pix, x, y):
    pix.rect(x, y + 6, 10, 8, RED)
    pix.rect(x + 1, y + 7, 8, 5, RED_HI)
    pix.outline(x, y + 6, 10, 8, RED_DK)
    for i, ox in enumerate((1, 3, 5, 7, 9)):
        pix.vline(x + ox, y + (2 if i % 2 else 1), 6 if i % 2 else 7, SODIUM if i % 2 else SODIUM_HI)


def draw_cup(pix, x, y, lid=True):
    pix.rect(x, y + 3, 7, 10, RED)
    pix.rect(x + 1, y + 4, 5, 7, RED_HI)
    pix.hline(x, y + 3, 7, CHROME)
    if lid:
        pix.rect(x - 1, y + 1, 9, 3, CHROME)
        pix.rect(x + 2, y - 2, 2, 4, CHROME_DK)
        pix.p(x + 3, y - 2, NEON_C)


def draw_tray(pix, x, y, w=28):
    pix.bevel(x, y, w, 8, RED, RED_HI, RED_DK)
    pix.rect(x + 2, y + 2, w - 4, 4, RED_DK)


def draw_ketchup(pix, x, y, mustard=False):
    col = SODIUM if mustard else RED
    col2 = SODIUM_HI if mustard else RED_HI
    pix.rect(x, y + 4, 6, 10, col)
    pix.rect(x + 1, y + 5, 4, 7, col2)
    pix.rect(x + 1, y, 4, 5, CHROME)
    pix.p(x + 2, y, CHROME_HI)
    pix.p(x + 3, y + 2, INK)  # tip


def draw_register(pix, x, y):
    # cash register / POS
    pix.bevel(x, y + 8, 22, 14, CHROME_DK, CHROME, CAR)
    pix.rect(x + 2, y, 18, 12, MENU_BG)
    pix.outline(x + 2, y, 18, 12, CHROME)
    # glowing screen
    pix.rect(x + 4, y + 2, 14, 8, GLASS)
    pix.dith(x + 4, y + 2, 14, 8, NEON_C, GLASS, "bayer")
    pix.rect(x + 5, y + 3, 6, 2, NEON_C)
    pix.rect(x + 5, y + 6, 8, 1, CHROME)
    # keypad
    for r in range(2):
        for c in range(3):
            pix.p(x + 5 + c * 4, y + 11 + r * 4, CHROME)
    # cash drawer
    pix.rect(x + 1, y + 20, 20, 5, CHROME)
    pix.hline(x + 1, y + 20, 20, CHROME_HI)
    pix.rect(x + 9, y + 21, 6, 2, CHROME_DK)


def draw_soda_fountain(pix, x, y):
    pix.bevel(x, y, 54, 36, CHROME, CHROME_HI, CHROME_DK)
    pix.rect(x + 2, y + 2, 50, 8, MENU_BG)
    text(pix, x + 6, y + 3, "FOUNTAIN", GLOW, font="3")
    # six spigots
    for i in range(6):
        sx = x + 5 + i * 8
        colors = [RED, SODIUM, NEON_C, RED_HI, GLOW, GLASS_HI]
        pix.rect(sx, y + 12, 6, 8, colors[i])
        pix.rect(sx + 1, y + 20, 3, 5, CHROME_DK)
        pix.p(sx + 2, y + 25, CHROME)
    # drip tray
    pix.rect(x + 2, y + 28, 50, 6, CHROME_DK)
    pix.dith(x + 4, y + 29, 46, 4, CAR, CHROME_DK, "h")
    # a cup under one spigot
    draw_cup(pix, x + 14, y + 22, lid=False)


def draw_pendant(pix, x, y, length=28):
    pix.vline(x, 0, length, CHROME_DK)
    pix.vline(x + 1, 0, length, CHROME)
    # warm globe
    pix.circle(x, y + length + 5, 7, SODIUM)
    pix.circle(x, y + length + 5, 5, SODIUM_HI)
    pix.p(x - 2, y + length + 3, CREAM)


def draw_booth_seat(pix, x, y, w, h, facing="front"):
    """Red vinyl booth seat. y is top of backrest; seat is lower."""
    # backrest
    pix.bevel(x, y, w, h, RED, RED_HI, RED_DK)
    # vertical tufting
    for i in range(1, w // 14):
        pix.vline(x + i * 14, y + 2, h - 4, RED_DK)
        pix.vline(x + i * 14 + 1, y + 2, h - 6, RED_HI)
    # piping along top
    pix.hline(x, y, w, CREAM_SH)
    pix.hline(x, y + 1, w, RED_HI)
    # seat cushion
    sh = 14
    pix.bevel(x - 2, y + h - 2, w + 4, sh, RED, RED_HI, RED_DK)
    pix.dith(x, y + h, w, 4, RED_HI, RED, "h")


def draw_table(pix, x, y, w, d=20):
    """Booth table; y is table top."""
    pix.bevel(x, y, w, 5, CREAM, CHROME_HI, CREAM_SH)
    pix.hline(x, y, w, CHROME)
    # pedestal
    pix.rect(x + w // 2 - 3, y + 5, 6, FLOOR_TOP - (y + 5) - 2, CHROME_DK)
    pix.rect(x + w // 2 - 8, FLOOR_TOP - 4, 16, 4, CHROME)
    # chrome edge underline
    pix.hline(x, y + 4, w, CHROME_DK)


def draw_car(pix, x, y, w=48, h=22, body=RED, facing=1):
    """Simple side-view parked car. y is top of roof."""
    pix.rect(x + 6, y, w - 14, 10, body)  # cabin
    pix.rect(x, y + 8, w, 12, body)  # body
    pix.hline(x + 6, y, w - 14, CHROME if body != CAR else LOT_LINE)
    # windows
    pix.rect(x + 8, y + 2, 12, 7, GLASS)
    pix.rect(x + 22, y + 2, 12, 7, GLASS)
    pix.dith(x + 8, y + 2, 12, 7, GLASS_HI, GLASS, "bayer")
    # wheels
    pix.circle(x + 10, y + h - 2, 5, INK)
    pix.circle(x + 10, y + h - 2, 2, CHROME_DK)
    pix.circle(x + w - 12, y + h - 2, 5, INK)
    pix.circle(x + w - 12, y + h - 2, 2, CHROME_DK)
    # lights
    if facing > 0:
        pix.rect(x + w - 3, y + 12, 3, 4, SODIUM_HI)
        pix.rect(x, y + 12, 3, 4, RED_HI)
    else:
        pix.rect(x, y + 12, 3, 4, SODIUM_HI)
        pix.rect(x + w - 3, y + 12, 3, 4, RED_HI)


def draw_bus(pix, x, y):
    """Generic band bus, side view. y is roof."""
    w, h = 110, 40
    pix.rect(x, y + 6, w, h - 6, SODIUM)
    pix.rect(x, y, w - 16, 8, SODIUM)  # high roof
    pix.hline(x, y, w - 16, SODIUM_HI)
    pix.rect(x, y + 6, w, 4, GLOW_DIM)
    # stripe
    pix.rect(x, y + 22, w, 4, NAVY)
    # windows
    for i in range(6):
        wx = x + 8 + i * 14
        pix.rect(wx, y + 8, 12, 10, GLASS)
        pix.dith(wx, y + 8, 12, 10, GLASS_HI, SKY, "bayer")
        pix.outline(wx, y + 8, 12, 10, INK)
    # door
    pix.rect(x + w - 18, y + 8, 12, h - 14, GLASS)
    pix.outline(x + w - 18, y + 8, 12, h - 14, INK)
    # wheels
    for wx in (x + 16, x + 44, x + 80):
        pix.circle(wx, y + h - 2, 7, INK)
        pix.circle(wx, y + h - 2, 3, CHROME_DK)
    # label
    text(pix, x + 30, y + 28, "BAND", CREAM, font="5")
    # headlights
    pix.rect(x + w - 4, y + 26, 4, 5, SODIUM_HI)
    pix.rect(x, y + 26, 3, 5, RED)


def draw_lamppost(pix, x, y_top, y_ground, glow=True):
    pix.vline(x, y_top, y_ground - y_top, CHROME_DK)
    pix.vline(x + 1, y_top, y_ground - y_top, LOT_LINE)
    pix.rect(x - 6, y_top, 14, 5, CAR)
    pix.rect(x - 5, y_top + 1, 12, 3, SODIUM_HI if glow else CHROME_DK)
    if glow:
        pix.dith(x - 16, y_top + 5, 34, 18, SODIUM, SKY2, "bayer")
        pix.dith(x - 10, y_top + 14, 22, 10, GLOW_DIM, LOT, "bayer")


def draw_night_scene(pix, w, h, rng, xoff=0):
    """Night parking lot composed for the mid window band (y≈48-198)."""
    pix.rect(0, 0, w, h, SKY)
    # sky bands — deeper at the top, slightly lighter toward the horizon
    pix.rect(0, 0, w, 70, SKY)
    pix.rect(0, 70, w, 40, SKY2)
    # stars
    rng2 = random.Random(77)
    for _ in range(70):
        sx = rng2.randint(0, w - 1)
        sy = rng2.randint(4, 95)
        pix.p(sx, sy, CREAM if rng2.random() < 0.25 else CHROME)
        if rng2.random() < 0.12:
            pix.p(sx + 1, sy, GLASS_HI)
    # crescent moon, upper right of the window view
    mx, my = w - 90 - xoff // 4, 28
    pix.circle(mx, my, 11, CREAM)
    pix.circle(mx + 4, my - 3, 11, SKY)
    pix.p(mx - 4, my + 1, CHROME_HI)

    # distant building silhouettes along the horizon (visible mid-window)
    rng3 = random.Random(91)
    horizon = 118
    for bx in range(-10, w, 26):
        bh = 16 + rng3.randint(0, 28)
        bw = 18 + rng3.randint(0, 10)
        pix.rect(bx, horizon - bh, bw, bh, CAR)
        if rng3.random() < 0.55 and bh > 18:
            pix.rect(bx + 4, horizon - bh + 5, 4, 4, SODIUM)
            if rng3.random() < 0.5:
                pix.rect(bx + 11, horizon - bh + 10, 3, 3, SODIUM_HI)
    pix.hline(0, horizon, w, INK)

    # parking lot starts immediately below the skyline so it reads through the windows
    pix.rect(0, horizon + 1, w, h - (horizon + 1), LOT)
    for _ in range(350):
        pix.p(rng3.randint(0, w - 1), rng3.randint(horizon + 2, min(h - 1, 260)), CAR)

    # stall lines in the window band
    for row, y in enumerate((128, 150, 174)):
        tw = 32 + row * 8
        x = 6 + row * 5
        while x < w:
            pix.hline(x, y, tw - 8, LOT_LINE)
            pix.vline(x, y, 8 + row * 2, LOT_LINE)
            x += tw

    # lamp posts — fixtures hang in the upper half of the windows
    draw_lamppost(pix, 60, 42, 175, glow=True)
    draw_lamppost(pix, 240, 36, 180, glow=True)
    draw_lamppost(pix, 420, 44, 176, glow=True)

    # pylon sign, cabinet placed in the lower window pane (below the transom at y≈98)
    px = 28
    pix.rect(px, 50, 6, 128, CHROME_DK)
    pix.bevel(px - 16, 100, 40, 36, MENU_BG, CHROME, INK)
    text(pix, px - 14, 104, "BURGER", NEON_P, font="3")
    text(pix, px - 10, 112, "SPOT", NEON_C, font="3")
    pix.rect(px - 12, 124, 32, 4, NEON_P)
    pix.dith(px - 18, 136, 44, 16, SODIUM, LOT, "bayer")

    # cars in the window band
    draw_car(pix, 40, 132, 46, 20, RED, 1)
    draw_car(pix, 120, 128, 44, 20, CREAM_SH, 1)
    draw_car(pix, 80, 154, 48, 20, CAR, -1)
    draw_car(pix, 200, 150, 46, 20, NAVY, 1)
    draw_car(pix, 360, 134, 44, 20, WALL_DK, 1)
    draw_car(pix, 480, 152, 48, 20, RED_DK, -1)

    # band bus — the after-the-game beat, sits in the center window
    # mid window 310-460 → far x=150-300, so park the bus around x=170
    draw_bus(pix, 165, 142)

    # fence along the skyline
    for fx in range(0, w, 8):
        pix.vline(fx, horizon - 2, 10, CHROME_DK)
    pix.hline(0, horizon + 2, w, CHROME_DK)

    # shrubs at the lot edge (still in / just below the sill)
    for sx, sy in ((16, 168), (300, 170), (560, 166)):
        pix.circle(sx, sy, 7, CAR)
        pix.circle(sx + 5, sy + 2, 5, INK)


def draw_window_frame(pix, x, y, w, h, panes=3, fill_night=False, rng=None):
    # brick / wall already around; draw chrome/dark frame and mullions
    pix.bevel(x, y, w, h, CHROME_DK, CHROME, INK)
    pix.rect(x + 3, y + 3, w - 6, h - 6, INK if fill_night else (0, 0, 0, 0))
    inner_w = w - 6
    pw = inner_w // panes
    for i in range(panes):
        px = x + 3 + i * pw
        if fill_night and rng is not None:
            # cheap night fill for parallax-edge windows
            pix.rect(px, y + 3, pw - 1, h - 6, SKY)
            pix.dith(px, y + 3 + (h - 6) // 2, pw - 1, (h - 6) // 2, LOT, SKY2, "h")
            if rng.random() < 0.7:
                pix.p(px + 4, y + 10, CREAM)
        # mullion
        if i:
            pix.rect(px - 1, y, 3, h, CHROME_DK)
            pix.vline(px, y, h, CHROME)
    # transom bar
    pix.rect(x, y + h // 3, w, 3, CHROME_DK)
    pix.hline(x, y + h // 3, w, CHROME)
    # sill
    pix.rect(x - 2, y + h - 2, w + 4, 5, WALL_DK)
    pix.hline(x - 2, y + h - 2, w + 4, CREAM_SH)
    # sparse interior reflections (always, even on transparent glass)
    rng2 = random.Random(12 + x)
    for _ in range((w * h) // 220):
        rx = x + 5 + rng2.randint(0, max(1, w - 12))
        ry = y + 5 + rng2.randint(0, max(1, h - 14))
        # skip mullions roughly
        pix.p(rx, ry, CREAM_SH if rng2.random() < 0.4 else CHROME)


def draw_neon_sign(pix, x, y, on=True, buzz_mask=None):
    """BURGER SPOT script-ish neon, with a burger icon. buzz_mask: set of dim letter indexes."""
    w, h = 168, 28
    # sign cabinet
    pix.bevel(x, y, w, h, MENU_BG, CHROME_DK, INK)
    pix.outline(x, y, w, h, CHROME)
    # neon letters
    word = "BURGER SPOT"
    cx = x + 8
    for i, ch in enumerate(word):
        col = NEON_P
        if ch == " ":
            cx += 4
            continue
        dim = False
        if buzz_mask and i in buzz_mask:
            dim = True
        if not on:
            dim = True
        color = (CHROME_DK if dim else NEON_P)
        # slight cyan outline when on
        if not dim:
            text(pix, cx + 1, y + 6, ch, NEON_C, scale=2)
        text(pix, cx, y + 5, ch, color, scale=2)
        cx += 14 if ch != "I" else 12
    # small burger badge on the left of cabinet already starts at letters
    if not on:
        # a couple sparks
        pix.p(x + 20, y + 4, NEON_P)
        pix.p(x + 80, y + 10, NEON_C)


def draw_open_sign(pix, x, y, on=True):
    pix.bevel(x, y, 36, 16, MENU_BG, CHROME, INK)
    col = NEON_C if on else CHROME_DK
    text(pix, x + 6, y + 5, "OPEN", col, font="3")
    if on:
        pix.outline(x + 1, y + 1, 34, 14, NEON_C)


def draw_menu_board(pix, x, y, title, rows, glow=True):
    """rows: list of (kind, name, price) kind in burger/fries/drink/combo."""
    w, h = 92, 96
    g = GLOW if glow else GLOW_DIM
    g2 = SODIUM_HI if glow else SODIUM
    pix.bevel(x, y, w, h, MENU_BG, CHROME_DK, INK)
    pix.rect(x + 2, y + 2, w - 4, 12, CAR)
    text(pix, x + 6, y + 4, title, g, font="3")
    if glow:
        pix.hline(x + 2, y + 14, w - 4, g)
    else:
        pix.hline(x + 2, y + 14, w - 4, GLOW_DIM)
    icons = {"burger": icon_burger, "fries": icon_fries, "drink": icon_drink, "combo": icon_combo}
    for i, (kind, name, price) in enumerate(rows):
        ry = y + 18 + i * 24
        ix = x + 4
        tx = ix + MENU_ICON_W + MENU_TEXT_GAP  # icon, then >=2px gap, then text
        icons.get(kind, icon_burger)(pix, ix, ry)
        text(pix, tx, ry + 2, name, g2, font="3")
        text(pix, tx, ry + 9, price, CREAM if glow else CHROME, font="3")
    # backlight frame
    if glow:
        pix.dith(x - 1, y - 1, w + 2, 2, g, GLOW_DIM, "h")


def draw_counter(pix, x, y, w):
    """Service counter; top at y, front down to FLOOR_TOP."""
    # top
    pix.bevel(x, y, w, 10, COUNTER, CREAM_SH, COUNTER_DK)
    pix.hline(x, y, w, CHROME)
    # front panel
    pix.rect(x, y + 10, w, FLOOR_TOP - (y + 10), COUNTER_DK)
    # red stripe brand-band (fictional)
    pix.rect(x, y + 16, w, 10, RED)
    pix.hline(x, y + 16, w, RED_HI)
    pix.hline(x, y + 25, w, RED_DK)
    # lower panels
    pw = 40
    for i, px in enumerate(range(x + 4, x + w - 8, pw)):
        pix.bevel(px, y + 30, pw - 6, FLOOR_TOP - (y + 34), COUNTER, COUNTER, COUNTER_DK)
    # kick plate
    pix.rect(x, FLOOR_TOP - 6, w, 6, CHROME_DK)
    pix.hline(x, FLOOR_TOP - 6, w, CHROME)


def draw_kid_booth(pix, x, y_table, facing=1, frame=0, hair="dark", action="eat"):
    """Upper body of a kid sitting at a booth, table at y_table. Head ~22px above table."""
    bob = (0, 1, 0, -1)[frame]
    head_cx = x
    head_cy = y_table - 22 + bob
    # torso
    pix.rect(head_cx - 8, y_table - 16 + bob, 16, 18, NAVY)
    pix.vline(head_cx - 8, y_table - 16 + bob, 18, NAVY_DK)
    pix.vline(head_cx + 7, y_table - 16 + bob, 18, NAVY_DK)
    pix.vline(head_cx - 6, y_table - 14 + bob, 12, GOLD)
    pix.vline(head_cx + 5, y_table - 14 + bob, 12, GOLD)
    pix.vline(head_cx, y_table - 14 + bob, 14, WHITE)
    # neck
    pix.rect(head_cx - 2, head_cy + 5, 4, 4, SKIN)
    # head
    pix.circle(head_cx, head_cy, 6, SKIN)
    hc = INK if hair == "dark" else (WALL_DK if hair == "brown" else SODIUM)
    pix.rect(head_cx - 6, head_cy - 6, 12, 5, hc)
    pix.p(head_cx - 6, head_cy - 1, hc)
    pix.p(head_cx + 5, head_cy - 1, hc)
    if hair == "blond":
        pix.p(head_cx, head_cy - 7, hc)
    # eyes
    pix.p(head_cx - 2, head_cy, INK)
    pix.p(head_cx + 2, head_cy, INK)
    # mouth
    if action == "eat" and frame in (1, 2):
        pix.p(head_cx, head_cy + 3, INK)
        pix.p(head_cx + 1, head_cy + 3, INK)
    else:
        pix.hline(head_cx - 1, head_cy + 3, 3, INK)
    # arm + fry / cup
    if action == "eat":
        if frame in (1, 2):
            # hand to mouth
            pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 14 + bob, 4, 6, NAVY)
            pix.rect(head_cx + (8 if facing > 0 else -10), head_cy + 2, 3, 3, SKIN)
            pix.p(head_cx + (7 if facing > 0 else -6), head_cy + 2, SODIUM_HI)  # fry
        else:
            pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 10 + bob, 4, 8, NAVY)
            pix.rect(head_cx + (7 if facing > 0 else -9), y_table - 2, 4, 3, SKIN)
            pix.p(head_cx + (10 if facing > 0 else -6), y_table - 1, SODIUM_HI)
    elif action == "drink":
        if frame in (1, 2):
            pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 16 + bob, 4, 8, NAVY)
            draw_cup(pix, head_cx + (8 if facing > 0 else -12), head_cy - 2, lid=True)
        else:
            pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 10 + bob, 4, 8, NAVY)
            pix.rect(head_cx + (7 if facing > 0 else -9), y_table - 2, 4, 3, SKIN)
            draw_cup(pix, head_cx + (10 if facing > 0 else -14), y_table - 8, lid=True)
    else:
        # talk / fidget
        pix.rect(head_cx + (6 if facing > 0 else -10), y_table - 12 + bob, 4, 10, NAVY)
        pix.rect(head_cx + (7 if facing > 0 else -9), y_table - 2, 4, 3, SKIN)
        if frame % 2 == 0:
            pix.rect(head_cx + (10 if facing > 0 else -12), y_table - 16 + bob, 3, 6, SKIN)


def draw_cashier(pix, x, y_counter, frame=0, facing=-1):
    """Cashier behind the counter. Only upper body visible above counter top."""
    bob = (0, 0, 1, 0)[frame]
    head_cx = x + (1 if frame in (2, 3) else 0) * facing
    head_cy = y_counter - 26 + bob
    # visor + polo (cream/red, not band uniform)
    pix.rect(head_cx - 8, y_counter - 18 + bob, 16, 20, CREAM)
    pix.rect(head_cx - 8, y_counter - 8 + bob, 16, 4, RED)
    pix.rect(head_cx - 2, head_cy + 5, 4, 4, SKIN)
    pix.circle(head_cx, head_cy, 6, SKIN)
    # visor
    pix.rect(head_cx - 7, head_cy - 4, 14, 3, RED)
    pix.rect(head_cx - 6, head_cy - 7, 12, 4, RED_DK)
    pix.p(head_cx, head_cy - 6, CREAM)
    # hair peeking
    pix.rect(head_cx - 5, head_cy - 8, 10, 2, INK)
    pix.p(head_cx - 2, head_cy, INK)
    pix.p(head_cx + 2, head_cy, INK)
    pix.hline(head_cx - 1, head_cy + 3, 3, INK)
    # arms
    if frame in (0, 1):
        # hands on register (to the left)
        pix.rect(head_cx - 14, y_counter - 14, 6, 8, CREAM)
        pix.rect(head_cx - 16, y_counter - 8, 5, 3, SKIN)
        pix.rect(head_cx + 8, y_counter - 12, 4, 8, CREAM)
        pix.rect(head_cx + 8, y_counter - 5, 4, 3, SKIN)
    else:
        # handing a bag to the left
        pix.rect(head_cx - 16, y_counter - 18, 6, 8, CREAM)
        pix.rect(head_cx - 20, y_counter - 14, 6, 5, SKIN)
        pix.rect(head_cx - 22, y_counter - 16, 8, 8, CREAM_SH)  # bag
        pix.outline(head_cx - 22, y_counter - 16, 8, 8, WALL_DK)
        pix.rect(head_cx + 8, y_counter - 12, 4, 8, CREAM)
        pix.rect(head_cx + 8, y_counter - 5, 4, 3, SKIN)



def draw_jukebox(pix, x, y_bottom):
    """Generic neon jukebox — fills the booth/counter gap. Feet at y_bottom (=FLOOR_TOP)."""
    h = 110
    y = y_bottom - h
    w = 52
    pix.bevel(x, y, w, h, MENU_BG, CHROME, INK)
    # rounded top
    pix.rect(x + 2, y + 2, w - 4, 28, CAR)
    pix.dith(x + 4, y + 4, w - 8, 24, NEON_P, NEON_C, "bayer")
    pix.circle(x + w // 2, y + 16, 10, MENU_BG)
    pix.circle(x + w // 2, y + 16, 8, GLOW)
    pix.circle(x + w // 2, y + 16, 4, SODIUM_HI)
    # grille / title strip
    pix.rect(x + 4, y + 32, w - 8, 10, RED)
    text(pix, x + 8, y + 34, "TUNES", CREAM, font="3")
    # selection buttons
    for r in range(3):
        for c in range(4):
            col = SODIUM_HI if (r + c) % 2 == 0 else NEON_C
            pix.rect(x + 6 + c * 10, y + 46 + r * 8, 8, 6, col)
            pix.p(x + 7 + c * 10, y + 47 + r * 8, CREAM)
    # speaker grille
    pix.rect(x + 6, y + 72, w - 12, 28, CHROME_DK)
    for gy in range(y + 74, y + 98, 3):
        pix.hline(x + 8, gy, w - 16, CAR)
    # chrome base
    pix.rect(x - 2, y_bottom - 6, w + 4, 6, CHROME)
    pix.hline(x - 2, y_bottom - 6, w + 4, CHROME_HI)
    # side neon tubes
    pix.vline(x + 1, y + 6, h - 16, NEON_P)
    pix.vline(x + w - 2, y + 6, h - 16, NEON_C)


def draw_trash(pix, x, y_bottom):
    h = 32
    y = y_bottom - h
    pix.bevel(x, y, 18, h, CHROME_DK, CHROME, INK)
    pix.rect(x + 2, y + 8, 14, h - 12, CAR)
    pix.rect(x + 1, y, 16, 8, CHROME)
    pix.rect(x + 5, y + 2, 8, 5, CAR)  # swing door
    pix.p(x + 8, y + 4, CHROME)


# Menu board positions (mid coords) for anim overpaint
MENU_X, MENU_Y = 548, 36
NEON_X, NEON_Y = 210, 14
OPEN_X, OPEN_Y = 488, 86
FOUNTAIN_X = 730


def draw_far(rng):
    pix = Pix(W_FAR, H, SKY)
    draw_night_scene(pix, W_FAR, H, rng, xoff=0)
    # The interior isn't on far; this is purely the lot/sky seen through windows.
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
            pix.rect(x, y0, tw, y1 - y0, TILE_W if even else TILE_R)
            x += tw
            col += 1
        pix.hline(0, y0, w, COUNTER_DK)
        x = -offset
        while x < w:
            pix.vline(x, y0, y1 - y0, COUNTER_DK)
            x += tw
    # warm light pools at the BACK of the floor only (y=300-308)
    for lx in (120, 280, 500, 700, 860):
        pix.dith(lx, FLOOR_TOP, 50, 6, SODIUM, TILE_W, "bayer")
    # tiny scuffs
    for _ in range(60):
        pix.p(rng.randint(0, w - 1), rng.randint(FLOOR_TOP + 2, H - 2), COUNTER_DK)


def draw_mid(rng):
    pix = Pix(W_MID, H, None)

    # Interior walls (opaque everywhere except window glass in the center)
    pix.rect(0, 0, W_MID, FLOOR_TOP, WALL)
    # darker lower wainscoting / tile wainscot
    pix.rect(0, 220, W_MID, FLOOR_TOP - 220, WALL_SH)
    pix.hline(0, 220, W_MID, RED_DK)
    pix.rect(0, 220, W_MID, 6, RED)
    pix.hline(0, 220, W_MID, RED_HI)
    # baseboard
    pix.rect(0, FLOOR_TOP - 5, W_MID, 5, WALL_DK)
    pix.hline(0, FLOOR_TOP - 5, W_MID, CREAM_SH)

    # ceiling
    pix.rect(0, 0, W_MID, 22, WALL_DK)
    pix.dith(0, 0, W_MID, 22, WALL_DK, COUNTER_DK, "h")
    pix.hline(0, 22, W_MID, WALL_SH)
    # ceiling tiles hint
    for tx in range(0, W_MID, 40):
        pix.vline(tx, 0, 22, COUNTER_DK)

    # pendant lamps (front of ceiling)
    for px in (80, 200, 330, 460, 700, 860):
        draw_pendant(pix, px, 0, length=20 + (px % 16) // 4)

    # ---- Windows along the back (left through center) ----
    # A long window wall from x=40 to x=560, with frames. Glass transparent in center.
    # Left parallax margin windows get painted night so panning isn't empty.
    windows = [
        # x, y, w, h, panes, fill_night
        (16, 48, 120, 150, 2, True),     # left margin, opaque night
        (148, 48, 150, 150, 3, False),   # visible left (pylon, cars)
        (310, 48, 160, 150, 3, False),   # visible center (band bus)
        # no third window: leaves a wall for the jukebox, clock, and signs
    ]
    for wx, wy, ww, wh, panes, fill in windows:
        draw_window_frame(pix, wx, wy, ww, wh, panes=panes, fill_night=fill, rng=rng)

    # brick/trim around windows (already wall). Add a few decorative tiles
    for tx in range(20, 560, 16):
        pix.outline(tx, 200, 14, 14, WALL_DK)
        pix.p(tx + 7, 207, CREAM_SH)

    # neon sign hanging above the two main windows (clearly in preview)
    draw_neon_sign(pix, NEON_X, NEON_Y, on=True)
    # chains for the sign
    pix.vline(NEON_X + 10, 0, NEON_Y, CHROME_DK)
    pix.vline(NEON_X + 158, 0, NEON_Y, CHROME_DK)

    draw_open_sign(pix, OPEN_X, OPEN_Y, on=True)

    # ---- Entrance door, far left of visible / margin ----
    pix.bevel(8, 140, 40, FLOOR_TOP - 140, RED_DK, RED, INK)
    pix.rect(12, 146, 32, FLOOR_TOP - 154, RED)
    # glass in door (fill night, it's in the margin)
    pix.rect(16, 150, 24, 70, SKY)
    pix.dith(16, 186, 24, 34, LOT, SKY2, "h")
    pix.outline(16, 150, 24, 70, INK)
    pix.rect(18, 260, 20, 8, CHROME)  # push bar
    text(pix, 14, 128, "IN", CREAM, font="3")

    # ---- Booths under the windows (left / center-left) ----
    # Booth 1 (visible left)
    draw_booth_seat(pix, 150, 200, 70, 70)
    draw_table(pix, 168, 248, 44)
    draw_booth_seat(pix, 220, 200, 70, 70)
    # table props
    draw_fry_box(pix, 176, 236)
    draw_cup(pix, 190, 236)
    draw_tray(pix, 200, 243, 22)
    draw_ketchup(pix, 172, 234, mustard=False)
    draw_ketchup(pix, 180, 234, mustard=True)

    # Booth 2 (center-left, still in preview)
    draw_booth_seat(pix, 310, 200, 70, 70)
    draw_table(pix, 328, 248, 44)
    draw_booth_seat(pix, 380, 200, 70, 70)
    draw_fry_box(pix, 336, 236)
    draw_fry_box(pix, 348, 236)
    draw_cup(pix, 362, 234)
    draw_tray(pix, 330, 243, 26)
    # shako left on the table after the game — a readable mid-stage beat
    draw_shako(pix, 352, 226)
    pix.rect(352, 226 + 2, 10, 8, CREAM)  # ensure hat body reads on the cream table
    draw_shako(pix, 350, 224)
    # napkin dispenser
    pix.bevel(372, 240, 12, 8, CHROME, CHROME_HI, CHROME_DK)
    pix.rect(374, 242, 8, 4, CREAM)

    # Booth 3 in left margin (parallax)
    draw_booth_seat(pix, 20, 210, 56, 60)
    draw_table(pix, 36, 254, 36)
    draw_booth_seat(pix, 80, 210, 56, 60)
    draw_fry_box(pix, 42, 242)
    draw_cup(pix, 56, 242)

    # ---- Right: menu boards + counter ----
    rows1 = [("combo", "COMBO A", "5.99"), ("combo", "COMBO B", "6.49"), ("burger", "BIG BURGER", "4.79")]
    rows2 = [("burger", "BURGER", "3.49"), ("fries", "FRIES", "1.99"), ("fries", "LG FRIES", "2.49")]
    rows3 = [("drink", "SODA", "1.49"), ("drink", "SHAKE", "2.29"), ("fries", "PIE", "1.79")]
    draw_menu_board(pix, MENU_X, MENU_Y, "COMBOS", rows1, glow=True)
    draw_menu_board(pix, MENU_X + 96, MENU_Y, "MAINS", rows2, glow=True)
    draw_menu_board(pix, MENU_X + 192, MENU_Y, "SIDES", rows3, glow=True)
    # menu canopy / hood
    pix.bevel(MENU_X - 8, MENU_Y - 14, 300, 14, CHROME_DK, CHROME, CAR)
    pix.rect(MENU_X - 6, MENU_Y - 12, 296, 8, MENU_BG)
    text(pix, MENU_X + 70, MENU_Y - 11, "BURGER SPOT MENU", GLOW, font="3")

    # tile backsplash under the menu boards
    pix.rect(548, 136, 300, 64, RED_DK)
    for ty in range(136, 200, 16):
        for tx in range(548, 848, 16):
            col = CREAM if ((tx + ty) // 16) % 2 == 0 else RED
            pix.rect(tx, ty, 15, 15, col)
            pix.outline(tx, ty, 15, 15, RED_DK)
    pix.hline(548, 136, 300, CHROME)
    pix.hline(548, 199, 300, CHROME_DK)

    # counter
    draw_counter(pix, 560, 200, 390)
    # fictional shop badge on the counter front
    pix.bevel(620, 236, 70, 28, RED, RED_HI, RED_DK)
    text(pix, 628, 240, "BURGER", CREAM, font="3")
    text(pix, 634, 248, "SPOT", SODIUM_HI, font="3")
    pix.outline(620, 236, 70, 28, INK)

    # registers
    draw_register(pix, 580, 176)
    draw_register(pix, 670, 176)

    # "ORDER HERE" / "PICK UP" plaques
    pix.bevel(578, 164, 50, 10, RED, RED_HI, RED_DK)
    text(pix, 582, 166, "ORDER", CREAM, font="3")
    pix.bevel(668, 164, 50, 10, RED, RED_HI, RED_DK)
    text(pix, 674, 166, "PICK UP", CREAM, font="3")

    # soda fountain
    draw_soda_fountain(pix, FOUNTAIN_X, 164)

    # condiment station on the counter
    pix.bevel(880, 186, 50, 16, CREAM, CHROME_HI, CREAM_SH)
    draw_ketchup(pix, 886, 178, False)
    draw_ketchup(pix, 896, 178, True)
    draw_ketchup(pix, 906, 178, False)
    # napkin + straws
    pix.bevel(916, 180, 12, 10, CHROME, CHROME_HI, CHROME_DK)
    pix.rect(918, 182, 8, 6, CREAM)
    for i in range(4):
        pix.vline(926, 176 + i, 6, CHROME_HI if i % 2 == 0 else RED)

    # stacked cups / lids
    pix.rect(786, 186, 12, 14, RED)
    pix.rect(787, 184, 10, 3, CHROME)
    pix.rect(787, 181, 10, 3, CHROME)
    pix.rect(802, 186, 12, 14, RED_DK)
    pix.rect(803, 184, 10, 3, CHROME)

    # bag rack / to-go bags
    pix.rect(850, 176, 20, 16, CREAM_SH)
    pix.outline(850, 176, 20, 16, WALL_DK)
    pix.rect(852, 178, 16, 4, WALL_SH)
    pix.rect(872, 176, 16, 16, CREAM)
    pix.outline(872, 176, 16, 16, WALL_DK)

    # receipt spike / tip jar
    pix.rect(640, 188, 6, 12, CHROME)
    pix.p(643, 186, CHROME_HI)
    pix.rect(636, 190, 5, 6, CREAM)  # receipt
    pix.circle(720, 192, 6, CHROME)
    pix.circle(720, 192, 4, SODIUM_HI)  # tip jar coins
    pix.p(718, 190, SODIUM)

    # trash at the end of the counter / near door
    draw_trash(pix, 544, FLOOR_TOP)

    # tray return slot in the counter front
    pix.rect(760, 230, 36, 10, INK)
    pix.outline(760, 230, 36, 10, CHROME_DK)
    text(pix, 766, 232, "TRAYS", CHROME, font="3")

    # right-wall tiles / poster (parallax edge + visible sliver)
    pix.bevel(900, 48, 44, 60, CREAM, CHROME_HI, CREAM_SH)
    icon_burger(pix, 914, 58)
    text(pix, 908, 80, "EAT", RED, font="3")
    text(pix, 906, 88, "UP", RED, font="3")

    # clean wall between the last window and the menu boards
    # speaker
    pix.bevel(476, 48, 26, 14, CHROME_DK, CHROME, INK)
    pix.circle(489, 55, 5, CAR)
    pix.circle(489, 55, 2, CHROME)
    # clock — clear of the menus (menus start at 548)
    pix.circle(510, 58, 14, CHROME)
    pix.circle(510, 58, 12, CREAM)
    pix.line(510, 58, 510, 50, INK)
    pix.line(510, 58, 518, 60, INK)
    pix.p(510, 58, RED)
    # GAME NIGHT plaque above the jukebox
    pix.bevel(476, 70, 72, 14, RED, RED_HI, RED_DK)
    text(pix, 480, 73, "GAME NIGHT", CREAM, font="3")

    # jukebox sits on this wall, not in front of a window
    draw_jukebox(pix, 478, FLOOR_TOP)

    # floor
    draw_checkered_floor(pix, W_MID, rng)

    # shadows just at the furniture line (not into the fight band)
    pix.dith(150, FLOOR_TOP, 300, 3, INK, TILE_R, "h")
    pix.dith(560, FLOOR_TOP, 390, 4, COUNTER_DK, INK, "h")
    pix.dith(20, FLOOR_TOP, 120, 3, INK, TILE_R, "h")

    # a thin floor mat at the entrance (y=300-306 only)
    pix.rect(8, FLOOR_TOP, 44, 5, RED_DK)
    pix.dith(8, FLOOR_TOP, 44, 5, RED, RED_DK, "checker")

    return pix


def draw_anim(frame):
    pix = Pix(W_MID, H, None)

    # neon buzz
    buzz_sets = [set(), {2, 8}, {5}, {1, 9, 10}]  # letter indexes in "BURGER SPOT"
    on = frame != 3
    # overpaint sign cabinet area from mid by redrawing
    # also a sliver of ceiling behind chains is already mid; just redraw sign
    draw_neon_sign(pix, NEON_X, NEON_Y, on=on, buzz_mask=buzz_sets[frame])
    draw_open_sign(pix, OPEN_X, OPEN_Y, on=frame != 2)

    # menu board glow flicker
    glow = frame != 3
    rows1 = [("combo", "COMBO A", "5.99"), ("combo", "COMBO B", "6.49"), ("burger", "BIG BURGER", "4.79")]
    rows2 = [("burger", "BURGER", "3.49"), ("fries", "FRIES", "1.99"), ("fries", "LG FRIES", "2.49")]
    rows3 = [("drink", "SODA", "1.49"), ("drink", "SHAKE", "2.29"), ("fries", "PIE", "1.79")]
    draw_menu_board(pix, MENU_X, MENU_Y, "COMBOS", rows1, glow=glow or frame == 1)
    draw_menu_board(pix, MENU_X + 96, MENU_Y, "MAINS", rows2, glow=frame in (0, 1, 2))
    draw_menu_board(pix, MENU_X + 192, MENU_Y, "SIDES", rows3, glow=frame in (0, 2))
    # extra surge glow
    if frame == 1:
        pix.dith(MENU_X - 4, MENU_Y - 4, 292, 4, GLOW, SODIUM_HI, "h")

    # kids in booths (same table positions as mid)
    # Booth 1: two kids
    draw_kid_booth(pix, 186, 248, facing=1, frame=frame, hair="dark", action="eat")
    draw_kid_booth(pix, 246, 248, facing=-1, frame=frame, hair="blond", action="drink")
    # Booth 2
    draw_kid_booth(pix, 346, 248, facing=1, frame=(frame + 2) % 4, hair="brown", action="eat")
    draw_kid_booth(pix, 406, 248, facing=-1, frame=(frame + 1) % 4, hair="dark", action="talk")
    # Booth 3 margin
    draw_kid_booth(pix, 50, 254, facing=1, frame=frame, hair="brown", action="drink")

    # cashier at first register (~x=600)
    draw_cashier(pix, 610, 200, frame=frame, facing=-1)

    # a drip from a soda spigot
    drop_y = 190 + frame * 5
    pix.p(FOUNTAIN_X + 16, drop_y, NEON_C)
    pix.p(FOUNTAIN_X + 16, drop_y + 1, GLASS_HI)

    # parking-lot sodium flicker in the left window, kept off the band bus
    if frame in (1, 3):
        pix.dith(200, 108, 28, 18, SODIUM, GLASS, "bayer")
    if frame == 1:
        pix.dith(168, 118, 20, 14, SODIUM_HI, GLASS, "bayer")

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
    anims = [crunch(draw_anim(i).im, opaque=False) for i in range(4)]

    far.save(DIR / "far.png")
    mid.save(DIR / "mid.png")
    for i, im in enumerate(anims):
        im.save(DIR / f"anim_{i}.png")

    preview = crunch(compose_preview(far, mid, anims[0]).convert("RGBA"), opaque=True)
    preview.save(DIR / "preview.png")
    preview.resize((W_FAR * 2, H * 2), Image.Resampling.NEAREST).save(DIR / "preview@2x.png")

    def info(p, im):
        return f"{p.name} {im.size[0]}x{im.size[1]} {im.mode}"

    files = [far, mid, *anims, preview]
    names = ["far.png", "mid.png", "anim_0.png", "anim_1.png", "anim_2.png", "anim_3.png", "preview.png"]
    for n, im in zip(names, files):
        print(info(DIR / n, im))
    print(info(DIR / "preview@2x.png", Image.open(DIR / "preview@2x.png")))
    print("palette", len(PALETTE))


if __name__ == "__main__":
    main()
