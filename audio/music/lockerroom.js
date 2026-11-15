/**
 * Band Wars — locker-room / tunnel pre-show theme
 * id: lockerroom
 *
 * Tense, echoey pre-show drum cadence. Sparse horn calls bounce off
 * concrete walls; the noise channel carries a heavy rudimental cadence.
 * Key: D minor. Tempo: 116 BPM. 4/4.
 *
 * Structure (in 16-step bars / sixteenths):
 *   Cadence  bars  1–8   (128 sixteenths) drums establish, lone trumpet calls
 *   Motif    bars  9–16  (128 sixteenths) sparse minor melody over the cadence
 *   Build    bars 17–24  (128 sixteenths) rising tension, then a drop for the loop
 * Whole pattern loops from the start (`loop: true`).
 * 24 bars = 384 sixteenths ≈ 49.66s at 116 BPM.
 *
 * Channels:
 *   pulse1  — sparse, echoey trumpet/horn calls (square, 50% duty in preview)
 *   pulse2  — delayed, quieter-feeling echo (square, 25% duty; written later
 *             in the bar / often an octave or fifth below)
 *   triangle — ominous tuba pedals with lots of space
 *   noise   — the lead voice. Note names:
 *              'kick'  bass drum
 *              'snare' snare (rolls / diddles / flam-feel = rapid snares)
 *              'hat'   stick click / cymbal choke
 *              or a pitch name (e.g. 'G3') for pitched percussion
 *   null    — rest
 * Each event is [noteName | null, lengthInSixteenths].
 * Every channel totals the same number of sixteenths.
 *
 * `loop`: true means loop from sixteenth 0.
 *         A number would mean loop-start in sixteenths (intro not repeated).
 */

function bars(...measures) {
  const notes = [];
  measures.forEach((m, i) => {
    const sum = m.reduce((acc, ev) => acc + ev[1], 0);
    if (sum !== 16) {
      throw new Error(`lockerroom: bar ${i + 1} is ${sum} sixteenths, expected 16`);
    }
    notes.push(...m);
  });
  return notes;
}

