import { useState } from 'react'
import { prasanam } from '../api'
import type { ComputeRequest, PrasanamResult, RuleFinding } from '../types'

/** The taught prasanam: hold the question in mind, think of a number
 *  1–249, and let that number choose the chart. */
export default function PrasanamPanel({
  request, autoFindings,
}: {
  request: ComputeRequest | null
  autoFindings: RuleFinding[]
}) {
  const [number, setNumber] = useState('')
  const [result, setResult] = useState<PrasanamResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const cast = () => {
    if (!request) return
    const n = Number(number)
    if (!Number.isInteger(n) || n < 1 || n > 249) {
      setError('Pick a whole number between 1 and 249.')
      return
    }
    setBusy(true)
    setError(null)
    prasanam(request, n)
      .then(setResult)
      .catch((e: Error) => setError(e.message))
      .finally(() => setBusy(false))
  }

  return (
    <div className="prasanam-panel">
      <div className="prasanam-ask">
        <p className="prasanam-how">
          Ask <strong>one exact question</strong> — one instrument, one
          direction, an explicit target and horizon. Then close your eyes,
          hold the question in mind, and think of a number from 1 to 249.
          The number chooses the ascendant; the planets are taken for the
          moment you ask.
        </p>
        <div className="prasanam-row">
          <label htmlFor="horary">Horary number</label>
          <input id="horary" type="number" min={1} max={249}
            value={number} placeholder="1–249"
            onChange={(e) => setNumber(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') cast() }} />
          <button onClick={cast} disabled={busy || !request}>
            {busy ? 'Casting…' : 'Cast prasanam'}
          </button>
        </div>
        {error && <div className="error-box">{error}</div>}
      </div>

      {result && (
        <div className="finding-section">
          {result.findings.map((f, i) => (
            <div key={i} className="finding">
              <div className="finding-title">{f.title}</div>
              <div className="finding-detail">{f.detail}</div>
              <div className="finding-source">{f.source}</div>
            </div>
          ))}
          <div className="prediction-note">{result.note}</div>
        </div>
      )}

      {!result && autoFindings.length > 0 && (
        <div className="finding-section">
          {autoFindings.map((f, i) => (
            <div key={i} className="finding">
              <div className="finding-title">{f.title}</div>
              <div className="finding-detail">{f.detail}</div>
              <div className="finding-source">{f.source}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
