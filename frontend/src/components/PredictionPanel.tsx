import type { Prediction } from '../types'

const SECTION_TITLES: Record<string, string> = {
  graph: 'Intraday graph (09:15–15:30)',
  weekly: 'Weekly',
  monthly: 'Monthly',
  long_term: 'Long term',
  prasanam: 'Prasanam',
}

export default function PredictionPanel({ prediction }: { prediction: Prediction }) {
  const sections = prediction.sections ?? {}
  const hasFindings = Object.keys(sections).length > 0

  return (
    <div className="prediction-panel">
      {!hasFindings && (
        <ul>
          {prediction.summary.map((line, i) => (
            <li key={i}>{line}</li>
          ))}
        </ul>
      )}
      {Object.entries(sections).map(([key, findings]) => (
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
      ))}
      <div className="prediction-note">{prediction.note}</div>
    </div>
  )
}
