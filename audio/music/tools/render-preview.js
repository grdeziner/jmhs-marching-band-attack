#!/usr/bin/env node
/**
 * Offline preview renderer for Band Wars chiptune song modules.
 *
 * Usage:
 *   node audio/music/tools/render-preview.js              # all tracks
 *   node audio/music/tools/render-preview.js football     # one track
 *
 * Reads ../<id>.js (default + named `song` export) and writes
 *   ../previews/<id>.wav
 *   ../previews/<id>.ogg   (if ffmpeg is on PATH)
 *
 * Renders 2 loops. If `song.loop` is a number (loop-start in sixteenths),
 * the intro plays once and the loop body plays twice.
 *
 * This file is a preview/tooling script only. The game uses its own
 * Web Audio synth; tracks do not depend on this player.
 */

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MUSIC_DIR = path.resolve(__dirname, '..');
const PREVIEW_DIR = path.join(MUSIC_DIR, 'previews');
const SAMPLE_RATE = 44100;
const MASTER_PEAK = 0.89; // ~-1 dBFS, no clipping
const LOOPS = 2;

const NOTE_OFFSETS = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };

function parseNote(name) {
  if (name == null) return null;
  if (typeof name !== 'string') {
    throw new Error(`Bad note: ${JSON.stringify(name)}`);
  }
  const drum = name.toLowerCase();
  if (drum === 'kick' || drum === 'snare' || drum === 'hat') {
    return { type: drum };
  }
  const m = name.match(/^([A-Ga-g])([#b]?)(-?\d+)$/);
  if (!m) throw new Error(`Unrecognized note name: ${JSON.stringify(name)}`);
  let semitone = NOTE_OFFSETS[m[1].toUpperCase()];
  if (m[2] === '#') semitone += 1;
  if (m[2] === 'b') semitone -= 1;
  const octave = Number(m[3]);
  const midi = (octave + 1) * 12 + semitone;
  const freq = 440 * 2 ** ((midi - 69) / 12);
  return { type: 'pitch', midi, freq, name };
}

function channelSteps(events) {
  return events.reduce((sum, ev) => {
    if (!Array.isArray(ev) || ev.length < 2 || typeof ev[1] !== 'number' || ev[1] <= 0) {
      throw new Error(`Bad event ${JSON.stringify(ev)}`);
    }
    return sum + ev[1];
  }, 0);
}

function expandEvents(channel, loopStart, loops) {
  const total = channelSteps(channel);
  const events = [];
  let cursor = 0;

  const apply = (startOffset, fromStep, toStep) => {
    let step = 0;
    for (const [note, len] of channel) {
      const end = step + len;
      if (end > fromStep && step < toStep) {
        const clipStart = Math.max(step, fromStep);
        const clipEnd = Math.min(end, toStep);
        if (note != null && clipStart < clipEnd) {
          events.push({
            note: parseNote(note),
            startStep: startOffset + (clipStart - fromStep),
            length: clipEnd - clipStart,
          });
        }
      }
      step = end;
    }
  };

  apply(0, 0, total);
  cursor = total;
  for (let i = 1; i < loops; i++) {
    apply(cursor, loopStart, total);
    cursor += total - loopStart;
  }
  return { events, totalSteps: cursor, patternSteps: total };
}

function stats(buf) {
  let peak = 0;
  let sumSq = 0;
  let clipped = 0;
  for (let i = 0; i < buf.length; i++) {
    const a = Math.abs(buf[i]);
    if (a > peak) peak = a;
    if (a > 1) clipped++;
    sumSq += buf[i] * buf[i];
  }
  const rms = Math.sqrt(sumSq / Math.max(1, buf.length));
  return { peak, rms, clipped, silent: peak < 1e-4 };
}

function writeWav(file, left, right, sampleRate) {
  const n = left.length;
  const dataSize = n * 4;
  const buf = Buffer.alloc(44 + dataSize);
  buf.write('RIFF', 0);
  buf.writeUInt32LE(36 + dataSize, 4);
  buf.write('WAVE', 8);
  buf.write('fmt ', 12);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(sampleRate, 24);
  buf.writeUInt32LE(sampleRate * 4, 28);
  buf.writeUInt16LE(4, 32);
  buf.writeUInt16LE(16, 34);
  buf.write('data', 36);
  buf.writeUInt32LE(dataSize, 40);
  let off = 44;
  for (let i = 0; i < n; i++) {
    const l = Math.max(-1, Math.min(1, left[i]));
    const r = Math.max(-1, Math.min(1, right[i]));
    buf.writeInt16LE(l < 0 ? Math.round(l * 32768) : Math.round(l * 32767), off);
    buf.writeInt16LE(r < 0 ? Math.round(r * 32768) : Math.round(r * 32767), off + 2);
    off += 4;
  }
  fs.writeFileSync(file, buf);
}

function fadeScale(i, start, end, attack, release) {
  const relPos = i - start;
  const len = end - start;
  if (relPos < attack) return Math.max(0, relPos) / attack;
  if (i > end - release) return Math.max(0, (end - i) / release);
  return 1;
}

function renderPulse(events, samples, stepSec, duty, gain) {
  const out = new Float64Array(samples);
  const attack = Math.floor(0.004 * SAMPLE_RATE);
  const release = Math.floor(0.008 * SAMPLE_RATE);
  const decay = Math.floor(0.08 * SAMPLE_RATE);
  const sustain = 0.72;
  let phase = 0;

  for (const ev of events) {
    if (ev.note.type !== 'pitch') continue;
    const start = Math.floor(ev.startStep * stepSec * SAMPLE_RATE);
    const end = Math.min(samples, Math.floor((ev.startStep + ev.length) * stepSec * SAMPLE_RATE));
    const freq = ev.note.freq;
    const inc = freq / SAMPLE_RATE;
    for (let i = start; i < end; i++) {
      const rel = i - start;
      let env = sustain;
      if (rel < attack) env = rel / attack;
      else if (rel < attack + decay) {
        const t = (rel - attack) / decay;
        env = 1 - t * (1 - sustain);
      }
      env *= fadeScale(i, start, end, attack, release);
      const s = phase < duty ? 1 : -1;
      out[i] += s * env * gain;
      phase += inc;
      if (phase >= 1) phase -= Math.floor(phase);
    }
  }
  return out;
}

function renderTriangle(events, samples, stepSec, gain) {
  // NES 32-step triangle (16 up, 16 down), no volume envelope besides click fades.
  const out = new Float64Array(samples);
  const fade = Math.floor(0.003 * SAMPLE_RATE);
  let phase = 0; // 0..31 in steps, stored as 0..1 of one cycle (32 steps)

  for (const ev of events) {
    if (ev.note.type !== 'pitch') continue;
    const start = Math.floor(ev.startStep * stepSec * SAMPLE_RATE);
    const end = Math.min(samples, Math.floor((ev.startStep + ev.length) * stepSec * SAMPLE_RATE));
    const inc = ev.note.freq / SAMPLE_RATE;
    for (let i = start; i < end; i++) {
      const step = (phase * 32) & 31;
      // NES triangle: 15,14,..0,0,1,..15  then repeats inverted? Classic:
      // sequence is 15 down to 0, then 0 up to 15. Mapped to -1..1.
      const level = step < 16 ? 15 - step : step - 16;
      const s = (level / 15) * 2 - 1;
      out[i] += s * fadeScale(i, start, end, fade, fade) * gain;
      phase += inc;
      if (phase >= 1) phase -= Math.floor(phase);
    }
  }
  return out;
}

function clockNoise(state, mode) {
  // 15-bit NES LFSR. mode=true is short (tap 6) metallic; false is long (tap 1).
  const bit = (state.lfsr & 1) ^ ((state.lfsr >> (mode ? 6 : 1)) & 1);
  state.lfsr = (state.lfsr >> 1) | (bit << 14);
  return state.lfsr & 1 ? 1 : -1;
}

function renderNoise(events, samples, stepSec, gain) {
  const out = new Float64Array(samples);
  const state = { lfsr: 1 };

  for (const ev of events) {
    const start = Math.floor(ev.startStep * stepSec * SAMPLE_RATE);
    if (start >= samples) continue;

    const kind = ev.note.type === 'pitch' ? 'pitched' : ev.note.type;
    let duration;
    let baseGain;
    if (kind === 'kick') {
      duration = Math.floor(0.14 * SAMPLE_RATE);
      baseGain = 1.0;
    } else if (kind === 'snare') {
      duration = Math.floor(0.16 * SAMPLE_RATE);
      baseGain = 0.85;
    } else if (kind === 'hat') {
      duration = Math.floor(0.05 * SAMPLE_RATE);
      baseGain = 0.45;
    } else {
      // pitched percussion: mid noise, decay scales a bit with length
      duration = Math.floor(Math.max(0.08, ev.length * stepSec) * SAMPLE_RATE);
      baseGain = 0.7;
    }
    const end = Math.min(samples, start + duration);

    if (kind === 'kick') {
      const startFreq = ev.note.type === 'pitch' ? ev.note.freq : 78;
      for (let i = start; i < end; i++) {
        const t = (i - start) / SAMPLE_RATE;
        const env = Math.exp(-t * 22);
        const freq = startFreq * Math.exp(-t * 12);
        const thump = Math.sin(2 * Math.PI * freq * t + (1 - env) * 0.4);
        // Low, slowly clocked noise for body
        if ((i - start) % 8 === 0) state.kickN = clockNoise(state, false);
        const noise = (state.kickN || 0) * Math.exp(-t * 28) * 0.35;
        out[i] += (thump * 0.9 + noise) * env * baseGain * gain;
      }
    } else if (kind === 'snare') {
      let lp = 0;
      const clockEvery = 2;
      for (let i = start; i < end; i++) {
        const t = (i - start) / SAMPLE_RATE;
        const snap = Math.exp(-t * 80);
        const body = Math.exp(-t * 16);
        if ((i - start) % clockEvery === 0) state.snareN = clockNoise(state, true);
        const n = state.snareN || 0;
        lp += (n - lp) * 0.55;
        // brief low sine for the "head"
        const head = Math.sin(2 * Math.PI * 180 * t) * snap * 0.25;
        out[i] += (lp * body * 0.85 + n * snap * 0.5 + head) * baseGain * gain;
      }
    } else if (kind === 'hat') {
      for (let i = start; i < end; i++) {
        const t = (i - start) / SAMPLE_RATE;
        const env = Math.exp(-t * 70);
        state.hatN = clockNoise(state, false);
        // crude high-pass: current - previous, approximated by using raw LFSR
        // (already bright) plus a little differentiation
        const n = state.hatN || 0;
        const hp = n - (state.hatPrev || 0);
        state.hatPrev = n;
        out[i] += hp * env * baseGain * gain;
      }
    } else {
      const clockEvery = ev.note.freq ? Math.max(1, Math.round(SAMPLE_RATE / (ev.note.freq * 8))) : 3;
      for (let i = start; i < end; i++) {
        const t = (i - start) / SAMPLE_RATE;
        const env = Math.exp(-t * 18);
        if ((i - start) % clockEvery === 0) state.pitN = clockNoise(state, true);
        out[i] += (state.pitN || 0) * env * baseGain * gain;
      }
    }
  }
  return out;
}

function equalPowerPan(mono, pan) {
  // pan: -1 left .. +1 right
  const angle = ((pan + 1) / 2) * (Math.PI / 2);
  const leftGain = Math.cos(angle);
  const rightGain = Math.sin(angle);
  const left = new Float64Array(mono.length);
  const right = new Float64Array(mono.length);
  for (let i = 0; i < mono.length; i++) {
    left[i] = mono[i] * leftGain;
    right[i] = mono[i] * rightGain;
  }
  return { left, right };
}

function mixTo(destL, destR, srcL, srcR, gain) {
  for (let i = 0; i < destL.length; i++) {
    destL[i] += srcL[i] * gain;
    destR[i] += srcR[i] * gain;
  }
}

function ffmpegAvailable() {
  try {
    execFileSync('ffmpeg', ['-version'], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function encodeOgg(wavPath, oggPath) {
  execFileSync(
    'ffmpeg',
    ['-y', '-i', wavPath, '-c:a', 'libvorbis', '-q:a', '6', oggPath],
    { stdio: 'ignore' },
  );
}

async function renderTrack(id) {
  const modPath = path.join(MUSIC_DIR, `${id}.js`);
  if (!fs.existsSync(modPath)) {
    throw new Error(`Missing song module: ${modPath}`);
  }
  const mod = await import(pathToFileURL(modPath).href);
  const song = mod.song ?? mod.default;
  if (!song || typeof song.bpm !== 'number' || !song.channels) {
    throw new Error(`${id}: module does not export a song object`);
  }

  const { pulse1, pulse2, triangle, noise } = song.channels;
  if (!pulse1 || !pulse2 || !triangle || !noise) {
    throw new Error(`${id}: channels must include pulse1, pulse2, triangle, noise`);
  }

  const lengths = {
    pulse1: channelSteps(pulse1),
    pulse2: channelSteps(pulse2),
    triangle: channelSteps(triangle),
    noise: channelSteps(noise),
  };
  const patternSteps = lengths.pulse1;
  for (const [ch, n] of Object.entries(lengths)) {
    if (n !== patternSteps) {
      throw new Error(`${id}: channel ${ch} is ${n} sixteenths, expected ${patternSteps}`);
    }
  }

  const loopStart = song.loop === true || song.loop == null ? 0 : song.loop;
  if (!Number.isInteger(loopStart) || loopStart < 0 || loopStart >= patternSteps) {
    throw new Error(`${id}: loop must be true or a start in sixteenths within the pattern (got ${song.loop})`);
  }

  const stepSec = 60 / song.bpm / 4;
  const expanded = expandEvents(pulse1, loopStart, LOOPS);
  const totalSteps = expanded.totalSteps;
  const durationSec = totalSteps * stepSec;
  const samples = Math.max(1, Math.round(durationSec * SAMPLE_RATE));

  const p1 = renderPulse(expandEvents(pulse1, loopStart, LOOPS).events, samples, stepSec, 0.5, 0.22);
  const p2 = renderPulse(expandEvents(pulse2, loopStart, LOOPS).events, samples, stepSec, 0.25, 0.18);
  const tri = renderTriangle(expandEvents(triangle, loopStart, LOOPS).events, samples, stepSec, 0.26);
  const noi = renderNoise(expandEvents(noise, loopStart, LOOPS).events, samples, stepSec, 0.32);

  const chStats = {
    pulse1: stats(p1),
    pulse2: stats(p2),
    triangle: stats(tri),
    noise: stats(noi),
  };

  const p1s = equalPowerPan(p1, -0.28);
  const p2s = equalPowerPan(p2, 0.28);
  const tris = equalPowerPan(tri, 0);
  const nois = equalPowerPan(noi, 0);

  const left = new Float64Array(samples);
  const right = new Float64Array(samples);
  mixTo(left, right, p1s.left, p1s.right, 1);
  mixTo(left, right, p2s.left, p2s.right, 1);
  mixTo(left, right, tris.left, tris.right, 1);
  mixTo(left, right, nois.left, nois.right, 1);

  const mixPeak = Math.max(stats(left).peak, stats(right).peak);
  const scale = mixPeak > 0 ? MASTER_PEAK / mixPeak : 1;
  for (let i = 0; i < samples; i++) {
    left[i] *= scale;
    right[i] *= scale;
  }

  const preScaleClipped = stats(left).clipped + stats(right).clipped; // after scale, should be 0
  // Recompute after scale
  const leftS = stats(left);
  const rightS = stats(right);
  const finalPeak = Math.max(leftS.peak, rightS.peak);
  const clipped = leftS.clipped + rightS.clipped;

  fs.mkdirSync(PREVIEW_DIR, { recursive: true });
  const wavPath = path.join(PREVIEW_DIR, `${id}.wav`);
  writeWav(wavPath, left, right, SAMPLE_RATE);

  let oggPath = null;
  let oggError = null;
  if (ffmpegAvailable()) {
    oggPath = path.join(PREVIEW_DIR, `${id}.ogg`);
    try {
      encodeOgg(wavPath, oggPath);
    } catch (err) {
      oggError = err.message || String(err);
      oggPath = null;
    }
  }

  const silentChannels = Object.entries(chStats)
    .filter(([, s]) => s.silent)
    .map(([name]) => name);

  const report = {
    id,
    bpm: song.bpm,
    loop: song.loop,
    patternSixteenths: patternSteps,
    patternBars: patternSteps / 16,
    patternSeconds: patternSteps * stepSec,
    loopBodySixteenths: patternSteps - loopStart,
    loopBodySeconds: (patternSteps - loopStart) * stepSec,
    introSixteenths: loopStart,
    renderedLoops: LOOPS,
    durationSec,
    samples,
    sampleRate: SAMPLE_RATE,
    peak: finalPeak,
    scaleApplied: scale,
    mixPeakBeforeScale: mixPeak,
    clippedSamples: clipped,
    preScaleClipped,
    channels: chStats,
    silentChannels,
    wavPath,
    oggPath,
    oggError,
    ok: clipped === 0 && silentChannels.length === 0 && durationSec > 1,
  };
  return report;
}

function printReport(r) {
  const fmt = (n, d = 3) => Number(n).toFixed(d);
  console.log(`\n=== ${r.id} ===`);
  console.log(`  bpm=${r.bpm}  loop=${r.loop}  pattern=${r.patternSixteenths} steps (${r.patternBars} bars, ${fmt(r.patternSeconds, 2)}s)`);
  if (r.introSixteenths) {
    console.log(`  intro=${r.introSixteenths} steps  loop body=${r.loopBodySixteenths} steps (${fmt(r.loopBodySeconds, 2)}s)`);
  }
  console.log(`  preview: ${r.renderedLoops} loops, duration=${fmt(r.durationSec, 3)}s  (${r.samples} samples @ ${r.sampleRate} Hz)`);
  console.log(`  peak=${fmt(r.peak, 4)}  scale=${fmt(r.scaleApplied, 3)}  (pre-scale peak ${fmt(r.mixPeakBeforeScale, 4)})  clipped=${r.clippedSamples}`);
  for (const [name, s] of Object.entries(r.channels)) {
    console.log(`  ${name.padEnd(9)} peak=${fmt(s.peak, 4)}  rms=${fmt(s.rms, 4)}  ${s.silent ? 'SILENT' : 'ok'}`);
  }
  console.log(`  wav: ${r.wavPath}`);
  if (r.oggPath) console.log(`  ogg: ${r.oggPath}`);
  else if (r.oggError) console.log(`  ogg: failed (${r.oggError})`);
  else console.log('  ogg: skipped (ffmpeg not found)');
  console.log(`  status: ${r.ok ? 'PASS' : 'FAIL'}${r.silentChannels.length ? ' silent=' + r.silentChannels.join(',') : ''}${r.clippedSamples ? ' CLIPPING' : ''}`);
}

const DEFAULT_IDS = ['football', 'lockerroom', 'fastfood'];

const ids = process.argv.slice(2).filter((a) => !a.startsWith('-'));
const targets = ids.length ? ids : DEFAULT_IDS;

const reports = [];
for (const id of targets) {
  const r = await renderTrack(id);
  printReport(r);
  reports.push(r);
}

const failed = reports.filter((r) => !r.ok);
if (failed.length) {
  console.error(`\n${failed.length} track(s) failed listen-check.`);
  process.exit(1);
}
console.log(`\nAll ${reports.length} track(s) passed listen-check.`);
