"""Pulse STT JSON (diarized, word-timestamped) -> transcript.js for the call-video composition.
 1. snap word starts/ends to the real speech (Pulse stretches ends through pauses and can start words early inside pauses)
 2. fold spoken amounts / IDs into the written token (merge groups), fix ASR slips, tag BFSI terms
 3. group into speaker turns
usage: build_transcript.py pulse.json audio.mp3 out_dir"""
import json, re, subprocess, sys
pulse, audio, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(pulse)); W = d["words"]
# ---- 1. timing clean-up against the audio itself
err = subprocess.run(["ffmpeg","-v","info","-i",audio,"-ac","1","-af","silencedetect=noise=-40dB:d=0.2","-f","null","-"],capture_output=True,text=True).stderr
SIL = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)",err)],[float(x) for x in re.findall(r"silence_end: ([\d.]+)",err)]))
moved_s, moved_e = [], []
for w in W:
    for a, b in SIL:
        if a - 0.02 <= w["start"] < b - 0.03 and b - a >= 0.25:       # starts inside a pause -> the sound really begins when the pause ends
            moved_s.append((w["word"], round(w["start"],2), round(b-0.03,2))); w["start"] = b - 0.03; w["end"] = max(w["end"], w["start"] + 0.2); break
    for a, b in SIL:
        if w["start"] < a < w["end"] - 0.1 and b - a >= 0.25:           # ends inside a pause -> speech stops where the pause starts
            moved_e.append((w["word"], round(w["end"],2), round(a+0.05,2))); w["end"] = a + 0.05; break
print("starts snapped:", moved_s); print("ends clamped:", len(moved_e))
# ---- 2. text rules, matched on the words themselves
norm = lambda w: re.sub(r"[^a-z0-9\-]", "", w.lower()); N = [norm(w["word"]) for w in W]
trail = lambda w: (re.search(r"[.,?!]+$", w) or [""])[0] if re.search(r"[.,?!]+$", w) else ""
AMT = [(["forty-two","thousand","five","hundred","rupees"],"₹42,500"),(["eight","thousand","four","hundred","rupees"],"₹8,400"),(["three","lakh","rupees"],"₹3,00,000"),(["five","hundred","rupees"],"₹500")]
DIG = ["zero","zero","zero","four","two","one","seven"]
IDS = [(["mrdn"]+DIG,"MRDN0004217"),(["m","r","d","n"]+DIG,"MRDN0004217"),(["abc","pm","four","two","one","seven","k"],"ABCPM4217K")]
groups = {}; i = 0
while i < len(N):
    hit = None
    for seq, fin in AMT:
        if N[i:i+len(seq)] == seq: hit = (i+len(seq)-1, fin+trail(W[i+len(seq)-1]["word"]), "amt"); break
    if not hit:
        for seq, fin in IDS:
            if N[i:i+len(seq)] == seq: hit = (i+len(seq)-1, fin+trail(W[i+len(seq)-1]["word"]), "id"); break
    if hit: groups[i] = hit; i = hit[0] + 1
    else: i += 1
sub = {}
for i, n in enumerate(N):
    if n in ("sibil","sybil","cibil") and N[i+1:i+2] == ["score"]: sub[i] = "CIBIL"
    if n == "principle": sub[i] = "principal" + trail(W[i]["word"])
    if n == "autodebited": sub[i] = "auto-debited" + trail(W[i]["word"])
    if n == "great": sub[i] = "Great" + trail(W[i]["word"])
    if N[i:i+5] == ["is","there","a","foreclosure","charges"]: sub[i] = "Are"; sub[i+2] = ""
PH = [["home","loan"],["emi"],["nach","mandate"],["overdue"],["salary","account"],["mandate"],["ifsc","code"],["ifsc"],["pan"],["kyc"],["bounce","charge"],["upi"],
      ["sibil","score"],["sybil","score"],["cibil","score"],["part","prepayment"],["prepayment"],["foreclosure","charges"],["foreclosure","charge"],["floating","rate","loan"],
      ["outstanding","principle"],["outstanding","principal"],["tenure"],["loan","insurance","premium"],["autodebited"],["nominee"],["interest","certificate"]]
PH.sort(key=lambda p: -len(p)); isterm = set(); i = 0
while i < len(N):
    for p in PH:
        if N[i:i+len(p)] == p: isterm.update(range(i, i+len(p))); i += len(p) - 1; break
    i += 1
items = []; i = 0
while i < len(W):
    if i in groups:
        b, fin, kind = groups[i]; raw = [{"t":W[k]["word"],"s":W[k]["start"],"e":W[k]["end"]} for k in range(i, b+1)]
        items.append({"g":1,"raw":raw,"fin":fin,"kind":kind,"tag":None,"s":raw[0]["s"],"e":raw[-1]["e"],"sp":W[i]["speaker"]}); i = b + 1; continue
    t = sub.get(i, W[i]["word"])
    if t != "": items.append({"t":t,"s":W[i]["start"],"e":W[i]["end"],"sp":W[i]["speaker"],"term":1 if i in isterm else 0})
    i += 1
# ---- 3. speaker turns
turns = []
for it in items:
    if not turns or turns[-1]["sp"] != it["sp"] or it["s"] - turns[-1]["items"][-1]["e"] > 2.2: turns.append({"sp":it["sp"],"items":[]})
    turns[-1]["items"].append(it)
out = {"turns":[{"sp":u["sp"],"start":u["items"][0]["s"],"end":u["items"][-1]["e"],"items":u["items"]} for u in turns],"speakers":{"0":"Agent","1":"Customer"}}
open(outdir + "/transcript2.js", "w").write("window.TRANSCRIPT=" + json.dumps(out, ensure_ascii=False) + ";")
print(len(out["turns"]), "turns;", len(groups), "merge groups;", sum(1 for t in out["turns"] for x in t["items"] if x.get("term")), "term words")
