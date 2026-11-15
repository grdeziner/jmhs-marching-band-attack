"""Checks the procedural fallback: with ?art=missing/ every fighter must use placeholder art (stages use a blank stand-in) and still play."""
import asyncio, sys, json, os
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8731/index.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await b.new_page(viewport={'width': 1280, 'height': 720})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL + '?mute=1&manual=1&art=__missing__/')
        await pg.wait_for_function('window.BAND && (BAND.ready || BAND.loadError)', timeout=30000)
        r = await pg.evaluate('''(()=>{ const out={f:Object.values(BAND.arts).map(a=>a.source), s:Object.values(BAND.stageArts).map(a=>a.source)};
          for (const st of BAND.content.stages) { BAND.done=null; BAND.startFight({mode:'watch',p1:BAND.fighter('drummer'),p2:BAND.fighter('colorguard'),stage:st,seed:3}); BAND.scene.fight.o.onEnd=(x)=>BAND.done=x; BAND.step(900); }
          out.err=BAND.errors; return out; })()''')
        os.makedirs('screenshots', exist_ok=True)
        await pg.locator('#game').screenshot(path='screenshots/50_fallback_procedural_fastfood.png')
        await pg.evaluate("BAND.startFight({mode:'watch',p1:BAND.fighter('drummer'),p2:BAND.fighter('tuba'),stage:BAND.stage('football'),seed:3}); BAND.step(600)")
        await pg.locator('#game').screenshot(path='screenshots/51_fallback_procedural_football.png')
        await pg.evaluate("BAND.go(new BAND.scenes.SelectScene(BAND,'versus')); BAND.step(10)")
        await pg.locator('#game').screenshot(path='screenshots/52_fallback_select.png')
        r['pageerrors'] = errs; print(json.dumps(r))
        ok = all(x == 'procedural' for x in r['f']) and all(x == 'missing' for x in r['s']) and not r['err'] and not errs
        await b.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
