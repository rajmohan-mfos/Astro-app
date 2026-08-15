# Gann Trading Course
*Built from the W D Gann Trader (@Bjybnf) YouTube series — transcripts extracted, cleaned, and annotated. Companion references: `Bjybnf_Gann_Concepts_Summary.md` (concept archive) and `Bjybnf_Gann_Aspect_Master_Table.xlsx` (master table + backtests). Educational material, not investment advice.*

**Lesson index**
1. Gann Angles and the Gann Fan ✅
2. Three Gann Fan Strategies (breakout entry/exit, + trendline, + Fibonacci) ✅
3. Gann Square of 9 — construction, the angle math, GannZilla Pro, S/R levels ✅
4. Cosmogram in GannZilla Pro — setup and his aspect-meaning scheme (part 1) ✅
5. Jupiter–Uranus Conjunction & Opposition — the rare-event reversal thesis (graded) ✅
6. Radix–Transit Mercury–Mars Conjunctions — the deflection window, quantified ✅
7. Venus–Saturn Quadrature (transit) — the 150–300 point reversal rule, fully tested ✅
8. Venus–natalVenus Sextile — the "85% win rate" birth-chart rule, tested ✅
9. Retrograde Momentum — stations as reversal dates, and the planet-selection method ✅
10. Venus–Jupiter Quadrature — the only rule with a complete trade plan (target + SL), tested ✅
11. The Three-Planet Pattern (Sun ⚻ Uranus/Neptune + Uranus ⚹ Neptune) — and the calendar trap ✅
12. Mercury–Saturn Conjunction — and the "three worked, so the fourth will" fallacy ✅
13. Jupiter–natalJupiter Opposition — the once-a-decade bullish claim (live call graded) ✅
14. Modified Square of 9 — the increment formula for high-priced instruments ✅
15. **Scaling the Gann Fan properly** — the best technical content in the series ✅
16. Solar Dates & Time Cycles (X threads) — the seasonal framework ✅
17. *(pending — Cosmogram part 2: the conjunction/trine/square strategies; chronometer/time methods; shapes)*

---

## Lesson 1 — Gann Angles and the Gann Fan

### 1.1 What Gann theory is (as the channel frames it)
A theory built on "natural geometric shapes and ancient mathematics": price patterns and angles are used to project future movement. The channel claims ~90% accuracy for the method — treat that as the channel's claim, not an established fact (see §1.7).

### 1.2 The nine Gann angles
Gann angles are trend lines drawn at fixed price-to-time slopes that act as support and resistance. The classic set of nine, as taught in the video:

| Ratio (time × price) | Conventional Gann degrees | True arctangent | Steepness |
|---|---|---|---|
| 1 × 8 | 82.5° | 82.87° | Steepest |
| 1 × 4 | 75° | 75.96° | |
| 1 × 3 | 71.25° | 71.57° | |
| 1 × 2 | 63.75° | 63.43° | |
| **1 × 1** | **45°** | **45°** | **The master line** |
| 2 × 1 | 26.25° | 26.57° | |
| 3 × 1 | 18.75° | 18.43° | |
| 4 × 1 | 15° | 14.04° | |
| 8 × 1 | 7.5° | 7.13° | Shallowest |

The conventional degree values are the traditional Gann-literature numbers; the true arctangents differ slightly. Nothing in the method changes either way — the ratios are what matter.

### 1.3 The math behind 1 × 1
On a chart, **time runs on the X-axis and price on the Y-axis** (the transcript states this backwards — corrected here). The angle of a line is:

> tan θ = price units ÷ time units

So 1 × 1 (one price unit per one time unit) gives tan θ = 1 → **45°**. A line rising 2 price units per time unit gives tan θ = 2 → ≈63°, and so on for the rest of the set.

### 1.4 The critical caveat the video skips: chart scale
A "45° line" is only meaningful once you fix **how much price equals one bar of time** on your chart. Zoom in or out, and the same line changes its visual angle while the price/time *ratio* stays constant. Gann himself worked on fixed-scale paper charts (e.g., 1 point per day). In modern software, always anchor the fan by the **ratio** (the tool handles this), never by eyeballing degrees — otherwise two traders with different zoom levels get different "angles" from identical data.

### 1.5 How to draw the Gann Fan (his TradingView method)
1. Identify the **major swing high** and **major swing low** on the chart (his example: high 12,450, low 7,505).
2. Draw a horizontal line at each.
3. From the swing low, draw a **vertical line**.
4. Using the trend-angle tool, draw a **45° line** from the intersection point.
5. Insert the **Gann Fan** tool (under Gann & Fibonacci tools) at the intersection, and rotate/scale it so the fan's **1/1 line overlays your 45° line**. All nine angles now radiate from the anchor.

### 1.6 Trading rules (as taught)
- **Bull/bear filter:** price **above the 1×1** line = bull market; **below the 1×1** = bear market.
- **Support/resistance ladder:** the fan lines above the 1×1 act as resistance; the lines below it act as support.
- **Angle-to-angle principle:** when one angle breaks, expect price to travel to — and consolidate at — the **next** angle.
- **His worked example:** after breaking the 1×1, the market rallied ~800 points and consolidated at the next line; after breaking that resistance, another ~400-point rally to the following line. Each fan line served as the staging post for the next move.

### 1.7 Notes & corrections (course annotations)
- **Notation clash:** the video's spoken words say "first number = price," but its own degree table only works if the first number is **time** (1×8 steep → 8×1 shallow). Note that TradingView's fan labels use the *opposite* order (its steep lines above 1/1 are labeled 2/1, 3/1, 4/1, 8/1). Don't memorize labels — anchor on the ratio and steepness.
- **Axis slip:** transcript says price on X, time on Y; standard charting (and the tan θ math) is the reverse. Corrected in §1.3.
- **The 90%-accuracy claim** is asserted, not demonstrated. Fixed-degree angle claims are untestable without a declared price/time scale, and the channel's testable claims that we *could* verify (aspect calls, the Venus–Saturn quadrature strategy) performed at market base rates — see the Backtest sheet in the companion Excel. Use the fan as a structured way to read trend and levels, not as a probability statement.

---

## Lesson 2 — Three Gann Fan Strategies
*Source video: "A 100% profitable trading strategy using Gann Fan and Fibonacci." Prerequisite: Lesson 1 (drawing the fan).*

### 2.1 Strategy 1 — Gann Fan breakout system (entry, stop, trail)
The complete mechanical sequence, on Nifty daily (he notes smaller timeframes also work):

**Entry (fan anchored at the significant HIGH):**
1. Mark the significant high and significant low of the move.
2. At the significant **high**, draw the 45° anchor line (at a high this line slopes *downward* to the right — see §2.4) and overlay the Gann Fan so 1/1 sits on it.
3. Wait for price to break **up through the 1/1 line**.
4. Entry triggers only when the **next fan line (labeled 2/1) also breaks** — the 1/1 break alone is not an entry.

