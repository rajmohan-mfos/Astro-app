import { useEffect, useState } from 'react'
import { vikasWeek } from '../api'
import type { VikasDay, VikasWeekResult } from '../types'

// Vikas ("Astro class" playlist) — a dates method, not a direction
// method. The engine (backend/app/vikas.py) lists the dates his rules
// produce; the trade is the date candle's high/low on the chart, which
// only the trader can take. Concept notes are condensed from
// backend/knowledge/vikas/NOTES.md; the verdict block from
// backend/knowledge/backtest/vikas/RESULTS.md.

const CONCEPTS: [string, string, string][] = [
  ['The date candle', 'A planetary event gives a DATE. Its daily candle\'s high and low are the levels: high-cross → long, low-cross → short, the other side is the stop. Event after 15:30, or on a holiday/weekend → next trading day (after a Friday, always Monday). Inside candle → take the outer one. A very big candle is unusable — the market ranges inside it.', 'Class 1, 6'],
  ['Reversal vs big dates', 'When the date lands at a swing top/bottom, do not take the first move — wait for the retest of the candle. Big dates (Mercury → Aries) trade on the break. A date\'s level keeps working for weeks.', 'Class 1'],
  ['Moon in a Saturn star', 'Pushya, Anuradha, Uttara Bhadrapada days (every ~9 days) are Nifty / Reliance dates; Jupiter stars → Bank Nifty; Venus stars → Bajaj Finance; Mars stars → Hindalco. The star must cover ≥ 4–5 h of the session; if it starts after the close the next day is the date; never a Friday; use it till that week\'s Friday unless a top or bottom formed. If the market is at a top or bottom on the date, trade the reverse; in the middle, leave it.', 'Class 3, 5'],
  ['Sun nakshatra dates', 'Same calendar day every year ±1: Uttarashadha (~11 Jan) "market does not fall that week, 95%"; Shravana (~24 Jan), Rohini (~25 May), Hasta (~27 Sep) — Moon-lorded stars → reversal dates; Dhanishta (~6 Feb) bearish 2–3 days.', 'Class 1, Demo 2'],
  ['Mercury enters Aries', '"Big date" — the day\'s low is not closed below for months (2022: 8 Apr; 2023: 31 Mar; 2025: 7 May → 13 May retest low). "Mesha is important for every planet — backtest each one, for every instrument"; Rahu in Mesha → IT tops and bottoms.', 'Class 1, 2'],
  ['Moon in Mesha', 'Both days of the Moon\'s ~2¼-day Aries transit are Nifty dates (count Meena too when Mesha lands on a holiday): 6–7 Jan 2025 top, 3–4 Mar 2025 bottom, 1–2 Apr 2025 gap-down, 9–10 Apr 2024 top. At a channel top do not go long — wait for the pull-back.', 'Class 2'],
  ['Mercury at the same degree as Rahu or Ketu', 'Same sign, 0° — "perfect reversal in Nifty", 2–4 dates a year: 30 Sep 2024 top, 3 Mar 2025 bottom, 20 Mar 2024 bottom, 11 Apr 2022 top. A match that completes after midday makes the next day the date.', 'Class 2, 4'],
  ['Venus within 8° of Uranus', 'Same sign (GannZilla, tropical): the day the orb closes to 8° is "important" — 19 Apr 2021 bottom (+30%), 6 Jun 2022, 26 Jun 2025 ("30,000 if it crosses the high"). Buying only: once its high is crossed the market does not come back.', 'Class 2, 6'],
  ['Mars vs Saturn (metals)', 'Mars in the 12th sign from Saturn (the sign before Saturn\'s) → metal sector falls; Saturn in an even sign → big fall (50% in 2020), odd sign → small (10% in 2024). Mars entering Saturn\'s own sign → rise (22 Mar 2020 bottom). Mars in Dhanishta → bearish metals.', 'Class 4'],
  ['Big × small planet 30°/60°', 'Jupiter/Saturn/Uranus/Neptune/Sun at 30° or 60° to Mars/Mercury/Venus → date; Jupiter 30° Mercury gave the 13 May 2024 bottom. Also Sun–Neptune same degree (bullish, buy above the high), Venus–Ketu, Mercury–Ketu/Rahu same degree.', 'Class 1, 4'],
  ['Moon at 45° at the open', 'GannZilla geocentric (tropical) Moon at 45 / 135 / 225 / 315° (and 270°) near 09:15, within ±2–3° — "universal date", high and low matter, not a reversal call, not on a holiday. Venus "45°" likewise (his 11 May / 23 Jun 2025 sit at a Sun–Venus 45° separation).', 'Class 4, 6'],
  ['Day-lord direction', 'Sequence Ketu·Venus·Sun·Moon·Mars·Rahu·Jupiter·Saturn·Mercury. Malefic lord (Ketu, Sun, Mars, Rahu, Saturn) takes the market UP (supply falls → prices rise); benefic (Venus, Jupiter, Mercury) DOWN. Moon is benefic only from Shukla Dashami to Krishna Panchami. He does not use Sun/Moon days.', 'Class 1, 5'],
  ['The carry-over', 'If a day closes AGAINST its lord and the next day\'s lord is of opposite nature, the next day goes the other way (or sideways) — "don\'t long". Conditions: consecutive trading days, Moon in the same sign, no other planet changed sign, the market still inside the previous candle (overlapping candles). Usable 7–8 times a month at most.', 'Class 1, 5'],
  ['Saturn → Mercury retrace', 'If a Saturn-star day falls the whole session, the next Mercury-star day (Ashlesha, Jyeshtha, Revati) retraces at least half of it, then falls again — "100%, don\'t doubt it". Pushya → Ashlesha is his favourite.', 'Class 1, 5'],
  ['Chart layer', 'Measuring gap between candle 1 and candle 3 of a leg = support/resistance (order block); never trade the break, wait for the retest; 5-/15-minute frames for intraday, weekly for trend, hourly is useless for a 6-hour market; flag targets = pole height; after a big candle sell options in the range.', 'Class 1, 3, 5, 6'],
  ['RBI policy day', 'Sideways till 10:00; the first 5-minute move at 10:00 / 10:05 is a trap — trade the opposite side with the candle\'s extreme as stop. "100% in the last 8, 90% last year".', 'Class 5'],
  ['Sectors and stocks', 'Mars = metals (also power, property); Jupiter = banking; Saturn = oil & gas, IT, Nifty itself; Venus = luxury, finance; Mercury/Rahu = IT; Ketu = pharma (Glenmark). Stock radix: incorporation or listing date; the sector planet at 0°/30°/60° to its natal place marks tops and bottoms.', 'Class 1, 5, 6'],
]

