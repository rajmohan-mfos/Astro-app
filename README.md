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

## Daily prediction to Telegram (GitHub Actions)

`.github/workflows/daily-prediction.yml` runs `backend/scripts/daily_push.py`
on weekdays and sends the day's reading to a Telegram chat.

**Telegram rather than WhatsApp** — a bot is free and needs no approval,
and it addresses a *chat id*, so your phone number never enters the
repository, its logs, or any commit. WhatsApp would need Twilio or Meta's
Business API, both paid, and business-initiated messages there require
pre-approved template messages.

### Setup (one time)

1. In Telegram, message **@BotFather** → `/newbot` → follow the prompts.
   It gives you a token like `123456:ABC-DEF...`.
2. Send your new bot any message (it cannot message you first).
3. Get your chat id — open in a browser:
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   and read `result[0].message.chat.id`.
4. In the repo: **Settings → Secrets and variables → Actions → New
   repository secret**, add both:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. Test without waiting for the cron: **Actions → Daily prediction to
   Telegram → Run workflow**. Set *dry_run* to `1` to print the message
   into the job log instead of sending it.

### Timing, and why it is not 09:10

The cron is `45 2 * * 1-5` — 02:45 UTC, **08:15 IST**, a full hour before
the 09:15 open. GitHub's scheduled workflows are best-effort: they
routinely start 5–20 minutes late and under load can be delayed much
further or skipped entirely. The hour of slack is what makes an ordinary
delay still arrive in time. Tightening it to 09:00 IST would mean
regularly missing the open.

Two other things to know:

- **NSE trading holidays are not handled.** The job fires every weekday,
  so expect a message on holidays.
- **GitHub disables cron on repos with no activity for 60 days.** If the
  messages stop, push any commit or re-enable the workflow.

### The message is not a trading signal

The push carries the same disclaimer the app does, and it is there for a
measured reason: a 5-year backtest across Nifty, BankNifty, Metal, Pharma
and a Defence proxy found **no forecasting ability on any of them** — the
engine loses to "always predict down" on every index (see
`backend/knowledge/backtest/RESULTS.md`). A daily notification makes a
study aid *feel* like a signal, which is exactly why the disclaimer ships
inside every message rather than only in the UI.
