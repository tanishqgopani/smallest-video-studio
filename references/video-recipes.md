# Video recipes

Each recipe lists the storyboard, timing template and the file to start from. Times are seconds in the finished film.

## 1. Launch / entities film (`examples/entities-launch.html`, ~38 s, dark, 60 fps)

Script shape (user-approved):
1. Problem, one sentence, then "That's where users drop off."
2. "Introducing <Product>, our <category>, now optimized for <what>."
3. What it does, shown as the four kinds of entity: names, brands, stock names, abbreviations (numbers were dropped — normalization handles numbers). Close: "Said the way a person says them."
4. Feature: pronunciation dictionary — "Save a pronunciation once, and every call uses it."
5. "Start building with <Product> today." → logo.

Scenes and how they animate:
- **S1** a sentence containing one entity of each kind; as the narration lists them each entity rolls up into its wrong phonetic spelling in rose with a small caps tag (name / brand / stock / abbreviation); width eases from the right word to the wrong word so neighbours glide; "✕ Caller dropped off", sentence dims. No staged mispronunciation audio.
- **S2 introducing, in three beats:** (0) "Introducing" + hero product name; (1) "Our text to speech model" arrives word by word; it lifts away; (2) "now optimized for" word by word; it steps up and shrinks (`y −150, scale .78`); (3) "entities" arrives as big letters rising from a mask. Make sure beat 1 has fully left before beat 2 starts (the overlap was a bug).
- **S3 poster:** four rows, label left (caps, sky), three words per row in 104 px Medium rising from masks on the narrated category word, hairline drawing under each row; closing line below, word by word.
- **S4 dictionary card:** label → rows (word → plain-word pronunciation, as really saved) → Save press → "Saved" per row → three "Call n ✓" lines on "every call uses it".
- **S5** "Start building with" + hero product name; exit; cream logo.
- Persistent: small cream logo top-left, narrator waveform at the bottom, stage drift, background intensity arc.

**Demo clips of the product saying the entities** (names, brands, stocks, abbreviations, e.g. Siobhan/Saoirse/Nguyen, Hyundai/Porsche/Xiaomi, Nvidia/Tesla/Zomato, NACH/IFSC/UPI) must come from Lightning. Without a working Smallest key the film ships without them and the category scene would need retiming when they're added (≈ +10 s). Check each demo with a Pulse round-trip.

## 2. Voice-agent call with live transcript (`examples/call-with-live-transcript.html`, ~113 s for a 105 s call)

Inputs: the call recording (mono mp3 is fine). Steps:
1. `smallest_stt.py call.mp3 --diarize --out pulse.json`.
2. Edit the rules at the top of `scripts/build_transcript.py` (merge groups for spoken amounts/IDs, ASR fixes, BFSI term list) — they match on words, not indices, so a re-recorded call re-uses them. Run it → `transcript2.js` (word timings snapped).
3. Phone: generated photo + `phone_quad.py` + iOS UI (see hyperframes-build.md). Call audio starts when the phone timer reads 00:00 (here 2.0 s into the film).
4. Transcript card (white, final choice) as in design-system.md; words appear on spoken times; spoken sequences merge into one written token (7 groups in the Meridian call: `₹42,500`, `MRDN0004217` ×2, `ABCPM4217K`, `₹500`, `₹3,00,000`, `₹8,400`).
5. Outro: card leaves, footage/black fades, logo.
Choices that were made on purpose: names "Agent"/"Customer" as labels; no tags or definition cards; blue words only; subtle handheld; grain under the screen. A speaker rename in the audio (Tom Stanley → Tom) means re-running steps 1–2.

## 3. Voice-clone quiz (`examples/voice-clone-quiz.html`, ~38 s, **white** → black end)

