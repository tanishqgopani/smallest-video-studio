#!/usr/bin/env python3
"""Pulse STT -> json with word timestamps (+ optional speaker labels). Key from the environment.

  python3 smallest_stt.py call.mp3 --diarize --out pulse.json         # two-speaker call
  python3 smallest_stt.py clip.wav --out clip.json                    # one clip, word times
  python3 smallest_stt.py clip.wav --check "Hyundai"                  # does Pulse hear this word? (pronunciation sanity check)

Pulse stretches word *ends* through the pause that follows and can start a word early inside a pause.
Run build_transcript.py (same folder) to snap timings to the real audio before using them for animation.
Content-Type must match the file: audio/wav, audio/mpeg ...
"""
import argparse, json, mimetypes, os, subprocess, sys


def transcribe(path, diarize=False, model="pulse", language="en", itn=False):
    key = os.environ.get("SMALLEST_API_KEY")
    if not key:
        sys.exit("SMALLEST_API_KEY is not set")
    ctype = {".wav": "audio/wav", ".mp3": "audio/mpeg"}.get(os.path.splitext(path)[1].lower()) or mimetypes.guess_type(path)[0] or "application/octet-stream"
    q = f"model={model}&language={language}&word_timestamps=true" + ("&diarize=true" if diarize else "") + ("&itn_normalize=true" if itn else "")
    r = subprocess.run(["curl", "-s", "-X", "POST", f"https://api.smallest.ai/waves/v1/stt/?{q}", "-H", f"Authorization: Bearer {key}",
                        "-H", f"Content-Type: {ctype}", "--data-binary", f"@{path}"], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        sys.exit("STT failed: " + r.stdout[:300])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("--out"); ap.add_argument("--diarize", action="store_true")
    ap.add_argument("--model", default="pulse"); ap.add_argument("--check")
    a = ap.parse_args()
    d = transcribe(a.audio, a.diarize, a.model)
    if a.out:
        json.dump(d, open(a.out, "w"), ensure_ascii=False)
    print(d.get("transcription"))
    if a.check:
        ok = a.check.lower() in (d.get("transcription") or "").lower()
        print("heard correctly" if ok else "NOT heard correctly", f"({a.check!r})")
        sys.exit(0 if ok else 2)
