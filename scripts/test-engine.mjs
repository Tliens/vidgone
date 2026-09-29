// Engine unit test — runs the page's engine script in Node (no DOM needed).
// Usage: node scripts/test-engine.mjs
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const html = readFileSync(join(root, 'index.html'), 'utf8');
const m = html.match(/<script id="engineSrc">([\s\S]*?)<\/script>/);
if (!m) { console.error('engine script not found in index.html'); process.exit(1); }
const src = m[1];
const VG = new Function('window', src + '\nreturn window.VG_ENGINE;')({});

let failed = 0;
const ok = (cond, name, extra = '') => {
  console.log((cond ? '  ✓ ' : '  ✗ ') + name + (extra ? '  — ' + extra : ''));
  if (!cond) failed++;
};

function psnr(a, b) {
  let mse = 0, n = 0;
  for (let i = 0; i < a.length; i++) { const d = a[i] - b[i]; mse += d * d; n++; }
  if (!n) return 100;
  mse /= n;
  return mse === 0 ? 100 : 10 * Math.log10(255 * 255 / mse);
}

// synthetic scene: smooth diagonal gradient + soft radial blob (no high-freq texture)
const W = 120, H = 120;
function scene() {
  const d = new Uint8ClampedArray(W * H * 4);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = (y * W + x) * 4;
    const blob = 90 * Math.exp(-(((x - 78) ** 2 + (y - 40) ** 2) / 900));
    d[i] = 30 + x * 0.9 + blob; d[i + 1] = 60 + y * 0.7 + blob * .6; d[i + 2] = 110 + (x + y) * 0.35;
    d[i + 3] = 255;
  }
  return d;
}
function runCase(mode, hx, hy, hw, hh, threshold, name) {
  const orig = scene();
  const img = { data: orig.slice(), width: W, height: H };
  const mask = new Uint8Array(W * H);
  for (let y = hy; y < hy + hh; y++) for (let x = hx; x < hx + hw; x++) mask[y * W + x] = 255;
  const gt = [];
  for (let y = hy; y < hy + hh; y++) for (let x = hx; x < hx + hw; x++) {
    const i = (y * W + x) * 4; gt.push(orig[i], orig[i + 1], orig[i + 2]);
  }
  const t0 = performance.now();
  const res = VG.process(img, mask, { mode });
  const ms = performance.now() - t0;
  const out = [];
  for (let y = hy; y < hy + hh; y++) for (let x = hx; x < hx + hw; x++) {
    const i = (y * W + x) * 4; out.push(img.data[i], img.data[i + 1], img.data[i + 2]);
  }
  const p = psnr(gt, out);
  ok(res.changed && p >= threshold, name, `PSNR ${p.toFixed(1)}dB (≥${threshold}) ${ms.toFixed(0)}ms`);
  return { p, ms };
}

console.log('VidGone engine tests');
console.log('  [quality — center hole 26x26 on smooth scene]');
runCase('fast', 47, 47, 26, 26, 16, 'fast');
runCase('std', 47, 47, 26, 26, 20, 'std');
runCase('fine', 47, 47, 26, 26, 22, 'fine');

console.log('  [edge cases]');
runCase('std', 0, 40, 22, 30, 16, 'hole touching left border');
runCase('std', 47, 47, 48, 48, 14, 'large hole 40% of region');
const blur = runCase('blur', 47, 47, 26, 26, 8, 'blur mode (smoothing)');

{
  // empty mask → untouched
  const orig = scene();
  const img = { data: orig.slice(), width: W, height: H };
  const res = VG.process(img, new Uint8Array(W * H), { mode: 'std' });
  ok(!res.changed, 'empty mask is a no-op');
}
{
  // full mask → guarded no-op (no crash, no garbage)
  const orig = scene();
  const img = { data: orig.slice(), width: W, height: H };
  const res = VG.process(img, new Uint8Array(W * H).fill(255), { mode: 'std' });
  ok(res.tooBig === true, 'full-region mask is guarded');
}
{
  // perf: 240x180 std region should stay fast
  const W2 = 240, H2 = 180;
  const d = new Uint8ClampedArray(W2 * H2 * 4);
  for (let i = 0; i < W2 * H2; i++) { d[i*4] = (i*7)%255; d[i*4+1] = (i*13)%255; d[i*4+2] = (i*29)%255; d[i*4+3]=255; }
  const img = { data: d, width: W2, height: H2 };
  const mask = new Uint8Array(W2 * H2);
  for (let y = 60; y < 120; y++) for (let x = 80; x < 170; x++) mask[y*W2+x] = 255;
  const t0 = performance.now();
  VG.process(img, mask, { mode: 'std' });
  const ms = performance.now() - t0;
  ok(ms < 400, 'perf: 240x180 std < 400ms', ms.toFixed(0) + 'ms');
}
{
  // scratch reuse: second call after first still correct (module-level buffers reused)
  const r1 = runCase('std', 47, 47, 26, 26, 20, 'repeat call #1 (scratch reuse)');
  const r2 = runCase('std', 10, 10, 20, 20, 20, 'repeat call #2 (different hole)');
  ok(Math.abs(r1.p - r2.p) < 25 || (r1.p >= 20 && r2.p >= 20), 'scratch reuse stable');
}

console.log(failed ? `\nFAILED: ${failed}` : '\nALL PASSED');
process.exit(failed ? 1 : 0);
