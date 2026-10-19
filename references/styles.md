# Styles

A style is a bundle: theme, background (mode + colours), type treatment, layout vocabulary, motion, end card. Offer the list at intake, let the user pick one, blend two ("style 2 layout, my colours"), or describe their own. The four Smallest videos gave four of these looks; the rest are variations built from the same parts.

## Constants (every style)

- **The background always moves.** Use `assets/gradient-bg.js` (modes `contours`, `mesh`, `flow`; `speed` ≥ 0.5). A frozen gradient reads as a still image. Even type-only styles carry a slow, low-contrast moving field. Confirm motion by comparing stills 3 s apart.
- Aeonik Pro (Regular body, Medium headlines) unless the user supplies another font. Sentence case.
- The real logo files; never recolour the mark. No capsule/pill labels, no underline highlights, no heavy glass on light themes.
- No invented claims; demo audio comes from the product it represents; say what is synthetic.
- Time every visual from the real audio. Check contrast against the **brightest** frame of the background.
- Fade the background intensity to 0 (dark) or to the paper colour (light) before an end card.

## Colours from the user

Ask for them at intake: "Which colours? Give 2–5 hex codes or names, and say dark or light." Then:

1. **Base** = `colors[0]`: near-black (dark theme) or near-white (light theme), tinted toward their hue so it feels related. If they gave only vivid colours, derive the base.
2. **Ramp** = remaining colours ordered dark → light; the lightest is used rarely (it is the highlight). Two colours is enough: base + one.
3. Dark theme: intensity 0.4–0.85. Light theme: `light: true`, intensity ~0.6–0.8, colour pools toward the edges so the centre stays readable (white + orange at 0.75 mesh was approved as a test).
4. Ink (text) is white or near-black chosen for contrast against the area it sits on at the brightest frame (≥ 3:1 for large text). Accent for highlighted words = one of their colours that passes that check, else ink at weight 500.
5. Orange, pink or anything else is fine **if the user asked for it**. The house rules "no orange" and "rose for errors" apply only to the Smallest house palette below.
6. No colours given: offer the house blues, or three suggestions (e.g. blue/sky, ink/white + one accent, warm white/orange) and use the house blues if they have no preference.

## The styles

### 1. Launch film (dark contours, house blues)
- For: product launches, feature announcements, concept explainers. Example: `examples/entities-launch.html`, `examples/concept-explainer.html`.
- Background: `contours`, colours `["#050607","#051257","#124de0","#2b78e6","#6bb3ff"]`, stops `[0,0.40,0.50,0.64,1.0]`, intensity arc ~0.42 → 0.6–0.9 → 0, dark vignette, grain at 0.24.
- Type: masked word rises, 82–130 px statements, hero words in sky `#8ec5ff`, caps labels 20–24 px.
- Layout: left-aligned statements (x = 190), posters with hairline rows, one diagram per scene, narrator waveform at the bottom, small cream logo top-left.
- End: cream logo on near-black.

### 2. Light explainer (white → black end)
- For: quizzes, short explainers, anything meant to feel calm and editorial. Example: `examples/voice-clone-quiz.html`.
- Background: `light: true`, pale blue `["#ffffff","#f0f6ff","#dde9ff","#c7ddff"]`, intensity ~0.4; no grain (it greys the white).
- Type: ink `#0b1124`, dim 0.26–0.40, plain type between hairlines instead of cards, black corner logo (196 px, at 72,58).
- End: clip-path wipe white → black from the bottom, cream logo on black.

### 3. Call demo (photoreal phone + live transcript)
- For: voice-agent call recordings. Example: `examples/call-with-live-transcript.html`; recipe 2.
- Dark desk photo with a phone, iOS call UI drawn in HTML and warped onto the glass, white transcript card, blue highlighted terms. Background is the photo; add subtle handheld motion (keeps it moving). Intake needs the call recording and a phone photo.

### 4. Data-led demo (waveform and real outputs)
- For: showing a model's real output: STT results, short-word catches, before/after. Example: `examples/short-words-stt.html`.
- White, whole-call waveform, results appearing in cells between hairlines, honest labels ("Demo audio · Pulse transcript"). Black end.

### 5. Brand-colour gradient (custom colours)
- For: anything where the user supplies colours. Use the layout vocabulary of style 1 (dark) or 2 (light) on a `mesh` or `flow` background in their colours.
- `mesh` = soft drifting colour pools (best for light themes and bold colours); `flow` = slow diagonal bands (calm, corporate); `contours` = marbled lines (technical).
- End card: logo on near-black, or on the brand base colour if the logo stays legible (check contrast).

### 6. Type-only poster
- For: statements, quotes, one-line announcements, teasers (5–15 s). Huge Medium type (150–250 px), one accent colour, a few words per beat, a slow `flow` background at low intensity (0.3–0.5).
- Fastest to produce; no diagrams. Use when the script is a few lines and there is no data to show.

### Diagram explainer (a recipe on top of style 1, 5 or 6)
- A concept told with one visual idea per sentence: stacked bars that add up (delay), a bolted-on block, a stack collapsing, signal flowing straight through, a state line updating. Every visual is drawn from the script's nouns and driven from the real audio times. See `examples/concept-explainer.html` and video-recipes.md recipe 5.

## Choosing quickly

| The user says | Start from |
|---|---|
| "launch", "introducing", "announcement" | 1 |
| "explain", "how it works", no data to show | 1 or 5 + diagram explainer |
| "quiz", "calm", "editorial", "white" | 2 |
| "call", "agent demo", "transcript" | 3 |
| "results", "benchmark", "show the output" | 4 |
| "our brand colours are…" | 5 |
| "short", "teaser", "quote" | 6 |
