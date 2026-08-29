import { useEffect, useState } from 'react'
import { saptarshWeek, vikasWeek, volatility } from '../api'
import type { SaptarshDay, VikasDay, VolatilityResult } from '../types'

// The opening tab. Everything the four backtests agreed on, in one
// place, and the only component with measured skill (session width)
// shown live. Numbers are copied from STRATEGY.md and the result
// files; the doc is the source of truth, this is its dashboard.

const ROWS: [string, string, string, string, string][] = [
  ['Predicts', 'Nifty session direction (sunrise chain, panchang tally, horai)', 'Reversals / swings at dated aspects and stations', 'Nifty session; gold & silver daily direction; intraday windows', 'Dates, not direction: planetary events → the date candle\'s high/low as levels; a day-lord direction rule; Mars-vs-Saturn metal rules'],
  ['Tested on', 'Nifty 2011–2026, walk-forward (3,830 bars); BankNifty', 'Nifty & Bank Nifty 2011–2026, every exact event of the 11 catalogued rules', 'Nifty, COMEX gold & silver 2016–2026 (~2,650 days each)', 'Nifty 2011–2026 (3,848 bars); Bank Nifty; Nifty Metal; COMEX gold & silver 2016–2026'],
  ['Must beat', 'Always-down on its own days: 53.0%', 'Same statistic on every other day: 5d reversal 49%, flip within ±2 days 88%, candle follow-through 57.5%', 'Majority side on its own days: 52.3% / 54.6% / 52.5%', 'The same statistic on every other day: candle follow-through 57.5%, week-holds-low 31%, majority side 54.6%'],
  ['Headline', 'Engine 48.9% (z −4.2, worse than always-down); best nested walk-forward 53.95% (z +0.5)', 'Mercury–Saturn flips 11/19 = 58% vs 49% (p 0.50 — the archive’s 70% does not replicate); Venus–Jupiter 55%; best row Mars–Jupiter semisquare +126 / +203 bp (p 0.07 / 0.03), 1 of 22 tests', 'Nifty 51.6% vs 52.3% (perm-p 0.11); gold 48.8% vs 54.6%; silver 49.7% vs 52.5%', 'Day-lord rule 49.8% (n 2,808); carry-over 47%; Saturn→Mercury retrace 70.6% vs 68.8% base; his date candles follow through 52–60% vs 57.5% for any candle'],
  ['Survives correction', '0 of 6,912 variants', '0 of 11 rules on either index', '0 of 32 rules, any instrument', '0 of ~45 daily / candle tests; 1 transit rule (Mars vs Saturn\'s sign, p ≈ 0.01 on n = 11)'],
  ['Second check', 'BankNifty 47.1% (z −2.85) — the Nifty winner vanishes', 'Bank Nifty agrees: nothing beyond chance size', '"Observed" calls = extrapolated calls; both below benchmark', 'Mars-vs-Saturn repeats on Nifty Metal (−4.0% / +8.2%) and in both halves; Sun→Uttarashadha "95%" week holds the low 6 of 16'],
  ['Verdict', 'No directional edge', 'No rule clears a fair bar', 'No directional edge', 'No edge in the daily or date-candle rules; one transit lead (n = 11) for a forward ledger'],
]

