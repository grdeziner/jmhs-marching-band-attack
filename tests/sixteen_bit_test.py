"""16-bit engine checks against the synthetic fixture tree (run tests/make_fixtures.py first; this script does it for you).
  * 128x112 sheets with frameW/frameH, row order, extra frames, portrait_large, super.png, tuba hold frames
  * stage near.png + anim_0..7 layer assignment
  * SNES synth: format-2 song (8 voices, mix, echo, chords, velocity, object channel) + legacy format + composer catalog
Usage: python tests/sixteen_bit_test.py [http://localhost:8731/index.html]"""
import asyncio, sys, json, os, subprocess
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8731/index.html'
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
subprocess.run([sys.executable if 'pwvenv' not in sys.executable else 'python3', os.path.join(HERE, 'make_fixtures.py')], check=True)
fails = []
def check(c, m):
    if not c: fails.append(m)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 720})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL + '?mute=1&manual=1&art=tests/fixtures/art16/')
        await pg.wait_for_function('window.BAND && (BAND.ready || BAND.loadError)', timeout=30000)
        shot = lambda n: pg.locator('#game').screenshot(path=os.path.join(ROOT, 'screenshots', n + '.png'))
        r = {}
        r['art'] = await pg.evaluate('''(()=>{ const A=BAND.arts, d=A.drummer, t=A.tuba, s=BAND.stageArts.football;
          return { src:Object.fromEntries(Object.entries(A).map(([k,v])=>[k,v.source])), drummer:{fw:d.frameW, fh:d.frameH, idle:d.anims.idle.length, idleW:d.anims.idle[0].sw, ax:d.anims.idle[0].ax, ay:d.anims.idle[0].ay,
            kickY:d.anims.kick[0].sy, large:!!d.portraitLarge, largeW:d.portraitLarge&&d.portraitLarge.width, sup:d.super?{n:d.super.n,w:d.super.w,h:d.super.h,ay:d.super.ay}:null, idleFps:d.meta.idle.fps},
            tuba:{fw:t.frameW, hold:t.meta.special.hold, spawn:t.meta.special.spawn, holdPoint:t.meta.special.holdPoint},
            stage:{src:s.source, near:s.near&&s.near.width, anims:s.anims.length, layers:Object.fromEntries(Object.entries(s.animLayers||{}).map(([k,v])=>[k,v.length]))},
            otherStages:Object.fromEntries(Object.entries(BAND.stageArts).map(([k,v])=>[k,v.source])) }; })()''')
        a = r['art']
        check(a['drummer']['fw'] == 128 and a['drummer']['fh'] == 112 and a['drummer']['idleW'] == 128, 'drummer frame size not 128x112')
        check(a['drummer']['idle'] == 8, 'idle frame count not read from sheet.json')
        check(a['drummer']['kickY'] == 6 * 112, 'row y not taken from animation order')
        check(a['drummer']['ax'] == 64 and a['drummer']['ay'] == 112, 'anchor 64,111 not applied')
        check(a['drummer']['large'] and a['drummer']['largeW'] == 128, 'portrait_large not loaded')
        check(a['drummer']['sup'] and a['drummer']['sup']['n'] == 6, 'super.png not loaded')
        check(a['tuba']['hold'] == [2, 3] and a['tuba']['spawn'] == 4, 'tuba hold/spawn frames not read')
        check(a['src'].get('trumpet') == 'procedural', 'missing fighter did not fall back to procedural')
        check(a['stage']['near'] == 1120 and a['stage']['anims'] == 8 and a['stage']['layers'].get('near') == 4 and a['stage']['layers'].get('mid') == 4, 'stage near/anim_0..7 not detected')
        await pg.evaluate("BAND.go(new BAND.scenes.SelectScene(BAND,'versus')); BAND.step(12)"); await shot('60_16bit_select_portrait_large')
        # drummer super with super.png
        r['super'] = await pg.evaluate('''(()=>{ BAND.startFight({mode:'versus',p1:BAND.fighter('drummer'),p2:BAND.fighter('tuba'),stage:BAND.stage('football'),seed:5}); const F=BAND.scene.fight; BAND.step(115);
          const [d,t]=F.f; d.x=F.cam+220; t.x=d.x+200; d.meter=999; d.startMove(F,d.superMove); let used=null, hp0=t.hp;
          for(let i=0;i<70;i++){ BAND.step(1); const p=F.projectiles.find(p=>p.usePng==='super'); if(p&&!used) used={y:p.y, age:p.age}; if(i===24) window.__shotSuper=1; }
          return {used, dmg:hp0-t.hp, freeze:!!F.freeze}; })()''')
        await shot('61_16bit_drummer_super_png')
        check(r['super']['used'] is not None and r['super']['used']['y'] == 0, 'drummer super did not use super.png on the ground line')
        check(r['super']['dmg'] > 0, 'drummer super did no damage')
        # super flash background frame
        await pg.evaluate("(()=>{ const F=BAND.scene.fight; F.f[0].meter=999; F.f[0].setState('idle'); F.projectiles=[]; F.f[0].startMove(F,F.f[0].superMove); BAND.step(8); })()"); await shot('62_16bit_super_flash')
        # tuba hold frames 2-3 carry the opponent overhead
        r['tuba'] = await pg.evaluate('''(()=>{ BAND.startFight({mode:'versus',p1:BAND.fighter('tuba'),p2:BAND.fighter('flute'),stage:BAND.stage('football'),seed:7}); const F=BAND.scene.fight; BAND.step(115);
          const [t,o]=F.f; t.x=F.cam+260; o.x=t.x+50; t.startMove(F,t.special); const seen=[], lifted=[]; let held=null;
          for(let i=0;i<90;i++){ BAND.step(1); if(o.state==='held'){ seen.push(t.moveFrameIndex()); if(o.y>30){ lifted.push(t.moveFrameIndex()); if(!held&&lifted.length>=4){ held={x:o.x-t.x,y:o.y}; break; } } } }
          return {seen, lifted, held}; })()''')
        await shot('63_16bit_tuba_overhead_hold')
        check(r['tuba']['lifted'] and set(r['tuba']['lifted']) <= {2, 3}, 'tuba overhead carry not on hold frames 2-3: %s' % r['tuba']['lifted'])
        check((r['tuba'].get('held') or {}).get('y', 0) > 30, 'opponent not lifted overhead')
        r['tuba_end'] = await pg.evaluate("(()=>{ const F=BAND.scene.fight; const o=F.f[1], hp=o.hp; BAND.step(80); return {dmg:o.maxHp-o.hp, state:o.state}; })()")
        check(r['tuba_end']['dmg'] >= 100, 'tuba slam did not land')
        # near layer in front of fighters + hit sparks/dust
        await pg.evaluate('''(()=>{ BAND.startFight({mode:'versus',p1:BAND.fighter('flute'),p2:BAND.fighter('drummer'),stage:BAND.stage('football'),seed:9}); const F=BAND.scene.fight; BAND.step(115);
          const [a,b]=F.f; a.x=F.cam+300; b.x=a.x+60; F.resolveHit(a,b,{dmg:90,stun:20,push:3,knockdown:1},b.x-20,250); BAND.step(2); })()''')
        await shot('64_16bit_sparks_near_layer')
        r['fx'] = await pg.evaluate("(()=>{ const F=BAND.scene.fight; const kinds=new Set(F.fx.list.map(e=>e.k)); BAND.step(40); F.fx.list.forEach(e=>kinds.add(e.k)); return {kinds:[...kinds], trail:F.f[1].dispHp>F.f[1].hp||F.f[1].trailDelay>=0}; })()")
        check('flash' in r['fx']['kinds'] and 'shard' in r['fx']['kinds'], 'hit sparks missing')
        check('dust' in r['fx']['kinds'], 'knockdown dust missing')
        # ---- audio ----
        r['audio'] = await pg.evaluate('''(async()=>{ const a=BAND.audio; a.setOption('music',true); a.ensure(); await a.ctx.resume();
          const m=await import(new URL('tests/fixtures/song_v2.js', document.baseURI).href); const out={catalog:Object.keys(a.catalog).length, organ:!!a.catalog.organ};
          a.play(m.song); await new Promise(r=>setTimeout(r,500)); out.v2={voices:a.voiceInfo.length, info:a.voiceInfo, sources:a.voices.size, echo:a.echoCfg}; a.stop();
          a.play(m.legacy); await new Promise(r=>setTimeout(r,400)); out.legacy={info:a.voiceInfo.map(v=>v.instrument), sources:a.voices.size}; a.stop();
          for (const s of BAND.content.stages) { a.play(BAND.content.music[s.id]); await new Promise(r=>setTimeout(r,300)); out[s.id]={voices:a.voiceInfo.length, sources:a.voices.size, fmt:BAND.content.music[s.id].format||1}; a.stop(); }
          for (const j of ['title','select','victory']) { const sg=BAND.content.music[j]; out[j]={present:!!sg, loop:sg?sg.loop:null}; if(sg){ a.play(sg,{loop:j==='victory'?false:undefined}); await new Promise(r=>setTimeout(r,300)); out[j].voices=a.voiceInfo.length; out[j].sources=a.voices.size; a.stop(); } }
          out.echoLP=a.echoLP.frequency.value;
          for (const n of ['hit','heavy','block','superflash','ko','tuba','bells','trumpet','snare','bassdrum']) a.sfx(n);
          return out; })()''')
        au = r['audio']
        check(au['v2']['voices'] == 8 and au['v2']['sources'] > 0, 'format-2 song did not schedule 8 voices')
        info = {v['id']: v for v in au['v2']['info']}
        check(abs(info['lead']['pan'] + 0.4) < 1e-6 and abs(info['horn']['pan'] + 0.7) < 1e-6 and info['horn']['instrument'] == 'horn', 'per-voice pan/instrument wrong')
        check(abs(au['v2']['echo']['delay'] - 0.3) < 1e-6, 'song echo settings not applied')
        check(au['legacy']['info'] == ['trumpet-lead', 'brass-section', 'tuba-bass', 'drumkit'], 'legacy channels not mapped to 16-bit patches')
        check(au['organ'], 'composer instrument catalog not loaded')
        for j in ('title', 'select', 'victory'): check(au[j]['present'] and au[j].get('sources', 0) > 0, j + ' music missing or silent')
        check(au['victory']['loop'] is False, 'victory should be a one-shot')
        check(3000 <= au['echoLP'] <= 5000, 'echo feedback low-pass outside 3-5 kHz')
        for sid in ('football', 'lockerroom', 'fastfood'): check(au[sid]['voices'] == 8 and au[sid]['sources'] > 0, sid + ' format-2 music silent')
        await b.close()
        r['errors'] = errs; r['fails'] = fails
        print(json.dumps(r, indent=1))
        sys.exit(1 if fails or errs else 0)
asyncio.run(main())
