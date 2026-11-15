/**
 * Scene stub.
 *
 * The placeholder state machine lives in src/main.js (loading, title,
 * select, error). Replace that loop with scene objects when the fight
 * exists. A scene is { enter(ctx), update(dt, input), draw(ctx2d), exit() }.
 *
 * Planned scenes: title, select, fight, ending.
 * select reads content/roster.json.
 * ending reads content/characters/<id>.json.
 */

export const sceneModule = Object.freeze({
  status: 'stub',
  planned: Object.freeze(['title', 'select', 'fight', 'ending']),
});
