#!/usr/bin/env python3
"""Audio -> data the composition can draw: a 36-band voice spectrum at 30 fps (for the mirrored waveform) and an amplitude envelope.

  python3 spectrum.py clip.wav --out clip.spec.json            # {"spec": [[36 floats] per frame], "env": [...], "dur": s}
  python3 spectrum.py a.wav b.wav --out all.js --var LINES     # several clips, normalised together, written as `window.LINES = [...]`

Smoothing is fast attack (0.7) / slower release (0.28): bars jump on a vowel and fall away naturally.
Draw it mirrored around the centre (bar i -> band |i-c|/c*33), tallest in the middle, and decay the last frame
over ~0.4s after the clip ends. Never write NaN into the json (empty bands are filled from the nearest bin).
"""
import argparse, json
import numpy as np
import scipy.io.wavfile as wav


def spec36(path, bands=36, fps=30, fmin=90, fmax=7000):
    sr, y = wav.read(path)
    yf = y.astype(np.float64) / 32768
    if yf.ndim > 1:
        yf = yf.mean(1)
    N = 1024 if sr >= 16000 else 512
    fq = np.fft.rfftfreq(N, 1 / sr)
    edges = np.geomspace(fmin, min(fmax, sr / 2 - 100), bands + 1)
    frames = []
    for f in range(max(1, int(len(yf) / sr * fps))):
        c = int(f / fps * sr)
        seg = yf[max(0, c - N // 2): c + N // 2]
        if len(seg) < N:
            seg = np.pad(seg, (0, N - len(seg)))
        sp = np.abs(np.fft.rfft(seg * np.hanning(N)))
        row = []
        for k in range(bands):
            m = (fq >= edges[k]) & (fq < edges[k + 1])
            row.append(float(np.sqrt((sp[m] ** 2).mean() + 1e-12)) if m.any() else float(sp[int(np.argmin(np.abs(fq - np.sqrt(edges[k] * edges[k + 1]))))] + 1e-6))
        frames.append(row)
    env = [float(np.sqrt((yf[i:i + sr // fps] ** 2).mean())) for i in range(0, len(yf) - sr // fps, sr // fps)]
    return np.array(frames), np.array(env), len(yf) / sr


def smooth(S, mx, floor_db=58):
    S = 20 * np.log10(S / mx + 1e-9)
    S = np.clip((S + floor_db) / floor_db, 0, 1) ** 1.35
    out = np.zeros_like(S)
    for f in range(len(S)):
        prev = out[f - 1] if f else np.zeros(S.shape[1])
        a = np.where(S[f] > prev, 0.7, 0.28)
        out[f] = prev + (S[f] - prev) * a
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("wavs", nargs="+"); ap.add_argument("--out", required=True); ap.add_argument("--var", default="SPEC")
    a = ap.parse_args()
    items = [spec36(p) for p in a.wavs]
    mx = max(i[0].max() for i in items); emx = max(i[1].max() for i in items) or 1
    data = [{"file": p, "dur": round(d, 3), "spec": [[round(float(v), 3) for v in r] for r in smooth(S, mx)], "env": [round(float(v / emx), 3) for v in e]}
            for p, (S, e, d) in zip(a.wavs, items)]
    payload = data[0] if len(data) == 1 and a.out.endswith(".json") else data
    if a.out.endswith(".js"):
        open(a.out, "w").write(f"window.{a.var}=" + json.dumps(data) + ";")
    else:
        json.dump(payload, open(a.out, "w"))
    print("wrote", a.out, [d["dur"] for d in data])
