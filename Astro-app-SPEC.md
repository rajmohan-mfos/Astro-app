# Astro-app — Build Specification

A personal Vedic-astrology (jothidam) tool. **React** front end, **Python (FastAPI)** back end.
This document is the build brief for Claude Code. The astronomy in Section 5 has been
**validated against the Swiss Ephemeris to < 0.006°** — implement it as written; don't
re-derive it.

> Workspace: `C:\Users\hgkri\workspace\Astro-app`
> How to use this file: open Claude Code in that folder and say
> *"Read SPEC.md and scaffold the project per Milestone 1, then stop for review."*
> Build one milestone at a time (Section 9) rather than all at once.

---

## 1. Vision — two layers

The app has two clearly separated layers. Keep them separate in code; it is the single most
important design decision here.

**Layer A — the astronomical engine (this spec fully defines it).**
For any date / time / place it computes the sidereal (Lahiri) rasi chart, the lagna, and the
full panchang (vaara, thithi, natchathiram + pada, yogam, karanam). This is deterministic
astronomy and is *done* — the formulas and test values are below.

**Layer B — the taught prediction method (built later, from video transcripts).**
This is **financial / market astrology**, not natal horoscopy. The source is the YouTube
channel **GRAHA MARKETS** (@GRAHAMARKETS) — a course on forecasting **Nifty 50 / Bank Nifty**
movements from planetary and panchang factors. The "graph prediction" means predicting the
*market price graph* (e.g. "tomorrow's graph"); "long-term prediction" means investment
horizon; "prasanam" is horary for a market question. This layer is the app's real
differentiator. It is **not** fully in this spec because it lives in the videos and must be
transcribed first (Section 8, and the domain map in **Appendix C**). Build it as a pluggable
rules module (`predict.py`) so the engine never changes as the method grows.

**Read the disclaimer in Appendix C before building Layer B.** This is educational, is not
SEBI-registered advice, and astrology-based market forecasting has no demonstrated predictive
edge — the app is a study tool, not a trading system.

Non-goal for v1: user accounts, database, or hosting. This is a local personal tool.

---

## 2. Tech stack & key decisions

| Concern | Choice | Why |
|---|---|---|
| Backend | Python 3.12 + FastAPI + Uvicorn | Fast, typed, trivial JSON API |
| Ephemeris | `pyswisseph` | Gold-standard sidereal engine; no data files needed (Moshier) |
| Frontend | React 18 + Vite + TypeScript | Fast dev server, no config, single-page |
| Styling | Plain CSS (dark theme, tokens) | No framework needed; theme in Section 7 |
| HTTP | `fetch` from frontend → FastAPI | Vite dev proxy `/api` → `:8000` |

**CRITICAL environment note — do not skip.** `pyswisseph` ships prebuilt wheels for
CPython **3.11 and 3.12** but *not* 3.13/3.14. On 3.14 pip tries to compile from source and
fails with *"Microsoft Visual C++ 14.0 or greater is required."* The user's machine hit
exactly this. **Create the backend venv with Python 3.12.** If only 3.14 is available, either
install Python 3.12 (`winget install Python.Python.3.12`) or, as a fallback, swap the engine
to `astronomy-engine` (pure Python, no compiler) using the formulas in Appendix B — the pure
formula path is already validated. Prefer pyswisseph on 3.12.

---

## 3. Repository structure

```
Astro-app/
├─ SPEC.md                      ← this file
├─ README.md                    ← generated: run instructions
├─ backend/
│  ├─ pyproject.toml            ← or requirements.txt
│  ├─ app/
│  │  ├─ main.py                ← FastAPI app + /api/compute
│  │  ├─ engine.py              ← Layer A (Section 5). The tested core.
│  │  ├─ panchang.py            ← thithi/nakshatra/yoga/karana/vaara helpers
│  │  ├─ names.py               ← rasi / nakshatra / graha name tables (Section 6)
│  │  └─ predict.py             ← Layer B (stub now; Section 8)
│  └─ tests/
│     └─ test_engine.py         ← fixtures in Section 5.7 (must pass)
└─ frontend/
   ├─ index.html
   ├─ vite.config.ts            ← proxy /api → http://127.0.0.1:8000
   ├─ package.json
   └─ src/
      ├─ main.tsx
      ├─ App.tsx                ← form + orchestration
      ├─ api.ts                 ← typed fetch to /api/compute
      ├─ types.ts               ← ComputeResult interface
      ├─ theme.css              ← Section 7 tokens
      └─ components/
         ├─ InputPanel.tsx
         ├─ PanchangTiles.tsx
         ├─ SouthIndianChart.tsx
         ├─ GrahaTable.tsx
         └─ PredictionPanel.tsx
```

