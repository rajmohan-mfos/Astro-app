# Rule provenance — GRAHA MARKETS method

Every rule in `app/rules/` traces to one of these sources. Update this file
whenever a new transcript or document is codified.

## Sources

| Tag | Source | Status |
|---|---|---|
| [C5] | `transcripts/ASTRO CLASS-5 ( GRAPH PREDICTION 2).en.txt` | transcribed, codified |
| [W] | `transcripts/WEEKLY AND MONTHLY PREDICTION.en.txt` | codified (`rules/weekly.py`) |
| [NOTES] | `docs/கிரகங்கள்.docx` (planet/house tables) | codified |
| [S4] | `docs/GRAPH ASTRO-4.pptx` (Class 4 slides) | partially codified |
| [S5] | `docs/GRAPH PREDICTION -5.pptx` (weekly horai rules) | codified (`rules/horai.py`) |
| [P1] | `transcripts/PRASANAM VIDEO 1.en.txt` | codified (`rules/prasanam.py`) |
| [P2] | `transcripts/prasanam 2.en.txt` | reviewed — same 2/6/11 vs 5/8/12 judgment |
| [HC] | `docs/HALF COURSE.docx` | mostly images; text headers only |
| [C4] | `transcripts/ASTRO CLASS -4 … PART 1.en.txt` | codified into `rules/graph.py` |
| [C11] | `transcripts/LONG TERM PREDICTION … CLASS - 11.en.txt` | codified (`rules/longterm.py`) |
| [LT2] | `transcripts/HOW TO PREDICT LONG TERM INVESTMENT PART - 2.en.txt` | prasanam judgment table extracted; full prasanam module pending |

## Core tables ([NOTES], verbatim)

- Planets: BULLISH = Jupiter, Rahu · BEARISH = Mars, Saturn ·
  SIDEWAYS = Venus, Sun, Moon, Mercury, Ketu · RETRO (வக்கிரம்) → bearish
- House counts from Moon (inclusive): உபஜெய 1,3,6,10,11 = bullish ·
  அபஜெய 5,8,12 = bearish · 4,7 = sideways · கோணம் 2,9 = angle
- Key planets: Moon → intraday · Sun → monthly · Jupiter → yearly

## Intraday method ([C5], codified in `rules/graph.py`)

X = Moon's nakshatra lord; Y = X's nakshatra lord ("star's star");
X1/Y1 = another graha occupying X's/Y's nakshatras; X1 overrides X, Y1
overrides Y ("when x1 comes … forget xy", C5 @ 03:57). House count from
Moon's rasi → bias table above. X-side = first half 09:15–12:00, Y-side =
second half 12:00–15:30. Conflict: bearish planet at bullish count →
sideways (C5 @ 10:55, Saturn at 10). Angle count → that half runs opposite
to the other; enter only after 12:00 on angle days (C5 @ 13:11).

## Weekly / monthly method ([W], codified in `rules/weekly.py`)

