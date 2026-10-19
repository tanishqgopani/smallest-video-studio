# Gotchas (each one cost real time)

## Process and judgement
- Read the reference video first (contact sheets + transcript). Match layout and pacing; apply our palette. The first call-video attempt was rejected because it used an old brand skill instead of the user's actual fonts and colours.
- Users react to **frames**. Send a still or a comparison before a long render when a look is uncertain; send the video when the direction is settled. After a direction change, rebuild the look first, then the details.
- "Too bright", "looks AI", "too shaky", "rounded shapes haunt me", "no underline", "no orange" — these were all real corrections. Default to quieter, plainer, calmer.
- Sub-agent review is useful for visual QA on zoomed crops (it caught a 1–2 px blue fringe around the phone glass). Brief it with the image paths and the exact questions; don't hand it your conclusion.

## Process additions (from the Hydra film test)
- Ask for style, colours and both keys (ElevenLabs, Smallest) **before** building. In the Hydra run the keys never arrived, the user went away, and the film shipped on a placeholder macOS voice; that is the fallback, not the plan.
- A background that "has motion" in code can still look static if the speed is low and the frames are judged from one still. Compare stills ≥ 3 s apart; the gradient asset defaults to visibly drifting.
- The colour rules (no orange, rose for errors) belong to the house palette only. A user who gives colours gets those colours.
- A light, user-coloured gradient needs the base to stay dominant: with a 4-colour white→orange ramp at intensity 0.9 the whole frame became orange; 0.75 with the tighter light-mode falloff kept real white.
- Fade the background to black/paper **before** the end-card logo; a bright gradient behind the logo looked like a mistake.
- `hyperframes check` reports `content_overlap` for words hidden in masks of other scenes and for stacked beats (11–13 "errors" on a clean film). Judge by snapshots. Real finds worth fixing: low-contrast coloured text on the brightest part of the gradient (rose on blue was 1.8–2.4:1; lighten the text colour or lower the intensity during that scene).
- A tall block of text in a narrow column wraps and can collide with the bottom waveform; set `white-space: nowrap` and a font size that fits, then check a still at the end of that beat.

## Audio
- Local transcription (`hyperframes transcribe`, whisper small.en) returned garbage on a short synthetic clip (one word, wrong times). Don't rely on it for timings; use `silencedetect` for phrase boundaries and spread words by character weight (see audio-pipeline.md).
- `hyperframes tts` needs `kokoro-onnx` installed and a model download; it isn't available by default. The offline fallback is `scripts/placeholder_tts.sh` (macOS `say`).
- A trim chain built from `afade` + `areverse` produced silent files (−87 dB). After any trim, run `volumedetect`; max volume should be around −2 to −4 dB.
- Smallest key rejected → it was rotated. Ask for a new one; don't search the disk or switch vendors for demos.
- Don't cut a recording at transcript times; cut at silence midpoints.
- Pulse word starts/ends need snapping before animating (audio-pipeline.md).
- Pronunciation is non-deterministic; validate by transcription over several takes and say you couldn't listen.
- `curl -F file=@x.wav` needs `;type=audio/wav` for the clone endpoint.
- Don't write NaN into data files: empty frequency bands must be filled before normalising.
- Pulse timestamps for a final tiny word are ~0.24 s; say "less than half a second", not a made-up figure.
- A one-line change in the audio (a renamed person) shifts everything after it; make every rule match words, not indices.

## Visual build
- `mk()` returns a span; blocks/labels must be `div`s or layout collapses inline.
- Keep grain below glass/screens; grain on a screen makes it a printed picture. Grain multiply on white greys the white — turn it off on light.
- Words animating width need `overflow:hidden` and `vertical-align:top`.
- Measure heights/widths in the final state before applying the starting states; then tween block height from the "spoken" layout to the final one so following blocks don't jump.
- Feed layouts: pad the first block below the top fade mask or its label disappears.
- Captions overlapping = exit too slow; exit within ~0.3 s of the line ending.
- Don't put the media's start under a fade if it's the call's first word.
- `hyperframes render` with two root compositions in one folder doubles audio.
- `npx hyperframes@latest` may differ from a pinned project version; stay on the pin and don't "upgrade" mid-film.

## Phone / footage
- A phone photo with a blank blue screen beats trying to get an image model to draw call UI; draw the UI yourself and warp it with a homography.
- A flat rotated rectangle for the screen overshoots (perspective). Fit edges and use `matrix3d`.
- Per-channel exposure matching tinted white text; use scalar gain and hold the last good screen for backlight dips.

## Claims and copy
- Never name "BFSI" in public copy; say banking and finance.
- Don't claim "trained on…" or a scale ("millions") unless the user states it — then flag it.
- Say what is synthetic (demo audio, clone of a stock voice, degraded to phone quality).
- Use `[Link]`, `[benchmark]`, `[customer]` placeholders and list them.
- The old `smallest-ai-animation` skill (orange/blue/pink palette, Poppins) is obsolete.