---

## 4. API contract

### `POST /api/compute`

Request:
```json
{ "year":1990, "month":1, "day":1, "hour":12, "minute":0,
  "tz_offset":5.5, "lat":13.0827, "lon":80.2707 }
```
`tz_offset` = hours east of UTC (India = 5.5). `hour` is 24-hour local clock time.

Response (shape the frontend depends on):
```json
{
  "input": { "date":"1990-01-01", "time":"12:00", "tz_offset":5.5, "lat":13.0827, "lon":80.2707 },
  "ayanamsa": 23.7174,
  "lagna": { "lon":346.4685, "sign":11, "rasi":"Meena", "rasi_ta":"மீனம்", "deg_in_sign":"16°28'" },
  "grahas": [
    { "name":"Sun","name_ta":"சூரியன்","lon":256.86,"sign":8,
      "rasi":"Dhanu","rasi_ta":"தனுசு","deg_in_sign":"16°52'","retro":false }
    /* … Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu */
  ],
  "chart": [["…tokens for Mesha…"], /* 12 arrays, index 0=Mesha … 11=Meena */],
  "panchang": {
    "vaara": {"en":"Monday","ta":"திங்கள்"},
    "thithi": {"num":5,"name":"Panchami","paksha":"Shukla"},
    "natchathiram": {"num":23,"name":"Dhanishta","name_ta":"அவிட்டம்","pada":4},
    "yogam": {"num":16,"name":"Siddhi"},
    "karanam": {"num":9,"name":"Bava"}
  },
  "prediction": { "status":"stub", "summary":[ "…" ], "note":"…" }
}
```
`chart[sign]` holds short tokens: `La` (lagna) and `Su Mo Ma Me Ju Ve Sa Ra Ke`, each with
`(R)` appended when retrograde. Sign index: 0=Mesha, 1=Vrishabha, … 11=Meena.

Errors → HTTP 400 `{ "error": "message" }`.

---

## 5. Layer A — the astronomy engine (VALIDATED — implement exactly)

All longitudes are **sidereal, Lahiri ayanamsa**, in degrees `[0,360)`.

### 5.1 Time
```
ut_hour = hour + minute/60 - tz_offset
jd      = swe.julday(year, month, day, ut_hour)   # rolls the day correctly
```

### 5.2 Ayanamsa & grahas (pyswisseph)
```python
import swisseph as swe
FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

# per graha: lon = swe.calc_ut(jd, body, FLAGS)[0][0]  (already sidereal)
# retro: the speed component [0][3] < 0  (do NOT flag Sun/Moon)
```
Bodies: `swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN`,
and `swe.MEAN_NODE` for **Rahu**. **Ketu = (Rahu + 180) mod 360.** Rahu & Ketu are always
shown retrograde.

### 5.3 Lagna (ascendant)
```python
cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
asc = ascmc[0] % 360           # already sidereal
```
(`b'W'` = whole-sign houses; only the ascendant degree is used for v1.)

### 5.4 Panchang
Let `sun`, `moon` be sidereal longitudes; `seg = 360/27`.
```
elongation   = (moon - sun) % 360
thithi_idx   = floor(elongation / 12)          # 0..29
paksha       = "Shukla" if thithi_idx < 15 else "Krishna"
thithi_name  = THITHI[thithi_idx % 15]         # table in §6

nak_idx      = floor(moon / seg)               # 0..26
pada         = floor((moon % seg) / (seg/4)) + 1   # 1..4

yoga_idx     = floor(((sun + moon) % 360) / seg)   # 0..26

k            = floor(elongation / 6)           # 0..59
if k == 0:      karana = "Kimstughna"
elif k >= 57:   karana = ["Shakuni","Chatushpada","Naga"][k-57]
else:           karana = KARANA_MOVABLE[(k-1) % 7]   # §6
```

