/**
 * Band Wars — football-field-at-night stage theme
 * id: football
 *
 * Marching-band fight song rendered as NES chiptune.
 * Key: Bb major. Tempo: 156 BPM. 4/4.
 *
 * Structure (in 16-step bars / sixteenths):
 *   Intro  bars  1–4   (64 sixteenths)  drum-line cadence + brass charge
 *   A      bars  5–12  (128 sixteenths) main hook
 *   A'     bars 13–20  (128 sixteenths) hook variation / flourish
 *   B      bars 21–28  (128 sixteenths) contrasting trio, then stadium stabs
 * Loop starts at sixteenth 64 (downbeat of A) so the intro plays once.
 * Loop body is 24 bars = 384 sixteenths ≈ 36.92s at 156 BPM.
 *
 * Channels:
 *   pulse1  — brass fanfare lead (square, 50% duty in the preview renderer)
 *   pulse2  — horn-line harmony in thirds / sixths (square, 25% duty)
 *   triangle — tuba / sousaphone bassline
 *   noise   — drumline. Note names:
 *              'kick'  bass drum
 *              'snare' snare (rolls / diddles / flam-feel = rapid snares)
 *              'hat'   cymbal choke / closed hat
 *              or a pitch name (e.g. 'G3') for pitched percussion
 *   null    — rest
 * Each event is [noteName | null, lengthInSixteenths].
 * Every channel totals the same number of sixteenths.
 *
 * `loop`: number = loop-start in sixteenths (intro is not repeated).
 *         Use `true` to loop from the beginning.
 */

function bars(...measures) {
  const notes = [];
  measures.forEach((m, i) => {
    const sum = m.reduce((acc, ev) => acc + ev[1], 0);
    if (sum !== 16) {
      throw new Error(`football: bar ${i + 1} is ${sum} sixteenths, expected 16`);
    }
    notes.push(...m);
  });
  return notes;
}

