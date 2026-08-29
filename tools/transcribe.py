#!/usr/bin/env python3
"""
transcribe.py — Transcribe the GRAHA MARKETS class videos to text.

RUN THIS ON YOUR OWN MACHINE (not a restricted cloud sandbox): the first run
downloads a speech model, which needs open internet. It produces, per video, an
English translation with timestamps (and optionally a Tamil transcript) under
./transcripts/. Hand those .txt files to Claude to codify the method into rules.

------------------------------------------------------------------------------
SETUP  (use Python 3.12 — faster-whisper has no wheels for 3.13/3.14, and your
        default `python` is the Microsoft Store stub, so call it explicitly)

    winget install Python.Python.3.12        # if you don't have 3.12 yet
    py -3.12 -m venv .venv-tx
    .venv-tx\Scripts\Activate.ps1            # (Set-ExecutionPolicy -Scope Process -Bypass if blocked)
    pip install faster-whisper
    # ffmpeg must be on PATH — you already have it (winget install Gyan.FFmpeg)

RUN

    python transcribe.py "C:\\Users\\hgkri\\Downloads\\yt-grab"

    # better Tamil accuracy (slower):   --model large-v3
    # also emit the Tamil transcript:   --both
    # just one file:                    --only "ASTRO CLASS -4"

Model sizes: tiny < base < small < medium (default) < large-v3.
large-v3 is markedly better for Tamil but several times slower on CPU.
------------------------------------------------------------------------------
"""
import os, sys, argparse, time
from faster_whisper import WhisperModel

MEDIA_EXT = (".mp4", ".mkv", ".webm", ".m4a", ".mp3", ".wav")


def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def transcribe_one(model, path, outdir, task, suffix, language="ta"):
    # language=None lets Whisper detect it from the first 30 s — needed
    # for the Vikas classes, which mix Tamil and Hindi sessions
    segs, info = model.transcribe(path, language=language, task=task,
                                  beam_size=1, vad_filter=True)
    base = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(outdir, base + suffix)
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {base}\n# task={task} lang_prob={info.language_probability:.2f}\n\n")
        for s in segs:
            f.write(f"[{fmt(s.start)} - {fmt(s.end)}] {s.text.strip()}\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="folder containing the class videos")
    ap.add_argument("--model", default="medium",
                    help="tiny/base/small/medium/large-v3 (default medium)")
    ap.add_argument("--out", default="transcripts")
    ap.add_argument("--both", action="store_true",
                    help="also write the Tamil transcript (.ta.txt)")
    ap.add_argument("--only", default=None,
                    help="substring: transcribe only matching filenames")
    ap.add_argument("--lang", default="ta",
                    help="source language code, or 'auto' to detect per file "
                         "(default ta)")
    args = ap.parse_args()
    lang = None if args.lang.lower() == "auto" else args.lang

    os.makedirs(args.out, exist_ok=True)
    vids = [os.path.join(args.folder, f) for f in os.listdir(args.folder)
            if f.lower().endswith(MEDIA_EXT)]
    if args.only:
        vids = [v for v in vids if args.only.lower() in os.path.basename(v).lower()]
    vids.sort()
    if not vids:
        print("No media files found."); sys.exit(1)

    print(f"{len(vids)} file(s). Loading model '{args.model}' "
          f"(first run downloads it, ~minutes)...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    for i, v in enumerate(vids, 1):
        print(f"\n[{i}/{len(vids)}] {os.path.basename(v)}")
        t = time.time()
        en = transcribe_one(model, v, args.out, "translate", ".en.txt", lang)
        msg = os.path.basename(en)
        if args.both:
            ta = transcribe_one(model, v, args.out, "transcribe", ".ta.txt", lang)
            msg += " + " + os.path.basename(ta)
        print(f"   -> {msg}   ({time.time()-t:.0f}s)")

    print(f"\nDone. Transcripts in ./{args.out}/  — send the .en.txt files to Claude.")


if __name__ == "__main__":
    main()