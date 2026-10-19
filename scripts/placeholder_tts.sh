#!/bin/sh
# Placeholder narration with the macOS built-in voice. Offline, no key, no download.
# ONLY for when the user has not supplied a voice key and cannot be reached. Say so plainly in the hand-off and
# offer to re-narrate and re-time once a key arrives. Never present it as a product voice.
#
#   placeholder_tts.sh out_dir clip1.txt clip2.txt ...      -> out_dir/<stem>.wav  (24 kHz mono, silence trimmed, 60 ms lead / 120 ms tail)
#   VOICE=Daniel RATE=165 placeholder_tts.sh ...
set -e
OUT="$1"; shift; mkdir -p "$OUT"
VOICE="${VOICE:-Daniel}"; RATE="${RATE:-165}"
for f in "$@"; do
  s=$(basename "$f" .txt)
  say -v "$VOICE" -r "$RATE" -o "$OUT/$s.aiff" -f "$f"
  ffmpeg -y -loglevel error -i "$OUT/$s.aiff" -ar 24000 -ac 1 "$OUT/$s.raw.wav"
  # trim: forward pass, reverse pass (do not chain afade+areverse tricks: that produced silent files once)
  ffmpeg -y -loglevel error -i "$OUT/$s.raw.wav" -af "silenceremove=start_periods=1:start_threshold=-46dB,areverse,silenceremove=start_periods=1:start_threshold=-46dB,areverse" "$OUT/$s.t.wav"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$s.t.wav")
  ffmpeg -y -loglevel error -i "$OUT/$s.t.wav" -af "adelay=60:all=1,apad=pad_dur=0.12,afade=t=in:d=0.02" -t "$(python3 -c "print(round($d+0.18,3))")" "$OUT/$s.wav"
  rm -f "$OUT/$s.aiff" "$OUT/$s.raw.wav" "$OUT/$s.t.wav"
  echo "$s $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$s.wav")"
done
# Check the result is not silent:  ffmpeg -i clip.wav -af volumedetect -f null -   (max_volume should be around -2 dB, not -50)
