// Aggregate day score — the four panchang elements combined with the
// chain, per Class 3 ("combine with whole concept"). Conviction is
// gated by the panchang, never by the chain alone.
import type { DayScore } from '../types'

const LABELS: Record<string, string> = {
  thithi: 'Thithi', karanam: 'Karanam', yogam: 'Yogam',
  nakshatra: 'Natchathiram',
}

export default function DayScoreBar({ score }: { score: DayScore }) {
  const parts = Object.entries(score.parts)
  return (
    <div className={`day-score conviction-${score.conviction}`}>
      <div className="day-score-head">
        <span className="day-score-conviction">
          {score.conviction} conviction
        </span>
        <span className="day-score-sub">
          panchang {score.panchang_total > 0 ? '+' : ''}
          {score.panchang_total} ({score.panchang_sign}) · chain{' '}
          {score.chain_score > 0 ? '+' : ''}
          {score.chain_score} ({score.chain_sign}) · {score.agreement}
        </span>
      </div>
      <div className="day-score-parts">
        {parts.map(([k, v]) => (
          <span key={k} className={
            v > 0 ? 'part-pos' : v < 0 ? 'part-neg' : 'part-zero'}>
            {LABELS[k] ?? k} {v > 0 ? '+' : ''}{v}
          </span>
        ))}
        {score.amplified && (
          <span className="part-amp">×1.5 {score.star_lord} amplifies</span>
        )}
        {score.chidra && (
          <span className="part-neg">Paksha Chidra — reduced</span>
        )}
      </div>
    </div>
  )
}
