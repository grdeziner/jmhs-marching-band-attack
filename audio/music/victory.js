/**
 * Band Wars — one-shot victory fanfare
 * id: victory
 *
 * Short heroic closer in the football-field key, ending on a “ta-da” I chord.
 * Key: Bb major. Tempo: 160 BPM. 4/4.
 * `loop: false`. 4 bars = 64 sixteenths = 6.00s (plus a cymbal/echo tail at render).
 *
 * Also exports `legacy` (4-channel 8-bit reduction). See instruments.js.
 */


function bars(label, ...measures) {
  const notes = [];
  measures.forEach((m, i) => {
    const sum = m.reduce((acc, ev) => acc + ev[1], 0);
    if (sum !== 16) throw new Error(label + ' bar ' + (i + 1) + ' is ' + sum + ' sixteenths, expected 16');
    notes.push(...m);
  });
  return notes;
}

export const song = {
  format: 2,
  bpm: 160,
  loop: false,
  instruments: {
    lead: "trumpet-lead",
    brass: "brass-section",
    horn: "horn",
    bass: "tuba-bass",
    glock: "glockenspiel",
    snare: "snare",
    kick: "bass-drum",
    cymbals: "cymbals"
  },
  mix: {
    lead: { volume: 0.9, pan: -0.08 },
    brass: { volume: 0.58, pan: 0.22 },
    horn: { volume: 0.64, pan: -0.34 },
    bass: { volume: 0.86, pan: 0.0 },
    glock: { volume: 0.45, pan: 0.14 },
    snare: { volume: 0.72, pan: 0.04 },
    kick: { volume: 0.9, pan: 0.0 },
    cymbals: { volume: 0.5, pan: -0.16 }
  },
  echo: { delay: 0.18, feedback: 0.28, mix: 0.22 },
  channels: {
    lead: bars('victory.lead',
        [["F4", 2], ["Bb4", 2], ["D5", 2], ["F5", 2], ["Bb5", 8]],  // 1
        [["A5", 2], ["Bb5", 2], ["C6", 2], ["D6", 2], ["Bb5", 4], ["F5", 4]],  // 2
        [["Eb5", 2], ["F5", 2], ["G5", 2], ["A5", 2], ["Bb5", 8]],  // 3
        [["Bb4", 2], [null, 2], ["F4", 2], [null, 2], ["Bb5", 8]],  // 4
    ),
    brass: bars('victory.brass',
        [["Bb3", 8], ["F3", 8]],  // 1
        [["F3", 8], ["Bb3", 8]],  // 2
        [["Eb3", 8], ["Bb3", 8]],  // 3
        [["F3", 4], ["F3", 4], ["Bb3", 8]],  // 4
    ),
    horn: bars('victory.horn',
        [["D4", 2], ["F4", 2], ["Bb4", 2], ["D5", 2], ["F5", 8]],  // 1
        [["F5", 2], ["G5", 2], ["A5", 2], ["Bb5", 2], ["F5", 4], ["D5", 4]],  // 2
        [["C5", 2], ["D5", 2], ["Eb5", 2], ["F5", 2], ["G5", 8]],  // 3
        [["D4", 2], [null, 2], ["C4", 2], [null, 2], ["F5", 8]],  // 4
    ),
    bass: bars('victory.bass',
        [["Bb2", 4], ["F2", 4], ["Bb2", 8]],  // 1
        [["F2", 8], ["Bb2", 8]],  // 2
        [["Eb2", 8], ["Bb2", 8]],  // 3
        [["F2", 4], ["F2", 4], ["Bb2", 8]],  // 4
    ),
    glock: bars('victory.glock',
        [["F5", 2], ["Bb5", 2], ["D6", 2], ["F6", 2], ["Bb6", 8]],  // 1
        [[null, 8], ["Bb6", 4], ["F6", 4]],  // 2
        [[null, 8], ["Bb6", 8]],  // 3
        [[null, 8], ["Bb6", 8]],  // 4
    ),
    snare: bars('victory.snare',
        [["flam", 2], ["hit", 2], ["hit", 2], ["hit", 6], ["hit", 2], ["hit", 1], ["hit", 1]],  // 1
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 2], ["hit", 1], ["hit", 1]],  // 2
        [["hit", 2], ["hit", 2], ["hit", 2], ["hit", 2], ["hit", 2], ["hit", 2], ["roll", 4]],  // 3
        [["hit", 4], ["hit", 8], ["hit", 4]],  // 4
    ),
    kick: bars('victory.kick',
        [["hit", 4], ["hit", 4], ["hit", 8]],  // 1
        [["hit", 8], ["hit", 8]],  // 2
        [["hit", 4], ["hit", 4], ["hit", 4], ["hit", 4]],  // 3
        [["hit", 4], ["hit", 8], ["hit", 4]],  // 4
    ),
    cymbals: bars('victory.cymbals',
        [["crash", 16]],  // 1
        [[null, 14], ["ride", 2]],  // 2
        [[null, 14], ["choke", 2]],  // 3
        [["crash", 8], ["crash", 8]],  // 4
    ),
  },
};

/** 8-bit reduction for the original 4-channel chip synth. */
export const legacy = {
  bpm: 160,
  loop: false,
  channels: {
    pulse1: bars('victory.legacy.pulse1',
        [["F4", 2], ["Bb4", 2], ["D5", 2], ["F5", 2], ["Bb5", 8]],  // 1
        [["A5", 2], ["Bb5", 2], ["C6", 2], ["D6", 2], ["Bb5", 4], ["F5", 4]],  // 2
        [["Eb5", 2], ["F5", 2], ["G5", 2], ["A5", 2], ["Bb5", 8]],  // 3
        [["Bb4", 2], [null, 2], ["F4", 2], [null, 2], ["Bb5", 8]],  // 4
    ),
    pulse2: bars('victory.legacy.pulse2',
        [["D4", 2], ["F4", 2], ["Bb4", 2], ["D5", 2], ["F5", 8]],  // 1
        [["F5", 2], ["G5", 2], ["A5", 2], ["Bb5", 2], ["F5", 4], ["D5", 4]],  // 2
        [["C5", 2], ["D5", 2], ["Eb5", 2], ["F5", 2], ["G5", 8]],  // 3
        [["D4", 2], [null, 2], ["C4", 2], [null, 2], ["F5", 8]],  // 4
    ),
    triangle: bars('victory.legacy.triangle',
        [["Bb2", 4], ["F2", 4], ["Bb2", 8]],  // 1
        [["F2", 8], ["Bb2", 8]],  // 2
        [["Eb2", 8], ["Bb2", 8]],  // 3
        [["F2", 4], ["F2", 4], ["Bb2", 8]],  // 4
    ),
    noise: bars('victory.legacy.noise',
        [["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2], ["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1]],  // 1
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1]],  // 2
        [["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2], ["kick", 2], ["hat", 2]],  // 3
        [["kick", 4], ["kick", 4], ["hat", 4], ["kick", 4]],  // 4
    ),
  },
};

export default song;
