import { useState } from 'react'
import type { Prediction } from '../types'

const SECTION_TITLES: Record<string, string> = {
  graph: 'Intraday graph (09:15–15:30)',
  weekly: 'Weekly',
  monthly: 'Monthly',
  long_term: 'Long term',
  prasanam: 'Prasanam',
}

// tab order; each tab shows one or more sections
const TABS: { key: string; label: string; sections: string[] }[] = [
  { key: 'intraday', label: 'Intraday', sections: ['graph'] },
  { key: 'weekly', label: 'Weekly', sections: ['weekly'] },
  { key: 'monthly', label: 'Monthly', sections: ['monthly'] },
  { key: 'long_term', label: 'Long term', sections: ['long_term'] },
  { key: 'prasanam', label: 'Prasanam', sections: ['prasanam'] },
]

export default function PredictionPanel({ prediction }: { prediction: Prediction }) {
  const sections = prediction.sections ?? {}
  const hasFindings = Object.keys(sections).length > 0

  // only offer tabs that actually carry findings
  const live = TABS.filter((t) =>
    t.sections.some((s) => (sections[s] ?? []).length > 0))
  const [tab, setTab] = useState<string>(live[0]?.key ?? 'intraday')
  const active = live.find((t) => t.key === tab) ?? live[0]

  if (!hasFindings) {
    return (
      <div className="prediction-panel">
        <ul>
          {prediction.summary.map((line, i) => (
            <li key={i}>{line}</li>
          ))}
        </ul>
        <div className="prediction-note">{prediction.note}</div>
      </div>
    )
  }

  return (
    <div className="prediction-panel">
      <div className="view-tabs sub-tabs">
        {live.map((t) => (
          <button key={t.key}
            className={t.key === active?.key ? 'tab active' : 'tab'}
            onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {active?.sections.map((key) => {
        const findings = sections[key] ?? []
        if (findings.length === 0) return null
        return (
          <div key={key} className="finding-section">
            <h3>{SECTION_TITLES[key] ?? key}</h3>
            {findings.map((f, i) => (
              <div key={i} className="finding">
                <div className="finding-title">{f.title}</div>
                <div className="finding-detail">{f.detail}</div>
                <div className="finding-source">{f.source}</div>
              </div>
            ))}
          </div>
        )
      })}
      <div className="prediction-note">{prediction.note}</div>
    </div>
  )
}
