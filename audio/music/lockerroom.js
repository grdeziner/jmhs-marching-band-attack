/**
 * Band Wars — locker-room / tunnel pre-show theme
 * id: lockerroom
 *
 * Tense, echoey 16-bit pre-show cadence. Sparse horn and trombone calls,
 * a thin clarinet color, and a heavy rudimental drumline (snare, bass drum,
 * cymbals, quad-toms).
 * Key: D minor. Tempo: 116 BPM. 4/4.
 *
 * Structure (16-step bars):
 *   Cadence  bars  1–8    drums establish, lone horn calls
 *   Motif    bars  9–16   sparse minor melody over the cadence
 *   Build    bars 17–24   rising tension, then a drop for the loop
 * `loop: true`. 24 bars = 384 sixteenths ≈ 49.66s.
 *
 * Echo is a long concrete-hallway hint (long delay, higher feedback).
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
  bpm: 116,
  loop: true,
  instruments: {
    horn: "horn",
    trombone: "trombone",
    bass: "tuba-bass",
    clarinet: "clarinet",
    snare: "snare",
    kick: "bass-drum",
    cymbals: "cymbals",
    toms: "quad-toms"
  },
  mix: {
    horn: { volume: 0.7, pan: -0.18 },
    trombone: { volume: 0.55, pan: 0.32 },
    bass: { volume: 0.8, pan: 0.0 },
    clarinet: { volume: 0.4, pan: 0.22 },
    snare: { volume: 0.8, pan: 0.05 },
    kick: { volume: 0.9, pan: 0.0 },
    cymbals: { volume: 0.38, pan: -0.28 },
    toms: { volume: 0.62, pan: 0.18 }
  },
  echo: { delay: 0.31, feedback: 0.46, mix: 0.34 },
  channels: {
    horn: bars('lockerroom.horn',
        [[null, 16]],  // 1
        [[null, 16]],  // 2
        [["A4", 4], [null, 12]],  // 3
        [[null, 8], ["A4", 2], [null, 2], ["A4", 4]],  // 4
        [[null, 16]],  // 5
        [[null, 16]],  // 6
        [["D5", 2], [null, 2], ["D5", 4], ["C5", 2], [null, 2], ["A4", 4]],  // 7
        [[null, 8], ["A4", 8]],  // 8
        [["D4", 4], ["F4", 4], ["A4", 4], [null, 4]],  // 9
        [[null, 4], ["G4", 4], ["F4", 4], [null, 4]],  // 10
        [["E4", 8], [null, 4], ["F4", 4]],  // 11
        [["E4", 4], [null, 4], ["D4", 8]],  // 12
        [[null, 16]],  // 13
        [[null, 12], ["A4", 4]],  // 14
        [["D5", 4], [null, 4], ["C5", 4], [null, 4]],  // 15
        [["A4", 8], [null, 8]],  // 16
        [["F4", 2], [null, 2], ["F4", 2], [null, 2], ["F4", 4], [null, 4]],  // 17
        [["G4", 2], [null, 2], ["G4", 2], [null, 2], ["G4", 4], [null, 4]],  // 18
        [["A4", 2], [null, 2], ["A4", 2], [null, 2], ["A4", 4], ["Bb4", 4]],  // 19
        [["A4", 8], [null, 8]],  // 20
        [["D5", 4], ["A4", 4], ["F4", 4], [null, 4]],  // 21
        [[null, 8], ["E4", 8]],  // 22
        [["D4", 16]],  // 23
        [[null, 16]],  // 24
    ),
    trombone: bars('lockerroom.trombone',
        [[null, 16]],  // 1
        [[null, 16]],  // 2
        [[null, 4], ["D4", 4], [null, 8]],  // 3
        [[null, 12], ["A3", 4]],  // 4
        [["A3", 4], [null, 12]],  // 5
        [[null, 16]],  // 6
        [[null, 4], ["F4", 2], [null, 2], ["F4", 4], ["E4", 2], [null, 2]],  // 7
        [["A3", 4], [null, 4], ["D4", 8]],  // 8
        [[null, 4], ["D4", 4], ["F4", 4], ["A3", 4]],  // 9
        [[null, 8], ["G3", 4], ["F3", 4]],  // 10
        [[null, 4], ["C4", 8], [null, 4]],  // 11
        [["F3", 4], ["E3", 4], [null, 4], ["A3", 4]],  // 12
        [[null, 16]],  // 13
        [[null, 16]],  // 14
        [["A3", 4], [null, 4], ["F4", 4], [null, 4]],  // 15
        [[null, 4], ["E4", 4], [null, 8]],  // 16
        [[null, 4], ["D4", 2], [null, 2], ["D4", 2], [null, 2], ["D4", 4]],  // 17
        [[null, 4], ["E4", 2], [null, 2], ["E4", 2], [null, 2], ["E4", 4]],  // 18
        [[null, 4], ["F4", 2], [null, 2], ["F4", 2], [null, 2], ["F4", 4]],  // 19
        [["Bb3", 4], ["E4", 8], [null, 4]],  // 20
        [[null, 4], ["A3", 4], ["F3", 4], ["D3", 4]],  // 21
        [[null, 12], ["C4", 4]],  // 22
        [["C4", 4], [null, 4], ["A3", 8]],  // 23
        [[null, 16]],  // 24
    ),
    bass: bars('lockerroom.bass',
        [[null, 16]],  // 1
        [["D2", 8], [null, 8]],  // 2
        [[null, 16]],  // 3
        [["D2", 8], [null, 8]],  // 4
        [[null, 16]],  // 5
        [["A1", 8], [null, 8]],  // 6
        [["D2", 8], [null, 8]],  // 7
        [["A1", 8], ["D2", 8]],  // 8
        [["D2", 8], ["F2", 8]],  // 9
        [["G2", 8], [null, 4], ["F2", 4]],  // 10
        [["E2", 8], [null, 8]],  // 11
        [["A1", 8], ["D2", 8]],  // 12
        [["D2", 4], [null, 4], ["D2", 4], [null, 4]],  // 13
        [["D2", 4], [null, 4], ["A1", 8]],  // 14
        [["D2", 8], ["C2", 8]],  // 15
        [["A1", 16]],  // 16
        [["F2", 4], [null, 4], ["F2", 8]],  // 17
        [["G2", 4], [null, 4], ["G2", 8]],  // 18
        [["A1", 4], [null, 4], ["A1", 4], ["Bb1", 4]],  // 19
        [["A1", 16]],  // 20
        [["D2", 8], ["A1", 8]],  // 21
        [["F2", 8], ["E2", 8]],  // 22
        [["D2", 16]],  // 23
        [["D2", 8], [null, 8]],  // 24
    ),
    clarinet: bars('lockerroom.clarinet',
        [[null, 16]],  // 1
        [[null, 16]],  // 2
        [[null, 16]],  // 3
        [[null, 16]],  // 4
        [[null, 16]],  // 5
        [[null, 16]],  // 6
        [[null, 8], ["A5", 2], [null, 2], ["F5", 4]],  // 7
        [[null, 8], ["E5", 8]],  // 8
        [[null, 12], ["A5", 4]],  // 9
        [[null, 16]],  // 10
        [["E5", 8], [null, 8]],  // 11
        [[null, 8], ["D5", 8]],  // 12
        [[null, 16]],  // 13
        [[null, 16]],  // 14
        [[null, 8], ["C6", 4], [null, 4]],  // 15
        [["A5", 8], [null, 8]],  // 16
        [[null, 16]],  // 17
        [[null, 16]],  // 18
        [[null, 8], ["A5", 4], ["Bb5", 4]],  // 19
        [["A5", 8], [null, 8]],  // 20
        [[null, 4], ["A5", 4], ["F5", 4], [null, 4]],  // 21
        [[null, 16]],  // 22
        [["D5", 16]],  // 23
        [[null, 16]],  // 24
    ),
    snare: bars('lockerroom.snare',
        [[null, 4], ["hit", 2], ["hit", 6], ["hit", 1], ["hit", 1], ["hit", 2]],  // 1
        [[null, 4], ["hit", 6], ["hit", 2], ["hit", 1], ["hit", 1], ["hit", 2]],  // 2
        [[null, 2], ["hit", 1], ["hit", 1], ["hit", 2], ["hit", 4], ["hit", 1], ["hit", 1], ["hit", 4]],  // 3
        [[null, 4], ["roll", 8], [null, 4]],  // 4
        [[null, 4], ["hit", 2], ["hit", 6], ["hit", 2], ["hit", 1], ["hit", 1]],  // 5
        [[null, 4], ["hit", 8], ["roll", 4]],  // 6
        [[null, 2], ["hit", 4], ["hit", 1], ["hit", 3], ["hit", 6]],  // 7
        [[null, 4], ["roll", 10], [null, 2]],  // 8
        [[null, 2], ["hit", 1], ["hit", 1], ["hit", 6], ["hit", 1], ["hit", 1], ["hit", 4]],  // 9
        [[null, 4], ["hit", 2], ["rim", 1], ["hit", 5], ["hit", 2], ["hit", 2]],  // 10
        [[null, 2], ["hit", 2], ["hit", 1], ["hit", 1], ["hit", 4], ["hit", 1], ["hit", 1], ["hit", 4]],  // 11
        [[null, 4], ["roll", 8], [null, 2], ["hit", 2]],  // 12
        [[null, 4], ["hit", 6], ["hit", 1], ["hit", 1], ["hit", 4]],  // 13
        [[null, 4], ["hit", 2], ["hit", 4], ["hit", 2], ["hit", 1], ["hit", 3]],  // 14
        [[null, 2], ["hit", 1], ["hit", 3], ["hit", 1], ["hit", 3], ["hit", 1], ["hit", 1], ["hit", 4]],  // 15
        [["roll", 12], [null, 4]],  // 16
        [[null, 2], ["hit", 4], ["hit", 4], ["hit", 4], ["hit", 2]],  // 17
        [[null, 2], ["hit", 4], ["hit", 4], ["hit", 4], ["hit", 2]],  // 18
        [[null, 2], ["hit", 1], ["hit", 3], ["hit", 1], ["hit", 3], ["hit", 1], ["hit", 3], ["hit", 1], ["hit", 1]],  // 19
        [[null, 2], ["roll", 6], [null, 2], ["roll", 6]],  // 20
        [[null, 4], ["hit", 8], ["hit", 4]],  // 21
        [[null, 4], ["hit", 2], ["hit", 1], ["hit", 5], ["hit", 4]],  // 22
        [[null, 2], ["roll", 6], [null, 2], ["roll", 6]],  // 23
        [[null, 8], ["hit", 8]],  // 24
    ),
    kick: bars('lockerroom.kick',
        [["hit", 8], ["hit", 8]],  // 1
        [["hit", 8], ["hit", 8]],  // 2
        [["hit", 8], ["hit", 8]],  // 3
        [["hit", 12], ["hit", 4]],  // 4
        [["hit", 8], ["hit", 2], ["hit", 6]],  // 5
        [["hit", 8], ["hit", 8]],  // 6
        [["hit", 4], ["hit", 4], ["hit", 4], ["hit", 4]],  // 7
        [["hit", 16]],  // 8
        [["hit", 8], ["hit", 8]],  // 9
        [["hit", 8], ["hit", 8]],  // 10
        [["hit", 8], ["hit", 8]],  // 11
        [["hit", 12], ["hit", 4]],  // 12
        [["hit", 2], ["hit", 6], ["hit", 8]],  // 13
        [["hit", 8], ["hit", 1], ["hit", 7]],  // 14
        [["hit", 4], ["hit", 4], ["hit", 8]],  // 15
        [[null, 12], ["hit", 4]],  // 16
        [["hit", 4], ["hit", 4], ["hit", 4], ["hit", 4]],  // 17
        [["hit", 4], ["hit", 4], ["hit", 4], ["hit", 4]],  // 18
        [["hit", 4], ["hit", 4], ["hit", 4], ["hit", 4]],  // 19
        [["hit", 8], ["hit", 8]],  // 20
        [["hit", 8], ["hit", 8]],  // 21
        [["hit", 8], ["hit", 8]],  // 22
        [["hit", 8], ["hit", 8]],  // 23
        [["hit", 16]],  // 24
    ),
    cymbals: bars('lockerroom.cymbals',
        [[null, 16]],  // 1
        [[null, 6], ["choke", 10]],  // 2
        [[null, 14], ["choke", 2]],  // 3
        [[null, 14], ["choke", 2]],  // 4
        [[null, 16]],  // 5
        [[null, 2], ["choke", 14]],  // 6
        [[null, 14], ["choke", 2]],  // 7
        [[null, 14], ["choke", 2]],  // 8
        [["crash", 14], ["choke", 2]],  // 9
        [[null, 10], ["choke", 6]],  // 10
        [[null, 14], ["choke", 2]],  // 11
        [[null, 16]],  // 12
        [[null, 6], ["choke", 8], ["choke", 2]],  // 13
        [[null, 14], ["choke", 2]],  // 14
        [[null, 14], ["choke", 2]],  // 15
        [[null, 14], ["choke", 2]],  // 16
        [["crash", 16]],  // 17
        [[null, 16]],  // 18
        [[null, 16]],  // 19
        [[null, 16]],  // 20
        [[null, 14], ["choke", 2]],  // 21
        [[null, 14], ["choke", 2]],  // 22
        [[null, 16]],  // 23
        [[null, 12], ["choke", 4]],  // 24
    ),
    toms: bars('lockerroom.toms',
        [[null, 16]],  // 1
        [[null, 16]],  // 2
        [[null, 16]],  // 3
        [[null, 16]],  // 4
        [[null, 16]],  // 5
        [[null, 16]],  // 6
        [[null, 16]],  // 7
        [[null, 8], ["A3", 2], ["E3", 2], ["C3", 2], ["G2", 2]],  // 8
        [[null, 16]],  // 9
        [[null, 16]],  // 10
        [[null, 16]],  // 11
        [[null, 10], ["A3", 2], ["E3", 2], ["C3", 2]],  // 12
        [[null, 16]],  // 13
        [[null, 16]],  // 14
        [[null, 16]],  // 15
        [[null, 8], ["A3", 2], ["E3", 2], ["C3", 2], ["G2", 2]],  // 16
        [[null, 16]],  // 17
        [[null, 16]],  // 18
        [[null, 16]],  // 19
        [[null, 4], ["C4", 2], ["A3", 2], ["E3", 2], ["C3", 2], ["G2", 4]],  // 20
        [[null, 16]],  // 21
        [[null, 16]],  // 22
        [[null, 8], ["A3", 2], ["E3", 2], ["C3", 2], ["G2", 2]],  // 23
        [["G2", 4], [null, 12]],  // 24
    ),
  },
};

/** 8-bit reduction for the original 4-channel chip synth. */
export const legacy = {
  bpm: 116,
  loop: true,
  channels: {
    pulse1: bars('lockerroom.legacy.pulse1',
        [[null, 16]],  // 1
        [[null, 16]],  // 2
        [["A4", 4], [null, 12]],  // 3
        [[null, 8], ["A4", 2], [null, 2], ["A4", 4]],  // 4
        [[null, 16]],  // 5
        [[null, 16]],  // 6
        [["D5", 2], [null, 2], ["D5", 4], ["C5", 2], [null, 2], ["A4", 4]],  // 7
        [[null, 8], ["A4", 8]],  // 8
        [["D4", 4], ["F4", 4], ["A4", 4], [null, 4]],  // 9
        [[null, 4], ["G4", 4], ["F4", 4], [null, 4]],  // 10
        [["E4", 8], [null, 4], ["F4", 4]],  // 11
        [["E4", 4], [null, 4], ["D4", 8]],  // 12
        [[null, 16]],  // 13
        [[null, 12], ["A4", 4]],  // 14
        [["D5", 4], [null, 4], ["C5", 4], [null, 4]],  // 15
        [["A4", 8], [null, 8]],  // 16
        [["F4", 2], [null, 2], ["F4", 2], [null, 2], ["F4", 4], [null, 4]],  // 17
        [["G4", 2], [null, 2], ["G4", 2], [null, 2], ["G4", 4], [null, 4]],  // 18
        [["A4", 2], [null, 2], ["A4", 2], [null, 2], ["A4", 4], ["Bb4", 4]],  // 19
        [["A4", 8], [null, 8]],  // 20
        [["D5", 4], ["A4", 4], ["F4", 4], [null, 4]],  // 21
        [[null, 8], ["E4", 8]],  // 22
        [["D4", 16]],  // 23
        [[null, 16]],  // 24
    ),
    pulse2: bars('lockerroom.legacy.pulse2',
        [[null, 16]],  // 1
        [[null, 16]],  // 2
        [[null, 4], ["D4", 4], [null, 8]],  // 3
        [[null, 12], ["A3", 4]],  // 4
        [["A3", 4], [null, 12]],  // 5
        [[null, 16]],  // 6
        [[null, 4], ["F4", 2], [null, 2], ["F4", 4], ["E4", 2], [null, 2]],  // 7
        [["A3", 4], [null, 4], ["D4", 8]],  // 8
        [[null, 4], ["D4", 4], ["F4", 4], ["A3", 4]],  // 9
        [[null, 8], ["G3", 4], ["F3", 4]],  // 10
        [[null, 4], ["C4", 8], [null, 4]],  // 11
        [["F3", 4], ["E3", 4], [null, 4], ["A3", 4]],  // 12
        [[null, 16]],  // 13
        [[null, 16]],  // 14
        [["A3", 4], [null, 4], ["F4", 4], [null, 4]],  // 15
        [[null, 4], ["E4", 4], [null, 8]],  // 16
        [[null, 4], ["D4", 2], [null, 2], ["D4", 2], [null, 2], ["D4", 4]],  // 17
        [[null, 4], ["E4", 2], [null, 2], ["E4", 2], [null, 2], ["E4", 4]],  // 18
        [[null, 4], ["F4", 2], [null, 2], ["F4", 2], [null, 2], ["F4", 4]],  // 19
        [["Bb3", 4], ["E4", 8], [null, 4]],  // 20
        [[null, 4], ["A3", 4], ["F3", 4], ["D3", 4]],  // 21
        [[null, 12], ["C4", 4]],  // 22
        [["C4", 4], [null, 4], ["A3", 8]],  // 23
        [[null, 16]],  // 24
    ),
    triangle: bars('lockerroom.legacy.triangle',
        [[null, 16]],  // 1
        [["D2", 8], [null, 8]],  // 2
        [[null, 16]],  // 3
        [["D2", 8], [null, 8]],  // 4
        [[null, 16]],  // 5
        [["A1", 8], [null, 8]],  // 6
        [["D2", 8], [null, 8]],  // 7
        [["A1", 8], ["D2", 8]],  // 8
        [["D2", 8], ["F2", 8]],  // 9
        [["G2", 8], [null, 4], ["F2", 4]],  // 10
        [["E2", 8], [null, 8]],  // 11
        [["A1", 8], ["D2", 8]],  // 12
        [["D2", 4], [null, 4], ["D2", 4], [null, 4]],  // 13
        [["D2", 4], [null, 4], ["A1", 8]],  // 14
        [["D2", 8], ["C2", 8]],  // 15
        [["A1", 16]],  // 16
        [["F2", 4], [null, 4], ["F2", 8]],  // 17
        [["G2", 4], [null, 4], ["G2", 8]],  // 18
        [["A1", 4], [null, 4], ["A1", 4], ["Bb1", 4]],  // 19
        [["A1", 16]],  // 20
        [["D2", 8], ["A1", 8]],  // 21
        [["F2", 8], ["E2", 8]],  // 22
        [["D2", 16]],  // 23
        [["D2", 8], [null, 8]],  // 24
    ),
    noise: bars('lockerroom.legacy.noise',
        [["kick", 4], ["snare", 2], ["snare", 2], ["kick", 4], ["snare", 1], ["snare", 1], ["snare", 2]],  // 1
        [["kick", 4], ["snare", 2], ["hat", 2], ["kick", 2], ["snare", 2], ["snare", 1], ["snare", 1], ["snare", 2]],  // 2
        [["kick", 2], ["snare", 1], ["snare", 1], ["snare", 2], ["snare", 2], ["kick", 2], ["snare", 1], ["snare", 1], ["snare", 2], ["hat", 2]],  // 3
        [["kick", 4], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["kick", 2], ["hat", 2]],  // 4
        [["kick", 4], ["snare", 2], ["snare", 2], ["kick", 2], ["kick", 2], ["snare", 2], ["snare", 1], ["snare", 1]],  // 5
        [["kick", 2], ["hat", 2], ["snare", 4], ["kick", 4], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1]],  // 6
        [["kick", 2], ["snare", 2], ["kick", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 2], ["kick", 2], ["hat", 2]],  // 7
        [["kick", 4], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["hat", 2]],  // 8
        [["kick", 2], ["snare", 1], ["snare", 1], ["snare", 4], ["kick", 2], ["snare", 1], ["snare", 1], ["snare", 2], ["hat", 2]],  // 9
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["hat", 2], ["snare", 2], ["snare", 2]],  // 10
        [["kick", 2], ["snare", 2], ["snare", 1], ["snare", 1], ["snare", 2], ["kick", 2], ["snare", 1], ["snare", 1], ["snare", 2], ["hat", 2]],  // 11
        [["kick", 4], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 2]],  // 12
        [["kick", 2], ["kick", 2], ["snare", 2], ["hat", 2], ["kick", 2], ["snare", 1], ["snare", 1], ["snare", 2], ["hat", 2]],  // 13
        [["kick", 4], ["snare", 2], ["snare", 2], ["kick", 1], ["kick", 1], ["snare", 2], ["snare", 1], ["snare", 1], ["hat", 2]],  // 14
        [["kick", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 1], ["snare", 1], ["snare", 2], ["hat", 2]],  // 15
        [["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["kick", 2], ["hat", 2]],  // 16
        [["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2]],  // 17
        [["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2], ["kick", 2], ["snare", 2]],  // 18
        [["kick", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 1], ["snare", 1]],  // 19
        [["kick", 2], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1]],  // 20
        [["kick", 4], ["snare", 4], ["kick", 4], ["snare", 2], ["hat", 2]],  // 21
        [["kick", 4], ["snare", 2], ["snare", 1], ["snare", 1], ["kick", 4], ["snare", 2], ["hat", 2]],  // 22
        [["kick", 2], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["kick", 2], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1], ["snare", 1]],  // 23
        [["kick", 8], ["snare", 4], ["hat", 2], [null, 2]],  // 24
    ),
  },
};

export default song;
