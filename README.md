# VidGone — Free Online Video Watermark Remover

**[vidgone.kuige.me](https://vidgone.kuige.me/)** · 免费在线视频去水印

Brush over a static watermark in your video, get a clean MP4 — processed **entirely in your browser** with WebCodecs. No upload, no signup, no limits, free forever.

涂抹框选视频里的静态水印，一键导出干净 MP4——全程在浏览器本地处理（WebCodecs 硬件加速）。不上传、免注册、无限制、永久免费。

## How it works 工作原理

- **Mask editor 蒙版编辑器**: brush / box / eraser over the watermark on any frame（画笔/方框/擦除）
- **Per-frame repair 逐帧修复**: three inpainting tiers (diffusion / directional / multi-scale) + soft blur mode（三档修复引擎 + 柔化）
- **Export 导出**: decode → repair → re-encode H.264 MP4 via [mediabunny](https://mediabunny.dev) + WebCodecs; AAC audio is packet-copied losslessly when possible（AAC 无损直拷）

## Privacy 隐私

Your video never leaves your device. There is no backend — the page is a static file; even the processing library (`mb/mediabunny.min.mjs`) is loaded from the same origin, so it works offline after first load.

视频永不离开你的设备。站点无后端——纯静态页面，处理库同源加载，首次加载后断网也能用。

## Dev 开发

```bash
python3 -m http.server 8981   # local test 本地测试
node scripts/test-engine.mjs  # engine unit tests 修复引擎单测
```

- Single-file app in `index.html` (i18n EN/zh, light/dark, SEO complete)
- Engine is DOM-free and unit-tested (`scripts/test-engine.mjs`)

## Roadmap 二期

Moving/animated watermarks (keyframed masks), platform link parsing (抖音/TikTok/快手/B站/小红书/微博), batch queue.

移动水印（关键帧蒙版）、平台链接解析、批量处理。

---

© 2026 [KuiGe · kuige.me](https://kuige.me/) — part of the free tool matrix · sister site: [MarkGone](https://markgone.kuige.me/) (image watermark remover)
