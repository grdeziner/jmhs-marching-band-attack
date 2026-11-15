/**
 * Band Wars — post-game fast-food jam
 * id: fastfood
 *
 * Goofy, bouncy, upbeat jam: playful syncopation and a swing-ish shuffle
 * (dotted-eighth + sixteenth = 3+1 sixteenths).
 * Key: F major. Tempo: 140 BPM. 4/4.
 *
 * Structure (in 16-step bars / sixteenths):
 *   A   bars  1–8   (128 sixteenths) bouncy hook
 *   B   bars  9–16  (128 sixteenths) call-and-response, chromatic jokes
 *   A'  bars 17–24  (128 sixteenths) hook reprise and tag
 * Whole pattern loops from the start (`loop: true`).
 * 24 bars = 384 sixteenths ≈ 41.14s at 140 BPM.
 *
 * Channels:
 *   pulse1  — playful lead (square, 50% duty in the preview renderer)
 *   pulse2  — honky harmony / chord stabs in thirds & sixths (square, 25% duty)
 *   triangle — bouncy tuba bass, shuffle pumps and a few walks
 *   noise   — swung kit groove. Note names:
 *              'kick'  bass drum
 *              'snare' snare (rolls / diddles / flam-feel = rapid snares)
 *              'hat'   closed hat / cymbal choke (often the swing skip)
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
      throw new Error(`fastfood: bar ${i + 1} is ${sum} sixteenths, expected 16`);
    }
    notes.push(...m);
  });
  return notes;
}

export const song = {
  bpm: 140,
  loop: true,
  channels: {
    pulse1: bars(
      // ---- A : hook ----
      // bar 1
      [['F4', 2], ['A4', 2], ['C5', 3], ['F5', 1], [null, 2], ['E5', 2], ['D5', 3], ['C5', 1]],
      // bar 2
      [['Bb4', 3], ['A4', 1], ['G4', 2], [null, 2], ['A4', 3], ['Bb4', 1], ['C5', 4]],
      // bar 3
      [['F4', 2], ['A4', 2], ['C5', 3], ['F5', 1], [null, 2], ['G5', 2], ['F5', 3], ['E5', 1]],
      // bar 4
      [['D5', 3], ['E5', 1], ['F5', 2], [null, 2], ['C5', 3], ['A4', 1], ['F4', 4]],
      // bar 5
      [['A4', 3], ['C5', 1], ['F5', 3], ['A5', 1], ['G5', 2], [null, 2], ['F5', 3], ['E5', 1]],
      // bar 6
      [['D5', 3], ['C5', 1], ['Bb4', 2], [null, 2], ['C5', 3], ['D5', 1], ['E5', 4]],
      // bar 7 — chromatic goof
      [['F5', 2], [null, 2], ['E5', 2], [null, 1], ['Eb5', 1], ['D5', 2], [null, 2], ['C5', 4]],
      // bar 8
      [['Bb4', 3], ['A4', 1], ['G4', 3], ['A4', 1], ['F4', 6], [null, 2]],

      // ---- B ----
      // bar 9
      [['C5', 3], [null, 1], ['C5', 3], [null, 1], ['C5', 2], ['D5', 2], ['E5', 2], ['C5', 2]],
      // bar 10 — chromatic slide joke
      [['F5', 3], [null, 1], ['F5', 3], [null, 1], ['E5', 2], ['Eb5', 2], ['D5', 4]],
      // bar 11
      [['Bb4', 3], [null, 1], ['Bb4', 3], [null, 1], ['Bb4', 2], ['A4', 2], ['G4', 2], ['Bb4', 2]],
      // bar 12
      [['A4', 3], ['G4', 1], ['F4', 4], ['G4', 2], [null, 2], ['A4', 4]],
      // bar 13 — syncopated climb
      [['C5', 1], [null, 1], ['C5', 2], ['D5', 1], [null, 1], ['D5', 2], ['E5', 1], [null, 1], ['E5', 2], ['F5', 4]],
      // bar 14
      [['G5', 3], ['F5', 1], ['E5', 3], ['F5', 1], ['D5', 3], ['E5', 1], ['C5', 4]],
      // bar 15 — off-beat stabs
      [[null, 2], ['F5', 2], [null, 2], ['A5', 2], [null, 2], ['F5', 2], [null, 2], ['C5', 2]],
      // bar 16 — turnaround
      [['D5', 3], ['C5', 1], ['Bb4', 3], ['C5', 1], ['A4', 6], [null, 2]],

      // ---- A' ----
      // bar 17 (= bar 1)
      [['F4', 2], ['A4', 2], ['C5', 3], ['F5', 1], [null, 2], ['E5', 2], ['D5', 3], ['C5', 1]],
      // bar 18
      [['Bb4', 3], ['A4', 1], ['G4', 2], [null, 2], ['A4', 3], ['Bb4', 1], ['C5', 4]],
      // bar 19
      [['F4', 2], ['A4', 2], ['C5', 3], ['F5', 1], [null, 2], ['G5', 2], ['F5', 3], ['E5', 1]],
      // bar 20
      [['D5', 3], ['E5', 1], ['F5', 2], [null, 2], ['C5', 3], ['A4', 1], ['F4', 4]],
      // bar 21
      [['A4', 3], ['C5', 1], ['F5', 3], ['A5', 1], ['G5', 2], [null, 2], ['Bb5', 3], ['A5', 1]],
      // bar 22
      [['G5', 3], ['F5', 1], ['E5', 2], [null, 2], ['F5', 3], ['G5', 1], ['A5', 4]],
      // bar 23
      [['Bb5', 3], ['A5', 1], ['G5', 3], ['F5', 1], ['E5', 3], ['D5', 1], ['C5', 2], ['Bb4', 2]],
      // bar 24 — button, loops cleanly back to F
      [['A4', 3], ['G4', 1], ['F4', 4], ['C5', 3], ['A4', 1], ['F4', 4]],
    ),

    pulse2: bars(
      // bar 1 — thirds / sixths under the hook
      [['C4', 2], ['F4', 2], ['A4', 3], ['C5', 1], [null, 2], ['G4', 2], ['Bb4', 3], ['A4', 1]],
      // bar 2
      [['G4', 3], ['F4', 1], ['E4', 2], [null, 2], ['F4', 3], ['G4', 1], ['A4', 4]],
      // bar 3
      [['C4', 2], ['F4', 2], ['A4', 3], ['C5', 1], [null, 2], ['E5', 2], ['C5', 3], ['C5', 1]],
      // bar 4
      [['Bb4', 3], ['C5', 1], ['D5', 2], [null, 2], ['A4', 3], ['F4', 1], ['C4', 4]],
      // bar 5
      [['F4', 3], ['A4', 1], ['C5', 3], ['F5', 1], ['E5', 2], [null, 2], ['C5', 3], ['C5', 1]],
      // bar 6
      [['Bb4', 3], ['A4', 1], ['G4', 2], [null, 2], ['A4', 3], ['Bb4', 1], ['C5', 4]],
      // bar 7
      [['C5', 2], [null, 2], ['Bb4', 2], [null, 1], ['A4', 1], ['Bb4', 2], [null, 2], ['A4', 4]],
      // bar 8
      [['G4', 3], ['F4', 1], ['E4', 3], ['F4', 1], ['C4', 6], [null, 2]],

      // bar 9
      [['E4', 3], [null, 1], ['E4', 3], [null, 1], ['E4', 2], ['F4', 2], ['G4', 2], ['E4', 2]],
      // bar 10
      [['A4', 3], [null, 1], ['A4', 3], [null, 1], ['G4', 2], ['Gb4', 2], ['F4', 4]],
      // bar 11
      [['D4', 3], [null, 1], ['D4', 3], [null, 1], ['D4', 2], ['C4', 2], ['Bb3', 2], ['D4', 2]],
      // bar 12
      [['C4', 3], ['Bb3', 1], ['A3', 4], ['Bb3', 2], [null, 2], ['C4', 4]],
      // bar 13
      [['A4', 1], [null, 1], ['A4', 2], ['Bb4', 1], [null, 1], ['Bb4', 2], ['C5', 1], [null, 1], ['C5', 2], ['A4', 4]],
      // bar 14
      [['E5', 3], ['D5', 1], ['C5', 3], ['D5', 1], ['Bb4', 3], ['C5', 1], ['A4', 4]],
      // bar 15 — off-beat stabs with the lead
      [[null, 2], ['C5', 2], [null, 2], ['F5', 2], [null, 2], ['C5', 2], [null, 2], ['A4', 2]],
      // bar 16
      [['Bb4', 3], ['A4', 1], ['G4', 3], ['A4', 1], ['F4', 6], [null, 2]],

      // bar 17
      [['C4', 2], ['F4', 2], ['A4', 3], ['C5', 1], [null, 2], ['G4', 2], ['Bb4', 3], ['A4', 1]],
      // bar 18
      [['G4', 3], ['F4', 1], ['E4', 2], [null, 2], ['F4', 3], ['G4', 1], ['A4', 4]],
      // bar 19
      [['C4', 2], ['F4', 2], ['A4', 3], ['C5', 1], [null, 2], ['E5', 2], ['C5', 3], ['C5', 1]],
      // bar 20
      [['Bb4', 3], ['C5', 1], ['D5', 2], [null, 2], ['A4', 3], ['F4', 1], ['C4', 4]],
      // bar 21
      [['F4', 3], ['A4', 1], ['C5', 3], ['F5', 1], ['E5', 2], [null, 2], ['G5', 3], ['F5', 1]],
      // bar 22
      [['E5', 3], ['D5', 1], ['C5', 2], [null, 2], ['D5', 3], ['E5', 1], ['F5', 4]],
      // bar 23
      [['G5', 3], ['F5', 1], ['E5', 3], ['D5', 1], ['C5', 3], ['Bb4', 1], ['A4', 2], ['G4', 2]],
      // bar 24
      [['F4', 3], ['E4', 1], ['C4', 4], ['A4', 3], ['F4', 1], ['C4', 4]],
    ),

    triangle: bars(
      // shuffle tuba: root on the beat, fifth on the swung skip of beat 2 / 4
      // bar 1
      [['F2', 3], [null, 1], ['C3', 4], ['F2', 3], [null, 1], ['C3', 4]],
      // bar 2
      [['Bb2', 3], [null, 1], ['F2', 4], ['C3', 3], [null, 1], ['C3', 4]],
      // bar 3
      [['F2', 3], [null, 1], ['C3', 4], ['F2', 3], [null, 1], ['C3', 4]],
      // bar 4
      [['Bb2', 3], [null, 1], ['C3', 4], ['F2', 8]],
      // bar 5
      [['F2', 3], [null, 1], ['A2', 4], ['C3', 3], [null, 1], ['F2', 4]],
      // bar 6
      [['Bb2', 3], [null, 1], ['F2', 4], ['C3', 3], [null, 1], ['C3', 4]],
      // bar 7 — walk down under the chromatic lick
      [['F2', 4], ['E2', 4], ['D2', 4], ['C3', 4]],
      // bar 8
      [['Bb2', 3], [null, 1], ['C3', 4], ['F2', 6], [null, 2]],

      // bar 9
      [['C3', 3], [null, 1], ['G2', 4], ['C3', 3], [null, 1], ['G2', 4]],
      // bar 10
      [['F2', 3], [null, 1], ['C3', 4], ['F2', 3], [null, 1], ['E2', 4]],
      // bar 11
      [['Bb2', 3], [null, 1], ['F2', 4], ['Bb2', 3], [null, 1], ['G2', 4]],
      // bar 12
      [['F2', 3], [null, 1], ['C3', 4], ['F2', 8]],
      // bar 13
      [['C3', 3], [null, 1], ['C3', 3], [null, 1], ['C3', 3], [null, 1], ['C3', 4]],
      // bar 14
      [['Bb2', 3], [null, 1], ['C3', 4], ['G2', 3], [null, 1], ['C3', 4]],
      // bar 15
      [['F2', 4], ['A2', 4], ['C3', 4], ['F2', 4]],
      // bar 16
      [['Bb2', 3], [null, 1], ['C3', 4], ['F2', 6], [null, 2]],

      // bar 17
      [['F2', 3], [null, 1], ['C3', 4], ['F2', 3], [null, 1], ['C3', 4]],
      // bar 18
      [['Bb2', 3], [null, 1], ['F2', 4], ['C3', 3], [null, 1], ['C3', 4]],
      // bar 19
      [['F2', 3], [null, 1], ['C3', 4], ['F2', 3], [null, 1], ['C3', 4]],
      // bar 20
      [['Bb2', 3], [null, 1], ['C3', 4], ['F2', 8]],
      // bar 21
      [['F2', 3], [null, 1], ['A2', 4], ['C3', 3], [null, 1], ['F2', 4]],
      // bar 22
      [['Bb2', 3], [null, 1], ['C3', 4], ['F2', 3], [null, 1], ['C3', 4]],
      // bar 23 — walk
      [['Bb2', 4], ['A2', 4], ['G2', 4], ['C3', 4]],
      // bar 24
      [['F2', 3], [null, 1], ['C3', 4], ['F2', 8]],
    ),

    noise: bars(
      // swung shuffle: kick/snare on the beat, hat on the 16th skip
      // bar 1
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 2
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 2], ['kick', 1], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 3
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 4 — fill
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['snare', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['hat', 2]],
      // bar 5
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 6
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 2], ['kick', 1], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 7
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 2], ['hat', 2]],
      // bar 8 — fill
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2]],

      // bar 9
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 10
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 2], ['kick', 1], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 11
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 12
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 2], ['snare', 2], ['snare', 2], ['hat', 2]],
      // bar 13
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 14
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 2], ['kick', 1], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 15 — kicks with the off-beat stabs (on the 'and')
      [['kick', 2], ['hat', 2], ['kick', 2], ['hat', 2], ['kick', 2], ['hat', 2], ['kick', 2], ['snare', 2]],
      // bar 16 — fill
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2]],

      // bar 17
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 18
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 2], ['kick', 1], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 19
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 20
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['snare', 2], ['snare', 2], ['snare', 1], ['snare', 1], ['hat', 2]],
      // bar 21
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 22
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 2], ['kick', 1], ['hat', 1], ['snare', 3], ['hat', 1]],
      // bar 23
      [['kick', 3], ['hat', 1], ['snare', 3], ['hat', 1], ['kick', 3], ['hat', 1], ['snare', 2], ['hat', 2]],
      // bar 24 — button fill, air into the loop
      [['kick', 3], ['hat', 1], ['snare', 4], ['snare', 1], ['snare', 1], ['snare', 1], ['snare', 1], ['hat', 2], ['kick', 2]],
    ),
  },
};

export default song;