export const song = {
  bpm: 116,
  loop: true,
  channels: {
    pulse1: bars(
      // ---- Cadence, sparse calls ----
      // bar 1
      [[null, 16]],
      // bar 2
      [[null, 16]],
      // bar 3 — lone call
      [['A4', 4], [null, 12]],
      // bar 4 — echo of the call
      [[null, 8], ['A4', 2], [null, 2], ['A4', 4]],
      // bar 5
      [[null, 16]],
      // bar 6
      [[null, 16]],
      // bar 7 — short falling figure
      [['D5', 2], [null, 2], ['D5', 4], ['C5', 2], [null, 2], ['A4', 4]],
      // bar 8 — held echo
      [[null, 8], ['A4', 8]],

      // ---- Motif ----
      // bar 9
      [['D4', 4], ['F4', 4], ['A4', 4], [null, 4]],
      // bar 10
      [[null, 4], ['G4', 4], ['F4', 4], [null, 4]],
      // bar 11
      [['E4', 8], [null, 4], ['F4', 4]],
      // bar 12
      [['E4', 4], [null, 4], ['D4', 8]],
      // bar 13 — drums take the floor
      [[null, 16]],
      // bar 14
      [[null, 12], ['A4', 4]],
      // bar 15
      [['D5', 4], [null, 4], ['C5', 4], [null, 4]],
      // bar 16
      [['A4', 8], [null, 8]],

      // ---- Build ----
      // bar 17
      [['F4', 2], [null, 2], ['F4', 2], [null, 2], ['F4', 4], [null, 4]],
      // bar 18
      [['G4', 2], [null, 2], ['G4', 2], [null, 2], ['G4', 4], [null, 4]],
      // bar 19
      [['A4', 2], [null, 2], ['A4', 2], [null, 2], ['A4', 4], ['Bb4', 4]],
      // bar 20
      [['A4', 8], [null, 8]],
      // bar 21
      [['D5', 4], ['A4', 4], ['F4', 4], [null, 4]],
      // bar 22
      [[null, 8], ['E4', 8]],
      // bar 23 — long tense pedal
      [['D4', 16]],
      // bar 24 — air before the loop
      [[null, 16]],
    ),

    pulse2: bars(
      // delayed / lower echoes of pulse1
      // bar 1
      [[null, 16]],
      // bar 2
      [[null, 16]],
      // bar 3 — echo enters a beat later, a fifth below
      [[null, 4], ['D4', 4], [null, 8]],
      // bar 4
      [[null, 12], ['A3', 4]],
      // bar 5 — spillover echo
      [['A3', 4], [null, 12]],
      // bar 6
      [[null, 16]],
      // bar 7 — delayed a beat
      [[null, 4], ['F4', 2], [null, 2], ['F4', 4], ['E4', 2], [null, 2]],
      // bar 8
      [['A3', 4], [null, 4], ['D4', 8]],
      // bar 9
      [[null, 4], ['D4', 4], ['F4', 4], ['A3', 4]],
      // bar 10
      [[null, 8], ['G3', 4], ['F3', 4]],
      // bar 11
      [[null, 4], ['C4', 8], [null, 4]],
      // bar 12
      [['F3', 4], ['E3', 4], [null, 4], ['A3', 4]],
      // bar 13
      [[null, 16]],
      // bar 14
      [[null, 16]],
      // bar 15 — echoes of the end of bar 14 / bar 15
      [['A3', 4], [null, 4], ['F4', 4], [null, 4]],
      // bar 16
      [[null, 4], ['E4', 4], [null, 8]],
      // bar 17
      [[null, 4], ['D4', 2], [null, 2], ['D4', 2], [null, 2], ['D4', 4]],
      // bar 18
      [[null, 4], ['E4', 2], [null, 2], ['E4', 2], [null, 2], ['E4', 4]],
      // bar 19
      [[null, 4], ['F4', 2], [null, 2], ['F4', 2], [null, 2], ['F4', 4]],
      // bar 20
      [['Bb3', 4], ['E4', 8], [null, 4]],
      // bar 21
      [[null, 4], ['A3', 4], ['F3', 4], ['D3', 4]],
      // bar 22
      [[null, 12], ['C4', 4]],
      // bar 23
      [['C4', 4], [null, 4], ['A3', 8]],
      // bar 24
      [[null, 16]],
    ),

    triangle: bars(
      // bar 1
      [[null, 16]],
      // bar 2 — first pedal, then space
      [['D2', 8], [null, 8]],
      // bar 3
      [[null, 16]],
      // bar 4
      [['D2', 8], [null, 8]],
      // bar 5
      [[null, 16]],
      // bar 6
      [['A1', 8], [null, 8]],
      // bar 7
      [['D2', 8], [null, 8]],
      // bar 8
      [['A1', 8], ['D2', 8]],
      // bar 9
      [['D2', 8], ['F2', 8]],
      // bar 10
      [['G2', 8], [null, 4], ['F2', 4]],
      // bar 11
      [['E2', 8], [null, 8]],
      // bar 12
      [['A1', 8], ['D2', 8]],
      // bar 13
      [['D2', 4], [null, 4], ['D2', 4], [null, 4]],
      // bar 14
      [['D2', 4], [null, 4], ['A1', 8]],
      // bar 15
      [['D2', 8], ['C2', 8]],
      // bar 16
      [['A1', 16]],
      // bar 17
      [['F2', 4], [null, 4], ['F2', 8]],
      // bar 18
      [['G2', 4], [null, 4], ['G2', 8]],
      // bar 19
      [['A1', 4], [null, 4], ['A1', 4], ['Bb1', 4]],
      // bar 20
      [['A1', 16]],
      // bar 21
      [['D2', 8], ['A1', 8]],
      // bar 22
      [['F2', 8], ['E2', 8]],
      // bar 23
      [['D2', 16]],
      // bar 24
      [['D2', 8], [null, 8]],
    ),

    noise: bars(
      // ---- Cadence A ----
      // bar 1
      [['kick', 4], ['snare', 2], ['snare', 2], ['kick', 4], ['snare', 1], ['snare', 1], ['snare', 2]],
      // bar 2
      [['kick', 4], ['snare', 2], ['hat', 2], ['kick', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['snare', 2]],
      // bar 3 — diddles
      [['kick', 2], ['snare', 1], ['snare', 1], ['snare', 2], ['snare', 2], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 2], ['hat', 2]],
      // bar 4 — roll
      [['kick', 4], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['kick', 2], ['hat', 2]],
      // bar 5
      [['kick', 4], ['snare', 2], ['snare', 2], ['kick', 2], ['kick', 2], ['snare', 2], ['snare', 1], ['snare', 1]],
      // bar 6
      [['kick', 2], ['hat', 2], ['snare', 4], ['kick', 4], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1]],
      // bar 7 — syncopated
      [['kick', 2], ['snare', 2], ['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 2], ['kick', 2], ['hat', 2]],
      // bar 8 — fill
      [['kick', 4], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2]],

      // ---- Cadence B (tighter) ----
      // bar 9
      [['kick', 2], ['snare', 1], ['snare', 1], ['snare', 4], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 2], ['hat', 2]],
      // bar 10
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['hat', 2], ['snare', 2], ['snare', 2]],
      // bar 11
      [['kick', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['snare', 2], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 2], ['hat', 2]],
      // bar 12
      [['kick', 4], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 2]],
      // bar 13
      [['kick', 2], ['kick', 2], ['snare', 2], ['hat', 2], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 2], ['hat', 2]],
      // bar 14
      [['kick', 4], ['snare', 2], ['snare', 2], ['kick', 1], ['kick', 1], ['snare', 2], ['snare', 1], ['snare', 1], ['hat', 2]],
      // bar 15
      [['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 2], ['hat', 2]],
      // bar 16 — long roll
      [['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['kick', 2], ['hat', 2]],

      // ---- Build, then drop ----
      // bar 17 — driving eighths
      [['kick', 2], ['snare', 2], ['kick', 2], ['snare', 2], ['kick', 2], ['snare', 2], ['kick', 2], ['snare', 2]],
      // bar 18
      [['kick', 2], ['snare', 2], ['kick', 2], ['snare', 2], ['kick', 2], ['snare', 2], ['kick', 2], ['snare', 2]],
      // bar 19
      [['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1]],
      // bar 20
      [['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1]],
      // bar 21
      [['kick', 4], ['snare', 4], ['kick', 4], ['snare', 2], ['hat', 2]],
      // bar 22
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 4], ['snare', 2], ['hat', 2]],
      // bar 23 — final roll
      [['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1]],
      // bar 24 — drop, leave air for the loop
      [['kick', 8], ['snare', 4], ['hat', 2], [null, 2]],
    ),
  },
};

export default song;
