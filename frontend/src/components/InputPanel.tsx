import { useState } from 'react'
import type { ComputeRequest } from '../types'

export const PLACES = [
  { name: 'Chennai', lat: 13.0827, lon: 80.2707 },
  { name: 'Bengaluru', lat: 12.9716, lon: 77.5946 },
  { name: 'Madurai', lat: 9.9252, lon: 78.1198 },
  { name: 'Coimbatore', lat: 11.0168, lon: 76.9558 },
  { name: 'Mumbai', lat: 19.076, lon: 72.8777 },
  { name: 'Delhi', lat: 28.6139, lon: 77.209 },
] as const

interface Props {
  onCompute: (req: ComputeRequest) => void
  busy: boolean
  error: string | null
}

export default function InputPanel({ onCompute, busy, error }: Props) {
  const [day, setDay] = useState('1')
  const [month, setMonth] = useState('1')
  const [year, setYear] = useState('1990')
  const [hour, setHour] = useState('12')
  const [minute, setMinute] = useState('0')
  const [place, setPlace] = useState('Chennai')
  const [lat, setLat] = useState('13.0827')
  const [lon, setLon] = useState('80.2707')
  const [tz, setTz] = useState('5.5')

  const custom = place === 'Custom'

  const selectPlace = (name: string) => {
    setPlace(name)
    const p = PLACES.find((p) => p.name === name)
    if (p) {
      setLat(String(p.lat))
      setLon(String(p.lon))
    }
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    onCompute({
      year: Number(year),
      month: Number(month),
      day: Number(day),
      hour: Number(hour),
      minute: Number(minute),
      tz_offset: Number(tz),
      lat: Number(lat),
      lon: Number(lon),
    })
  }

  const goToDate = (d: Date) => {
    setDay(String(d.getDate()))
    setMonth(String(d.getMonth() + 1))
    setYear(String(d.getFullYear()))
    onCompute({
      year: d.getFullYear(),
      month: d.getMonth() + 1,
      day: d.getDate(),
      hour: Number(hour),
      minute: Number(minute),
      tz_offset: Number(tz),
      lat: Number(lat),
      lon: Number(lon),
    })
  }

  const goToday = () => goToDate(new Date())
  const goTomorrow = () => {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    goToDate(d)
  }

  return (
    <form className="panel input-panel" onSubmit={submit}>
      <h2>Input</h2>

      <div className="row">
        <div>
          <label htmlFor="in-day">Day</label>
          <input id="in-day" value={day} onChange={(e) => setDay(e.target.value)}
            inputMode="numeric" />
        </div>
        <div>
          <label htmlFor="in-month">Month</label>
          <input id="in-month" value={month} onChange={(e) => setMonth(e.target.value)}
            inputMode="numeric" />
        </div>
        <div>
          <label htmlFor="in-year">Year</label>
          <input id="in-year" value={year} onChange={(e) => setYear(e.target.value)}
            inputMode="numeric" />
        </div>
      </div>

      <div className="row">
        <div>
          <label htmlFor="in-hour">Hour (0–23)</label>
          <input id="in-hour" value={hour} onChange={(e) => setHour(e.target.value)}
            inputMode="numeric" />
        </div>
        <div>
          <label htmlFor="in-minute">Minute</label>
          <input id="in-minute" value={minute} onChange={(e) => setMinute(e.target.value)}
            inputMode="numeric" />
        </div>
      </div>

      <div className="row">
        <div>
          <label htmlFor="in-place">Place</label>
          <select id="in-place" value={place} onChange={(e) => selectPlace(e.target.value)}>
            {PLACES.map((p) => (
              <option key={p.name} value={p.name}>{p.name}</option>
            ))}
            <option value="Custom">Custom…</option>
          </select>
        </div>
      </div>

      <div className="row">
        <div>
          <label htmlFor="in-lat">Latitude</label>
          <input id="in-lat" value={lat} disabled={!custom}
            onChange={(e) => setLat(e.target.value)} inputMode="decimal" />
        </div>
        <div>
          <label htmlFor="in-lon">Longitude</label>
          <input id="in-lon" value={lon} disabled={!custom}
            onChange={(e) => setLon(e.target.value)} inputMode="decimal" />
        </div>
      </div>

      <div className="row">
        <div>
          <label htmlFor="in-tz">Timezone (hours east of UTC)</label>
          <input id="in-tz" value={tz} onChange={(e) => setTz(e.target.value)}
            inputMode="decimal" />
        </div>
      </div>

      <div className="day-nav-row">
        <button className="today-btn" type="button" disabled={busy}
          onClick={goToday}>
          Today
        </button>
        <button className="today-btn" type="button" disabled={busy}
          onClick={goTomorrow}>
          Tomorrow
        </button>
      </div>
      <button className="compute-btn" type="submit" disabled={busy}>
        {busy ? 'Computing…' : 'Compute'}
      </button>

      {error && <div className="error-box">{error}</div>}
    </form>
  )
}