Anchor = SUN. Window = the Sun-nakshatra period ("take the month when the
stars change", ~13.5 days), split into halves at its midpoint: X-side rules
the first half, Y-side the second. Chain identical to intraday (X = Sun's
star lord, Y = X's star lord, X1/Y1 override) but house counts are
DEGREE-based — 30° spans from the Sun's exact degree (W @ 02:38, 07:41).
Same bias table. Monthly = successive windows. Always confirm with
prasanam before acting (W @ 06:44). Teacher's worked example: Mars at
degree-house 12 → first half down; Venus at 2 (angle) → second half up.

## Class 4 confirmations (codified)

- X = Moon's star lord, Y = X's star lord — confirmed by the "12 sun and
  12 sun" worked example (C4 @ 04:30–07:30).
- Counting is DEGREE-based (C4 @ 05:23 degree check + slide "MOON 29* TO
  NEXT 29* - 1 HOUSE"); `rules/graph.py` switched from whole-sign counts.
- X=Y same planet & count → full-day bias (C4 @ 21:52).
- Sideways planet on a bearish count → grinding "every rise a selling
  opportunity" drift, not a hard fall (C4 @ 07:54); bearish planet there
  means a hard move (C4 @ 13:43).
- Pre-trade checklist: own-rasi Moon transit not in 5/8/12 → prasanam →
  entry (C4 @ 19:03).

## Long-term method ([C11] + [LT2], codified in `rules/longterm.py`)

Anchor = JUPITER. Window = Jupiter-nakshatra period (found by daily
sampling — the teacher's July 2021 example is a RETROGRADE ingress into
Dhanishta, ~5.3 months to the direct exit). Chain and degree-counts from
Jupiter; X-side = first half, Y-side = second half, deeper chain splits
the second half further (Venus 8 → Moon 3 example). Prasanam judgment
numbers from LT2: 2/6/11 profit (6 median, 11 heavy), 5/12 median loss,
8 heavy loss.

## Prasanam ([P1]+[P2]+[LT2], codified in `rules/prasanam.py`)

KP horary, cast at the question moment (teacher uses AstroSage "KP Murai",
old KP method; 1–249 seed variant pending a UI input). Question planet =
lagna's SUB lord; answer planet = its position's nakshatra lord. Houses
(whole-sign from KP lagna): 2/6/11 profit (6 median, 11 heavy), 5/12
median loss, 8 heavy loss. Answer planet's house carries the verdict.

## Horai golden rules ([S5], codified in `rules/horai.py`)

Equal one-hour horai from sunrise (swe.rise_trans), Chaldean sequence from
the weekday lord — standard Tamil convention, CONFIRM against Class 7.
Mon: Mercury horai UP, Venus horai unexpected · Tue: Saturn horai DOWN
(stronger with Uthiradam) · Wed: Venus horai UP (75%/100%) · Thu: Sun
horai + Karthigai → BankNifty up; Visagam day positive · Fri: Mercury
horai UP · Open in Saturn horai → recovery after (~30 Nifty / 80+ BN).

## Classes 6/8/9 (codified increments)

- [C6 @ 09:21] third confirmation of degree-counting ("14 degree to 14
  degree … 10, because only one degree is different").
- [C6 @ 13:16] bearish planet at bullish count = "upside-ways" — first
  push up, then capped (refines the C5 conflict-sideways).
- [C8 @ 02:02] thithi biases → `rules/panchang_rules.py`: Jaya positive,
  Rikta very negative, Pournami positive, Amavasai negative, else neutral;
  [C9 @ 01:35] Shashti positive.
- [C8 @ 05:20–08:37] horai magnitudes folded into `rules/horai.py`
  (Monday Mercury ~100 Nifty pts; Tuesday Saturn 40–50/70–80 with the
  fails-to-fall inverse signal; Venus horai = no-trade reversal window).
- [C8 @ 02:42] karanam/yogam positive-negative lists live in a PDF the
  teacher WhatsApps — transcript too garbled to codify. **Get the PDF into
  docs/ if available.**
- [C6 @ 06:05] session halves generalize: commodities and forex split
  their own sessions in half (not implemented; Indian equities only).

## MASTER-RULES.md (user-verified, authoritative — 2026-08-10)

The user's scenario document adjudicated the transcript ambiguities; the
bias matrix in `rules/graph.py` is calibrated to reproduce all five
scenarios exactly (tests/test_scenarios.py):
- Bearish planet (Mars/Saturn/retro) on a bullish count → BEARISH — the
  planet dominates [S3], overriding my earlier C5 "sideways" reading.
- House 8 (heavy loss) → bearish regardless of planet [S1 Venus(8)].
- Houses 5/12 (median loss) with a non-bearish planet → sideways-down.
- Jupiter is BULLISH (scenarios override the master list's sideways line);
  Rahu is bullish but its permanent retro softens it to sideways-up [S2].
- Angle stretches resolve OPPOSITE to the neighbour's HOUSE direction, and
  the neighbour flips to its house direction when paired [S4b, S1].
- Class 10: multiple occupants of X's stars (x1, x2 …) split the half into
  EQUAL time windows (09:15–10:37 / 10:38–12:00) [S1].
- X never counts as a Y-occupant (it defines Y) [S1].

## Class 7 (codified)

- Day-lord rule [C7 @ 06:16–08:47]: the weekday lord appearing as BARE
  X or Y → that half bullish ("bullish at any time", "heavy rally");
  never applies to X1/Y1 overrides. In `rules/graph.py`.
- Karanam [C7 @ 11:25]: seven movable positive, four fixed negative —
  in `rules/panchang_rules.py`.
- Nanda thithis (1/6/11) positive [C7 @ 09:18]; Rikta "heavy fall"
  reconfirmed. Yogam list still pending the teacher's PDF.
- Fourth confirmation of degree-counting (29°→29° = 1 house) and of the
  star-lord qualities (Jupiter = current situation, Corona example).
- Angle-deadlock tolerance: an all-angle day is unresolvable, so counts
  within 0.35° of the next house may be nudged across to break the
  deadlock (the teacher's 25/05/2021 Saturn(10) vs our 269.74° arc).

## Example Chart video ([EX], cross-checked 2026-08-10)

The teacher's full 07/01/2022 walkthrough matches our engine exactly:
X=Jupiter(12), Y=Rahu(3), no X1/Y1 ("Jupiter's [occupant] is not there,
we can leave it"), first half down / second half "sideways up" ("3 is
sideways and rahu is bullish"), degree counting "from 21 degree to 21
degree". New extractions: Vyatipata yogam = very negative ("disease…
very dangerous") → `NEGATIVE_YOGAS`; horai are PROPORTIONAL twelfths of
daylight/night (his Saturn horai 09:24–10:29 ≈ proportional 09:29–10:26,
not equal-hour 09:37–10:37) → `transit.horai_timeline` updated; "XOI"
(OI confirmation) checks run 5–10 minutes past the horai boundary.

## Classes 2/3/10 + 12-Bhavam (final sweep)

- [C10 @ 04:44–08:53] validates the x1/x2 half-splitting and angle
  resolution FROM THE SOURCE (Mercury x1(9) angle → opposite of Venus
  x2(8) bearish; Jupiter Y bullish; "divide the first half into 2
  divisions") — previously implemented from the user's S1 scenario.
- [C3 @ 02:03–03:47] Moon transiting over Rahu/Ketu → avoid/caution →
  `rules/basics.py`.
- 12-Bhavam transcript is heavily garbled; usable significations kept as
  a reference table in `rules/bhavam.py` ("2,6,11 is profit" @ 00:23).

## Nifty-50 stock mapping (RESOLVED — GRAPH ASTRO-4.pptx slide 1)

The "NIFTY 50 STOCKS AND THEIR PLANETS" table (an image on slide 1) is
codified in `rules/stocks.py` — all 50 rows, cross-validated against the
videos (C4 Reliance=Sun & Cipla=Rahu+Sun rejected as mixed; C6 Coal
India=Saturn; C11 Grasim=Venus+Moon, ITC/Titan=Venus). Predictions now
list pure-planet stocks for each half's chain planet; the teacher avoids
mixed-planet stocks for clean signals [C4 @ 15:26–16:32]. Note: a few
rows use Neptune/Uranus (outside the nine grahas) — they only affect
purity, never a signal.

## Course guide cross-check (Financial_Astrology_Course_Complete_Guide.md)

Applied: full yogam lists (neg Vaidhriti/Vyatipata/Vishkambha, pos
Shubha/Ayushman/Saubhagya) §3C; Bhadra thithis (2/7/12) positive §3B;
prasanam Rahu/Ketu sub-lord → CANCEL §2.3; prasanam Moon validation
(house must touch 2/6/11 or 5/8/12, else INVALID) §7.2; can-trade now
also counts from the birth LAGNA and flags transit Moon over NATAL
Rahu/Ketu §2.1–2.2. Rejected (contradicts validated video examples):
"Y = star lord of the Sun" §5 (ours: star lord of X's position, proven
by 05/05 & 07/01 charts); Saturn(10) "slanted upside" §5 (user's S3
adjudication: bearish, planet dominates — flip only on user's call).

## Buzz transcripts validation ("transcripts from buzz/", higher quality)

C6-Buzz settles the Saturn(10) dispute with the teacher's own words:
"upside-wise market — up move only, like a slight slope, capped by the
bearish planet; second half sideways." Bias rule flipped: bearish planet
on a bullish count → SIDEWAYS-BULLISH (upside-wise), overriding the S3
memo's "bearish" and agreeing with guide §5 "slanted upside". C6-Buzz
also re-confirms X=Saturn(10)/Y=Sun(10) degree-counting for 19/01/2021.
Remaining Buzz files not yet deep-compared — future sweep may refine
garbled segments further (12-Bhavam especially).

## Full Buzz sweep (three-agent audit, all 15 remaining files)

APPLIED: thithi groups per C7-Buzz (only Jaya positive / Rikta negative
with 1000–2000pt magnitude / others neutral; 5 & 6 positive from worked
examples); prasanam Moon-in-5/8/12 → do-not-cast [P2]; prasanam validity
gate moved to the QUESTION planet [LT2]; re-ask 2–3h; basics.py retired
(C3's node rule is about NATAL nodes — lives in /api/can-trade, now
source-stated); MASTER-RULES S4b second half = sideways-up (angle-partner
house-flip demoted to unsourced); Jupiter-bullish now source-stated [C2].

DEFERRED TODO (each sourced in the agent reports):
1. Prasanam significator SETS (occupied+owned+star-lord houses) with
   any-5/8/12-contaminates rule; house 3 = delayed profit; 1/4/10 =
   satisfaction axis; seed 1–249 as primary input; sub-vs-star ordering
   caveat; Rahu/Ketu-cancel now conditional (P1 counter-evidence).
2. Horai: 45-min/half-window action rule (C8/C9/C10); Saturn horai as
   general reversal (C9); divergence rule as standalone (trade Nifty on
   divergence); Uthiradam tier magnitudes 100/300–400; "minimum" framing;
   Venus-unexpected not Monday-only (C9); negative-yogam suppresses the
   Friday Mercury rule with precedence panchang→chain→horai [EX].
3. longterm.py: split the second half across y-occupants equally (Class
   10 co-occupant rule, [C11] 1.5+1.5 months); state the 3/6-month probe.
4. weekly.py: emit stock findings for the window.
5. stocks.py: add the SECTORS dict [C2]; bhavam.py: houses 3 & 9, house
   7 "not used", stock-exchange/gambling in 5, dual 6th, sudden gains in
   11 — Buzz 12-Bhavam is clean, "garbled" tags stale.
6. Gap up/down via prasanam; 30/60 confluence minimum [C10]; forex/
   crypto/stocks scope; Dow ~70% claim; second-half split symmetry and
   day-lord-vs-house-8 ordering remain open questions.
7. [EX-Buzz] horai figures correction: Saturn horai 09:24–10:21 (57 min —
   strengthens proportional model); cast-time heading downgraded to
   "resolved by inference" (source only ever says 05:30).

## FULL-guide audit fixes (applied)

- prasanam `judge()`: poison rule — a 2/6/11 answer is now spoiled by a
  5/8/12 question house (previously returned YES). Real wrong verdict.
- yogam lists completed: +Vyaghata (negative), +Shobhana (positive).
- stock purity now counts only the nine grahas, so Asian Paints
  (Mars+Neptune), UPL and Tata Steel are no longer filtered out — Asian
  Paints is the teacher's flagship long-term Mars trade.
- explicit Rahu/Ketu corruption warning in the stock finding.
- removed the unreachable angle-partner house-flip branch (unsourced).
- STAR_QUALITY["Sun"] filled from guide §2 (was a placeholder shown to
  users); bhavam houses 3 & 9 added, 5/6/7/11 enriched, house 7 marked
  "not used for market judgment".
- stale docs corrected: MASTER-RULES S3 (engine returns sideways-bullish),
  predict.py module list, longterm.py "mapping pending" text.

STILL OPEN from that audit: generic per-horai effect table (Sun/Saturn/
Mars/Mercury/Venus/Jupiter, day-independent — biggest functional gap);
Sun-horai-at-open recovery; Thursday Jupiter-day rule; aggregate day
score with panchang→chain→horai precedence; weekly/longterm co-occupant
splitting and weekly stock findings; prasanam whole-sign vs KP Placidus
house frame mismatch; day-lord outranking house 8 / angle.

## Course thithi/yogam sheets (user-supplied images, 2026-08-10) — CLOSES
## the long-standing "yogam PDF pending" item

- **Complete 27-yoga classification** now codified from the OPTIONS MERSAL
  yogam sheet: 16 சுபம் (auspicious), 8 அசுபம் (inauspicious), 3 அதித
  அசுபம் (extremely inauspicious: Vyaghata, Vyatipata, Vaidhriti).
  NOTE: this system marks Dhriti, Dhruva and **Siddhi** inauspicious,
  contrary to classical convention — the sheet governs.
- **Thithi families** applied per the sheet with its own glosses (Nanda =
  joy; Bhadra = suitable to begin actions; Jaya = conquer enemies; Rikta =
  obstacles and sorrow; Purna = complete all matters). User adjudicated in
  favour of the guide/sheet reading over C7-Buzz's "others all neutral".
- **NEW பகூச்சித்திரை (Paksha Chidra)**: thithis 4/6/8/12/14 in EITHER
  paksha are defective — emitted as a reduced-conviction flag that
  overlays (does not replace) the family bias.
- **NEW தக்க யோகத் திதிகள்**: auspicious thithi+weekday pairs —
  Dwadasi/Sun, Ekadasi/Mon, Panchami/Tue, Dwitiyai/Wed, Shashti/Thu,
  Ashtami/Fri, Navami/Sat.
- **Prasanam derivation**: user confirmed keeping the transcript reading
  (question = lagna's upa-nakshatra/sub lord; answer = its star lord) over
  the FULL guide's "Moon's star lord" phrasing.

## Kaala Purusha Chakram sheets (user-supplied, 2026-08-10)

- **All 27 star-lords VALIDATED against the course's own chart.** The
  sheet prints each lord's three nakshatras; a test now asserts the
  engine's Vimshottari derivation reproduces the printed table exactly
  (tests/test_rules.py::test_nakshatra_lords_match_course_chart). Every
  star-lord the app reports — intraday X/Y, weekly, long-term, prasanam —
  rests on this mapping, so it is now source-verified end to end.
- **No finer nakshatra grade exists.** The sheets classify stars only by
  lord, confirming that lord-quality scoring IS the method — there is no
  per-star market grade left to codify.
- Reference data captured in `rules/reference.py`: rasi attributes (lord,
  movable/fixed/dual, element, direction, gender), Deva/Asura teams,
  benefic/malefic groups, male/female/neuter planets.
- **Deliberately NOT wired into the bias engine** (spec Appendix C.5 —
  background must not masquerade as a transcribed rule): "Mercury takes
  the nature of the planet it joins" and "waxing Moon benefic / waning
  Moon malefic". Both are classical framework printed on the sheet; no
  class applies either to a graph call, and the market planet list
  (கிரகங்கள்.docx) fixes Mercury and the Moon as sideways planets for
  trading. Candidate refinements only — flagged here, not applied.

## Prasanam question planet — RESOLVED (user, 2026-08-11): the MOON

The transcripts genuinely disagree with each other:
- **P1**: "Lakhna Upanachathram is the Savai" — question = the LAGNA's
  sub-lord.
- **LT2**: "The moon is the question. You should take the moon… the star
  in the moon is the question… First, the moon is a question, the Buddha
  is an answer" — question = the MOON's star lord, and he works the whole
  Reliance-4000 example that way.

User adjudicated in favour of the **Moon** reading. `prasanam_chain` now
returns question = Moon's nakshatra lord, answer = that planet's star
lord, and still exposes `lagna_sub_lord`. The Rahu/Ketu CANCEL rule was
moved onto `lagna_sub_lord`, because [C3] ties it specifically to
"Lakhanam's Upanachathram", not to the question planet. Validation
(2/6/11 or 5/8/12) stays on the question planet, which under the Moon
reading is what LT2 means by "in the question of the moon… there should
be a connection".

Also applied from LT2: house 2 regraded "median profit" ("2, 6 is the
medium profit"); the three-rules-for-a-valid-question finding; re-ask
etiquette (2–3 h same question, 1–2 weeks same stock, ladder the target
down on a NO) and the ~5-year prasanam horizon vs ~1 year for the
Jupiter graph method. Still deferred: 3+11 = profit-with-delay, which
needs KP significator sets rather than one house per planet.

## Weekly video cross-check (2026-08-11) — two discrepancies, NOT changed

His February window matches ours (Sun in Dhanishta/Mars, ~7→19 Feb, next
lord Rahu, chain X=Mars Y=Venus, split into halves, stocks of the half's
planet, prasanam mandatory). Two numbers do not, and in both cases the
sources contradict each other, so the engine was left alone:

1. **Mars 12 vs our 11.** Sun 294.17°, Mars 255.77° → arc 321.6°, i.e.
   21.6° INTO degree-house 11 — not a boundary case. Whole-sign counting
   gives exactly his 12. So in this video he used a whole-sign count for
   X while preaching degree counting in the same breath. C4/C6/C7/C10 and
   the guide all insist on degree counting (C6 explicitly corrects 11→10
   by degree), so degree counting stands.

2. **Venus as Y1 by self-occupancy.** He says "Venus is in Venus, so Y1
   is there" and counts Venus→Sun = 2 (our reverse count is 35.79° →
   house 2, an exact match), making the second half an ANGLE and giving
   his "1st down, 2nd up". Our `occupants_of_stars` excludes the lord
   itself, so we read a bare Y=Venus forward at 11.
   **Why not changed:** C11 has the identical structure — "X is Mars,
   again it is in Mars" — yet counts Mars FORWARD at 6, which our engine
   reproduces exactly along with his stocks and outcomes. Treating
   self-occupancy as X1/Y1 would fix Weekly and break the fully verified
   C11 example. The two videos are inconsistent; C11 is the better-
   evidenced example, so it wins. Revisit if a third source settles it.

## 5/8/12 counted from BOTH rasi and lagna — confirmed 2026-08-11

[C4] is the only place the reference is stated explicitly, and it names
both: "Where is the moon for your **Ras and Lakkana**? If it is in 5, 8,
12, then definitely… you will do something wrong." Elsewhere he is looser
("for your Ras…", "in your birth chart"); nothing says lagna-only. Guide
§2.1 agrees. `/api/can-trade` therefore counts from both and flags AVOID
if EITHER lands in 5/8/12, returning `count` and `lagna_count` separately.
Materiality check over 60 days for a sample kundali: 4 days flagged by
both, 12 rasi-only, **9 lagna-only** — i.e. a rasi-only implementation
would silently miss a quarter of the blocked days.

## Prasanam significator SETS (implemented 2026-08-11)

[P1] reads houses as sets — "the star is the question, 4, 9, 10, 11 are
there; Rahu is here, 4, 10, 12 are there" — not one house per planet.
`prasanam_chain` now returns `question_houses`/`answer_houses`/
`moon_houses` using the KP four-fold rule: houses the planet OCCUPIES and
OWNS, plus those its STAR LORD occupies and owns; Rahu/Ketu own no rasi
so they borrow their sign lord's. Whole-sign houses, so ownership maps
1:1 onto houses.

This makes three previously-undeliverable rules work, all sourced from
[P2]: the poison rule can now see a 5/8/12 hiding among an otherwise
profitable answer ("even one drop… it is poison"); 3+11 = profit but
delayed ("you will buy it, you will cut it, in the end it will go up");
and the 1/4/10 satisfaction axis. P1's own example — question 4/9/10/11,
answer 4/10/12 — is a regression test and returns NO on the 12, matching
his "it will be a joke" and the market falling.

RESOLVED 2026-08-11 — house frame is now PLACIDUS. KP is cusp-based by
definition and the teacher's "KP Murai / old method" computes Placidus,
so the prasanam side moved, not the sheet. Occupancy uses cusp
containment; ownership uses the canonical KP rule (a planet owns the
house whose CUSP falls in a rasi it rules), so a sign may hold two cusps
or none — interception, not a bug. Verified: 28/28 planet-house pairs
match the planet-position sheet across 14 dates.

This changes verdicts, not just display: 07/01/2022's question planet
went from [1,2,4,9,11] to [1,2,3,4,9,11] — house 3 appears because its
cusp falls in a Jupiter-ruled sign — so with 11 present the chart now
reads profit-but-DELAYED rather than plain profit. Verdicts computed
before this commit are not comparable with those after it.

`judge(int, int)` is retained and still passes its cases.

## Open questions / pending

0. **RESOLVED — cast time & occupant counting.** The chain chart is cast
   at SUNRISE (panchang day start). The user first said 05:30 (the
   teacher's phrase, Class 4 @ 03:52 "panchangam from morning 5.30"), but
   the Example Chart scenario (07/01/2022, x=Jupiter(12)) requires the
   Moon past 320° — crossed ~06:20, sunrise 06:37 — while S4b
   (25/05/2021) requires it still under 200° — crossed ~07:20, sunrise
   05:46. Sunrise is the unique convention satisfying every verified
   scenario; a fixed 05:30 or 09:00 each fail one. Count convention:
   X/Y from the Moon to the planet; X1/Y1 from the planet BACK to the
   Moon (C5 @ 04:51). Remaining boundary case: S4b's Saturn 0.4° shy of
   house 10 (accepted 9 or 10 in tests).

1. **[C4] X/Y exact derivation + day-lord rule** — slides say "X OR Y (DAY
   LORD RULE), X1 & Y1 (NO DAY LORD RULE)"; the rule itself is in the
   Class 4 video (transcription queued). Until then the chain derivation in
   `rules/graph.py` is inferred from C5's worked examples.
2. **Conflict mirror** — bullish planet at bearish count → sideways is an
   UNVERIFIED inference (only the bearish-at-bullish case is stated).
3. **[S5] horai rules** — need planetary-hour computation (sunrise via
   `swe.rise_trans`); then codify the Monday–Friday golden rules.
4. **Intraday count basis** — `rules/graph.py` counts whole signs, but the
   Class 4 slide says "MOON 29* TO NEXT 29* - 1 HOUSE" and the weekly video
   insists on degree-based counting for the Sun. The intraday count may
   also be degree-based — check against the Class 4 transcript when it
   lands and against the EXAMPLE CHART video.
5. **Vakya vs drik** — the author's printed பஞ்ச அங்கங்கள் end times
   (05/05/2021) disagree with their own KP Moon table; our engine follows
   the drik/KP computation (see tests/test_transit.py docstring).
