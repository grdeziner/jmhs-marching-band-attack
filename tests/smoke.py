import asyncio, sys, json
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8731/index.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 720})
        errs = []
        pg.on('console', lambda m: errs.append(m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        await pg.goto(URL + '?mute=1&manual=1')
        await pg.wait_for_function('window.BAND && (window.BAND.ready || window.BAND.loadError)', timeout=20000)
        await pg.evaluate('BAND.step(30)')
        await pg.screenshot(path='/tmp/bw_title.png')
        print(json.dumps(await pg.evaluate('({err: BAND.errors, load: BAND.loadError||null, src: Object.fromEntries(Object.entries(BAND.arts).map(([k,v])=>[k,v.source])), st: Object.fromEntries(Object.entries(BAND.stageArts).map(([k,v])=>[k,v.source]))})'), indent=1))
        print('\n'.join(e for e in errs if '404' not in e)[:3000])
        await b.close()
asyncio.run(main())
