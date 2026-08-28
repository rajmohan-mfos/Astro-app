import { useEffect, useState } from 'react'
import { saptarshWeek } from '../api'
import type {
  SaptarshDay, SaptarshTone, SaptarshWeekResult,
} from '../types'

// One entry per calendar day in the Gann-calendar shape: a headline,
// the three instrument chips, a "For the market" line in the channel's
// voice, the in-session timers, and an expandable detail block. Every
// call carries its source badge — "observed" means the channel wrote
// that exact call in Aug 2026, "extrapolated" means the app filled it
// in by rule and it has never been seen in their output.

const TONE_CHIP: Record<SaptarshTone, string> = {
  bull: 'bias-bullish', bear: 'bias-bearish', vol: 'bias-reversal',
  neutral: 'bias-neutral',
}
const TONE_LABEL: Record<SaptarshTone, string> = {
  bull: '▲ Bullish', bear: '▼ Bearish', vol: '⇅ Volatile', neutral: '— Neutral',
}
const INSTRUMENTS = ['nifty', 'gold', 'silver'] as const
const INST_NAME = { nifty: 'Nifty', gold: 'Gold', silver: 'Silver' }

function DayRow({ d, today }: { d: SaptarshDay; today: string }) {
  const [open, setOpen] = useState(false)
  const live = d.aspects.filter((a) => a.in_session)
  const moonLine = `Moon in ${d.moon.sign} · ${d.moon.nakshatra}`
    + (d.moon.sign_change ? ` → ${d.moon.sign_change.to} ${d.moon.sign_change.time}` : '')
    + (d.moon.nakshatra_change
      ? ` → ${d.moon.nakshatra_change.to} ${d.moon.nakshatra_change.time}` : '')
  return (
    <li className={'gann-event' + (d.date === today ? ' today' : '')
      + (d.closed ? ' sap-closed' : '')}>
      <div className="gann-event-head" onClick={() => setOpen(!open)}>
        <span className="gann-date">{d.date} · {d.weekday.slice(0, 3)}
          {d.date === today && <span className="gann-today-chip">today</span>}
        </span>
        <span className="gann-title">{moonLine}</span>
      </div>
      <div className="sap-line">
        {INSTRUMENTS.map((k) => (
          <span className="sap-inst" key={k}>
            <span className="sap-name">{INST_NAME[k]}</span>
            <span className={`bias-chip ${TONE_CHIP[d.calls[k].tone]}`}>
              {TONE_LABEL[d.calls[k].tone]}
            </span>
            <span className={`src-badge src-${d.calls[k].source}`}>
              {d.calls[k].source}
            </span>
          </span>
        ))}
      </div>
      {d.closed
        ? <div className="gann-note">{d.closed} — market closed; the
            sky is shown for study only.</div>
        : <div className="gann-market">For the market: {d.calls.nifty.text}</div>}
      {!d.closed && (
        <>
          <p className="sap-line"><span className="sap-k">Gold</span>
            {d.calls.gold.why[0]}{d.calls.gold.why.length > 1
              ? ` · ${d.calls.gold.why.slice(1).join(' · ')}` : ''}</p>
          <p className="sap-line"><span className="sap-k">Silver</span>
            {d.calls.silver.why[0]}{d.calls.silver.why.length > 1
              ? ` · ${d.calls.silver.why.slice(1).join(' · ')}` : ''}</p>
        </>
      )}
      <div className="gann-detail">
        {live.length > 0
          ? 'Session timers: ' + live.map((a) =>
            `${a.time} ${a.a} ${a.angle} ${a.b} (${a.tone})`).join(' · ')
          : 'No exact aspect inside the session'}
        {' · '}Rahu Kaal {d.kaal.rahu_kaal[0]}–{d.kaal.rahu_kaal[1]}
        {d.eclipse ? ` · ${d.eclipse}` : ''}
      </div>
      {open && (
        <div className="gann-expand">
          <div className="sap-windows">
            {d.windows.map((w, i) => (
              <span key={i} className={`sap-win t-${w.tone}`}
                title={w.driver}>{w.start}–{w.end} {w.tone}</span>
            ))}
          </div>
          <p><strong>Panchang:</strong> {d.panchang.tithi} ends {d.panchang.tithi_ends ?? '—'}
            {' · '}{d.moon.nakshatra} ends {d.panchang.nakshatra_ends ?? '—'}
            {' · '}{d.panchang.yoga} yoga ends {d.panchang.yoga_ends ?? '—'}
            {' · '}karana {d.panchang.karanas.map((k) =>
              `${k.name}${k.ends ? ` (ends ${k.ends})` : ''}`).join(', ')}</p>
          <p><strong>Kaal:</strong> sunrise {d.kaal.sunrise} · sunset {d.kaal.sunset}
            {' · '}Yamaganda {d.kaal.yamaganda[0]}–{d.kaal.yamaganda[1]}
            {' · '}Gulika {d.kaal.gulika_kaal[0]}–{d.kaal.gulika_kaal[1]}
            {' · '}Abhijit {d.kaal.abhijit[0]}–{d.kaal.abhijit[1]}</p>
          <p><strong>All aspects (IST):</strong> {d.aspects.length === 0 ? 'none' :
            d.aspects.map((a) =>
              `${a.time} ${a.a} ${a.angle} ${a.b} — ${a.tone}${a.source === 'extrapolated' ? '*' : ''}`
            ).join(' · ')}</p>
          {d.flags.length > 0 && <p><strong>Flags:</strong> {d.flags.join(' ')}</p>}
          <p><strong>Nifty reasoning:</strong> {d.calls.nifty.why.join(' · ')}</p>
          <p className="gann-source">* extrapolated by rule — never seen in the channel's output</p>
        </div>
      )}
    </li>
  )
}

export default function SaptarshWeek({ date }: { date?: string }) {
  const [data, setData] = useState<SaptarshWeekResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setData(null)
    setError(null)
    saptarshWeek(date).then(setData).catch((e: Error) => setError(e.message))
  }, [date])

  if (error) return <section className="panel"><p className="muted-note">
    Week outlook failed: {error}</p></section>
  if (!data) return <div className="loading">Computing the week…</div>

  const today = data.start
  return (
    <section className="panel">
      <h2>Next 1 week — Nifty · Gold · Silver</h2>
      <p className="muted-note">
        Rebuilt in the channel's own shape from the sky alone: Moon sign +
        nakshatra during 09:15–15:30 with change times, Vishti / Vaidhriti
        / Vyatipata, Rahu Kaal, every exact aspect at their eight angles,
        and eclipse days. Click a day for its windows, panchang end-times
        and full aspect list.
      </p>
      <div className="gann-legend">
        <span className="src-badge src-observed">observed</span> = the
        channel wrote this exact call in Aug 2026.{' '}
        <span className="src-badge src-extrapolated">extrapolated</span> =
        filled in by nakshatra-lord / aspect-family rule, never seen in
        their output.
      </div>
      <h3 className="gann-h3">Upcoming — {data.start} to {data.end}</h3>
      <ul className="gann-list">
        {data.days.map((d) => <DayRow key={d.date} d={d} today={today} />)}
      </ul>
      <p className="muted-note">{data.note}</p>
    </section>
  )
}