### 5.5 Vaara (weekday) — read this carefully
Use the **local civil date** at (year, month, day), NOT `swe.day_of_week(jd)`.
`swe.day_of_week` operates on the UT Julian day; for early-morning births in IST the UT date
rolls back a day and returns the wrong weekday (verified: a 03:15 IST birth returned Saturday
when the correct local vaara was Sunday). Compute from the civil calendar date directly:
```python
import datetime
idx = datetime.date(year, month, day).weekday()   # Mon=0 … Sun=6
```
(Traditional panchang starts the day at sunrise; civil-local is the v1 approximation and is
the right default. Sunrise-based vaara is a future refinement — Section 10.)

### 5.6 South Indian chart placement
Fixed-sign layout on a 4×4 grid; center 2×2 is the title block. Sign index → grid cell
`[row, col]` (1-based):
```
11:[1,1] 0:[1,2] 1:[1,3] 2:[1,4]
10:[2,1]                  3:[2,4]
 9:[3,1]                  4:[3,4]
 8:[4,1] 7:[4,2] 6:[4,3] 5:[4,4]
```

### 5.7 Validation fixtures — write these as tests (`tests/test_engine.py`)
All inputs use `tz_offset = 5.5`. Assert planet/lagna longitudes within **0.02°**, and exact
matches for ayanamsa (3 dp), thithi/nakshatra/pada/yoga/karana numbers, and vaara.

| # | date | time | lat, lon | ayanamsa | lagna° | vaara | thithi# | nak#/pada | yoga# | karana# |
|---|------|------|----------|----------|--------|-------|---------|-----------|-------|---------|
| 1 | 1990-01-01 | 12:00 | 13.0827, 80.2707 | 23.7174 | 346.468 | Monday | 5 | 23 / 4 | 16 | 9 |
| 2 | 1985-06-15 | 07:30 | 13.0827, 80.2707 | 23.6539 | 83.918 | Saturday | 27 | 2 / 3 | 7 | 54 |
| 3 | 2001-11-23 | 18:45 | 12.9716, 77.5946 | 23.8836 | 51.791 | Friday | 9 | 24 / 3 | 13 | 17 |
| 4 | 1975-03-09 | 03:15 | 19.0760, 72.8777 | 23.5104 | 262.013 | **Sunday** | 27 | 21 / 4 | 19 | 53 |

Reference graha longitudes (sidereal) for case 1 — sanity check:
Sun 256.860, Moon 306.465, Mars 226.118, Mercury 272.014, Jupiter 71.459, Venus 282.530,
Saturn 261.910, Rahu 294.726, Ketu 114.726.

> Note: case 4 vaara is **Sunday** by the civil-date rule in §5.5. If a naive
> `swe.day_of_week` implementation returns Saturday, that test correctly fails — fix the
> implementation, not the fixture.

---

## 6. Name tables (`names.py`) — copy verbatim

```python
RASIS = ["Mesha","Vrishabha","Mithuna","Kataka","Simha","Kanya",
         "Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"]
RASIS_TA = ["மேஷம்","ரிஷபம்","மிதுனம்","கடகம்","சிம்மம்","கன்னி",
            "துலாம்","விருச்சிகம்","தனுசு","மகரம்","கும்பம்","மீனம்"]

NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
  "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
  "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
  "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
NAKSHATRAS_TA = ["அசுவினி","பரணி","கார்த்திகை","ரோகிணி","மிருகசீரிஷம்","திருவாதிரை",
  "புனர்பூசம்","பூசம்","ஆயில்யம்","மகம்","பூரம்","உத்திரம்","அஸ்தம்","சித்திரை","சுவாதி",
  "விசாகம்","அனுஷம்","கேட்டை","மூலம்","பூராடம்","உத்திராடம்","திருவோணம்","அவிட்டம்",
  "சதயம்","பூரட்டாதி","உத்திரட்டாதி","ரேவதி"]

THITHIS = ["Prathamai","Dwitiyai","Tritiyai","Chaturthi","Panchami","Shashti","Saptami",
  "Ashtami","Navami","Dasami","Ekadasi","Dwadasi","Trayodasi","Chaturdasi","Pournami/Amavasai"]

YOGAS = ["Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarman","Dhriti",
  "Shula","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
  "Variyan","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"]

KARANA_MOVABLE = ["Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti"]

WEEKDAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WEEKDAYS_TA = ["திங்கள்","செவ்வாய்","புதன்","வியாழன்","வெள்ளி","சனி","ஞாயிறு"]

GRAHA_TA = {"Sun":"சூரியன்","Moon":"சந்திரன்","Mars":"செவ்வாய்","Mercury":"புதன்",
  "Jupiter":"குரு","Venus":"சுக்கிரன்","Saturn":"சனி","Rahu":"ராகு","Ketu":"கேது"}
```
Degree-in-sign display format: `DD°MM'` (e.g., `16°28'`), computed from `lon % 30`.

