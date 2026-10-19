# Design system (Smallest house look)

Approved after several rounds of corrections. When in doubt, be quieter and plainer.

This is the **house** look (styles 1 and 2 in `styles.md`). If the user picks another style or gives their own colours, keep the constants (Aeonik, real logos, no pills, no underline highlights, moving background) and replace the palette and background with theirs. The colour prohibitions below ("never orange", rose for errors) are house rules, not universal ones.

## Palette

| Token | Dark theme | Light theme |
|---|---|---|
| background | `#050607` + flowing blue contours | `#ffffff` + very pale blue wash at the edges |
| ink | `#f3f5f4` | `#0b1124` |
| dim text | ink at 0.45–0.55 | ink at 0.26–0.40 |
| label grey | — | `#7d88a3` |
| accent | sky `#8ec5ff` / `#b4e0ff` | blue `#1f5fe0`, sky `#7db4ff` |
| error / wrong | rose `#ff7a9c` (light: `#d6336c`) | same |

**Never orange in the house palette.** It was removed from everything on request (use rose for errors). A user who asks for orange (or any other colour) gets it, in their own palette. Avoid large saturated blue fields — a bright, flat blue promo look was rejected as "too bright". The dark background should read near-black with blue light moving through it.

End cards: dark pieces end on the cream logo on near-black. Light pieces transition **white → black** with a clip-path wipe from the bottom and end on the cream logo on black. Light pieces also carry a small black corner logo (`logo_black.png`, ~196 px wide, top-left at 72,58) for the whole film until the wipe.

## Type

Aeonik Pro only: Regular 400 for body, Medium 500 for headlines/emphasis. `@font-face` from `assets/fonts`. Sentence case everywhere. Tight tracking on big type (−0.03 to −0.055em). Small labels: Medium, caps, letter-spacing 0.2–0.34em, in the label grey/dim.

Sizes that worked at 1920×1080: title 76 · hero 130–250 · statement 82–104 · transcript 43 · caption 40–44 · small label 20–24.

## Labels and highlights (the "no pills" rules)

- Section/speaker labels: **icon + text + hairline rule** (flex row, `::after` 1.5 px line at 28% opacity). Never a rounded capsule.
- Highlighted words in transcripts: **change colour only** (blue) and weight 500. No underline, no wash, no tag above the word.
- Marker tags above words are plain text (no box) and only for "wrong" demos.
- Cards: rounded rectangles (radius 22–30) are fine on dark; on light use plain type between hairlines instead of cards. Buttons: radius 14, not capsules.
- Waveforms: thin bars (5–7 px, 2–3 px radius). They are the one rounded thing that's welcome.

## Background shader

**Use `assets/gradient-bg.js`** (`GradientBG.create(canvas, {colors, mode, light, speed, stops})`, then `bg.draw(t, intensity)` inside the single timeline-driven `draw()`). It takes any 2–6 colours and has three moving modes: `contours` (the house look below), `mesh` (drifting colour pools), `flow` (slow bands). The house blues are `["#050607","#051257","#124de0","#2b78e6","#6bb3ff"]` with stops `[0,0.40,0.50,0.64,1.0]`. `examples/concept-explainer.html` shows it wired in; the older examples still carry the shader inline.

The background must visibly move for the whole film: drive `t` linearly from 0 to the film's duration, keep `speed` ≥ 0.5, and tween only `intensity` per scene.

The notes below describe the house contour look.

### Dark contours

Warped sine contours, 5 domain-warp iterations, drawn at 960×540 on a canvas scaled to 1920×1080, time-driven by the timeline (seek-safe). Intensity `I` tweened per scene: ~0.42 at the start, 0.6–0.8 mid-film, 0.85 at the CTA, 0 at the end. Ramp: near-black → navy `(0.02,0.07,0.34)` → blue `(0.07,0.30,0.88)` → sky `(0.17,0.47,0.90)` → pale `(0.42,0.70,1.0)` only above v=0.92. Keep the pale step low or text on top loses contrast.

Light variant: same warp, ramp white → `(0.94,0.965,1)` → `(0.87,0.925,1)` → `(0.78,0.87,1)`, multiplied by an edge mask so the centre stays clean (`v *= I*(0.35+0.85*edge)`). Film grain: dark theme `grain.png` overlay at opacity 0.24 (50% of the original, per request); light theme none (it greys the white). Add a vignette on dark.

The full shader source is in every file under `examples/` (search `const FS`).

## Motion

- Ease: `expo.out` for entrances (0.8–1.1 s), `power3.in` / `expo.in` for exits (0.5–0.7 s), `expo.inOut` for repositioning.
- **Masked rises** for headline type (natural, premium): wrap each word in `overflow:hidden` with `padding-bottom:.2em; margin-bottom:-.2em`, animate the inner word `yPercent 108 → 0`. Blur-ins (`blur(12px)`) for scene blocks and cards.
- Scene exits: rise and blur out (`y -40`, `blur(12px)`), never a hard cut except to the end card.
- Slow stage drift on the whole composition (≈ ±7 px, ±0.14°, scale 1 → 1.045 over the film) with the background moving the opposite way, so nothing is ever perfectly static.
- Words appear on their spoken times (`start − 0.04 s`). One caption/line at a time: a caption must be gone (fade ≤ 0.3 s after its line) before the next arrives.
- Handheld camera (only for real-world scenes like the phone photo): sums of slow sines — translate ±2 px, rotate ±0.1°, perspective ±0.15°, scale breathing 0.4%, plus a 0.2 px tremor. The first version at ±7 px / ±0.34° was "too shaky"; the approved one is about 25–30% of that.

## Waveforms

The mirrored 36-band spectrum (`scripts/spectrum.py`): 45–49 bars, height from the interpolated band value (`pow(v·1.25, 0.85)`), bar *i* uses band `|i−c|/c·33`, tallest in the middle. Active voice: blue gradient bars (`#7db4ff → #1f5fe0` on light, `#bfe0ff → #3d7bff` on dark) with a soft blue radial glow behind; idle voice: a dotted grey line. Decay the last frame over 0.4 s after a clip ends. Whole-call timeline waveform (bars lit as the call plays, the tiny final bars highlighted) is used in the short-words film.

## Transcript card (call demos)

White card (light, final choice) or dark glass; no speaker tabs, no definition cards. Per turn: small caps label "Agent" (blue) / "Customer" (grey), text 43 px / 1.5. Older turns fade to 0.28–0.30; three turns visible; top fade mask 15%. Feed scrolls so the active turn's bottom sits 120 px above the card bottom; first block padded 150 px so its label isn't under the fade. BFSI terms are blue weight 500. Spoken sequences (IDs, amounts) appear word by word, **then** turn blue, squeeze together and grow into one written token (`MRDN0004217`, `₹42,500`) with the block height easing in step — see `examples/call-with-live-transcript.html`.

## Logo and credits

Cream logo on dark, black logo on light. Don't recolour the mark. Never put a vendor name on screen unless it is ours. Disclose synthetic demo audio in small caps ("Demo audio · Pulse transcript").