**Stop loss (a second fan, anchored at the significant LOW):**
5. Draw a fresh 45° anchor + fan at the significant **low**.
6. Initial SL sits **below that fan's 2/1 line** — and only a candle **closing** below it triggers the exit, not an intraday poke.
7. If the gap to that 2/1 line is too small to be a meaningful stop, place the SL below the **significant low point** instead.

**Trailing:**
8. Once a candle breaks above the **significant-high horizontal line**, trail the stop to **3–5% below that line**.

### 2.2 Strategy 2 — Gann Fan + Trendline confluence
Add a classic trendline (minimum three touch points). Wherever the trendline **intersects a fan angle**, that point acts as strong support/resistance. His example: after a breakout, price returned to retest exactly the trendline-×-fan intersection and resumed the rally — the confluence zone held as support.

### 2.3 Strategy 3 — Gann Fan + Fibonacci confluence
1. Draw the Fibonacci retracement from the significant **high to low**.
2. Draw the Gann Fan at the significant **low**.
3. The intersection of the **61.8% retracement** with the **1/1 fan line** marks a strong support zone — his "buy more from this area" level. He notes this variant is most useful for **sector analysis**.

### 2.4 Notes & corrections (course annotations)
- **"100% profitable" is a title, not a statistic.** The video demonstrates only winning examples; no losing trade is shown, and no sample is counted. A breakout-plus-trailing system's results live in its loss distribution, which is exactly what isn't displayed.
- **At a high, the anchor is minus 45°.** The transcript says "draw a 45° line at the significant high"; practically, the trend-angle at a high slopes down-right (−45°) and the fan opens downward. At a low it's +45° opening upward. TradingView's label caveat from Lesson 1 (§1.7) applies to which line reads "2/1."
- **The system is heavily anchor-dependent.** His own phrasing — "we can take *any* significant high and *any* significant low" — means two traders on the same chart can legitimately pick different anchors and get different entries, stops, and trails. Combined with the discretionary SL adjustment (fan 2/1 vs. the swing low) in §2.1 step 7, the strategy's outcomes are as much about anchor selection as about the fan itself. When you test or trade it, fix your anchor rules in advance (e.g., highest high / lowest low of the visible trend) so the method is reproducible.
- **Untested here:** unlike the aspect calls, this system has too many free parameters (anchor choice, timeframe, SL variant, trail %) to backtest as a single rule; any honest test would first require freezing those choices.

---

## Lesson 3 — Gann Square of 9: Construction, Angle Math, and Support/Resistance
*Source video: "Gann Square of 9 | The only true method that will change the way you do trading." Tool: GannZilla Pro (free).*

### 3.1 Building the square
Draw a 9×9 grid. Place **1 at the center** and spiral **clockwise**, incrementing by 1, out to **81**. Each cell is treated as a "point of vibration." The perfect squares are structurally significant — odd squares (1, 9, 25, 49, 81) and even squares (4, 16, 36, 64) fall along opposing diagonals of the spiral.

### 3.2 The angle math (the engine of the whole method)
Wrap a circle around the square; the key rays are **0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°, 360°**. Moving a price "around the square" by an angle uses:

> **next level = ( √price + n × 0.25 )²**  where n = 1 per 45° step (n=2 for 90°, 3 for 135°, 4 for 180° …).

His worked examples from 49 (√49 = 7): 45° → (7.25)² = 52.56 → he takes **53**; 135° → (7.75)² = 60.06 → he takes **61**. A full 360° rotation is (√price + 2)², which completes one "cycle" — cycle completions are treated as major reversal zones.

**Derived insight (course addition):** one 45° step spaces levels roughly **√price ÷ 2** apart. At Nifty 24,000 that's ~78 points per 45° level (~155 per 90°); on an ₹800 stock it's ~14. Level spacing grows with the square root of price — worth knowing before judging how "often" price respects them (see §3.7).

### 3.3 GannZilla Pro — tool map
- **Layout:** clockwise spiral; **Size** adds rows/columns; **View** = Square of Nine; **Data type** = price.
- **Price (start value):** default 1; for high-priced instruments set the start near the significant low (e.g., Nifty spiral started at **15,178** with the 18,900 top as context) to keep the square compact.
- **Find** locates any number; **Increment** changes the step between cells (e.g., 5 → 9, 14, 19, 24…); right-click highlights a cell.
- **Protractor:** overlays the degree circle; its marker measures the angle between any two numbers (his demo: 1 ↔ 92 = 52°).
- **Chronometer:** time-of-year ring (annual or daily; session time 09:15–15:30 for India) — deferred to the next video.
- **Cosmogram:** the astrology layer (set **geocentric**, city Mumbai) — deferred.
- **Shapes** (triangle/square/pentagon/hexagon overlays) — deferred.

### 3.4 Manual support/resistance method
1. Find the **significant high or low** (his example: KPIT Tech high **801**).
2. **Find + highlight** that number on the spiral.
3. Open the **vector** tool; keep only the 45°-family rays (45/90/135/180/225/270/315).
4. **Rotate the vector so one ray passes through your number** — the spiral cells the rays now intersect are the levels.
5. Reading **clockwise** from the anchor gives **resistance** (his: 816, 829, 845…); **anticlockwise** gives **support** (789, 773, 760, 745, 733, 718…).
6. **Too many levels?** Drop the 45° rays and keep only the two 90° lines.
7. Plot the levels as horizontals on the chart and drop to a lower timeframe (he demos 30-minute) to watch them act as S/R.

### 3.5 Intraday shortcut method (5-minute charts)
1. Let the first hour form: note the day's significant high/low **as of 10:15 AM**.
2. Enter it into any online **"Gann square of nine calculator"** (first Google result).
3. Plot the generated supports/resistances at 10:15 and trade the day against them (his demo: Lodha, first-hour high 893 → levels broken/retested through the day).

### 3.6 His own usage guidance (worth keeping verbatim in spirit)
"**Use this as confirmation for any trade setup. Don't use it directly as a strategy** — combine it with other strategies for more accurate results." Stated twice, for both methods. He also prefers the manual method over the calculator, and rates the manual version usable for intraday, short- and long-term alike.

