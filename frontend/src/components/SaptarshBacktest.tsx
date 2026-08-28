import results from '../saptarsh_backtest.json'

// Renders backend/knowledge/backtest/saptarsh/results.json (copied into
// src/ at build time by scripts/backtest_saptarsh.py's consumer — see the
// README). The numbers are the whole point of the tab: every "observed"
// call above is his; this is what those calls did against prices.

type Score = {
  label: string; n: number; hits: number; rate: number; ci_lo: number; ci_hi: number
  z_vs_base: number; naive?: number; p_binom?: number; perm_p?: number
}
type Event = Score & {
  mean_bp: number; all_mean_bp: number; wide_rate: number; p_binom_vs_base: number
  call?: string; source?: string; hit_rate?: number; p_hit?: number
}
type Inst = {
  days: number; base_up: number; headline: Score[]
  by_year: (Score & { year: string })[]
  nakshatra: Event[]; rules: Event[]; aspects: Event[]
  bonferroni: { tests: number; alpha: number; survivors: number }
}
type Results = { window: [string, string]; instruments: Record<string, Inst> }

const R = results as unknown as Results
const INST = ['nifty', 'gold', 'silver'] as const
const NAME = { nifty: 'Nifty (session, close vs open)', gold: 'Gold (COMEX, close vs prev close)', silver: 'Silver (COMEX, close vs prev close)' }

function pct(x: number) { return `${x.toFixed(1)}%` }
function sig(p: number) { return p < 0.01 ? 'sig-strong' : p < 0.05 ? 'sig-weak' : '' }

