/**
 * Playable placeholder for JMHS Marching Band Attack.
 *
 * Draws a title screen and a character-select grid into the 320×180 canvas.
 * Fighter names come from content/roster.json. The fighting engine is not
 * here; drop it into src/engine and replace this loop when the match exists.
 */

const canvas = document.querySelector('#game');
const statusEl = document.querySelector('#status');
if (!(canvas instanceof HTMLCanvasElement) || !statusEl) {
  throw new Error('Missing game markup');
}

const ctx = canvas.getContext('2d', { alpha: false });
if (!ctx) {
  throw new Error('Canvas 2D is unavailable');
}
ctx.imageSmoothingEnabled = false;

const C = {
  sky: '#100c14',
  gold: '#ffcc33',
  cream: '#f6f1e4',
  red: '#9d1c32',
  field: '#0e2a18',
  fieldEdge: '#245c34',
  yard: '#d5e2c4',
  cell: '#171e2e',
  cellOn: '#342c16',
  edge: '#31405c',
  hint: '#93a0b8',
  shadow: '#14080e',
  starDim: '#6a6278',
};

const STARS = [
  [12, 10, C.cream],
  [30, 24, C.starDim],
  [304, 12, C.cream],
  [284, 28, C.starDim],
  [158, 8, C.starDim],
];

const state = {
  scene: 'loading',
  fighters: [],
  index: 0,
  reduceMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
};

const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
motionQuery.addEventListener('change', (event) => {
  state.reduceMotion = event.matches;
});

function fitCanvas() {
  const scale = Math.max(
    1,
    Math.floor(Math.min(window.innerWidth / 320, window.innerHeight / 180)),
  );
  canvas.style.width = `${320 * scale}px`;
  canvas.style.height = `${180 * scale}px`;
  canvas.style.imageRendering = 'pixelated';
}

window.addEventListener('resize', fitCanvas);
fitCanvas();

function publish() {
  const ids = state.fighters.map((fighter) => fighter.id).join(',');
  const names = state.fighters.map((fighter) => fighter.name).join(', ');
  const current = state.fighters[state.index];
  let label = 'JMHS Marching Band Attack. Loading.';
  let live = 'Loading.';
  if (state.scene === 'title') {
    label = 'JMHS Marching Band Attack. Press start.';
    live = label;
  } else if (state.scene === 'select' && current) {
    label = `Choose your fighter. ${names}. Selected ${current.name}. ${current.placeholder ?? ''}`;
    live = `${current.name}. ${current.placeholder ?? ''}`.trim();
  } else if (state.scene === 'error') {
    label = 'Could not load the roster.';
    live = label;
  }
  canvas.dataset.scene = state.scene;
  canvas.dataset.index = String(state.index);
  canvas.dataset.fighters = ids;
  canvas.setAttribute('aria-label', label);
  statusEl.textContent = live;
}

let loadInFlight = false;

