/**
 * Band Wars — format-2 instrument catalog (16-bit / SNES–Genesis era).
 *
 * Track modules at audio/music/<id>.js export:
 *   song (default + named)  format-2 arrangement
 *   legacy                  8-bit reduction { bpm, loop, channels: {pulse1,pulse2,triangle,noise} }
 *
 * Format 2 song shape (backward compatible: still has bpm, loop, channels):
 *   {
 *     format: 2,
 *     bpm,
 *     loop: true | false | number,   // number = loop-start in sixteenths; false = one-shot
 *     instruments: { [voiceId]: instrumentId },
 *     channels:    { [voiceId]: [ [noteName|null, lengthInSixteenths], ... ] },
 *     mix?:        { [voiceId]: { volume: 0..1, pan: -1..1 } },
 *     echo?:       { delay: seconds, feedback: 0..1, mix: 0..1 }
 *   }
 *
 * Up to 8 voices per track (SNES-style). Every voice must have the same
 * total length in sixteenths.
 *
 * Pitched notes: 'C4', 'F#5', 'Bb3' (sharps or flats). null = rest.
 *
 * Drum / percussion voices (snare, bass-drum, cymbals, quad-toms):
 *   The first event field is an articulation or a pitch name, not a
 *   chromatic melody note (unless the instrument is pitched, e.g. toms).
 *   Length is the spacing until the next event. One-shots (hit, rim, flam,
 *   crash, choke, ride) trigger at the start and decay on their own;
 *   'roll' is a sustained buzz for the full length.
 *
 * Snare articulations:
 *   'hit'  — full snare stroke (also accept 'snare' as an alias)
 *   'rim'  — rimshot / cross-stick, short and clicky
 *   'roll' — buzz / multiple-bounce roll for the written length
 *   'flam' — grace note + main stroke
 *
 * Bass-drum articulations:
 *   'hit'  — standard bass-drum stroke (alias: 'kick')
 *   a pitch name (e.g. 'G1') — tuned stroke, frequency taken from the note
 *
 * Cymbals articulations:
 *   'hit' / 'crash' — crash cymbal, long decay
 *   'choke'         — muted / choked crash, short decay
 *   'ride'          — ride-cymbal tick
 *
 * Quad-toms:
 *   a pitch name (e.g. 'G3', 'C4') — the tom's pitch
 *   'hit' — default mid tom (approx. C3) if no pitch is given
 *
 * Engine notes:
 *   - `bpm` is authoritative. `loop` is true / false / a sixteenth index.
 *   - `instruments[voiceId]` chooses the patch; unknown ids should fall
 *     back to a generic muted saw.
 *   - `mix` is optional; default volume 0.75, pan 0 if omitted.
 *   - `echo` is an SNES-style hint: delay time, feedback, and wet mix.
 *     A low-pass inside the delay loop (around 3–5 kHz) is authentic.
 *   - Until the in-game synth speaks format 2, play the named `legacy`
 *     export (4 NES-style channels). `loadSong()` currently returns
 *     `m.song || m.default` (the format-2 object). Suggested adapter:
 *       const data = m.song || m.default;
 *       play(data.format === 2 && !supportsV2 ? m.legacy : data);
 *   - Song modules may import this file; the exported song object itself
 *     is plain data (safe to JSON-serialize in the single-file build).
 */

export const SNARE_ARTICULATIONS = {
  hit: 'Full snare stroke. Alias: snare.',
  rim: 'Rimshot or cross-stick. Short, high, little body.',
  roll: 'Buzz / multiple-bounce roll held for the written length.',
  flam: 'Grace stroke plus main hit, a few milliseconds apart.',
};

export const BASS_DRUM_ARTICULATIONS = {
  hit: 'Standard marching bass-drum stroke. Alias: kick.',
  /* pitch names are also legal, documented in the file header */
};

export const CYMBAL_ARTICULATIONS = {
  hit: 'Crash cymbal (long decay). Alias: crash.',
  crash: 'Same as hit.',
  choke: 'Muted or choked crash, short decay.',
  ride: 'Ride-cymbal bow tick.',
};

