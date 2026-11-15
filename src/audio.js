// SNES-style Web Audio synth for JMHS MARCHING BAND ATTACK.
//  * up to 8 song voices, each with its own patch, volume, pan and echo send
//  * an echo bus (delay + low-pass in the feedback loop, like the S-DSP echo) and a small reverb
//  * data-driven patches: the composer's format-2 catalog (audio/music/instruments.js, INSTRUMENTS[id].recipe)
//    is merged over the built-in copies below, so the game still sounds right if that file is missing
//  * song formats:
//      legacy  { bpm, loop, channels: { pulse1, pulse2, triangle, noise } }           (8-bit, still supported)
//      format2 { format: 2, bpm, loop, instruments: {voice: id}, channels: {voice: events},
//                mix?: {voice: {volume, pan, echo}}, echo?: {delay, feedback, mix} }
//      a channel may also be an object { instrument|patch, volume, pan, echo, notes|events: [...] }
//      events: [note|null|[chord...], sixteenths, velocity?]; drum voices take articulations ('hit','rim','roll',...)
//  BPM is authoritative; loop is true | false | a sixteenth index.
const NOTE = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
export function noteFreq(name) {
  const m = /^([A-Ga-g])([#b]?)(-?\d+)$/.exec(name || ''); if (!m) return null;
  const s = NOTE[m[1].toUpperCase()] + (m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0);
  return 440 * 2 ** (((+m[3] + 1) * 12 + s - 69) / 12);
}
export const MAX_VOICES = 8;

// Built-in patch recipes (same schema as audio/music/instruments.js).
const O = (type, gain, extra = {}) => ({ type, gain, detune: 0, ...extra });
export const PATCHES = {
  'trumpet-lead': { oscillators: [O('sawtooth', 0.7), O('square', 0.35, { detune: 8 })], envelope: { attack: 0.008, decay: 0.1, sustain: 0.7, release: 0.08 },
    filter: { type: 'lowpass', frequency: 3200, q: 0.7, envAmount: 1800, envDecay: 0.14 }, vibrato: { rate: 5.5, depthCents: 8, delay: 0.18 }, pitchEnv: { startCents: 35, time: 0.03 } },
  'brass-section': { oscillators: [O('sawtooth', 0.5), O('sawtooth', 0.4, { detune: -12 }), O('sawtooth', 0.4, { detune: 10 })], envelope: { attack: 0.018, decay: 0.12, sustain: 0.8, release: 0.1 },
    filter: { type: 'lowpass', frequency: 2200, q: 0.6, envAmount: 1200, envDecay: 0.18 }, vibrato: { rate: 4.8, depthCents: 4, delay: 0.25 } },
  horn: { oscillators: [O('sawtooth', 0.55), O('sine', 0.4)], envelope: { attack: 0.022, decay: 0.12, sustain: 0.75, release: 0.1 },
    filter: { type: 'lowpass', frequency: 1600, q: 0.7, envAmount: 800, envDecay: 0.2 }, vibrato: { rate: 4.5, depthCents: 10, delay: 0.22 } },
  trombone: { oscillators: [O('sawtooth', 0.7), O('square', 0.2, { detune: -6 })], envelope: { attack: 0.028, decay: 0.1, sustain: 0.8, release: 0.1 },
    filter: { type: 'lowpass', frequency: 1200, q: 0.6, envAmount: 700, envDecay: 0.16 }, portamento: 0.04, vibrato: { rate: 4.2, depthCents: 6, delay: 0.28 } },
  'tuba-bass': { oscillators: [O('sine', 0.85), O('sine', 0.3, { octave: -1 }), O('sawtooth', 0.18)], envelope: { attack: 0.008, decay: 0.08, sustain: 0.9, release: 0.06 },
    filter: { type: 'lowpass', frequency: 650, q: 0.5, envAmount: 300, envDecay: 0.1 } },
  glockenspiel: { oscillators: [O('sine', 0.7), O('sine', 0.35, { ratio: 2 }), O('sine', 0.16, { ratio: 4 }), O('sine', 0.06, { ratio: 2.76 })],
    envelope: { attack: 0.002, decay: 1.1, sustain: 0, release: 0.4 }, struck: true, filter: { type: 'lowpass', frequency: 8000, q: 0.4 } },
  snare: { noise: { type: 'bandpass', frequency: 1800, q: 0.7, decay: 0.14 }, body: { type: 'sine', frequency: 190, decay: 0.08 },
    articulations: { hit: { noiseDecay: 0.14, bodyGain: 0.25 }, rim: { noiseDecay: 0.05, highpass: 2500, bodyGain: 0.05 }, roll: { grainHz: 28, grainDecay: 0.05, bodyGain: 0 }, flam: { graceMs: 18, graceGain: 0.55, then: 'hit' } } },
  'bass-drum': { oscillators: [{ type: 'sine', startFreq: 78, endFreq: 38, time: 0.12 }], click: { type: 'highpass-noise', frequency: 1200, decay: 0.02, gain: 0.25 },
    envelope: { attack: 0.002, decay: 0.16, sustain: 0, release: 0.05 } },
  cymbals: { noise: { type: 'highpass', frequency: 6000, q: 0.5 }, struck: true,
    articulations: { hit: { decay: 1.4, gain: 0.7 }, crash: { decay: 1.4, gain: 0.7 }, choke: { decay: 0.12, gain: 0.6 }, ride: { decay: 0.1, gain: 0.35, highpass: 7500, metallic: 0.2 } } },
  'quad-toms': { oscillators: [O('sine', 0.7), O('triangle', 0.3)], pitchEnv: { startCents: 200, time: 0.06 }, noise: { type: 'bandpass', frequency: 800, decay: 0.05, gain: 0.2 },
    envelope: { attack: 0.003, decay: 0.22, sustain: 0, release: 0.08 }, defaultPitch: 'C3' },
  clarinet: { oscillators: [O('square', 0.7), O('sine', 0.2)], envelope: { attack: 0.016, decay: 0.1, sustain: 0.8, release: 0.08 },
    filter: { type: 'lowpass', frequency: 2000, q: 0.85, envAmount: 600, envDecay: 0.15 }, vibrato: { rate: 5, depthCents: 7, delay: 0.2 } },
  flute: { oscillators: [O('sine', 0.85), O('triangle', 0.1, { detune: 4 })], breath: { gain: 0.04, highpass: 4000 }, envelope: { attack: 0.02, decay: 0.08, sustain: 0.8, release: 0.1 },
    filter: { type: 'lowpass', frequency: 5000, q: 0.4 }, vibrato: { rate: 5.2, depthCents: 14, delay: 0.25 } },
  organ: { oscillators: [O('square', 0.45), O('square', 0.28, { detune: 3, octave: 1 }), O('square', 0.16, { detune: -3, octave: 2 }), O('sine', 0.12, { ratio: 3 })],
    envelope: { attack: 0.004, decay: 0.02, sustain: 0.9, release: 0.04 }, tremolo: { rate: 4.5, depth: 0.12 }, filter: { type: 'lowpass', frequency: 3500, q: 0.4 } },
  'muted-saw': { oscillators: [O('sawtooth', 0.6)], envelope: { attack: 0.01, decay: 0.1, sustain: 0.7, release: 0.08 }, filter: { type: 'lowpass', frequency: 1400, q: 0.5 } },
};
// friendly aliases (brief names, camelCase) -> catalog ids
export const ALIASES = { brass: 'brass-section', brassSection: 'brass-section', trumpet: 'trumpet-lead', trumpetLead: 'trumpet-lead', lead: 'trumpet-lead',
  tuba: 'tuba-bass', tubaBass: 'tuba-bass', bass: 'tuba-bass', snareDrum: 'snare', bassDrum: 'bass-drum', kick: 'bass-drum', cymbal: 'cymbals', crash: 'cymbals',
  glock: 'glockenspiel', bells: 'glockenspiel', toms: 'quad-toms', quads: 'quad-toms', tenors: 'quad-toms', mellophone: 'horn', frenchHorn: 'horn', piccolo: 'flute' };
const KINDS = { snare: 'snare', 'bass-drum': 'bassdrum', cymbals: 'cymbal', 'quad-toms': 'tom', drumkit: 'kit' };
// legacy 4-channel songs -> 16-bit voices
const LEGACY = { pulse1: { instrument: 'trumpet-lead', volume: 0.62, pan: -0.2, echo: 0.35 }, pulse2: { instrument: 'brass-section', volume: 0.42, pan: 0.3, echo: 0.45 },
  triangle: { instrument: 'tuba-bass', volume: 0.9, pan: 0, echo: 0.1 }, noise: { instrument: 'drumkit', volume: 0.8, pan: 0.05, echo: 0.2 } };

class SnesAudio {
  constructor() { this.ctx = null; this.opts = { music: true, sfx: true, announcer: true }; this.song = null; this.timer = null; this.voices = new Set(); this.catalog = {}; this.voiceInfo = []; this.echoCfg = null; }
  setCatalog(cat) { // composer catalog: { id: { description, recipe } } or { id: recipe }
    if (!cat || typeof cat !== 'object') return; for (const [k, v] of Object.entries(cat)) if (v && typeof v === 'object') this.catalog[k] = v.recipe || v; }
  patch(id) { if (id && typeof id === 'object') return id.recipe || id; const k = ALIASES[id] || id; return this.catalog[k] || PATCHES[k] || (k === 'drumkit' ? {} : PATCHES['muted-saw']); }
  patchId(id) { return typeof id === 'string' ? (ALIASES[id] || id) : 'custom'; }
  ensure() {
    if (this.ctx) { if (this.ctx.state === 'suspended') this.ctx.resume(); return this.ctx; }
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null;
    const c = this.ctx = new AC();
    // master: gentle 32 kHz-style low-pass for that warm SNES top end
    this.master = c.createGain(); this.master.gain.value = 0.75;
    const tone = c.createBiquadFilter(); tone.type = 'lowpass'; tone.frequency.value = 12000; tone.Q.value = 0.3;
    const comp = c.createDynamicsCompressor(); comp.threshold.value = -14; comp.ratio.value = 4;
    this.master.connect(tone).connect(comp).connect(c.destination);
    this.musicBus = c.createGain(); this.musicBus.gain.value = this.opts.music ? 0.5 : 0; this.musicBus.connect(this.master);
    this.sfxBus = c.createGain(); this.sfxBus.gain.value = this.opts.sfx ? 0.75 : 0; this.sfxBus.connect(this.master);
    // echo bus: send -> delay <-> (lowpass -> feedback) ; delay -> wet. plus a short reverb tail
    this.echoIn = c.createGain(); this.delay = c.createDelay(1.5); this.echoLP = c.createBiquadFilter(); this.echoLP.type = 'lowpass'; this.echoLP.frequency.value = 4000;
    this.echoFB = c.createGain(); this.echoWet = c.createGain();
    this.echoIn.connect(this.delay); this.delay.connect(this.echoLP).connect(this.echoFB).connect(this.delay); this.echoLP.connect(this.echoWet).connect(this.master);
    this.verb = c.createConvolver(); this.verb.buffer = this.impulse(1.4); this.verbWet = c.createGain(); this.verbWet.gain.value = 0.22;
    this.echoIn.connect(this.verb).connect(this.verbWet).connect(this.master);
    this.musicSend = c.createGain(); this.musicSend.gain.value = this.opts.music ? 1 : 0; this.musicSend.connect(this.echoIn);
    this.sfxSend = c.createGain(); this.sfxSend.gain.value = this.opts.sfx ? 0.25 : 0; this.sfxBus.connect(this.sfxSend).connect(this.echoIn);
    this.setEcho({ delay: 0.24, feedback: 0.35, mix: 0.28 });
    const len = c.sampleRate; const nb = this.noiseBuf = c.createBuffer(1, len, c.sampleRate); const d = nb.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    if (this.pending) { const p = this.pending; this.pending = null; this.play(p.song, p.opts); }
    return c;
  }
  impulse(sec) { const c = this.ctx, n = Math.floor(c.sampleRate * sec), b = c.createBuffer(2, n, c.sampleRate);
    for (let ch = 0; ch < 2; ch++) { const d = b.getChannelData(ch); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 3); } return b; }
  setEcho(e = {}) { if (!this.ctx) return; const t = this.ctx.currentTime;
    this.echoCfg = { delay: Math.min(1.4, Math.max(0.02, e.delay ?? 0.24)), feedback: Math.min(0.85, Math.max(0, e.feedback ?? 0.35)), mix: Math.min(1, Math.max(0, e.mix ?? 0.28)) };
    this.delay.delayTime.setTargetAtTime(this.echoCfg.delay, t, 0.02); this.echoFB.gain.setTargetAtTime(this.echoCfg.feedback, t, 0.02); this.echoWet.gain.setTargetAtTime(this.echoCfg.mix, t, 0.02); }
  setOption(k, v) { this.opts[k] = v;
    if (this.ctx) { if (k === 'music') { this.musicBus.gain.value = v ? 0.5 : 0; this.musicSend.gain.value = v ? 1 : 0; } if (k === 'sfx') { this.sfxBus.gain.value = v ? 0.75 : 0; this.sfxSend.gain.value = v ? 0.25 : 0; } } }

  // ---------- song normalisation ----------
  voicesOf(song) {
    const v2 = song.format === 2 || !!song.instruments, out = [];
    for (const [id, ch] of Object.entries(song.channels || {})) {
      const obj = Array.isArray(ch) ? { notes: ch } : (ch || {}); const mix = (song.mix && song.mix[id]) || {};
      const leg = !v2 ? LEGACY[id] : null;
      const inst = obj.instrument || obj.patch || (song.instruments && song.instruments[id]) || (leg && leg.instrument) || (LEGACY[id] && LEGACY[id].instrument) || ALIASES[id] || id;
      out.push({ id, instrument: inst, notes: obj.notes || obj.events || [], volume: obj.volume ?? mix.volume ?? (leg ? leg.volume : 0.75), pan: obj.pan ?? mix.pan ?? (leg ? leg.pan : 0),
        echo: obj.echo ?? mix.echo ?? (leg ? leg.echo : 0.35) });
    }
    if (out.length > MAX_VOICES) { console.warn(`song has ${out.length} voices; SNES limit is ${MAX_VOICES}, extra voices muted`); out.length = MAX_VOICES; }
    return out;
  }
  // ---------- music ----------
  play(song, opts = {}) {
    if (!song) { this.stop(); return; }
    if (this.song === song && this.timer) return;
    if (!this.ctx || this.ctx.state !== 'running') { this.pending = { song, opts }; if (this.ctx) this.ctx.resume().then(() => { if (this.pending) { const p = this.pending; this.pending = null; this.play(p.song, p.opts); } }); return; }
    this.stop(); this.song = song; this.onEnd = opts.onEnd || null;
    const loop = opts.loop === false ? false : song.loop, step = 60 / song.bpm / 4, c = this.ctx;
    this.setEcho(song.echo || (song.format === 2 ? {} : { delay: 0.2, feedback: 0.3, mix: 0.22 }));
    const voices = this.voicesOf(song);
    this.voiceInfo = voices.map(v => ({ id: v.id, instrument: this.patchId(v.instrument), volume: v.volume, pan: v.pan, echo: v.echo }));
    const chans = voices.map(v => {
      const g = c.createGain(); g.gain.value = v.volume; const p = c.createStereoPanner(); p.pan.value = Math.max(-1, Math.min(1, v.pan));
      const send = c.createGain(); send.gain.value = v.echo; g.connect(p); p.connect(this.musicBus); p.connect(send); send.connect(this.musicSend);
      let pos = 0; const list = v.notes.map(e => { const o = { n: e[0], len: e[1], vel: e[2] ?? 1, at: pos }; pos += e[1]; return o; });
      const ls = loop === true ? 0 : typeof loop === 'number' ? loop : -1;
      return { ...v, out: g, nodes: [g, p, send], recipe: this.patch(v.instrument), kind: KINDS[this.patchId(v.instrument)] || null, list, total: pos,
        loopIdx: ls < 0 || !list.length ? -1 : Math.max(0, list.findIndex(o => o.at >= ls)), idx: 0, next: 0, last: null };
    });
    this.chans = chans;
    const t0 = c.currentTime + 0.08;
    const tick = () => {
      const horizon = c.currentTime + 0.25; let alive = false;
      for (const ch of chans) {
        while (ch.idx < ch.list.length || ch.loopIdx >= 0) {
          if (ch.idx >= ch.list.length) ch.idx = ch.loopIdx;
          const ev = ch.list[ch.idx], t = t0 + ch.next * step; if (t > horizon) break;
          if (ev.n) for (const n of [].concat(ev.n)) this.voiceNote(ch, n, t, ev.len * step, ev.vel);
          ch.next += ev.len; ch.idx++;
        }
        if (ch.idx < ch.list.length || ch.loopIdx >= 0) alive = true;
      }
      if (!alive) { const end = t0 + Math.max(0, ...chans.map(ch => ch.next)) * step; clearInterval(this.timer); this.timer = null;
        const cb = this.onEnd; setTimeout(() => { if (this.song === song) { this.song = null; cb && cb(); } }, Math.max(0, (end - c.currentTime) * 1000)); }
    };
    tick(); this.timer = setInterval(tick, 40);
  }
  stop() { if (this.timer) clearInterval(this.timer); this.timer = null; this.song = null; this.pending = null;
    for (const v of this.voices) { try { v.stop(); } catch {} } this.voices = new Set();
    if (this.chans) { const t = this.ctx ? this.ctx.currentTime : 0; for (const ch of this.chans) { try { ch.out.gain.setTargetAtTime(0, t, 0.02); } catch {} const ns = ch.nodes; setTimeout(() => ns.forEach(n => { try { n.disconnect(); } catch {} }), 400); } this.chans = null; }
    this.voiceInfo = []; }
  track(src) { this.voices.add(src); src.onended = () => this.voices.delete(src); }
  voiceNote(ch, n, t, dur, vel) {
    const k = ch.kind;
    if (k === 'kit') { const s = String(n).toLowerCase();
      if (s === 'kick') return this.bassDrum(this.patch('bass-drum'), null, t, ch.out, vel);
      if (s === 'snare') return this.snare(this.patch('snare'), 'hit', t, dur, ch.out, vel);
      if (s === 'hat') return this.cymbal(this.patch('cymbals'), 'choke', t, ch.out, vel * 0.5);
      return this.tom(this.patch('quad-toms'), n, t, ch.out, vel * 0.8); }
    if (k === 'snare') return this.snare(ch.recipe, n, t, dur, ch.out, vel);
    if (k === 'bassdrum') return this.bassDrum(ch.recipe, n, t, ch.out, vel);
    if (k === 'cymbal') return this.cymbal(ch.recipe, n, t, ch.out, vel);
    if (k === 'tom') return this.tom(ch.recipe, n, t, ch.out, vel);
    const f = noteFreq(n); if (!f) return;
    this.tonal(ch.recipe, f, t, dur, ch.out, vel, ch.last); ch.last = f;
  }
  // ---------- recipe interpreters ----------
  env(g, e, t, dur, vel, struck) {
    const a = e.attack ?? 0.01, d = e.decay ?? 0.1, s = e.sustain ?? 0.7, r = e.release ?? 0.08;
    g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vel, t + a);
    if (struck || s <= 0) { g.gain.setTargetAtTime(0.0001, t + a, Math.max(0.01, d / 3)); return t + a + d * 1.6 + 0.05; }
    const gate = Math.max(a + 0.01, dur * 0.9);
    g.gain.setTargetAtTime(vel * s, t + a, Math.max(0.005, d / 3)); g.gain.setValueAtTime(vel * s, t + gate); g.gain.setTargetAtTime(0.0001, t + gate, Math.max(0.005, r / 3));
    return t + gate + r * 2 + 0.02;
  }
  noise(t, end, out, filt, gain = 1) { const c = this.ctx, s = c.createBufferSource(); s.buffer = this.noiseBuf; s.loop = true;
    let node = s; if (filt) { const f = c.createBiquadFilter(); f.type = filt.type || 'bandpass'; f.frequency.value = filt.frequency || 1000; if (filt.q != null) f.Q.value = filt.q; node.connect(f); node = f; }
    const g = c.createGain(); g.gain.value = gain; node.connect(g).connect(out); s.start(t, Math.random() * 0.8); s.stop(end); this.track(s); return g; }
  tonal(R, f, t, dur, out, vel = 1, last = null) {
    const c = this.ctx, e = R.envelope || {}, g = c.createGain(); let end = this.env(g, e, t, dur, vel * 0.32, !!R.struck);
    let dest = g;
    if (R.tremolo) { const tg = c.createGain(), l = c.createOscillator(), lg = c.createGain(); l.frequency.value = R.tremolo.rate; lg.gain.value = R.tremolo.depth; tg.gain.value = 1 - R.tremolo.depth;
      l.connect(lg).connect(tg.gain); g.connect(tg); dest = tg; l.start(t); l.stop(end); this.track(l); }
    dest.connect(out);
    let input = g;
    if (R.filter) { const F = R.filter, fl = c.createBiquadFilter(); fl.type = F.type || 'lowpass'; if (F.q != null) fl.Q.value = F.q;
      const base = Math.min(F.frequency || 2000, 18000); if (F.envAmount) { fl.frequency.setValueAtTime(Math.min(18000, base + F.envAmount), t); fl.frequency.setTargetAtTime(base, t, Math.max(0.01, (F.envDecay || 0.15) / 3)); } else fl.frequency.value = base;
      fl.connect(g); input = fl; }
    let vib = null; if (R.vibrato) { const l = c.createOscillator(), lg = c.createGain(); l.frequency.value = R.vibrato.rate || 5; lg.gain.setValueAtTime(0, t);
      lg.gain.linearRampToValueAtTime(0, t + (R.vibrato.delay || 0)); lg.gain.linearRampToValueAtTime(R.vibrato.depthCents || 6, t + (R.vibrato.delay || 0) + 0.12); l.connect(lg); l.start(t); l.stop(end); this.track(l); vib = lg; }
    for (const os of R.oscillators || []) {
      const o = c.createOscillator(), og = c.createGain(); o.type = os.type || 'sawtooth'; og.gain.value = os.gain ?? 0.5;
      const mul = (os.ratio || 1) * 2 ** (os.octave || 0), ff = (os.startFreq ? os.startFreq : f) * mul;
      if (R.portamento && last) { o.frequency.setValueAtTime(last * mul, t); o.frequency.exponentialRampToValueAtTime(ff, t + R.portamento); } else o.frequency.setValueAtTime(ff, t);
      const dt = os.detune || 0; if (R.pitchEnv) { o.detune.setValueAtTime(dt + (R.pitchEnv.startCents || 0), t); o.detune.linearRampToValueAtTime(dt, t + (R.pitchEnv.time || 0.03)); } else o.detune.value = dt;
      if (vib) vib.connect(o.detune);
      o.connect(og).connect(input); o.start(t); o.stop(end); this.track(o);
    }
    if (R.breath) this.noise(t, end, input, { type: 'highpass', frequency: R.breath.highpass || 4000 }, R.breath.gain || 0.04);
    if (R.noise && R.noise.decay) { const ng = this.noise(t, t + R.noise.decay * 3, g, R.noise, R.noise.gain ?? 0.2); ng.gain.setTargetAtTime(0.0001, t, R.noise.decay / 3); }
    return end;
  }
  snare(R, art, t, dur, out, vel = 1) {
    const c = this.ctx, A = R.articulations || {}; let a = String(art || 'hit').toLowerCase(); if (a === 'snare' || noteFreq(art)) a = 'hit';
    const p = A[a] || A.hit || {}, N = R.noise || { type: 'bandpass', frequency: 1800, q: 0.7, decay: 0.14 }, B = R.body || { frequency: 190, decay: 0.08 };
    const stroke = (tt, gain, P) => { const d = P.noiseDecay ?? N.decay ?? 0.14, g = c.createGain(); g.gain.setValueAtTime(gain * 0.9, tt); g.gain.setTargetAtTime(0.0001, tt, d / 3); g.connect(out);
      const ng = this.noise(tt, tt + d * 3, g, { ...N, ...(P.highpass ? { type: 'highpass', frequency: P.highpass } : {}) }, 1);
      if ((P.bodyGain ?? 0.25) > 0) { const o = c.createOscillator(), og = c.createGain(); o.type = B.type || 'sine'; o.frequency.setValueAtTime(B.frequency * 1.3, tt); o.frequency.exponentialRampToValueAtTime(B.frequency, tt + 0.03);
        og.gain.setValueAtTime(gain * (P.bodyGain ?? 0.25) * 2.4, tt); og.gain.setTargetAtTime(0.0001, tt, (B.decay || 0.08) / 3); o.connect(og).connect(out); o.start(tt); o.stop(tt + (B.decay || 0.08) * 3); this.track(o); } return ng; };
    if (a === 'roll') { const hz = p.grainHz || 28, n = Math.max(2, Math.floor(dur * hz)); for (let i = 0; i < n; i++) stroke(t + i / hz, vel * (0.55 + 0.15 * (i % 2)), { noiseDecay: p.grainDecay || 0.05, bodyGain: p.bodyGain || 0 }); return; }
    if (a === 'flam') { stroke(t, vel * (p.graceGain || 0.55), A.hit || {}); stroke(t + (p.graceMs || 18) / 1000, vel, A[p.then || 'hit'] || {}); return; }
    stroke(t, vel, p);
  }
  bassDrum(R, art, t, out, vel = 1) {
    const c = this.ctx, os = (R.oscillators || [])[0] || { startFreq: 78, endFreq: 38, time: 0.12 }, e = R.envelope || { decay: 0.16 };
    const pf = art && noteFreq(art); const f0 = pf ? pf * 2 : os.startFreq || 78, f1 = pf ? pf : os.endFreq || 38;
    const o = c.createOscillator(), g = c.createGain(); o.type = os.type || 'sine'; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + (os.time || 0.12));
    const d = e.decay || 0.16; g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vel * 1.1, t + (e.attack || 0.002)); g.gain.setTargetAtTime(0.0001, t + 0.01, d / 2.5);
    o.connect(g).connect(out); o.start(t); o.stop(t + d * 3 + 0.05); this.track(o);
    if (R.click) { const cg = this.noise(t, t + 0.06, out, { type: 'highpass', frequency: R.click.frequency || 1200 }, (R.click.gain || 0.25) * vel); cg.gain.setTargetAtTime(0.0001, t, (R.click.decay || 0.02) / 3); }
  }
  cymbal(R, art, t, out, vel = 1) {
    const A = R.articulations || {}, p = A[String(art || 'hit').toLowerCase()] || A.hit || { decay: 1.2, gain: 0.6 }, N = R.noise || { type: 'highpass', frequency: 6000 };
    const g = this.noise(t, t + p.decay * 2.5, out, { ...N, ...(p.highpass ? { frequency: p.highpass } : {}) }, 1);
    g.gain.setValueAtTime(vel * (p.gain || 0.6) * 0.8, t); g.gain.setTargetAtTime(0.0001, t + 0.01, p.decay / 3);
    if (p.metallic) for (const fr of [3150, 4720, 6010]) { const o = this.ctx.createOscillator(), og = this.ctx.createGain(); o.type = 'square'; o.frequency.value = fr; og.gain.setValueAtTime(vel * p.metallic * 0.08, t); og.gain.setTargetAtTime(0.0001, t, p.decay / 3); o.connect(og).connect(out); o.start(t); o.stop(t + p.decay * 2); this.track(o); }
  }
  tom(R, art, t, out, vel = 1) { const f = noteFreq(art) || noteFreq(R.defaultPitch || 'C3'); return this.tonal({ ...R, struck: true }, f, t, 0.2, out, vel * 2.2); }

  // ---------- sfx (routed through the 16-bit patches) ----------
  sfxNote(id, n, dt = 0, dur = 0.15, vel = 1, last) { const c = this.ctx, t = c.currentTime + dt, R = this.patch(id), k = KINDS[this.patchId(id)];
    if (k === 'snare') return this.snare(R, n, t, dur, this.sfxBus, vel); if (k === 'bassdrum') return this.bassDrum(R, n, t, this.sfxBus, vel);
    if (k === 'cymbal') return this.cymbal(R, n, t, this.sfxBus, vel); if (k === 'tom') return this.tom(R, n, t, this.sfxBus, vel);
    const f = typeof n === 'number' ? n : noteFreq(n); if (f) this.tonal(R, f, t, dur, this.sfxBus, vel, last ? (typeof last === 'number' ? last : noteFreq(last)) : null); }
  sweep(f0, f1, dur, vol, type = 'square', dt = 0) { const c = this.ctx, t = c.currentTime + dt, o = c.createOscillator(), g = c.createGain(); o.type = type;
    o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur); g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.connect(g).connect(this.sfxBus); o.start(t); o.stop(t + dur + 0.02); }
  sfx(name) {
    if (!this.ctx || !this.opts.sfx) return; const N = (...a) => this.sfxNote(...a);
    switch (name) {
      case 'hit': N('snare', 'hit', 0, 0.1, 1); N('bass-drum', 'hit', 0, 0.1, 0.6); break;
      case 'heavy': N('bass-drum', 'hit', 0, 0.1, 1.2); N('snare', 'flam', 0, 0.1, 1); N('cymbals', 'choke', 0.01, 0.1, 0.7); break;
      case 'block': N('cymbals', 'ride', 0, 0.1, 1); N('snare', 'rim', 0, 0.05, 0.6); break;
      case 'whiff': { const t = this.ctx.currentTime, g = this.noise(t, t + 0.12, this.sfxBus, { type: 'bandpass', frequency: 1400, q: 1.2 }, 0.25); g.gain.setTargetAtTime(0.0001, t + 0.03, 0.03); break; }
      case 'jump': this.sweep(260, 520, 0.08, 0.06, 'triangle'); break;
      case 'land': N('bass-drum', 'hit', 0, 0.1, 0.5); break;
      case 'select': N('glockenspiel', 'E6', 0, 0.1, 0.8); break;
      case 'confirm': ['C5', 'E5', 'G5', 'C6'].forEach((n, i) => N('glockenspiel', n, i * 0.06, 0.2, 0.9)); N('brass-section', 'C5', 0.18, 0.25, 0.8); break;
      case 'ko': N('cymbals', 'crash', 0, 1, 1); N('bass-drum', 'hit', 0, 0.2, 1.3); N('trombone', 'C3', 0.02, 0.9, 1, 'G3'); break;
      case 'superflash': ['C5', 'E5', 'G5', 'C6'].forEach(n => N('brass-section', n, 0, 0.32, 0.55)); N('cymbals', 'crash', 0, 0.8, 0.7); N('snare', 'roll', 0, 0.3, 0.5); break;
      case 'bassdrum': N('bass-drum', 'hit', 0, 0.1, 1.2); N('bass-drum', 'G1', 0.09, 0.1, 1.1); N('tuba-bass', 'G1', 0, 0.35, 0.8); break;
      case 'snare': N('snare', 'roll', 0, 0.24, 1); N('snare', 'flam', 0.24, 0.1, 1); break;
      case 'bells': ['C6', 'E6', 'G6', 'C7'].forEach((n, i) => N('glockenspiel', n, i * 0.05, 0.4, 0.9)); break;
      case 'flute': N('flute', 'G6', 0, 0.3, 1); N('flute', 'A6', 0.12, 0.2, 0.7); break;
      case 'trumpet': N('trumpet-lead', 'Bb5', 0, 0.3, 1); N('trumpet-lead', 'F6', 0.1, 0.25, 0.8); break;
      case 'trombone': N('trombone', 'Bb3', 0, 0.35, 1); N('trombone', 'Bb4', 0.08, 0.3, 1, 'Bb3'); break;
      case 'tuba': N('tuba-bass', 'Bb1', 0, 0.55, 1.4); N('brass-section', 'F2', 0, 0.45, 0.5); break;
      case 'clarinet': N('clarinet', 'D6', 0, 0.15, 0.9); N('clarinet', 'A6', 0.1, 0.2, 0.7); break;
      case 'bassclarinet': N('clarinet', 'D2', 0, 0.7, 1.2); N('tuba-bass', 'D1', 0.03, 0.6, 0.9); break;
      default: N('glockenspiel', 'A5', 0, 0.1, 0.5);
    }
  }
  announce(text) {
    if (!this.opts.announcer) return;
    this.sfx('superflash');
    try { if (window.speechSynthesis) { const u = new SpeechSynthesisUtterance(text); u.rate = 0.9; u.pitch = 0.55; u.volume = 0.9; speechSynthesis.cancel(); speechSynthesis.speak(u); } } catch {}
  }
}
export const audio = new SnesAudio();
