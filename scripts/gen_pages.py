#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate VidGone SEO landing pages (bilingual EN/zh) + rebuild sitemap.xml.

Usage: python3 scripts/gen_pages.py
Pages are static, self-contained HTML. EN prefilled (crawlers); `?lang=zh`
swaps every element from data-zh attributes via a tiny inline script.
Regenerating overwrites the generated pages and sitemap.xml.
"""

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://vidgone.kuige.me"
TODAY = "2026-09-30"


def attr(v):
    """Escape for a double-quoted HTML attribute, preserving inner markup."""
    return v.replace("&", "&amp;").replace('"', "&quot;")


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
header .lang{color:var(--mut);text-decoration:none;font-weight:700;font-size:13.5px;border:1px solid var(--bd);border-radius:8px;padding:6px 10px}
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
.hidden{display:none!important}
.rel a{color:var(--accent);text-decoration:none;font-weight:600}
footer{border-top:1px solid var(--bd);margin-top:36px;padding:22px 0 34px;color:var(--mut);font-size:13.5px;text-align:center}
footer a{color:var(--accent);text-decoration:none}
"""

LANG_SCRIPT = """
(function(){
  var u = new URL(location.href);
  var q = u.searchParams.get('lang');
  var stored = null;
  try { stored = localStorage.getItem('vidgone-lang'); } catch(e){}
  var nav = (navigator.language || 'en').toLowerCase().indexOf('zh') === 0 ? 'zh' : 'en';
  var lang = (q === 'zh' || q === 'en') ? q : (stored === 'zh' || stored === 'en' ? stored : nav);
  var root = document.documentElement;
  var link = document.getElementById('langLink');
  if (link){ link.href = lang === 'zh' ? '?lang=en' : '?lang=zh'; link.textContent = lang === 'zh' ? 'EN' : '中文'; }
  if (lang === 'zh'){
    root.lang = 'zh-CN';
    document.title = root.getAttribute('data-title-zh');
    var md = document.querySelector('meta[name="description"]');
    if (md) md.setAttribute('content', root.getAttribute('data-desc-zh'));
    document.querySelectorAll('[data-zh]').forEach(function(el){
      var v = el.getAttribute('data-zh');
      if (v) el.innerHTML = v;
    });
    var zs = document.getElementById('zhSummary');
    if (zs) zs.classList.add('hidden');
  }
  try { localStorage.setItem('vidgone-lang', lang); } catch(e){}
})();
"""

SHARED = {
    "h2_steps": ("How to do it in VidGone (3 steps, nothing uploaded)", "在 VidGone 里三步完成（全程不上传）"),
    "step1": ("Open VidGone and drop your video in. The file is read straight from your disk by your own browser — there is no upload step, because there is no server to upload to.",
              "打开 VidGone，把视频拖进去。文件由你自己的浏览器直接从磁盘读取——不存在上传这一步，因为没有服务器可上传。"),
    "step2": ("Mark the watermark. Scrub the timeline to the scene with the mark, then brush over it or draw a box. The same mask applies to the whole clip, which is exactly what a fixed-position logo needs.",
              "标记水印。拖动时间轴找到有水印的镜头，用画笔涂抹或画个方框。同一蒙版作用于整段视频——位置固定的 logo 正需要这个。"),
    "step3": ("Export a clean MP4. Every frame is repaired and re-encoded with hardware acceleration (WebCodecs). AAC audio is copied losslessly when the source uses it. Preview the result before downloading.",
              "导出干净 MP4。每一帧都经修复并用硬件加速（WebCodecs）重新编码；源音频为 AAC 时无损直拷。下载前可先预览成品。"),
    "cta": ("Remove the watermark now — free, in your browser", "立即去水印——免费，就在你的浏览器里"),
    "cta_small": ("No account · works offline after first load · MP4 / MOV / WebM", "无需账号 · 首次加载后断网可用 · 支持 MP4 / MOV / WebM"),
    "faq_h": ("Frequently asked questions", "常见问题"),
    "rel_h": ("Related guides", "相关指南"),
    "open_tool": ("Open the tool ↗", "打开工具 ↗"),
    "footer": ('VidGone — free online video watermark remover · Part of <a href="https://kuige.me/">KuiGe Tools</a> · Sister site: <a href="https://markgone.kuige.me/">MarkGone</a> (image watermark remover)',
               'VidGone——免费在线视频去水印 · <a href="https://kuige.me/">KuiGe Tools</a> 家族 · 姊妹站：<a href="https://markgone.kuige.me/">MarkGone</a>（图片去水印）'),
}

