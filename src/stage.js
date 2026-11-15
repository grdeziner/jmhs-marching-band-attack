import { VIEW_W, VIEW_H, WORLD_W } from './config.js';
import { layerScale } from './assets.js';
// Draws far / mid / anim layers with parallax. cam = left edge of view in world px (0..WORLD_W-VIEW_W).
export function drawStage(ctx, art, cam, frame) {
  const span = WORLD_W - VIEW_W;
  const layer = (img) => { const s = layerScale(img), w = img.width * s; const off = span > 0 ? -cam * Math.max(0, w - VIEW_W) / span : 0;
    ctx.drawImage(img, Math.round(off), 0, Math.round(w), VIEW_H); };
  layer(art.far);
  const anim = art.anims && art.anims.length ? art.anims[Math.floor(frame * 7 / 60) % art.anims.length] : null;
  if (anim && art.animLayer === 'far') layer(anim);
  layer(art.mid);
  if (anim && art.animLayer !== 'far') layer(anim);
}
