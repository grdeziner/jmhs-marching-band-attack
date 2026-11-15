# JMHS Marching Band Attack

Working title: **Band Wars**. An in-browser, 8-bit, Street Fighter II-style 1v1 fighting game about a high school marching band. The page is plain HTML5 canvas and vanilla JavaScript (ES modules). There is no framework and no build step.

The fight engine is not in this repo yet. What runs today is a placeholder: a title screen and a character-select grid filled from [`content/roster.json`](content/roster.json). Module stubs under `src/` are the drop-in points for the engine.

## Play on GitHub Pages

<https://grdeziner.github.io/jmhs-marching-band-attack/>

Every push to `main` runs [`.github/workflows/pages.yml`](.github/workflows/pages.yml), which uploads the repository root and deploys it with GitHub Pages.

One-time setup: the owner must set **Settings > Pages > Source** to **GitHub Actions** once. Until that source is selected, the workflow has nowhere to publish.

## Run locally

ES modules and `content/roster.json` have to be loaded over HTTP. Opening `index.html` as a file will not start the game.

From the repository root:

```
python3 -m http.server 8000
```

or:

```
npx serve . -p 8000
```

Then open <http://localhost:8000>.

`npx serve .` on its own also works. It prints the address it picked (port 3000 when that port is free).

## Controls

On the title screen, press Enter or Space, or click the canvas. **PRESS START** blinks unless the OS asks for reduced motion.

On the character select screen, move with the arrow keys, WASD, the number keys 1–9, or a click. Esc or Backspace returns to the title. The nine names are read from the roster file, not hard-coded.

## Layout

```
index.html              canvas page
src/main.js             placeholder title and select
src/engine/             fight simulation stub
src/scenes/             scene stub
src/fighters/           sprite and data loader stub
src/audio/              audio stub
src/input/              two-player input stub
content/roster.json     nine fighter ids and select-screen lines
content/stages.json     three stages and the stage size contract
content/characters/     one backstory JSON per fighter
art/characters/<id>/    sheet.png, sheet.json, portrait.png
art/stages/<id>/        far.png, mid.png, optional anim_N.png
```

Stage art, character art, and character backstories each have a lane. See [CONTRIBUTING.md](CONTRIBUTING.md). The backstory field list is in [content/characters/README.md](content/characters/README.md).
