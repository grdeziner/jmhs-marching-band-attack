#!/usr/bin/env python3
"""Generate Band Wars football-field stage layers.

Native view is 640x360. Mid/anim layers are 960x360 for parallax.
Crisp 1px pixels, no antialiasing, limited palette.
School colors (from the shared fighter palette): navy + gold + white trim.

Story beat: the last home game is over, stadium lights still hum, finals
are fought on the 50-yard line. Bleachers are mostly empty, with clusters
of JMHS band kids and a few lingering fans. Lights flicker, flags stir.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent
VIEW_W, VIEW_H = 640, 360
MID_W, MID_H = 960, 360
MID_OFFSET = (MID_W - VIEW_W) // 2  # 160 — center mid in the view
FLOOR_Y = 320
FLOOR_TOP = 300

# 8 px per yard; mid width = 120 yards (10-yard endzones + 100-yard field).
# Goal lines at x=80 and x=880. 50-yard line at x=480 (view center).
YARD = 8
GOAL_L, GOAL_R = 80, 880
FIFTY = 480


def C(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------------------
# Limited palette. Official JMHS uniform swatches are copied verbatim.
# ---------------------------------------------------------------------------
P = {
    # School / uniform (must match art/characters/tools/pxart/palette.py)
    "outline": C("#0A0B10"),
    "navy_dk": C("#0C1734"),
    "navy": C("#17305F"),
    "navy_lt": C("#3A5A9C"),
    "gold_dk": C("#7A5410"),
    "gold": C("#D4A017"),
    "gold_lt": C("#F5DE6A"),
    "white": C("#F6F2EA"),
    "white_sh": C("#B9B3A6"),
    "white_dk": C("#8B8578"),
    "skin_dk": C("#8E4E2C"),
    "skin": C("#E09A68"),
    "skin_lt": C("#F5C49A"),
    "hair": C("#1A1210"),
    "wood_dk": C("#5A3016"),
    "wood": C("#A05A28"),
    "wood_lt": C("#C47A44"),
    "shoe": C("#141418"),
    "flash": C("#FFF6C8"),
    # Extra skin ramps for the crowd (still tight)
    "skin_b_dk": C("#3A2218"),
    "skin_b": C("#6B3E28"),
    "skin_b_lt": C("#A06640"),
    "skin_c_dk": C("#A07050"),
    "skin_c": C("#E8B898"),
    "skin_c_lt": C("#F8DCC8"),
    # Hair variants
    "hair_br": C("#3A2218"),
    "hair_bl": C("#C4A056"),
    "hair_rd": C("#6A2818"),
    # Sky (night, slightly navy)
    "sky0": C("#070A14"),
    "sky1": C("#0C1020"),
    "sky2": C("#12182C"),
    "sky3": C("#182038"),
    "sky4": C("#1E2A48"),
    "sky5": C("#263456"),
    "sky6": C("#304060"),
    "sky_moon": C("#3A4A6C"),  # hard halo band, not a blur
    # Moon / stars
    "moon": C("#E8E8D0"),
    "moon2": C("#C4C4B0"),
    "moon3": C("#8E8E7A"),
    "star": C("#F0F4FF"),
    "star2": C("#B4C4DC"),
    "star3": C("#FFF0B0"),
    # Far landscape
    "hill0": C("#0A1410"),
    "hill1": C("#101C16"),
    "hill2": C("#16241C"),
    "tree": C("#08160E"),
    "bldg": C("#1A1E28"),
    "bldg2": C("#12151C"),
    "bldg3": C("#242834"),
    "win_on": C("#E8B44A"),
    "win_dim": C("#8A6020"),
    "park": C("#CC8820"),
    "tower": C("#2A2E36"),
    "tower2": C("#1A1E24"),
    "tower3": C("#3A3E46"),
    # Stadium steel / concrete
    "steel_dk": C("#1A1C22"),
    "steel": C("#2C3038"),
    "steel_lt": C("#4A4E58"),
    "steel_hi": C("#6A6E78"),
    "conc_dk": C("#2A2C30"),
    "conc": C("#3A3E44"),
    "conc_lt": C("#52565E"),
    "conc_hi": C("#6A6E74"),
    "seat": C("#262A32"),
    "seat_lt": C("#343842"),
    "seat_dk": C("#181C22"),
    "riser": C("#20242C"),
    "rail": C("#8A8E96"),
    "rail_dk": C("#4A4E56"),
    # Lights
    "lamp": C("#FFF4C0"),
    "lamp2": C("#FFE070"),
    "lamp3": C("#E0A030"),
    "lamp_off": C("#6A5840"),
    "lamp_cage": C("#3A3E46"),
    "glow1": C("#FFF8D0"),
    "glow2": C("#E8C860"),
    "glow3": C("#A07828"),
    "beacon": C("#E03030"),
    "beacon_dk": C("#6A1010"),
    # Turf (lit by warm stadium lamps — slightly yellow-green)
    "turf0": C("#145024"),
    "turf1": C("#1C6830"),
    "turf2": C("#24783A"),
    "turf3": C("#2C8C44"),
    "turf4": C("#186028"),
    "turf_end": C("#143C28"),  # navy-tinted endzone grass
    "turf_end2": C("#104020"),
    "line": C("#F0EDE4"),
    "line_dk": C("#C8C4B8"),
    "track": C("#6A3A28"),
    "track2": C("#5A3020"),
    "track3": C("#7A4A34"),
    "track_line": C("#D8D0C0"),
    # Goal posts
    "post": C("#E8C430"),
    "post_dk": C("#A08418"),
    "post_lt": C("#F8E878"),
    # Misc
    "case": C("#2A1A10"),
    "case2": C("#4A2A18"),
    "podium": C("#3A2A18"),
}

SKINS = [
    (P["skin_dk"], P["skin"], P["skin_lt"]),
    (P["skin_b_dk"], P["skin_b"], P["skin_b_lt"]),
    (P["skin_c_dk"], P["skin_c"], P["skin_c_lt"]),
]
HAIRS = [P["hair"], P["hair_br"], P["hair_bl"], P["hair_rd"], P["navy_dk"]]


# ---------------------------------------------------------------------------
# Canvas — integer pixels only, alpha 0 or 255, no blending.
# ---------------------------------------------------------------------------
class CV:
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        if bg is None:
            self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        elif len(bg) == 3:
            self.im = Image.new("RGB", (w, h), bg)
        else:
            self.im = Image.new("RGBA", (w, h), bg)
        self.px = self.im.load()
        self.rgba = self.im.mode == "RGBA"

    def p(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            if self.rgba:
                self.px[x, y] = (c[0], c[1], c[2], 255) if len(c) == 3 else c
            else:
                self.px[x, y] = c[:3]

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[x, y]
        return None

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                self.p(xx, yy, c)

    def hline(self, x1, x2, y, c):
        if x2 < x1:
            x1, x2 = x2, x1
        for x in range(x1, x2 + 1):
            self.p(x, y, c)

    def vline(self, x, y1, y2, c):
        if y2 < y1:
            y1, y2 = y2, y1
        for y in range(y1, y2 + 1):
            self.p(x, y, c)

    def frame(self, x, y, w, h, c):
        self.hline(x, x + w - 1, y, c)
        self.hline(x, x + w - 1, y + h - 1, c)
        self.vline(x, y, y + h - 1, c)
        self.vline(x + w - 1, y, y + h - 1, c)

    def fill_circle(self, cx, cy, r, c):
        r2 = r * r
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            for x in range(cx - r, cx + r + 1):
                dx = x - cx
                if dx * dx + dy * dy <= r2:
                    self.p(x, y, c)

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ry and rx and ((x - cx) * (x - cx)) * (ry * ry) + ((y - cy) * (y - cy)) * (rx * rx) <= rx * rx * ry * ry:
                    self.p(x, y, c)

    def stamp(self, ox, oy, rows, mapping):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in mapping and mapping[ch] is not None:
                    self.p(ox + i, oy + j, mapping[ch])

    def save(self, path):
        self.im.save(path)


# 5x7 pixel font (A-Z, 0-9, and a few marks). Each glyph is 5 wide, 7 tall.
_F = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["01110", "10001", "00001", "00110", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00100", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "&": ["01100", "10010", "10010", "01100", "10101", "10010", "01101"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


def text_width(s, scale=1, spacing=1):
    return len(s) * (5 * scale + spacing) - spacing


def draw_text(cv, x, y, s, color, scale=1, spacing=1):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = _F.get(ch, _F[" "])
        for j, row in enumerate(glyph):
            for i, bit in enumerate(row):
                if bit == "1":
                    if scale == 1:
                        cv.p(cx + i, y + j, color)
                    else:
                        cv.rect(cx + i * scale, y + j * scale, scale, scale, color)
        cx += 5 * scale + spacing
    return cx




# ---------------------------------------------------------------------------
# FAR layer — 640x360 opaque. Sky, moon, stars, distant landscape.
# ---------------------------------------------------------------------------
def draw_far() -> CV:
    cv = CV(VIEW_W, VIEW_H, bg=P["sky0"])
    # Banded night sky (hard steps, no gradients)
    bands = [
        (0, 36, "sky0"),
        (36, 70, "sky1"),
        (70, 100, "sky2"),
        (100, 122, "sky3"),
        (122, 138, "sky4"),
        (138, 150, "sky5"),
        (150, 168, "sky6"),
    ]
    for y0, y1, k in bands:
        cv.rect(0, y0, VIEW_W, y1 - y0, P[k])

    # Hard moon halo (concentric rings of sky color, not blur)
    mx, my, mr = 548, 44, 16
    cv.fill_circle(mx, my, mr + 8, P["sky_moon"])
    cv.fill_circle(mx, my, mr + 4, P["sky6"])
    cv.fill_circle(mx, my, mr, P["moon"])
    cv.fill_circle(mx - 3, my - 2, 4, P["moon2"])  # shallow crater
    cv.fill_circle(mx + 5, my + 3, 3, P["moon2"])
    cv.fill_circle(mx + 2, my - 6, 2, P["moon3"])
    cv.p(mx + 7, my - 4, P["moon3"])
    # lit rim
    for a in range(-mr, mr + 1):
        cv.p(mx + 10, my + a, P["moon2"]) if abs(a) < 8 else None

    # A few flat cloud wisps (hard shapes)
    def cloud(x, y, w, h, col):
        cv.rect(x + 4, y, w - 8, h, col)
        cv.rect(x, y + 2, w, h - 3, col)
        cv.rect(x + 10, y - 2, w // 3, h, col)

    cloud(40, 58, 70, 7, P["sky3"])
    cloud(90, 64, 50, 5, P["sky4"])
    cloud(400, 30, 80, 6, P["sky2"])
    cloud(430, 36, 44, 5, P["sky3"])
    cloud(220, 48, 60, 5, P["sky3"])

    # Stars — deterministic
    rng = random.Random(640360)
    for _ in range(90):
        x = rng.randint(0, VIEW_W - 1)
        y = rng.randint(2, 130)
        # fewer stars near horizon
        if y > 90 and rng.random() < 0.55:
            continue
        col = rng.choice([P["star"], P["star"], P["star2"], P["star2"], P["star3"]])
        cv.p(x, y, col)
        if rng.random() < 0.12 and y < 80:
            # 2px plus-shaped brighter star
            cv.p(x + 1, y, col)
            cv.p(x, y + 1, col)
            cv.p(x - 1, y, P["star2"])
            cv.p(x, y - 1, P["star2"])

    # Distant rolling hills / tree line
    rng2 = random.Random(77)
    # back hill
    for x in range(VIEW_W):
        h = 14 + int(6 * (0.5 + 0.5 * __import__("math").sin(x * 0.02 + 1.2)))
        h += int(3 * (0.5 + 0.5 * __import__("math").sin(x * 0.07)))
        ytop = 150 - h
        cv.rect(x, ytop, 1, 170 - ytop, P["hill0"])
    # front tree line with irregular treetops
    for x in range(VIEW_W):
        h = 10 + int(8 * (0.5 + 0.5 * __import__("math").sin(x * 0.05 + 0.4)))
        h += int(4 * (0.5 + 0.5 * __import__("math").sin(x * 0.13 + 2)))
        if rng2.random() < 0.08:
            h += rng2.randint(4, 10)  # taller tree
        ytop = 158 - h
        cv.rect(x, ytop, 1, 180 - ytop, P["hill1"])
    # individual tree blobs
    for x in range(8, VIEW_W, rng2.randint(7, 12)):
        th = rng2.randint(8, 18)
        tw = rng2.randint(5, 10)
        ty = 156 - th
        cv.fill_ellipse(x, ty + tw // 3, tw // 2, tw // 2 + 1, P["tree"])
        cv.rect(x - tw // 2, ty + tw // 3, tw, 162 - (ty + tw // 3), P["hill1"])
        # re-roll step by continuing; step is fixed-ish
    # denser trees, second pass with fixed positions
    for x, th, tw in [
        (20, 16, 9), (36, 12, 7), (52, 18, 10), (70, 11, 6),
        (110, 15, 8), (128, 20, 11), (150, 13, 7), (200, 17, 9),
        (230, 12, 6), (248, 14, 8), (300, 11, 7), (330, 16, 9),
        (360, 13, 7), (390, 19, 10), (420, 12, 6), (450, 15, 8),
        (480, 11, 7), (510, 14, 8), (580, 17, 9), (605, 13, 7),
        (622, 15, 8), (90, 10, 5), (175, 14, 7), (270, 12, 6),
        (540, 16, 8), (560, 12, 6),
    ]:
        ty = 157 - th
        cv.fill_ellipse(x, ty + 3, tw // 2, tw // 2, P["tree"])
        cv.rect(x - 1, ty + 4, 3, 162 - (ty + 4), P["hill2"])

    # Ground fill under the tree line so the far layer is fully opaque
    cv.rect(0, 160, VIEW_W, VIEW_H - 160, P["hill0"])
    # slightly lighter strip just below trees (distant field / parking)
    cv.rect(0, 160, VIEW_W, 8, P["hill1"])
    cv.rect(0, 168, VIEW_W, 6, P["hill0"])

    # Water tower (left) — classic high-school silhouette
    tx, ty = 86, 108
    # truss legs
    for i, xoff in enumerate((-7, 7)):
        cv.vline(tx + xoff, ty + 14, 160, P["tower2"])
        cv.vline(tx + xoff + 1, ty + 14, 160, P["tower"])
    cv.vline(tx, ty + 14, 160, P["tower2"])  # center pipe
    # cross braces
    for y in range(ty + 20, 158, 8):
        cv.hline(tx - 7, tx + 8, y, P["tower2"])
    # tank
    cv.fill_ellipse(tx, ty + 6, 11, 9, P["tower"])
    cv.fill_ellipse(tx, ty + 4, 11, 8, P["tower3"])
    cv.rect(tx - 11, ty + 6, 23, 8, P["tower"])
    cv.rect(tx - 11, ty + 6, 23, 2, P["tower3"])
    # peak + finial
    cv.rect(tx - 3, ty - 4, 7, 4, P["tower3"])
    cv.vline(tx, ty - 10, ty - 4, P["rail"])
    cv.p(tx, ty - 11, P["beacon_dk"])  # unlit in far (anim will blink a mid/near beacon)

    # School building, mid-left behind trees (long low brick/gym)
    bx, by, bw, bh = 250, 138, 130, 24
    cv.rect(bx, by, bw, bh, P["bldg"])
    cv.rect(bx, by, bw, 2, P["bldg3"])  # roofline
    # gym roof bump
    cv.rect(bx + 70, by - 10, 50, 12, P["bldg2"])
    cv.rect(bx + 70, by - 10, 50, 2, P["bldg3"])
    # narrow windows, some lit
    rng3 = random.Random(12)
    for i in range(14):
        wx = bx + 6 + i * 9
        wy = by + 8
        on = i in (2, 5, 6, 11, 13)
        cv.rect(wx, wy, 5, 6, P["win_on"] if on else P["win_dim"] if i % 3 == 0 else P["bldg2"])
        cv.vline(wx + 2, wy, wy + 5, P["bldg2"])
    # flagpole by the school (tiny)
    cv.vline(bx - 4, by - 16, by + 8, P["rail_dk"])
    cv.rect(bx - 3, by - 15, 7, 4, P["navy"])
    cv.p(bx + 1, by - 14, P["gold"])

    # Another low building / field house further right
    bx2 = 420
    cv.rect(bx2, 144, 70, 18, P["bldg2"])
    cv.rect(bx2, 144, 70, 2, P["bldg3"])
    for i in range(6):
        cv.rect(bx2 + 6 + i * 11, 150, 6, 5, P["win_dim"] if i not in (1, 4) else P["win_on"])

    # Parking-lot lights (tiny orange dots on poles), right and left
    for x, yb in [
        (30, 162), (50, 164), (70, 163),
        (190, 161), (210, 163),
        (500, 162), (520, 164), (545, 163), (570, 165),
        (600, 162), (620, 164),
    ]:
        cv.vline(x, yb - 10, yb, P["tower2"])
        cv.p(x, yb - 11, P["park"])
        cv.p(x - 1, yb - 11, P["lamp3"])

    # A few distant car/window glints in the parking
    for x, y in [(34, 166), (58, 167), (198, 166), (508, 167), (528, 166), (574, 168), (608, 167)]:
        cv.p(x, y, P["win_dim"])

    # Fill remainder already done; darken the very bottom so mid always covers it
    cv.rect(0, 180, VIEW_W, VIEW_H - 180, P["hill0"])
    return cv




# ---------------------------------------------------------------------------
# MID layer — 960x360, transparent sky, opaque structure + floor.
# ---------------------------------------------------------------------------
def _lamp_bank(cv: CV, cx: int, top: int, cols=5, rows=4, tilt=0):
    """Draw a rectangular stadium lamp cage. tilt: -1 left, 0, +1 right (shifts rows)."""
    lamp_w, lamp_h, gap = 6, 5, 2
    pad = 3
    bw = cols * (lamp_w + gap) - gap + pad * 2
    bh = rows * (lamp_h + gap) - gap + pad * 2
    x0 = cx - bw // 2
    y0 = top
    # cage
    cv.rect(x0, y0, bw, bh, P["steel_dk"])
    cv.frame(x0, y0, bw, bh, P["steel_hi"])
    cv.frame(x0 + 1, y0 + 1, bw - 2, bh - 2, P["steel"])
    # mount / visor
    cv.rect(x0 - 1, y0 - 3, bw + 2, 3, P["steel_lt"])
    cv.hline(x0 - 1, x0 + bw, y0 - 3, P["steel_hi"])
    # lamps (base ON state — anim flickers over these)
    for r in range(rows):
        shift = tilt * r
        for c in range(cols):
            lx = x0 + pad + c * (lamp_w + gap) + shift
            ly = y0 + pad + r * (lamp_h + gap)
            cv.rect(lx, ly, lamp_w, lamp_h, P["lamp2"])
            cv.rect(lx + 1, ly + 1, lamp_w - 2, lamp_h - 2, P["lamp"])
            cv.p(lx + 1, ly + 1, P["flash"])  # hot highlight
            # fixture lip
            cv.hline(lx, lx + lamp_w - 1, ly + lamp_h - 1, P["lamp3"])
    return x0, y0, bw, bh


def _tower(cv: CV, cx: int, bank_top: int, base_y: int, tilt=0, cols=5, rows=4):
    x0, y0, bw, bh = _lamp_bank(cv, cx, bank_top, cols=cols, rows=rows, tilt=tilt)
    # pole
    pole_top = y0 + bh
    cv.rect(cx - 3, pole_top, 7, base_y - pole_top, P["steel"])
    cv.vline(cx - 3, pole_top, base_y, P["steel_dk"])
    cv.vline(cx + 3, pole_top, base_y, P["steel_lt"])
    # cross-braced mid section (truss look)
    for y in range(pole_top + 8, base_y - 10, 10):
        cv.hline(cx - 3, cx + 3, y, P["steel_dk"])
        cv.p(cx - 2, y + 4, P["steel_dk"])
        cv.p(cx + 2, y + 6, P["steel_dk"])
    # base footing
    cv.rect(cx - 8, base_y - 6, 17, 6, P["conc"])
    cv.rect(cx - 10, base_y - 2, 21, 3, P["conc_dk"])
    cv.hline(cx - 8, cx + 8, base_y - 6, P["conc_lt"])
    return (x0, y0, bw, bh)


def _goal_post(cv: CV, x_goal: int, facing=1):
    """Yellow goal post at a goal line. facing: 1 posts go toward midfield (right of left goal)."""
    # The post sits just behind the goal line, slightly "into" the endzone visually,
    # but the uprights are the iconic Y. Base at the back of the endzone? No —
    # at the goal line, slightly off the fight floor (base at y=300, on the sideline
    # edge of the field). Uprights rise in front of the stands.
    base_y = FLOOR_TOP
    cross_y = 228
    top_y = 168
    # offset the stem a few px into the endzone so the goal line stays clean
    stem_x = x_goal - facing * 6
    # stem
    cv.rect(stem_x - 2, cross_y, 5, base_y - cross_y, P["post"])
    cv.vline(stem_x - 2, cross_y, base_y, P["post_dk"])
    cv.vline(stem_x + 2, cross_y, base_y, P["post_lt"])
    # padded base
    cv.rect(stem_x - 5, base_y - 10, 11, 10, P["post_dk"])
    cv.rect(stem_x - 4, base_y - 9, 9, 8, P["post"])
    cv.rect(stem_x - 6, base_y - 2, 13, 2, P["white_dk"])
    # crossbar
    half = 28
    cv.rect(stem_x - half, cross_y, half * 2 + 5, 4, P["post"])
    cv.hline(stem_x - half, stem_x + half + 4, cross_y, P["post_lt"])
    cv.hline(stem_x - half, stem_x + half + 4, cross_y + 3, P["post_dk"])
    # uprights
    for ux in (stem_x - half, stem_x + half):
        cv.rect(ux, top_y, 4, cross_y - top_y + 4, P["post"])
        cv.vline(ux, top_y, cross_y + 3, P["post_lt"])
        cv.vline(ux + 3, top_y, cross_y + 3, P["post_dk"])
        cv.rect(ux, top_y, 4, 2, P["post_lt"])  # cap


def _scoreboard(cv: CV):
    # Gantry / truss above the press box, board hanging from it
    gx0, gx1 = 360, 600
    gy = 16
    cv.rect(gx0, gy, gx1 - gx0, 6, P["steel"])
    cv.hline(gx0, gx1 - 1, gy, P["steel_hi"])
    cv.hline(gx0, gx1 - 1, gy + 5, P["steel_dk"])
    # truss Xs
    for x in range(gx0 + 8, gx1, 16):
        cv.p(x, gy + 1, P["steel_dk"])
        cv.p(x + 4, gy + 2, P["steel_dk"])
        cv.p(x + 8, gy + 1, P["steel_dk"])
    # hangers
    for hx in (390, 480, 570):
        cv.vline(hx, gy + 6, 26, P["steel_lt"])
        cv.vline(hx + 1, gy + 6, 26, P["steel_dk"])

    # Board body
    bx, by, bw, bh = 392, 26, 176, 70
    cv.rect(bx - 3, by - 3, bw + 6, bh + 6, P["steel_dk"])
    cv.frame(bx - 3, by - 3, bw + 6, bh + 6, P["steel_hi"])
    cv.rect(bx, by, bw, bh, P["outline"])  # black face
    cv.frame(bx, by, bw, bh, P["navy_lt"])
    cv.frame(bx + 1, by + 1, bw - 2, bh - 2, P["navy"])

    # Title bar
    cv.rect(bx + 4, by + 4, bw - 8, 13, P["navy"])
    tw = text_width("BAND WARS", scale=1, spacing=1)
    draw_text(cv, bx + (bw - tw) // 2, by + 6, "BAND WARS", P["gold_lt"], scale=1, spacing=1)

    # Score row: JMHS  21     17  VISIT
    draw_text(cv, bx + 8, by + 22, "JMHS", P["gold"], scale=1, spacing=1)
    draw_text(cv, bx + bw - 8 - text_width("VISIT"), by + 22, "VISIT", P["white_sh"], scale=1, spacing=1)
    # big scores
    draw_text(cv, bx + 40, by + 32, "21", P["flash"], scale=2, spacing=1)
    draw_text(cv, bx + bw - 40 - text_width("17", scale=2), by + 32, "17", P["flash"], scale=2, spacing=1)

    # Bottom ticker: 4TH  0:00   FINALS
    cv.rect(bx + 4, by + bh - 16, bw - 8, 12, P["navy_dk"])
    draw_text(cv, bx + 8, by + bh - 14, "4TH 0:00", P["white"], scale=1, spacing=1)
    draw_text(cv, bx + bw - 8 - text_width("FINALS"), by + bh - 14, "FINALS", P["gold"], scale=1, spacing=1)

    # small amber lamps along the top edge of the board
    for i, lx in enumerate(range(bx + 8, bx + bw - 6, 8)):
        cv.rect(lx, by + 2, 3, 2, P["lamp3"] if i % 2 == 0 else P["lamp2"])


def _press_box(cv: CV):
    px, py, pw, ph = 368, 100, 224, 52
    # roof
    cv.rect(px - 6, py - 6, pw + 12, 8, P["conc"])
    cv.hline(px - 6, px + pw + 5, py - 6, P["conc_hi"])
    cv.rect(px - 4, py - 8, pw + 8, 3, P["conc_lt"])  # parapet
    # body
    cv.rect(px, py, pw, ph, P["conc"])
    cv.rect(px, py, pw, ph, P["conc"])
    cv.vline(px, py, py + ph - 1, P["conc_dk"])
    cv.vline(px + pw - 1, py, py + ph - 1, P["conc_lt"])
    # mid cornice
    cv.hline(px, px + pw - 1, py + 24, P["conc_dk"])
    cv.rect(px, py + 24, pw, 3, P["conc_lt"])
    # two rows of windows, warm interior
    def windows(y, n=9):
        gap = 4
        ww, wh = 18, 14
        total = n * ww + (n - 1) * gap
        x0 = px + (pw - total) // 2
        for i in range(n):
            wx = x0 + i * (ww + gap)
            cv.rect(wx - 1, y - 1, ww + 2, wh + 2, P["outline"])
            # warm glow glass
            cv.rect(wx, y, ww, wh, P["win_on"] if i not in (3, 7) else P["win_dim"])
            # mullion
            cv.vline(wx + ww // 2, y, y + wh - 1, P["bldg2"])
            cv.hline(wx, wx + ww - 1, y + 6, P["bldg2"])
            # silhouettes in a few windows (announcers)
            if i in (1, 2, 5, 8):
                headx = wx + 5 + (i % 3)
                cv.rect(headx, y + 8, 3, 3, P["outline"])
                cv.rect(headx - 1, y + 11, 5, 3, P["outline"])

    windows(py + 4, 9)
    windows(py + 30, 9)
    # antenna + beacon mast on the roof
    ax = px + pw - 16
    cv.vline(ax, py - 28, py - 8, P["steel_hi"])
    cv.vline(ax + 1, py - 28, py - 8, P["steel"])
    cv.p(ax, py - 29, P["beacon"])  # mid has it ON; anim may blink
    cv.p(ax + 1, py - 29, P["beacon"])
    cv.p(ax, py - 30, P["lamp"])
    # small dish
    cv.rect(px + 20, py - 12, 8, 4, P["steel_lt"])
    cv.vline(px + 24, py - 16, py - 8, P["steel"])
    # support columns down into the stands
    for cx in (px + 16, px + pw // 2, px + pw - 17):
        cv.rect(cx - 3, py + ph, 7, 8, P["conc_dk"])


def _bleachers(cv: CV):
    top, bot = 152, 288
    nrows = 8
    row_h = (bot - top) // nrows  # 17
    # backing wall behind top row
    cv.rect(8, top - 6, MID_W - 16, 8, P["conc_dk"])
    cv.hline(8, MID_W - 9, top - 6, P["conc"])
    # full bleacher mass
    cv.rect(4, top, MID_W - 8, bot - top, P["seat_dk"])

    for r in range(nrows):
        y = top + r * row_h
        # riser
        cv.rect(4, y, MID_W - 8, 2, P["riser"])
        cv.hline(4, MID_W - 5, y, P["steel_dk"])
        # seat back
        cv.rect(4, y + 2, MID_W - 8, 3, P["seat"])
        cv.hline(4, MID_W - 5, y + 2, P["seat_lt"])
        # bench
        cv.rect(4, y + 5, MID_W - 8, row_h - 5, P["seat_dk"])
        cv.rect(4, y + row_h - 3, MID_W - 8, 2, P["seat"])
        cv.hline(4, MID_W - 5, y + row_h - 1, P["steel_dk"])
        # seat dividers every 8 px (individual seats)
        for x in range(8, MID_W - 8, 8):
            cv.p(x, y + 3, P["seat_dk"])
            cv.p(x, y + row_h - 3, P["seat_lt"])

    # aisles / stairs (lighter, with tread lines)
    aisles = [80, 200, 320, 480, 640, 760, 880]
    for ax in aisles:
        cv.rect(ax - 7, top, 15, bot - top, P["conc"])
        for r in range(nrows):
            y = top + r * row_h
            cv.hline(ax - 7, ax + 7, y + row_h - 1, P["conc_dk"])
            cv.hline(ax - 7, ax + 7, y + row_h - 2, P["conc_lt"])
        # handrails
        cv.vline(ax - 7, top, bot - 1, P["rail_dk"])
        cv.vline(ax + 7, top, bot - 1, P["rail_dk"])
        for r in range(nrows):
            cv.p(ax - 7, top + r * row_h + 2, P["rail"])
            cv.p(ax + 7, top + r * row_h + 2, P["rail"])

    # navy + gold bunting along the front fascia
    fy = bot - 2
    cv.rect(4, fy - 10, MID_W - 8, 12, P["navy_dk"])
    cv.rect(4, fy - 10, MID_W - 8, 3, P["navy"])
    cv.hline(4, MID_W - 5, fy - 10, P["gold"])
    cv.hline(4, MID_W - 5, fy - 7, P["gold_dk"])
    # hanging pennants
    for x in range(12, MID_W - 12, 16):
        col = P["navy"] if (x // 16) % 2 == 0 else P["gold"]
        col2 = P["navy_dk"] if col == P["navy"] else P["gold_dk"]
        cv.rect(x, fy - 6, 10, 6, col)
        # triangle tip
        cv.p(x + 4, fy, col)
        cv.p(x + 5, fy, col)
        cv.p(x + 3, fy, col2)
        cv.p(x + 6, fy, col2)

    # "GO JMHS" banner over the center fascia (between aisles around 50)
    bw = text_width("GO JMHS", scale=1, spacing=1)
    bx = FIFTY - bw // 2 - 6
    cv.rect(bx, bot - 22, bw + 12, 11, P["navy"])
    cv.frame(bx, bot - 22, bw + 12, 11, P["gold"])
    draw_text(cv, bx + 6, bot - 20, "GO JMHS", P["gold_lt"], scale=1, spacing=1)

    # front railing
    cv.rect(2, bot, MID_W - 4, 3, P["rail_dk"])
    cv.hline(2, MID_W - 3, bot, P["rail"])
    for x in range(6, MID_W - 4, 6):
        cv.vline(x, bot, bot + 6, P["rail_dk"])
    cv.hline(2, MID_W - 3, bot + 6, P["rail"])


def _track_and_sideline(cv: CV):
    # cinder/rubber track between railing and turf, y=288-300
    cv.rect(0, 288, MID_W, 12, P["track"])
    # lane line
    cv.hline(0, MID_W - 1, 291, P["track_line"])
    cv.hline(0, MID_W - 1, 296, P["track2"])
    # slight texture (sparse darker crumbs)
    rng = random.Random(300)
    for _ in range(180):
        x = rng.randint(0, MID_W - 1)
        y = rng.randint(288, 299)
        cv.p(x, y, P["track2"] if rng.random() < 0.7 else P["track3"])

    # sideline objects — stay at y<=299, never into the fight floor
    # empty band podium, left-center
    cv.rect(300, 292, 22, 8, P["podium"])
    cv.rect(300, 292, 22, 2, P["wood"])
    cv.vline(300, 292, 299, P["wood_dk"])
    cv.vline(321, 292, 299, P["wood_dk"])
    # instrument cases on the track, left and right
    for x, w in ((150, 16), (178, 12), (790, 16), (814, 14)):
        cv.rect(x, 293, w, 7, P["case"])
        cv.rect(x + 1, 294, w - 2, 3, P["case2"])
        cv.hline(x, x + w - 1, 293, P["wood"])
        cv.p(x + w - 3, 296, P["gold_dk"])  # latch
    # first-down marker / chain pole, right of midfield at the sideline
    cv.rect(560, 276, 3, 24, P["gold"])
    cv.vline(560, 276, 299, P["gold_dk"])
    cv.vline(562, 276, 299, P["gold_lt"])
    cv.rect(557, 274, 9, 5, P["gold_lt"])
    # water cooler
    cv.rect(700, 290, 10, 10, P["white_dk"])
    cv.rect(701, 291, 8, 6, P["navy_lt"])
    cv.rect(703, 289, 4, 2, P["white"])
    cv.rect(702, 297, 6, 3, P["white_sh"])
    # flag poles (flags themselves are in the anim layer)
    for fx in (16, 120, 328, 600, 752, 880):
        cv.vline(fx, 248, 299, P["steel_hi"])
        cv.vline(fx + 1, 248, 299, P["steel"])
        cv.rect(fx - 2, 298, 6, 2, P["steel_dk"])  # base


def _field(cv: CV):
    """Turf y=300..359. Clean, readable, uncluttered. Fighters' feet at y=320."""
    # base fill
    cv.rect(0, FLOOR_TOP, MID_W, MID_H - FLOOR_TOP, P["turf1"])
    # 5-yard alternating stripes (40 px). Align to yard lines.
    # Stripe 0 starts at goal line (x=80). Endzones get a navy-tinted grass.
    cv.rect(0, FLOOR_TOP, GOAL_L, MID_H - FLOOR_TOP, P["turf_end"])
    cv.rect(GOAL_R, FLOOR_TOP, MID_W - GOAL_R, MID_H - FLOOR_TOP, P["turf_end"])
    # faint gold endzone hint (not letters in the fight band — letters stay high)
    for x0, x1 in ((8, GOAL_L - 8), (GOAL_R + 8, MID_W - 8)):
        # thin gold inner box at the top of the endzone only (y=301-308)
        cv.hline(x0, x1, FLOOR_TOP + 1, P["gold_dk"])
    # JMHS in endzones, only in the top 10 px of the turf so the fight band stays clean
    for origin, facing in ((16, 1), (MID_W - 16, -1)):
        # draw vertical-ish stacked letters? horizontal is fine, mostly off-view
        s = "JMHS"
        if facing == 1:
            draw_text(cv, origin, FLOOR_TOP + 2, s, P["gold"], scale=1, spacing=1)
        else:
            w = text_width(s, scale=1, spacing=1)
            draw_text(cv, origin - w, FLOOR_TOP + 2, s, P["gold"], scale=1, spacing=1)

    # in-field 5-yard stripes
    x = GOAL_L
    stripe = 0
    while x < GOAL_R:
        w = YARD * 5  # 40
        if stripe % 2 == 1:
            cv.rect(x, FLOOR_TOP, w, MID_H - FLOOR_TOP, P["turf3"])
        else:
            cv.rect(x, FLOOR_TOP, w, MID_H - FLOOR_TOP, P["turf1"])
        x += w
        stripe += 1

    # sideline (top of floor band)
    cv.hline(0, MID_W - 1, FLOOR_TOP, P["line"])
    cv.hline(0, MID_W - 1, FLOOR_TOP + 1, P["line_dk"])

    # 10-yard lines (1px white), full height of the floor
    for yard in range(0, 101, 10):
        x = GOAL_L + yard * YARD
        col = P["line"]
        cv.vline(x, FLOOR_TOP, MID_H - 1, col)
        # slightly thicker 50
        if yard == 50:
            cv.vline(x - 1, FLOOR_TOP, MID_H - 1, P["line_dk"])
            cv.vline(x + 1, FLOOR_TOP, MID_H - 1, P["line_dk"])
            cv.vline(x, FLOOR_TOP, MID_H - 1, P["line"])

    # 5-yard hash ticks ONLY at the top (y=302-307) and very bottom (y=354-359)
    # so the fight band y=308..353 stays clean aside from the 10-yard lines.
    for yard in range(0, 101, 5):
        x = GOAL_L + yard * YARD
        if yard % 10 == 0:
            continue
        cv.vline(x, FLOOR_TOP + 2, FLOOR_TOP + 7, P["line_dk"])
        cv.vline(x, MID_H - 6, MID_H - 1, P["line_dk"])

    # Yard numbers at the TOP of the turf only (y=304-312), not through the feet line.
    # 20, 30, 40, 50, 40, 30, 20  (10s sit at the view edge)
    def yard_num(yard, label):
        x = GOAL_L + yard * YARD
        w = text_width(label, scale=1, spacing=1)
        draw_text(cv, x - w // 2, FLOOR_TOP + 4, label, P["line"], scale=1, spacing=1)

    yard_num(20, "20")
    yard_num(30, "30")
    yard_num(40, "40")
    yard_num(50, "50")
    yard_num(60, "40")
    yard_num(70, "30")
    yard_num(80, "20")

    # Very subtle darker near-ground at the bottom (depth), still clean
    cv.rect(0, 354, MID_W, 6, P["turf0"])
    # re-draw yard lines over the shadow so they stay continuous
    for yard in range(0, 101, 10):
        x = GOAL_L + yard * YARD
        cv.vline(x, 354, MID_H - 1, P["line"])
        if yard == 50:
            cv.vline(x - 1, 354, MID_H - 1, P["line_dk"])
            cv.vline(x + 1, 354, MID_H - 1, P["line_dk"])
            cv.vline(x, 354, MID_H - 1, P["line"])
    # re-draw sideline already done

    # sparse grass specks — only in y=301-312 and y=348-353, never in the fight strip
    rng = random.Random(50)
    for _ in range(220):
        x = rng.randint(0, MID_W - 1)
        if rng.random() < 0.6:
            y = rng.randint(FLOOR_TOP + 2, FLOOR_TOP + 12)
        else:
            y = rng.randint(348, 353)
        cv.p(x, y, P["turf4"] if rng.random() < 0.7 else P["turf3"])

    # goal lines already drawn as yard 0 and 100; add a thin gold hash just inside each endzone top
    cv.vline(GOAL_L - 1, FLOOR_TOP, FLOOR_TOP + 8, P["gold_dk"])
    cv.vline(GOAL_R + 1, FLOOR_TOP, FLOOR_TOP + 8, P["gold_dk"])


def draw_mid() -> CV:
    cv = CV(MID_W, MID_H, bg=None)  # transparent sky
    # Light towers (back of stands). Two main (visible) + two edge (parallax).
    # Bank tops poke into the sky. Bases sit on the stadium deck (~y=152).
    _tower(cv, 70, 10, 154, tilt=-1, cols=4, rows=4)
    _tower(cv, 250, 6, 154, tilt=-1, cols=5, rows=4)
    _tower(cv, 710, 6, 154, tilt=1, cols=5, rows=4)
    _tower(cv, 890, 10, 154, tilt=1, cols=4, rows=4)

    _scoreboard(cv)
    _press_box(cv)
    _bleachers(cv)
    # Goal posts after bleachers so they sit in front of the side stands
    _goal_post(cv, GOAL_L, facing=1)
    _goal_post(cv, GOAL_R, facing=-1)
    _track_and_sideline(cv)
    _field(cv)

    # A couple of leftover shakos / a blanket on empty seats (static mid flavor)
    # left section, row 5
    cv.stamp(140, 152 + 5 * 17 + 4, [
        " w ",
        "NNN",
        "NGN",
        "NNN",
    ], {"w": P["white"], "N": P["navy"], "G": P["gold"]})
    cv.stamp(430, 152 + 3 * 17 + 6, [
        "NNNNNN",
        "NnnnnN",
        "NNNNNN",
    ], {"N": P["navy_dk"], "n": P["navy"]})  # folded jacket
    cv.stamp(650, 152 + 6 * 17 + 5, [
        " GGG ",
        "GgggG",
        " GGG ",
    ], {"G": P["gold"], "g": P["gold_dk"]})  # pom / souvenir
    return cv




# ---------------------------------------------------------------------------
# ANIM overlays — 960x360 transparent. Crowd bob, flags, light flicker.
# ---------------------------------------------------------------------------
def _person_band(cv, x, y, skin, hair, bob=0, plume_col=None, facing=1):
    """Seated JMHS band member in navy + gold, optional shako plume. y is feet/seat."""
    y = y + bob
    sk_d, sk, sk_l = skin
    # shako
    if plume_col:
        cv.p(x + 2, y - 15, plume_col)
        cv.p(x + 2, y - 16, plume_col)
        cv.p(x + 3, y - 15, P["white"] if plume_col != P["white"] else P["gold_lt"])
    cv.rect(x, y - 14, 5, 5, P["navy"])
    cv.hline(x, x + 4, y - 14, P["navy_dk"])
    cv.hline(x, x + 4, y - 11, P["gold"])  # braid
    cv.p(x + 2, y - 13, P["gold_lt"])  # badge
    # face
    cv.rect(x + 1, y - 9, 3, 3, sk)
    cv.p(x + 1, y - 9, hair)
    cv.p(x + 2, y - 9, hair)
    cv.p(x + 3, y - 9, hair)
    cv.p(x + 1, y - 8, sk_d)
    # torso (navy jacket, white baldric)
    cv.rect(x, y - 6, 5, 6, P["navy"])
    cv.vline(x + (2 if facing >= 0 else 1), y - 6, y - 2, P["white"])
    cv.p(x + 2, y - 5, P["gold"])  # button
    # legs on seat
    cv.p(x, y, P["navy_dk"])
    cv.p(x + 1, y, P["navy_dk"])
    cv.p(x + 3, y, P["navy_dk"])
    cv.p(x + 4, y, P["navy_dk"])


def _person_fan(cv, x, y, skin, hair, body, body2, bob=0, arm_up=False):
    """Civilian seated fan. Optional raised arm."""
    y = y + bob
    sk_d, sk, sk_l = skin
    # hair / head
    cv.rect(x + 1, y - 11, 3, 2, hair)
    cv.rect(x + 1, y - 9, 3, 3, sk)
    cv.p(x + 1, y - 9, hair)
    cv.p(x + 1, y - 8, sk_d)
    if arm_up:
        cv.vline(x + 5, y - 16 + bob, y - 6, sk)
        cv.p(x + 5, y - 17 + bob, sk_l)
        cv.p(x + 4, y - 6, body)
    # torso
    cv.rect(x, y - 6, 5, 5, body)
    cv.p(x + 1, y - 5, body2)
    cv.p(x + 3, y - 5, body2)
    cv.p(x, y, P["shoe"])
    cv.p(x + 4, y, P["shoe"])


def _person_guard(cv, x, y, skin, hair, bob=0):
    """Color guard in navy with gold sash, sitting or kneeling-ish on a seat."""
    y = y + bob
    sk_d, sk, sk_l = skin
    cv.rect(x + 1, y - 11, 3, 2, hair)
    cv.rect(x + 1, y - 9, 3, 3, sk)
    cv.p(x + 1, y - 8, sk_d)
    cv.rect(x, y - 6, 5, 5, P["navy"])
    cv.hline(x, x + 4, y - 4, P["gold"])  # sash
    cv.p(x + 4, y - 6, P["white"])
    cv.p(x, y, P["navy_dk"])
    cv.p(x + 4, y, P["navy_dk"])


def _sousaphone(cv, x, y, skin, hair, bob=0):
    """A wide sousaphone player (seated)."""
    y = y + bob
    sk_d, sk, _ = skin
    cv.rect(x + 3, y - 13, 5, 5, P["navy"])
    cv.hline(x + 3, x + 7, y - 10, P["gold"])
    cv.rect(x + 4, y - 8, 3, 3, sk)
    cv.p(x + 4, y - 8, hair)
    cv.rect(x + 3, y - 5, 5, 5, P["navy"])
    # bell wrap, gold
    cv.rect(x - 1, y - 10, 4, 8, P["gold"])
    cv.rect(x, y - 9, 2, 6, P["gold_lt"])
    cv.p(x - 1, y - 10, P["gold_dk"])
    cv.rect(x + 8, y - 6, 3, 3, P["gold_dk"])  # tubing
    cv.p(x + 9, y - 4, P["gold"])


def _trumpet_kid(cv, x, y, skin, hair, bob=0):
    y = y + bob
    sk_d, sk, _ = skin
    cv.rect(x, y - 13, 5, 5, P["navy"])
    cv.hline(x, x + 4, y - 10, P["gold"])
    cv.rect(x + 1, y - 8, 3, 3, sk)
    cv.p(x + 1, y - 8, hair)
    cv.rect(x, y - 5, 5, 5, P["navy"])
    cv.vline(x + 5, y - 7, y - 4, P["gold"])
    cv.p(x + 6, y - 6, P["gold_lt"])  # bell


def draw_flag(cv, pole_x, pole_y, frame, kind="school", hoist=0):
    """Wave a flag off a mid-layer pole. pole_y is the top of the cloth."""
    # horizontal wave offsets per cloth row, 4-frame cycle
    tables = {
        0: [0, 0, 1, 1, 2, 2, 1, 1, 0, 0, 1, 1],
        1: [1, 0, 0, 1, 1, 2, 2, 1, 1, 0, 0, 1],
        2: [2, 1, 1, 0, 0, 1, 1, 2, 2, 1, 1, 0],
        3: [1, 2, 2, 1, 0, 0, 1, 1, 0, 0, 1, 2],
    }
    wave = tables[frame % 4]
    w, h = 20, 12
    if kind == "guard":
        w, h = 16, 10
    for fy in range(h):
        ox = wave[fy % len(wave)]
        for fx in range(w):
            px = pole_x + 2 + fx + ox
            py = pole_y + hoist + fy
            if kind == "school":
                # navy field, gold border, gold chevron, white hoist stripe
                col = P["navy"]
                if fx < 2:
                    col = P["white"]
                elif fy < 1 or fy == h - 1 or fx == w - 1:
                    col = P["gold"]
                elif 6 <= fx <= 8 and 3 <= fy <= 8:
                    col = P["gold"]
                elif 5 <= fx <= 9 and fy in (4, 7):
                    col = P["gold_lt"]
                elif fx + fy == 14 or fx + fy == 15:
                    col = P["gold_dk"]
                cv.p(px, py, col)
            else:
                # color-guard show flag: gold field, navy flash, white tip
                col = P["gold"]
                if fy < 1 or fy == h - 1:
                    col = P["gold_lt"]
                if fx < 2:
                    col = P["navy_lt"]
                elif 4 <= fy <= 7 and 4 <= fx <= 12:
                    col = P["navy"]
                elif fx > w - 3:
                    col = P["white"]
                if fy == 5 and 6 <= fx <= 10:
                    col = P["gold_lt"]
                cv.p(px, py, col)
    # gold finial already implied by the mid pole; add a small cloth wrap at hoist
    cv.p(pole_x + 1, pole_y + hoist, P["gold"])
    cv.p(pole_x + 1, pole_y + hoist + 1, P["navy"])


def _light_glow(cv, cx, cy, w, h, level=2):
    """Hard-edged rectangular glow around a lamp bank. level 1-3."""
    cols = [None, P["glow3"], P["glow2"], P["glow1"]]
    # stepped rings, no blur
    if level >= 1:
        cv.rect(cx - 4, cy - 3, w + 8, h + 6, P["glow3"])
    if level >= 2:
        cv.rect(cx - 2, cy - 1, w + 4, h + 2, P["glow2"])
    if level >= 3:
        # only paint over existing dark sky? We are on a transparent overlay,
        # so this glow will lighten whatever is under it when composited.
        # Keep it tight so it doesn't wash the scoreboard.
        pass


def _lamp_override(cv, cx, top, cols, rows, tilt, pattern):
    """Redraw some lamps dim/bright according to a 0/1/2 pattern list."""
    lamp_w, lamp_h, gap = 6, 5, 2
    pad = 3
    bw = cols * (lamp_w + gap) - gap + pad * 2
    bh = rows * (lamp_h + gap) - gap + pad * 2
    x0 = cx - bw // 2
    y0 = top
    i = 0
    for r in range(rows):
        shift = tilt * r
        for c in range(cols):
            lx = x0 + pad + c * (lamp_w + gap) + shift
            ly = y0 + pad + r * (lamp_h + gap)
            state = pattern[i % len(pattern)]
            i += 1
            if state == 0:
                # dim / flicker off
                cv.rect(lx, ly, lamp_w, lamp_h, P["lamp_off"])
                cv.rect(lx + 1, ly + 1, lamp_w - 2, lamp_h - 2, P["lamp3"])
            elif state == 2:
                # extra hot
                cv.rect(lx, ly, lamp_w, lamp_h, P["lamp"])
                cv.rect(lx + 1, ly + 1, lamp_w - 2, lamp_h - 2, P["flash"])
                cv.p(lx + 2, ly + 1, P["white"])
            # state 1 = leave mid's base lamp alone (no overlay)
    # soft hard-edged bloom around the whole bank, intensity from average
    avg = sum(pattern) / len(pattern)
    if avg >= 1.1:
        # thin glow collar
        cv.frame(x0 - 2, y0 - 2, bw + 4, bh + 4, P["glow2"])
        cv.frame(x0 - 3, y0 - 3, bw + 6, bh + 6, P["glow3"])
    return x0, y0, bw, bh


# People layout: clusters of remaining band kids + a few fans.
# Coordinates are mid-space. Seat rows start at y=152, row_h=17.
# A person 'y' is the seat bench (row y + row_h - 3).
_ROW_TOP = 152
_ROW_H = 17


def _seat_y(row):
    return _ROW_TOP + row * _ROW_H + _ROW_H - 4


def _crowd(cv: CV, frame: int):
    rng = random.Random(99)
    # bob groups: A up on frames 0-1, B up on frames 2-3, 1px only
    def bob(group):
        if group == "A":
            return -1 if frame in (0, 1) else 0
        if group == "B":
            return -1 if frame in (2, 3) else 0
        if group == "C":
            return -1 if frame in (1, 2) else 0
        return 0

    # --- Band cluster, left of 50, rows 2-7 (home section) ---
    band_xs_rows = [
        # row, x, kind, group, skin_i, hair_i  (rows 2-6 only; row 7 sits in the fascia)
        (2, 220, "band", "A", 0, 0),
        (2, 228, "band", "B", 1, 1),
        (2, 236, "trumpet", "A", 2, 0),
        (2, 252, "band", "C", 0, 2),
        (3, 216, "band", "B", 1, 0),
        (3, 224, "sousa", "A", 0, 1),
        (3, 240, "band", "C", 2, 3),
        (3, 248, "trumpet", "B", 1, 0),
        (3, 256, "band", "A", 0, 4),
        (4, 214, "band", "C", 2, 1),
        (4, 222, "band", "A", 1, 0),
        (4, 230, "trumpet", "B", 0, 2),
        (4, 238, "band", "A", 2, 0),
        (4, 246, "band", "C", 0, 1),
        (4, 254, "band", "B", 1, 3),
        (5, 218, "sousa", "B", 1, 0),
        (5, 234, "band", "A", 0, 2),
        (5, 242, "trumpet", "C", 2, 0),
        (5, 250, "band", "B", 0, 1),
        (6, 226, "band", "A", 2, 4),
        (6, 234, "band", "C", 1, 0),
        (6, 242, "band", "B", 0, 3),
        (6, 250, "guard", "C", 2, 2),
        (6, 258, "guard", "B", 1, 0),
        # a few more to the left of the aisle at 200 (leave 120-142 clear for a flag)
        (4, 160, "band", "B", 1, 1),
        (4, 168, "band", "A", 0, 0),
        (5, 156, "trumpet", "C", 2, 0),
        (5, 164, "band", "B", 0, 2),
        (6, 160, "band", "A", 1, 3),
        (6, 172, "band", "C", 0, 0),
        # scattered right of that cluster toward midfield (leave 328-350 clear for a flag)
        (3, 280, "fan", "A", 2, 1),
        (3, 288, "fan", "B", 0, 0),
        (5, 276, "fan", "C", 1, 2),
        (6, 284, "band", "A", 0, 0),
        (6, 296, "fan", "B", 2, 4),
    ]

    # --- Center under press box: a few staff / parents ---
    center = [
        (4, 400, "fan", "B", 0, 0),
        (4, 416, "fan", "A", 1, 1),
        (5, 408, "fan", "C", 2, 0),
        (5, 424, "fan", "B", 0, 3),
        (6, 400, "fan", "A", 1, 2),
        (6, 440, "fan", "C", 2, 0),
        (3, 448, "fan", "A", 1, 4),
        # skip 454-507 in rows 5-6 (GO JMHS banner)
        (5, 430, "fan", "C", 2, 1),
        (4, 500, "fan", "B", 0, 0),
        (6, 528, "fan", "A", 1, 2),
        (5, 536, "fan", "C", 0, 3),
        (4, 544, "fan", "B", 2, 0),
        (6, 548, "fan", "A", 1, 1),
        (5, 560, "band", "C", 0, 0),
    ]

    # --- Right cluster: color guard + a few fans / band ---
    right = [
        (3, 660, "guard", "A", 2, 2),
        (3, 672, "guard", "B", 0, 0),
        (4, 652, "guard", "C", 1, 3),
        (4, 664, "band", "A", 0, 0),
        (4, 680, "fan", "B", 2, 1),
        (5, 656, "fan", "A", 1, 0),
        (5, 668, "guard", "B", 0, 2),
        (5, 684, "fan", "C", 2, 4),
        (6, 648, "band", "C", 0, 1),
        (6, 660, "trumpet", "A", 1, 0),
        (6, 676, "fan", "B", 0, 3),
        (6, 688, "guard", "A", 2, 0),
        (4, 720, "fan", "A", 1, 0),
        (5, 728, "fan", "C", 2, 1),
        (6, 716, "fan", "B", 0, 4),
        # far right parallax cluster (leave 752-774 and 880-902 clear for flags)
        (5, 820, "fan", "C", 0, 0),
        (6, 828, "band", "A", 1, 1),
        (6, 836, "fan", "B", 2, 3),
        (5, 844, "fan", "A", 0, 0),
        # far left parallax (leave 16-40 clear for a flag; 120-142 also clear)
        (5, 52, "fan", "B", 1, 2),
        (6, 64, "fan", "A", 0, 0),
        (4, 56, "fan", "C", 2, 1),
        (4, 100, "band", "A", 0, 0),
        (6, 108, "fan", "B", 1, 3),
        (5, 96, "fan", "C", 0, 2),
    ]

    fan_bodies = [
        (P["navy"], P["navy_lt"]),
        (P["navy_dk"], P["navy"]),
        (P["white_dk"], P["white_sh"]),
        (P["conc"], P["conc_lt"]),
        (P["gold_dk"], P["gold"]),
        (P["bldg"], P["bldg3"]),
        (P["track2"], P["track3"]),
    ]

    arm_cycle = set()  # a few fans raise arms on alternating frames
    if frame in (0, 2):
        arm_cycle = {(7, 278), (7, 508), (6, 676), (7, 724), (5, 424)}
    else:
        arm_cycle = {(7, 270), (6, 440), (7, 678), (6, 716), (4, 416)}

    for row, x, kind, group, si, hi in band_xs_rows + center + right:
        y = _seat_y(row)
        b = bob(group)
        skin = SKINS[si % len(SKINS)]
        hair = HAIRS[hi % len(HAIRS)]
        if kind == "band":
            plume = P["gold_lt"] if (row + x) % 3 != 0 else P["white"]
            _person_band(cv, x, y, skin, hair, bob=b, plume_col=plume)
        elif kind == "sousa":
            _sousaphone(cv, x, y, skin, hair, bob=b)
        elif kind == "trumpet":
            _trumpet_kid(cv, x, y, skin, hair, bob=b)
        elif kind == "guard":
            _person_guard(cv, x, y, skin, hair, bob=b)
        else:
            body, body2 = fan_bodies[(row + x) % len(fan_bodies)]
            _person_fan(cv, x, y, skin, hair, body, body2, bob=b,
                        arm_up=(row, x) in arm_cycle)

    # A couple of standing figures on the track (y~299), still above the floor band
    # drum major-ish on the podium at x=300
    y = 298
    b = bob("A")
    skin = SKINS[0]
    # standing, feet at 298
    yy = y + b
    cv.rect(308, yy - 22, 5, 5, P["navy"])  # shako
    cv.hline(308, 312, yy - 19, P["gold"])
    cv.p(310, yy - 24, P["gold_lt"])  # plume
    cv.p(310, yy - 25, P["gold_lt"])
    cv.rect(309, yy - 17, 3, 3, skin[1])
    cv.p(309, yy - 17, P["hair"])
    cv.rect(308, yy - 14, 5, 8, P["navy"])
    cv.vline(310, yy - 14, yy - 8, P["white"])
    cv.rect(308, yy - 6, 2, 6, P["navy_dk"])
    cv.rect(311, yy - 6, 2, 6, P["navy_dk"])
    cv.p(308, yy, P["shoe"])
    cv.p(312, yy, P["shoe"])
    # mace raised (bobs)
    cv.vline(314, yy - 30, yy - 12, P["gold"])
    cv.p(314, yy - 31, P["gold_lt"])
    cv.rect(313, yy - 28, 3, 3, P["gold_lt"])

    # two color guard standing on the track near flags, left and right of 50
    for gx, group, si in ((372, "B", 2), (512, "C", 1)):
        yy = 298 + bob(group)
        skin = SKINS[si]
        cv.rect(gx + 1, yy - 18, 3, 2, HAIRS[si])
        cv.rect(gx + 1, yy - 16, 3, 3, skin[1])
        cv.rect(gx, yy - 13, 5, 7, P["navy"])
        cv.hline(gx, gx + 4, yy - 11, P["gold"])
        cv.rect(gx, yy - 6, 2, 6, P["navy_dk"])
        cv.rect(gx + 3, yy - 6, 2, 6, P["navy_dk"])
        cv.p(gx, yy, P["shoe"])
        cv.p(gx + 4, yy, P["shoe"])


def draw_anim(frame: int) -> CV:
    cv = CV(MID_W, MID_H, bg=None)

    # Light flicker patterns (0 dim, 1 unchanged/mid, 2 hot). Each tower differs.
    # Towers at x=70,250,710,890
    patterns = {
        0: {
            70:  [1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1],
            250: [2, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 1],
            710: [1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1],
            890: [2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1],
        },
        1: {
            70:  [1, 0, 1, 2, 1, 1, 0, 1, 2, 1, 1, 2, 1, 0, 1, 2],
            250: [1, 2, 1, 1, 2, 0, 1, 2, 1, 2, 1, 1, 0, 2, 1, 1, 2, 1, 1, 2],
            710: [2, 1, 0, 1, 2, 1, 1, 2, 0, 1, 2, 1, 1, 0, 2, 1, 1, 2, 1, 0],
            890: [1, 2, 1, 0, 1, 1, 2, 1, 0, 2, 1, 1, 2, 1, 0, 1],
        },
        2: {
            70:  [2, 1, 2, 1, 0, 2, 1, 2, 1, 0, 2, 1, 2, 1, 1, 0],
            250: [2, 1, 2, 2, 1, 1, 2, 1, 2, 1, 0, 2, 1, 2, 1, 2, 1, 0, 2, 1],
            710: [1, 2, 1, 2, 1, 2, 0, 1, 2, 1, 2, 1, 2, 1, 0, 2, 1, 2, 1, 2],
            890: [0, 2, 1, 2, 1, 1, 2, 0, 1, 2, 1, 2, 1, 2, 1, 1],
        },
        3: {
            70:  [1, 2, 0, 1, 2, 1, 2, 0, 1, 2, 1, 1, 0, 2, 1, 2],
            250: [1, 0, 2, 1, 2, 1, 0, 2, 1, 1, 2, 0, 2, 1, 2, 1, 0, 2, 1, 1],
            710: [2, 1, 2, 0, 1, 2, 1, 0, 2, 1, 1, 2, 0, 1, 2, 1, 2, 0, 1, 2],
            890: [2, 1, 2, 1, 0, 2, 1, 2, 1, 0, 2, 1, 1, 0, 2, 1],
        },
    }
    towers = [(70, 10, 4, 4, -1), (250, 6, 5, 4, -1), (710, 6, 5, 4, 1), (890, 10, 4, 4, 1)]
    for cx, top, cols, rows, tilt in towers:
        _lamp_override(cv, cx, top, cols, rows, tilt, patterns[frame][cx])

    # Scoreboard lamp sparkle + colon blink on 0:00 (blink off on odd frames)
    bx, by, bw, bh = 392, 26, 176, 70
    for i, lx in enumerate(range(bx + 8, bx + bw - 6, 8)):
        on = (i + frame) % 3 != 0
        cv.rect(lx, by + 2, 3, 2, P["lamp"] if on else P["lamp_off"])
    if frame % 2 == 1:
        # paint over the colon in "0:00" with black to blink it
        # "4TH 0:00" starts at bx+8, by+bh-14
        # chars: 4 T H   0 : 0 0   — colon is the 6th glyph (index 5)
        # each glyph 5+1=6 px, so colon at bx+8 + 5*6 = bx+38
        colon_x = bx + 8 + 5 * 6
        colon_y = by + bh - 14
        cv.rect(colon_x, colon_y, 5, 7, P["navy_dk"])

    # Press-box beacon blink (off on frame 1 and 2)
    ax = 368 + 224 - 16
    py = 100
    if frame in (1, 2):
        cv.p(ax, py - 29, P["beacon_dk"])
        cv.p(ax + 1, py - 29, P["beacon_dk"])
        cv.p(ax, py - 30, P["steel_hi"])
    else:
        cv.p(ax, py - 29, P["flash"])
        cv.p(ax + 1, py - 29, P["beacon"])
        cv.p(ax, py - 30, P["flash"])
        cv.p(ax - 1, py - 29, P["beacon"])
        cv.p(ax + 2, py - 29, P["beacon"])

    # Flags on mid poles at (240, 360, 600, 720, 120, 840), cloth starts near pole top (y=248)
    flag_specs = [
        (16, 248, "school"),
        (120, 248, "guard"),
        (328, 248, "school"),
        (600, 248, "school"),
        (752, 248, "guard"),
        (880, 248, "school"),
    ]
    for i, (fx, fy, kind) in enumerate(flag_specs):
        draw_flag(cv, fx, fy, (frame + i) % 4, kind=kind, hoist=0)
    # handheld color-guard flags: shorter, lower, in front of the fascia (not the stands)
    def held_flag(pole_x, fy, fr):
        tables = {
            0: [0, 0, 1, 1, 2, 2, 1, 1],
            1: [1, 0, 0, 1, 1, 2, 2, 1],
            2: [2, 1, 1, 0, 0, 1, 1, 2],
            3: [1, 2, 2, 1, 0, 0, 1, 1],
        }
        wave = tables[fr % 4]
        w, h = 12, 8
        for row in range(h):
            ox = wave[row % len(wave)]
            for col in range(w):
                px, py = pole_x + 2 + col + ox, fy + row
                if col < 2:
                    c = P["navy_lt"]
                elif col > w - 3:
                    c = P["white"]
                elif 2 <= row <= 5 and 3 <= col <= 8:
                    c = P["navy"]
                else:
                    c = P["gold"]
                cv.p(px, py, c)
        cv.vline(pole_x, fy, 297, P["white_dk"])
        cv.p(pole_x, fy, P["gold"])

    held_flag(380, 278, (frame + 2) % 4)
    held_flag(520, 278, (frame + 3) % 4)

    _crowd(cv, frame)

    # A few "phone" / glow-stick twinkles in the stands
    twinkles = [
        (410, _seat_y(4) - 12, 0),
        (500, _seat_y(6) - 14, 1),
        (670, _seat_y(5) - 13, 2),
        (170, _seat_y(6) - 12, 3),
        (820, _seat_y(7) - 11, 0),
        (540, _seat_y(5) - 12, 2),
    ]
    for x, y, ph in twinkles:
        if frame % 4 == ph or (frame + 1) % 4 == ph:
            cv.p(x, y, P["flash"])
            cv.p(x + 1, y, P["lamp2"])

    return cv


# ---------------------------------------------------------------------------
# Composite + IO
# ---------------------------------------------------------------------------
def composite_preview(far: CV, mid: CV, anim: CV) -> Image.Image:
    """640x360 composite of far + centered mid + centered anim_0."""
    out = Image.new("RGBA", (VIEW_W, VIEW_H), (0, 0, 0, 255))
    out.paste(far.im.convert("RGBA"), (0, 0))
    mid_crop = mid.im.crop((MID_OFFSET, 0, MID_OFFSET + VIEW_W, VIEW_H))
    out.alpha_composite(mid_crop)
    anim_crop = anim.im.crop((MID_OFFSET, 0, MID_OFFSET + VIEW_W, VIEW_H))
    out.alpha_composite(anim_crop)
    # preview is used as a still; keep RGBA but flatten to opaque RGB for size/clarity
    bg = Image.new("RGB", (VIEW_W, VIEW_H), (0, 0, 0))
    bg.paste(out, mask=out.split()[3])
    return bg


def unique_rgb(im: Image.Image, ignore_clear=True) -> int:
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    s = set()
    for r, g, b, a in im.getdata():
        if ignore_clear and a == 0:
            continue
        s.add((r, g, b, a))
    return len(s)


def assert_qa(far, mid, anims, preview, preview2x):
    problems = []
    if far.im.size != (VIEW_W, VIEW_H):
        problems.append(f"far size {far.im.size}")
    # far must be fully opaque
    far_rgba = far.im.convert("RGBA")
    alphas = {a for (*_, a) in far_rgba.getdata()}
    if alphas != {255}:
        problems.append(f"far alpha values {alphas}")
    if mid.im.size != (MID_W, MID_H):
        problems.append(f"mid size {mid.im.size}")
    # floor band must be opaque in mid
    mp = mid.im.load()
    for y in range(FLOOR_TOP, MID_H):
        for x in range(MID_W):
            if mp[x, y][3] != 255:
                problems.append(f"mid transparent in floor at {x},{y}")
                break
        else:
            continue
        break
    for i, a in enumerate(anims):
        if a.im.size != (MID_W, MID_H):
            problems.append(f"anim_{i} size {a.im.size}")
        # no partial alpha
        al = {px[3] for px in a.im.getdata()}
        if not al <= {0, 255}:
            problems.append(f"anim_{i} partial alpha {al}")
    if preview.size != (VIEW_W, VIEW_H):
        problems.append(f"preview size {preview.size}")
    if preview2x.size != (VIEW_W * 2, VIEW_H * 2):
        problems.append(f"preview@2x size {preview2x.size}")
    if problems:
        raise SystemError("QA failed:\n  " + "\n  ".join(problems))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    far = draw_far()
    mid = draw_mid()
    anims = [draw_anim(i) for i in range(4)]

    far_path = OUT / "far.png"
    mid_path = OUT / "mid.png"
    # far is RGB opaque
    if far.im.mode != "RGB":
        Image.new("RGB", far.im.size, (0, 0, 0)).paste(
            far.im.convert("RGBA"), mask=far.im.convert("RGBA").split()[3]
        )
        rgb = Image.new("RGB", far.im.size)
        rgb.paste(far.im.convert("RGBA"), mask=far.im.convert("RGBA").split()[3])
        rgb.save(far_path)
        far.im = rgb
    else:
        far.im.save(far_path)
    mid.im.save(mid_path)
    for i, a in enumerate(anims):
        a.im.save(OUT / f"anim_{i}.png")

    preview = composite_preview(far, mid, anims[0])
    preview.save(OUT / "preview.png")
    preview2x = preview.resize((VIEW_W * 2, VIEW_H * 2), Image.Resampling.NEAREST)
    preview2x.save(OUT / "preview@2x.png")
    # also a 4x viewing copy for local QA (not a required deliverable)
    preview4x = preview.resize((VIEW_W * 4, VIEW_H * 4), Image.Resampling.NEAREST)
    preview4x.save(OUT / "_qa_preview@4x.png")

    assert_qa(far, mid, anims, preview, preview2x)

    files = [
        ("far.png", far.im),
        ("mid.png", mid.im),
        ("anim_0.png", anims[0].im),
        ("anim_1.png", anims[1].im),
        ("anim_2.png", anims[2].im),
        ("anim_3.png", anims[3].im),
        ("preview.png", preview),
        ("preview@2x.png", preview2x),
    ]
    print("Wrote:")
    for name, im in files:
        w, h = im.size
        cols = unique_rgb(im if im.mode == "RGBA" else im.convert("RGBA"))
        mode = im.mode
        print(f"  {name:16s} {w}x{h}  {mode:4s}  {cols:3d} colors")
    print(f"Floor line y={FLOOR_Y}; floor band y={FLOOR_TOP}..{MID_H - 1}")
    print(f"Mid offset in view: x={-MID_OFFSET}")


if __name__ == "__main__":
    main()
