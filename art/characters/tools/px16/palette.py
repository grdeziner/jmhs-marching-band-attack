"""15-color SNES-style palette for the 16-bit Band Wars fighters.

Ramps are 3–4 steps, light to shadow. No color outside this set may appear
on a character sheet (transparent is extra and not counted).
"""

from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple

Color = Tuple[int, int, int, int]


def C(r, g, b) -> Color:
    return (int(r), int(g), int(b), 255)


# --- navy cloth (4) --------------------------------------------------------
N1 = C(74, 106, 181)     # lit fold
N2 = C(40, 68, 140)      # mid
N3 = C(22, 40, 84)       # shadow
N4 = C(12, 20, 44)       # deep / cloth outline

# --- gold / brass (4): specular, mid, shadow, dark core --------------------
G1 = C(255, 241, 160)    # specular highlight
G2 = C(212, 160, 24)     # mid brass
G3 = C(150, 96, 16)      # shadow
G4 = C(80, 52, 10)       # dark core / gold outline

# --- skin (3) --------------------------------------------------------------
S1 = C(243, 201, 160)
S2 = C(196, 138, 88)
S3 = C(122, 74, 40)      # also light wood / skin outline

# --- white: gloves, drum head, belt (3) ------------------------------------
W1 = C(255, 251, 240)
W2 = C(200, 192, 176)
W3 = C(122, 114, 104)    # also leather sheen, white outline

# --- utility near-black (1): hair, shoes, pupils, rare deep outline --------
K = C(16, 14, 20)

PAL: Tuple[Color, ...] = (
    N1, N2, N3, N4,
    G1, G2, G3, G4,
    S1, S2, S3,
    W1, W2, W3,
    K,
)

assert len(PAL) == 15
assert len(set(PAL)) == 15

RAMPS = {
    "navy": (N1, N2, N3, N4),
    "gold": (G1, G2, G3, G4),
    "skin": (S1, S2, S3),
    "white": (W1, W2, W3),
    "wood": (S2, S3, G4),       # tan / brown / dark core (shares skin + gold)
    "shoe": (W3, N4, K),
    "hair": (N4, K),
}


def hex_of(c: Color) -> str:
    return f"#{c[0]:02X}{c[1]:02X}{c[2]:02X}"


def hex_list(colors: Iterable[Color] = PAL) -> list:
    return [hex_of(c) for c in colors]


def nearest(c: Sequence[int], pal: Sequence[Color] = PAL) -> Color:
    best, best_d = pal[0], 10**9
    r, g, b = c[0], c[1], c[2]
    for p in pal:
        d = (r - p[0]) ** 2 + (g - p[1]) ** 2 + (b - p[2]) ** 2
        if d < best_d:
            best, best_d = p, d
    return best


def enforce(canvas, pal: Sequence[Color] = PAL) -> int:
    """Remap every opaque pixel to the palette. Returns unique opaque count."""
    seen = {}
    for y in range(canvas.h):
        row = canvas.px[y]
        for x in range(canvas.w):
            c = row[x]
            if c is None or c[3] == 0:
                continue
            if c not in pal:
                c = nearest(c, pal)
                row[x] = c
            seen[c] = True
    return len(seen)


def count_opaque(canvas, pal: Sequence[Color] = PAL) -> int:
    seen = set()
    for y in range(canvas.h):
        for x in range(canvas.w):
            c = canvas.px[y][x]
            if c is not None and c[3]:
                seen.add(c if c in pal else nearest(c, pal))
    return len(seen)
