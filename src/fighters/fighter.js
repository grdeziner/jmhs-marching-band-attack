/**
 * Fighter-loader stub.
 *
 * One fighter id is shared by every lane:
 *   content/roster.json                         select-screen name and placeholder
 *   content/characters/<id>.json                backstory
 *   art/characters/<id>/sheet.png               576×1120 sprite sheet
 *   art/characters/<id>/sheet.json              frame map
 *   art/characters/<id>/portrait.png            64×64 portrait
 *
 * Frames are 96×112, face right, and keep their feet on the bottom center
 * of the cell. See CONTRIBUTING.md.
 */

export const fighterModule = Object.freeze({
  status: 'stub',
  frameWidth: 96,
  frameHeight: 112,
  portrait: 64,
});