PAGES = [
    dict(
        slug="remove-watermark-from-video",
        anchor="Remove a watermark from a video — the no-upload way",
        anchor_zh="视频去水印完整指南（无需上传）",
        title="Remove a Watermark from a Video — Without Uploading It | VidGone",
        title_zh="视频去水印完整指南——全程不上传 | VidGone",
        description="How to remove a watermark from a video without uploading it: a free browser-based remover that repairs frames locally with WebCodecs. Step-by-step guide.",
        description_zh="怎么不上传视频就去掉水印：免费的浏览器本地去水印工具，WebCodecs 逐帧修复。分步指南。",
        h1="How to Remove a Watermark from a Video (Without Uploading It)",
        h1_zh="怎么去掉视频里的水印（不用上传）",
        sub="A practical guide to cleaning watermarks from your own clips — locally, privately, and for free.",
        sub_zh="一份实用指南：把自己视频里的水印清理干净——本地、私密、免费。",
        lead=('Most online removers work the same way: you <b>upload your video to their server</b>, they process it, you download the result. '
              'That means waiting for uploads, file-size limits, and your footage sitting on someone else\'s machine. '
              '<b>VidGone flips the model</b>: the video is opened by your own browser and repaired frame by frame on your device — '
              'there is no upload step at all.'),
        lead_zh=('大多数在线去水印工具都是一个套路：你把视频<b>上传到它的服务器</b>，它处理完你再下载。等待上传、限制文件大小，素材还躺在别人的机器上。'
                 '<b>VidGone 把这个模式倒了过来</b>：视频由你自己的浏览器打开，在你的设备上逐帧修复——根本不存在上传这一步。'),
        h2_1="What actually works on a burned-in watermark",
        h2_1_zh="烧录在画面里的水印，怎样才去得掉",
        p1=("A watermark that is part of the picture (a platform logo, a channel name, a date stamp) can't be \"deleted\" — it has to be "
            "reconstructed. VidGone's repair engine rebuilds the covered area from the pixels around it, every single frame. "
            "Results are cleanest when the watermark sits on a fairly stable background: sky, walls, water, smooth gradients. "
            "Over busy motion, the Soft-blur mode is often the better trade."),
        p1_zh=("已经成为画面一部分的水印（平台 logo、频道名、日期角标）没法直接「删除」，只能重建。VidGone 的修复引擎用周围像素重建被遮挡区域，每一帧都如此。"
               "水印落在较稳定的背景上（天空、墙面、水面、平滑渐变）时效果最干净；压在剧烈运动的画面上时，柔化模糊往往是更划算的选择。"),
        h2_2="Free + local + private, not just free",
        h2_2_zh="不止免费：免费 + 本地 + 隐私",
        p2=("Free is easy to promise. What makes VidGone different is the combination: free <i>and</i> local <i>and</i> private. "
            "Because everything runs in your browser with WebCodecs, there are no per-export fees, no accounts, and no copy of your video anywhere but your own disk."),
        p2_zh=("免费谁都承诺得起，VidGone 的差异在于组合：免费、本地、隐私三位一体。一切都在浏览器里靠 WebCodecs 完成，没有按次收费、没有账号，你的视频除自己的磁盘外不存在任何副本。"),
        faq=[
            ("Is it really free?", "Yes — free to use with no signup. Processing happens in your browser, so there are no server costs to pass on to you.",
             "真的免费吗？", "免费使用，无需注册。处理发生在你的浏览器里，没有服务器成本需要转嫁给你。"),
            ("Will the video quality drop?", "The video is re-encoded as H.264 MP4; choose the High quality preset to keep more detail. Audio is copied losslessly when the source uses AAC.",
             "画质会下降吗？", "视频会重新编码为 H.264 MP4，选「高质量」可保留更多细节；源音频为 AAC 时无损直拷。"),
            ("Does it work on moving watermarks?", "The current version applies one mask to the whole clip, so it targets fixed-position watermarks. Moving watermarks are on the roadmap.",
             "能去移动水印吗？", "当前版本一个蒙版作用于整段视频，针对位置固定的水印；移动水印已在路线图中。"),
            ("Is my video uploaded anywhere?", "No. VidGone has no backend — your browser opens the file from your disk and processes every frame locally.",
             "我的视频会被上传吗？", "不会。VidGone 没有后端——浏览器从你的磁盘打开文件，每一帧都在本地处理。"),
        ],
        zh_summary="这是一篇教你「不上传视频就去掉水印」的指南：VidGone 在浏览器里用 WebCodecs 逐帧修复画面，视频全程留在本机，免费、免注册。适合去除平台 logo、频道名、日期角标等固定位置水印。",
    ),
    dict(
        slug="remove-logo-from-video",
        anchor="Remove a logo from a video (corner bugs, channel marks)",
        anchor_zh="去除视频角落 logo（频道标/台标）",
        title="Remove a Logo from a Video Online — Free & Local | VidGone",
        title_zh="在线去除视频 logo——免费且本地处理 | VidGone",
        description="Remove corner logos, channel bugs and station marks from videos without uploading. Local browser-based removal with per-frame inpainting.",
        description_zh="不上传视频，去掉角落 logo、频道标、台标：浏览器本地逐帧修复，免费。",
        h1="Remove a Logo from a Video — Corner Bugs, Channel Marks, Station IDs",
        h1_zh="去除视频里的 logo——角落台标、频道标、素材站水印",
        sub="The classic watermark problem: a small logo parked in the corner of every frame. Here's the clean way to deal with it.",
        sub_zh="最经典的水印问题：一个小 logo 停在每一帧的角落。这里是最干净的解法。",
        lead=("Corner logos are the most common watermark: a <b>channel bug</b>, a stock-footage mark, a broadcaster\'s station ID. "
              "Because the logo never moves, one mask fixes every frame — which makes this the case VidGone handles best. "
              "And because nothing is uploaded, even sensitive or unreleased footage stays on your machine."),
        lead_zh=("角落 logo 是最常见的水印：<b>频道标</b>、素材站标记、电视台台标。因为 logo 从不移动，一个蒙版就能管住所有帧——这正是 VidGone 最擅长的场景。"
                 "而且全程不上传，连未发布素材、敏感素材都只留在你自己的电脑里。"),
        h2_1="Match the removal method to the background",
        h2_1_zh="按背景选对去除方式",
        p1=("Quick fix (fast diffusion) is ideal when a logo sits on sky, walls or water. Smart repair (directional inpainting) is the best balance for most logos on textured scenes. "
            "Fine repair rebuilds texture at multiple scales — slower, and the strongest on complex backgrounds. If the logo sits on top of important moving detail, Soft blur is the honest fallback."),
        p1_zh=("logo 在天空、墙面、水面上：用「快速修复」（快速扩散）就很好。多数带纹理场景的 logo：「智能修复」（方向性修复）最平衡。"
               "复杂背景选「精细修复」（多尺度重建）——最慢也最强。logo 压在重要的运动细节上时，「柔化模糊」是诚实的选择。"),
        h2_2="Tips that visibly improve the result",
        h2_2_zh="几个能明显提升效果的技巧",
        p2=("Cover slightly beyond the logo\'s edge so the engine anchors on clean pixels; check 3–4 scenes across the timeline before exporting; "
            "and prefer the source resolution — the repair runs at full resolution either way, so there\'s nothing to gain from downscaling first."),
        p2_zh=("蒙版稍微盖过 logo 边缘，让引擎锚定在干净像素上；导出前沿时间轴抽查 3–4 个镜头；保留原分辨率——修复本来就按原分辨率逐帧运行，先压缩再修毫无收益。"),
        faq=[
            ("Can it remove a TikTok or Douyin logo?", "Yes — static platform logos are exactly the fixed-position case VidGone is built for. Brush over the mark once; every frame is repaired with the same mask.",
             "能去 TikTok 或抖音 logo 吗？", "可以——静态平台 logo 正是 VidGone 针对的固定位置场景。涂抹一次，所有帧用同一蒙版修复。"),
            ("How long does an export take?", "It depends on your device. The pipeline is hardware-accelerated via WebCodecs; on a typical laptop a short 1080p clip exports in well under a minute.",
             "导出要多久？", "取决于设备。管线经 WebCodecs 硬件加速；一般笔记本上，短片 1080p 导出远不到一分钟。"),
            ("Is there a watermark on the output?", "No. The exported MP4 is clean — VidGone adds nothing to your video.",
             "导出的视频有水印吗？", "没有。导出的 MP4 是干净的——VidGone 不会往你的视频上加任何东西。"),
            ("Does it cost anything?", "No. It's a free tool; processing runs on your own device.",
             "要花钱吗？", "不要。免费工具，处理跑在你自己的设备上。"),
        ],
        zh_summary="去除视频角落 logo（频道标、素材站水印、台标）的最佳场景：位置固定 = 一个蒙版管全部帧。涂抹稍大于 logo 边缘、多检查几个镜头、无需上传即可导出干净 MP4。",
    ),
    dict(
        slug="remove-text-from-video",
        anchor="Remove text, captions & timestamps from a video",
        anchor_zh="去除视频文字、字幕与时间码",
        title="Remove Text, Captions & Timestamps from a Video | VidGone",
        title_zh="去除视频里的文字、字幕与时间码 | VidGone",
        description="Remove burned-in text overlays, captions and timestamps from videos locally in your browser — no upload, free, frame-by-frame repair.",
        description_zh="浏览器本地去除烧录文字、字幕、时间码——不上传、免费、逐帧修复。",
        h1="Remove Text, Captions and Timestamps from a Video",
        h1_zh="去掉视频里的文字、字幕和时间码",
        sub="Burned-in subtitles, date stamps and caption overlays — how to clean them off without sending your footage to a server.",
        sub_zh="烧录字幕、日期戳、标题横幅——不把素材交给任何服务器也能清掉。",
        lead=("Text that was burned into the picture — hardcoded subtitles, a <b>date/time stamp</b> from a dashcam or camera, "
              "a headline banner — behaves exactly like a logo watermark: it\'s part of the pixels now. "
              "VidGone rebuilds the covered strip of the image on every frame, right in your browser."),
        lead_zh=("烧进画面的文字——硬字幕、行车记录仪或相机的<b>日期时间戳</b>、新闻横幅——和 logo 水印本质相同：都已是像素的一部分。"
                 "VidGone 在浏览器里逐帧重建被文字覆盖的那条区域。"),
        h2_1="Text is usually the easiest case",
        h2_1_zh="文字通常是最容易的情况",
        p1=("Subtitles and timestamps sit in predictable strips with fairly simple surroundings, so the repair engine has clean pixels to work from. "
            "Draw a rectangle over the whole text block (slightly taller than the glyphs), preview a frame, then export. "
            "For dashcam timestamps in the corner, a single box typically handles the entire clip."),
        p1_zh=("字幕和时间码落在 predictable 的条带里，周边背景相对简单，修复引擎有干净的像素可用。框住整块文字（比字形稍高一点），预览一帧，然后导出。"
               "行车记录仪的角落时间码，通常一个方框就能管全片。"),
        h2_2="When the text crosses busy motion",
        h2_2_zh="文字压在剧烈运动画面上时",
        p2=("If a caption sits on top of faces or fast-moving detail, no tool can rebuild what was never recorded. "
            "There, Soft blur gives an unobtrusive result instead of a smeared patch. For everything else, Smart or Fine repair reconstructs the background convincingly."),
        p2_zh=("字幕压在人脸或高速运动细节上时，没被记录下来的内容任何工具都重建不出来。此时「柔化模糊」给出的是不突兀的结果，而不是一片涂抹痕。其余场景，智能/精细修复都能可信地重建背景。"),
        faq=[
            ("Can it remove hardcoded subtitles?", "Yes — mark the subtitle strip once and the same mask is applied to every frame, so burned-in captions disappear across the whole clip.",
             "能去硬字幕吗？", "可以——框住字幕条一次，同一蒙版作用于每一帧，整段视频的烧录字幕全部消失。"),
            ("Does it work on dashcam date stamps?", "Yes — corner timestamps on stable backgrounds are one of the cleanest cases for the repair engine.",
             "行车记录仪时间码能去吗？", "可以——稳定背景上的角落时间码是修复引擎最干净的场景之一。"),
            ("Can it remove text that changes wording?", "If the text block stays in the same position, one mask covers all its variations. Text that moves around the frame is a future feature.",
             "文字内容会变也能去吗？", "只要文字块位置不变，一个蒙版覆盖所有变化；在画面里移动的文字属于后续功能。"),
            ("Is anything uploaded?", "No — the whole pipeline runs locally in your browser.",
             "会上传任何东西吗？", "不会——整条管线都在你的浏览器里本地运行。"),
        ],
        zh_summary="去除烧录在画面里的文字：硬字幕、行车记录仪时间码、标题横幅。框选整块文字区即可全片生效；文字压在剧烈运动画面上时建议用柔化模糊。",
    ),
    dict(
        slug="no-upload-video-watermark-remover",
        anchor="Why a no-upload watermark remover keeps your videos private",
        anchor_zh="为什么“无上传”的去水印工具更保护隐私",
        title="No-Upload Video Watermark Remover — Your Video Never Leaves Your Device | VidGone",
        title_zh="无上传视频去水印——视频永不离开你的设备 | VidGone",
        description="A video watermark remover with no upload: VidGone processes every frame locally in your browser with WebCodecs. Private by architecture, not by promise.",
        description_zh="无上传的视频去水印：VidGone 用 WebCodecs 在浏览器里逐帧本地处理。隐私靠架构，不靠承诺。",
        h1="A Video Watermark Remover with No Upload",
        h1_zh="一个「无上传」的视频去水印工具",
        sub="Private by architecture, not by promise — there is no server to upload to.",
        sub_zh="隐私靠架构，不靠承诺——根本没有可上传的服务器。",
        lead=("\"Your files are safe with us\" is a promise. <b>VidGone doesn't need to make it</b>: the tool is a static web page, "
              "and the entire pipeline — demuxing, decoding, per-frame repair, encoding — runs inside your browser tab with WebCodecs. "
              "Your video is read from your disk, processed in memory, and handed back as a download. Nothing is transmitted, because there is nothing to transmit to."),
        lead_zh=("「你的文件在我们这里很安全」是一句承诺。<b>VidGone 根本不需要这句承诺</b>：它是一个纯静态网页，"
                 "从解封装、解码、逐帧修复到编码，整条管线都在你的浏览器标签页里靠 WebCodecs 完成。"
                 "视频从磁盘读取、内存里处理、以下载的形式交还——没有任何传输，因为没有传输的目标。"),
        h2_1="Why this matters for real footage",
        h2_1_zh="为什么这对真实素材很重要",
        p1=("Client cuts, unreleased edits, family videos, internal training clips — the videos people most want to clean are exactly the ones they shouldn\'t upload to a stranger\'s queue. "
            "With local processing the question never comes up: you can even disconnect from the internet after the page loads and keep working."),
        p1_zh=("客户成片、未发布的剪辑、家庭录像、内部培训视频——人们最想清理的，恰恰是最不该传进陌生人队列的那些视频。"
               "本地处理让这个问题根本不存在：页面加载完成后你甚至可以断网继续用。"),
        h2_2="How the no-upload pipeline works",
        h2_2_zh="无上传管线是怎么工作的",
        p2=("The page ships the processing engine from the same origin it\'s served from (with CDN fallbacks). Your browser decodes the video with hardware acceleration, "
            "the repair engine rebuilds each masked frame, and the encoder writes a fresh H.264 MP4 — all in memory on your device. "
            "You can verify it yourself: open your browser\'s network tab while exporting and watch nothing leave."),
        p2_zh=("处理引擎与页面同源分发（带 CDN 兜底）。浏览器用硬件加速解码视频，修复引擎重建每个被标记的帧，编码器写出全新的 H.264 MP4——全部发生在你设备的内存里。"
               "你可以自己验证：导出时打开浏览器 Network 面板，看不到任何视频流量。"),
        faq=[
            ("How can you prove nothing is uploaded?", "Open your browser's developer tools, switch to the Network tab, and run an export — you'll see no video traffic. The tool also keeps working offline after the first load.",
             "怎么证明没有上传？", "打开浏览器开发者工具的 Network 标签，跑一次导出——看不到任何视频流量。首次加载后断网也能继续用。"),
            ("Does no-upload mean slower?", "No — quite the opposite on fast connections. There's no upload wait and no result download wait; processing speed is limited only by your device.",
             "无上传意味着更慢吗？", "不——网速快时恰恰相反。没有上传等待、没有结果下载等待，处理速度只取决于你的设备。"),
            ("Is there a file-size limit?", "There's no artificial limit; practical limits come from your device's memory, since frames are streamed rather than stored.",
             "有文件大小限制吗？", "没有人为限制；帧是流式处理而非整段存储，实际限制来自设备内存。"),
            ("Which browsers support this?", "Any browser with WebCodecs: Chrome and Edge (recommended), Safari 16.4+, Firefox 130+.",
             "哪些浏览器支持？", "支持 WebCodecs 的浏览器均可：Chrome 和 Edge（推荐）、Safari 16.4+、Firefox 130+。"),
        ],
        zh_summary="无上传 = 架构级隐私：VidGone 是纯静态页面，解码、逐帧修复、编码全部发生在浏览器标签页里，视频从磁盘读取、内存处理、本地下载，加载后断网都能用。",
    ),
    dict(
        slug="free-video-watermark-remover",
        anchor="Free video watermark remover — what “free + local + private” really means",
        anchor_zh="免费视频去水印——“免费+本地+隐私”的真正含义",
        title="Free Video Watermark Remover — Free + Local + Private | VidGone",
        title_zh="免费视频去水印——免费+本地+隐私 | VidGone",
        description="What a genuinely free video watermark remover looks like: no signup, no per-export fees, no upload — local WebCodecs processing in your browser.",
        description_zh="真正免费的在线视频去水印长什么样：无注册、无按次收费、无上传——浏览器本地 WebCodecs 处理。",
        h1="Free Video Watermark Remover — What \"Free + Local + Private\" Really Means",
        h1_zh="免费视频去水印——「免费+本地+隐私」的真正含义",
        sub="Most tools are free the way trialware is free. Here's the difference, and why the business model makes it sustainable.",
        sub_zh="多数工具的「免费」是试用装的免费。差别在哪，以及为什么这个模式能持续。",
        lead=("Plenty of sites advertise a free video watermark remover, then gate the actual export behind an account, a subscription, a per-minute fee, or a stamped watermark of their own. "
              "<b>VidGone can afford to be genuinely free because it has almost no costs to gate</b>: the processing happens on your device, not on paid servers."),
        lead_zh=("很多网站宣传免费视频去水印，然后把真正的导出锁在账号、订阅、按分钟计费或它自家水印后面。"
                 "<b>VidGone 敢于真免费，因为它几乎没有可以设卡的成本</b>：处理发生在你的设备上，而不是付费服务器上。"),
        h2_1="The three-part promise",
        h2_1_zh="三位一体",
        p1=("<b>Free</b> — no account, no trial, no per-export pricing, and no watermark added to your output. "
            "<b>Local</b> — frames are repaired by your own browser; nothing is transmitted. "
            "<b>Private</b> — your footage never exists anywhere but your disk, which is a stronger guarantee than any privacy policy."),
        p1_zh=("<b>免费</b>——无账号、无试用、无按次计费，导出不加任何水印。<b>本地</b>——每一帧由你自己的浏览器修复，没有任何传输。"
               "<b>隐私</b>——素材除你的磁盘外不存在任何副本，这比任何隐私政策都硬。"),
        h2_2="Why it can stay free",
        h2_2_zh="为什么能一直免费",
        p2=("The site is static — it costs pennies to serve. There\'s no GPU cluster to rent, no upload storage to pay for, no queue to staff. "
            "VidGone is part of the KuiGe Tools family, a collection of free, privacy-first single-purpose tools; the tools funnel traffic to each other instead of charging you."),
        p2_zh=("站点是纯静态的——托管成本可以忽略。没有 GPU 集群要租、没有上传存储要付、没有队列要人守。"
               "VidGone 属于 KuiGe Tools 家族——一批免费、隐私优先的单一用途工具；工具之间互相导流，而不是向你收费。"),
        faq=[
            ("What's the catch?", "There isn't a billing-shaped one. The honest trade-offs are technical: it's tuned for fixed-position watermarks, and export speed depends on your device rather than a fast server farm.",
             "有什么 catch？", "没有收费意义上的 catch。诚实的取舍是技术性的：它针对固定位置水印优化，导出速度取决于你的设备而非服务器集群。"),
            ("Do I need an account?", "No. There is no signup, no email, no login — open the page and use the tool.",
             "需要注册账号吗？", "不需要。没有注册、没有邮箱、没有登录——打开页面直接用。"),
            ("Are exports limited?", "There are no artificial limits on the tool itself; you're bounded only by your device's performance and memory.",
             "导出有限制吗？", "工具本身没有人为限制；只受你设备的性能和内存约束。"),
            ("Is the output watermark-free?", "Yes — VidGone adds nothing to your video.",
             "导出的视频没有水印吧？", "对——VidGone 不往你的视频里加任何东西。"),
        ],
        zh_summary="真正免费的秘诀是成本结构：处理在你设备上跑，没有 GPU 集群和上传存储要付费。免费 + 本地 + 隐私三位一体，无账号、无次数限制、导出不加任何水印。",
    ),
]

