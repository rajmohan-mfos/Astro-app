import { useEffect, useState } from 'react'
import { saptarshWeek, volatility } from '../api'
import type { SaptarshDay, VolatilityResult } from '../types'

// The opening tab. Everything the three backtests agreed on, in one
// place, and the only component with measured skill (session width)
// shown live. Numbers are copied from STRATEGY.md and the three result
// files; the doc is the source of truth, this is its dashboard.

const ROWS: [string, string, string, string][] = [
  ['Predicts', 'Nifty session direction (sunrise chain, panchang tally, horai)', 'Reversals / swings at dated aspects and stations', 'Nifty session; gold & silver daily direction; intraday windows'],
  ['Tested on', 'Nifty 2011–2026, walk-forward (3,830 bars); BankNifty', 'Nifty 2007–2026, every exact event of 11 rules', 'Nifty, COMEX gold & silver 2016–2026 (~2,650 days each)'],
  ['Must beat', 'Always-down on its own days: 53.0%', 'Trend flips on any day: 49%; within ±2 days: 85%', 'Majority side on its own days: 52.3% / 54.6% / 52.5%'],
  ['Headline', 'Engine 48.9% (z −4.2, worse than always-down); best nested walk-forward 53.95% (z +0.5)', 'Best rule 54% vs 43% on 26 trades (n.s.); Mercury–Saturn 70% vs 49% (p 0.038, 1 of ~25 tests)', 'Nifty 51.6% vs 52.3% (perm-p 0.11); gold 48.8% vs 54.6%; silver 49.7% vs 52.5%'],
  ['Survives correction', '0 of 6,912 variants', '0 of 11 rules', '0 of 32 rules, any instrument'],
  ['Second check', 'BankNifty 47.1% (z −2.85) — the Nifty winner vanishes', '—', '"Observed" calls = extrapolated calls; both below benchmark'],
  ['Verdict', 'No directional edge', 'No rule clears a fair bar', 'No directional edge'],
]

const LEADS: [string, string, string, string, string][] = [
  ['Moon in Mula → gold up', 'Saptarsh (his call)', '66.7%, n=102, p=0.010', '66.0% / 67.3%', 'holds in both halves — the only rule of his that does'],
  ['Moon in Jyeshtha → gold down', 'Saptarsh (he says "volatile")', '36.0% up, n=100, p=0.0004', '32.0% / 40.0%', 'holds and clears correction — but not a direction he gave'],
  ['Vishti karana → Nifty down', 'Saptarsh', '41.5% up, n=537, p=0.014', 'z −0.4 / z −3.1', 'second half only — unstable'],
  ['Amavasya → silver up', 'Saptarsh', '66.4%, n=107, p=0.005', '77% / 56%', 'decays to nothing after 2020'],
  ['Mercury–Saturn conjunction flip', 'Gann', '70% vs 49%, n=23, p=0.038', '—', 'one expected false positive in 25; forward call failed'],
]

function pct(x: number) { return `${(x * 100).toFixed(0)}%` }

export default function StrategyPanel({ date }: { date?: string }) {
  const [vol, setVol] = useState<VolatilityResult | null>(null)
  const [volErr, setVolErr] = useState<string | null>(null)
  const [today, setToday] = useState<SaptarshDay | null>(null)

  useEffect(() => {
    volatility().then(setVol).catch((e: Error) => setVolErr(e.message))
  }, [])
  useEffect(() => {
    setToday(null)
    saptarshWeek(date, 1).then((w) => setToday(w.days[0])).catch(() => setToday(null))
  }, [date])

  const iv90 = vol?.intervals['0.90']
  const goldStar = today?.moon.nakshatra
  const goldLead = goldStar === 'Mula' ? 'lean long gold (Mula)'
    : goldStar === 'Jyeshtha' ? 'lean short gold (Jyeshtha)' : null

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
            from your technical levels — none of the three methods beat the majority side.
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
          <p className="muted-note">
            Everything else the app shows (chain, horai, Gann events, Vishti, Amavasya, Rahu Kaal,
            stellia, Kaal Sarp, Mercury ℞ …) is study material. The table below is why.
          </p>
        </div>
      </section>

      <section className="panel">
        <h2>Three methods, one verdict</h2>
        <table className="graha-table learn-table">
          <thead><tr><th></th><th>Options Mersal (Prediction tab)</th><th>Gann cosmogram</th><th>Saptarsh Insight</th></tr></thead>
          <tbody>
            {ROWS.map(([k, a, b, c]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{a}</td><td>{b}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Each was scored against the trivial benchmark on its own traded days and corrected for
          the number of rules tried. Full write-ups: <code>STRATEGY.md</code>,{' '}
          <code>backend/knowledge/backtest/opt/OPTIMISATION.md</code>,{' '}
          <code>backend/knowledge/backtest/saptarsh/RESULTS.md</code>, and the Gann tab's evidence lines.
        </p>

        <h3 className="gann-h3">The one thing that works — and it isn't astrology</h3>
        <p className="learn-p">
          The volatility model (six recent-range features, no astrology) calls whether the session
          will be wider or narrower than its median move about <strong>60%</strong> of the time
          out-of-sample, and its 90% band holds ~91%. It says nothing about direction. Adding any
          panchang or chain feature made it significantly worse (−5.05 pp Nifty, −4.09 pp BankNifty,
          p &lt; 0.001).
        </p>

        <h3 className="gann-h3">Leads that survived a split-sample check (2016–20 vs 2021–26)</h3>
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
          <li><strong>Direction from technical levels.</strong> All three sources say so themselves; the backtests say it louder.</li>
          <li><strong>One optional tie-breaker:</strong> Moon in Mula (lean long gold) / Jyeshtha (lean short gold) — ~100-day samples on one instrument; use only on top of a setup, with a stop.</li>
          <li><strong>Ignore the rest for trading; keep it for study.</strong> The two Saptarsh leads that looked best are regime-dependent.</li>
          <li><strong>Keep the ledger.</strong> Score the band and the two gold leads forward for a year before believing either.</li>
        </ol>
      </section>
    </>
  )
}
