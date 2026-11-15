// JMHS MARCHING BAND ATTACK - boot, main loop, scene routing and test hooks.
import { VIEW_W, VIEW_H, params } from './config.js';
import { loadContent, BASE } from './content.js';
import { loadFighterArt, loadStageArt } from './assets.js';
import { Controller, initKeyboard } from './input.js';
import { audio } from './audio.js';
import { CPU } from './ai.js';
import { Fight } from './fight.js';
import { drawText } from './font.js';
import { TitleScene, SelectScene, StageSelectScene, VSScene, FightScene, ResultScene, ContinueScene, EndingScene, HowToScene, OptionsScene } from './scenes.js';

const Q = params();
class Game {
  constructor(canvas) {
    this.canvas = canvas; this.ctx = canvas.getContext('2d'); this.ctx.imageSmoothingEnabled = false;
    this.ctl = [new Controller(0), new Controller(1)]; this.cpus = [null, null]; this.scene = null; this.frame = 0; this.errors = [];
    const saved = (() => { try { return JSON.parse(localStorage.getItem('jmhs-settings') || '{}'); } catch { return {}; } })();
    this.settings = { cpuDifficulty: 2, roundsToWin: 2, roundTime: 99, music: true, sfx: true, announcer: true, debug: false, ...saved };
    if (Q.mute) { this.settings.music = false; this.settings.sfx = false; this.settings.announcer = false; }
    for (const k of ['music', 'sfx', 'announcer']) audio.setOption(k, this.settings[k]);
  }
  saveSettings() { try { localStorage.setItem('jmhs-settings', JSON.stringify(this.settings)); } catch {} }
  async load() {
    this.drawLoading('LOADING...');
    this.content = await loadContent(); if (this.content.instruments) audio.setCatalog(this.content.instruments);
    const s = this.content.settings || {}; for (const k of ['cpuDifficulty', 'roundsToWin', 'roundTime']) if (s[k] !== undefined && !(k in (JSON.parse(localStorage.getItem('jmhs-settings') || '{}')))) this.settings[k] = s[k];
    this.arts = {}; this.stageArts = {};
    await Promise.all(this.content.fighters.map(async d => { this.arts[d.id] = await loadFighterArt(d); }));
    await Promise.all(this.content.stages.map(async st => { this.stageArts[st.id] = await loadStageArt(st); }));
    this.ready = true;
  }
  drawLoading(t) { const c = this.ctx; c.fillStyle = '#000'; c.fillRect(0, 0, VIEW_W, VIEW_H); drawText(c, t, VIEW_W / 2, VIEW_H / 2, { scale: 2, align: 'center' }); }
  go(scene) { this.scene = scene; }
  fighter(id) { return this.content.fighters.find(f => f.id === id) || this.content.fighters[0]; }
  stage(id) { return this.content.stages.find(s => s.id === id) || this.content.stages[0]; }
  makeFight(m, onEnd) {
    const lvl = this.settings.cpuDifficulty;
    this.cpus = [m.mode === 'watch' || m.cpu1 ? new CPU(m.cpuLevel1 || lvl) : null, m.mode === 'versus' && !m.cpu2 ? null : new CPU(m.cpuLevel2 || lvl)];
    if (m.mode === 'versus' && m.cpu2) this.cpus[1] = new CPU(lvl);
    this.ctl[0].solo = m.mode !== 'versus'; for (const c of this.ctl) c.clearVirtual();
    const f = new Fight({ p1: m.p1, p2: m.p2, art1: this.arts[m.p1.id], art2: this.arts[m.p2.id], stage: m.stage, stageArt: this.stageArts[m.stage.id],
      settings: { roundsToWin: this.settings.roundsToWin, roundTime: this.settings.roundTime }, seed: m.seed, debug: this.settings.debug, onEnd });
    audio.play(this.content.music[m.stage.id]);
    this.fight = f; return f;
  }
  startFight(m) { this.go(new FightScene(this, m)); }
  startArcadeMatch() { const A = this.arcade, opp = A.ladder[A.idx], st = this.content.stages[A.idx % this.content.stages.length];
    this.go(new VSScene(this, { mode: 'arcade', p1: A.p1, p2: opp, stage: st })); }
  afterFight(m, res) {
    for (const c of this.ctl) c.clearVirtual();
    this.lastResult = res;
    if (m.mode === 'arcade') {
      const A = this.arcade;
      if (res.winner === 0) this.go(new ResultScene(this, m, res, () => { A.idx++; if (A.idx >= A.ladder.length) this.go(new EndingScene(this, A.p1)); else this.startArcadeMatch(); }));
      else this.go(new ResultScene(this, m, res, () => this.go(new ContinueScene(this))));
    } else this.go(new ResultScene(this, m, res, () => this.go(m.auto ? new ResultScene(this, m, res, () => {}) : new SelectScene(this, m.mode))));
  }
  tick() {
    if (!this.ready || !this.scene) return;
    try { this.scene.update(); this.frame++; } catch (e) { this.errors.push(String(e && e.stack || e)); console.error(e); }
  }
  render() { if (!this.ready || !this.scene) return; try { this.ctx.imageSmoothingEnabled = false; this.scene.draw(this.ctx); } catch (e) { this.errors.push(String(e && e.stack || e)); console.error(e); } }
}

function fit(canvas) {
  const s = Math.max(1, Math.min(innerWidth / VIEW_W, innerHeight / VIEW_H)); const k = s >= 2 ? Math.floor(s) : s;
  canvas.style.width = VIEW_W * k + 'px'; canvas.style.height = VIEW_H * k + 'px';
}

async function boot() {
  const canvas = document.getElementById('game'); canvas.width = VIEW_W; canvas.height = VIEW_H; fit(canvas); addEventListener('resize', () => fit(canvas));
  if (Q.art) BASE.art = Q.art.endsWith('/') ? Q.art : Q.art + '/';
  const G = new Game(canvas); window.BAND = G; G.audio = audio;
  G.scenes = { TitleScene, SelectScene, StageSelectScene, VSScene, FightScene, ResultScene, ContinueScene, EndingScene, HowToScene, OptionsScene };
  initKeyboard(() => audio.ensure());
  try { await G.load(); } catch (e) { G.drawLoading('ERROR: ' + e.message.slice(0, 60)); console.error(e); G.errors.push(String(e)); G.loadError = String(e); return; }
  // URL test hooks: ?fight=1&p1=drummer&p2=tuba&stage=football&cpu1=1&cpu2=1&seed=7&manual=1&mute=1
  if (Q.fight) { const m = { mode: Q.cpu1 ? 'watch' : 'cpu', p1: G.fighter(Q.p1), p2: G.fighter(Q.p2 || G.content.fighters[1].id), stage: G.stage(Q.stage), cpu1: !!Q.cpu1, seed: +Q.seed || 1, auto: true };
    G.startFight(m); }
  else if (Q.scene === 'select') G.go(new SelectScene(G, Q.mode || 'versus'));
  else G.go(new TitleScene(G));
  // fixed 60 Hz simulation
  G.step = (n = 1) => { for (let i = 0; i < n; i++) G.tick(); G.render(); };
  if (Q.manual) return;
  let acc = 0, last = performance.now(); const speed = +Q.speed || 1;
  const loop = (now) => { acc += Math.min(250, now - last); last = now; while (acc >= 1000 / 60) { for (let i = 0; i < speed; i++) G.tick(); acc -= 1000 / 60; } G.render(); requestAnimationFrame(loop); };
  requestAnimationFrame(loop);
}
boot();