const LEADS: [string, string, string, string, string][] = [
  ['Mars in Saturn\'s sign → Nifty up over the transit', 'Vikas (his metals rule)', '+7.5% mean, 11/11 spans up vs 65% base, p=0.01', '+8.6% / +6.7%', 'holds in both halves and on Nifty Metal (+8.2%); n=11, one span every ~18 months'],
  ['Mars in the sign before Saturn\'s → Nifty down', 'Vikas', '−5.2% mean, 8/11 down vs 35% base, p=0.02', '+0.9% / −10.3%', 'median −3.4%; even-sign Saturn −10.8% vs odd +1.4% (as he says); 2020 is the mean; gold does not show it'],
  ['Moon in Mula → gold up', 'Saptarsh (his call)', '66.7%, n=102, p=0.010', '66.0% / 67.3%', 'holds in both halves — the only rule of his that does'],
  ['Moon in Jyeshtha → gold down', 'Saptarsh (he says "volatile")', '36.0% up, n=100, p=0.0004', '32.0% / 40.0%', 'holds and clears correction — but not a direction he gave'],
  ['Vishti karana → Nifty down', 'Saptarsh', '41.5% up, n=537, p=0.014', 'z −0.4 / z −3.1', 'second half only — unstable'],
  ['Amavasya → silver up', 'Saptarsh', '66.4%, n=107, p=0.005', '77% / 56%', 'decays to nothing after 2020'],
  ['Saturn-star days close down', 'Vikas (his rule says up)', '58.4% down, n=406, p=0.001', '57.6% / 59.1%', 'one of 9 lords; the opposite of his reading — study, not a rule'],
  ['Moon at 45/135/225/315° (tropical) at open → breakout follows', 'Vikas', '64% vs 57.5%, n=281, p=0.03', '—', 'one of ~25 candle families; sidereal version 55%'],
  ['Mars–Jupiter semisquare → up 5 days', 'Gann ("lean")', '+126 bp Nifty (p 0.07), +203 bp Bank Nifty (p 0.03), n=17', '—', 'one of 22 rule × index tests — watch'],
  ['Mercury–Saturn conjunction flip', 'Gann', 'archive 70%; repo 58% vs 49%, n=19, p=0.50', '—', 'does not replicate; forward call failed'],
]

function pct(x: number) { return `${(x * 100).toFixed(0)}%` }

