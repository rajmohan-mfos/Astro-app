"""Build a zip holding ONLY what the bot needs to run.

The repository carries a third party's paid course material — the video
transcripts, the PPTX/DOCX originals and the tables extracted from them.
None of it is needed to serve the bot: the engine reads the ephemeris, not
the course notes. Uploading this zip instead of cloning keeps that
material off the hosting provider entirely.

Usage: python bot/package_for_deploy.py [out.zip]
"""
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Everything under these, minus __pycache__.
TREES = [
    os.path.join("backend", "app"),
    "bot",
]
FILES = [
    os.path.join("backend", "scripts", "daily_push.py"),
]
SKIP_DIRS = {"__pycache__", ".pytest_cache"}


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "astro-bot-deploy.zip"
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for tree in TREES:
            for dirpath, dirnames, filenames in os.walk(
                    os.path.join(ROOT, tree)):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for fn in filenames:
                    if fn.endswith((".pyc", ".pyo")):
                        continue
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.relpath(full, ROOT))
                    n += 1
        for f in FILES:
            z.write(os.path.join(ROOT, f), f)
            n += 1

    size = os.path.getsize(out) / 1024
    print(f"wrote {out} — {n} files, {size:.0f} KB")
    print("\nContains: backend/app, backend/scripts/daily_push.py, bot/")
    print("Excludes: knowledge/ (transcripts, course tables), docs/,")
    print("          tests/, frontend/, the backtest CSVs")


if __name__ == "__main__":
    main()
