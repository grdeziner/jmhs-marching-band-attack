#!/usr/bin/env python3
"""Band Wars — Friday Night Field, SNES / Street Fighter II Turbo-era 16-bit stage.

Native view 640x360. Mid/anim 960x360 (origin x=-160). Near 1120x360 (origin x=-240).
Crisp 1px pixels, no antialiasing, no partial alpha. Ordered dithering for
gradients, blooms, and light beams. School colors: navy + gold + white trim.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent
VIEW_W, VIEW_H = 640, 360
MID_W, MID_H = 960, 360
NEAR_W, NEAR_H = 1120, 360
MID_OFFSET = (MID_W - VIEW_W) // 2    # 160
NEAR_OFFSET = (NEAR_W - VIEW_W) // 2  # 240
FLOOR_Y = 320
FLOOR_TOP = 300
YARD = 8
GOAL_L, GOAL_R = 80, 880
FIFTY = 480
ANIM_FRAMES = 8

# Bleachers
ROW_TOP = 150
NROWS = 8
ROW_H = 17  # 150..286
BLEACH_BOT = ROW_TOP + NROWS * ROW_H  # 286
AISLES = (80, 200, 320, 480, 640, 760, 880)

# Lamp towers in mid space: (cx, bank_top, cols, rows, tilt)
TOWERS = (
    (70, 8, 4, 4, -1),
    (250, 4, 5, 4, -1),
    (710, 4, 5, 4, 1),
    (890, 8, 4, 4, 1),
)


def C(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------------------
# Palette — 16-bit, well beyond 32 colors. Official JMHS swatches kept exact.
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
    # Extra skin ramps
    "skin_b_dk": C("#3A2218"),
    "skin_b": C("#6B3E28"),
    "skin_b_lt": C("#A06640"),
    "skin_c_dk": C("#A07050"),
    "skin_c": C("#E8B898"),
    "skin_c_lt": C("#F8DCC8"),
    "skin_d_dk": C("#2A1810"),
    "skin_d": C("#5A3828"),
    "skin_d_lt": C("#8A5A40"),
    "skin_e_dk": C("#6A4030"),
    "skin_e": C("#C49068"),
    "skin_e_lt": C("#E8C4A0"),
    # Hair variants
    "hair_br": C("#3A2218"),
    "hair_bl": C("#C4A056"),
    "hair_rd": C("#6A2818"),
    "hair_au": C("#E8D090"),
    "hair_gy": C("#6A6868"),
    # Sky (deep night → dusty horizon light-pollution)
    "sky0": C("#06070F"),
    "sky1": C("#080A16"),
    "sky2": C("#0B0E1E"),
    "sky3": C("#0E1328"),
    "sky4": C("#121830"),
    "sky5": C("#161E3C"),
    "sky6": C("#1B2548"),
    "sky7": C("#212C54"),
    "sky8": C("#283460"),
    "sky9": C("#303C6A"),
    "sky10": C("#384474"),
    "sky11": C("#424E7C"),
    "sky_warm": C("#3A3E68"),  # slight stadium wash
    # Moon
    "moon": C("#F2F2E6"),
    "moon2": C("#DCDCC8"),
    "moon3": C("#C0C0AA"),
    "moon4": C("#9A9A86"),
    "moon5": C("#6E6E60"),
    "moon_glow0": C("#2A3058"),
    "moon_glow1": C("#3A4268"),
    "moon_glow2": C("#5A6280"),
    "star": C("#F4F6FF"),
    "star2": C("#C4CEE4"),
    "star3": C("#FFE9A8"),
    "star4": C("#8A9AB8"),
    # Far landscape
    "hill0": C("#080E0C"),
    "hill1": C("#0C1612"),
    "hill2": C("#121C18"),
    "hill3": C("#182820"),
    "tree0": C("#060E0A"),
    "tree1": C("#0A1610"),
    "tree2": C("#102018"),
    "tree3": C("#16281C"),
    "bldg0": C("#10141C"),
    "bldg1": C("#181C26"),
    "bldg2": C("#222632"),
    "bldg3": C("#2E3340"),
    "bldg4": C("#3A4050"),
    "win_on": C("#F0C056"),
    "win_on2": C("#FFE08A"),
    "win_dim": C("#8A6420"),
    "win_off": C("#1A1E28"),
    "park": C("#E09020"),
    "park2": C("#F8C050"),
    "tower0": C("#1A1E26"),
    "tower1": C("#2A3038"),
    "tower2": C("#3A424C"),
    "tower3": C("#525A64"),
    # Stadium steel / concrete (more 16-bit steps)
    "steel0": C("#14161C"),
    "steel1": C("#1E2228"),
    "steel2": C("#2C3038"),
    "steel3": C("#3C424C"),
    "steel4": C("#545A64"),
    "steel5": C("#707880"),
    "steel6": C("#8A929A"),
    "conc0": C("#1C1E22"),
    "conc1": C("#282A30"),
    "conc2": C("#34363C"),
    "conc3": C("#42454C"),
    "conc4": C("#545860"),
    "conc5": C("#686C74"),
    "conc6": C("#7C8088"),
    "seat0": C("#14161C"),
    "seat1": C("#1C2028"),
    "seat2": C("#262A32"),
    "seat3": C("#323640"),
    "seat4": C("#40444E"),
    "riser0": C("#181A20"),
    "riser1": C("#22242C"),
    "rail0": C("#3A3E46"),
    "rail1": C("#6A727C"),
    "rail2": C("#A0A8B0"),
    "rail3": C("#C8D0D6"),
    # Lights / glow
    "lamp0": C("#FFFCE8"),
    "lamp1": C("#FFF4C0"),
    "lamp2": C("#FFE070"),
    "lamp3": C("#F0B838"),
    "lamp4": C("#C88820"),
    "lamp_off": C("#5A4A30"),
    "lamp_off2": C("#3A3220"),
    "glow0": C("#FFF8D8"),
    "glow1": C("#FFE898"),
    "glow2": C("#F0C858"),
    "glow3": C("#C89830"),
    "glow4": C("#8A6820"),
    "glow5": C("#5A4818"),
    "beam0": C("#FFF6C8"),
    "beam1": C("#F8E090"),
    "beam2": C("#D4B050"),
    "beam3": C("#8A7430"),
    "beacon": C("#E03030"),
    "beacon2": C("#FF6060"),
    "beacon_dk": C("#6A1010"),
    # Turf (warm stadium-lit greens)
    "turf0": C("#0E3A1A"),
    "turf1": C("#144822"),
    "turf2": C("#1A582A"),
    "turf3": C("#206832"),
    "turf4": C("#287A3C"),
    "turf5": C("#328C46"),
    "turf6": C("#3C9E52"),
    "turf7": C("#4AB05E"),
    "turf_warm": C("#3A8C44"),
    "turf_hot": C("#52A85A"),
    "turf_end0": C("#0E3020"),
    "turf_end1": C("#143828"),
    "turf_end2": C("#1A4430"),
    "line": C("#F4F0E4"),
    "line2": C("#D8D4C8"),
    "line3": C("#B8B4A8"),
    "track0": C("#4A281C"),
    "track1": C("#5C3424"),
    "track2": C("#6E4030"),
    "track3": C("#80503C"),
    "track4": C("#3A2018"),
    "track_line": C("#D4C8B0"),
    # Goal posts
    "post0": C("#8A7010"),
    "post1": C("#C4A020"),
    "post2": C("#E8C430"),
    "post3": C("#F8E878"),
    "post4": C("#FFF8C0"),
    # Crowd wardrobe (civilian)
    "c_red": C("#A02830"),
    "c_red2": C("#C84848"),
    "c_mar": C("#6A2030"),
    "c_denim": C("#2A4A78"),
    "c_denim2": C("#3A62A0"),
    "c_teal": C("#1A6868"),
    "c_teal2": C("#2A8888"),
    "c_cream": C("#E8D8B8"),
    "c_grey": C("#5A5E66"),
    "c_grey2": C("#7A7E86"),
    "c_olive": C("#3A5828"),
    "c_mustard": C("#C8A038"),
    "c_orange": C("#C86020"),
    "c_pink": C("#C87880"),
    "c_burg": C("#682030"),
    "c_black": C("#18181C"),
    "c_forest": C("#1A4030"),
    "c_sky": C("#6890C8"),
    "c_yellow": C("#E8D060"),
    # Misc props
    "cam0": C("#1A1C20"),
    "cam1": C("#2C3038"),
    "cam2": C("#4A5060"),
    "cam3": C("#8A90A0"),
    "cool0": C("#C86018"),
    "cool1": C("#E87820"),
    "cool2": C("#F09840"),
    "cool3": C("#F8F0E0"),
    "cool4": C("#8A3A10"),
}

SKINS = [
    (P["skin_dk"], P["skin"], P["skin_lt"]),
    (P["skin_b_dk"], P["skin_b"], P["skin_b_lt"]),
    (P["skin_c_dk"], P["skin_c"], P["skin_c_lt"]),
    (P["skin_d_dk"], P["skin_d"], P["skin_d_lt"]),
    (P["skin_e_dk"], P["skin_e"], P["skin_e_lt"]),
]
HAIRS = [P["hair"], P["hair_br"], P["hair_bl"], P["hair_rd"], P["hair_au"], P["hair_gy"], P["navy_dk"]]
CIV_BODIES = [
    (P["c_red"], P["c_red2"]),
    (P["c_mar"], P["c_red"]),
    (P["c_denim"], P["c_denim2"]),
    (P["c_teal"], P["c_teal2"]),
    (P["c_cream"], P["white_sh"]),
    (P["c_grey"], P["c_grey2"]),
    (P["c_olive"], P["c_forest"]),
    (P["c_mustard"], P["c_yellow"]),
    (P["c_orange"], P["cool2"]),
    (P["c_pink"], P["c_cream"]),
    (P["c_burg"], P["c_mar"]),
    (P["c_black"], P["c_grey"]),
    (P["c_forest"], P["c_olive"]),
    (P["c_sky"], P["c_denim2"]),
    (P["navy"], P["navy_lt"]),
    (P["navy_dk"], P["navy"]),
    (P["gold_dk"], P["gold"]),
    (P["white_dk"], P["white"]),
    (P["c_yellow"], P["gold_lt"]),
    (P["steel2"], P["steel4"]),
]

# Sky stops for vertical dithered gradient (y 0..168)
SKY_STOPS = [
    (0, P["sky0"]),
    (22, P["sky1"]),
    (44, P["sky2"]),
    (66, P["sky3"]),
    (86, P["sky4"]),
    (104, P["sky5"]),
    (120, P["sky6"]),
    (134, P["sky7"]),
    (146, P["sky8"]),
    (156, P["sky9"]),
    (166, P["sky10"]),
    (180, P["sky11"]),
]

# 8x8 Bayer (values 0..63)
BAYER8 = [
    [0, 32, 8, 40, 2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21],
]
BAYER4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
]


def bayer_t(x, y, n=8) -> float:
    if n == 4:
        return (BAYER4[y & 3][x & 3] + 0.5) / 16.0
    return (BAYER8[y & 7][x & 7] + 0.5) / 64.0


def dither_pick(x, y, t, c0, c1, n=8):
    """t in [0,1] → c0 or c1 by ordered dither. No blending, no partial alpha."""
    if t <= 0:
        return c0
    if t >= 1:
        return c1
    return c1 if t > bayer_t(x, y, n) else c0


def lerp_stops(t, stops):
    """Return (c0, c1, local_t) for a 0..1 t through (pos, color) stops."""
    if t <= stops[0][0]:
        return stops[0][1], stops[0][1], 0.0
    if t >= stops[-1][0]:
        return stops[-1][1], stops[-1][1], 1.0
    for i in range(1, len(stops)):
        p0, c0 = stops[i - 1]
        p1, c1 = stops[i]
        if t <= p1:
            return c0, c1, (t - p0) / (p1 - p0) if p1 != p0 else 0.0
    return stops[-1][1], stops[-1][1], 1.0


def dither_stops_y(x, y, y_min, y_max, stops, n=8):
    t = 0 if y_max == y_min else (y - y_min) / (y_max - y_min)
    c0, c1, lt = lerp_stops(t, stops)
    return dither_pick(x, y, lt, c0, c1, n)


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

    def clear_px(self, x, y):
        if self.rgba and 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = (0, 0, 0, 0)

    def is_clear(self, x, y):
        if not self.rgba or not (0 <= x < self.w and 0 <= y < self.h):
            return False
        return self.px[x, y][3] == 0

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
                if (x - cx) * (x - cx) + dy * dy <= r2:
                    self.p(x, y, c)

    def fill_ellipse(self, cx, cy, rx, ry, c):
        if rx <= 0 or ry <= 0:
            return
        rx2, ry2 = rx * rx, ry * ry
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if (x - cx) * (x - cx) * ry2 + (y - cy) * (y - cy) * rx2 <= rx2 * ry2:
                    self.p(x, y, c)

    def stamp(self, ox, oy, rows, mapping):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in mapping and mapping[ch] is not None:
                    self.p(ox + i, oy + j, mapping[ch])

    def save(self, path):
        self.im.save(path)


# 5x7 pixel font
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


def in_aisle(x, half=7):
    return any(abs(x - a) <= half for a in AISLES)


def seat_y(row):
    return ROW_TOP + row * ROW_H + ROW_H - 3




# ---------------------------------------------------------------------------
# FAR — 640x360 opaque. Dithered night sky, moon glow, distant landscape.
# ---------------------------------------------------------------------------
def draw_far() -> CV:
    cv = CV(VIEW_W, VIEW_H, bg=P["sky0"])
    mx, my, mr = 552, 42, 20

    # Vertical dithered sky
    sky_y_stops = [(y, c) for y, c in SKY_STOPS]
    for y in range(0, 186):
        for x in range(VIEW_W):
            col = dither_stops_y(x, y, 0, 180, sky_y_stops, n=8)
            # Warm stadium light-pollution near the horizon center
            if y >= 110:
                poll = (y - 110) / 70.0
                # stronger in the middle (under the stadium)
                cx = abs(x - 320) / 320.0
                poll *= (1.0 - 0.45 * cx)
                col = dither_pick(x, y + 3, poll * 0.55, col, P["sky_warm"], n=8)
            cv.p(x, y, col)

    # Moon glow — concentric dithered rings (no blur, no partial alpha)
    glow_rings = [
        (56, P["moon_glow0"], 0.35),
        (42, P["moon_glow1"], 0.50),
        (30, P["moon_glow2"], 0.70),
        (24, P["moon3"], 0.45),
    ]
    rmax = 56
    for y in range(my - rmax, my + rmax + 1):
        for x in range(mx - rmax, mx + rmax + 1):
            d = math.sqrt((x - mx) ** 2 + (y - my) ** 2)
            if d >= rmax or y < 0 or y >= 186:
                continue
            # intensity 1 at rim of moon, 0 at rmax
            t = max(0.0, 1.0 - (d - mr) / (rmax - mr)) if d > mr else 1.0
            if d <= mr:
                continue  # moon disk itself later
            # pick glow color by distance, dither against existing sky
            if d < 24:
                glow = P["moon3"]
                dens = 0.55 * t
            elif d < 30:
                glow = P["moon_glow2"]
                dens = 0.7 * t
            elif d < 42:
                glow = P["moon_glow1"]
                dens = 0.55 * t
            else:
                glow = P["moon_glow0"]
                dens = 0.4 * t
            if dens > bayer_t(x, y, 8):
                cv.p(x, y, glow)

    # Moon disk with soft (dithered) terminator and craters
    for y in range(my - mr - 1, my + mr + 2):
        for x in range(mx - mr - 1, mx + mr + 2):
            d2 = (x - mx) ** 2 + (y - my) ** 2
            if d2 <= (mr + 1) ** 2 and d2 > mr * mr:
                # 1px dithered rim
                if bayer_t(x, y, 4) < 0.5:
                    cv.p(x, y, P["moon4"])
            if d2 <= mr * mr:
                # lighting: highlight upper-left, shade lower-right
                nx = (x - mx) / mr
                ny = (y - my) / mr
                lit = 0.55 - 0.55 * (nx * 0.55 + ny * 0.65)
                lit = max(0.0, min(1.0, lit))
                c0, c1, lt = lerp_stops(lit, [
                    (0.0, P["moon5"]),
                    (0.25, P["moon4"]),
                    (0.5, P["moon3"]),
                    (0.75, P["moon2"]),
                    (1.0, P["moon"]),
                ])
                cv.p(x, y, dither_pick(x, y, lt, c0, c1, 4))

    # Craters
    for cx, cy, r, col in (
        (mx - 5, my - 3, 4, P["moon3"]),
        (mx + 6, my + 4, 3, P["moon4"]),
        (mx + 2, my - 8, 2, P["moon4"]),
        (mx - 8, my + 6, 2, P["moon3"]),
        (mx + 8, my - 2, 2, P["moon4"]),
    ):
        cv.fill_circle(cx, cy, r, col)
        cv.p(cx - 1, cy - 1, P["moon2"])  # tiny inner highlight

    # Flat dithered clouds
    def cloud(x0, y0, w, h, col_a, col_b):
        for y in range(y0, y0 + h):
            # rounded ends via inset
            inset = 2 if y in (y0, y0 + h - 1) else 0
            if y == y0 + 1 or y == y0 + h - 2:
                inset = 1
            for x in range(x0 + inset, x0 + w - inset):
                # dither body, sparser at edges
                edge = min(x - x0, x0 + w - 1 - x, y - y0, y0 + h - 1 - y)
                dens = 0.85 if edge >= 2 else 0.5
                if dens > bayer_t(x, y, 8):
                    cv.p(x, y, dither_pick(x, y, 0.45, col_a, col_b, 4))

    cloud(28, 56, 86, 9, P["sky5"], P["sky6"])
    cloud(70, 64, 54, 7, P["sky6"], P["sky7"])
    cloud(390, 26, 96, 8, P["sky3"], P["sky4"])
    cloud(430, 34, 50, 6, P["sky4"], P["sky5"])
    cloud(210, 46, 70, 7, P["sky4"], P["sky5"])
    cloud(580, 72, 40, 6, P["sky7"], P["sky8"])

    # Stars
    rng = random.Random(640360)
    for _ in range(140):
        x = rng.randint(0, VIEW_W - 1)
        y = rng.randint(2, 140)
        if y > 90 and rng.random() < 0.5:
            continue
        # skip moon disk
        if (x - mx) ** 2 + (y - my) ** 2 < (mr + 8) ** 2:
            continue
        col = rng.choice([P["star"], P["star"], P["star2"], P["star2"], P["star3"], P["star4"]])
        cv.p(x, y, col)
        if rng.random() < 0.14 and y < 80:
            cv.p(x + 1, y, col)
            cv.p(x, y + 1, col)
            cv.p(x - 1, y, P["star2"])
            cv.p(x, y - 1, P["star2"])

    # Distant rolling hills — layered silhouettes with dithered contact
    for x in range(VIEW_W):
        h = 16 + int(7 * (0.5 + 0.5 * math.sin(x * 0.018 + 1.1)))
        h += int(4 * (0.5 + 0.5 * math.sin(x * 0.06)))
        ytop = 148 - h
        for y in range(ytop, 186):
            t = (y - ytop) / 20.0
            cv.p(x, y, dither_pick(x, y, min(1.0, t), P["hill1"], P["hill0"], 4))

    # Front tree line
    rng2 = random.Random(77)
    for x in range(VIEW_W):
        h = 12 + int(9 * (0.5 + 0.5 * math.sin(x * 0.045 + 0.4)))
        h += int(5 * (0.5 + 0.5 * math.sin(x * 0.13 + 2)))
        if rng2.random() < 0.07:
            h += rng2.randint(5, 12)
        ytop = 156 - h
        for y in range(ytop, 186):
            cv.p(x, y, P["hill2"] if y < ytop + 3 else P["hill1"])

    # Tree blobs with a couple of highlight pixels (moonlit canopy)
    trees = [
        (20, 18, 10), (36, 14, 8), (52, 20, 12), (70, 13, 7),
        (110, 17, 9), (128, 22, 12), (150, 15, 8), (200, 19, 10),
        (230, 14, 7), (248, 16, 9), (300, 13, 8), (330, 18, 10),
        (360, 15, 8), (390, 21, 11), (420, 14, 7), (450, 17, 9),
        (480, 13, 8), (510, 16, 9), (580, 19, 10), (605, 15, 8),
        (622, 17, 9), (90, 12, 6), (175, 16, 8), (270, 14, 7),
        (540, 18, 9), (560, 14, 7), (14, 16, 8), (400, 12, 6),
    ]
    for x, th, tw in trees:
        ty = 157 - th
        cv.fill_ellipse(x, ty + 3, tw // 2, tw // 2 + 1, P["tree0"])
        cv.fill_ellipse(x - 1, ty + 2, max(2, tw // 3), max(2, tw // 3), P["tree1"])
        # a few moonlit leaves on the right side of canopies
        cv.p(x + tw // 3, ty + 1, P["tree3"])
        cv.p(x + tw // 3 + 1, ty + 2, P["tree2"])
        cv.rect(x - 1, ty + 4, 3, max(1, 164 - (ty + 4)), P["tree1"])

    # Ground fill (opaque far)
    cv.rect(0, 166, VIEW_W, VIEW_H - 166, P["hill0"])
    for y in range(166, 186):
        for x in range(VIEW_W):
            cv.p(x, y, dither_pick(x, y, (186 - y) / 20.0, P["hill0"], P["hill1"], 4))

    # Water tower (left) — more truss / tank detail
    tx, ty = 86, 100
    for xoff in (-8, 0, 8):
        cv.vline(tx + xoff, ty + 16, 166, P["tower0"])
        cv.vline(tx + xoff + 1, ty + 16, 166, P["tower1"])
    for y in range(ty + 20, 164, 7):
        cv.hline(tx - 8, tx + 9, y, P["tower0"])
        cv.p(tx - 4, y + 3, P["tower1"])
        cv.p(tx + 5, y + 3, P["tower1"])
    # tank
    cv.fill_ellipse(tx, ty + 8, 13, 10, P["tower1"])
    cv.fill_ellipse(tx - 1, ty + 5, 13, 9, P["tower2"])
    cv.rect(tx - 13, ty + 8, 27, 10, P["tower1"])
    cv.rect(tx - 13, ty + 8, 27, 3, P["tower3"])
    cv.hline(tx - 13, tx + 13, ty + 17, P["tower0"])
    # peak + finial
    cv.rect(tx - 4, ty - 4, 9, 6, P["tower2"])
    cv.vline(tx, ty - 12, ty - 4, P["rail1"])
    cv.p(tx, ty - 13, P["beacon_dk"])

    # School buildings
    bx, by, bw, bh = 248, 136, 140, 28
    cv.rect(bx, by, bw, bh, P["bldg1"])
    cv.rect(bx, by, bw, 3, P["bldg3"])
    cv.hline(bx, bx + bw - 1, by, P["bldg4"])
    # gym bump
    cv.rect(bx + 74, by - 12, 56, 14, P["bldg0"])
    cv.rect(bx + 74, by - 12, 56, 3, P["bldg2"])
    cv.hline(bx + 74, bx + 129, by - 12, P["bldg3"])
    # windows, some lit, with mullions and a warm dither glow
    rng3 = random.Random(12)
    for i in range(15):
        wx = bx + 6 + i * 9
        wy = by + 9
        on = i in (2, 5, 6, 11, 13)
        dim = i % 4 == 0
        bg = P["win_on"] if on else (P["win_dim"] if dim else P["win_off"])
        cv.rect(wx, wy, 6, 8, bg)
        if on:
            cv.p(wx + 1, wy + 1, P["win_on2"])
        cv.vline(wx + 3, wy, wy + 7, P["bldg0"])
        cv.hline(wx, wx + 5, wy + 4, P["bldg0"])
        cv.frame(wx - 1, wy - 1, 8, 10, P["bldg0"])
    # flagpole
    cv.vline(bx - 5, by - 18, by + 10, P["rail0"])
    cv.vline(bx - 4, by - 18, by + 10, P["rail1"])
    cv.rect(bx - 3, by - 17, 9, 5, P["navy"])
    cv.p(bx + 1, by - 15, P["gold"])
    cv.p(bx + 2, by - 14, P["gold_lt"])

    bx2 = 418
    cv.rect(bx2, 142, 78, 22, P["bldg0"])
    cv.rect(bx2, 142, 78, 3, P["bldg2"])
    for i in range(7):
        lit = i in (1, 4, 5)
        cv.rect(bx2 + 6 + i * 10, 150, 7, 7, P["win_on"] if lit else P["win_off"])
        cv.vline(bx2 + 9 + i * 10, 150, 156, P["bldg0"])

    # Parking-lot lights + tiny car glints
    for x, yb in [
        (28, 164), (48, 166), (68, 165),
        (188, 163), (208, 165),
        (500, 164), (520, 166), (545, 165), (570, 167),
        (598, 164), (620, 166),
    ]:
        cv.vline(x, yb - 12, yb, P["tower0"])
        cv.p(x, yb - 13, P["park2"])
        cv.p(x - 1, yb - 13, P["park"])
        cv.p(x + 1, yb - 13, P["park"])
        # tiny dithered spill
        for dx, dy in ((-2, 1), (-1, 2), (0, 2), (1, 2), (2, 1)):
            if bayer_t(x + dx, yb - 13 + dy, 4) < 0.5:
                cv.p(x + dx, yb - 13 + dy, P["glow4"])
    for x, y in [(32, 168), (54, 169), (196, 168), (506, 169), (526, 168), (574, 170), (606, 169)]:
        cv.p(x, y, P["win_dim"])
        cv.p(x + 1, y, P["park"])

    cv.rect(0, 186, VIEW_W, VIEW_H - 186, P["hill0"])
    return cv


# ---------------------------------------------------------------------------
# MID — 960x360, transparent sky, architecture + floor + light beams/halos.
# ---------------------------------------------------------------------------
def _lamp_bank(cv: CV, cx, top, cols=5, rows=4, tilt=0):
    lamp_w, lamp_h, gap = 6, 5, 2
    pad = 4
    bw = cols * (lamp_w + gap) - gap + pad * 2
    bh = rows * (lamp_h + gap) - gap + pad * 2
    x0 = cx - bw // 2
    y0 = top
    # housing
    cv.rect(x0 - 2, y0 - 4, bw + 4, bh + 6, P["steel0"])
    cv.frame(x0 - 2, y0 - 4, bw + 4, bh + 6, P["steel4"])
    cv.frame(x0 - 1, y0 - 3, bw + 2, bh + 4, P["steel2"])
    # visor
    cv.rect(x0 - 3, y0 - 6, bw + 6, 4, P["steel3"])
    cv.hline(x0 - 3, x0 + bw + 2, y0 - 6, P["steel5"])
    cv.hline(x0 - 3, x0 + bw + 2, y0 - 3, P["steel1"])
    # lamps ON (anim will flicker some)
    for r in range(rows):
        shift = tilt * r
        for c in range(cols):
            lx = x0 + pad + c * (lamp_w + gap) + shift
            ly = y0 + pad + r * (lamp_h + gap)
            cv.rect(lx - 1, ly - 1, lamp_w + 2, lamp_h + 2, P["steel1"])
            cv.rect(lx, ly, lamp_w, lamp_h, P["lamp2"])
            cv.rect(lx + 1, ly, lamp_w - 2, lamp_h - 2, P["lamp1"])
            cv.p(lx + 1, ly, P["lamp0"])
            cv.hline(lx, lx + lamp_w - 1, ly + lamp_h - 1, P["lamp3"])
    return x0, y0, bw, bh


def _tower(cv: CV, cx, bank_top, base_y, tilt=0, cols=5, rows=4):
    x0, y0, bw, bh = _lamp_bank(cv, cx, bank_top, cols=cols, rows=rows, tilt=tilt)
    pole_top = y0 + bh + 2
    # lattice pole
    cv.rect(cx - 4, pole_top, 9, base_y - pole_top, P["steel2"])
    cv.vline(cx - 4, pole_top, base_y, P["steel0"])
    cv.vline(cx + 4, pole_top, base_y, P["steel4"])
    cv.vline(cx - 3, pole_top, base_y, P["steel1"])
    for y in range(pole_top + 6, base_y - 8, 8):
        cv.hline(cx - 4, cx + 4, y, P["steel0"])
        cv.p(cx - 2, y + 3, P["steel0"])
        cv.p(cx + 2, y + 5, P["steel1"])
        # X brace
        cv.p(cx - 1, y + 2, P["steel1"])
        cv.p(cx + 1, y + 4, P["steel1"])
    # footing
    cv.rect(cx - 10, base_y - 8, 21, 8, P["conc2"])
    cv.rect(cx - 12, base_y - 3, 25, 4, P["conc1"])
    cv.hline(cx - 10, cx + 10, base_y - 8, P["conc4"])
    cv.vline(cx - 10, base_y - 8, base_y, P["conc0"])
    return x0, y0, bw, bh


def _dithered_halo(cv: CV, cx, cy, rmax, only_clear=True):
    """Radial ordered-dither bloom. Paints opaque glow pixels; holes show far sky."""
    for y in range(cy - rmax, cy + rmax + 1):
        for x in range(cx - rmax, cx + rmax + 1):
            if not (0 <= x < cv.w and 0 <= y < cv.h):
                continue
            if only_clear and not cv.is_clear(x, y):
                continue
            # slightly wider than tall
            d = math.sqrt((x - cx) ** 2 + ((y - cy) * 1.15) ** 2)
            if d >= rmax:
                continue
            t = (1.0 - d / rmax) ** 1.35
            if t < 0.06:
                continue
            if t > 0.75:
                col, dens = P["glow1"], min(1.0, t)
            elif t > 0.5:
                col, dens = P["glow2"], t
            elif t > 0.28:
                col, dens = P["glow3"], t * 0.95
            else:
                col, dens = P["glow4"], t * 1.1
            if dens > bayer_t(x, y, 8):
                cv.p(x, y, col)


def _dithered_beam(cv: CV, cx, y0, y1, half0, half1, only_clear=True, phase=0):
    """Downward light shaft, widening, dither-fading. Does not paint the floor band."""
    y1 = min(y1, FLOOR_TOP - 2)
    if y1 <= y0:
        return
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        half = half0 + (half1 - half0) * t
        # fade out toward the bottom
        fade = (1.0 - t) * (1.0 - t * 0.35)
        for dx in range(-int(half) - 1, int(half) + 2):
            x = cx + dx
            if not (0 <= x < cv.w):
                continue
            if only_clear and not cv.is_clear(x, y):
                # allow painting over mid's transparent sky only; skip solid
                # (beams over stands are drawn later with a lighter hand)
                continue
            edge = 1.0 - min(1.0, abs(dx) / max(0.5, half))
            dens = fade * edge * 0.55
            if dens <= 0:
                continue
            if dens > bayer_t(x + phase, y, 4):
                col = P["beam1"] if edge > 0.65 and fade > 0.45 else (P["beam2"] if edge > 0.3 else P["beam3"])
                cv.p(x, y, col)


def _beam_over_stands(cv: CV, cx, y0, y1, half0, half1, phase=0):
    """Sparse shaft over already-drawn stands — only dithers lighter pixels on dark concrete."""
    y1 = min(y1, FLOOR_TOP - 4)
    for y in range(max(y0, ROW_TOP - 4), y1 + 1):
        t = (y - y0) / max(1, (y1 - y0))
        half = half0 + (half1 - half0) * t
        fade = (1.0 - t) * 0.28
        for dx in range(-int(half), int(half) + 1):
            x = cx + dx
            if not (0 <= x < cv.w and 0 <= y < cv.h):
                continue
            if cv.is_clear(x, y):
                continue
            edge = 1.0 - min(1.0, abs(dx) / max(0.5, half))
            dens = fade * edge
            if dens > bayer_t(x + phase, y, 8):
                # don't clobber already-bright lamps; only lift dark pixels
                existing = cv.get(x, y)
                if existing and existing[0] < 180:
                    cv.p(x, y, P["beam3"] if dens < 0.2 else P["beam2"])


def _scoreboard(cv: CV):
    gx0, gx1 = 352, 608
    gy = 14
    # truss
    cv.rect(gx0, gy, gx1 - gx0, 8, P["steel2"])
    cv.hline(gx0, gx1 - 1, gy, P["steel5"])
    cv.hline(gx0, gx1 - 1, gy + 7, P["steel0"])
    for x in range(gx0 + 6, gx1, 12):
        cv.p(x, gy + 2, P["steel0"])
        cv.p(x + 3, gy + 4, P["steel1"])
        cv.p(x + 6, gy + 2, P["steel0"])
        cv.p(x + 3, gy + 3, P["steel4"])
    for hx in (392, 480, 568):
        cv.rect(hx, gy + 8, 3, 8, P["steel3"])
        cv.vline(hx, gy + 8, gy + 15, P["steel5"])
        cv.vline(hx + 2, gy + 8, gy + 15, P["steel0"])

    bx, by, bw, bh = 384, 24, 192, 74
    # bezel
    cv.rect(bx - 5, by - 5, bw + 10, bh + 10, P["steel0"])
    cv.frame(bx - 5, by - 5, bw + 10, bh + 10, P["steel5"])
    cv.frame(bx - 4, by - 4, bw + 8, bh + 8, P["steel3"])
    cv.frame(bx - 2, by - 2, bw + 4, bh + 4, P["navy_dk"])
    cv.rect(bx, by, bw, bh, P["outline"])
    cv.frame(bx, by, bw, bh, P["navy_lt"])
    cv.frame(bx + 1, by + 1, bw - 2, bh - 2, P["navy"])

    cv.rect(bx + 5, by + 4, bw - 10, 14, P["navy"])
    tw = text_width("BAND WARS", scale=1, spacing=1)
    draw_text(cv, bx + (bw - tw) // 2, by + 7, "BAND WARS", P["gold_lt"], scale=1, spacing=1)
    # gold underline
    cv.hline(bx + 20, bx + bw - 21, by + 18, P["gold_dk"])

    draw_text(cv, bx + 10, by + 24, "JMHS", P["gold"], scale=1, spacing=1)
    draw_text(cv, bx + bw - 10 - text_width("VISIT"), by + 24, "VISIT", P["white_sh"], scale=1, spacing=1)
    draw_text(cv, bx + 44, by + 34, "21", P["flash"], scale=2, spacing=1)
    draw_text(cv, bx + bw - 44 - text_width("17", scale=2), by + 34, "17", P["flash"], scale=2, spacing=1)

    cv.rect(bx + 5, by + bh - 16, bw - 10, 12, P["navy_dk"])
    draw_text(cv, bx + 10, by + bh - 14, "4TH 0:00", P["white"], scale=1, spacing=1)
    draw_text(cv, bx + bw - 10 - text_width("FINALS"), by + bh - 14, "FINALS", P["gold"], scale=1, spacing=1)

    for i, lx in enumerate(range(bx + 8, bx + bw - 6, 7)):
        cv.rect(lx, by + 2, 4, 2, P["lamp2"] if i % 2 == 0 else P["lamp3"])
        cv.p(lx + 1, by + 2, P["lamp0"])


def _press_box(cv: CV):
    px, py, pw, ph = 360, 104, 240, 48
    # thin parapet sitting just under the hanging scoreboard
    cv.rect(px - 8, py - 6, pw + 16, 7, P["conc2"])
    cv.hline(px - 8, px + pw + 7, py - 6, P["conc5"])
    cv.rect(px - 6, py - 7, pw + 12, 2, P["conc3"])
    # warm dither on the roof only (not up into the ticker)
    for y in range(py - 6, py):
        for x in range(px - 6, px + pw + 6):
            if bayer_t(x, y, 8) < 0.16:
                cv.p(x, y, P["glow4"])
    # body + rusticated corners
    cv.rect(px, py, pw, ph, P["conc2"])
    cv.vline(px, py, py + ph - 1, P["conc0"])
    cv.vline(px + pw - 1, py, py + ph - 1, P["conc4"])
    cv.rect(px, py + 23, pw, 3, P["conc4"])
    cv.hline(px, px + pw - 1, py + 23, P["conc0"])
    # concrete speckles
    rng = random.Random(42)
    for _ in range(180):
        x = rng.randint(px + 2, px + pw - 3)
        y = rng.randint(py + 1, py + ph - 2)
        cv.p(x, y, P["conc1"] if rng.random() < 0.6 else P["conc3"])

    def windows(y, n=9):
        gap, ww, wh = 4, 18, 14
        total = n * ww + (n - 1) * gap
        x0 = px + (pw - total) // 2
        for i in range(n):
            wx = x0 + i * (ww + gap)
            cv.rect(wx - 1, y - 1, ww + 2, wh + 2, P["outline"])
            lit = i not in (3, 7)
            cv.rect(wx, y, ww, wh, P["win_on"] if lit else P["win_dim"])
            if lit:
                # hot corner
                cv.p(wx + 1, y + 1, P["win_on2"])
                cv.p(wx + 2, y + 1, P["win_on2"])
            cv.vline(wx + ww // 2, y, y + wh - 1, P["bldg0"])
            cv.hline(wx, wx + ww - 1, y + 6, P["bldg0"])
            if i in (1, 2, 5, 6, 8):
                hx = wx + 4 + (i % 3)
                cv.rect(hx, y + 8, 3, 3, P["outline"])
                cv.rect(hx - 1, y + 11, 5, 3, P["outline"])

    windows(py + 4, 9)
    windows(py + 30, 9)
    # mast + dish
    ax = px + pw - 18
    cv.vline(ax, py - 30, py - 10, P["steel5"])
    cv.vline(ax + 1, py - 30, py - 10, P["steel2"])
    cv.p(ax, py - 31, P["beacon"])
    cv.p(ax + 1, py - 31, P["beacon2"])
    cv.p(ax, py - 32, P["lamp0"])
    cv.rect(px + 22, py - 14, 10, 5, P["steel4"])
    cv.vline(px + 26, py - 18, py - 8, P["steel3"])
    for cx in (px + 18, px + pw // 2, px + pw - 19):
        cv.rect(cx - 3, py + ph, 7, 6, P["conc0"])


def _bleachers(cv: CV):
    top, bot = ROW_TOP, BLEACH_BOT
    cv.rect(6, top - 7, MID_W - 12, 8, P["conc1"])
    cv.hline(6, MID_W - 7, top - 7, P["conc4"])
    # rear wall
    cv.rect(2, top - 2, MID_W - 4, bot - top + 4, P["seat0"])
    rng = random.Random(9)

    for r in range(NROWS):
        y = top + r * ROW_H
        cv.rect(4, y, MID_W - 8, 2, P["riser1"])
        cv.hline(4, MID_W - 5, y, P["riser0"])
        cv.rect(4, y + 2, MID_W - 8, 3, P["seat3"])
        cv.hline(4, MID_W - 5, y + 2, P["seat4"])
        cv.rect(4, y + 5, MID_W - 8, ROW_H - 5, P["seat1"])
        cv.rect(4, y + ROW_H - 3, MID_W - 8, 2, P["seat2"])
        cv.hline(4, MID_W - 5, y + ROW_H - 1, P["seat0"])
        # seat dividers + slight color variation (empty seat look under the crowd)
        for x in range(8, MID_W - 8, 7):
            cv.p(x, y + 3, P["seat0"])
            cv.p(x, y + ROW_H - 3, P["seat3"])
        # dark packed-mass undertone in the people zone (so bob gaps stay full)
        for yy in range(y + 4, y + ROW_H - 2):
            for xx in range(8, MID_W - 8):
                if in_aisle(xx, 7):
                    continue
                if rng.random() < 0.55:
                    cv.p(xx, yy, rng.choice((P["navy_dk"], P["c_black"], P["seat0"], P["c_mar"], P["c_denim"], P["navy"])))

    # aisles / stairs
    for ax in AISLES:
        cv.rect(ax - 8, top, 17, bot - top, P["conc2"])
        for r in range(NROWS):
            y = top + r * ROW_H
            cv.hline(ax - 8, ax + 8, y + ROW_H - 1, P["conc0"])
            cv.hline(ax - 8, ax + 8, y + ROW_H - 2, P["conc4"])
            # tread highlight
            cv.hline(ax - 6, ax + 6, y + 3, P["conc3"])
        cv.vline(ax - 8, top, bot - 1, P["rail0"])
        cv.vline(ax + 8, top, bot - 1, P["rail0"])
        for r in range(NROWS):
            cv.p(ax - 8, top + r * ROW_H + 2, P["rail1"])
            cv.p(ax + 8, top + r * ROW_H + 2, P["rail1"])
        # section letter near the top of a couple of aisles
    for ax, letter in ((200, "A"), (320, "B"), (640, "C"), (760, "D")):
        draw_text(cv, ax - 2, top + 3, letter, P["gold_dk"], scale=1, spacing=0)

    # fascia + bunting
    fy = bot
    cv.rect(4, fy - 12, MID_W - 8, 14, P["navy_dk"])
    cv.rect(4, fy - 12, MID_W - 8, 3, P["navy"])
    cv.hline(4, MID_W - 5, fy - 12, P["gold"])
    cv.hline(4, MID_W - 5, fy - 9, P["gold_dk"])
    for x in range(12, MID_W - 12, 14):
        col = P["navy"] if (x // 14) % 2 == 0 else P["gold"]
        col2 = P["navy_dk"] if col == P["navy"] else P["gold_dk"]
        cv.rect(x, fy - 8, 10, 7, col)
        cv.p(x + 4, fy, col)
        cv.p(x + 5, fy, col)
        cv.p(x + 3, fy, col2)
        cv.p(x + 6, fy, col2)

    bw = text_width("GO JMHS", scale=1, spacing=1)
    bx = FIFTY - bw // 2 - 6
    cv.rect(bx, bot - 24, bw + 12, 12, P["navy"])
    cv.frame(bx, bot - 24, bw + 12, 12, P["gold"])
    cv.frame(bx + 1, bot - 23, bw + 10, 10, P["gold_dk"])
    draw_text(cv, bx + 6, bot - 21, "GO JMHS", P["gold_lt"], scale=1, spacing=1)

    # front railing
    cv.rect(2, bot, MID_W - 4, 3, P["rail0"])
    cv.hline(2, MID_W - 3, bot, P["rail2"])
    for x in range(6, MID_W - 4, 5):
        cv.vline(x, bot, bot + 6, P["rail0"])
        cv.p(x, bot + 1, P["rail1"])
    cv.hline(2, MID_W - 3, bot + 6, P["rail1"])
    cv.hline(2, MID_W - 3, bot + 7, P["rail0"])


def _goal_post(cv: CV, x_goal, facing=1):
    base_y = FLOOR_TOP
    cross_y = 224
    top_y = 160
    stem_x = x_goal - facing * 6
    cv.rect(stem_x - 2, cross_y, 5, base_y - cross_y, P["post2"])
    cv.vline(stem_x - 2, cross_y, base_y, P["post0"])
    cv.vline(stem_x + 2, cross_y, base_y, P["post3"])
    cv.rect(stem_x - 6, base_y - 12, 13, 12, P["post0"])
    cv.rect(stem_x - 5, base_y - 11, 11, 9, P["post1"])
    cv.rect(stem_x - 4, base_y - 10, 9, 5, P["post2"])
    cv.rect(stem_x - 7, base_y - 2, 15, 2, P["white_dk"])
    half = 30
    cv.rect(stem_x - half, cross_y, half * 2 + 5, 5, P["post2"])
    cv.hline(stem_x - half, stem_x + half + 4, cross_y, P["post3"])
    cv.hline(stem_x - half, stem_x + half + 4, cross_y + 4, P["post0"])
    for ux in (stem_x - half, stem_x + half):
        cv.rect(ux, top_y, 5, cross_y - top_y + 5, P["post2"])
        cv.vline(ux, top_y, cross_y + 4, P["post3"])
        cv.vline(ux + 4, top_y, cross_y + 4, P["post0"])
        cv.rect(ux, top_y, 5, 3, P["post4"])


def _track_and_sideline(cv: CV):
    cv.rect(0, BLEACH_BOT + 2, MID_W, FLOOR_TOP - (BLEACH_BOT + 2), P["track1"])
    rng = random.Random(300)
    for y in range(BLEACH_BOT + 2, FLOOR_TOP):
        for x in range(MID_W):
            t = (y - (BLEACH_BOT + 2)) / max(1, FLOOR_TOP - BLEACH_BOT - 3)
            col = dither_pick(x, y, t * 0.4 + 0.2, P["track1"], P["track2"], 4)
            if rng.random() < 0.04:
                col = rng.choice((P["track0"], P["track3"], P["track4"]))
            cv.p(x, y, col)
    cv.hline(0, MID_W - 1, BLEACH_BOT + 5, P["track_line"])
    cv.hline(0, MID_W - 1, FLOOR_TOP - 3, P["track0"])

    # podium
    cv.rect(300, 290, 24, 10, P["wood"])
    cv.rect(301, 291, 22, 3, P["wood_lt"])
    cv.vline(300, 290, 299, P["wood_dk"])
    cv.vline(323, 290, 299, P["wood_dk"])
    cv.hline(300, 323, 290, P["gold_dk"])
    # cases
    for x, w in ((148, 18), (176, 14), (786, 18), (812, 16)):
        cv.rect(x, 291, w, 9, P["wood_dk"])
        cv.rect(x + 1, 292, w - 2, 4, P["wood"])
        cv.hline(x, x + w - 1, 291, P["wood_lt"])
        cv.p(x + w - 3, 296, P["gold"])
    # first-down marker
    cv.rect(558, 272, 4, 28, P["post2"])
    cv.vline(558, 272, 299, P["post0"])
    cv.vline(561, 272, 299, P["post3"])
    cv.rect(554, 270, 12, 7, P["post3"])
    cv.frame(554, 270, 12, 7, P["post0"])
    # small mid cooler (the big one is on the near layer)
    cv.rect(698, 288, 12, 12, P["cool0"])
    cv.rect(699, 289, 10, 6, P["cool1"])
    cv.rect(700, 287, 8, 3, P["cool3"])
    cv.rect(701, 297, 6, 3, P["cool4"])
    # flag poles (cloth in anim)
    for fx in (200, 320, 640, 760, 80, 880):
        cv.vline(fx, 246, 299, P["steel5"])
        cv.vline(fx + 1, 246, 299, P["steel2"])
        cv.rect(fx - 2, 297, 6, 3, P["steel0"])
        cv.p(fx, 245, P["gold"])


def _field(cv: CV):
    """Turf y=300..359 with a dithered lit pool. Crisp yard lines on top."""
    # endzones
    for x in range(0, GOAL_L):
        for y in range(FLOOR_TOP, MID_H):
            cv.p(x, y, dither_pick(x, y, 0.35, P["turf_end0"], P["turf_end1"], 4))
    for x in range(GOAL_R, MID_W):
        for y in range(FLOOR_TOP, MID_H):
            cv.p(x, y, dither_pick(x, y, 0.35, P["turf_end0"], P["turf_end1"], 4))
    cv.hline(8, GOAL_L - 8, FLOOR_TOP + 1, P["gold_dk"])
    cv.hline(GOAL_R + 8, MID_W - 8, FLOOR_TOP + 1, P["gold_dk"])
    draw_text(cv, 16, FLOOR_TOP + 2, "JMHS", P["gold"], scale=1, spacing=1)
    w = text_width("JMHS", scale=1, spacing=1)
    draw_text(cv, MID_W - 16 - w, FLOOR_TOP + 2, "JMHS", P["gold"], scale=1, spacing=1)

    # in-field stripes + lit pool
    # pool: wide ellipse around midfield, plus a slight warm lift from each tower
    for y in range(FLOOR_TOP, MID_H):
        for x in range(GOAL_L, GOAL_R):
            stripe = ((x - GOAL_L) // (YARD * 5)) % 2
            base_a, base_b = (P["turf3"], P["turf4"]) if stripe == 0 else (P["turf5"], P["turf6"])
            # ellipse pool centered slightly above the feet line
            nx = (x - FIFTY) / 260.0
            ny = (y - 328) / 42.0
            pool = max(0.0, 1.0 - (nx * nx + ny * ny))
            pool = pool * pool
            # near-camera darkening at the very bottom
            if y >= 352:
                pool *= 0.45
            col = dither_pick(x, y, 0.4 + 0.2 * stripe, base_a, base_b, 4)
            if pool > 0.15:
                hot = P["turf_hot"] if stripe else P["turf_warm"]
                col = dither_pick(x, y + 1, min(1.0, pool * 0.85), col, hot, 8)
            if y >= 354:
                col = dither_pick(x, y, 0.7, P["turf1"], P["turf0"], 4)
            cv.p(x, y, col)

    # very sparse grass only at the top and bottom of the band (not the fight strip)
    rng = random.Random(50)
    for _ in range(260):
        x = rng.randint(0, MID_W - 1)
        if rng.random() < 0.6:
            y = rng.randint(FLOOR_TOP + 2, FLOOR_TOP + 11)
        else:
            y = rng.randint(350, 357)
        cv.p(x, y, rng.choice((P["turf1"], P["turf2"], P["turf6"])))

    # sideline
    cv.hline(0, MID_W - 1, FLOOR_TOP, P["line"])
    cv.hline(0, MID_W - 1, FLOOR_TOP + 1, P["line2"])

    # yard lines (always crisp, drawn last)
    for yard in range(0, 101, 10):
        x = GOAL_L + yard * YARD
        cv.vline(x, FLOOR_TOP, MID_H - 1, P["line"])
        if yard == 50:
            cv.vline(x - 1, FLOOR_TOP, MID_H - 1, P["line2"])
            cv.vline(x + 1, FLOOR_TOP, MID_H - 1, P["line2"])
            cv.vline(x, FLOOR_TOP, MID_H - 1, P["line"])
    for yard in range(0, 101, 5):
        if yard % 10 == 0:
            continue
        x = GOAL_L + yard * YARD
        cv.vline(x, FLOOR_TOP + 2, FLOOR_TOP + 7, P["line3"])
        cv.vline(x, MID_H - 6, MID_H - 1, P["line3"])

    def yard_num(yard, label):
        x = GOAL_L + yard * YARD
        w = text_width(label, scale=1, spacing=1)
        draw_text(cv, x - w // 2, FLOOR_TOP + 4, label, P["line"], scale=1, spacing=1)

    for yd, lab in ((20, "20"), (30, "30"), (40, "40"), (50, "50"), (60, "40"), (70, "30"), (80, "20")):
        yard_num(yd, lab)
    cv.vline(GOAL_L - 1, FLOOR_TOP, FLOOR_TOP + 8, P["gold_dk"])
    cv.vline(GOAL_R + 1, FLOOR_TOP, FLOOR_TOP + 8, P["gold_dk"])


def draw_mid() -> CV:
    cv = CV(MID_W, MID_H, bg=None)
    # Halos + sky beams first (only on transparent sky), then towers on top
    for cx, top, cols, rows, tilt in TOWERS:
        lamp_w, lamp_h, gap, pad = 6, 5, 2, 4
        bw = cols * (lamp_w + gap) - gap + pad * 2
        bh = rows * (lamp_h + gap) - gap + pad * 2
        _dithered_halo(cv, cx, top + bh // 2, 54, only_clear=True)
        # slight inward aim
        aim = 480 + (cx - 480) * 0.35
        _dithered_beam(cv, cx, top + bh, 292, 6, 28, only_clear=True, phase=cx)

    for cx, top, cols, rows, tilt in TOWERS:
        _tower(cv, cx, top, 152, tilt=tilt, cols=cols, rows=rows)

    _press_box(cv)
    _scoreboard(cv)
    _bleachers(cv)
    _goal_post(cv, GOAL_L, facing=1)
    _goal_post(cv, GOAL_R, facing=-1)
    _track_and_sideline(cv)
    _field(cv)

    # sparse shafts over the stands (don't touch the floor)
    for cx, top, cols, rows, tilt in TOWERS:
        lamp_h, gap, pad = 5, 2, 4
        bh = rows * (lamp_h + gap) - gap + pad * 2
        _beam_over_stands(cv, cx, top + bh, 294, 8, 30, phase=cx)

    # leftover mid-seat flavor (a shako, a jacket) — will sit under the packed crowd, that's fine
    return cv




# ---------------------------------------------------------------------------
# CROWD + ANIM — 8 frames, packed SF2-style bleachers, flags, light flicker.
# ---------------------------------------------------------------------------
def _bob(group, frame):
    # 1px head bob, 8-frame loop, phase-offset groups
    tables = {
        "A": (0, 0, -1, -1, 0, 0, 1, 0),
        "B": (-1, 0, 0, 1, 0, 0, -1, -1),
        "C": (0, 1, 0, 0, -1, -1, 0, 1),
        "D": (1, 0, -1, 0, 0, 1, 0, -1),
    }
    return tables[group][frame % 8]


def _arm(group, frame):
    # 0 down, 1 mid, 2 up
    tables = {
        "A": (0, 1, 2, 2, 1, 0, 0, 1),
        "B": (2, 2, 1, 0, 0, 1, 2, 2),
        "C": (0, 0, 1, 2, 2, 1, 0, 0),
        "D": (1, 0, 0, 1, 2, 2, 1, 0),
    }
    return tables[group][frame % 8]


def _draw_arm(cv, x, y, skin, body, level, side=1):
    """Raised arm. level 0=none/down, 1=mid, 2=up. side +1 right, -1 left."""
    if level <= 0:
        return
    sx = x + (4 if side > 0 else -1)
    if level == 1:
        cv.p(sx, y - 7, body)
        cv.p(sx + side, y - 8, skin[1])
        cv.p(sx + side, y - 9, skin[2])
    else:
        cv.p(sx, y - 7, body)
        cv.vline(sx + side, y - 13, y - 7, skin[1])
        cv.p(sx + side, y - 14, skin[2])
        cv.p(sx + side * 2, y - 14, skin[1])


def _civ(cv, x, y, skin, hair, body, body2, bob, arm, front=False, foam=False):
    y = y + bob
    sk_d, sk, sk_l = skin
    if front:
        cv.rect(x + 1, y - 13, 4, 3, hair)
        cv.rect(x + 1, y - 11, 4, 4, sk)
        cv.p(x + 1, y - 11, hair)
        cv.p(x + 2, y - 10, sk_d)  # eye socket
        cv.p(x + 4, y - 10, sk_d)
        cv.p(x + 1, y - 9, sk_d)
        cv.rect(x, y - 7, 6, 7, body)
        cv.p(x + 1, y - 6, body2)
        cv.p(x + 4, y - 6, body2)
        cv.p(x, y, P["shoe"])
        cv.p(x + 5, y, P["shoe"])
        _draw_arm(cv, x, y, skin, body, arm, side=1)
        if foam and arm >= 1:
            fx, fy = x + 6, y - 16
            cv.rect(fx, fy, 3, 5, P["c_yellow"])
            cv.p(fx + 1, fy - 1, P["c_yellow"])
    else:
        cv.rect(x + 1, y - 10, 3, 2, hair)
        cv.rect(x + 1, y - 8, 3, 3, sk)
        cv.p(x + 1, y - 8, hair)
        cv.p(x + 1, y - 7, sk_d)
        cv.rect(x, y - 5, 5, 5, body)
        cv.p(x + 1, y - 4, body2)
        cv.p(x, y, P["shoe"])
        cv.p(x + 4, y, P["shoe"])
        if arm >= 2:
            cv.vline(x + 5, y - 13, y - 5, sk)
            cv.p(x + 5, y - 14, sk_l)
        elif arm == 1:
            cv.p(x + 5, y - 8, sk)
            cv.p(x + 6, y - 9, sk_l)


def _band(cv, x, y, skin, hair, bob, arm, front=False, plume=None, brass=False):
    y = y + bob
    sk_d, sk, sk_l = skin
    plume = plume or P["gold_lt"]
    if front:
        cv.p(x + 2, y - 18, plume)
        cv.p(x + 2, y - 19, plume)
        cv.p(x + 3, y - 18, P["white"])
        cv.rect(x, y - 17, 6, 6, P["navy"])
        cv.hline(x, x + 5, y - 17, P["navy_dk"])
        cv.hline(x, x + 5, y - 13, P["gold"])
        cv.p(x + 2, y - 15, P["gold_lt"])
        cv.rect(x + 1, y - 11, 4, 4, sk)
        cv.p(x + 1, y - 11, hair)
        cv.p(x + 2, y - 10, sk_d)
        cv.p(x + 4, y - 10, sk_d)
        cv.rect(x, y - 7, 6, 7, P["navy"])
        cv.vline(x + 2, y - 7, y - 2, P["white"])
        cv.p(x + 3, y - 5, P["gold"])
        cv.p(x, y, P["navy_dk"])
        cv.p(x + 5, y, P["navy_dk"])
        if brass:
            cv.rect(x + 6, y - 9, 5, 3, P["gold"])
            cv.p(x + 10, y - 8, P["gold_lt"])
            cv.p(x + 7, y - 10, P["gold_dk"])
        _draw_arm(cv, x, y, skin, P["navy"], arm, side=-1 if brass else 1)
    else:
        cv.p(x + 2, y - 14, plume)
        cv.p(x + 2, y - 15, plume)
        cv.rect(x, y - 13, 5, 5, P["navy"])
        cv.hline(x, x + 4, y - 10, P["gold"])
        cv.rect(x + 1, y - 8, 3, 3, sk)
        cv.p(x + 1, y - 8, hair)
        cv.rect(x, y - 5, 5, 5, P["navy"])
        cv.vline(x + 2, y - 5, y - 2, P["white"])
        if brass:
            cv.vline(x + 5, y - 7, y - 4, P["gold"])
            cv.p(x + 6, y - 6, P["gold_lt"])
        if arm >= 2:
            cv.vline(x + 5, y - 12, y - 5, sk)
            cv.p(x + 5, y - 13, sk_l)


def _sousa(cv, x, y, skin, hair, bob):
    y = y + bob
    sk_d, sk, _ = skin
    cv.rect(x + 3, y - 15, 6, 5, P["navy"])
    cv.hline(x + 3, x + 8, y - 12, P["gold"])
    cv.rect(x + 4, y - 10, 4, 3, sk)
    cv.p(x + 4, y - 10, hair)
    cv.rect(x + 3, y - 7, 6, 7, P["navy"])
    cv.vline(x + 5, y - 7, y - 3, P["white"])
    # bell
    cv.rect(x - 2, y - 12, 6, 10, P["gold"])
    cv.rect(x - 1, y - 11, 4, 8, P["gold_lt"])
    cv.frame(x - 2, y - 12, 6, 10, P["gold_dk"])
    cv.p(x - 1, y - 10, P["gold"])
    cv.rect(x + 9, y - 7, 4, 3, P["gold_dk"])
    cv.p(x + 11, y - 6, P["gold"])


def _guard(cv, x, y, skin, hair, bob, arm, front=False):
    y = y + bob
    sk_d, sk, sk_l = skin
    if front:
        cv.rect(x + 1, y - 14, 4, 3, hair)
        cv.rect(x + 1, y - 12, 4, 4, sk)
        cv.p(x + 1, y - 11, sk_d)
        cv.rect(x, y - 8, 6, 8, P["navy"])
        cv.hline(x, x + 5, y - 5, P["gold"])
        cv.hline(x, x + 5, y - 4, P["gold_lt"])
        cv.p(x + 5, y - 8, P["white"])
        cv.p(x, y, P["navy_dk"])
        cv.p(x + 5, y, P["navy_dk"])
        _draw_arm(cv, x, y, skin, P["navy"], arm, side=1)
    else:
        cv.rect(x + 1, y - 11, 3, 2, hair)
        cv.rect(x + 1, y - 9, 3, 3, sk)
        cv.rect(x, y - 6, 5, 6, P["navy"])
        cv.hline(x, x + 4, y - 4, P["gold"])
        if arm >= 2:
            cv.vline(x + 5, y - 14, y - 6, sk)
            cv.p(x + 5, y - 15, sk_l)


def _drummer(cv, x, y, skin, hair, bob):
    y = y + bob
    sk_d, sk, _ = skin
    cv.rect(x, y - 15, 5, 5, P["navy"])
    cv.hline(x, x + 4, y - 12, P["gold"])
    cv.p(x + 2, y - 16, P["gold_lt"])
    cv.rect(x + 1, y - 10, 3, 3, sk)
    cv.p(x + 1, y - 10, hair)
    cv.rect(x, y - 7, 5, 7, P["navy"])
    # snare in front
    cv.rect(x - 1, y - 5, 8, 5, P["white_sh"])
    cv.hline(x - 1, x + 6, y - 5, P["gold"])
    cv.hline(x - 1, x + 6, y - 1, P["gold_dk"])
    cv.p(x + 2, y - 3, P["white"])


def _sign(cv, x, y, text, bob, arm, skin, hair, body):
    # person holding a sign above their head
    _civ(cv, x, y, skin, hair, body, body, bob, 0, front=True)
    y2 = y + bob - 16 - (1 if arm else 0)
    w = text_width(text, scale=1, spacing=1)
    cv.rect(x + 1, y2, w + 4, 10, P["navy_dk"])
    cv.frame(x + 1, y2, w + 4, 10, P["gold"])
    draw_text(cv, x + 3, y2 + 2, text, P["gold_lt"], scale=1, spacing=1)
    # sticks
    cv.vline(x + 2, y2 + 10, y + bob - 7, P["wood"])
    cv.vline(x + w + 2, y2 + 10, y + bob - 7, P["wood"])


def layout_crowd():
    """Deterministic packed bleacher layout. Returns list of person dicts."""
    rng = random.Random(2026)
    people = []
    for row in range(NROWS):
        if row < 3:
            spacing = 5
        elif row < 6:
            spacing = 6
        else:
            spacing = 7
        front = row >= 5
        x = 10
        while x < MID_W - 12:
            if in_aisle(x, 8) or in_aisle(x + spacing // 2, 8):
                x += 17
                continue
            # 6% empty seats so the grid isn't perfectly military
            if rng.random() < 0.06:
                x += spacing
                continue
            # skip GO JMHS banner zone in the lowest kept row
            if row >= 6 and 440 <= x <= 520:
                x += spacing
                continue
            # flag cloth waves to the right of the pole — leave a wide gap
            if row >= 4 and any(fx - 2 <= x <= fx + 26 for fx in (80, 200, 320, 640, 760, 880)):
                x += spacing
                continue
            seed = rng.randint(0, 10_000)
            group = "ABCD"[seed % 4]
            skin = seed % len(SKINS)
            hair = (seed // 3) % len(HAIRS)
            # band block: left-center home section
            in_band = 150 <= x <= 305 and row >= 1
            in_guard = 650 <= x <= 720 and row >= 4
            roll = rng.random()
            if in_band:
                if roll < 0.07 and row >= 4:
                    kind = "sousa"
                elif roll < 0.22:
                    kind = "brass"
                elif roll < 0.30 and row >= 3:
                    kind = "drum"
                else:
                    kind = "band"
                text = ""
            elif in_guard:
                kind = "guard" if roll < 0.40 else "civ"
                text = ""
            elif roll < 0.07 and 150 <= x <= 400:
                kind = "band"  # stray band kids
                text = ""
            else:
                kind = "civ"
                text = ""
            people.append({
                "row": row, "x": x, "kind": kind, "group": group,
                "skin": skin, "hair": hair, "body": seed % len(CIV_BODIES),
                "front": front, "seed": seed, "text": text,
                "foam": front and roll > 0.92,
                "plume": P["gold_lt"] if seed % 3 else P["white"],
            })
            x += spacing
    # Curated short signs with a cleared neighborhood so letters stay readable
    signs = [
        (4, 116, "GO"),
        (5, 360, "GO"),
        (4, 424, "50"),
        (5, 552, "GO"),
        (4, 700, "J"),
        (5, 804, "50"),
        (3, 268, "J"),
        (4, 900, "GO"),
    ]
    for row, sx, text in signs:
        people = [pe for pe in people if not (pe["row"] == row and abs(pe["x"] - sx) < 18)]
        seed = 1000 + sx + row
        people.append({
            "row": row, "x": sx, "kind": "sign", "group": "ABCD"[seed % 4],
            "skin": seed % len(SKINS), "hair": (seed // 3) % len(HAIRS),
            "body": seed % len(CIV_BODIES), "front": True, "seed": seed,
            "text": text, "foam": False, "plume": P["gold_lt"],
        })
    return people


CROWD = None  # filled lazily so import is side-effect free... we just build in main


def draw_crowd(cv: CV, frame: int, people):
    # back rows first
    for pe in people:
        x, row = pe["x"], pe["row"]
        y = seat_y(row)
        bob = _bob(pe["group"], frame)
        arm = _arm(pe["group"], frame)
        # stagger arm so the whole stand isn't in lockstep
        if pe["seed"] % 5 == 0:
            arm = _arm("ABCD"[(pe["seed"] // 5) % 4], frame)
        skin = SKINS[pe["skin"]]
        hair = HAIRS[pe["hair"]]
        body, body2 = CIV_BODIES[pe["body"]]
        kind = pe["kind"]
        if kind == "band":
            _band(cv, x, y, skin, hair, bob, arm, front=pe["front"], plume=pe["plume"], brass=False)
        elif kind == "brass":
            _band(cv, x, y, skin, hair, bob, arm, front=pe["front"], plume=pe["plume"], brass=True)
        elif kind == "sousa":
            _sousa(cv, x, y, skin, hair, bob)
        elif kind == "drum":
            _drummer(cv, x, y, skin, hair, bob)
        elif kind == "guard":
            _guard(cv, x, y, skin, hair, bob, arm, front=pe["front"])
        elif kind == "sign":
            _sign(cv, x, y, pe["text"] or "GO", bob, arm, skin, hair, body)
        else:
            _civ(cv, x, y, skin, hair, body, body2, bob, arm, front=pe["front"], foam=pe["foam"])
        # Front-row people may only peek over the fascia (keep bunting clean)
        if row >= 7:
            fascia = BLEACH_BOT - 12  # 274
            for yy in range(fascia, BLEACH_BOT + 10):
                for xx in range(x - 4, x + 16):
                    cv.clear_px(xx, yy)


def draw_flag(cv, pole_x, pole_y, frame, kind="school"):
    # 8-frame smoother wave
    phase = frame % 8
    w, h = (22, 13) if kind == "school" else (18, 11)
    for fy in range(h):
        # traveling sine, quantized
        wave = int(round(1.6 * math.sin((fy * 0.55) + phase * 0.85)))
        for fx in range(w):
            # slight delay along the fly
            ox = wave + int(round(0.7 * math.sin((fx * 0.4) + phase * 0.7)))
            px, py = pole_x + 2 + fx + ox, pole_y + fy
            if kind == "school":
                col = P["navy"]
                if fx < 2:
                    col = P["white"]
                elif fy < 1 or fy == h - 1 or fx >= w - 1:
                    col = P["gold"]
                elif 7 <= fx <= 10 and 3 <= fy <= 9:
                    col = P["gold"]
                elif 6 <= fx <= 11 and fy in (5, 7):
                    col = P["gold_lt"]
                elif abs((fx - 9) ) + abs((fy - 6)) <= 1:
                    col = P["gold_lt"]
                cv.p(px, py, col)
            else:
                col = P["gold"]
                if fy < 1 or fy == h - 1:
                    col = P["gold_lt"]
                if fx < 2:
                    col = P["navy_lt"]
                elif 3 <= fy <= 7 and 4 <= fx <= 13:
                    col = P["navy"]
                elif fx > w - 3:
                    col = P["white"]
                if fy == 5 and 6 <= fx <= 11:
                    col = P["gold_lt"]
                cv.p(px, py, col)
    cv.p(pole_x + 1, pole_y, P["gold"])


def _lamp_flicker(cv, cx, top, cols, rows, tilt, pattern):
    lamp_w, lamp_h, gap, pad = 6, 5, 2, 4
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
                cv.rect(lx, ly, lamp_w, lamp_h, P["lamp_off"])
                cv.rect(lx + 1, ly + 1, lamp_w - 2, lamp_h - 2, P["lamp4"])
            elif state == 2:
                cv.rect(lx, ly, lamp_w, lamp_h, P["lamp1"])
                cv.rect(lx + 1, ly, lamp_w - 2, lamp_h - 2, P["lamp0"])
                cv.p(lx + 2, ly, P["flash"])
    # pulse the halo a little (only on clear pixels, plus a tight extra ring)
    avg = sum(pattern) / len(pattern)
    extra = 8 if avg >= 1.15 else 0
    if extra:
        _dithered_halo(cv, cx, y0 + bh // 2, 46 + extra, only_clear=True)
    return x0, y0, bw, bh


def _pattern_for(frame, tower_i, n_lamps):
    rng = random.Random(1000 + tower_i)
    base = [1] * n_lamps
    # a slow pulse of "hot" lamps plus 1-2 dim ones that wander
    hot = (frame + tower_i * 2) % n_lamps
    base[hot] = 2
    base[(hot + 3) % n_lamps] = 2
    dim = (frame * 3 + tower_i * 5) % n_lamps
    if frame % 3 != 1:
        base[dim] = 0
    if frame % 5 == 4:
        base[(dim + 2) % n_lamps] = 0
    return base


def draw_anim(frame: int, people) -> CV:
    cv = CV(MID_W, MID_H, bg=None)
    # flicker + pulsing halo
    for i, (cx, top, cols, rows, tilt) in enumerate(TOWERS):
        pat = _pattern_for(frame, i, cols * rows)
        _lamp_flicker(cv, cx, top, cols, rows, tilt, pat)
        # modest shaft on every tower; extra pulse on alternating frames
        lamp_h, gap, pad = 5, 2, 4
        bh = rows * (lamp_h + gap) - gap + pad * 2
        _dithered_beam(cv, cx, top + bh, 280, 5, 20, only_clear=True, phase=frame * 3 + cx)
        if frame % 2 == i % 2:
            _dithered_beam(cv, cx, top + bh, 286, 6, 24, only_clear=True, phase=frame * 5 + cx + 4)

    # scoreboard lamps + colon blink
    bx, by, bw, bh = 384, 24, 192, 74
    for i, lx in enumerate(range(bx + 8, bx + bw - 6, 7)):
        on = (i + frame) % 3 != 0
        cv.rect(lx, by + 2, 4, 2, P["lamp0"] if on else P["lamp_off"])
    if frame % 2 == 1:
        colon_x = bx + 10 + 5 * 6  # "4TH 0:00" — colon is glyph index 5
        colon_y = by + bh - 14
        cv.rect(colon_x, colon_y, 5, 7, P["navy_dk"])

    # press-box beacon
    ax = 360 + 240 - 18
    py = 100
    if frame in (2, 3, 6, 7):
        cv.p(ax, py - 31, P["beacon_dk"])
        cv.p(ax + 1, py - 31, P["beacon_dk"])
        cv.p(ax, py - 32, P["steel5"])
    else:
        cv.p(ax, py - 31, P["flash"])
        cv.p(ax + 1, py - 31, P["beacon2"])
        cv.p(ax, py - 32, P["flash"])
        cv.p(ax - 1, py - 31, P["beacon"])
        cv.p(ax + 2, py - 31, P["beacon"])

    draw_crowd(cv, frame, people)

    # flags in aisles, drawn after the crowd so cloth sits in front
    flag_specs = [
        (80, 246, "school"),
        (200, 246, "guard"),
        (320, 246, "school"),
        (640, 246, "school"),
        (760, 246, "guard"),
        (880, 246, "school"),
    ]
    for i, (fx, fy, kind) in enumerate(flag_specs):
        draw_flag(cv, fx, fy, (frame + i * 2) % 8, kind=kind)

    # standing drum major on the podium + two color guard on the track (y<=299)
    y = 298
    b = _bob("A", frame)
    yy = y + b
    # drum major
    cv.p(310, yy - 28, P["gold_lt"])
    cv.p(310, yy - 27, P["gold_lt"])
    cv.rect(307, yy - 26, 7, 6, P["navy"])
    cv.hline(307, 313, yy - 22, P["gold"])
    cv.p(310, yy - 24, P["gold_lt"])
    cv.rect(308, yy - 20, 5, 4, SKINS[0][1])
    cv.p(308, yy - 20, P["hair"])
    cv.p(309, yy - 18, SKINS[0][0])
    cv.rect(307, yy - 16, 7, 10, P["navy"])
    cv.vline(310, yy - 16, yy - 8, P["white"])
    cv.p(310, yy - 12, P["gold"])
    cv.rect(307, yy - 6, 3, 6, P["navy_dk"])
    cv.rect(311, yy - 6, 3, 6, P["navy_dk"])
    cv.p(307, yy, P["shoe"])
    cv.p(313, yy, P["shoe"])
    # mace
    mx = 315
    cv.vline(mx, yy - 34, yy - 14, P["gold"])
    cv.rect(mx - 2, yy - 33, 5, 5, P["gold_lt"])
    cv.p(mx, yy - 35, P["flash"])

    for gx, group, si in ((368, "B", 2), (612, "C", 1)):
        yy = 298 + _bob(group, frame)
        skin = SKINS[si]
        cv.rect(gx + 1, yy - 20, 4, 3, HAIRS[si])
        cv.rect(gx + 1, yy - 18, 4, 4, skin[1])
        cv.p(gx + 1, yy - 17, skin[0])
        cv.rect(gx, yy - 14, 6, 8, P["navy"])
        cv.hline(gx, gx + 5, yy - 11, P["gold"])
        cv.rect(gx, yy - 6, 2, 6, P["navy_dk"])
        cv.rect(gx + 4, yy - 6, 2, 6, P["navy_dk"])
        cv.p(gx, yy, P["shoe"])
        cv.p(gx + 5, yy, P["shoe"])
        # small held flag to the OUTSIDE of the guard, cloth above the track
        hx = gx + 8
        hy = 270
        phase = (frame + si * 3) % 8
        for fy in range(7):
            ox = int(round(math.sin(fy * 0.7 + phase * 0.8)))
            for fx in range(9):
                col = P["gold"]
                if fx < 2:
                    col = P["navy"]
                elif fy in (0, 6) or fx >= 8:
                    col = P["gold_lt"]
                elif 2 <= fy <= 4 and 3 <= fx <= 6:
                    col = P["navy_lt"]
                cv.p(hx + 1 + fx + ox, hy + fy, col)
        cv.vline(hx, hy, yy - 8, P["white_dk"])
        cv.p(hx, hy, P["gold"])

    # phone / glow-stick twinkles
    twinkles = [
        (410, seat_y(4) - 12, 0), (500, seat_y(6) - 14, 2),
        (670, seat_y(5) - 13, 4), (170, seat_y(6) - 12, 6),
        (820, seat_y(5) - 11, 1), (540, seat_y(5) - 12, 5),
        (260, seat_y(3) - 12, 3), (730, seat_y(4) - 11, 7),
    ]
    for x, y, ph in twinkles:
        if frame % 8 == ph or (frame + 1) % 8 == ph:
            cv.p(x, y, P["flash"])
            cv.p(x + 1, y, P["lamp2"])
    return cv


# ---------------------------------------------------------------------------
# NEAR — 1120x360, in front of fighters. Edge props only.
# ---------------------------------------------------------------------------
def _railing_segment(cv, x0, x1, y_rail=332):
    """Foreground steel railing along the sideline edge."""
    # posts
    for x in range(x0 + 4, x1, 16):
        cv.rect(x, y_rail - 18, 3, 28, P["rail0"])
        cv.vline(x, y_rail - 18, y_rail + 9, P["cam0"])
        cv.vline(x + 2, y_rail - 18, y_rail + 9, P["rail1"])
        cv.p(x + 1, y_rail - 18, P["rail2"])
    # two rails
    for y, hi, lo in ((y_rail - 16, P["rail2"], P["rail0"]), (y_rail - 4, P["rail1"], P["rail0"])):
        cv.rect(x0, y, x1 - x0, 3, lo)
        cv.hline(x0, x1 - 1, y, hi)
        cv.hline(x0, x1 - 1, y + 2, P["cam0"])
    # foot plate
    cv.rect(x0, y_rail + 8, x1 - x0, 3, P["steel1"])
    cv.hline(x0, x1 - 1, y_rail + 8, P["steel3"])


def _camera_rig(cv, x, y_foot):
    """Sideline camcorder on a tripod. y_foot is the ground contact."""
    # legs
    # left, mid, right
    for dx, ytop in ((-10, y_foot - 40), (0, y_foot - 44), (10, y_foot - 40)):
        x0, x1 = x, x + dx
        y0, y1 = ytop, y_foot
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(steps + 1):
            t = i / max(1, steps)
            px = int(round(x0 + (x1 - x0) * t))
            py = int(round(y0 + (y1 - y0) * t))
            cv.p(px, py, P["cam0"])
            cv.p(px + 1, py, P["cam1"])
    # feet
    for dx in (-11, 0, 11):
        cv.rect(x + dx - 2, y_foot - 1, 5, 2, P["cam0"])
        cv.p(x + dx, y_foot - 2, P["cam2"])
    # head / pan
    cv.rect(x - 5, y_foot - 52, 11, 10, P["cam1"])
    cv.frame(x - 5, y_foot - 52, 11, 10, P["cam0"])
    cv.hline(x - 5, x + 5, y_foot - 52, P["cam3"])
    # camera body
    cv.rect(x - 8, y_foot - 64, 18, 14, P["cam1"])
    cv.frame(x - 8, y_foot - 64, 18, 14, P["cam0"])
    cv.rect(x - 6, y_foot - 62, 8, 6, P["cam2"])
    # lens
    cv.rect(x + 9, y_foot - 60, 8, 7, P["cam0"])
    cv.rect(x + 11, y_foot - 58, 5, 4, P["c_black"])
    cv.p(x + 13, y_foot - 57, P["steel5"])
    # rec light
    cv.p(x - 6, y_foot - 62, P["beacon"])
    cv.p(x - 5, y_foot - 62, P["beacon2"])
    # viewfinder
    cv.rect(x - 10, y_foot - 60, 3, 4, P["cam0"])
    # cable
    for i, (dx, dy) in enumerate(((0, 0), (1, 2), (2, 4), (2, 7), (3, 10))):
        cv.p(x - 4 + dx, y_foot - 50 + dy, P["cam0"])


def _cooler(cv, x, y_foot, palette="orange"):
    if palette == "orange":
        a, b, c, lid, sh = P["cool0"], P["cool1"], P["cool2"], P["cool3"], P["cool4"]
    else:
        a, b, c, lid, sh = P["navy_dk"], P["navy"], P["navy_lt"], P["white"], P["gold"]
    w, h = 22, 20
    y = y_foot - h
    cv.rect(x, y, w, h, a)
    cv.rect(x + 1, y + 2, w - 2, h - 5, b)
    cv.rect(x + 2, y + 4, 6, 8, c)  # highlight face
    cv.rect(x, y, w, 4, lid)
    cv.hline(x, x + w - 1, y, P["white"])
    cv.hline(x, x + w - 1, y + 3, sh)
    # handle
    cv.rect(x + 6, y - 4, 10, 4, P["steel3"])
    cv.hline(x + 6, x + 15, y - 4, P["steel5"])
    cv.vline(x + 6, y - 4, y, P["steel1"])
    cv.vline(x + 15, y - 4, y, P["steel1"])
    # spigot
    cv.rect(x + w, y + 10, 4, 3, P["steel4"])
    cv.p(x + w + 3, y + 13, P["steel2"])
    # shadow / feet
    cv.rect(x + 1, y_foot - 2, 6, 2, sh)
    cv.rect(x + w - 7, y_foot - 2, 6, 2, sh)
    # stripe (generic, no logo)
    cv.rect(x + 1, y + 12, w - 2, 3, lid if palette == "orange" else P["gold"])


def _pompoms(cv, x, y_foot):
    # two pom clusters sitting on the ground, navy + gold
    rng = random.Random(x + 11)
    for i, (ox, col, col2) in enumerate(((0, P["navy"], P["navy_lt"]), (13, P["gold"], P["gold_lt"]))):
        cx, cy = x + ox + 6, y_foot - 9
        for dy in range(-9, 4):
            w = 6 - abs(dy) // 2
            for dx in range(-w, w + 1):
                if dx * dx + dy * dy * 2 <= 46 and rng.random() < 0.9:
                    cv.p(cx + dx, cy + dy, col if rng.random() < 0.6 else col2)
        cv.rect(cx - 1, y_foot - 5, 3, 5, P["white_dk"])
        cv.p(cx, y_foot, P["wood_dk"])


def _bass_drum(cv, x, y_foot):
    """Navy bass drum on a hardware stand, white head, gold hoops."""
    cx, cy, rx, ry = x + 16, y_foot - 28, 16, 18
    # stand
    cv.vline(cx - 10, cy + 4, y_foot, P["steel1"])
    cv.vline(cx + 10, cy + 4, y_foot, P["steel1"])
    cv.vline(cx - 9, cy + 4, y_foot, P["steel4"])
    cv.vline(cx + 11, cy + 4, y_foot, P["steel4"])
    cv.rect(cx - 14, y_foot - 2, 8, 3, P["steel0"])
    cv.rect(cx + 8, y_foot - 2, 8, 3, P["steel0"])
    cv.hline(cx - 10, cx + 11, cy + 8, P["steel2"])
    # shell (side view-ish, slightly 3/4)
    cv.fill_ellipse(cx, cy, rx, ry, P["navy"])
    cv.fill_ellipse(cx - 1, cy - 1, rx - 3, ry - 3, P["navy_lt"])
    # hoops
    for a in range(360):
        pass  # use outline by ellipse subtraction feel
    # hoop as a thick ellipse frame
    for y in range(cy - ry - 1, cy + ry + 2):
        for xx in range(cx - rx - 1, cx + rx + 2):
            # distance from ellipse
            if rx and ry:
                v = ((xx - cx) ** 2) / (rx * rx) + ((y - cy) ** 2) / (ry * ry)
                if 0.86 <= v <= 1.08:
                    cv.p(xx, y, P["gold"] if v < 1.0 else P["gold_dk"])
    # head (slightly inset, lit)
    cv.fill_ellipse(cx - 1, cy - 1, rx - 5, ry - 5, P["white"])
    cv.fill_ellipse(cx - 3, cy - 3, 5, 4, P["white_sh"])  # shade
    cv.p(cx - 6, cy - 6, P["white"])
    # tiny JMHS word (generic, school-appropriate) on the head — only if it fits
    tw = text_width("J", scale=1, spacing=0)
    draw_text(cv, cx - 2, cy - 3, "J", P["navy"], scale=1, spacing=0)
    # lugs
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        lx = cx + int((rx - 2) * math.cos(rad))
        ly = cy + int((ry - 2) * math.sin(rad))
        cv.p(lx, ly, P["gold_lt"])
    # sticks resting on top
    cv.hline(cx + 6, cx + 20, cy - ry - 1, P["wood_lt"])
    cv.hline(cx + 6, cx + 20, cy - ry, P["wood"])
    cv.p(cx + 20, cy - ry, P["white"])


def draw_near() -> CV:
    """Foreground parallax. Transparent in the action well; props only at edges."""
    cv = CV(NEAR_W, NEAR_H, bg=None)
    # Safe action well in near space: x=280..840, y=200..360 must stay clear
    # Visible edge peeks: x=240-280 and 840-880. Margins: 0-240 and 880-1120.

    # LEFT side (margin + 40px peek)
    _railing_segment(cv, 0, 272, y_rail=334)
    _camera_rig(cv, 78, 354)
    _cooler(cv, 128, 350, palette="orange")
    _pompoms(cv, 168, 350)
    # a second smaller cooler tucked behind the camera, navy/gold
    _cooler(cv, 24, 350, palette="navy")

    # RIGHT side
    _railing_segment(cv, 848, NEAR_W, y_rail=334)
    _bass_drum(cv, 1048, 354)
    _cooler(cv, 980, 350, palette="navy")
    _pompoms(cv, 944, 350)
    # a second camera further into the right margin
    _camera_rig(cv, 1088, 354)

    # Thin additional posts just inside the visible edges so the peek reads
    for x in (252, 264, 856, 868):
        cv.rect(x, 316, 3, 28, P["rail0"])
        cv.vline(x, 316, 343, P["cam0"])
        cv.vline(x + 2, 316, 343, P["rail1"])
        cv.p(x + 1, 316, P["rail2"])
    # short rail cap at the visible ends (the "railing ends")
    cv.rect(248, 316, 28, 3, P["rail0"])
    cv.hline(248, 275, 316, P["rail2"])
    cv.rect(848, 316, 28, 3, P["rail0"])
    cv.hline(848, 875, 316, P["rail2"])
    return cv


# ---------------------------------------------------------------------------
# Composite + IO
# ---------------------------------------------------------------------------
def composite_preview(far: CV, mid: CV, anim: CV, near: CV) -> Image.Image:
    out = Image.new("RGBA", (VIEW_W, VIEW_H), (0, 0, 0, 255))
    out.paste(far.im.convert("RGBA"), (0, 0))
    mid_crop = mid.im.crop((MID_OFFSET, 0, MID_OFFSET + VIEW_W, VIEW_H))
    out.alpha_composite(mid_crop)
    anim_crop = anim.im.crop((MID_OFFSET, 0, MID_OFFSET + VIEW_W, VIEW_H))
    out.alpha_composite(anim_crop)
    near_crop = near.im.crop((NEAR_OFFSET, 0, NEAR_OFFSET + VIEW_W, VIEW_H))
    out.alpha_composite(near_crop)
    bg = Image.new("RGB", (VIEW_W, VIEW_H), (0, 0, 0))
    bg.paste(out, mask=out.split()[3])
    return bg


def unique_rgb(im: Image.Image) -> int:
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return len({(r, g, b, a) for r, g, b, a in im.getdata() if a != 0})


def assert_qa(far, mid, anims, near, preview, preview2x):
    problems = []
    if far.im.size != (VIEW_W, VIEW_H):
        problems.append(f"far size {far.im.size}")
    far_rgba = far.im.convert("RGBA")
    alphas = {a for (*_, a) in far_rgba.getdata()}
    if alphas != {255}:
        problems.append(f"far alpha values {alphas}")
    if mid.im.size != (MID_W, MID_H):
        problems.append(f"mid size {mid.im.size}")
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
        al = {px[3] for px in a.im.getdata()}
        if not al <= {0, 255}:
            problems.append(f"anim_{i} partial alpha {al}")
    if near.im.size != (NEAR_W, NEAR_H):
        problems.append(f"near size {near.im.size}")
    # action-well transparency: x=280..839, y=200..359 must be clear
    npx = near.im.load()
    hits = 0
    sample = None
    for y in range(200, NEAR_H):
        for x in range(280, 840):
            if npx[x, y][3] != 0:
                hits += 1
                if sample is None:
                    sample = (x, y, npx[x, y])
    if hits:
        problems.append(f"near action-well has {hits} opaque px, first at {sample}")
    nal = {px[3] for px in near.im.getdata()}
    if not nal <= {0, 255}:
        problems.append(f"near partial alpha {nal}")
    if preview.size != (VIEW_W, VIEW_H):
        problems.append(f"preview size {preview.size}")
    if preview2x.size != (VIEW_W * 2, VIEW_H * 2):
        problems.append(f"preview@2x size {preview2x.size}")
    if problems:
        raise SystemError("QA failed:\n  " + "\n  ".join(problems))


def save_rgb_opaque(im: Image.Image, path: Path):
    if im.mode == "RGB":
        im.save(path)
        return im
    rgb = Image.new("RGB", im.size, (0, 0, 0))
    rgba = im.convert("RGBA")
    rgb.paste(rgba, mask=rgba.split()[3])
    rgb.save(path)
    return rgb


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    people = layout_crowd()
    print(f"Crowd sprites: {len(people)}")
    far = draw_far()
    mid = draw_mid()
    print("mid done")
    anims = []
    for i in range(ANIM_FRAMES):
        anims.append(draw_anim(i, people))
        print(f"anim_{i} done")
    near = draw_near()
    print("near done")

    far.im = save_rgb_opaque(far.im, OUT / "far.png")
    mid.im.save(OUT / "mid.png")
    for i, a in enumerate(anims):
        a.im.save(OUT / f"anim_{i}.png")
    # delete stale frames beyond 7
    for stale in OUT.glob("anim_*.png"):
        try:
            n = int(stale.stem.split("_")[1])
        except ValueError:
            continue
        if n >= ANIM_FRAMES or n < 0:
            stale.unlink()
            print(f"deleted stale {stale.name}")
    near.im.save(OUT / "near.png")

    preview = composite_preview(far, mid, anims[0], near)
    preview.save(OUT / "preview.png")
    preview2x = preview.resize((VIEW_W * 2, VIEW_H * 2), Image.Resampling.NEAREST)
    preview2x.save(OUT / "preview@2x.png")
    preview4x = preview.resize((VIEW_W * 4, VIEW_H * 4), Image.Resampling.NEAREST)
    preview4x.save("/tmp/qa_preview@4x.png")

    assert_qa(far, mid, anims, near, preview, preview2x)

    files = [
        ("far.png", far.im),
        ("mid.png", mid.im),
        *[ (f"anim_{i}.png", anims[i].im) for i in range(ANIM_FRAMES) ],
        ("near.png", near.im),
        ("preview.png", preview),
        ("preview@2x.png", preview2x),
    ]
    print("Wrote:")
    for name, im in files:
        w, h = im.size
        cols = unique_rgb(im if im.mode == "RGBA" else im.convert("RGBA"))
        print(f"  {name:16s} {w}x{h}  {im.mode:4s}  {cols:4d} colors")
    print(f"Floor line y={FLOOR_Y}; floor band y={FLOOR_TOP}..{MID_H - 1}")
    print(f"Mid origin x={-MID_OFFSET}; near origin x={-NEAR_OFFSET}")


if __name__ == "__main__":
    main()