### 3.7 Notes & corrections (course annotations)
- **The formula is the classical Sq9 relation, cleaned up:** the transcript's "N factor for 180° is one" means *add 1 to the square root per half-rotation*; hence 0.25 per 45° and (√p + 2)² per full cycle. The math as given checks out.
- **His rounding is a ceiling, and it's aggressive:** 52.56 → 53 is ordinary, but 60.06 → 61 turns a 0.06 overshoot into a full extra point. Rounding to nearest (60) is the more common convention; whichever you choose, fix it and stay consistent, since ceiling shifts every level up ~half a point on average.
- **Level density explains much of the visual "respect":** with 45° levels ~0.3% apart at Nifty prices (§3.2), intraday price is nearly always close to *some* level; broken-then-retested sequences appear naturally. His own two concessions — "keep only 90° lines if there are too many" and "confirmation only, never standalone" — implicitly acknowledge this, and to his credit the video is more honest on this point than the aspect content.
- **Two more free parameters join the family:** the spiral's start value (1 vs. the swing low) and the choice of significant point both change the entire level set — same anchor-dependence caveat as Lesson 2 (§2.4). The 10:15 first-hour rule, by contrast, is fully specified — the one piece of this lesson that could be frozen and honestly backtested as-is.

---

## Lesson 4 — Cosmogram in GannZilla Pro: Setup and Aspect Meanings (Part 1)
*Source video: "Cosmogram in GannZilla Pro | The only true method that will change the way you do trading." A setup lesson — the three strategies it introduces are deferred to his part 2.*

### 4.1 What the Cosmogram is, and the system choice
The Cosmogram overlays planetary positions on the price wheel. Under **System**, GannZilla offers **geocentric** (Earth-centered) and **heliocentric** (Sun-centered) models; he selects **geocentric** for all his strategies. *(Course cross-check: this matches what we verified independently — every one of his live aspect calls we tested reproduced against geocentric longitudes, and the heliocentric alternative failed. The setting stated here is the setting he genuinely uses.)*

### 4.2 Setup walkthrough
- **Location:** Mumbai, India for the Indian market (or your own city/timezone).
- **Moon phases:** ring of new/full moon markers at the top — shown, then hidden; not used in this strategy set.
- **Cycles:** tetragram, pentagram, hexagram overlays representing time periods — not used here.
- **Price feed:** Sensex for India; commodity series also available (coffee, corn, cotton, soybeans, sugar, wheat, copper).

### 4.3 The working set: six planets, three aspects
For the strategies to come he restricts the toolkit to:
- **Planets:** Sun, Mercury, Venus, Mars, Jupiter, Saturn — the six classical bodies only.
- **Aspects:** conjunction (0°), quadrature/square (90°), trine (120°), with these stated meanings:

| Aspect | His meaning in this video |
|---|---|
| Conjunction | "Blending energy" — bullish momentum and reversals |
| Quadrature (square) | "Challenging aspect" — bearish momentum |
| Trine | "Positive opportunities" — bullish momentum |

### 4.4 The three strategies (pending part 2)
Strategy 1 uses conjunctions, strategy 2 trines, strategy 3 squares — all deferred to the Cosmogram part-2 video. This lesson will be extended when that transcript arrives.

### 4.5 Notes & corrections (course annotations)
- **Three conflicting aspect-meaning schemes now exist in his own material.** Cross-referencing this lesson against his X rulebook thread (07 Feb 26) and his actual recorded calls:

| Aspect | This video | His X rulebook | His actual calls (master table) |
|---|---|---|---|
| Conjunction | Bullish momentum / reversals | "Start — new cycle begins" | Mercury–Mars conj → bearish; Mars–Neptune conj → bearish |
| Square / quadrature | Bearish momentum | "#1 most powerful — sharp moves near tops & bottoms" (direction-neutral) | Venus–Venus quadrature → bullish; Venus–Saturn quadrature → reversal either way |
| Trine | Bullish momentum | "Flow — trend continues" | Uranus–Uranus trine → bearish reversal; Venus–Venus trine → bullish |

  No single scheme survives contact with the other two. When part 2 defines the strategies, note which scheme it actually uses — and treat any of the three as a labeling convention, not a law.
- **Planet-set discrepancy:** this video limits the toolkit to the classical six, yet his live X calls lean heavily on Uranus and Neptune (Uranus–Uranus trine, Venus–Neptune opposition, Mars–Uranus sesquisquare, Mars–Neptune conjunction). The taught system and the practiced system differ.
- **Nothing testable in this lesson** — it is tool setup plus vocabulary; the testable content arrives with part 2's rules.

---

## Lesson 5 — Jupiter–Uranus Conjunction & Opposition: The Rare-Event Reversal Thesis
*Source video: "Gann Opposition and Conjunction Strategy using Cosmogram" (Hindi, recorded 21 Mar 2024). This lesson is unusual: the video contains a forward prediction made on camera, which our price data can now grade.*

### 5.1 The concept and setup
Thesis: the Jupiter–Uranus **conjunction (0°)** and **opposition (180°)** are rare events that mark **major reversals of the prevailing trend**. Setup in GannZilla: Cosmogram visible → planets Jupiter + Uranus → aspects conjunction + opposition; find the next exact date.

**Frequency, corrected:** the Jupiter–Uranus synodic period is ~13.8 years, so conjunctions and oppositions alternate roughly every **6.9 years** (not "9–10"). More importantly, because of retrogradation each "event" is usually a **triple pass** — three exact hits spread over ~9 months — a mechanical fact the video never mentions and which matters below.

### 5.2 His two historical examples, verified
- **"Opposition, 21 Sep 2017 → 10,162 to 9,737 in 5 days."** The fall is real: from 21 Sep the index dropped ~3.5–4% in five sessions. But the exact opposition was **29 Sep 2017** — by which date the fall had already finished, and the market rose +2.0% in the five days *after* exactness. The example works only from his early date, not from the aspect's. It is also the *third* pass of a triple (27 Dec 2016 and 3 Mar 2017 were the others — both followed by rallies).
- **"Conjunction, 7 Jan 2011 → 6,092 to 5,208."** Real fall, right order of magnitude: from the 5 Jan 2011 exact pass, −3.6% in 5 days and −9.1% in a month, bottoming ~−11.5% about five weeks later (not immediately). Again the third pass of a triple — the 9 Jun 2010 pass was followed by a **+4.7%** five-day rally, and 19 Sep 2010 by nothing. *(Transcript slip: he calls this fall a "bullish reversal"; he means bearish.)*

### 5.3 The live forward call — graded
On camera (21 Mar 2024): market in a strong uptrend, conjunction due 20 Apr 2024 → *"very high chances we will see a good bearish reversal after 20th April 2024."*

What Nifty actually did from the 19 Apr 2024 close (22,147): **+1.2%** in 5 days, **+1.7%** in a month, **+12.0%** in three months, and **+18.4%** to the September 2024 high (26,216). No bearish reversal occurred at any horizon; the aspect date preceded one of the strongest five-month rallies in the dataset.

### 5.4 The complete event ledger (all exact passes, 2007–2026)