Layout copied from a reference "Which voice is the real one?" video: title top, VOICE A / VOICE B columns with spectrum bars, alternating lines, word-highlight caption, reveal.
- Voices: A = stock Lightning voice, B = clone of it (see consent note). Six lines, ~1.5–3.7 s each, 0.6 s gaps; start at 2.4 s; reveal 2.2 s after the last line.
- Script that was approved (rewrite freely, keep the shape): hook ("Close your eyes for a second.") → "You don't hear words. You hear a person." → what a voice carries → "from a few seconds of recording…" → question aimed at the viewer ("So listen again. Which of us is the real one?").
- Reveal copy: **"Voice B was a cloned voice, made from just 9 seconds of audio."** (no model name; use the true sample length). End card: "Clone your voice / with smallest.ai" in white on black, then the cream logo.
- Spectrum columns lit only for the speaking voice with a soft glow; captions fade ≤0.3 s after their line so they never overlap; small black logo top-left.

## 4. Short-words STT demo (`examples/short-words-stt.html`, ~48 s, **white** → black end)

Point: Pulse catches the short words that decide a call. Never claim a stat the docs don't give; show real output.
- Generate the call with Lightning (agent `blake`, caller `kaitlyn`): agent asks "…Do you want me to go ahead?"; the caller rambles ("Well, I did order it for my mum's birthday last Tuesday, and the tracking says delivered, but honestly I'd rather wait and see if it turns up first, so… no.") and ends on one tiny word. Run Pulse on it and on 8 kHz µ-law copies.
- Scenes: whole-call waveform with the caller's words appearing and the final bars highlighted ("less than half a second") → hero "no." → "Short words." six cells between hairlines (Yes, No, Uh-huh, Okay, "Four eight one seven", Nope) filling with real Pulse text as each clip plays → "8 kHz phone line" replay with "same result" → "Pulse — Speech-to-text for the words that change a call." → black end.
- Narration was Lightning `meher` here; label the audio "Demo audio · Pulse transcript".
- The earlier version failed because it opened on a one-word answer, used a bright blue promo look, and claimed "trained on…". Open with the long sentence; keep claims to what was demonstrated.

## 5. Diagram explainer (`examples/concept-explainer.html`, ~49 s, any gradient)

Built for "Hydra removes the stack": a concept told one visual idea per sentence. The script (user's own, lightly cut) was split into six beats, each with its own audio clip, and every visual maps to a noun or verb in its sentence.

| Beat (sentence) | Visual |
|---|---|
| Problem: "not a latency problem… an addition problem" | two lines of type; the first dims, "addition" turns accent colour |
| Four stages | four labels; a bar for each starts where the previous one ended (a staircase), then a total bar spans them all |
| Turn detection bolted on | the four stages shrink to a stack; a fifth block drops onto the top; three plain-text rows with ✕ (interruptions, pauses, background speech); the block turns error-coloured on "wrong" |
| "X removes the stack." | the product name huge, then the line under it |
| Speech-native, audio in / out | a waveform travelling straight from "Audio in" to "Audio out"; a "Transcript" label appears and is struck through |
| Per-frame state, early response | frame bars arriving on a playhead, a state line updating, response bars that start before the input ends |

Technique: one `P` proxy object tweened linearly for time; canvases redrawn in `draw()` from `P.t` so seeking is deterministic; DOM text via masked rises at spoken word times; scene exits rise and blur; the background intensity fades to 0 before the logo. Use `{ light: true }` and ink text for a light version.

## 6. Captions and notes for the post

See SKILL.md "Captions". (This section was 5 before the diagram explainer was added.) The approved BFSI voice-agent caption opened with "Precision." then: small errors in banking are never small → concrete failures (wrong digit in an IFSC code; ₹3,00,000 heard as ₹30,000; mispronounced bank name) → the vocabulary (EMI, NACH, IFSC, KYC, UPI, CIBIL, foreclosure, tenure) → the stack in one line each (Pulse hears, Lightning says, Electron is the brain — claims supplied by the user, flag them) → "Shift to the Smallest AI voice stack today. [Link]".