for pg in PAGES:
    pg["anchor_list"] = [(p["slug"], p["anchor"], p["anchor_zh"]) for p in PAGES if p["slug"] != pg["slug"]]


def render_page(pg):
    e = html.escape
    # FAQ (en prefilled; data-zh per element)
    faq_html = "".join(
        f'<details><summary data-zh="{attr(qz)}">{e(q)}</summary>'
        f'<p data-zh="{attr(az)}">{e(a)}</p></details>'
        for (q, a, qz, az) in pg["faq"]
    )
    rel = " · ".join(
        f'<a href="{BASE}/{slug}" data-zh="{attr(azh)}">{e(aen)}</a>'
        for (slug, aen, azh) in pg["anchor_list"]
    )
    steps_en = [SHARED["step1"][0], SHARED["step2"][0], SHARED["step3"][0]]
    steps_zh = [SHARED["step1"][1], SHARED["step2"][1], SHARED["step3"][1]]
    steps_html = "".join(
        f'<li data-zh="{attr(sz)}">{e(se)}</li>' for se, sz in zip(steps_en, steps_zh)
    )
    return f"""<!doctype html>
<html lang="en" data-title-zh="{attr(pg['title_zh'])}" data-desc-zh="{attr(pg['description_zh'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(pg['title'])}</title>
<meta name="description" content="{e(pg['description'])}">
<link rel="canonical" href="{BASE}/{pg['slug']}">
<link rel="alternate" hreflang="en" href="{BASE}/{pg['slug']}">
<link rel="alternate" hreflang="zh" href="{BASE}/{pg['slug']}?lang=zh">
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
  <a class="lang" id="langLink" href="?lang=zh">中文</a>
  <a class="cta" href="{BASE}/" data-zh="{attr(SHARED['open_tool'][1])}">{e(SHARED['open_tool'][0])}</a>
</div></header>
<main class="wrap">
  <h1 data-zh="{attr(pg['h1_zh'])}">{e(pg['h1'])}</h1>
  <p class="sub" data-zh="{attr(pg['sub_zh'])}">{e(pg['sub'])}</p>

  <div class="card lead" data-zh="{attr(pg['lead_zh'])}">{pg['lead']}</div>

  <h2 data-zh="{attr(pg['h2_1_zh'])}">{e(pg['h2_1'])}</h2>
  <p data-zh="{attr(pg['p1_zh'])}">{e(pg['p1'])}</p>

  <h2 data-zh="{attr(SHARED['h2_steps'][1])}">{e(SHARED['h2_steps'][0])}</h2>
  <ol class="steps">{steps_html}</ol>

  <h2 data-zh="{attr(pg['h2_2_zh'])}">{e(pg['h2_2'])}</h2>
  <p data-zh="{attr(pg['p2_zh'])}">{e(pg['p2'])}</p>

  <div class="cta-card">
    <a class="btn" href="{BASE}/" data-zh="{attr(SHARED['cta'][1])}">{e(SHARED['cta'][0])}</a>
    <small data-zh="{attr(SHARED['cta_small'][1])}">{e(SHARED['cta_small'][0])}</small>
  </div>

  <h2 data-zh="{attr(SHARED['faq_h'][1])}">{e(SHARED['faq_h'][0])}</h2>
  <div class="faq">{faq_html}</div>

  <h2 data-zh="{attr(SHARED['rel_h'][1])}">{e(SHARED['rel_h'][0])}</h2>
  <p class="rel">{rel}</p>

  <div class="zh" id="zhSummary">
    <h2>中文摘要</h2>
    <p>{e(pg['zh_summary'])}</p>
    <p><a href="{BASE}/?lang=zh">打开中文界面 →</a></p>
  </div>
</main>
<footer><div class="wrap" data-zh="{attr(SHARED['footer'][1])}">{SHARED['footer'][0]}</div></footer>
<script>{LANG_SCRIPT}</script>
</body>
</html>
"""


def faq_ld(faqs):
    items = ",".join(
        '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
        % (q.replace('"', '\\"'), a.replace('"', '\\"'))
        for (q, a, _, _) in faqs
    )
    return '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}' % items


def rebuild_sitemap():
    urls = []
    # 主站三件套
    urls.append(("index", f"{BASE}/", "1.0", True))
    urls.append(("en", f"{BASE}/?lang=en", "0.8", False))
    urls.append(("zh", f"{BASE}/?lang=zh", "0.8", False))
    # 落地页：clean（hreflang 三连）+ ?lang=zh 深链
    for pg in PAGES:
        urls.append((pg["slug"], f"{BASE}/{pg['slug']}", "0.7", True))
        urls.append((pg["slug"] + "?lang=zh", f"{BASE}/{pg['slug']}?lang=zh", "0.6", False))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for _, loc, pri, hreflang in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        if hreflang:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{loc}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="zh" href="{loc}?lang=zh"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{loc}"/>')
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
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
