# Building and rendering with HyperFrames

Load the `hyperframes`, `hyperframes-core` and `hyperframes-cli` skills for the contract. This file is the short list of what mattered on these videos.

## Project setup

```
mkdir myfilm && cd myfilm
mkdir -p assets/fonts assets/audio
cp <skill>/assets/fonts/*.otf assets/fonts/ ; cp <skill>/assets/{logo.png,logo_black.png,grain.png,gradient-bg.js} assets/   # gradient-bg.js = moving gradient in the user's colours (see styles.md)
# hyperframes.json / meta.json / package.json: copy from any earlier project, or `npx hyperframes init name --non-interactive --skip-transcribe`
cp <skill>/examples/<closest>.html index.html
```
One composition per project; keep older iterations out of the project root (two root `index*.html` files raise `multiple_root_compositions` and can double the audio). Move old versions to `_old/`.

Root: `<div id="root" data-composition-id="main" data-start="0" data-duration="N" data-width="1920" data-height="1080">`. Register one paused GSAP timeline at `window.__timelines["main"]`. Building inside `document.fonts.ready.then(build)` is fine (needed so word widths and block heights are measured with Aeonik loaded). Do **not** use `requestAnimationFrame` (lint error).

## Time everything from audio

- `<audio id="…" src="…" data-start="T" data-duration="D" data-track-index="n" data-volume="1">` — every audio needs a unique id. Cut one recording into segments with `data-media-start` when demos must be inserted between lines; cut at the **middle of real silences** (`silencedetect`), not at transcript times (a cut at a transcript end clipped the last word of a line once).
- Keep a `STARTS`/`NS` table in the script that matches the audio tags; derive beat times from `start + wordStart`.
- Drive anything continuous (shader time, waveforms, timers, handheld camera, marquees) from one tween on a proxy object whose `onUpdate` calls `draw()` — it re-runs on every seek, so renders are deterministic.

## Lint and runtime gotchas

- Never tween `visibility`/`autoAlpha` on a `.clip`; animate a child. Don't mix a CSS initial `transform` with a GSAP tween on the same property — use `fromTo`.
- A security hook rejected files containing `innerHTML`. Build DOM with `createElement`/`textContent`/`append` (helper `mk(cls,text,tag)` in the examples). Remember `mk` defaults to `<span>` — block-level labels and text blocks need `"div"` or they flow inline.
- `check` reports layout "content_overlap" for words hidden inside reveal masks and for intentionally stacked beats; judge by snapshots. Real contrast failures on dim labels are worth fixing (raise opacity).
- Animating `width`/`height` of inline words to fold them together works (`overflow:hidden` + explicit px widths measured at build); set `vertical-align:top` on inline-block words or baselines jump while `overflow:hidden` is on.

## Commands

```
npx hyperframes check
npx hyperframes snapshot --at 2.5,8,14.2          # PNGs + contact-sheet(.jpg) in ./snapshots (look at the sheet)
npx hyperframes render -o name.mp4 [--fps 60]      # 60 fps for motion-heavy pieces; ~45 s for a 40 s film
ffmpeg -i name.mp4 -c:v libx264 -crf 22 -preset medium -pix_fmt yuv420p -c:a aac -b:a 160k name-share.mp4
```
Pin with `npx hyperframes@0.8.140` if the project pins that version. Send the compressed file, not the 200 MB master. The tool's own ffmpeg lacks `drawtext`; label comparisons by position (left = before) or in the composition.

Audio checks on the render: `ffmpeg -i out.mp4 -af silencedetect=noise=-45dB:d=0.4 -f null -` — speech should start where planned and pauses should be the planned ones. A render prints "Audio lowered by x dB to stay under −1 dBTP" — normal.

## Footage enhancement (real phone clips)

`scripts/enhance_footage.py in.mp4 out.mp4 <seconds> <hold_frames>`:
- Phone auto-exposure swings (here 2×, background 33→64) when the screen dims; that was the "flicker". Fix = per-frame **scalar** brightness lock for background and screen regions (median target), then temporal denoise (`hqdn3d=6:5:9:7`), a cooler grade (`colorchannelmixer` to pull the orange cast, curves keeping highlights, `unsharp`, vignette).
- Do **not** match per-channel gains on the screen: its red channel is near zero, so white text turned teal.
- When the phone dims its backlight for a few seconds, no gain brings the colour back: hold the last good screen through those frames with a soft blend (weight from a dilated `gain > 1.06` mask). The on-screen timer pausing 2–3 s is acceptable.
- Output constant 30 fps with dense keyframes (`-g 30`) for seeking.
- The screen text can be verified against the audio by the on-screen timer (see audio-pipeline).

## Photoreal phone from a generated photo

1. Generate a top-down flat-lay with a **blank blue** screen (no text/icons — image models garble UI text), phone on the left third, empty dark desk on the right for the transcript. Upscale to 2K/4K (Higgsfield `upscale_image`) — a 1344 px still is too soft at 1080p.
2. `scripts/phone_quad.py phone.png --design 385 737 --stage-height 1080 --left -5` → `matrix3d(...)` for the UI layer.
3. Build the real iOS call UI in HTML inside that layer (status bar 9:41, island + orange mic dot, signal/wifi/battery, timer under bold name, 3×2 glass buttons: Speaker FaceTime Mute / More End(red) Keypad). Use the proportions from a real screenshot, not memory.
4. Black bezel ring + inner shadow + a diagonal glass reflection; grain **below** the screen layer; same handheld transform on photo and screen.
5. Timer counts from the sync point; "calling…" before; "Call Ended" at the end.
Higgsfield tools are deferred MCP tools: load with ToolSearch. A still costs ≈0.25 credit, a 2K upscale ≈2.