| Exact date | Type | Prior 5d trend | Fwd 5d | Fwd 20d | Reversal as claimed? |
|---|---|---|---|---|---|
| 09 Jun 2010 | Conjunction | −0.4% | **+4.7%** | +4.8% | No — rallied |
| 19 Sep 2010 | Conjunction | +3.8% | +0.9% | +1.6% | No |
| 05 Jan 2011 | Conjunction | +0.3% | **−3.6%** | −9.1% | **Yes** (his example) |
| 27 Dec 2016 | Opposition | −0.6% | +2.0% | +5.5% | No — rallied |
| 03 Mar 2017 | Opposition | −0.5% | +0.4% | +3.8% | No |
| 29 Sep 2017 | Opposition | −1.8% | +2.0% | +5.6% | No — fall preceded exactness |
| 21 Apr 2024 | Conjunction | −0.8% | +1.4% | +1.2% | No — +18% rally followed (his live call) |

Score for the thesis as stated: **1 of 7 exact passes.**

### 5.5 Notes & corrections (course annotations)
- **The triple-pass structure is the cherry-pick mechanism here:** each cited "event" had three exact hits, and only the pass followed by a fall gets shown. Displayed evidence: 2 events. Actual record: 7 passes, 1 hit.
- **Date flexibility strikes again:** the 2017 example is anchored 8 days before exactness, on the day the fall happened to start — the same ±-days freedom documented in the Venus–Saturn video test.
- **This rule is statistically untestable by design:** with one usable event cluster per ~7 years, no sample will ever exist. What *can* be graded is the one forward prediction on record — and it failed by the widest margin in this course.
- **Keep the frequency fact:** it's genuinely true that Jupiter–Uranus contacts are rare and generational in feel. What the ledger shows is that rarity confers narrative weight, not predictive power.

---

## Lesson 6 — Radix–Transit Mercury–Mars Conjunctions
*Source video: "Gann Cosmogram analysis using Mercury Mars Conjunction" (recorded 12 Apr 2024). The lesson where the natal chart is finally stated on camera — and where the "1–2 day deflection" gets quantified.*

### 6.1 The method
- GannZilla with **both charts visible**: the **Radix** (birth chart) set to the Nifty's first-trade date — **22 April 1996**, stated explicitly — and the normal **Transit** chart.
- Planets: **Mercury and Mars only**, on both charts. Aspect: **conjunction only**.
- Signal: a conjunction **between a radix planet and a transit planet** — transit Mercury reaching natal Mars, or transit Mars reaching natal Mercury. Transit-to-transit conjunctions are explicitly excluded.
- Claim: at every such conjunction, the market reverses — with an allowed **"deflection" of 1–2 days** either side.
- *Course cross-validation:* this is the same radix we derived independently in the Venus–Venus analysis (natal Venus ≈ 16° Gemini) before he ever named the date. Natal positions for this lesson: **Mercury 52.4° (≈22° Taurus), Mars 22.1° (≈22° Aries)**. The taught chart and the reverse-engineered chart agree — the one fully consistent pillar of his system.

### 6.2 His cited history — complete, for once
He walks through ten dates from Mar 2019 to May 2024. Checked against the ephemeris: **his list contains every single radix–transit Mercury–Mars conjunction in that window — 11 of 11 events, no omissions.** Unlike the Jupiter–Uranus lesson, there is no event cherry-picking here. The issue lives elsewhere.

### 6.3 The graded ledger (all events, 2019–2026)

| Exact date | Pair | Prior 5d | Fwd 5d | Reversal at exact date? | Within ±2-day deflection? |
|---|---|---|---|---|---|
| 20 Mar 2019 | tMars × nMerc | +1.6% | +0.4% | No | Yes |
| 03 May 2019 | tMerc × nMars | −0.1% | −3.7% | No | Yes |
| 24 Apr 2020 | tMerc × nMars | −1.2% | +1.5% | **Yes** | Yes |
| 19 Feb 2021 | tMars × nMerc | −1.2% | −3.0% | No | Yes |
| 16 Apr 2021 | tMerc × nMars | −1.7% | −0.9% | No | Yes |
| 08 Apr 2022 | tMerc × nMars | +0.6% | −4.6% | **Yes** | Yes |
| 08 Aug 2022 | tMars × nMerc | +1.1% | +2.4% | No | No |
| 31 Mar 2023 | tMerc × nMars | +1.7% | +2.1% | No | Yes |
| 24 Mar 2024 | tMerc × nMars | −0.2% | +2.0% | **Yes** | Yes |
| 13 Apr 2024 | tMerc × nMars | −1.1% | +0.4% | **Yes** | Yes |
| 09 May 2024 | tMerc × nMars | −3.0% | +2.0% | **Yes** | Yes |
| 10 Jul 2024 | tMars × nMerc | +0.2% | +2.0% | No | No |
| 06 May 2025 | tMerc × nMars | +0.2% | +0.8% | No | Yes |

### 6.4 The deflection window, quantified — the cleanest number pair in this course
- Reversal (5-day trend flip) **at the exact date: 5 of 13 = 38%** — *below* the 49% rate on any random day.
- Reversal **within his ±2-day deflection: 11 of 13 = 85%**.
- Base rate of a reversal within ±2 days of **any randomly chosen day: 85%**.

**85% vs 85%.** The deflection window does not reveal the signal — it manufactures the accuracy. Once a "reversal in either direction, any day within a 5-day span" counts as a hit, ~85% of the calendar qualifies, planets or no planets. This single comparison explains the felt accuracy of every deflection-based claim in his catalogue.

