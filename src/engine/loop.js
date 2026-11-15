/**
 * Fighting-engine stub.
 *
 * Drop the match simulation in this folder. src/main.js is only the title
 * screen and character select. It does not import this file, so the
 * placeholder keeps running while the engine is added.
 *
 * Expected entry, once the engine is here:
 *   createMatch({ left, right, stage, input }) -> { step(dt), snapshot() }
 *
 * snapshot() positions are in the 320×180 canvas. Fighter feet stand on
 * canvas y=160, which is y=320 in a 640×360 stage file.
 */

export const engineModule = Object.freeze({
  status: 'stub',
  canvas: Object.freeze({ width: 320, height: 180 }),
  floorY: 160,
});
