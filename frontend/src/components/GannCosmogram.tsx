import { useEffect, useState } from 'react'
import { gannCalendar } from '../api'
import type { GannCalendarResult, GannEvent } from '../types'

// The Gann cosmogram calendar (gann-engine-CLAUDE.md). The verdict
// travels with every event on purpose: the course's audit found almost
// every rule at the noise floor, and a rule shown without its
// hit-rate-vs-base-rate quietly becomes a belief.

const VERDICT_LABEL: Record<GannEvent['verdict'], string> = {
  'paper-trade': 'paper-trade',
  lean: 'lean, unproven',
  null: 'no edge',
  rare: 'too rare to test',
  'calendar-trap': 'calendar trap',
}

const BIAS_LABEL: Record<GannEvent['bias'], string> = {
  bullish: '▲ Bullish',
  bearish: '▼ Bearish',
  reversal: '⇅ Reversal',
}

function EventRow({ e, today }: { e: GannEvent; today: string }) {
  const [open, setOpen] = useState(false)
  const when = e.end_date && e.end_date !== e.date
    ? `${e.date} → ${e.end_date}` : e.date
  const isToday = e.date <= today && today <= (e.end_date ?? e.date)
  return (
    <li className={'gann-event' + (e.excluded ? ' excluded' : '')
      + (isToday ? ' today' : '')}>
      <div className="gann-event-head" onClick={() => setOpen(!open)}>
        <span className="gann-date">{when}
          {isToday && <span className="gann-today-chip">today</span>}
        </span>
        <span className="gann-title">{e.title}</span>
        <span className={`bias-chip bias-${e.bias}`}>
          {BIAS_LABEL[e.bias]}
        </span>
        <span className={`verdict-badge v-${e.verdict.replace('paper-trade', 'paper')}`}>
          {VERDICT_LABEL[e.verdict]}
        </span>
      </div>
      <div className="gann-market">
        For the market: {e.bias === 'reversal'
          ? 'flips whatever the trend was in the days before — bullish '
            + 'into the date turns bearish, bearish turns bullish'
          : `${e.bias} (his fixed call for this pair)`}.{' '}
        When: {e.timing.toLowerCase()}.
      </div>
      <div className="gann-detail">{e.detail}
        {e.retro.length > 0 && (
          <span className="gann-retro"> · {e.retro.join(', ')} retrograde
            {e.excluded && ' — excluded by the taught retrograde filter'}
          </span>
        )}
      </div>
      {e.market_note && <div className="gann-note">{e.market_note}</div>}
      {open && (
        <div className="gann-expand">
          <p><strong>Claimed:</strong> {e.direction}</p>
          <p><strong>Measured:</strong> {e.evidence}</p>
          <p className="gann-source">{e.source}</p>
        </div>
      )}
    </li>
  )
}

export default function GannCosmogram({ date }: { date?: string }) {
  const [data, setData] = useState<GannCalendarResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setData(null)
    setError(null)
    gannCalendar(date).then(setData).catch((e: Error) => setError(e.message))
  }, [date])

  if (error) return <section className="panel"><p className="muted-note">
    Cosmogram calendar failed: {error}</p></section>
  if (!data) return <div className="loading">Computing cosmogram…</div>

  const upcoming = data.events.filter((e) => (e.end_date ?? e.date) >= data.center)
  const past = data.events.filter((e) => (e.end_date ?? e.date) < data.center).reverse()

  return (
    <>
      <section className="panel">
        <h2>Gann cosmogram — aspect calendar</h2>
        <p className="muted-note">
          Tropical zodiac (the GannZilla convention), snapshots at 09:15
          IST. Radix: Nifty first trade {data.radix.date} — natal Venus{' '}
          {data.radix.positions['Venus']}°, Mercury{' '}
          {data.radix.positions['Mercury']}°, Mars{' '}
          {data.radix.positions['Mars']}°, Jupiter{' '}
          {data.radix.positions['Jupiter']}°. Click an event for its
          claimed direction and its measured record. Base rates any rule
          must beat: trend flips on {data.base_rates['trend_flip_any_day']}{' '}
          of all days, and within ±2 days of{' '}
          {data.base_rates['trend_flip_within_2_days']} of them.
        </p>
        <div className="gann-legend">
          <span className="bias-chip bias-bullish">▲ Bullish</span> and{' '}
          <span className="bias-chip bias-bearish">▼ Bearish</span> are his
          fixed-direction calls.{' '}
          <span className="bias-chip bias-reversal">⇅ Reversal</span> rules
          flip the prior trend, so their direction depends on how the
          market goes INTO the date — no fixed color exists for them.
        </div>
        <h3 className="gann-h3">Upcoming — {data.center} to {data.end}</h3>
        {upcoming.length === 0 && <p className="muted-note">
          No catalogued aspects in this window.</p>}
        <ul className="gann-list">
          {upcoming.map((e, i) =>
            <EventRow key={`${e.rule_id}-${e.date}-${i}`} e={e}
              today={data.center} />)}
        </ul>
        {past.length > 0 && (
          <>
            <h3 className="gann-h3">Recent — since {data.start}</h3>
            <ul className="gann-list gann-past">
              {past.map((e, i) =>
                <EventRow key={`${e.rule_id}-${e.date}-${i}`} e={e}
                  today={data.center} />)}
            </ul>
          </>
        )}
        <p className="muted-note">{data.note}</p>
      </section>
    </>
  )
}