export default function SaptarshBacktest() {
  return (
    <section className="panel">
      <h2>Backtest — what his rules actually did, {R.window[0]} → {R.window[1]}</h2>
      <p className="learn-lead">
        The outlook above was run for every day of ten years and scored
        against prices. Nifty is scored on the session (close vs open) because
        the report is a session call; gold and silver on the COMEX bar dated
        the same day, which is the 03:30 → 27:30 IST Globex day the metals
        report covers. <strong>base</strong> = up-rate on the same days;{' '}
        <strong>naive</strong> = what always calling the majority side would
        have scored on exactly those days; <strong>p</strong> = exact binomial
        against 50%; <strong>perm-p</strong> = 2,000-draw moving-block shuffle of
        the returns. None of the rules were tuned on these prices.
      </p>
      <div className="sap-regime">
        <p><span className="learn-key">Verdict</span></p>
        {INST.map((k) => {
          const I = R.instruments[k]
          if (!I) return null
          const f = I.headline[0]
          const obs = I.headline[1]
          const gap = f.rate - (f.naive ?? 0)
          return (
            <p key={k}>
              <strong>{k}</strong>: his call {pct(f.rate)} on {f.n} days vs {pct(f.naive ?? 0)} for
              always calling the majority side ({gap >= 0 ? '+' : ''}{gap.toFixed(1)} pts,
              perm-p {f.perm_p?.toFixed(2)}); "observed" calls alone {pct(obs.rate)} vs{' '}
              {pct(obs.naive ?? 0)}. {I.bonferroni.survivors} of {I.bonferroni.tests} rules survive
              correction.
            </p>
          )
        })}
        <p className="muted-note">
          Read: on none of the three instruments does the method beat the
          trivial benchmark, and the "observed" calls — his own words — do no
          better than the app's extrapolated ones. Individual rows that light
          up below are what a 90-test sweep produces by chance; the one
          star-level result that clears correction (gold in Jyeshtha) is a
          nakshatra he calls "volatile", not a direction he gave.
        </p>
      </div>
      {INST.map((k) => {
        const I = R.instruments[k]
        if (!I) return null
        return (
          <div key={k}>
            <h3 className="gann-h3">{NAME[k]} — {I.days} days, base up-rate {pct(I.base_up)}</h3>
            <table className="graha-table learn-table">
              <thead><tr><th>Test</th><th>n</th><th>hit</th><th>95% CI</th><th>naive</th><th>z</th><th>p</th><th>perm-p</th></tr></thead>
              <tbody>
                {I.headline.map((s) => (
                  <tr key={s.label} className={sig(s.p_binom ?? 1)}>
                    <td className="learn-key">{s.label}</td><td>{s.n}</td><td>{pct(s.rate)}</td>
                    <td>[{s.ci_lo.toFixed(1)}, {s.ci_hi.toFixed(1)}]</td>
                    <td>{s.naive !== undefined ? pct(s.naive) : '—'}</td>
                    <td>{s.z_vs_base >= 0 ? '+' : ''}{s.z_vs_base.toFixed(2)}</td>
                    <td>{(s.p_binom ?? 1).toFixed(3)}</td>
                    <td>{s.perm_p !== undefined ? s.perm_p.toFixed(3) : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="muted-note">
              Per year: {I.by_year.map((y) => `${y.year} ${pct(y.rate)} (n=${y.n})`).join(' · ')}
            </p>
            <details>
              <summary className="gann-h3">Rules as event studies — {I.bonferroni.tests} tests, {I.bonferroni.survivors} survive Bonferroni (α = {I.bonferroni.alpha.toFixed(4)})</summary>
              <table className="graha-table learn-table">
                <thead><tr><th>Rule</th><th>n</th><th>up-rate</th><th>mean (bp)</th><th>all days (bp)</th><th>wide</th><th>z</th><th>p</th></tr></thead>
                <tbody>
                  {I.rules.map((e) => (
                    <tr key={e.label} className={sig(e.p_binom_vs_base)}>
                      <td className="learn-key">{e.label}</td><td>{e.n}</td><td>{pct(e.rate)}</td>
                      <td>{e.mean_bp >= 0 ? '+' : ''}{e.mean_bp.toFixed(1)}</td>
                      <td>{e.all_mean_bp >= 0 ? '+' : ''}{e.all_mean_bp.toFixed(1)}</td>
                      <td>{e.wide_rate.toFixed(0)}%</td>
                      <td>{e.z_vs_base >= 0 ? '+' : ''}{e.z_vs_base.toFixed(2)}</td>
                      <td>{e.p_binom_vs_base.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </details>
            <details>
              <summary className="gann-h3">Moon nakshatra at the open — his call vs the realised up-rate</summary>
              <table className="graha-table learn-table">
                <thead><tr><th>Nakshatra</th><th>his call</th><th>n</th><th>up-rate</th><th>mean (bp)</th><th>z</th><th>p</th></tr></thead>
                <tbody>
                  {I.nakshatra.map((e) => (
                    <tr key={e.label} className={sig(e.p_binom_vs_base)}>
                      <td className="learn-key">{e.label}</td>
                      <td>{e.call} <span className={`src-badge src-${e.source}`}>{e.source}</span></td>
                      <td>{e.n}</td><td>{pct(e.rate)}</td>
                      <td>{e.mean_bp >= 0 ? '+' : ''}{e.mean_bp.toFixed(1)}</td>
                      <td>{e.z_vs_base >= 0 ? '+' : ''}{e.z_vs_base.toFixed(2)}</td>
                      <td>{e.p_binom_vs_base.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </details>
            {I.aspects.length > 0 && (
              <details>
                <summary className="gann-h3">Observed aspect labels — exact on the day, n ≥ 15</summary>
                <table className="graha-table learn-table">
                  <thead><tr><th>Aspect → his label</th><th>n</th><th>label hit</th><th>up-rate</th><th>mean (bp)</th><th>p</th></tr></thead>
                  <tbody>
                    {I.aspects.map((e) => (
                      <tr key={e.label} className={sig(e.p_hit ?? 1)}>
                        <td className="learn-key">{e.label}</td><td>{e.n}</td>
                        <td>{pct(e.hit_rate ?? 0)}</td><td>{pct(e.rate)}</td>
                        <td>{e.mean_bp >= 0 ? '+' : ''}{e.mean_bp.toFixed(1)}</td>
                        <td>{(e.p_hit ?? 1).toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </details>
            )}
          </div>
        )
      })}
      <p className="muted-note">
        Rows tinted amber are p &lt; 0.05, red p &lt; 0.01 — before any
        correction for the number of tests. With ~30 rules × 3 instruments,
        about four or five rows are expected to clear 0.05 by chance alone;
        the Bonferroni line per instrument is the honest count. Source:
        <code> backend/scripts/backtest_saptarsh.py</code>, results in{' '}
        <code>backend/knowledge/backtest/saptarsh/</code>.
      </p>
    </section>
  )
}
