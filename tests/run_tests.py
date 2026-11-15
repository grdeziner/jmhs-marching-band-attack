"""Headless test suite for JMHS MARCHING BAND ATTACK.
Usage: python tests/run_tests.py [base_url_or_file]   (default http://localhost:8731/index.html)
Writes screenshots to screenshots/ and prints a JSON report; exits 1 on failure."""
import asyncio, sys, json, os, itertools
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8731/index.html'
SHOTS = os.environ.get('SHOTS_DIR') or os.path.join(os.path.dirname(__file__), '..', 'screenshots'); os.makedirs(SHOTS, exist_ok=True)
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')
fails, report = [], {}
def check(cond, msg):
    if not cond: fails.append(msg)

async def shot(pg, name):
    await pg.locator('#game').screenshot(path=os.path.join(SHOTS, name + '.png'))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None, args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 720})
        errs = []
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and '404' not in m.text and 'Failed to load resource' not in m.text else None)
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        sep = '&' if '?' in URL else '?'
        await pg.goto(URL + sep + 'mute=1&manual=1')
        await pg.wait_for_function('window.BAND && (BAND.ready || BAND.loadError)', timeout=30000)
        check(not await pg.evaluate('BAND.loadError || null'), 'load error')
        info = await pg.evaluate('''({fighters: BAND.content.fighters.map(f=>({id:f.id,name:f.fullName,short:f.short,instrument:f.instrument,taunt:!!f.taunt,win:!!f.winQuote,special:f.special.name,super:f.super.name,art:BAND.arts[f.id].source})),
            stages: BAND.content.stages.map(s=>({id:s.id,name:s.name,art:BAND.stageArts[s.id].source,anims:BAND.stageArts[s.id].anims.length,music:!!BAND.content.music[s.id], bpm: BAND.content.music[s.id] && BAND.content.music[s.id].bpm}))})''')
        report['content'] = info
        check(len(info['fighters']) == 9, 'expected 9 fighters')
        check(all(f['taunt'] and f['win'] for f in info['fighters']), 'story text missing')
        check(len(info['stages']) == 3 and all(s['music'] for s in info['stages']), 'stage music missing')
        # --- menus ---
        await pg.evaluate('BAND.step(40)'); await shot(pg, '01_title')
        await pg.evaluate("BAND.go(new BAND.scenes.SelectScene(BAND,'versus')); BAND.ctl[1].virtual={right:true}; BAND.step(2); BAND.ctl[1].virtual={}; BAND.step(30)")
        await shot(pg, '02_select')
        await pg.evaluate("BAND.go(new BAND.scenes.StageSelectScene(BAND,'versus',BAND.fighter('drummer'),BAND.fighter('tuba'))); BAND.step(20)"); await shot(pg, '03_stage_select')
        await pg.evaluate("BAND.go(new BAND.scenes.VSScene(BAND,{mode:'versus',p1:BAND.fighter('drummer'),p2:BAND.fighter('bassclarinet'),stage:BAND.stage('football')})); BAND.step(60)"); await shot(pg, '04_vs')
        await pg.evaluate("BAND.go(new BAND.scenes.HowToScene(BAND)); BAND.step(2)"); await shot(pg, '05_howto')
        # --- full CPU vs CPU matches on every stage ---
        stages = [s['id'] for s in info['stages']]
        ids = [f['id'] for f in info['fighters']]
        pairs = [('drummer', 'tuba'), ('xylophone', 'bassclarinet'), ('flute', 'trumpet'), ('trombone', 'clarinet'), ('colorguard', 'drummer'), ('clarinet', 'bassclarinet')]
        matches = []
        for i, (a, c) in enumerate(pairs):
            st = stages[i % len(stages)]
            await pg.evaluate(f"""BAND.settings.cpuDifficulty={2 + i % 3}; BAND.done=null; BAND.startFight({{mode:'watch',p1:BAND.fighter('{a}'),p2:BAND.fighter('{c}'),stage:BAND.stage('{st}'),seed:{i+3}}});
              BAND.afterFight = (m,res)=>{{BAND.done=res;}}; BAND.scene.fight.o.onEnd=(res)=>{{BAND.done=res;}}""")
            if i < 3:
                await pg.evaluate('BAND.step(20)'); await shot(pg, f'1{i}_round1_{st}')
                await pg.evaluate('BAND.step(85)'); await shot(pg, f'1{i}_fight_call_{st}')
                await pg.evaluate('BAND.step(400)'); await shot(pg, f'1{i}_midfight_{st}')
            res = None
            for _ in range(120):
                r = await pg.evaluate('''(()=>{ const F=BAND.scene.fight; for(let k=0;k<300;k++){ if(BAND.done) break; BAND.tick(); if(F.phase==='ko' && F.phaseT===20 && !BAND.koShot){BAND.koShot=1; BAND.render(); return 'ko';} } BAND.render(); return BAND.done ? 'done' : 'running'; })()''')
                if r == 'ko' and i < 3: await shot(pg, f'1{i}_ko_{st}')
                if r == 'done': break
                await pg.evaluate('BAND.koShot = BAND.koShot && BAND.scene.fight.phase==="ko" ? 1 : 0')
            res = await pg.evaluate('BAND.done && {winner: BAND.done.winner, rounds: BAND.done.rounds, frames: BAND.scene.fight.frame, hits: BAND.scene.fight.log.length}')
            matches.append({'p1': a, 'p2': c, 'stage': st, **(res or {'winner': 'timeout'})})
            check(res is not None, f'match {a} v {c} did not finish')
            if res: check(res['hits'] > 5, f'match {a} v {c}: too few hits ({res["hits"]})')
        report['matches'] = matches
        # --- every special + super fires without errors ---
        moves = {}
        for fid in ids:
            out = await pg.evaluate(f"""(()=>{{ BAND.startFight({{mode:'versus',p1:BAND.fighter('{fid}'),p2:BAND.fighter('drummer'),stage:BAND.stage('football'),seed:5}});
              const F=BAND.scene.fight; BAND.cpus=[null,null]; BAND.step(115); const me=F.f[0], op=F.f[1]; me.x=op.x-120; 
              const res={{}};
              const press=(k)=>{{BAND.ctl[0].virtual={{[k]:true}}; BAND.tick(); BAND.ctl[0].virtual={{}};}};
              op.hp=op.maxHp; press('special'); res.specialState=me.state; let maxP=0, hit0=op.hp;
              for(let i=0;i<90;i++){{ BAND.tick(); maxP=Math.max(maxP,F.projectiles.length); if(i===14) BAND.render(); }}
              res.specialDmg=hit0-op.hp; res.specialProj=maxP;
              F.f[1].reset(me.x+120,-1); F.f[1].state='idle'; me.reset(me.x,1); me.state='idle'; me.meter=100; hit0=op.hp; press('super'); res.superState=me.state; res.freeze=!!F.freeze;
              for(let i=0;i<30;i++) BAND.tick(); BAND.render();
              return res; }})()""")
            await shot(pg, f'2_super_{fid}')
            out2 = await pg.evaluate("""(()=>{ const F=BAND.scene.fight, op=F.f[1]; const h=op.hp; for(let i=0;i<160;i++) BAND.tick(); BAND.render(); return {superDmg: op.maxHp - op.hp}; })()""")
            out.update(out2); moves[fid] = out
            check(out['specialState'] == 'move', f'{fid}: special did not start')
            check(out['superState'] == 'move' and out['freeze'], f'{fid}: super did not start')
            check(out['superDmg'] > 0, f'{fid}: super did no damage')
        report['moves'] = moves
        # special screenshot for the drummer's png projectile
        await pg.evaluate("""(()=>{ BAND.startFight({mode:'versus',p1:BAND.fighter('drummer'),p2:BAND.fighter('bassclarinet'),stage:BAND.stage('lockerroom'),seed:5}); BAND.cpus=[null,null]; BAND.step(115);
           const F=BAND.scene.fight; F.f[0].x = F.f[1].x - 250; BAND.ctl[0].virtual={special:true}; BAND.tick(); BAND.ctl[0].virtual={}; BAND.step(26); })()""")
        await shot(pg, '30_drummer_png_shockwave')
        await pg.evaluate("BAND.ctl[1].virtual={special:true}; BAND.tick(); BAND.ctl[1].virtual={}; BAND.step(20)")
        await shot(pg, '31_bassclarinet_drone')
        # result + ending screens
        await pg.evaluate("""BAND.go(new BAND.scenes.ResultScene(BAND,{p1:BAND.fighter('tuba'),p2:BAND.fighter('flute')},{winner:0},()=>{})); BAND.step(30)"""); await shot(pg, '40_win_quote')
        await pg.evaluate("""BAND.go(new BAND.scenes.EndingScene(BAND,BAND.fighter('drummer'))); BAND.step(30)"""); await shot(pg, '41_ending')
        await pg.evaluate("""BAND.go(new BAND.scenes.OptionsScene(BAND)); BAND.step(2)"""); await shot(pg, '42_options')
        # --- audio: chip synth schedules notes for every stage song ---
        aud = await pg.evaluate('''(async()=>{ const a=BAND.audio; a.setOption('music',true); a.ensure(); await a.ctx.resume(); const out={state:a.ctx.state};
            for (const s of BAND.content.stages) { a.play(BAND.content.music[s.id]); await new Promise(r=>setTimeout(r,400)); out[s.id]=a.voices.size; a.stop(); }
            a.sfx('hit'); a.sfx('bassclarinet'); return out; })()''')
        report['audio'] = aud
        check(all(aud.get(s['id'], 0) > 0 for s in info['stages']), 'music did not schedule notes')
        errs += await pg.evaluate('BAND.errors')
        report['errors'] = errs
        check(not errs, 'runtime errors: ' + '; '.join(errs[:5]))
        await b.close()
    report['fails'] = fails
    print(json.dumps(report, indent=1))
    sys.exit(1 if fails else 0)
asyncio.run(main())
