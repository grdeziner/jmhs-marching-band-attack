"""Shared Band Wars palettes. School colors are navy + gold with white trim."""

from __future__ import annotations

from typing import Iterable, Tuple

Color = Tuple[int, int, int, int]


def rgba(hex_color: str, a: int = 255) -> Color:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, a)


class Palette(dict):
    """Named color map that also tracks insertion order for the hex list."""

    def add(self, name: str, hex_color: str) -> Color:
        c = rgba(hex_color)
        self[name] = c
        return c

    def hex_list(self) -> list[str]:
        seen = []
        dumped = set()
        for _name, col in self.items():
            hx = "#{:02X}{:02X}{:02X}".format(col[0], col[1], col[2])
            if hx not in dumped:
                dumped.add(hx)
                seen.append(hx)
        return seen


def _build_uniform() -> Palette:
    p = Palette()
    # Outline / deep shadow (used for all 1px outlines)
    p.add("outline", "#0A0B10")
    # Navy cloth (jacket, pants, shako body, drum shell)
    p.add("navy_dk", "#0C1734")
    p.add("navy", "#17305F")
    p.add("navy_lt", "#3A5A9C")
    # Gold metal / braid / plume / hoops
    p.add("gold_dk", "#7A5410")
    p.add("gold", "#D4A017")
    p.add("gold_lt", "#F5DE6A")
    # White trim, gloves, baldric, drum head
    p.add("white", "#F6F2EA")
    p.add("white_sh", "#B9B3A6")
    p.add("white_dk", "#8B8578")
    # Skin (warm medium tone, 3 shades)
    p.add("skin_dk", "#8E4E2C")
    p.add("skin", "#E09A68")
    p.add("skin_lt", "#F5C49A")
    # Hair / brows
    p.add("hair", "#1A1210")
    # Wood (mallet shafts, maybe other instruments later)
    p.add("wood_dk", "#5A3016")
    p.add("wood", "#A05A28")
    p.add("wood_lt", "#C47A44")
    # Shoes
    p.add("shoe", "#141418")
    p.add("shoe_lt", "#3A3A42")
    # Drum head (slightly warmer than glove white)
    p.add("head", "#EDE6D2")
    p.add("head_sh", "#C4B99A")
    p.add("head_dk", "#8F866C")
    # Mouth / blush
    p.add("mouth", "#8A3040")
    p.add("blush", "#D07058")
    # Extra accent used sparingly (impact flashes share gold_lt / white)
    p.add("flash", "#FFF6C8")
    return p


UNIFORM = _build_uniform()


def hex_list(colors: Iterable[Tuple[int, int, int, int]]) -> list[str]:
    seen = []
    dumped = set()
    for col in colors:
        if col is None or col[3] == 0:
            continue
        hx = "#{:02X}{:02X}{:02X}".format(col[0], col[1], col[2])
        if hx not in dumped:
            dumped.add(hx)
            seen.append(hx)
    return seen


# Convenience aliases used by body parts
OUTLINE = UNIFORM["outline"]
NAVY_DK = UNIFORM["navy_dk"]
NAVY = UNIFORM["navy"]
NAVY_LT = UNIFORM["navy_lt"]
GOLD_DK = UNIFORM["gold_dk"]
GOLD = UNIFORM["gold"]
GOLD_LT = UNIFORM["gold_lt"]
WHITE = UNIFORM["white"]
WHITE_SH = UNIFORM["white_sh"]
WHITE_DK = UNIFORM["white_dk"]
SKIN_DK = UNIFORM["skin_dk"]
SKIN = UNIFORM["skin"]
SKIN_LT = UNIFORM["skin_lt"]
HAIR = UNIFORM["hair"]
WOOD_DK = UNIFORM["wood_dk"]
WOOD = UNIFORM["wood"]
WOOD_LT = UNIFORM["wood_lt"]
SHOE = UNIFORM["shoe"]
SHOE_LT = UNIFORM["shoe_lt"]
DHEAD = UNIFORM["head"]
DHEAD_SH = UNIFORM["head_sh"]
DHEAD_DK = UNIFORM["head_dk"]
MOUTH = UNIFORM["mouth"]
BLUSH = UNIFORM["blush"]
FLASH = UNIFORM["flash"]


def shade(color: Color, factor: float) -> Color:
    """factor < 1 darkens, > 1 lightens toward white."""
    r, g, b, a = color if len(color) == 4 else (*color, 255)
    if factor >= 1.0:
        t = factor - 1.0
        return (
            int(min(255, r + (255 - r) * t)),
            int(min(255, g + (255 - g) * t)),
            int(min(255, b + (255 - b) * t)),
            a,
        )
    return (int(r * factor), int(g * factor), int(b * factor), a)


# Silver / nickel (flute body, flag hardware, xylophone frame)
SILVER_DK = rgba("#5A6574")
SILVER = rgba("#A8B4C4")
SILVER_LT = rgba("#E2E8F0")