const VERDICT: [string, string, string][] = [
  ['Day-lord direction (malefic up / benefic down)', '49.8% on 2,808 clean sessions (ex Sun/Moon days), majority side 54.6%', 'coin. Saturn-star days actually close DOWN 58% (p 0.001, one of 9 lords) — the opposite of his reading and the classical one'],
  ['Carry-over (his full conditions)', '47.3% on 423 setups; "day 2 does not close beyond day 1\'s extreme" 63% vs 62% base', 'nothing. His "100%" is the base rate'],
  ['Saturn → Mercury half-retrace', '70.6% of 136 vs 68.8% for any down day', 'nothing — any down day is retraced half the time'],
  ['His date candles as breakout levels', 'follow-through 52–60% across every date family vs 57.5% for any candle; "range held 5 sessions" ≈ 0% for all', 'a date\'s candle is no better a level than any other candle'],
  ['Sun → Uttarashadha week "does not fall, 95%"', 'week holds the day\'s low 6 of 16 years (31% base)', 'no'],
  ['Mercury → Aries low "not closed below for months"', 'holds 20 sessions 7/18 (base 26%), 60 sessions 4/18 (18%)', 'no'],
  ['Mars in the 12th sign from Saturn → fall', 'Nifty −5.2% mean over the transit, 8/11 down vs 35% base (p 0.02); Nifty Metal −4.0%, 8/11; gold +2.3% (no)', 'the one lead: median −3.4%, even-sign Saturn −10.8% vs odd +1.4% as he says — but n = 11 and the mean is the 2020 span'],
  ['Mars in Saturn\'s sign → rise', 'Nifty +7.5% mean, 11/11 up vs 65% base (p 0.01); both halves +8.6% / +6.7%; Nifty Metal +8.2%', 'holds everywhere it was looked at; n = 11, one span every ~18 months. Forward ledger, not a strategy'],
  ['Moon at 45/135/225/315° (tropical) at open', 'breakout follow-through 64% vs 57.5% (n 281, p 0.03); sidereal 55%', 'one of ~28 candle families — expected by chance'],
  ['Moon in Mesha (both days) as Nifty dates', 'follow-through 60% vs 57.5% (n 282); +5d +35 bp vs +21 (p 0.26)', 'no'],
  ['Mercury at Rahu/Ketu\'s degree → reversal', 'n 41 dates: follow-through 57%; 5-day reversal no better than base', 'no'],
  ['Venus within 8° of Uranus → big date', 'n 12 since 2011: follow-through 7/10; +5d +72 bp vs +21 (p 0.44), +10d +39 vs +42', 'too few to say anything, and no lean'],
  ['Mars in Dhanishta → metals fall', 'gold +0.9%, silver +3.1%, Nifty Metal −0.7%, Nifty −0.8% (7/9)', 'no'],
  ['Jupiter & Venus one sign → bullish', 'Nifty +0.1% over 26 spans vs +0.8% base', 'no'],
  ['Monday green → Tuesday red', '58% vs 55.5% base', 'no'],
]

