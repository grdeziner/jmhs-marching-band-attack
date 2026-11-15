"""16-bit (SNES / SF2 Turbo) character art pipeline.

Reusable part templates, faceted (non-capsule) anatomy, 15-color ramps,
selective outlines, and pose-specific cloth folds. Palettes stay at or
under 15 opaque colors plus transparent.
"""

from .palette import PAL, RAMPS, hex_of, nearest, enforce, count_opaque
from .draw import (
    fill_poly,
    fill_ellipse,
    shade_limb,
    shade_volume,
    crease,
    specular,
    selective_outline,
    stamp,
    line,
)