export const INSTRUMENTS = {
  'trumpet-lead': {
    description:
      'Bright solo trumpet for fanfares and fight-song hooks. Cuts the mix, slight lip scoop into notes.',
    recipe: {
      oscillators: [
        { type: 'sawtooth', detune: 0, gain: 0.7 },
        { type: 'square', detune: 8, gain: 0.35 },
      ],
      envelope: { attack: 0.008, decay: 0.1, sustain: 0.7, release: 0.08 },
      filter: { type: 'lowpass', frequency: 3200, q: 0.7, envAmount: 1800, envDecay: 0.14 },
      vibrato: { rate: 5.5, depthCents: 8, delay: 0.18 },
      pitchEnv: { startCents: 35, time: 0.03 },
    },
  },
  'brass-section': {
    description:
      'Massed horns / trumpet section. Detuned stacked saws for width; written pitch is the section’s unison note (not an auto-triad).',
    recipe: {
      oscillators: [
        { type: 'sawtooth', detune: 0, gain: 0.5 },
        { type: 'sawtooth', detune: -12, gain: 0.4 },
        { type: 'sawtooth', detune: 10, gain: 0.4 },
      ],
      envelope: { attack: 0.018, decay: 0.12, sustain: 0.8, release: 0.1 },
      filter: { type: 'lowpass', frequency: 2200, q: 0.6, envAmount: 1200, envDecay: 0.18 },
      vibrato: { rate: 4.8, depthCents: 4, delay: 0.25 },
    },
  },
  horn: {
    description:
      'Warm French-horn / mellophone countermelody. Softer attack, darker than trumpet, gentle vibrato.',
    recipe: {
      oscillators: [
        { type: 'sawtooth', detune: 0, gain: 0.55 },
        { type: 'sine', detune: 0, gain: 0.4 },
      ],
      envelope: { attack: 0.022, decay: 0.12, sustain: 0.75, release: 0.1 },
      filter: { type: 'lowpass', frequency: 1600, q: 0.7, envAmount: 800, envDecay: 0.2 },
      vibrato: { rate: 4.5, depthCents: 10, delay: 0.22 },
    },
  },
  trombone: {
    description:
      'Tenor trombone. Darker midrange, slower tongue, short portamento between notes to suggest the slide.',
    recipe: {
      oscillators: [
        { type: 'sawtooth', detune: 0, gain: 0.7 },
        { type: 'square', detune: -6, gain: 0.2 },
      ],
      envelope: { attack: 0.028, decay: 0.1, sustain: 0.8, release: 0.1 },
      filter: { type: 'lowpass', frequency: 1200, q: 0.6, envAmount: 700, envDecay: 0.16 },
      portamento: 0.04,
      vibrato: { rate: 4.2, depthCents: 6, delay: 0.28 },
    },
  },
  'tuba-bass': {
    description:
      'Tuba / sousaphone bassline. Sub-heavy sine plus a muted saw for growl.',
    recipe: {
      oscillators: [
        { type: 'sine', detune: 0, gain: 0.85 },
        { type: 'sine', detune: 0, octave: -1, gain: 0.3 },
        { type: 'sawtooth', detune: 0, gain: 0.18 },
      ],
      envelope: { attack: 0.008, decay: 0.08, sustain: 0.9, release: 0.06 },
      filter: { type: 'lowpass', frequency: 650, q: 0.5, envAmount: 300, envDecay: 0.1 },
    },
  },
  glockenspiel: {
    description:
      'Marching bells / glockenspiel. Struck-metal decay; doubles hooks an octave up. Rings past the written length.',
    recipe: {
      oscillators: [
        { type: 'sine', detune: 0, gain: 0.7 },
        { type: 'sine', detune: 0, ratio: 2, gain: 0.35 },
        { type: 'sine', detune: 0, ratio: 4, gain: 0.16 },
        { type: 'sine', detune: 0, ratio: 2.76, gain: 0.06 },
      ],
      envelope: { attack: 0.002, decay: 1.1, sustain: 0.0, release: 0.4 },
      struck: true,
      filter: { type: 'lowpass', frequency: 8000, q: 0.4 },
    },
  },
  snare: {
    description:
      'Marching snare. Articulations: hit (alias snare), rim, roll, flam. See SNARE_ARTICULATIONS.',
    recipe: {
      noise: { type: 'bandpass', frequency: 1800, q: 0.7, decay: 0.14 },
      body: { type: 'sine', frequency: 190, decay: 0.08 },
      articulations: {
        hit: { noiseDecay: 0.14, bodyGain: 0.25 },
        rim: { noiseDecay: 0.05, highpass: 2500, bodyGain: 0.05 },
        roll: { grainHz: 28, grainDecay: 0.05, bodyGain: 0 },
        flam: { graceMs: 18, graceGain: 0.55, then: 'hit' },
      },
    },
  },
  'bass-drum': {
    description:
      'Marching bass drum. Articulation: hit (alias kick), or a pitch name for a tuned stroke.',
    recipe: {
      oscillators: [{ type: 'sine', startFreq: 78, endFreq: 38, time: 0.12 }],
      click: { type: 'highpass-noise', frequency: 1200, decay: 0.02, gain: 0.25 },
      envelope: { attack: 0.002, decay: 0.16, sustain: 0, release: 0.05 },
    },
  },
  cymbals: {
    description:
      'Crash / ride / choke cymbals. Articulations: hit (alias crash), choke, ride. See CYMBAL_ARTICULATIONS. Crash rings past the written length.',
    recipe: {
      noise: { type: 'highpass', frequency: 6000, q: 0.5 },
      articulations: {
        hit: { decay: 1.4, gain: 0.7 },
        crash: { decay: 1.4, gain: 0.7 },
        choke: { decay: 0.12, gain: 0.6 },
        ride: { decay: 0.1, gain: 0.35, highpass: 7500, metallic: 0.2 },
      },
      struck: true,
    },
  },
  'quad-toms': {
    description:
      'Marching tenor / quad toms. Pitched by note name (G3, C4, E4, A4 from low to high). hit = default mid tom (~C3). Slight pitch drop on each stroke.',
    recipe: {
      oscillators: [
        { type: 'sine', gain: 0.7 },
        { type: 'triangle', gain: 0.3 },
      ],
      pitchEnv: { startCents: 200, time: 0.06 },
      noise: { type: 'bandpass', frequency: 800, decay: 0.05, gain: 0.2 },
      envelope: { attack: 0.003, decay: 0.22, sustain: 0, release: 0.08 },
      defaultPitch: 'C3',
    },
  },
  clarinet: {
    description:
      'Clarinet / bass-clarinet color. Odd-harmonic (square-like) tone, woody midrange, light vibrato.',
    recipe: {
      oscillators: [
        { type: 'square', detune: 0, gain: 0.7 },
        { type: 'sine', detune: 0, gain: 0.2 },
      ],
      envelope: { attack: 0.016, decay: 0.1, sustain: 0.8, release: 0.08 },
      filter: { type: 'lowpass', frequency: 2000, q: 0.85, envAmount: 600, envDecay: 0.15 },
      vibrato: { rate: 5.0, depthCents: 7, delay: 0.2 },
    },
  },
  flute: {
    description:
      'Flute / piccolo color. Mostly sine with a little breath noise and delayed vibrato.',
    recipe: {
      oscillators: [
        { type: 'sine', detune: 0, gain: 0.85 },
        { type: 'triangle', detune: 4, gain: 0.1 },
      ],
      breath: { gain: 0.04, highpass: 4000 },
      envelope: { attack: 0.02, decay: 0.08, sustain: 0.8, release: 0.1 },
      filter: { type: 'lowpass', frequency: 5000, q: 0.4 },
      vibrato: { rate: 5.2, depthCents: 14, delay: 0.25 },
    },
  },
  organ: {
    description:
      'Combo / carnival organ (fast-food / locker-room-adjacent color). Drawbar-ish 8′ + 4′ + 2′ + 2⅔′ squares, instant attack, light tremolo.',
    recipe: {
      oscillators: [
        { type: 'square', detune: 0, octave: 0, gain: 0.45 },
        { type: 'square', detune: 3, octave: 1, gain: 0.28 },
        { type: 'square', detune: -3, octave: 2, gain: 0.16 },
        { type: 'sine', detune: 0, ratio: 3, gain: 0.12 },
      ],
      envelope: { attack: 0.004, decay: 0.02, sustain: 0.9, release: 0.04 },
      tremolo: { rate: 4.5, depth: 0.12 },
      filter: { type: 'lowpass', frequency: 3500, q: 0.4 },
    },
  },
};

export const INSTRUMENT_IDS = Object.keys(INSTRUMENTS);

export default INSTRUMENTS;