export const song = {
  bpm: 156,
  loop: 64,
  channels: {
    pulse1: bars(
      // ---- Intro ----
      // bar 1
      [[null, 16]],
      // bar 2 (pickup arpeggio)
      [[null, 8], ['F4', 2], ['Bb4', 2], ['D5', 2], ['F5', 2]],
      // bar 3 (charge hits)
      [['Bb5', 4], [null, 2], ['F5', 2], ['Bb5', 4], [null, 2], ['F5', 2]],
      // bar 4 (descend + pickup into the hook)
      [['D6', 2], ['Bb5', 2], ['F5', 2], ['D5', 2], ['F5', 4], [null, 2], ['F4', 2]],

      // ---- A : main hook ----
      // bar 5
      [['F4', 2], ['Bb4', 2], ['D5', 2], ['F5', 2], ['F5', 4], ['Eb5', 2], ['D5', 2]],
      // bar 6
      [['C5', 2], ['D5', 2], ['Eb5', 2], ['C5', 2], ['D5', 8]],
      // bar 7
      [['Bb4', 2], ['D5', 2], ['F5', 2], ['Bb5', 2], ['A5', 4], ['G5', 2], ['F5', 2]],
      // bar 8
      [['Eb5', 2], ['F5', 2], ['G5', 2], ['Eb5', 2], ['F5', 8]],
      // bar 9
      [['F4', 2], ['Bb4', 2], ['D5', 2], ['F5', 2], ['F5', 4], ['Eb5', 2], ['D5', 2]],
      // bar 10
      [['C5', 2], ['D5', 2], ['Eb5', 2], ['G5', 2], ['F5', 8]],
      // bar 11
      [['F5', 2], ['G5', 2], ['A5', 2], ['Bb5', 2], ['C6', 4], ['Bb5', 2], ['A5', 2]],
      // bar 12
      [['G5', 2], ['F5', 2], ['Eb5', 2], ['C5', 2], ['Bb4', 8]],

      // ---- A' : hook variation ----
      // bar 13
      [['F4', 2], ['Bb4', 2], ['D5', 2], ['F5', 2], ['F5', 2], ['G5', 2], ['A5', 2], ['Bb5', 2]],
      // bar 14
      [['C6', 2], ['Bb5', 2], ['A5', 2], ['G5', 2], ['F5', 8]],
      // bar 15
      [['D5', 2], ['F5', 2], ['Bb5', 2], ['D6', 2], ['C6', 4], ['Bb5', 2], ['A5', 2]],
      // bar 16
      [['G5', 2], ['A5', 2], ['Bb5', 2], ['G5', 2], ['F5', 8]],
      // bar 17
      [['F4', 2], ['Bb4', 2], ['D5', 2], ['F5', 2], ['F5', 4], ['Eb5', 2], ['D5', 2]],
      // bar 18
      [['Eb5', 2], ['D5', 2], ['C5', 2], ['Eb5', 2], ['D5', 4], ['C5', 2], ['Bb4', 2]],
      // bar 19
      [['C5', 2], ['D5', 2], ['Eb5', 2], ['F5', 2], ['G5', 4], ['F5', 2], ['Eb5', 2]],
      // bar 20
      [['D5', 4], ['F5', 4], ['Bb5', 8]],

      // ---- B : trio + stadium stabs ----
      // bar 21
      [['Eb5', 6], ['D5', 2], ['C5', 4], ['Bb4', 4]],
      // bar 22
      [['C5', 6], ['Bb4', 2], ['A4', 4], ['F4', 4]],
      // bar 23
      [['Bb4', 2], ['C5', 2], ['D5', 2], ['Eb5', 2], ['F5', 4], ['Eb5', 2], ['D5', 2]],
      // bar 24
      [['C5', 4], ['A4', 4], ['F4', 8]],
      // bar 25
      [['Bb4', 2], [null, 2], ['D5', 2], [null, 2], ['F5', 2], [null, 2], ['Bb5', 4]],
      // bar 26
      [['A5', 2], [null, 2], ['G5', 2], [null, 2], ['F5', 4], ['Eb5', 4]],
      // bar 27
      [['F5', 2], ['G5', 2], ['A5', 2], ['Bb5', 2], ['C6', 2], ['Bb5', 2], ['A5', 2], ['G5', 2]],
      // bar 28
      [['F5', 4], ['D5', 4], ['Bb4', 6], [null, 2]],
    ),

    pulse2: bars(
      // bar 1
      [[null, 16]],
      // bar 2
      [[null, 8], ['D4', 2], ['F4', 2], ['Bb4', 2], ['D5', 2]],
      // bar 3
      [['G5', 4], [null, 2], ['D5', 2], ['G5', 4], [null, 2], ['D5', 2]],
      // bar 4
      [['Bb5', 2], ['G5', 2], ['D5', 2], ['Bb4', 2], ['A4', 4], [null, 2], ['D4', 2]],

      // bar 5
      [['D4', 2], ['F4', 2], ['Bb4', 2], ['D5', 2], ['D5', 4], ['C5', 2], ['Bb4', 2]],
      // bar 6
      [['A4', 2], ['Bb4', 2], ['C5', 2], ['A4', 2], ['Bb4', 8]],
      // bar 7
      [['F4', 2], ['Bb4', 2], ['D5', 2], ['F5', 2], ['F5', 4], ['Eb5', 2], ['D5', 2]],
      // bar 8
      [['C5', 2], ['D5', 2], ['Eb5', 2], ['C5', 2], ['D5', 8]],
      // bar 9
      [['D4', 2], ['F4', 2], ['Bb4', 2], ['D5', 2], ['D5', 4], ['C5', 2], ['Bb4', 2]],
      // bar 10
      [['A4', 2], ['Bb4', 2], ['C5', 2], ['Eb5', 2], ['D5', 8]],
      // bar 11
      [['D5', 2], ['Eb5', 2], ['F5', 2], ['G5', 2], ['A5', 4], ['G5', 2], ['F5', 2]],
      // bar 12
      [['Eb5', 2], ['D5', 2], ['C5', 2], ['A4', 2], ['F4', 8]],

      // bar 13
      [['D4', 2], ['F4', 2], ['Bb4', 2], ['D5', 2], ['D5', 2], ['Eb5', 2], ['F5', 2], ['G5', 2]],
      // bar 14
      [['A5', 2], ['G5', 2], ['F5', 2], ['Eb5', 2], ['D5', 8]],
      // bar 15
      [['Bb4', 2], ['D5', 2], ['F5', 2], ['Bb5', 2], ['A5', 4], ['G5', 2], ['F5', 2]],
      // bar 16
      [['Eb5', 2], ['F5', 2], ['G5', 2], ['Eb5', 2], ['D5', 8]],
      // bar 17
      [['D4', 2], ['F4', 2], ['Bb4', 2], ['D5', 2], ['D5', 4], ['C5', 2], ['Bb4', 2]],
      // bar 18
      [['C5', 2], ['Bb4', 2], ['A4', 2], ['C5', 2], ['Bb4', 4], ['A4', 2], ['G4', 2]],
      // bar 19
      [['A4', 2], ['Bb4', 2], ['C5', 2], ['D5', 2], ['Eb5', 4], ['D5', 2], ['C5', 2]],
      // bar 20
      [['Bb4', 4], ['D5', 4], ['F5', 8]],

      // bar 21
      [['G4', 6], ['F4', 2], ['A4', 4], ['G4', 4]],
      // bar 22
      [['A4', 6], ['G4', 2], ['F4', 4], ['C4', 4]],
      // bar 23
      [['G4', 2], ['A4', 2], ['Bb4', 2], ['C5', 2], ['D5', 4], ['C5', 2], ['Bb4', 2]],
      // bar 24
      [['A4', 4], ['F4', 4], ['C4', 8]],
      // bar 25
      [['F4', 2], [null, 2], ['Bb4', 2], [null, 2], ['D5', 2], [null, 2], ['F5', 4]],
      // bar 26
      [['F5', 2], [null, 2], ['Eb5', 2], [null, 2], ['D5', 4], ['C5', 4]],
      // bar 27
      [['D5', 2], ['Eb5', 2], ['F5', 2], ['G5', 2], ['A5', 2], ['G5', 2], ['F5', 2], ['Eb5', 2]],
      // bar 28
      [['D5', 4], ['Bb4', 4], ['F4', 6], [null, 2]],
    ),

    triangle: bars(
      // bar 1
      [[null, 16]],
      // bar 2
      [['Bb2', 4], [null, 4], ['Bb2', 4], [null, 4]],
      // bar 3
      [['Bb2', 4], ['Bb2', 4], ['F2', 4], ['Bb2', 4]],
      // bar 4
      [['F2', 4], ['F2', 4], ['F2', 2], ['F2', 2], ['F2', 4]],

      // bar 5
      [['Bb2', 4], ['Bb2', 4], ['Bb2', 4], ['F2', 4]],
      // bar 6
      [['Eb2', 4], ['Eb2', 4], ['F2', 4], ['F2', 4]],
      // bar 7
      [['Bb2', 4], ['D3', 4], ['F2', 4], ['Bb2', 4]],
      // bar 8
      [['Eb2', 4], ['Eb2', 4], ['F2', 4], ['F2', 4]],
      // bar 9
      [['Bb2', 4], ['Bb2', 4], ['Bb2', 4], ['F2', 4]],
      // bar 10
      [['Eb2', 4], ['Eb2', 4], ['F2', 8]],
      // bar 11
      [['F2', 4], ['F2', 4], ['F2', 2], ['G2', 2], ['A2', 4]],
      // bar 12
      [['Bb2', 4], ['F2', 4], ['Bb2', 8]],

      // bar 13
      [['Bb2', 4], ['Bb2', 2], ['F2', 2], ['Bb2', 4], ['D3', 4]],
      // bar 14
      [['Eb2', 4], ['F2', 4], ['Bb2', 8]],
      // bar 15
      [['Bb2', 4], ['D3', 4], ['F2', 4], ['Bb2', 4]],
      // bar 16
      [['Eb2', 4], ['C3', 2], ['Eb2', 2], ['F2', 8]],
      // bar 17
      [['Bb2', 4], ['Bb2', 4], ['F2', 4], ['Bb2', 4]],
      // bar 18
      [['Eb2', 4], ['Eb2', 4], ['Bb2', 4], ['Bb2', 4]],
      // bar 19
      [['F2', 4], ['F2', 4], ['C3', 4], ['F2', 4]],
      // bar 20
      [['Bb2', 4], ['F2', 4], ['Bb2', 8]],

      // bar 21
      [['Eb2', 8], ['Eb2', 4], ['G2', 4]],
      // bar 22
      [['F2', 8], ['F2', 4], ['C3', 4]],
      // bar 23
      [['Bb2', 4], ['F2', 4], ['G2', 4], ['D3', 4]],
      // bar 24
      [['F2', 4], ['C3', 4], ['F2', 8]],
      // bar 25
      [['Bb2', 4], [null, 4], ['F2', 4], [null, 4]],
      // bar 26
      [['F2', 4], [null, 4], ['Eb2', 8]],
      // bar 27
      [['F2', 2], ['F2', 2], ['G2', 2], ['A2', 2], ['Bb2', 2], ['C3', 2], ['D3', 2], ['Eb3', 2]],
      // bar 28
      [['F2', 4], ['F2', 4], ['Bb2', 6], [null, 2]],
    ),

    noise: bars(
      // bar 1 — snare solo cadence
      [['snare', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['snare', 2], ['snare', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['snare', 2]],
      // bar 2 — bass drum joins
      [['kick', 2], ['snare', 2], ['kick', 1], ['snare', 1], ['snare', 2], ['kick', 2], ['snare', 2], ['kick', 1], ['snare', 1], ['snare', 2]],
      // bar 3 — diddle / roll feel
      [['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1]],
      // bar 4 — 8-stroke roll into A
      [['kick', 4], ['snare', 2], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1]],

      // bar 5 — street beat (kick 1 & 3, snare diddles on 2 & 4)
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1]],
      // bar 6
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['kick', 2], ['snare', 2], ['hat', 2]],
      // bar 7
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1]],
      // bar 8 — fill
      [['kick', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2]],
      // bar 9
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1]],
      // bar 10
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['kick', 2], ['snare', 2], ['hat', 2]],
      // bar 11
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 4], ['snare', 2], ['hat', 2]],
      // bar 12 — roll fill
      [['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['kick', 2]],

      // bar 13 — busier hats
      [['kick', 2], ['hat', 2], ['snare', 2], ['hat', 2], ['kick', 2], ['hat', 2], ['snare', 2], ['hat', 2]],
      // bar 14
      [['kick', 2], ['hat', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['kick', 2], ['snare', 2], ['hat', 2]],
      // bar 15
      [['kick', 2], ['hat', 2], ['snare', 2], ['hat', 2], ['kick', 2], ['hat', 2], ['snare', 2], ['hat', 2]],
      // bar 16
      [['kick', 2], ['snare', 2], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2], ['kick', 2]],
      // bar 17
      [['kick', 2], ['hat', 2], ['snare', 2], ['hat', 2], ['kick', 2], ['hat', 2], ['snare', 2], ['hat', 2]],
      // bar 18
      [['kick', 2], ['hat', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['kick', 2], ['snare', 2], ['hat', 2]],
      // bar 19
      [['kick', 2], ['hat', 2], ['snare', 2], ['hat', 2], ['kick', 2], ['kick', 2], ['snare', 1], ['snare', 1], ['hat', 2]],
      // bar 20
      [['kick', 4], ['snare', 2], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2]],

      // bar 21 — more open under the trio
      [['kick', 4], [null, 2], ['hat', 2], ['snare', 4], ['kick', 2], ['hat', 2]],
      // bar 22
      [['kick', 4], [null, 2], ['hat', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['hat', 2]],
      // bar 23
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1]],
      // bar 24
      [['kick', 4], ['snare', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2]],
      // bar 25 — stabs with the horns
      [['kick', 2], [null, 2], ['kick', 2], [null, 2], ['kick', 2], [null, 2], ['kick', 2], ['snare', 2]],
      // bar 26
      [['kick', 2], [null, 2], ['kick', 2], [null, 2], ['kick', 4], ['snare', 2], ['hat', 2]],
      // bar 27 — build
      [['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1], ['kick', 2], ['snare', 1], ['snare', 1]],
      // bar 28 — roll, then air so the looped A downbeat can land
      [['kick', 4], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2], [null, 2]],
    ),
  },
};

export default song;
