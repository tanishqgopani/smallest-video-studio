#!/usr/bin/env python3
"""Narration with ElevenLabs. Key from the environment (XI_KEY). Use for NARRATION only.

  export XI_KEY=...
  python3 elevenlabs_tts.py --text "..." --voice EXAVITQu4vr4xnSDxMaL --out narr/n1.wav

Rules that came out of use:
 * Never use ElevenLabs audio as a "demo" of Lightning / Pulse / Atoms. Demos must be our own models.
 * A free-plan key cannot use library voices through the API (402 paid_plan_required). The house narrator
   "Belle B - Premium Ad Narrator" (SQQyvkXssth4s6HD2OuR) is a library voice, so it needs a paid plan.
   Premade voices work on free: Sarah EXAVITQu4vr4xnSDxMaL (premium female read, used for the entities video),
   Alice Xb7hH8MSUJpSbSDYk0k2, Matilda XrExE9yKIg1WjnnlVkGX, Bella hpp4J3VqNfWAUOO0d1Us, Eric cjVigY5qzO86Huf0OWal.
 * Settings used: model eleven_multilingual_v2, stability 0.5, similarity_boost 0.75, style 0.18, speaker boost on.
 * ElevenLabs reads continuously, so silencedetect finds few pauses; get word times with a transcriber (hyperframes transcribe).
"""
import argparse, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from smallest_tts import trim_silence

ap = argparse.ArgumentParser()
ap.add_argument("--text", required=True); ap.add_argument("--voice", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--model", default="eleven_multilingual_v2"); ap.add_argument("--style", type=float, default=0.18)
a = ap.parse_args()
key = os.environ.get("XI_KEY") or sys.exit("XI_KEY is not set")
os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
mp3 = a.out + ".mp3"
body = {"text": a.text, "model_id": a.model, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": a.style, "use_speaker_boost": True, "speed": 1.0}}
r = subprocess.run(["curl", "-s", "-X", "POST", f"https://api.elevenlabs.io/v1/text-to-speech/{a.voice}?output_format=mp3_44100_128", "-H", f"xi-api-key: {key}",
                    "-H", "Content-Type: application/json", "-d", json.dumps(body), "--output", mp3, "-w", "%{http_code}"], capture_output=True, text=True)
if r.stdout != "200":
    sys.exit(f"ElevenLabs failed: http {r.stdout}: {open(mp3, 'rb').read(300)!r}")
raw = a.out + ".raw.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "44100", "-ac", "1", raw], check=True)
dur = trim_silence(raw, a.out, pad_out=0.14)
os.remove(mp3); os.remove(raw)
print(json.dumps({"file": a.out, "dur": dur}))