---

## 7. Frontend spec

Single page, dark theme, two columns (input left, output right; stack under 900px).
Sections top-to-bottom on the right: **Panchang tiles** (5), **South Indian chart**,
**Graha table**, **Prediction panel**.

Design tokens (`theme.css`):
```css
--bg:#0f1216; --panel:#171b21; --line:#2a313b; --ink:#e8ecf1;
--muted:#9aa6b2; --accent:#d9a441; --accent2:#5aa9e6; --cell:#12161b;
```
Accent gold `--accent` = lagna + buttons + chart border. Retrograde text = `#e77`.

Components:
- **InputPanel** — day/month/year, hour/minute, a place `<select>` (Chennai, Bengaluru,
  Madurai, Coimbatore, Mumbai, Delhi, + Custom lat/lon), timezone (default 5.5), Compute button.
  Auto-compute once on load with the default (1990-01-01 12:00 Chennai).
- **PanchangTiles** — Vaara / Thithi / Natchathiram / Yogam / Karanam. Show Tamil + English.
- **SouthIndianChart** — 4×4 CSS grid using the cell map in §5.6; center tile shows lagna rasi
  (Tamil), degree, and the input date/time. Each cell: Tamil rasi name (top-left, muted) + the
  graha tokens; `La` in gold, `(R)` tokens in red.
- **GrahaTable** — Graha (En · Ta) | Rasi (En + Ta) | Degree | Retro.
- **PredictionPanel** — renders `prediction.summary` as a list + `prediction.note`; a small
  `status` chip ("stub" now).

A fully working single-file reference implementation of this exact UI + math is provided
alongside this spec (`jothidam_prototype.html`). Use it as the visual target and as a
**living oracle**: the React build must produce the same numbers for the §5.7 fixtures.

---

## 8. Layer B — the taught method (later milestone)

`predict.py` starts as a stub returning `{status:"stub", summary:[…chart facts…], note:…}`.
The real method is **financial-astrology** market forecasting from the **GRAHA MARKETS**
course (see Appendix C for the domain map, curriculum, and disclaimer). Transcribe the videos
in `C:\Users\hgkri\Downloads\yt-grab` (12 bhavam significations, Astro Classes 1–11, graph /
"tomorrow's graph" prediction, thithi/yogam/karnam/natchathiram, prasanam, weekly/monthly &
long-term investment prediction).

Pipeline to build it:
1. **Transcribe** each video (Tamil → English text). Use the provided `tools/transcribe.py`
   (delivered with this spec). **Run it locally**, not in a restricted sandbox — Whisper models
   download from HuggingFace/Azure, which locked-down cloud environments block (verified: 403).
   Use **Python 3.12** for this tool (faster-whisper has no 3.13/3.14 wheels). It writes
   `transcripts/<class>.en.txt` (English, timestamped; `--both` also emits Tamil). Keep them
   under `backend/knowledge/transcripts/`.
   Easy no-code alternative: the desktop apps **Buzz** or **Subtitle Edit** both run Whisper
   with a GUI and handle the model download.
2. **Codify** each rule the teacher states as a small pure function
   `rule(chart) -> Optional[Finding]`, where `chart` is the engine output. Group by topic
   (`rules/graph.py`, `rules/weekly.py`, `rules/longterm.py`, `rules/prasanam.py`).
