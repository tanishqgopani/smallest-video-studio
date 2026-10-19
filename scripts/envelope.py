#!/usr/bin/env python3
"""Amplitude envelopes for a composition, with no numpy needed.

  python3 envelope.py n1.wav n2.wav ... --out assets/data.js

Writes `window.N = {"n1": {"dur": s, "env": [0..1 per 1/30 s]}, ...}`, normalised across all clips (keys are the file stems).
Clips must be 16-bit mono wav. Convert first:  ffmpeg -i in.aiff -ar 24000 -ac 1 out.wav
Use it for narrator waveforms, "signal flowing through" visuals and frame-by-frame scenes; for the 36-band spectrum use spectrum.py.
"""
import argparse, json, math, os, struct, wave

ap = argparse.ArgumentParser()
ap.add_argument("wavs", nargs="+")
ap.add_argument("--out", required=True)
ap.add_argument("--var", default="N")
a = ap.parse_args()

out, mx = {}, 1e-9
for p in a.wavs:
    w = wave.open(p)
    sr, n = w.getframerate(), w.getnframes()
    y = struct.unpack("<%dh" % n, w.readframes(n))
    h = max(1, sr // 30)
    env = [math.sqrt(sum(v * v for v in y[k:k + h]) / h) / 32768 for k in range(0, n - h, h)]
    out[os.path.splitext(os.path.basename(p))[0]] = {"dur": round(n / sr, 3), "env": env}
    mx = max(mx, max(env or [0]))
for v in out.values():
    v["env"] = [round(x / mx, 3) for x in v["env"]]
open(a.out, "w").write("window.%s=%s;" % (a.var, json.dumps(out)))
print({k: v["dur"] for k, v in out.items()})
