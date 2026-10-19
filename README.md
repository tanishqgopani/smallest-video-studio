# smallest-video-studio

A Claude Code skill that makes Smallest AI videos end to end: script, narration, a HyperFrames composition, a rendered MP4.zz

`assets/fonts` contains Aeonik Pro, which is licensed to Smallest.

## What it does

- Asks up front for the story, the style, the gradient colours and the voice keys, then builds.
- Styles: launch film, light explainer, call demo, data-led demo, brand-colour gradient, type-only poster, plus a diagram explainer. Pick one, blend two, or describe your own.
- Moving gradient background in any colours (`assets/gradient-bg.js`: `contours`, `mesh`, `flow`).
- Recipes with working examples: launch film, diagram explainer, voice-agent call with live transcript, voice-clone quiz, speech-to-text short-words demo.
- Never fakes a demo: audio standing in for a Smallest product must come from that product. ElevenLabs is narration only.

## Install

```bash
git clone git@github.com:tanishqgopani/smallest-video-studio.git ~/.claude/skills/smallest-video-studio
```

Restart Claude Code, then ask for a video or run `/smallest-video-studio`.

## Requirements

- [HyperFrames](https://hyperframes.dev) via `npx hyperframes` (needs Node), `ffmpeg`, Python 3.
- `ELEVENLABS_API_KEY` for narration; `SMALLEST_API_KEY` for Lightning, Pulse, cloning and Atoms. Pass keys inline for one command; the scripts read them from the environment and never write them to disk.
- `numpy` and `scipy` only for `scripts/spectrum.py`.
- With no voice key the skill falls back to a placeholder macOS voice (`scripts/placeholder_tts.sh`) and says so.

## Layout

| Path | Contents |
|---|---|
| `SKILL.md` | Entry point: rules, intake, workflow, recipes |
| `references/` | styles, design system, audio pipeline, HyperFrames build notes, recipes, gotchas |
| `scripts/` | TTS, STT, cloning, spectrum/envelope data, transcript timing, footage and phone helpers |
| `assets/` | Aeonik fonts, logos, grain, `gradient-bg.js` |
| `examples/` | Finished compositions to start from |

## Updating

Edit the files, test with a short render, commit. Add every new mistake to `references/gotchas.md`.