export default function StrategyPanel({ date }: { date?: string }) {
  const [vol, setVol] = useState<VolatilityResult | null>(null)
  const [volErr, setVolErr] = useState<string | null>(null)
  const [today, setToday] = useState<SaptarshDay | null>(null)
  const [vikas, setVikas] = useState<VikasDay | null>(null)

  useEffect(() => {
    volatility().then(setVol).catch((e: Error) => setVolErr(e.message))
  }, [])
  useEffect(() => {
    setToday(null)
    setVikas(null)
    saptarshWeek(date, 1).then((w) => setToday(w.days[0])).catch(() => setToday(null))
    vikasWeek(date, 1).then((w) => setVikas(w.days[0])).catch(() => setVikas(null))
  }, [date])

  const iv90 = vol?.intervals['0.90']
  const goldStar = today?.moon.nakshatra
  const goldLead = goldStar === 'Mula' ? 'lean long gold (Mula)'
    : goldStar === 'Jyeshtha' ? 'lean short gold (Jyeshtha)' : null
  const marsRule = vikas?.events.find((e) => e.family === 'mars_sign'
    && (e.key.startsWith('12th_from_saturn') || e.key === 'with_saturn'))

  return (
    <>
      <section className="panel">
        <h2>Today — what the app can honestly tell you</h2>
        <div className="sap-regime">
          <p><span className="learn-key">1 · Size</span>{' '}
            {volErr && <span className="muted-note">volatility model unavailable: {volErr}</span>}
            {!vol && !volErr && 'loading the volatility band…'}
            {vol && iv90 && (
              <>
                Nifty next session: <strong>{vol.band_label.toUpperCase()}</strong>{' '}
                (P wider than usual {pct(vol.p_wide)}). 90% band ±{iv90.half_width_points} pts →{' '}
                {iv90.low.toFixed(0)} – {iv90.high.toFixed(0)}, holds {iv90.realised_coverage.toFixed(0)}% of
                the time out-of-sample.{' '}
                {vol.source === 'published' && vol.age_hours !== null && (
                  <span className="muted-note">(published {vol.age_hours.toFixed(0)} h ago — no live prices from this host)</span>
                )}
              </>
            )}
          </p>
          <p><span className="learn-key">2 · Direction</span>{' '}
            from your technical levels — none of the four methods beat the majority side.
            {today && (
              <> Today's astrological calls, for the record: Nifty {today.calls.nifty.tone},
                gold {today.calls.gold.tone}, silver {today.calls.silver.tone} (Moon in {today.moon.nakshatra}
                {today.mercury?.retrograde ? ', Mercury retrograde' : ''}).</>
            )}
          </p>
          <p><span className="learn-key">3 · Gold tie-breaker</span>{' '}
            {goldLead
              ? <>Moon is in {goldStar} today — the one replicated lead says <strong>{goldLead}</strong>, as a tie-breaker on a technical setup only, with a stop.</>
              : <>Moon is in {goldStar ?? '…'} — neither Mula nor Jyeshtha, so no gold lead today.</>}
          </p>
          <p><span className="learn-key">4 · Vikas dates</span>{' '}
            {vikas
              ? <>
                  {vikas.star_date
                    ? <>Moon in {vikas.star.nakshatra} ({vikas.star.lord} star) — a <strong>{vikas.star_date}</strong> date: mark today's candle, trade the cross, not the guess. </>
                    : <>Moon in {vikas.star.nakshatra} ({vikas.star.lord}) — not one of his star dates. </>}
                  {vikas.events.length > 0 && <>Events today: {vikas.events.map((e) => e.label).join(', ')}. </>}
                  {marsRule && <><strong>{marsRule.note}</strong> — the one Vikas lead with a split-sample record (n = 11). </>}
                  {vikas.events.length === 0 && !vikas.star_date && 'No event date. '}
                  <span className="muted-note">(Dates only; the backtest gave his date candles no edge over any other candle.)</span>
                </>
              : 'loading…'}
          </p>
          <p className="muted-note">
            Everything else the app shows (chain, horai, Gann events, Vishti, Amavasya, Rahu Kaal,
            stellia, Kaal Sarp, Mercury ℞, day-lords …) is study material. The table below is why.
          </p>
        </div>
      </section>

      <section className="panel">
        <h2>Four methods, one verdict</h2>
        <table className="graha-table learn-table">
          <thead><tr><th></th><th>Options Mersal (Prediction tab)</th><th>Gann cosmogram</th><th>Saptarsh Insight</th><th>Vikas dates</th></tr></thead>
          <tbody>
            {ROWS.map(([k, a, b, c, d]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Each was scored against the trivial benchmark on its own traded days and corrected for
          the number of rules tried. Full write-ups: <code>STRATEGY.md</code>,{' '}
          <code>backend/knowledge/backtest/opt/OPTIMISATION.md</code>,{' '}
          <code>backend/knowledge/backtest/saptarsh/RESULTS.md</code>,{' '}
          <code>backend/knowledge/backtest/vikas/RESULTS.md</code>,{' '}
          <code>backend/knowledge/backtest/gann/RESULTS.md</code>.
        </p>

        <h3 className="gann-h3">The one thing that works — and it isn't astrology</h3>
        <p className="learn-p">
          The volatility model (six recent-range features, no astrology) calls whether the session
          will be wider or narrower than its median move about <strong>60%</strong> of the time
          out-of-sample, and its 90% band holds ~91%. It says nothing about direction. Adding any
          panchang or chain feature made it significantly worse (−5.05 pp Nifty, −4.09 pp BankNifty,
          p &lt; 0.001).
        </p>

        <h3 className="gann-h3">Leads that survived a split-sample check</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Lead</th><th>Method</th><th>Whole window</th><th>Halves</th><th>Reading</th></tr></thead>
          <tbody>
            {LEADS.map(([k, m, w, h, r]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{m}</td><td>{w}</td><td>{h}</td><td>{r}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">The combined recipe</h3>
        <ol className="learn-ol">
          <li><strong>Size with the volatility band, never direct with astrology.</strong> Wide day → smaller size, wider stop; narrow day → don't expect a trend.</li>
          <li><strong>Direction from technical levels.</strong> All four sources say so themselves; the backtests say it louder. Vikas's dates can tell you <em>which</em> candle to mark — they cannot tell you which way it breaks, and the backtest says the break itself is no more reliable than on any other day.</li>
          <li><strong>One optional tie-breaker:</strong> Moon in Mula (lean long gold) / Jyeshtha (lean short gold) — ~100-day samples on one instrument; use only on top of a setup, with a stop.</li>
          <li><strong>One positional lean to ledger, not to trade yet:</strong> Mars entering Saturn's sign → Nifty / metals up for the transit (11 of 11 since 2011); Mars in the sign before Saturn's → down (8 of 11). Eleven spans is too few — record the next two before sizing anything on it.</li>
          <li><strong>Ignore the rest for trading; keep it for study.</strong> The Saptarsh leads that looked best are regime-dependent; every Vikas daily rule scored at base rate.</li>
          <li><strong>Keep the ledger.</strong> Score the band, the two gold leads and the Mars–Saturn lean forward for a year before believing any of them.</li>
        </ol>
      </section>
    </>
  )
}
