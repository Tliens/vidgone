#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate VidGone SEO landing pages + rebuild sitemap.xml.

Usage: python3 scripts/gen_pages.py
Pages are static, self-contained HTML (EN-primary, zh summary block).
Regenerating overwrites the generated pages and sitemap.xml.
"""

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://vidgone.kuige.me"

CSS = """
:root{--bg:#faf7f8;--card:#fff;--tx:#241a20;--mut:#84707c;--bd:#eadfe4;--accent:#d63c41;--accent2:#c07a12;--chip:#f7eef1}
@media (prefers-color-scheme:dark){:root{--bg:#141017;--card:#1d171f;--tx:#f4eef2;--mut:#a89aae;--bd:#2c2331;--accent:#e5484d;--accent2:#f5a623;--chip:#241c27}}
*{box-sizing:border-box}
body{margin:0;font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--tx)}
.wrap{max-width:820px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--bd);background:var(--card)}
header .wrap{display:flex;align-items:center;gap:12px;height:56px}
.brand{display:flex;align-items:center;gap:8px;font-weight:800;font-size:18px;color:var(--tx);text-decoration:none}
.brand i{width:24px;height:24px;border-radius:7px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:inline-flex;align-items:center;justify-content:center;color:#fff;font-style:normal;font-weight:900;font-size:13px}
header .cta{margin-left:auto;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;text-decoration:none;font-weight:700;font-size:14px;border-radius:9px;padding:7px 14px}
h1{font-size:clamp(26px,4.6vw,38px);line-height:1.18;letter-spacing:-.5px;margin:38px 0 12px}
.sub{color:var(--mut);font-size:17.5px;margin:0 0 8px}
.lead b{color:var(--tx)}
.card{background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:20px 22px;margin:18px 0}
h2{font-size:22px;margin:30px 0 10px;letter-spacing:-.3px}
p{color:var(--mut)} p b,li b{color:var(--tx)}
ol,ul{color:var(--mut);padding-left:22px} li{margin:7px 0}
.steps li{margin:12px 0}
.faq details{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:12px 17px;margin-bottom:9px}
.faq summary{cursor:pointer;font-weight:700;font-size:15.5px;color:var(--tx)}
.faq p{margin:9px 0 2px}
.cta-card{background:linear-gradient(135deg,rgba(229,72,77,.09),rgba(245,166,35,.09));border:1px solid var(--bd);border-radius:16px;padding:24px;text-align:center;margin:30px 0}
.cta-card .btn{display:inline-block;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;text-decoration:none;font-weight:800;border-radius:12px;padding:12px 26px;font-size:16px}
.cta-card small{display:block;color:var(--mut);margin-top:9px;font-size:13.5px}
.zh{border-top:1px dashed var(--bd);margin-top:30px;padding-top:18px}
.zh h2{font-size:19px} .zh p{font-size:14.5px}
.rel a{color:var(--accent);text-decoration:none;font-weight:600}
footer{border-top:1px solid var(--bd);margin-top:36px;padding:22px 0 34px;color:var(--mut);font-size:13.5px;text-align:center}
footer a{color:var(--accent);text-decoration:none}
"""


def faq_ld(faqs):
    items = ",".join(
        '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}' % (q, a)
        for q, a in faqs
    )
    return ('{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}' % items).replace("\n", " ")


def render_page(pg):
    e = html.escape
    faq_html = "".join(
        f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in pg["faq"]
    )
    rel = " · ".join(
        f'<a href="{BASE}/{p["slug"]}">{e(p["anchor"])}</a>' for p in PAGES if p["slug"] != pg["slug"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(pg['title'])}</title>
<meta name="description" content="{e(pg['description'])}">
<link rel="canonical" href="{BASE}/{pg['slug']}">
<link rel="alternate" hreflang="en" href="{BASE}/{pg['slug']}">
<link rel="alternate" hreflang="x-default" href="{BASE}/{pg['slug']}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(pg['title'])}">
<meta property="og:description" content="{e(pg['description'])}">
<meta property="og:url" content="{BASE}/{pg['slug']}">
<link rel="icon" type="image/png" href="{BASE}/favicon.png?v=2">
<script type="application/ld+json">{faq_ld(pg['faq'])}</script>
<style>{CSS}</style>
</head>
<body>
<header><div class="wrap">
  <a class="brand" href="{BASE}/"><i>V</i>VidGone</a>
  <a class="cta" href="{BASE}/">Open the tool ↗</a>
</div></header>
<main class="wrap">
  <h1>{e(pg['h1'])}</h1>
  <p class="sub">{e(pg['sub'])}</p>

  <div class="card lead">{pg['lead']}</div>

  <h2>{e(pg['h2_1'])}</h2>
  <p>{e(pg['p1'])}</p>

  <h2>How to do it in VidGone (3 steps, nothing uploaded)</h2>
  <ol class="steps">
    <li><b>Open VidGone and drop your video in.</b> The file is read straight from your disk by your own browser — there is no upload step, because there is no server to upload to.</li>
    <li><b>Mark the watermark.</b> Scrub the timeline to the scene with the mark, then brush over it or draw a box. The same mask applies to the whole clip, which is exactly what a fixed-position logo needs.</li>
    <li><b>Export a clean MP4.</b> Every frame is repaired and re-encoded with hardware acceleration (WebCodecs). AAC audio is copied losslessly when the source uses it. Preview the result before downloading.</li>
  </ol>

  <h2>{e(pg['h2_2'])}</h2>
  <p>{e(pg['p2'])}</p>

  <div class="cta-card">
    <a class="btn" href="{BASE}/">Remove the watermark now — free, in your browser</a>
    <small>No account · works offline after first load · MP4 / MOV / WebM</small>
  </div>

  <h2>Frequently asked questions</h2>
  <div class="faq">{faq_html}</div>

  <h2>Related guides</h2>
  <p class="rel">{rel}</p>

  <div class="zh">
    <h2>中文摘要</h2>
    <p>{e(pg['zh_summary'])}</p>
    <p><a href="{BASE}/?lang=zh">打开中文界面 →</a></p>
  </div>
</main>
<footer><div class="wrap">VidGone — free online video watermark remover · Part of <a href="https://kuige.me/">KuiGe Tools</a> · Sister site: <a href="https://markgone.kuige.me/">MarkGone</a> (image watermark remover)</div></footer>
</body>
</html>
"""


PAGES = [
    dict(
        slug="remove-watermark-from-video",
        title="Remove a Watermark from a Video — Without Uploading It | VidGone",
        description="How to remove a watermark from a video without uploading it: a free browser-based remover that repairs frames locally with WebCodecs. Step-by-step guide.",
        h1="How to Remove a Watermark from a Video (Without Uploading It)",
        sub="A practical guide to cleaning watermarks from your own clips — locally, privately, and for free.",
        lead=('Most online removers work the same way: you <b>upload your video to their server</b>, they process it, you download the result. '
              'That means waiting for uploads, file-size limits, and your footage sitting on someone else\'s machine. '
              '<b>VidGone flips the model</b>: the video is opened by your own browser and repaired frame by frame on your device — '
              'there is no upload step at all.'),
        h2_1="What actually works on a burned-in watermark",
        p1=("A watermark that is part of the picture (a platform logo, a channel name, a date stamp) can\'t be deleted — it has to be "
            "reconstructed. VidGone\'s repair engine rebuilds the covered area from the pixels around it, every single frame. "
            "Results are cleanest when the watermark sits on a fairly stable background: sky, walls, water, smooth gradients. "
            "Over busy motion, the Soft-blur mode is often the better trade."),
        h2_2="Free + local + private, not just free",
        p2=("Free is easy to promise. What makes VidGone different is the combination: free <i>and</i> local <i>and</i> private. "
            "Because everything runs in your browser with WebCodecs, there are no per-export fees, no accounts, and no copy of your video anywhere but your own disk."),
        faq=[
            ("Is it really free?", "Yes — free to use with no signup. Processing happens in your browser, so there are no server costs to pass on to you."),
            ("Will the video quality drop?", "The video is re-encoded as H.264 MP4; choose the High quality preset to keep more detail. Audio is copied losslessly when the source uses AAC."),
            ("Does it work on moving watermarks?", "The current version applies one mask to the whole clip, so it targets fixed-position watermarks. Moving watermarks are on the roadmap."),
            ("Is my video uploaded anywhere?", "No. VidGone has no backend — your browser opens the file from your disk and processes every frame locally."),
        ],
        zh_summary="这是一篇教你「不上传视频就去掉水印」的指南：VidGone 在浏览器里用 WebCodecs 逐帧修复画面，视频全程留在本机，免费、免注册。适合去除平台 logo、频道名、日期角标等固定位置水印。",
    ),
    dict(
        slug="remove-logo-from-video",
        title="Remove a Logo from a Video Online — Free & Local | VidGone",
        description="Remove corner logos, channel bugs and station marks from videos without uploading. Local browser-based removal with per-frame inpainting.",
        h1="Remove a Logo from a Video — Corner Bugs, Channel Marks, Station IDs",
        sub="The classic watermark problem: a small logo parked in the corner of every frame. Here's the clean way to deal with it.",
        lead=("Corner logos are the most common watermark: a <b>channel bug</b>, a stock-footage mark, a broadcaster\'s station ID. "
              "Because the logo never moves, one mask fixes every frame — which makes this the case VidGone handles best. "
              "And because nothing is uploaded, even sensitive or unreleased footage stays on your machine."),
        h2_1="Match the removal method to the background",
        p1=("Quick fix (fast diffusion) is ideal when a logo sits on sky, walls or water. Smart repair (directional inpainting) is the best balance for most logos on textured scenes. "
            "Fine repair rebuilds texture at multiple scales — slower, and the strongest on complex backgrounds. If the logo sits on top of important moving detail, Soft blur is the honest fallback."),
        h2_2="Tips that visibly improve the result",
        p2=("Cover slightly beyond the logo\'s edge so the engine anchors on clean pixels; check 3–4 scenes across the timeline before exporting; "
            "and prefer the source resolution — the repair runs at full resolution either way, so there\'s nothing to gain from downscaling first."),
        faq=[
            ("Can it remove a TikTok or Douyin logo?", "Yes — static platform logos are exactly the fixed-position case VidGone is built for. Brush over the mark once; every frame is repaired with the same mask."),
            ("How long does an export take?", "It depends on your device. The pipeline is hardware-accelerated via WebCodecs; on a typical laptop a short 1080p clip exports in well under a minute."),
            ("Is there a watermark on the output?", "No. The exported MP4 is clean — VidGone adds nothing to your video."),
            ("Does it cost anything?", "No. It\'s a free tool; processing runs on your own device."),
        ],
        zh_summary="去除视频角落 logo（频道标、素材站水印、台标）的最佳场景：位置固定 = 一个蒙版管全部帧。涂抹稍大于 logo 边缘、多检查几个镜头、无需上传即可导出干净 MP4。",
    ),
    dict(
        slug="remove-text-from-video",
        title="Remove Text, Captions & Timestamps from a Video | VidGone",
        description="Remove burned-in text overlays, captions and timestamps from videos locally in your browser — no upload, free, frame-by-frame repair.",
        h1="Remove Text, Captions and Timestamps from a Video",
        sub="Burned-in subtitles, date stamps and caption overlays — how to clean them off without sending your footage to a server.",
        lead=("Text that was burned into the picture — hardcoded subtitles, a <b>date/time stamp</b> from a dashcam or camera, "
              "a headline banner — behaves exactly like a logo watermark: it\'s part of the pixels now. "
              "VidGone rebuilds the covered strip of the image on every frame, right in your browser."),
        h2_1="Text is usually the easiest case",
        p1=("Subtitles and timestamps sit in predictable strips with fairly simple surroundings, so the repair engine has clean pixels to work from. "
            "Draw a rectangle over the whole text block (slightly taller than the glyphs), preview a frame, then export. "
            "For dashcam timestamps in the corner, a single box typically handles the entire clip."),
        h2_2="When the text crosses busy motion",
        p2=("If a caption sits on top of faces or fast-moving detail, no tool can rebuild what was never recorded. "
            "There, Soft blur gives an unobtrusive result instead of a smeared patch. For everything else, Smart or Fine repair reconstructs the background convincingly."),
        faq=[
            ("Can it remove hardcoded subtitles?", "Yes — mark the subtitle strip once and the same mask is applied to every frame, so burned-in captions disappear across the whole clip."),
            ("Does it work on dashcam date stamps?", "Yes — corner timestamps on stable backgrounds are one of the cleanest cases for the repair engine."),
            ("Can it remove text that changes wording?", "If the text block stays in the same position, one mask covers all its variations. Text that moves around the frame is a future feature."),
            ("Is anything uploaded?", "No — the whole pipeline runs locally in your browser."),
        ],
        zh_summary="去除烧录在画面里的文字：硬字幕、行车记录仪时间码、标题横幅。框选整块文字区即可全片生效；文字压在剧烈运动画面上时建议用柔化模糊。",
    ),
    dict(
        slug="no-upload-video-watermark-remover",
        title="No-Upload Video Watermark Remover — Your Video Never Leaves Your Device | VidGone",
        description="A video watermark remover with no upload: VidGone processes every frame locally in your browser with WebCodecs. Private by architecture, not by promise.",
        h1="A Video Watermark Remover with No Upload",
        sub="Private by architecture, not by promise — there is no server to upload to.",
        lead=("Your files are safe with us is a promise. <b>VidGone doesn\'t need to make it</b>: the tool is a static web page, "
              "and the entire pipeline — demuxing, decoding, per-frame repair, encoding — runs inside your browser tab with WebCodecs. "
              "Your video is read from your disk, processed in memory, and handed back as a download. Nothing is transmitted, because there is nothing to transmit to."),
        h2_1="Why this matters for real footage",
        p1=("Client cuts, unreleased edits, family videos, internal training clips — the videos people most want to clean are exactly the ones they shouldn\'t upload to a stranger\'s queue. "
            "With local processing the question never comes up: you can even disconnect from the internet after the page loads and keep working."),
        h2_2="How the no-upload pipeline works",
        p2=("The page ships the processing engine from the same origin it\'s served from (with CDN fallbacks). Your browser decodes the video with hardware acceleration, "
            "the repair engine rebuilds each masked frame, and the encoder writes a fresh H.264 MP4 — all in memory on your device. "
            "You can verify it yourself: open your browser\'s network tab while exporting and watch nothing leave."),
        faq=[
            ("How can you prove nothing is uploaded?", "Open your browser\'s developer tools, switch to the Network tab, and run an export — you\'ll see no video traffic. The tool also keeps working offline after the first load."),
            ("Does no-upload mean slower?", "No — quite the opposite on fast connections. There\'s no upload wait and no result download wait; processing speed is limited only by your device."),
            ("Is there a file-size limit?", "There\'s no artificial limit; practical limits come from your device\'s memory, since frames are streamed rather than stored."),
            ("Which browsers support this?", "Any browser with WebCodecs: Chrome and Edge (recommended), Safari 16.4+, Firefox 130+."),
        ],
        zh_summary="无上传 = 架构级隐私：VidGone 是纯静态页面，解码、逐帧修复、编码全部发生在浏览器标签页里，视频从磁盘读取、内存处理、本地下载，加载后断网都能用。",
    ),
    dict(
        slug="free-video-watermark-remover",
        title="Free Video Watermark Remover — Free + Local + Private | VidGone",
        description="What a genuinely free video watermark remover looks like: no signup, no per-export fees, no upload — local WebCodecs processing in your browser.",
        h1="Free Video Watermark Remover — What Free + Local + Private Really Means",
        sub="Most tools are free the way trialware is free. Here's the difference, and why the business model makes it sustainable.",
        lead=("Plenty of sites advertise a free video watermark remover, then gate the actual export behind an account, a subscription, a per-minute fee, or a stamped watermark of their own. "
              "<b>VidGone can afford to be genuinely free because it has almost no costs to gate</b>: the processing happens on your device, not on paid servers."),
        h2_1="The three-part promise",
        p1=("<b>Free</b> — no account, no trial, no per-export pricing, and no watermark added to your output. "
            "<b>Local</b> — frames are repaired by your own browser; nothing is transmitted. "
            "<b>Private</b> — your footage never exists anywhere but your disk, which is a stronger guarantee than any privacy policy."),
        h2_2="Why it can stay free",
        p2=("The site is static — it costs pennies to serve. There\'s no GPU cluster to rent, no upload storage to pay for, no queue to staff. "
            "VidGone is part of the KuiGe Tools family, a collection of free, privacy-first single-purpose tools; the tools funnel traffic to each other instead of charging you."),
        faq=[
            ("What\'s the catch?", "There isn\'t a billing-shaped one. The honest trade-offs are technical: it\'s tuned for fixed-position watermarks, and export speed depends on your device rather than a fast server farm."),
            ("Do I need an account?", "No. There is no signup, no email, no login — open the page and use the tool."),
            ("Are exports limited?", "There are no artificial limits on the tool itself; you\'re bounded only by your device\'s performance and memory."),
            ("Is the output watermark-free?", "Yes — VidGone adds nothing to your video."),
        ],
        zh_summary="真正免费的秘诀是成本结构：处理在你设备上跑，没有 GPU 集群和上传存储要付费。免费 + 本地 + 隐私三位一体，无账号、无次数限制、导出不加任何水印。",
    ),
]

# shared anchors for related links
for pg in PAGES:
    pg["anchor"] = pg["h1"].split("—")[0].split("|")[0].strip()


def rebuild_sitemap():
    today = "2026-09-30"
    urls = [
        ("", "1.0"),
        ("?lang=en", "0.8"),
        ("?lang=zh", "0.8"),
    ]
    for pg in PAGES:
        urls.append((pg["slug"], "0.7"))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for path, pri in urls:
        loc = f"{BASE}/{path}" if path else f"{BASE}/"
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        if not path.startswith("?"):
            lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{loc}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{loc}"/>')
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <priority>{pri}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap.xml rebuilt ({len(urls)} URLs)")


def main():
    for pg in PAGES:
        out = ROOT / f"{pg['slug']}.html"
        out.write_text(render_page(pg), encoding="utf-8")
        print("generated", out.name)
    rebuild_sitemap()


if __name__ == "__main__":
    main()