### 6.5 The live calls, graded
- **12 Apr 2024** (the video's own date): by his narration the reversal had *already started* and the market gapped down 75 points at the open before the "capture." Forward from the 12 Apr close: −0.8% in 5 days — a modest dip, announced intra-move.
- **8 May 2024** (announced for the future): market had fallen −3.0% into it; the 5-day forward was −0.5%, and the turn up came at the 10-day horizon (+3.0%). A hit under his elastic definition — as ~85% of dates would be.

### 6.6 Notes & corrections (course annotations)
- **Even his own narration betrays the definition:** the 6 Aug 2022 example is described as "market was in a good upward run… but exactly from 6th August market started going up." That is a continuation narrated as a reversal — and it fails the flip test even with deflection.
- **The unfalsifiability arithmetic:** either-direction reversal × ±2-day window ⇒ ~85% of all days qualify. Any rule graded this way will look like it "works every time."
- **The durable takeaway is the radix:** 22 Apr 1996 is now confirmed from two independent directions (his statement here, our earlier reverse-engineering). If you build anything from his system, that chart is the one specification you can rely on.

---

## Lesson 7 — Venus–Saturn Quadrature (Transit): The 150–300 Point Reversal Rule
*Source video: "Best trading strategy for Nifty with very high accuracy." This strategy was tested in full before the course began (see the Excel Backtest sheet); this lesson consolidates the teaching, adds the full-transcript details, and corrects one earlier finding.*

### 7.1 The setup — and how it differs from Lesson 6
- Cosmogram with **transit only** — the radix is explicitly switched off (contrast Lesson 6, which is radix–transit; his system uses both architectures on different rules).
- Planets **Venus + Saturn**; aspect **quadrature (90°)** only; **orb = 0°** — "we want the two planets exactly 90° away."
- **Holiday rule** applied throughout: aspect on a closed day → use the previous session (8 Jun 2024 → 7 Jun; 15 Apr 2023 → 13 Apr; 8 Nov 2022 → 7 Nov).

### 7.2 The rule and his cited ledger
When the quadrature forms: reversal of the prevailing trend, **150–300 points within 1–2 days**. His eight walkthrough cases (2020–2024) with claimed outcomes: 1 Jan 2024 (−220 pts), 13 Apr 2023 (−200), 7 Nov 2022 (−200), **17 Jun 2022 (+300, the one downtrend→bullish case)**, 16–17 Sep 2021 (−200), 23 Apr 2021 (bullish), 18 Nov 2020 (−166 next day), and the forward date 7 Jun 2024.

### 7.3 The verdict (from the full test — Backtest sheet)
All dates are astronomically real. But a ≥150-point counter-trend excursion within 2 days occurs on **39% of all trading days** in the same era; on ephemeris-exact dates the rule scored **5/8 (62%, p≈0.24)**; and across all 40 quadratures since 2007, the percent-normalized version hit **57% vs a 55% base rate** with identical median excursions (0.75% vs 0.76%). The rule performs at the noise floor — the "very high accuracy" is the noise floor, measured generously.

### 7.4 Correction and what the full transcript adds
- **Coverage corrected:** the earlier summarized transcript omitted the 17 Jun 2022 example, producing a false "1 event omitted" finding. The full transcript shows **all 8 events presented — no event cherry-picking in this video.** The accuracy is manufactured by target size vs. noise and by ±1–3-day date placement, not by omission.
- **Elastic horizons in the narration:** "fallen for the next four to five days… 200 points in the next two days" — magnitudes quoted over whichever window fits. When testing, fix the horizon first.
- **His own floor is soft:** the 18 Nov 2020 case is presented at 166 points, and the 13 Apr 2023 case (quoted as ~200) measured 127 points from his date on closing data — quoted magnitudes and measured ones differ.

### 7.5 Where Venus–Saturn now stands across his whole catalogue
Three appearances, one consistent reading: the 27 Dec 2023 post (bearish from Monday "because of Venus–Saturn"), the 25 Jul 2025 combined quadrature post (reversal template), and this transit rule (reversal, either direction). Venus–Saturn is his most internally consistent aspect — and the most thoroughly tested one, with the clearest null result.

---

## Lesson 8 — Venus–natalVenus Sextile: The "85% Win Rate" Birth-Chart Rule
*Source video: "The proven 85% win rate trading strategy for nifty | Gann Cosmogram" (recorded ~Jul 2024). Same radix architecture as Lesson 6, different planet and aspect — and it introduces his one genuine methodological filter.*

### 8.1 Setup
Cosmogram, **clockwise**, angle 0°, **geocentric**, location Mumbai. **Both radix and transit visible.** Radix date = **22 Apr 1996** (the Nifty birth chart, third confirmation); radix planet **Venus** only. Transit planet **Venus** only; aspect **sextile (60°)**; **orb 2°**. Two Venus markers appear — the fixed natal one and the moving transit one. He notes the same setup works for other instruments by substituting their listing date.

**Reversal timing:** not on the aspect date — **1–2 days after**. If that lands on a weekend, use the following Monday.

### 8.2 The new element: the retrograde exclusion filter
**Any aspect formed while the planet is retrograde is discarded.** He demonstrates it visually: stepping forward in time, a retrograde Venus appears to move backwards on the wheel. This is the only *restrictive* filter anywhere in his catalogue — every other rule we have documented widens the criteria. It is applied honestly here: the Aug 2023 sextile falls in Venus's retrograde period and he skips it, exactly as the ephemeris says he should.

### 8.3 His cited results
Claimed reversals: 20 Feb 2020 (~4,500 pts — "caught the Corona crash at the very top"), 18 Sep 2020 (800), 6 Mar 2023 (17,767 → 16,785), 19 Sep 2023 (20,238 → 19,345 ≈ 800), 18 Apr 2024 (~900), plus 500/300/250-point cases, **one acknowledged failure** ("here we can see it not went as per the analysis"), and the forward call for 25 Jul 2024.

### 8.4 The test — all events, his settings, his metric

| Exact date | Retrograde? | Cited | Reversal D+1 or D+2 |
|---|---|---|---|
| 11 Aug 2019 | — | no | Yes |
| 22 Feb 2020 | — | YES | **No** |
| 21 Sep 2020 | — | YES | Yes |
| 04 Apr 2021 | — | no | Yes |
| 11 Jul 2021 | — | no | **No** |
| 17 May 2022 | — | no | Yes |
| 25 Aug 2022 | — | no | Yes |
| 06 Mar 2023 | — | YES | Yes |
| 25 Jun 2023 | — | no | **No** |
| 21 Aug 2023 | **RETRO** | — | *excluded by his own filter* |
| 19 Sep 2023 | — | YES | **No** |
| 19 Apr 2024 | — | YES | Yes |
| 25 Jul 2024 | — | YES | Yes |
| 23 May 2025 | — | no | Yes |
| 08 Sep 2025 | — | no | **No** |
| 20 Mar 2026 | — | no | Yes |

**Result: 10 of 15 = 67%** — not 85%. **Base rate for the identical metric on a random day: 64%.** A 3-point edge on 15 events is indistinguishable from noise.

### 8.5 Notes & corrections (course annotations)
- **Where "85%" comes from:** not from this ledger. Counting only his *shown* examples (~8 wins, 1 acknowledged loss) gives ~89%; the title number sits in that neighbourhood. The five failures among events he didn't walk through are what separate 85% from 67%.
- **The Corona claim needs a correction:** the 20 Feb 2020 sextile did **not** catch the top. Nifty's high was 12,201 on 12 Feb; by the 20th it had already slipped to 12,081 and was falling (prior 5 days −0.8%). By his own D+1/D+2 flip test this event scores **No** — the market was already declining, so there was no trend to reverse. Attributing a 4,500-point pandemic crash to a Venus sextile is the largest single attribution in his catalogue, and it is the weakest.
- **Magnitude framing:** reversals are quoted as the *entire subsequent swing* (800, 900, 4,500 points) with no stop, no invalidation, and no maximum adverse excursion. A rule with no stop-loss cannot have a "win rate" in any tradeable sense.
- **Genuine credit — the retrograde filter:** this is the one place he *narrows* his criteria and takes a rule that costs him a data point. It's the most methodologically honest moment in the entire video series. (It doesn't rescue the edge — 67% vs 64% — but the intent is sound, and a retrograde filter is a legitimate, testable variable.)

