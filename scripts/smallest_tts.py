#!/usr/bin/env python3
"""Lightning TTS -> trimmed wav (+ duration json).  Key comes from the environment, never from a file.

  export SMALLEST_API_KEY=...            # ask the user for a fresh key if you get 'unauthorized'
  python3 smallest_tts.py --text "Hello." --voice kaitlyn --out out/hello.wav
  python3 smallest_tts.py --text "Hi Siobhan" --voice blake --dict <pronunciation_dict_id> --out out/x.wav

Voices that worked well:  narrator meher | agent blake | caller/original kaitlyn | UK sophie.
Pro voices only work with model lightning_v3.1_pro; standard voices with lightning_v3.1.
Needs: ffmpeg, numpy, scipy (pip install numpy scipy in a venv).
"""
import argparse, json, os, subprocess, sys
import numpy as np
import scipy.io.wavfile as wav


def synth(text, voice, out_raw, model="lightning_v3.1_pro", speed=1.0, dict_id=None, language="en"):
    key = os.environ.get("SMALLEST_API_KEY")
    if not key:
        sys.exit("SMALLEST_API_KEY is not set")
    body = {"text": text, "voice_id": voice, "model": model, "sample_rate": 24000, "speed": speed,
            "language": language, "output_format": "wav"}
    if dict_id:
        body["pronunciation_dicts"] = [dict_id]
    r = subprocess.run(["curl", "-s", "-X", "POST", "https://api.smallest.ai/waves/v1/tts",
                        "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json", "-H", "Accept: audio/wav",
                        "-d", json.dumps(body), "--output", out_raw, "-w", "%{http_code}"], capture_output=True, text=True)
    if r.stdout != "200":
        sys.exit(f"TTS failed: http {r.stdout}: {open(out_raw, 'rb').read(200)!r}")


def trim_silence(raw, out, floor_db=-46, pad_in=0.06, pad_out=0.12):
    """cut leading/trailing silence, add tiny fades. Returns trimmed duration in seconds."""
    sr, x = wav.read(raw)
    xf = x.astype(np.float64) / 32768
    hop = int(sr * 0.01)
    e = np.array([np.sqrt((xf[i:i + hop] ** 2).mean()) for i in range(0, len(xf) - hop, hop)])
    idx = np.where(20 * np.log10(e + 1e-9) > floor_db)[0]
    a = max(0, idx[0] * 0.01 - pad_in)
    b = min(len(xf) / sr, (idx[-1] + 1) * 0.01 + pad_out)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", raw,
                    "-af", f"afade=t=in:d=0.01,afade=t=out:st={b - a - 0.04:.3f}:d=0.04", out], check=True)
    return round(b - a, 3)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True); ap.add_argument("--voice", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="lightning_v3.1_pro"); ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--dict", dest="dict_id"); ap.add_argument("--language", default="en")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    raw = a.out + ".raw.wav"
    synth(a.text, a.voice, raw, a.model, a.speed, a.dict_id, a.language)
    dur = trim_silence(raw, a.out)
    os.remove(raw)
    print(json.dumps({"file": a.out, "dur": dur, "text": a.text, "voice": a.voice}))