const FAMILY_CLASS: Record<string, string> = {
  sun_nak: 'bias-reversal', mercury_sign: 'bias-bullish', mars_sign: 'bias-bearish',
  mars_nak: 'bias-bearish', big_small: 'bias-neutral', same_degree: 'bias-neutral',
}
function chipClass(family: string) {
  if (family.startsWith('moon')) return 'bias-neutral'
  if (family.startsWith('venus45')) return 'bias-neutral'
  return FAMILY_CLASS[family] ?? 'bias-neutral'
}

function DayRow({ d, today }: { d: VikasDay; today: string }) {
  const s = d.star
  const starLine = `${s.nakshatra} (${s.lord}, ${s.nature})`
    + (s.open_ends ? ` — ${s.open_nakshatra} till ${s.open_ends}` : '')
    + (!s.full_session && !s.open_ends ? ' — changes during the session' : '')
  const quiet = !d.star_date && d.events.length === 0 && !d.carry_over
  return (
    <li className={'gann-event' + (d.date === today ? ' today' : '')
      + (!d.trading ? ' sap-closed' : '') + (quiet ? ' vikas-quiet' : '')}>
      <div className="gann-event-head">
        <span className="gann-date">{d.date} · {d.weekday}
          {d.date === today && <span className="gann-today-chip">today</span>}
        </span>
        <span className="gann-title">Moon in {starLine}</span>
        {d.star_date && (
          <span className="verdict-badge v-lean" title="Moon in a lorded star that covers ≥ 4 h of the session, not a Friday">
            {s.lord} star → {d.star_date}
          </span>
        )}
      </div>
      {d.events.length > 0 && (
        <div className="sap-line">
          {d.events.map((e, i) => (
            <span className="sap-inst" key={i} title={e.note}>
              <span className={`bias-chip ${chipClass(e.family)}`}>{e.label}</span>
              <span className="sap-name">{e.instrument}</span>
            </span>
          ))}
        </div>
      )}
      {d.events.length > 0 && (
        <div className="gann-market">
          {d.events.map((e) => e.note).filter((n, i, a) => a.indexOf(n) === i).join(' · ')}
          {!d.trading && d.shifted_to && <> — market closed ({d.closed}); the date moves to <strong>{d.shifted_to}</strong>.</>}
          {d.trading && d.weekday === 'Fri' && <> (a Friday date: he takes Monday instead)</>}
        </div>
      )}
      {d.carry_over && <div className="gann-note">Carry-over setup: {d.carry_over.text}</div>}
      {!d.trading && d.events.length === 0 && <div className="gann-note">{d.closed} — closed.</div>}
    </li>
  )
}