async function boot() {
  if (loadInFlight) return;
  loadInFlight = true;
  try {
    const url = new URL('../content/roster.json', import.meta.url);
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Roster request failed (${response.status})`);
    }
    const data = await response.json();
    if (!Array.isArray(data.fighters) || data.fighters.length === 0) {
      throw new Error('Roster has no fighters');
    }
    for (const fighter of data.fighters) {
      if (typeof fighter.id !== 'string' || fighter.id === '') {
        throw new Error('A fighter is missing an id');
      }
      if (typeof fighter.name !== 'string' || fighter.name === '') {
        throw new Error('A fighter is missing a name');
      }
    }
    state.fighters = data.fighters;
    state.index = Math.min(state.index, data.fighters.length - 1);
    state.scene = 'title';
  } catch (error) {
    state.scene = 'error';
    console.error(error);
  } finally {
    loadInFlight = false;
    publish();
  }
}

function startFromTitle() {
  if (state.scene === 'title' && state.fighters.length > 0) {
    state.scene = 'select';
    publish();
    return;
  }
  if (state.scene === 'error') {
    state.scene = 'loading';
    publish();
    boot();
  }
}

function gridMetrics() {
  const cols = 3;
  const count = Math.max(state.fighters.length, 1);
  const rows = Math.ceil(count / cols);
  const gap = 4;
  const gridY = 32;
  const gridBottom = 132;
  const cellH = Math.max(16, Math.floor((gridBottom - gridY - gap * (rows - 1)) / rows));
  const cellW = 96;
  const gridW = cols * cellW + (cols - 1) * gap;
  const gridX = Math.floor((320 - gridW) / 2);
  return { cols, rows, gap, gridY, gridX, cellW, cellH };
}

function cellRect(index) {
  const metrics = gridMetrics();
  const col = index % metrics.cols;
  const row = Math.floor(index / metrics.cols);
  return {
    x: metrics.gridX + col * (metrics.cellW + metrics.gap),
    y: metrics.gridY + row * (metrics.cellH + metrics.gap),
    w: metrics.cellW,
    h: metrics.cellH,
  };
}

function cellAt(px, py) {
  for (let index = 0; index < state.fighters.length; index += 1) {
    const rect = cellRect(index);
    if (px >= rect.x && px < rect.x + rect.w && py >= rect.y && py < rect.y + rect.h) {
      return index;
    }
  }
  return -1;
}

function moveCursor(dx, dy) {
  const { cols, rows } = gridMetrics();
  const count = state.fighters.length;
  if (count === 0) return;
  let x = state.index % cols;
  let y = Math.floor(state.index / cols);
  x = Math.min(cols - 1, Math.max(0, x + dx));
  y = Math.min(rows - 1, Math.max(0, y + dy));
  let next = y * cols + x;
  if (next >= count) next = count - 1;
  state.index = next;
}

function canvasPoint(event) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: ((event.clientX - rect.left) * canvas.width) / rect.width,
    y: ((event.clientY - rect.top) * canvas.height) / rect.height,
  };
}

window.addEventListener('keydown', (event) => {
  const key = event.key;
  if (key === ' ' || key === 'Enter' || key === 'Escape' || key === 'Backspace' || key.startsWith('Arrow')) {
    event.preventDefault();
  }
  if (state.scene === 'title' || state.scene === 'error') {
    if ((key === 'Enter' || key === ' ') && !event.repeat) startFromTitle();
    return;
  }
  if (state.scene !== 'select') return;
  if ((key === 'Escape' || key === 'Backspace') && !event.repeat) {
    state.scene = 'title';
    publish();
    return;
  }
  if (key === 'ArrowLeft' || key === 'a' || key === 'A') moveCursor(-1, 0);
  else if (key === 'ArrowRight' || key === 'd' || key === 'D') moveCursor(1, 0);
  else if (key === 'ArrowUp' || key === 'w' || key === 'W') moveCursor(0, -1);
  else if (key === 'ArrowDown' || key === 's' || key === 'S') moveCursor(0, 1);
  else if (/^[1-9]$/.test(key)) {
    const next = Number(key) - 1;
    if (next < state.fighters.length) state.index = next;
  } else {
    return;
  }
  publish();
});

canvas.addEventListener('contextmenu', (event) => {
  event.preventDefault();
});

canvas.addEventListener('pointerdown', (event) => {
  const point = canvasPoint(event);
  if (state.scene === 'title' || state.scene === 'error') {
    startFromTitle();
    return;
  }
  if (state.scene !== 'select') return;
  const hit = cellAt(point.x, point.y);
  if (hit >= 0) {
    state.index = hit;
    publish();
  }
});

function draw(now) {
  ctx.imageSmoothingEnabled = false;
  if (state.scene === 'select') drawSelect();
  else drawTitle(now);
  requestAnimationFrame(draw);
}

function drawTitle(now) {
  rect(0, 0, 320, 180, C.sky);
  for (const [x, y, color] of STARS) rect(x, y, 1, 1, color);
  rect(0, 58, 320, 36, C.red);
  rect(0, 58, 320, 1, C.gold);
  rect(0, 93, 320, 1, C.gold);
  rect(0, 136, 320, 44, C.field);
  rect(0, 136, 320, 2, C.fieldEdge);
  rect(0, 152, 320, 1, C.yard);
  drawCentered('JMHS', 18, C.cream, 2, C.shadow);
  drawCentered('MARCHING BAND', 38, C.gold, 2, C.shadow);
  drawCentered('ATTACK', 66, C.gold, 3, '#4a0c18');

  let prompt = 'LOADING';
  let promptColor = C.cream;
  let visible = true;
  if (state.scene === 'title') {
    prompt = 'PRESS START';
    promptColor = C.gold;
    visible = state.reduceMotion || Math.floor(now / 480) % 2 === 0;
  } else if (state.scene === 'error') {
    prompt = 'ROSTER FAILED';
    promptColor = '#ff6670';
  }
  if (visible) drawCentered(prompt, 112, promptColor, 2, C.shadow);
  drawCabinet();
}

function drawSelect() {
  const metrics = gridMetrics();
  rect(0, 0, 320, 180, C.sky);
  rect(0, 0, 320, 26, C.red);
  rect(0, 25, 320, 1, C.gold);
  drawCentered('CHOOSE YOUR FIGHTER', 9, C.gold, 1, '#4a0c18');

  for (let index = 0; index < state.fighters.length; index += 1) {
    const fighter = state.fighters[index];
    const rectBox = cellRect(index);
    const selected = index === state.index;
    rect(rectBox.x, rectBox.y, rectBox.w, rectBox.h, selected ? C.cellOn : C.cell);
    strokeRect(rectBox.x, rectBox.y, rectBox.w, rectBox.h, selected ? C.gold : C.edge, selected ? 2 : 1);
    const label = sanitize(fighter.name);
    const scale = 1;
    const width = label.length * 6 * scale;
    const textX = rectBox.x + Math.floor((rectBox.w - width) / 2);
    const textY = rectBox.y + Math.floor((rectBox.h - 7 * scale) / 2);
    drawText(label, textX, textY, selected ? C.gold : C.cream, scale);
  }

  const current = state.fighters[state.index];
  if (current) {
    drawCentered(sanitize(current.name), 138, C.gold, 1, C.shadow);
    const lines = wrapLines(sanitize(current.placeholder || ''), 48).slice(0, 2);
    lines.forEach((line, lineIndex) => {
      drawCentered(line, 150 + lineIndex * 9, C.cream, 1, C.shadow);
    });
  }
  rect(0, 166, 320, 14, '#0c1018');
  drawCentered('ARROWS OR CLICK TO PICK   ESC BACK', 170, C.hint, 1);
  drawCabinet();
}

function drawCabinet() {
  rect(0, 0, 320, 2, C.gold);
  rect(0, 178, 320, 2, C.gold);
  rect(0, 0, 2, 180, C.gold);
  rect(318, 0, 2, 180, C.gold);
  rect(2, 2, 316, 1, C.red);
  rect(2, 177, 316, 1, C.red);
  rect(2, 2, 1, 176, C.red);
  rect(317, 2, 1, 176, C.red);
}

function rect(x, y, w, h, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, h);
}

function strokeRect(x, y, w, h, color, thickness) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, thickness);
  ctx.fillRect(x, y + h - thickness, w, thickness);
  ctx.fillRect(x, y, thickness, h);
  ctx.fillRect(x + w - thickness, y, thickness, h);
}

function sanitize(text) {
  return String(text ?? '')
    .toUpperCase()
    .replace(/[^A-Z0-9 .,'!?:/-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function wrapLines(text, maxChars) {
  if (!text) return [];
  const words = text.split(' ');
  const lines = [];
  let line = '';
  for (const word of words) {
    const next = line ? `${line} ${word}` : word;
    if (next.length > maxChars && line) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function textWidth(text, scale) {
  return text.length * 6 * scale;
}

function drawCentered(text, y, color, scale, shadow) {
  const x = Math.floor((320 - textWidth(text, scale)) / 2);
  if (shadow) drawText(text, x + scale, y + scale, shadow, scale);
  drawText(text, x, y, color, scale);
}

function drawText(text, x, y, color, scale) {
  ctx.fillStyle = color;
  for (let i = 0; i < text.length; i += 1) {
    const glyph = FONT[text[i]];
    if (!glyph) continue;
    const originX = x + i * 6 * scale;
    for (let row = 0; row < glyph.length; row += 1) {
      const bits = glyph[row];
      for (let col = 0; col < 5; col += 1) {
        if (((bits >> (4 - col)) & 1) === 1) {
          ctx.fillRect(originX + col * scale, y + row * scale, scale, scale);
        }
      }
    }
  }
}

function compileFont() {
  const compiled = {};
  for (const [character, rows] of Object.entries(GLYPH_ROWS)) {
    if (rows.length !== 7 || rows.some((row) => !/^[01]{5}$/.test(row))) {
      throw new Error(`Bad glyph ${character}`);
    }
    compiled[character] = rows.map((row) => Number.parseInt(row, 2));
  }
  return compiled;
}

const GLYPH_ROWS = {
  ' ': ['00000', '00000', '00000', '00000', '00000', '00000', '00000'],
  '.': ['00000', '00000', '00000', '00000', '00000', '01100', '01100'],
  ',': ['00000', '00000', '00000', '00000', '00110', '00110', '01100'],
  "'": ['00100', '00100', '01000', '00000', '00000', '00000', '00000'],
  '!': ['00100', '00100', '00100', '00100', '00100', '00000', '00100'],
  '?': ['01110', '10001', '00001', '00010', '00100', '00000', '00100'],
  '-': ['00000', '00000', '00000', '11111', '00000', '00000', '00000'],
  ':': ['00000', '01100', '01100', '00000', '01100', '01100', '00000'],
  '/': ['00001', '00010', '00010', '00100', '01000', '01000', '10000'],
  A: ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
  B: ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
  C: ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
  D: ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
  E: ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
  F: ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
  G: ['01110', '10001', '10000', '10111', '10001', '10001', '01110'],
  H: ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
  I: ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
  J: ['00111', '00010', '00010', '00010', '10010', '10010', '01100'],
  K: ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
  L: ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
  M: ['10001', '11011', '10101', '10001', '10001', '10001', '10001'],
  N: ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
  O: ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
  P: ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
  Q: ['01110', '10001', '10001', '10001', '10101', '10010', '01101'],
  R: ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
  S: ['01110', '10001', '10000', '01110', '00001', '10001', '01110'],
  T: ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
  U: ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
  V: ['10001', '10001', '10001', '10001', '01010', '01010', '00100'],
  W: ['10001', '10001', '10001', '10101', '10101', '10101', '01010'],
  X: ['10001', '10001', '01010', '00100', '01010', '10001', '10001'],
  Y: ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
  Z: ['11111', '00001', '00010', '00100', '01000', '10000', '11111'],
  0: ['01110', '10001', '10011', '10101', '11001', '10001', '01110'],
  1: ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
  2: ['01110', '10001', '00001', '00110', '01000', '10000', '11111'],
  3: ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
  4: ['00010', '00110', '01010', '10010', '11111', '00010', '00010'],
  5: ['11111', '10000', '11110', '00001', '00001', '10001', '01110'],
  6: ['01110', '10000', '10000', '11110', '10001', '10001', '01110'],
  7: ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
  8: ['01110', '10001', '10001', '01110', '10001', '10001', '01110'],
  9: ['01110', '10001', '10001', '01111', '00001', '00001', '01110'],
};

const FONT = compileFont();

publish();
requestAnimationFrame(draw);
boot();
