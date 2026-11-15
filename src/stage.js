import { VIEW_W, VIEW_H, WORLD_W } from './config.js';
import { layerScale } from './assets.js';
// Parallax stage. cam = left edge of the view in world px (0..WORLD_W-VIEW_W). Each layer scrolls across its own
// extra width: far 640 (fixed), mid 960 (x=-160 when centred), near 1120 (x=-240 when centred, in front of fighters).
function layer(ctx, img, cam) {
  const span = WORLD_W - VIEW_W, s = layerScale(img), w = img.width * s;
  const off = span > 0 ? -cam * Math.max(0, w - VIEW_W) / span : 0;
  ctx.drawImage(img, Math.round(off), 0, Math.round(w), VIEW_H);
}
function animFrame(list, frame, fps) { return list && list.length ? list[Math.floor(frame * fps / 60) % list.length] : null; }
export function drawStageBack(ctx, art, cam, frame) {
  const L = art.animLayers || { [art.animLayer || 'mid']: art.anims || [] }, fps = art.animFps || 1000 / 120;
  layer(ctx, art.far, cam); const fa = animFrame(L.far, frame, fps); if (fa) layer(ctx, fa, cam);
  layer(ctx, art.mid, cam); const ma = animFrame(L.mid, frame, fps); if (ma) layer(ctx, ma, cam);
}
export function drawStageFront(ctx, art, cam, frame) {
  const L = art.animLayers || {}, fps = art.animFps || 1000 / 120;
  if (art.near) layer(ctx, art.near, cam); const na = animFrame(L.near, frame, fps); if (na) layer(ctx, na, cam);
}
export function drawStage(ctx, art, cam, frame) { drawStageBack(ctx, art, cam, frame); drawStageFront(ctx, art, cam, frame); }