export default function VikasPanel({ date }: { date?: string }) {
  const [week, setWeek] = useState<VikasWeekResult | null>(null)
  const [err, setErr] = useState<string | null>(null)
  useEffect(() => {
    setWeek(null)
    setErr(null)
    vikasWeek(date, 28).then(setWeek).catch((e: Error) => setErr(e.message))
  }, [date])
  const today = week?.start ?? ''

  return (
    <>
      <section className="panel">
        <h2>Vikas — important dates, next four weeks</h2>
        <p className="learn-p">
          His method gives <strong>dates</strong>, not direction: "daily prediction by astrology is
          rubbish … astrology is for dates, the trade comes from the chart." Each row is the Moon
          star that owns the session (with its lord and his malefic/benefic tag), the star dates
          he trades, and every planetary event whose date falls that day, already shifted past the
          close and past holidays the way he does it. What you do with a date is mark its candle's
          high and low and trade the cross — see the concept notes below.
        </p>
        {err && <p className="muted-note">calendar unavailable: {err}</p>}
        {!week && !err && <p className="muted-note">computing the dates…</p>}
        {week && (
          <ul className="gann-list">
            {week.days.map((d) => <DayRow d={d} key={d.date} today={today} />)}
          </ul>
        )}
        <p className="muted-note">
          Sidereal Lahiri (drikpanchang) for stars and ingresses; GannZilla-style tropical
          longitude for the Moon-45° dates, as he uses them. Backtested against Nifty
          2011–2026 — see the verdict block.
        </p>
      </section>

      <section className="panel">
        <h2>His concepts (from the nine class recordings)</h2>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>The rule as he teaches it</th><th>Where</th></tr></thead>
          <tbody>
            {CONCEPTS.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td className="learn-missing">{w}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Full provenance with transcript timestamps: <code>backend/knowledge/vikas/NOTES.md</code>.
          He is a separate teacher from GRAHA MARKETS (Prediction tab) and Saptarsh Insight;
          classes are in Hindi and Tamil, transcribed with <code>tools/transcribe.py --lang auto</code>.
        </p>
      </section>

      <section className="panel">
        <h2>Backtest verdict — Nifty 2011–2026, Bank Nifty, Nifty Metal, COMEX gold &amp; silver</h2>
        <p className="learn-p">
          Every computable rule was run over 3,848 Nifty sessions and scored against the same
          statistic on <em>every other day</em>, with no parameter fitted to prices. He insists
          on self-backtesting ("if you get 80–90% note it down, otherwise reject it") — this is
          that, done with his own dates.
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Rule</th><th>Result</th><th>Reading</th></tr></thead>
          <tbody>
            {VERDICT.map(([k, v, r]) => (
              <tr key={k} className={k.startsWith('Mars in') && !k.includes('Dhanishta') ? 'sig-weak' : ''}>
                <td className="learn-key">{k}</td><td>{v}</td><td>{r}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Not testable without intraday bars: the high/low-cross entries themselves, the first-hour
          rule, gap retests, the RBI-day fade, stock radix dates. Numbers:{' '}
          <code>backend/knowledge/backtest/vikas/RESULTS.md</code>; rerun with{' '}
          <code>python scripts/backtest_vikas.py</code> from <code>backend/</code>.
        </p>
      </section>
    </>
  )
}