---

## Lesson 9 — Retrograde Momentum: Stations as Reversal Dates
*Source video: "High accuracy trading strategy | Retrograde momentum explanation | Gann Cosmogram Course."*

### 9.1 What retrograde motion actually is (his explanation — and it's correct)
A planet appearing to move backwards through the zodiac is an **illusion of relative motion**, not real reversal in orbit. His analogy is sound: a faster car overtaking a slower one makes the slower appear to drift backwards; likewise trees appear to slide back past a moving vehicle. Since it is an Earth-observer effect, **retrograde exists only in the geocentric system** — never heliocentric. That is astronomically accurate, and it's the clearest piece of teaching in the series.

### 9.2 The strategy
- Settings: Cosmogram, **clockwise**, angle 0°, **geocentric** (mandatory, per above), one planet at a time.
- The tradeable moments are the **stations** — the dates retrograde motion **starts** and **ends** — not the retrograde period itself. His claim: at a station, the prevailing trend reverses.
- **Planet selection method:** "every planet does not work on every stock." He advises scanning each planet's stations against an instrument's history and adopting whichever fits best. For Nifty he reports **Venus retrograde works ~90% of the time**.
- **Speed/accuracy tradeoff (his framing):** Mercury stations 3–4× per year, Venus ~every 2 years, outer planets rarer — and "the more it takes time to make retrograde, the more the accuracy."
- His cited cases: 21 Jul 2023 (Rx start, uptrend → fall), 31 Aug 2023 (Rx end, downtrend → rise), 13 Dec 2021 (17,359 → 16,518), 25 Jan 2022 (Rx end → five green days).

### 9.3 The test — every Venus station, 2007–2026

22 stations occurred. Results using the standard 5-day trend-flip test:

| Metric | Venus stations | Base rate (any day) | Significance |
|---|---|---|---|
| Flip **at the station date** | 12/22 = **55%** | 49% | p = 0.38 — not significant |
| Flip **within ±2 days** | 21/22 = **95%** | 85% | p = 0.14 — not significant |

Not 90%. And the headline number is *sensitive to the metric*: 55% strictly, 95% loosely — with the loose version's base rate at 85%, exactly as in Lesson 6. Individual failures are easy to find: the Nov 2010 station (a downtrend that kept falling, −2.3%) fails both tests; May–Jun 2020 stations both fail at D0.

**His own comparison, checked:** Mercury stations (118 of them, far larger sample) also flip at **55%** — identical to Venus. His claim that slower planets give higher accuracy does not appear in the data; the two rates are the same, and Mercury's is measured on 5× more events.

### 9.4 Notes & corrections (course annotations)
- **The planet-selection method is the problem, stated openly.** "Go into the past, apply every planet, see which works perfectly, then use that one" is textbook **overfitting** — with 8–10 planets scanned across a fixed history, one will look excellent by chance alone. The ~90% figure is what a search over candidates produces, which is precisely why it doesn't survive out-of-sample: Venus lands at 55%, indistinguishable from Mercury's 55%.
- **Two-sided claims can't fail:** both the start *and* the end of retrograde are reversal dates, and either direction counts. That's four reversal opportunities per Venus cycle, each ±2 days wide.
- **Sample size:** 22 Venus stations in 19 years. Even a real effect couldn't be established at this sample size — a fact worth remembering whenever "high accuracy" is claimed for a rare-event rule.
- **Credit where due:** the physics explanation is correct and well taught, the geocentric-only constraint is right, and the honest admission that a planet must be *selected* per instrument is more transparent than most of his other content — even though that admission is exactly what invalidates the accuracy claim.

### 9.5 Course-commerce note
This video also markets his paid course (₹8,499 discounted, stridewise.in, 4 chapters / 15 lessons, 2-year access, WhatsApp support). Recorded here for completeness. Given the test results across Lessons 5–9 — every headline accuracy figure landing at or near base rates once all events are counted — evaluate that purchase against the evidence in this course document rather than the claims in the videos.

---

## Lesson 10 — Venus–Jupiter Quadrature: The Only Rule With a Complete Trade Plan
*Source video: "Gann Cosmogram strategy for Nifty | High accuracy Trading Strategy" (Hindi). The one video that states target and stop-loss — which finally makes a proper win-rate and expectancy test possible.*

### 10.1 Setup and rule
Cosmogram, clockwise, angle 0°, **geocentric**, Mumbai, **transit only** (radix off — birth-chart mode is for other strategies). Planets **Venus + Jupiter**; aspect **quadrature (90°)**. **Retrograde dates are excluded** — the filter from Lesson 9 is applied consistently here, and in the video he skips a Venus-retrograde instance mid-walkthrough. **Holiday rule:** aspect on a closed day → use the previous session.

**Direction:** judged by the last 2–3 days. Bullish into the date → expect a bearish reversal; bearish into it → expect a bullish one.

**His honest definition of "reversal":** explicitly *not* a huge turn — he defines the expected move as **250–300 up to 900–1,000 points**, a useful clarification that applies retroactively to his whole catalogue.

### 10.2 The trade plan — the part worth having
| Parameter | His guidance |
|---|---|
| Entry | At the market close of the aspect date (or prior session if holiday) |
| Target | **Minimum 250–300 points** |
| After target | Hold with a **trailing stop** for a longer move |
| Stop loss | **210–220 points** |
| Claimed accuracy | **>80%** |

This is the only complete, tradeable specification in the entire video series. His cited cases: 23 Feb 2024 (+300), 15 Sep 2023 (750), 9 Jun 2023 (300), 9 Dec 2022 (bullish, 3 days).

### 10.3 The test — his exact parameters
Every non-retrograde Venus–Jupiter quadrature, 2007–2026: entry at the close, target 275, stop 215, 10-day cap.

| Result | Count |
|---|---|
| Events | 36 |
| Wins | 14 |
| Losses | 12 |
| Neither hit in 10 days | 10 |
| **Win rate (decided trades)** | **54%** (his claim: >80%) |
| Expectancy | **+35 points per trade** (before costs) |
| Base rate: same trade, random entry days | **43%** |

**Reading it fairly:** 54% vs a 43% base is the largest positive gap any rule in this course has produced, and the expectancy is positive on paper. But with 26 decided trades it is not statistically significant, +35 points is thin against slippage and spread on a 215-point stop, and the win rate is nowhere near 80%. Treat it as the one hypothesis in his catalogue that merits paper-trading forward, not as a proven edge.