3. `predict.run(chart)` collects the findings that fire and returns them as structured sections
   (`graph_prediction`, `weekly`, `monthly`, `long_term`). The engine (Layer A) never changes.

Rule finding schema (suggested):
```python
@dataclass
class Finding:
    section: str        # "graph" | "weekly" | "monthly" | "long_term" | "prasanam"
    title: str
    detail: str
    source: str         # e.g. "Astro Class 5 @ 12:40" for traceability
```
Keep a `source` on every rule so each prediction traces back to the exact lesson.

---

## 9. Build milestones (do them in order; stop for review after each)

1. **Scaffold** — repo structure (Section 3), backend venv on **Python 3.12**, install
   `fastapi uvicorn pyswisseph`, Vite React-TS app, dev proxy. `GET /api/health` → `{ok:true}`.
2. **Engine + tests** — implement Section 5 in `engine.py`/`panchang.py`/`names.py`; wire
   `POST /api/compute`; make all §5.7 fixtures pass (`pytest`).
3. **Frontend** — build the components (Section 7) against the running API; match the prototype.
4. **Polish** — input validation, error states, loading state, "copy chart as text" button.
5. **Layer B stub** — `predict.py` stub wired into the response + PredictionPanel.
6. **Layer B v1** — transcription pipeline (Section 8) + first real rules from Astro Class 2.

---

## 10. Run instructions (put in README.md)

Backend:
```
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn pyswisseph pytest
uvicorn app.main:app --reload --port 8000
```
Frontend:
```
cd frontend
npm install
npm run dev        # Vite serves http://localhost:5173, proxies /api → :8000
```

---

## 11. Notes & caveats

- **Ayanamsa** is Lahiri (South-Indian standard). If a different school is wanted later,
  it's one `set_sid_mode` change. Appendix B gives the validated linear Lahiri fallback
  (`23.85697 + ((jd-2451545)/365.25) * 0.0139552`) for the non-pyswisseph path.
- **Rahu** uses the *mean* node. True node (`swe.TRUE_NODE`) is a one-line switch if preferred.
- **Vaara** — civil-local now; sunrise-based is the accurate refinement (needs sunrise time
  via `swe.rise_trans`). Ship civil first.
- **Honesty for the market/investment features (important).** The graph / weekly / monthly /
  long-term modules are the *whole point* of this app, and they forecast real money markets.
  Astrology-based market prediction has **no demonstrated predictive edge** in evidence. Build
  and label every prediction as a study aid reflecting the GRAHA MARKETS teaching — not
  financial advice, not SEBI-registered, and never auto-wired to live orders. Put a persistent
  disclaimer in the UI's PredictionPanel. See Appendix C.

---

## Appendix A — reference prototype
`jothidam_prototype.html` (delivered with this spec): the full UI + a JavaScript port of the
Section 5 engine, validated to < 0.006° against the Swiss Ephemeris. Runs offline in any
browser. Use it as the design target and numeric oracle for the React build.

## Appendix B — no-compiler fallback (only if Python 3.12 is unavailable)
Swap `pyswisseph` for `astronomy-engine` (pure Python, `pip install astronomy-engine`,
no C compiler). Get tropical ecliptic longitudes, subtract the Lahiri value from Appendix A's
formula for sidereal; ascendant via the standard formula
`asc = atan2(cos(RAMC), -(sin(RAMC)cosε + tanφ sinε))` (no quadrant flip — verified against
all four fixtures); Rahu via the mean-node polynomial
`125.04452 − 1934.136261·T + 0.0020708·T² + T³/450000` (T in Julian centuries from J2000).
This is the exact logic proven in the prototype.

## Appendix C — Domain map: Financial Astrology (GRAHA MARKETS method)

> **Disclaimer — surface this in code and UI.** Source: YouTube channel **GRAHA MARKETS**
> (@GRAHAMARKETS), whose own about page states it is *"purely for educational purpose"* and
> *"not a SEBI registered advisor."* This app reproduces a teaching for study only. Astrology
> has no established power to predict financial markets; treat every output as an interpretive
> exercise, never as a signal to buy, sell, or size a real position. Keep a visible disclaimer
> in `PredictionPanel` and do not connect this to any broker/order system.

