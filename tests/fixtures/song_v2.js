// Extended (format 2) song fixture: 8 voices, instruments map, per-voice mix, echo, object channel + chord + velocity.
const bar = (n) => [[n, 4], [null, 4], [n, 4], [null, 4]];
export const song = {
  format: 2, bpm: 132, loop: true,
  instruments: { lead: 'trumpet-lead', section: 'brass-section', bass: 'tuba-bass', bells: 'glockenspiel', snare: 'snare', bd: 'bass-drum', cym: 'cymbals' },
  mix: { lead: { volume: 0.8, pan: -0.4 }, section: { volume: 0.5, pan: 0.4 }, bass: { volume: 0.9, pan: 0 }, bells: { volume: 0.4, pan: 0.6 },
         snare: { volume: 0.7, pan: -0.15 }, bd: { volume: 0.9, pan: 0 }, cym: { volume: 0.4, pan: 0.25 } },
  echo: { delay: 0.3, feedback: 0.4, mix: 0.3 },
  channels: {
    lead: [['C5', 4], ['E5', 4], ['G5', 4], ['C6', 4, 0.7]],
    section: [[['C4', 'E4', 'G4'], 8], [['F4', 'A4', 'C5'], 8]],
    bass: bar('C2'),
    bells: [['G6', 2], [null, 6], ['E6', 2], [null, 6]],
    snare: [['hit', 4], ['rim', 4], ['flam', 4], ['roll', 4]],
    bd: [['kick', 4], [null, 4], ['G1', 4], [null, 4]],
    cym: [['crash', 8], ['choke', 4], ['ride', 4]],
    horn: { instrument: 'horn', volume: 0.5, pan: -0.7, echo: 0.6, notes: [['G4', 8], ['A4', 8]] },
  },
};
export const legacy = { bpm: 132, loop: true, channels: { pulse1: [['C5', 16]], pulse2: [['E4', 16]], triangle: [['C2', 16]], noise: [['kick', 4], ['snare', 4], ['hat', 4], ['G3', 4]] } };
export default song;
