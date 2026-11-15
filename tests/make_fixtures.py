"""Builds tests/fixtures/art16/ — a synthetic 16-bit art tree used by tests/sixteen_bit_test.py.
Reads (never writes) the real art/ tree. Exercises every optional part of the 16-bit contract:
  * 128x112 frames declared with frameW/frameH, anchor 64,111, animations without 'row' keys (row = order),
    extra frames (idle has 8, so the sheet is wider than 6 columns), per-animation fps/loop, spawn + hold frames
  * portrait_large.png (128x128), super.png listed under 'super' in sheet.json
  * stage near.png (1120x360, 240px margins) and anim_0..7 (0-3 mid width, 4-7 near width)
Characters not present here fall back to procedural art, which the test also checks."""
import json, os, shutil
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art'); OUT = os.path.join(ROOT, 'tests', 'fixtures', 'art16')
ORDER = ['idle', 'walk', 'jump', 'crouch', 'block', 'punch', 'kick', 'special', 'hit', 'ko']
EXTRA = {'idle': 8}  # more frames than the 8-bit defaults

def fighter(cid):
    d = os.path.join(SRC, 'characters', cid); js = json.load(open(os.path.join(d, 'sheet.json')))
    fw = js.get('frameW') or js.get('frameWidth') or 96; fh = js.get('frameH') or js.get('frameHeight') or 112
    sheet = Image.open(os.path.join(d, 'sheet.png')).convert('RGBA'); anims = js['animations']
    NW, NH, pad = 128, 112, (128 - fw) // 2
    counts = {a: EXTRA.get(a, anims[a]['frames']) for a in ORDER}
    out = Image.new('RGBA', (NW * max(counts.values()), NH * len(ORDER)), (0, 0, 0, 0))
    newanims = {}
    for r, a in enumerate(ORDER):
        src = anims[a]; row = src.get('row', ORDER.index(a)); n = src['frames']
        for i in range(counts[a]):
            fr = sheet.crop(((i % n) * fw, row * fh, (i % n) * fw + fw, row * fh + fh))
            out.paste(fr, (i * NW + pad, r * NH + (NH - fh)))
        na = {k: v for k, v in src.items() if k != 'row'}; na['frames'] = counts[a]
        for bk in ('hurtbox', 'hitbox', 'blockbox'):
            if bk in na: na[bk] = {**na[bk], 'x': na[bk]['x'] + pad}
        newanims[a] = na
    sp = newanims['special']
    if cid == 'tuba': sp['hold_frames'] = [2, 3]; sp['hold_point'] = {'x': 6, 'y': -100}; sp['spawn_projectile_on'] = 4
    o = os.path.join(OUT, 'characters', cid); os.makedirs(o, exist_ok=True)
    out.save(os.path.join(o, 'sheet.png'))
    nj = {'id': cid, 'frameW': NW, 'frameH': NH, 'anchor': {'x': 64, 'y': 111}, 'animations': newanims}
    if 'projectile' in js: nj['projectile'] = js['projectile']; shutil.copy(os.path.join(d, js['projectile'].get('file', 'projectile.png')), o)
    elif os.path.exists(os.path.join(d, 'projectile.png')): shutil.copy(os.path.join(d, 'projectile.png'), o)
    pr = Image.open(os.path.join(d, 'portrait.png')).convert('RGBA'); pr.save(os.path.join(o, 'portrait.png'))
    big = pr.resize((128, 128), Image.NEAREST); ImageDraw.Draw(big).rectangle((0, 0, 127, 127), outline=(255, 0, 255, 255), width=3)  # magenta frame marks the large one
    big.save(os.path.join(o, 'portrait_large.png'))
    if cid == 'drummer':  # synthetic super strip: 6 frames of an expanding ground ring, anchor bottom-centre
        s = Image.new('RGBA', (128 * 6, 80), (0, 0, 0, 0)); g = ImageDraw.Draw(s)
        for i in range(6):
            r = 10 + i * 9; cx = i * 128 + 64
            g.ellipse((cx - r, 72 - r // 2 - 8, cx + r, 72 + r // 2 - 8), outline=(255, 230, 90, 255), width=4)
            g.ellipse((cx - 8, 56, cx + 8, 72), fill=(255, 255, 255, 255))
        s.save(os.path.join(o, 'super.png'))
        nj['super'] = {'file': 'super.png', 'frameW': 128, 'frameH': 80, 'frames': 6, 'fps': 12, 'loop': False, 'anchor': {'x': 64, 'y': 72}}
    json.dump(nj, open(os.path.join(o, 'sheet.json'), 'w'), indent=1)

def stage(sid):
    d = os.path.join(SRC, 'stages', sid); o = os.path.join(OUT, 'stages', sid); os.makedirs(o, exist_ok=True)
    shutil.copy(os.path.join(d, 'far.png'), o); shutil.copy(os.path.join(d, 'mid.png'), o)
    for i in range(4):
        a = os.path.join(d, f'anim_{i}.png')
        (shutil.copy(a, os.path.join(o, f'anim_{i}.png')) if os.path.exists(a) else Image.new('RGBA', (960, 360)).save(os.path.join(o, f'anim_{i}.png')))
    near = Image.new('RGBA', (1120, 360), (0, 0, 0, 0)); g = ImageDraw.Draw(near)
    for x in range(0, 1120, 40): g.rectangle((x, 330, x + 30, 360), fill=(40, 30, 60, 255)); g.rectangle((x + 2, 332, x + 28, 336), fill=(120, 100, 160, 255))
    g.rectangle((0, 300, 60, 360), fill=(20, 20, 30, 255)); g.rectangle((1060, 300, 1120, 360), fill=(20, 20, 30, 255))
    near.save(os.path.join(o, 'near.png'))
    for i in range(4, 8):  # near-width animated foreground: a blinking sign
        a = Image.new('RGBA', (1120, 360), (0, 0, 0, 0)); ImageDraw.Draw(a).rectangle((540, 306, 580, 326), fill=((255, 60, 60, 255) if i % 2 else (255, 230, 90, 255)))
        a.save(os.path.join(o, f'anim_{i}.png'))

if __name__ == '__main__':
    shutil.rmtree(OUT, ignore_errors=True)
    for c in ('drummer', 'tuba', 'flute'): fighter(c)
    stage('football')
    print('fixtures written to', OUT)
