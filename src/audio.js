// Web Audio chip synth: plays the song modules in audio/music/*.js (2 pulse, triangle, noise)
// plus synthesized SFX and announcer callouts. Song BPM is authoritative.
const NOTE = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
export function noteFreq(name) {
  const m = /^([A-Ga-g])([#b]?)(-?\d+)$/.exec(name || ''); if (!m) return null;
  let s = NOTE[m[1].toUpperCase()] + (m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0);
  return 440 * 2 ** (((+m[3] + 1) * 12 + s - 69) / 12);
}

class ChipAudio {
  constructor() { this.ctx = null; this.opts = { music: true, sfx: true, announcer: true }; this.song = null; this.timer = null; }
  ensure() {
    if (this.ctx) { if (this.ctx.state === 'suspended') this.ctx.resume(); return this.ctx; }
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null;
    const c = this.ctx = new AC();
    this.master = c.createGain(); this.master.gain.value = 0.7; this.master.connect(c.destination);
    this.musicBus = c.createGain(); this.musicBus.gain.value = this.opts.music ? 0.32 : 0; this.musicBus.connect(this.master);
    this.sfxBus = c.createGain(); this.sfxBus.gain.value = this.opts.sfx ? 0.55 : 0; this.sfxBus.connect(this.master);
    const len = c.sampleRate; const nb = this.noiseBuf = c.createBuffer(1, len, c.sampleRate); const d = nb.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    this.waves = { p50: this.pulse(0.5), p25: this.pulse(0.25), p125: this.pulse(0.125) };
    if (this.pending) { const p = this.pending; this.pending = null; this.play(p.song, p.opts); }
    return c;
  }
  pulse(duty) { const n = 64, re = new Float32Array(n), im = new Float32Array(n);
    for (let k = 1; k < n; k++) im[k] = (2 / (k * Math.PI)) * Math.sin(k * Math.PI * duty) * 1; // fourier of pulse
    for (let k = 1; k < n; k++) { re[k] = im[k]; im[k] = 0; }
    return this.ctx.createPeriodicWave(re, im); }
  setOption(k, v) { this.opts[k] = v;
    if (this.ctx) { if (k === 'music') this.musicBus.gain.value = v ? 0.32 : 0; if (k === 'sfx') this.sfxBus.gain.value = v ? 0.55 : 0; } }

  // ---------- music ----------
  play(song, opts = {}) {
    if (!song) { this.stop(); return; }
    if (this.song === song && this.timer) return;
    if (!this.ctx || this.ctx.state !== 'running') { this.pending = { song, opts }; if (this.ctx) this.ctx.resume().then(() => { if (this.pending) { const p = this.pending; this.pending = null; this.play(p.song, p.opts); } }); return; }
    this.stop(); this.song = song; this.onEnd = opts.onEnd || null;
    const loop = opts.loop === false ? false : song.loop;
    const step = 60 / song.bpm / 4;
    const chans = Object.entries(song.channels || {}).map(([name, evs]) => {
      let pos = 0; const list = evs.map(e => { const o = { n: e[0], len: e[1], at: pos }; pos += e[1]; return o; });
      const ls = loop === true ? 0 : typeof loop === 'number' ? loop : -1;
      return { name, list, total: pos, loopIdx: ls < 0 ? -1 : Math.max(0, list.findIndex(o => o.at >= ls)), idx: 0, next: 0 };
    });
    const t0 = this.ctx.currentTime + 0.08; this.voices = new Set();
    const tick = () => {
      const horizon = this.ctx.currentTime + 0.25; let alive = false;
      for (const ch of chans) {
        while (ch.idx < ch.list.length || ch.loopIdx >= 0) {
          if (ch.idx >= ch.list.length) ch.idx = ch.loopIdx;
          const ev = ch.list[ch.idx], t = t0 + ch.next * step; if (t > horizon) break;
          if (ev.n) this.note(ch.name, ev.n, t, ev.len * step); ch.next += ev.len; ch.idx++;
        }
        if (ch.idx < ch.list.length || ch.loopIdx >= 0) alive = true;
      }
      if (!alive) { const end = t0 + Math.max(...chans.map(c => c.next)) * step; clearInterval(this.timer); this.timer = null;
        const cb = this.onEnd; setTimeout(() => { if (this.song === song) { this.song = null; cb && cb(); } }, Math.max(0, (end - this.ctx.currentTime) * 1000)); }
    };
    tick(); this.timer = setInterval(tick, 40);
  }
  stop() { if (this.timer) clearInterval(this.timer); this.timer = null; this.song = null; this.pending = null;
    if (this.voices) for (const v of this.voices) { try { v.stop(); } catch {} } this.voices = new Set(); }
  track(src) { this.voices.add(src); src.onended = () => this.voices.delete(src); }
  note(ch, n, t, dur) {
    const c = this.ctx;
    if (ch === 'noise') return this.drum(n, t, this.musicBus, true);
    const f = noteFreq(n); if (!f) return;
    const o = c.createOscillator(), g = c.createGain();
    if (ch === 'triangle') { o.type = 'triangle'; } else o.setPeriodicWave(ch === 'pulse1' ? this.waves.p50 : this.waves.p25);
    o.frequency.value = f;
    const vol = ch === 'triangle' ? 0.55 : ch === 'pulse1' ? 0.22 : 0.15, gate = Math.max(0.04, dur * 0.88);
    g.gain.setValueAtTime(vol, t); g.gain.setValueAtTime(vol * 0.8, t + Math.min(0.05, gate)); g.gain.linearRampToValueAtTime(0.0001, t + gate);
    o.connect(g).connect(this.musicBus); o.start(t); o.stop(t + gate + 0.02); this.track(o);
  }
  drum(n, t, bus, track) {
    const c = this.ctx; const k = String(n).toLowerCase();
    if (k === 'kick') { const o = c.createOscillator(), g = c.createGain(); o.frequency.setValueAtTime(150, t); o.frequency.exponentialRampToValueAtTime(40, t + 0.12);
      g.gain.setValueAtTime(0.9, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.16); o.connect(g).connect(bus); o.start(t); o.stop(t + 0.18); if (track) this.track(o); return; }
    const s = c.createBufferSource(); s.buffer = this.noiseBuf; const f = c.createBiquadFilter(), g = c.createGain();
    let len = 0.12, vol = 0.5;
    if (k === 'snare') { f.type = 'bandpass'; f.frequency.value = 1800; f.Q.value = 0.7; len = 0.12; vol = 0.6; }
    else if (k === 'hat') { f.type = 'highpass'; f.frequency.value = 7000; len = 0.04; vol = 0.35; }
    else { const fr = noteFreq(n) || 1000; f.type = 'bandpass'; f.frequency.value = fr * 4; f.Q.value = 2; len = 0.08; vol = 0.5; }
    g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + len);
    s.connect(f).connect(g).connect(bus); s.start(t, Math.random() * 0.5); s.stop(t + len + 0.02); if (track) this.track(s);
  }

  // ---------- sfx ----------
  tone(type, f0, f1, dur, vol = 0.3, t = 0, wave) {
    const c = this.ctx; if (!c) return; const at = c.currentTime + t; const o = c.createOscillator(), g = c.createGain();
    if (wave) o.setPeriodicWave(wave); else o.type = type;
    o.frequency.setValueAtTime(f0, at); if (f1 !== f0) o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), at + dur);
    g.gain.setValueAtTime(vol, at); g.gain.exponentialRampToValueAtTime(0.001, at + dur);
    o.connect(g).connect(this.sfxBus); o.start(at); o.stop(at + dur + 0.02);
  }
  vib(f, dur, vol, wave, t = 0, depth = 6) { const c = this.ctx; const at = c.currentTime + t; const o = c.createOscillator(), g = c.createGain(), l = c.createOscillator(), lg = c.createGain();
    if (typeof wave === 'string') o.type = wave; else o.setPeriodicWave(wave); o.frequency.value = f; l.frequency.value = 7; lg.gain.value = depth;
    l.connect(lg).connect(o.frequency); g.gain.setValueAtTime(0.0001, at); g.gain.linearRampToValueAtTime(vol, at + 0.03); g.gain.setValueAtTime(vol, at + dur * 0.7); g.gain.exponentialRampToValueAtTime(0.001, at + dur);
    o.connect(g).connect(this.sfxBus); o.start(at); l.start(at); o.stop(at + dur + 0.02); l.stop(at + dur + 0.02); }
  sfx(name) {
    if (!this.ctx || !this.opts.sfx) return; const W = this.waves, b = this.sfxBus, now = this.ctx.currentTime;
    switch (name) {
      case 'hit': this.drum('snare', now, b); this.tone('square', 220, 80, 0.08, 0.25); break;
      case 'heavy': this.drum('kick', now, b); this.drum('snare', now, b); this.tone('sawtooth', 160, 50, 0.18, 0.3); break;
      case 'block': this.drum('hat', now, b); this.tone('square', 900, 700, 0.05, 0.12); break;
      case 'whiff': this.tone('triangle', 500, 900, 0.06, 0.1); break;
      case 'jump': this.tone('square', 300, 600, 0.08, 0.08, 0, W.p25); break;
      case 'land': this.drum('kick', now, b); break;
      case 'select': this.tone('square', 880, 880, 0.05, 0.15, 0, W.p25); break;
      case 'confirm': [523, 659, 784, 1047].forEach((f, i) => this.tone('square', f, f, 0.09, 0.15, i * 0.06, W.p50)); break;
      case 'ko': this.tone('sawtooth', 400, 40, 1.2, 0.35); this.drum('kick', now, b); break;
      case 'superflash': [392, 523, 659, 784, 1047].forEach((f, i) => this.tone('square', f, f, 0.1, 0.12, i * 0.04, W.p125)); break;
      case 'bassdrum': for (let i = 0; i < 2; i++) this.drum('kick', now + i * 0.09, b); this.tone('sine', 90, 45, 0.4, 0.5); break;
      case 'snare': for (let i = 0; i < 6; i++) this.drum('snare', now + i * 0.04, b); break;
      case 'bells': [1047, 1319, 1568, 2093].forEach((f, i) => this.tone('sine', f, f, 0.5, 0.18, i * 0.05)); break;
      case 'flute': this.vib(1568, 0.35, 0.18, 'sine', 0, 18); this.vib(1760, 0.2, 0.1, 'sine', 0.1, 30); break;
      case 'trumpet': this.vib(932, 0.35, 0.16, W.p25, 0, 8); this.vib(1397, 0.25, 0.1, W.p25, 0.08, 8); break;
      case 'trombone': this.tone('sawtooth', 233, 466, 0.35, 0.18); break;
      case 'tuba': this.vib(58, 0.6, 0.45, 'sawtooth', 0, 2); this.tone('square', 87, 44, 0.5, 0.2); break;
      case 'clarinet': this.tone('square', 1200, 2600, 0.15, 0.15, 0, W.p50); this.vib(1175, 0.2, 0.08, W.p50, 0.12, 20); break;
      case 'bassclarinet': this.vib(73, 0.8, 0.4, W.p50, 0, 3); this.vib(110, 0.6, 0.15, W.p50, 0.05, 2); break;
      default: this.tone('square', 440, 440, 0.05, 0.1);
    }
  }
  announce(text) {
    if (!this.opts.announcer) return;
    this.sfx('superflash');
    try { if (window.speechSynthesis) { const u = new SpeechSynthesisUtterance(text); u.rate = 0.9; u.pitch = 0.55; u.volume = 0.9; speechSynthesis.cancel(); speechSynthesis.speak(u); } } catch {}
  }
}
export const audio = new ChipAudio();
