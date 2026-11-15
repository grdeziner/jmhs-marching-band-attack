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


def dante():
    """Dante 'High C' Reyes — cocky, compact-normal, dark skin, black hair, orange plume."""
    s, sd, sl = _skin("#8D5524", "#5C3414", "#B5743A")
    p, pl, pd = _plume("#FF9F1C")
    return Look(skin=s, skin_dk=sd, skin_lt=sl, hair=_hair("#111111"),
                plume=p, plume_lt=pl, plume_dk=pd,
                limb=0.94, torso=0.96, shoe=0.94, head=0.98, glove=0.92,
                jaw=1.00, neck=0.94, female=False, hat="shako",
                hair_style="temples", sleeves=True, gloves=True, shoes="marching")


def theo():
    """Theo 'Slide' Washington — rangy normal, warm skin, brown hair, terra plume."""
    s, sd, sl = _skin("#E0AC69", "#B07A3C", "#F0C98A")
    p, pl, pd = _plume("#E76F51")
    return Look(skin=s, skin_dk=sd, skin_lt=sl, hair=_hair("#5A3825"),
                plume=p, plume_lt=pl, plume_dk=pd,
                limb=0.90, torso=0.90, shoe=0.94, head=0.96, glove=0.90,
                jaw=1.00, neck=0.92, female=False, hat="shako",
                hair_style="temples", sleeves=True, gloves=True, shoes="marching")


def maya():
    """Maya 'Squeak' Patel — balanced medium, mid-brown skin, dark hair, lime plume."""
    s, sd, sl = _skin("#C68642", "#8A5426", "#E0A86A")
    p, pl, pd = _plume("#8AC926")
    return Look(skin=s, skin_dk=sd, skin_lt=sl, hair=_hair("#3D2B1F"),
                plume=p, plume_lt=pl, plume_dk=pd,
                limb=0.82, torso=0.86, shoe=0.88, head=0.95, glove=0.86,
                jaw=0.90, neck=0.86, female=True, hat="shako",
                hair_style="temples", sleeves=True, gloves=True, shoes="marching")


def ozzie():
    """Ozzie 'The Deep End' Lindqvist — tall and lanky, dark skin, black hair, violet plume."""
    s, sd, sl = _skin("#8D5524", "#5C3414", "#B5743A")
    p, pl, pd = _plume("#A78BFA")
    return Look(skin=s, skin_dk=sd, skin_lt=sl, hair=_hair("#111111"),
                plume=p, plume_lt=pl, plume_dk=pd,
                limb=0.64, torso=0.68, shoe=0.82, head=0.88, glove=0.78,
                jaw=0.90, neck=0.72, female=False, hat="shako",
                hair_style="temples", sleeves=True, gloves=True, shoes="marching")
