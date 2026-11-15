/**
 * Band Wars — looping character-select groove
 * id: select
 *
 * Tight 16-bit drumline groove with brass stabs, a clarinet riff, and a
 * walking-ish tuba ostinato. Mixolydian color (Bb against a C tonic)
 * keeps it cooler than the fight-song stages.
 * Key: C mixolydian. Tempo: 128 BPM. 4/4.
 *
 * Structure (16-step bars):
 *   Groove  bars  1–4   stabs over the ostinato
 *   Riff    bars  5–8   trumpet / clarinet riff
 *   Tag     bars  9–12  variation and turnaround
 * `loop: true`. 12 bars = 192 sixteenths ≈ 22.50s.
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
  bpm: 128,
  loop: true,
  instruments: {
    lead: "trumpet-lead",
    horn: "horn",
    clarinet: "clarinet",
    bass: "tuba-bass",
    glock: "glockenspiel",
    snare: "snare",
    kick: "bass-drum",
    cymbals: "cymbals"
  },
  mix: {
    lead: { volume: 0.82, pan: -0.12 },
    horn: { volume: 0.58, pan: 0.3 },
    clarinet: { volume: 0.48, pan: -0.34 },
    bass: { volume: 0.84, pan: 0.0 },
    glock: { volume: 0.32, pan: 0.18 },
    snare: { volume: 0.74, pan: 0.04 },
    kick: { volume: 0.88, pan: 0.0 },
    cymbals: { volume: 0.4, pan: -0.18 }
  },
  echo: { delay: 0.15, feedback: 0.25, mix: 0.16 },
  channels: {
    lead: bars('select.lead',
        [[null, 2], ["E4", 2], [null, 2], ["G4", 2], [null, 2], ["C5", 2], ["G4", 4]],  // 1
        [[null, 2], ["E4", 2], [null, 2], ["G4", 2], ["Bb4", 2], ["A4", 2], ["G4", 4]],  // 2
        [[null, 2], ["E4", 2], [null, 2], ["G4", 2], [null, 2], ["C5", 2], ["D5", 4]],  // 3
        [["E5", 2], ["D5", 2], ["C5", 2], ["Bb4", 2], ["A4", 4], ["G4", 4]],  // 4
        [["E4", 2], ["F4", 2], ["G4", 4], ["A4", 2], ["G4", 2], ["F4", 4]],  // 5
        [["G4", 2], ["A4", 2], ["Bb4", 4], ["A4", 2], ["G4", 2], ["E4", 4]],  // 6
        [["C5", 2], [null, 2], ["D5", 2], [null, 2], ["E5", 2], [null, 2], ["G5", 4]],  // 7
        [["F5", 2], ["E5", 2], ["D5", 2], ["C5", 2], ["Bb4", 4], ["G4", 4]],  // 8
        [[null, 2], ["E4", 2], [null, 2], ["G4", 2], [null, 2], ["C5", 2], ["G4", 4]],  // 9
        [[null, 2], ["Bb4", 2], [null, 2], ["A4", 2], [null, 2], ["G4", 2], ["F4", 4]],  // 10
        [["E4", 2], ["G4", 2], ["C5", 2], ["E5", 2], ["G5", 4], ["E5", 2], ["C5", 2]],  // 11
        [["Bb4", 2], ["A4", 2], ["G4", 2], ["F4", 2], ["E4", 4], ["C4", 4]],  // 12
    ),
    horn: bars('select.horn',
        [["C4", 4], [null, 4], ["E4", 4], [null, 4]],  // 1
        [["C4", 4], [null, 4], ["D4", 4], [null, 4]],  // 2
        [["C4", 4], [null, 4], ["E4", 4], ["G4", 4]],  // 3
        [["A4", 4], ["G4", 4], ["F4", 4], ["E4", 4]],  // 4
        [["C4", 8], ["D4", 8]],  // 5
        [["E4", 8], ["C4", 8]],  // 6
        [[null, 4], ["G4", 4], [null, 4], ["C5", 4]],  // 7
        [["A4", 4], ["G4", 4], ["F4", 4], ["D4", 4]],  // 8
        [["C4", 4], [null, 4], ["E4", 4], [null, 4]],  // 9
        [["D4", 4], [null, 4], ["F4", 4], [null, 4]],  // 10
        [["G4", 8], ["E4", 8]],  // 11
        [["F4", 4], ["D4", 4], ["C4", 8]],  // 12
    ),
    clarinet: bars('select.clarinet',
        [[null, 16]],  // 1
        [[null, 16]],  // 2
        [[null, 8], ["E5", 2], [null, 2], ["G5", 4]],  // 3
        [["A5", 2], ["G5", 2], ["F5", 2], ["E5", 2], ["D5", 4], ["C5", 4]],  // 4
        [[null, 8], ["A5", 2], ["G5", 2], ["F5", 4]],  // 5
        [[null, 8], ["Bb5", 2], ["A5", 2], ["G5", 4]],  // 6
        [["C6", 2], [null, 2], ["D6", 2], [null, 2], ["E6", 2], [null, 2], ["G6", 4]],  // 7
        [["F6", 2], ["E6", 2], ["D6", 2], ["C6", 2], ["Bb5", 4], [null, 4]],  // 8
        [[null, 16]],  // 9
        [[null, 8], ["Bb5", 2], ["A5", 2], ["G5", 4]],  // 10
        [[null, 8], ["G6", 4], ["E6", 2], ["C6", 2]],  // 11
        [["Bb5", 2], ["A5", 2], ["G5", 2], ["F5", 2], ["E5", 4], ["C5", 4]],  // 12
    ),
    bass: bars('select.bass',
        [["C2", 4], ["C2", 2], ["G2", 2], ["C2", 4], ["Bb2", 2], ["G2", 2]],  // 1
        [["C2", 4], ["C2", 2], ["G2", 2], ["Bb2", 4], ["G2", 4]],  // 2
        [["C2", 4], ["C2", 2], ["G2", 2], ["C2", 4], ["Bb2", 2], ["G2", 2]],  // 3
        [["F2", 4], ["F2", 2], ["C3", 2], ["G2", 4], ["G2", 2], ["D2", 2]],  // 4
        [["C2", 4], ["C2", 2], ["G2", 2], ["C2", 4], ["Bb2", 2], ["G2", 2]],  // 5
        [["E2", 4], ["E2", 2], ["C3", 2], ["F2", 4], ["F2", 2], ["C3", 2]],  // 6
        [["C2", 4], ["G2", 4], ["C2", 4], ["G2", 4]],  // 7
        [["F2", 4], ["F2", 2], ["C3", 2], ["G2", 8]],  // 8
        [["C2", 4], ["C2", 2], ["G2", 2], ["C2", 4], ["Bb2", 2], ["G2", 2]],  // 9
        [["Bb2", 4], ["Bb2", 2], ["F2", 2], ["F2", 4], ["F2", 2], ["C3", 2]],  // 10
        [["C2", 4], ["E2", 4], ["G2", 4], ["C3", 4]],  // 11
        [["F2", 4], ["G2", 4], ["C2", 6], [null, 2]],  // 12
    ),
    glock: bars('select.glock',
        [[null, 16]],  // 1
        [[null, 16]],  // 2
        [[null, 12], ["C6", 4]],  // 3
        [[null, 8], ["A5", 4], ["G5", 4]],  // 4
        [[null, 16]],  // 5
        [[null, 16]],  // 6
        [[null, 12], ["G6", 4]],  // 7
        [["F6", 2], ["E6", 2], ["D6", 2], ["C6", 2], [null, 8]],  // 8
        [[null, 16]],  // 9
        [[null, 16]],  // 10
        [[null, 8], ["G6", 4], ["E6", 4]],  // 11
        [[null, 8], ["C6", 4], [null, 4]],  // 12
    ),
    snare: bars('select.snare',
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 2], ["hit", 1], ["hit", 1]],  // 1
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 2], ["rim", 2]],  // 2
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 2], ["hit", 1], ["hit", 1]],  // 3
        [[null, 2], ["hit", 2], ["hit", 1], ["hit", 1], ["hit", 1], ["hit", 5], ["roll", 4]],  // 4
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 2], ["hit", 1], ["hit", 1]],  // 5
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 3], ["hit", 2], ["hit", 2], ["hit", 1], ["hit", 1]],  // 6
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 2], ["hit", 1], ["hit", 1]],  // 7
        [["flam", 2], ["hit", 2], ["hit", 1], ["hit", 1], ["hit", 1], ["hit", 3], ["roll", 4], [null, 2]],  // 8
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 2], ["hit", 1], ["hit", 1]],  // 9
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 2], ["rim", 2]],  // 10
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 3], ["hit", 2], ["hit", 2], ["hit", 2]],  // 11
        [["hit", 2], ["roll", 10], [null, 4]],  // 12
    ),
    kick: bars('select.kick',
        [["hit", 8], ["hit", 2], ["hit", 6]],  // 1
        [["hit", 8], ["hit", 4], ["hit", 4]],  // 2
        [["hit", 8], ["hit", 2], ["hit", 6]],  // 3
        [["hit", 4], ["hit", 8], ["hit", 4]],  // 4
        [["hit", 8], ["hit", 2], ["hit", 6]],  // 5
        [["hit", 8], ["hit", 4], ["hit", 4]],  // 6
        [["hit", 8], ["hit", 2], ["hit", 6]],  // 7
        [["hit", 4], ["hit", 4], ["hit", 8]],  // 8
        [["hit", 8], ["hit", 2], ["hit", 6]],  // 9
        [["hit", 8], ["hit", 4], ["hit", 4]],  // 10
        [["hit", 8], ["hit", 2], ["hit", 2], ["hit", 4]],  // 11
        [["hit", 8], ["hit", 8]],  // 12
    ),
    cymbals: bars('select.cymbals',
        [["crash", 6], ["ride", 8], ["ride", 2]],  // 1
        [[null, 6], ["ride", 8], ["ride", 2]],  // 2
        [[null, 6], ["ride", 8], ["ride", 2]],  // 3
        [[null, 14], ["choke", 2]],  // 4
        [["crash", 6], ["ride", 8], ["ride", 2]],  // 5
        [[null, 6], ["ride", 8], ["ride", 2]],  // 6
        [[null, 6], ["ride", 8], ["ride", 2]],  // 7
        [[null, 14], ["choke", 2]],  // 8
        [["crash", 6], ["ride", 8], ["ride", 2]],  // 9
        [[null, 6], ["ride", 8], ["ride", 2]],  // 10
        [["ride", 2], ["ride", 2], ["ride", 2], ["ride", 2], ["ride", 2], ["ride", 2], ["ride", 2], ["ride", 2]],  // 11
        [["crash", 16]],  // 12
    ),
  },
};

/** 8-bit reduction for the original 4-channel chip synth. */
export const legacy = {
  bpm: 128,
  loop: true,
  channels: {
    pulse1: bars('select.legacy.pulse1',
        [[null, 2], ["E4", 2], [null, 2], ["G4", 2], [null, 2], ["C5", 2], ["G4", 4]],  // 1
        [[null, 2], ["E4", 2], [null, 2], ["G4", 2], ["Bb4", 2], ["A4", 2], ["G4", 4]],  // 2
        [[null, 2], ["E4", 2], [null, 2], ["G4", 2], [null, 2], ["C5", 2], ["D5", 4]],  // 3
        [["E5", 2], ["D5", 2], ["C5", 2], ["Bb4", 2], ["A4", 4], ["G4", 4]],  // 4
        [["E4", 2], ["F4", 2], ["G4", 4], ["A4", 2], ["G4", 2], ["F4", 4]],  // 5
        [["G4", 2], ["A4", 2], ["Bb4", 4], ["A4", 2], ["G4", 2], ["E4", 4]],  // 6
        [["C5", 2], [null, 2], ["D5", 2], [null, 2], ["E5", 2], [null, 2], ["G5", 4]],  // 7
        [["F5", 2], ["E5", 2], ["D5", 2], ["C5", 2], ["Bb4", 4], ["G4", 4]],  // 8
        [[null, 2], ["E4", 2], [null, 2], ["G4", 2], [null, 2], ["C5", 2], ["G4", 4]],  // 9
        [[null, 2], ["Bb4", 2], [null, 2], ["A4", 2], [null, 2], ["G4", 2], ["F4", 4]],  // 10
        [["E4", 2], ["G4", 2], ["C5", 2], ["E5", 2], ["G5", 4], ["E5", 2], ["C5", 2]],  // 11
        [["Bb4", 2], ["A4", 2], ["G4", 2], ["F4", 2], ["E4", 4], ["C4", 4]],  // 12
    ),
    pulse2: bars('select.legacy.pulse2',
        [["C4", 4], [null, 4], ["E4", 4], [null, 4]],  // 1
        [["C4", 4], [null, 4], ["D4", 4], [null, 4]],  // 2
        [["C4", 4], [null, 4], ["E4", 4], ["G4", 4]],  // 3
        [["A4", 4], ["G4", 4], ["F4", 4], ["E4", 4]],  // 4
        [["C4", 8], ["D4", 8]],  // 5
        [["E4", 8], ["C4", 8]],  // 6
        [[null, 4], ["G4", 4], [null, 4], ["C5", 4]],  // 7
        [["A4", 4], ["G4", 4], ["F4", 4], ["D4", 4]],  // 8
        [["C4", 4], [null, 4], ["E4", 4], [null, 4]],  // 9
        [["D4", 4], [null, 4], ["F4", 4], [null, 4]],  // 10
        [["G4", 8], ["E4", 8]],  // 11
        [["F4", 4], ["D4", 4], ["C4", 8]],  // 12
    ),
    triangle: bars('select.legacy.triangle',
        [["C2", 4], ["C2", 2], ["G2", 2], ["C2", 4], ["Bb2", 2], ["G2", 2]],  // 1
        [["C2", 4], ["C2", 2], ["G2", 2], ["Bb2", 4], ["G2", 4]],  // 2
        [["C2", 4], ["C2", 2], ["G2", 2], ["C2", 4], ["Bb2", 2], ["G2", 2]],  // 3
        [["F2", 4], ["F2", 2], ["C3", 2], ["G2", 4], ["G2", 2], ["D2", 2]],  // 4
        [["C2", 4], ["C2", 2], ["G2", 2], ["C2", 4], ["Bb2", 2], ["G2", 2]],  // 5
        [["E2", 4], ["E2", 2], ["C3", 2], ["F2", 4], ["F2", 2], ["C3", 2]],  // 6
        [["C2", 4], ["G2", 4], ["C2", 4], ["G2", 4]],  // 7
        [["F2", 4], ["F2", 2], ["C3", 2], ["G2", 8]],  // 8
        [["C2", 4], ["C2", 2], ["G2", 2], ["C2", 4], ["Bb2", 2], ["G2", 2]],  // 9
        [["Bb2", 4], ["Bb2", 2], ["F2", 2], ["F2", 4], ["F2", 2], ["C3", 2]],  // 10
        [["C2", 4], ["E2", 4], ["G2", 4], ["C3", 4]],  // 11
        [["F2", 4], ["G2", 4], ["C2", 6], [null, 2]],  // 12
    ),
    noise: bars('select.legacy.noise',
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["kick", 2], ["snare", 2], ["snare", 1], ["snare", 1]],  // 1
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 4], ["kick", 2], ["snare", 2]],  // 2
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["kick", 2], ["snare", 2], ["snare", 1], ["snare", 1]],  // 3
        [["kick", 2], ["snare", 2], ["kick", 1], ["snare", 1], ["snare", 1], ["snare", 5], ["kick", 2], ["hat", 2]],  // 4
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["kick", 2], ["snare", 2], ["snare", 1], ["snare", 1]],  // 5
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 2], ["kick", 2], ["snare", 1], ["snare", 1]],  // 6
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["kick", 2], ["snare", 2], ["snare", 1], ["snare", 1]],  // 7
        [["kick", 2], ["snare", 2], ["kick", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 4], ["hat", 2]],  // 8
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["kick", 2], ["snare", 2], ["snare", 1], ["snare", 1]],  // 9
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 4], ["kick", 2], ["snare", 2]],  // 10
        [["kick", 2], ["hat", 2], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["kick", 2], ["kick", 2], ["snare", 2]],  // 11
        [["kick", 2], ["snare", 6], ["kick", 8]],  // 12
    ),
  },
};

export default song;
