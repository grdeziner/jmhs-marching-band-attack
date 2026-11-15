"""Roster-faithful Look presets (skin, hair, plume, body type)."""

from .body import Look
from .palette import rgba, shade

def _skin(mid_hex, dk_hex=None, lt_hex=None):
    mid = rgba(mid_hex)
    dk = rgba(dk_hex) if dk_hex else shade(mid, 0.62)
    lt = rgba(lt_hex) if lt_hex else shade(mid, 1.35)
    return mid, dk, lt

def _plume(mid_hex):
    mid = rgba(mid_hex)
    return mid, shade(mid, 1.4), shade(mid, 0.55)

def _hair(mid_hex):
    return rgba(mid_hex)


def penny():
    """Penny 'Mallets' Okafor — slim, warm skin, red hair, coral plume."""
    s, sd, sl = _skin("#F1C27D", "#C48A4A", "#F8D9A8")
    p, pl, pd = _plume("#FF595E")
    return Look(skin=s, skin_dk=sd, skin_lt=sl, hair=_hair("#D1495B"),
                plume=p, plume_lt=pl, plume_dk=pd,
                limb=0.72, torso=0.78, shoe=0.82, head=0.94, glove=0.85,
                jaw=0.88, neck=0.82, female=True, hat="shako",
                hair_style="temples", sleeves=True, gloves=True, shoes="marching")


def skye():
    """Skye 'Silver Stick' Lin — lean, light skin, blonde hair, cyan plume."""
    s, sd, sl = _skin("#FFDBAC", "#E0A878", "#FFE8C8")
    p, pl, pd = _plume("#7EF9FF")
    return Look(skin=s, skin_dk=sd, skin_lt=sl, hair=_hair("#E9C46A"),
                plume=p, plume_lt=pl, plume_dk=pd,
                limb=0.66, torso=0.70, shoe=0.78, head=0.92, glove=0.82,
                jaw=0.84, neck=0.78, female=True, hat="shako",
                hair_style="temples", sleeves=True, gloves=True, shoes="marching")


def gus():
    """Gus 'Sousa-Mountain' Romero — huge, tan skin, dark hair, white plume."""
    s, sd, sl = _skin("#A16E4B", "#6E442C", "#C4926A")
    p, pl, pd = _plume("#FFFFFF")
    return Look(skin=s, skin_dk=sd, skin_lt=sl, hair=_hair("#222222"),
                plume=p, plume_lt=pl, plume_dk=pd,
                limb=1.22, torso=1.28, shoe=1.18, head=1.08, glove=1.12,
                jaw=1.16, neck=1.18, female=False, hat="shako",
                hair_style="temples", sleeves=True, gloves=True, shoes="marching")


def jade():
    """Jade 'Banner' Castillo — acrobatic color guard, hair up, no shako."""
    s, sd, sl = _skin("#F1C27D", "#C48A4A", "#F8D9A8")
    p, pl, pd = _plume("#FF006E")  # used as flag accent, not a hat plume
    return Look(skin=s, skin_dk=sd, skin_lt=sl, hair=_hair("#6A040F"),
                plume=p, plume_lt=pl, plume_dk=pd,
                limb=0.70, torso=0.74, shoe=0.76, head=0.92, glove=0.80,
                jaw=0.82, neck=0.80, female=True, hat="none",
                hair_style="bun", sleeves=False, gloves=False, shoes="jazz")
