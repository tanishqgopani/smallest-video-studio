#!/usr/bin/env python3
"""Instant voice clone on Lightning v3.1 Pro.  CONSENT FIRST: only clone a voice the speaker has agreed to,
or (for demos) clone a stock Lightning voice. 5-15 s of clean speech, under 5 MB.

  export SMALLEST_API_KEY=...
  python3 clone_voice.py sample.wav --name demo-clone --out clone.json     # prints the voiceId

Gotcha: curl must send the multipart file with an explicit type, otherwise the API answers 'Invalid file type':
  -F "file=@sample.wav;type=audio/wav"
Use the returned voiceId as voice_id in smallest_tts.py with model lightning_v3.1_pro.
"""
import argparse, json, os, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("sample"); ap.add_argument("--name", required=True); ap.add_argument("--out", default="clone.json")
ap.add_argument("--language", default="en"); ap.add_argument("--accent", default="general")
a = ap.parse_args()
key = os.environ.get("SMALLEST_API_KEY") or sys.exit("SMALLEST_API_KEY is not set")
ctype = "audio/mpeg" if a.sample.lower().endswith(".mp3") else "audio/wav"
r = subprocess.run(["curl", "-s", "-X", "POST", "https://api.smallest.ai/waves/v1/voice-cloning", "-H", f"Authorization: Bearer {key}",
                    "-F", f"displayName={a.name}", "-F", f"file=@{a.sample};type={ctype}", "-F", "model=lightning-v3.1-pro",
                    "-F", f"language={a.language}", "-F", f"accent={a.accent}"], capture_output=True, text=True)
d = json.loads(r.stdout)
json.dump(d, open(a.out, "w"), indent=1)
print(d.get("data", {}).get("voiceId") or d)