### 10.4 Why the trade plan matters more than the aspect
The favourable risk-reward (275 target vs 215 stop) plus a trailing stop after target is *ordinary sound trade management*, and it is what produces the +35 expectancy — not the planetary trigger, whose event dates barely outperform random entries. **This is the transferable lesson of the whole series: his risk mechanics are the valuable half of his output.**

---

## Lesson 11 — The Three-Planet Pattern, and the Calendar Trap
*Source video: "Gann Cosmogram | The only true method that will change the way you do trading."*

### 11.1 The pattern
Transit only, geocentric. Planets **Sun, Uranus, Neptune**. Aspects: **sextile (orb 5°)** and **quincunx (orb 3°)**. The signal is a triangle: **Sun quincunx Uranus, Sun quincunx Neptune, and Uranus sextile Neptune simultaneously.**

His reasoning: Uranus–Neptune sextile is "largely positive," while the two Sun quincunxes are "challenging" — growth plus challenge together produce a reversal. Direction as always: bullish market → bearish reversal, and vice versa. Cited: 18 Oct 2023 (19,830 → 18,800, ~1,000 pts), 14 Oct 2022 (17,009 → 18,449, ~1,400 pts), with 21 Oct 2024 given as the forward date.

**Orb teaching (worth keeping):** his explanation is textbook-correct — orb 5° on a sextile means the aspect counts anywhere from 55° to 65°.

### 11.2 The calendar trap — the finding of this lesson
Uranus and Neptune move so slowly that their sextile persists for **years**; the Sun supplies all the timing. A Sun quincunx to a near-stationary point recurs at **the same calendar position every year**. Result: every occurrence of this "pattern" in the entire dataset falls in **mid-to-late October**:

- 17–18 Oct 2023 · 18–22 Oct 2024 · 21–25 Oct 2025

That's the complete list — **three windows, all in October, all consecutive years**. The pattern is not a rare planetary configuration; it is *an October date*, dressed in aspect language. Any trader could reproduce it with a calendar reminder.

### 11.3 The test
Of the three windows, **1 of 3** produced a 5-day trend flip (2023: no — the decline continued; 2024: no; 2025: yes). His two cited "successes" both fail the flip test on closing data — in Oct 2023 the market was already falling before his date (prior 5 days −0.7%), so there was no uptrend to reverse, the same error documented in Lesson 8's Corona claim.

Nifty's October seasonality, for context: average daily return **+0.032% vs +0.045% for all months** — October is unremarkable, so no hidden seasonal edge is being captured either.

### 11.4 Notes & corrections
- **Three planets sound rarer than they are.** With Uranus–Neptune within 5° of sextile on 11% of all days across this era, the "triple pattern" reduces to one fast-moving body hitting an angle — annual, not exotic.
- **Sample of three cannot support "very high accuracy."** No test at n=3 can distinguish a rule from a coin flip.
- **A useful diagnostic to carry forward:** whenever a multi-planet pattern includes the Sun (or Moon) plus slow outer planets, check the calendar dates first. If they cluster in one month, the "pattern" is a season, not a signal.

---

## Lesson 12 — Mercury–Saturn Conjunction
*Source video: "High accuracy nifty strategy | Gann Cosmogram Strategy."*

**Setup:** transit only, geocentric, Mumbai. Planets **Mercury + Saturn**, aspect **conjunction**, **orb 1°**. He describes the pair as "mixed effect — can be bearish or bullish," hence a reversal indicator. Direction from the prior 3–5 days. Expected move: **400+ points**; he defines reversal here as "small retracements." Cited: 3 Mar 2022 (600+), 2 Mar 2023 (400+), 29 Feb 2024 (400+), forward call 25 Feb 2025.

**Test (23 conjunctions, 2007–2026):** flip rate **16/23 = 70%** vs a 49% base rate, p = 0.038. This is the **strongest single result of the entire project** — but three cautions apply. First, ~25 rules have now been formally tested here, so at p<0.05 roughly one false positive is expected by chance, and this is it. Second, n=23. Third, **his own forward call failed**: 25 Feb 2025 showed no flip (prior 5 days −1.7%, next 5 days −0.9% — the decline simply continued). Worth paper-trading alongside Venus–Jupiter, not worth believing yet.

**The reasoning error to avoid (§12.1):** his stated logic is *"it worked the past three dates, so there is high chance it will work for the 4th too… whenever any relationship is working from the past three dates then it has high accuracy."* Three consecutive successes cannot establish reliability — and here the fourth, which he predicted on that basis, failed. Note also that his three cited cases all fall in late Feb/early March of consecutive years; the full 23-event set spreads across eight different months, so the tight clustering is a selection artifact, not a property of the aspect.

---

## Lesson 13 — Jupiter–natalJupiter Opposition
*Source video: "Gann Cosmogram Nifty analysis using Jupiter-Jupiter Opposition."*

**Setup:** birth-chart mode — radix (22 Apr 1996) and transit both visible, planet **Jupiter** on both, aspect **opposition**, **orb 2°**. Claim: *"whenever Jupiter–Jupiter opposition forms, Nifty has given good movement in the bullish direction **always**"* — the only unidirectional (non-reversal) claim in his catalogue. Cited: 9 May 2014 (6,659 → 7,430, ~10%) and 31 May 2002 (1,027 → 1,096, ~6–7%). Forward call: **25 Aug 2025, bullish**.

**Mechanics:** transit Jupiter opposes its natal position once per ~11.86-year orbit, so this is a genuinely rare event — and, like Jupiter–Uranus in Lesson 5, each occurrence is a **triple pass** across ~9 months.

**The event record (natal Jupiter 287.4°):**

| Pass | Nifty +1m | +3m | +6m |
|---|---|---|---|
| 24 Sep 2013 | +4.6% | +6.7% | +11.7% |
| 22 Dec 2013 | +0.9% | +4.8% | +19.2% |
| 16 May 2014 | +4.7% | +5.9% | +17.0% |
| 30 Aug 2025 | +0.0% | +6.5% | +3.2% |
| 01 Feb 2026 | −0.9% | **−5.0%** | **−5.0%** |

**Grading his live call:** from 25 Aug 2025 (24,968), Nifty ran **+0.8% at one month, +4.4% at three months** — then gave it back, sitting **−4.5%** by April 2026. Short-to-medium horizon: a fair hit. His first genuinely successful forward call in this course, and it deserves the credit.

**But the "always" fails:** the Feb 2026 pass of the same triple was followed by −5% at both three and six months. One directional claim, five passes, one clear miss — and the 2013–14 cluster coincides with the well-known Modi-election bull run, which no aspect was needed to produce. With ~2 independent events per two decades, this rule can never be statistically established.

---

## Lesson 14 — Modified Square of 9
*Source video: "Modified version of Gann Square of 9." Part 2 of the Sq9 series (Lesson 3 is part 1).*