### C.1 What the app actually forecasts
The subject is the **Indian market** (Nifty 50, Bank Nifty), not a person's horoscope. So the
"chart" of interest is usually the sky **at a market moment** — an intraday session, a day, a
week, a month, or a query instant (prasanam) — rather than a birth chart. The engine (Layer A)
already computes everything the method reads from the sky; Layer B is the *interpretation* of
those numbers for markets.

Indian market session for intraday work: **09:15–15:30 IST**. Intraday "graph prediction"
typically tracks the **Moon** (fast mover) through rasis/nakshatras across the session, plus
the day's panchang and any aspects/ingresses that fall inside market hours.

### C.2 Curriculum → module map (from the downloaded classes)
Each class becomes a rules file under `backend/app/rules/`. Titles are confirmed; the *rules*
inside are TBD until transcription.

| Class (video) | Layer B module | What to extract |
|---|---|---|
| 12 BHAVAM EXPLANATION | `bhavam.py` | House (bhava) significations mapped to market/finance themes |
| ASTRO CLASS 2, 3 (Rahu/Ketu/Thithi) | `basics.py` | Core factors: Rahu/Ketu role, thithi meaning for markets |
| CLASS 4–9 (GRAPH PREDICTION, "tomorrow's graph") | `graph.py` | The intraday/next-day price-graph method (the core) |
| CLASS 7 (thithi/yogam/karnam/natchathiram) | `panchang_rules.py` | How each panchang element biases the day |
| WEEKLY AND MONTHLY PREDICTION | `weekly.py`, `monthly.py` | Swing-horizon rules |
| HOW TO PREDICT LONG TERM INVESTMENT p2, CLASS 11 | `longterm.py` | Investment-horizon rules |
| PRASANAM VIDEO 1, prasanam 2 | `prasanam.py` | Horary: chart cast at the moment a market question is asked |
| EXAMPLE CHART | (tests) | A worked example → turn into a regression fixture |

### C.3 Inputs the method draws on (all already produced by Layer A)
Sidereal graha longitudes + rasi, retrogrades, Rahu/Ketu, the lagna, and the full panchang
(vaara, thithi, natchathiram + pada, yogam, karanam). The likely extra computations Layer B
will need on top of the current engine:
- **Moon transit timeline across a session** — the rasi/nakshatra the Moon occupies at each
  point between 09:15 and 15:30 IST (sub-hour resolution). Add a helper that samples the Moon
  every N minutes.
- **Ingress / sign-change times** — when any graha changes rasi or nakshatra during the window.
- **Aspects (drishti)** and possibly **degree hits** if the teacher uses them.
Add these to the engine only when a transcribed rule actually requires them — don't pre-build.

### C.4 Rule module shape
```python
# rules/graph.py
def rules(ctx) -> list[Finding]:
    """ctx = engine output for the market moment + a Moon-transit timeline.
    Each entry the teacher states becomes one check here, with a `source`
    pointing back to the exact class + timestamp for traceability."""
    out = []
    # e.g. if ctx.moon_nakshatra in TEACHER_BULLISH_STARS: out.append(Finding(...))
    return out
```
`predict.run()` aggregates findings across modules into the response sections
(`graph_prediction`, `weekly`, `monthly`, `long_term`, `prasanam`). Every `Finding` keeps a
`source` string (e.g. `"Astro Class 5 @ 12:40"`) so a prediction can always be traced to the
lesson it came from — essential for a method you're still learning.

### C.5 General background (label as GENERAL, confirm against the course — do NOT ship as the
teacher's rules)
Public Vedic financial-astrology writing commonly associates broad market/finance themes with
certain factors (e.g. Moon & fast intraday sentiment; Rahu with speculation/volatility;
Jupiter with expansion; Saturn with contraction; the 2nd/11th houses with wealth/gains). This
is *orientation only*. The GRAHA MARKETS course has its own specific system, and where its
teaching differs, **the course wins**. Never let this general background masquerade as a
transcribed rule — tag any placeholder built from it as `source="GENERAL (unverified)"`.

### C.6 First transcription target
Start Layer B with **Astro Class 4 (“How to predict tomorrow graph”, Part 1)** and its
follow-ups (5–9), since the intraday graph method is the spine everything else hangs on. The
transcription pipeline is in Section 8.