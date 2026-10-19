# Audio pipeline

All Smallest endpoints use `Authorization: Bearer $SMALLEST_API_KEY`. Scripts in `../scripts/` wrap each step. Use a venv: `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install numpy scipy opencv-python-headless`.

## Lightning TTS

`POST https://api.smallest.ai/waves/v1/tts` JSON `{text, voice_id, model, sample_rate:24000, speed, language, output_format:"wav"}`, header `Accept: audio/wav`.

- `model: lightning_v3.1_pro` for Pro voices (`kaitlyn`, `blake`, `meher`, `sophie`, `sam` …); `lightning_v3.1` for the standard pool. Voice and model must be paired.
- Always trim: cut leading/trailing silence at −46 dB with 60 ms / 120 ms padding and 10/40 ms fades (`smallest_tts.py` does it).
- Roles that worked: narrator `meher`, agent `blake`, caller / "original" `kaitlyn`.
- Speed 0.93 gave deliberate, emotional reads for the clone quiz; 1.0 elsewhere.

## Voice cloning

`POST /waves/v1/voice-cloning` (multipart): `displayName`, `file` (5–15 s, < 5 MB), `model=lightning-v3.1-pro`, `language`, `accent`, `tags`. Send the file with an explicit type (`-F "file=@x.wav;type=audio/wav"`) or you get `Invalid file type`. The response `data.voiceId` is used as `voice_id` with model `lightning_v3.1_pro`.

**Consent:** only clone a speaker who agreed. For demos, clone a stock Lightning voice (original = stock voice, clone = same voice cloned) and word the reveal honestly ("original / clone"), not "real human". Sanity check a clone without listening: compare median F0 and spectral centroid of original vs clone clips (autocorrelation pitch); they should sit in the same range.

## Pronunciation dictionaries

`POST /waves/v1/pronunciation-dicts` `{items:[{word, pronunciation}]}` → `id`; use `pronunciation_dicts:[id]` in the TTS body. The pronunciation is **plain words written as they sound**.

- Hyphenated respellings (`hun-day`, `en-vid-ee-uh`) were read literally and came out wrong.
- Concatenated plain words worked better (`shivawn`, `envidia`); for Hyundai the Indian reading `hyun dye` round-tripped as "Hyundai".
- Output is **non-deterministic**: one dictionary gave "Yandai", "Hyun Dai", "Hanyada" and "Hyundai" across takes. Generate 4–6 takes, run each through Pulse, keep a take where the entities transcribe cleanly (`smallest_stt.py --check`). Tell the user you validated by transcription only.
- Raw Lightning with no dictionary transcribed Hyundai, Nvidia and Siobhan correctly in tests — consider letting the model read hard names unaided and reserve the dictionary for genuinely hard words.

## Pulse STT

`POST /waves/v1/stt/?model=pulse&language=en&word_timestamps=true[&diarize=true]` with the raw bytes and the right `Content-Type`. Returns `transcription`, `words[{word,start,end,speaker}]`, `utterances[]`. Diarization worked cleanly for a two-speaker call (speaker 0 = agent, 1 = customer by who opens the call — label by reading the content).

Timing quirks (found by measuring against the audio): word **ends** are stretched through the following pause; some **starts** are early inside the customer's hesitations. `scripts/build_transcript.py` fixes both with `silencedetect` (−40 dB, ≥0.25 s): snap a word start that lies inside a pause to the pause end; clamp an end that spans a pause to the pause start.

Local alternative for timings: `npx hyperframes transcribe file.wav --model medium.en --json` (grep the `"type":"words"` line). Its mid-sentence times can drift by ~1 s on long clips — sanity-check against the audio.

## ElevenLabs (narration only)

`scripts/elevenlabs_tts.py`. Never present ElevenLabs audio as a Smallest model. Library voices (e.g. "Belle B - Premium Ad Narrator", `SQQyvkXssth4s6HD2OuR`) need a paid plan via the API; the free plan returns 402. Premade voices work on free. Voice-settings guess for the house read: stability 0.5, similarity 0.75, style ~0.2, speaker boost on.

## No key available (placeholder narration and timings)

Only when the user has not supplied a voice key and cannot be reached. Label it a placeholder and offer to redo it with a key.

1. One text file per beat (a beat = one or two sentences) → `scripts/placeholder_tts.sh out_dir beat1.txt beat2.txt …` (macOS `say`, 24 kHz mono, trimmed). Check `volumedetect`.
2. Phrase boundaries: `ffmpeg -i clip.wav -af silencedetect=noise=-38dB:d=0.14 -f null -` → speech segments between the silences; each segment is a phrase in the script.
3. Word times inside a phrase: spread the words across the segment by character weight (`len(word)+1.5`). Good to ±0.1 s, enough for kinetic type. `examples/concept-explainer.html` has the `seg(clip, start, end, text)` helper.
4. Envelopes for the narrator waveform and signal visuals: `scripts/envelope.py clips… --out assets/data.js`.
5. When a key arrives, regenerate the clips with the same beat split, re-run steps 2–4, and update the `seg()` phrase boundaries and the `<audio>` durations; nothing else changes.

## Spectra and envelopes for visuals

`scripts/spectrum.py clip.wav … --out data.js --var NAME` → per clip `{dur, spec[frames][36], env[]}` at 30 fps, normalised across all clips so loudness is comparable. The composition interpolates between frames, so 60 fps rendering stays smooth.

## Phone-quality audio (for "works on bad lines" demos)

```
ffmpeg -i clean.wav -f lavfi -i "anoisesrc=color=pink:amplitude=0.012:sample_rate=24000" \
  -filter_complex "[0:a]highpass=f=300,lowpass=f=3400,acompressor=threshold=-24dB:ratio=3[v];[v][1:a]amix=inputs=2:duration=first:weights=1 0.5,aresample=8000" \
  -acodec pcm_mulaw -ar 8000 -ac 1 phone.wav
ffmpeg -i phone.wav -acodec pcm_s16le -ar 8000 phone_pcm.wav     # playable in the browser, still sounds narrowband
```
Send the mu-law file to Pulse; play the PCM copy in the film. Be honest on screen: the source is synthetic speech degraded to a phone line, not a real-world noise stress test.

## Syncing a call recording to a phone filmed on a desk

The phone's own mic is usually silent, so cross-correlation fails. Sync by the on-screen call timer: if the timer reads 00:00 at footage time `t0`, start the recording at `t0`. If the footage shows "connecting" for a couple of seconds first, keep that as a natural intro.