**The problem it solves:** the standard Sq9 spiral increments by 1, which is useless when Bank Nifty trades in five digits — the levels come out impossibly dense.

**The increment formula:**

> **increment = ( (major high − major low) ÷ N ) × 4**,  where N = number of candles between the high and low

**Constraint: N must exceed 150 candles** (use TradingView's date-range tool to count bars). His worked example: (20,222 − 18,837) ÷ 183 × 4 = **30.27 → 30.3**.

⚠️ **Correction:** his spoken words — "divided by N into four" — literally mean ÷(N×4), which gives 1.89, not 30.27. His own arithmetic confirms the formula is **((H−L)/N)×4**. Use the parenthesised version.

**The two-pass level construction:**

| | Value (start) | Find | Increment sign |
|---|---|---|---|
| Case 1 | major **high** | major low | **negative** (−30.3) |
| Case 2 | major **low** | major high | **positive** (+30.3) |

For each case: set GannZilla layout to Square of Nine with that value/increment, locate the cell nearest the "find" price, add the vector rays (45/90/135/180/225/270/315), and rotate until a ray passes through that cell. **Major levels** = all cells along that ray. **Minor levels** = cells on the rays 90° away. Plot both sets; his demo showed price repeatedly respecting them across multiple retests. Works on any timeframe, high or low, provided N > 150.

**Annotation:** this is a legitimate scaling fix and the levels are reproducible *once* the anchors are chosen — but anchor choice (which major high, which major low) remains free, so two analysts still get two level sets. Same caveat as Lessons 2 and 3, and the same as with all level methods: with major *and* minor levels plotted, the chart is dense enough that "respecting levels" is close to guaranteed (Lesson 3, §3.7).

---

## Lesson 15 — Scaling the Gann Fan Properly
*Source video: "how to draw and scale Gann Fan properly." **This is the strongest technical content in the entire series** — and it directly answers the objection raised in Lesson 1 (§1.4).*

### 15.1 The problem
A hand-drawn 45° line assumes fixed paper scale. In TradingView, zooming in or out changes the visual angle of the same line — so a "45° fan" is not reproducible. He states the problem plainly and offers two fixes.

### 15.2 Method 1 — Lock price to bar ratio
Right-click the price panel → **Lock price to bar ratio**. The scale then stops changing on zoom. His honest verdict: *correct for hand-drawn paper charts in the Gann tradition, but not truly correct in TradingView.*

### 15.3 Method 2 — Time-and-price scaling (his own method)
Built from Gann's "squaring price and time": if price = time², then **time = √price**. So **one unit of price = √(price at the anchor point)**.

**Procedure:**
1. Draw the fan from the significant low; open **Settings → Coordinates**.
2. Read point 1: price P₁ and bar B₁ (bar = candle index, i.e. time).
3. Set point 2 to **bar = B₁ + N** and **price = P₁ + N×√P₁**, for any natural number N.
4. From a significant **high**, **subtract** instead: price = P₁ − N×√P₁ (the second point sits lower).

**His worked example:** anchor at 32,343.5 on bar 175. √32,343.5 = 179.84. So point 2 = bar 176, price 32,523.34 (N=1) — or bar 180, price 33,242.7 (N=5). The fan is now scale-invariant: zooming changes nothing.

### 15.4 Why this one earns credit
The mathematics is sound and internally consistent — square-root price scaling is a genuine Gann tradition (it's the same √price relationship underlying the Square of 9 formula in Lesson 3), and fixing the fan by *coordinates* rather than by eye makes it genuinely reproducible: two analysts with the same anchor now draw the identical fan. **This is real technical craft, and unlike his aspect claims it makes no accuracy promise at all.** If you take one practical technique from his entire body of work, this is the strongest candidate.

---

## Lesson 16 — Solar Dates & Time Cycles
*Source: his X threads (the "Gann knowledge Day 1–3/50" series and the solar/time-cycle threads).*

### 16.1 Solar dates
- **The market year starts 21 March** (spring equinox), not 1 January.
- **Four seasonal turning points:** 21 Mar (new trends), 21 Jun (tops form), 23 Sep (reversals begin), 22 Dec (bottoming).
- **Static degrees** react strongly: 30, 45, 60, 72, 90, 120, 135, 150, 180, 210, 225, 240, 252, 270, 288, 300, 315, 330, 360.
- **Conversion formula: degrees × 1.0146 = days forward.** ✅ *Verified: 365.25 ÷ 360 = 1.0146 — the mean days per degree of solar longitude. The arithmetic is exactly right.* Example: 30° × 1.0146 ≈ 30.4 days after 21 Mar → ~20 April, a static window every year.
- **Dynamic dates:** same formula, but counted forward from a major high or low instead of the equinox. He notes the strongest setups occur when static and dynamic dates **align**.

**Test of the four turning points** (±2 days, 5-day flip test, Nifty 2007–2026): 21 Mar **43%**, 21 Jun **65%**, 23 Sep **57%**, 22 Dec **56%**, and the 30° date (~20 Apr) **52%** — against a 49% base. The June solstice window is the standout (p = 0.007), but the same multiple-testing caveat as Lesson 12 applies, and 21 March — the framework's anchor — underperforms the base rate.

### 16.2 Time cycles
The hierarchy: **10-year "king" cycle** (major tops/bottoms; sub-turns at 5 years, 2.5 years, 40 months, 15 months), **7-year** (sub-turns at 3.5 years, 21 months, 10–11 months), **5-year** (half the king cycle — "the market's breathing rhythm"), and small 1–3 year cycles. His stated bull pattern: 2 years up, 1 year correction, 2 years up, with a major turn at month 59–60; the bear pattern mirrors it. Watch for exhaustion near 23–24, 30, and 41–42 months.

### 16.3 The best epistemics in his catalogue
This thread contains his most disciplined statements, and they deserve quoting in spirit:
> *"Time cycles are not magic and not every stock follows the same rhythm. They must be BACKTESTED."*
> *"These are turning windows, not guaranteed reversal days. Use with support/resistance, trendline breaks, volume spikes. Time gives the signal zone, not blind entries."*
> *"Every stock and index has its own time personality — your job is to find which clock the market follows."*

That is a fair description of how cycle work should be treated — as a watchlist of dates requiring price confirmation, not a prediction engine. Held against his own video claims of "90% accuracy," "100% profitable," and "proven 85% win rate," the gap between the standard he articulates here and the standard he markets elsewhere is the single most useful observation in this course.

### 16.4 One notation resolution
Day 1 of the thread settles the ambiguity flagged in Lesson 1 (§1.7): *"1×1 means you can plot it as (1,1)… similarly 1×2 means (1,2)."* With x = time and y = price, 1×2 gives slope 2 ≈ 63.75° — confirming **first number = time, second = price**. Lesson 1's correction stands.

---

*Further lessons will be added as transcripts arrive.*
