# Astro-app

Personal Vedic-astrology (jothidam) tool — React frontend, FastAPI backend.
Build brief: `Astro-app-SPEC.md`.

## Backend

> **Python version note:** the spec says 3.12, but `pyswisseph` ships Windows wheels
> only up to CPython **3.11** — on 3.12+ pip tries to compile from source and fails
> without MSVC Build Tools. The venv therefore uses **Python 3.11** (installed via
> `winget install Python.Python.3.11`). Python 3.12 is also installed on this machine
> for the Milestone 6 transcription tool (`faster-whisper`).

```
cd backend
py -3.11 -m venv .venv          # already created
.venv\Scripts\activate
pip install -r requirements.txt  # fastapi uvicorn pyswisseph pytest
uvicorn app.main:app --reload --port 8000
```

Health check: http://127.0.0.1:8000/api/health → `{"ok":true}`

Tests (Milestone 2 onward): `.venv\Scripts\python -m pytest tests/`

## Frontend

```
cd frontend
npm install
npm run dev        # Vite serves http://localhost:5173, proxies /api → :8000
```

Run the backend first; the page shows a "connected ✓" indicator when the proxy works.

## What the app does now

- **Jothidam tab**: panchang tiles, KP planet-position sheet with the
  sunrise ruling chain, the advance prediction chart (X/X1/Y/Y1 chips +
  per-window graph), South Indian rasi chart (copy-as-text), graha table,
  and the rule findings for intraday/weekly/monthly/long-term/prasanam.
- **Panchang chart (KP) tab**: the author-style day sheet — Moon sub-lord
  transit table, other-graha transits, panchang end times.
- **Today / Tomorrow** buttons; **My profile** saves your kundali in the
  browser and answers "can I trade today" (Moon 5/8/12 gochara rule).
- Rule provenance: `backend/knowledge/RULES-SOURCES.md` and
  `MASTER-RULES.md`; scenario regressions in `backend/tests/`.
- Backtest: `backend/scripts/backtest_nifty.py N` (results in
  `backend/knowledge/backtest/` — 5-year result: no predictive edge; the
  app is a study aid, not a trading system).
