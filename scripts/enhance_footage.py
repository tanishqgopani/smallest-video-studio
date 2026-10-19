"""Enhance the raw phone clip: lock exposure per frame (kills flicker + AE pumping + screen-dim swing),
temporal denoise, cool premium grade, sharpen, and prepend a 2s hold so the call timer matches the audio."""
import subprocess, sys, json, re, numpy as np
V = sys.argv[1]; OUT = sys.argv[2]
DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 105.6        # seconds of source to use
HOLD = int(sys.argv[4]) if len(sys.argv) > 4 else 60           # frames of held first frame
W, H = 1920, 1080

def chan_stats():
    """per-frame mean RGB of a background crop and of the phone screen (measured on a 480x270 proxy)"""
    dec = subprocess.Popen(["ffmpeg","-v","error","-i",V,"-t",str(DUR),"-vf","fps=30,scale=480:270,format=rgb24",
                            "-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
    B, S = [], []
    while True:
        buf = dec.stdout.read(480*270*3)
        if len(buf) < 480*270*3: break
        f = np.frombuffer(buf, np.uint8).reshape(270, 480, 3).astype(np.float32)
        B.append(f[100:225, 275:400].mean((0,1))); S.append(f[75:250, 45:185].mean((0,1)))
    return np.array(B), np.array(S)
bg3, sc3 = chan_stats()
lum = lambda x: 0.299*x[:,0] + 0.587*x[:,1] + 0.114*x[:,2]
bg, sc = lum(bg3), lum(sc3)
n = len(bg)
tb, ts = np.median(bg[150:]), np.median(sc[150:])
gb = np.clip(tb / bg, 0.45, 2.5); gs = np.clip(ts / sc, 0.45, 2.5)      # scalar brightness lock per frame
print("frames", n, "targets", tb, ts, "gain range bg", gb.min(), gb.max(), "screen", gs.min(), gs.max(), flush=True)

hold = (gs > 1.06).astype(np.float32)
hold = np.maximum.reduce([np.roll(hold, d) for d in range(-5, 6)])           # dilate +-5 frames
hold = np.convolve(hold, np.ones(11)/11, mode="same")                         # soft edges
print("hold frames", int((hold>0.5).sum()), flush=True)

# feathered mask for the phone screen region
mask = np.zeros((H, W), np.float32); mask[170:H, 140:830] = 1
from scipy.ndimage import gaussian_filter
mask = gaussian_filter(mask, 22)[..., None]

GRADE = ("colorchannelmixer=rr=0.62:rg=0.30:rb=0.08:gr=0.04:gg=0.92:gb=0.06:br=0.03:bg=0.10:bb=1.08,"
         "colorbalance=bs=0.10:bm=0.08:rh=-0.06,"
         "curves=all='0/0 0.10/0.075 0.5/0.50 0.8/0.84 1/1',"
         "eq=contrast=1.14:saturation=1.05:gamma=0.96,unsharp=7:7:0.9:5:5:0.0,vignette=angle=PI/4.5")
dec = subprocess.Popen(["ffmpeg","-v","error","-i",V,"-t",str(DUR),"-vf","fps=30,hqdn3d=6:5:9:7,format=rgb24",
                        "-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE, bufsize=W*H*3*2)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-",
                        "-vf",GRADE+",format=yuv420p","-c:v","libx264","-crf","14","-preset","medium","-g","30","-keyint_min","30",
                        "-sc_threshold","0","-movflags","+faststart",OUT], stdin=subprocess.PIPE)
first = None
good = None
i = 0
while True:
    buf = dec.stdout.read(W*H*3)
    if len(buf) < W*H*3: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
    k = min(i, n-1)
    g = gb[k]*(1-mask) + gs[k]*mask
    f = f*g
    # the phone really dims its backlight for ~3s twice: hold the last good screen through those frames (soft blend in/out)
    w = float(hold[k])
    if w <= 0.0:
        good = f.copy()
    elif good is not None:
        f = f*(1-mask*w) + good*(mask*w)
    o = np.clip(f, 0, 255).astype(np.uint8)
    if first is None:
        first = o.copy()
        for _ in range(HOLD): enc.stdin.write(first.tobytes())
    enc.stdin.write(o.tobytes())
    i += 1
    if i % 300 == 0: print("frame", i, flush=True)
enc.stdin.close(); enc.wait(); dec.wait()
print("done", i, "frames +", HOLD, "hold", flush=True)
