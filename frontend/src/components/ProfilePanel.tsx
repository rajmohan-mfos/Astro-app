// My profile (kundali): birth details saved in localStorage, plus the
// teacher's own-horoscope gochara check — transit Moon in 5/8/12 from the
// janma rasi means "do not trade today".
import { useEffect, useState } from 'react'
import { canTrade } from '../api'
import type { CanTradeResult } from '../types'
import { PLACES } from './InputPanel'

const STORAGE_KEY = 'astro-app-profile'

export interface BirthProfile {
  year: number
  month: number
  day: number
  hour: number
  minute: number
  tz_offset: number
  lat: number
  lon: number
}

export function loadProfile(): BirthProfile | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as BirthProfile) : null
  } catch {
    return null
  }
}

interface Props {
  chartDate: { year: number; month: number; day: number; tz_offset: number } | null
}

export default function ProfilePanel({ chartDate }: Props) {
  const [profile, setProfile] = useState<BirthProfile | null>(loadProfile)
  const [editing, setEditing] = useState(profile === null)
  const [check, setCheck] = useState<CanTradeResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [day, setDay] = useState(profile ? String(profile.day) : '1')
  const [month, setMonth] = useState(profile ? String(profile.month) : '1')
  const [year, setYear] = useState(profile ? String(profile.year) : '1990')
  const [hour, setHour] = useState(profile ? String(profile.hour) : '6')
  const [minute, setMinute] = useState(profile ? String(profile.minute) : '0')
  const [place, setPlace] = useState('Chennai')
  const [lat, setLat] = useState(profile ? String(profile.lat) : '13.0827')
  const [lon, setLon] = useState(profile ? String(profile.lon) : '80.2707')

  useEffect(() => {
    if (!profile || !chartDate) {
      setCheck(null)
      return
    }
    setError(null)
    canTrade(profile, chartDate)
      .then(setCheck)
      .catch((e: Error) => setError(e.message))
  }, [profile, chartDate?.year, chartDate?.month, chartDate?.day])

  const save = (e: React.FormEvent) => {
    e.preventDefault()
    const p: BirthProfile = {
      year: Number(year), month: Number(month), day: Number(day),
      hour: Number(hour), minute: Number(minute),
      tz_offset: 5.5, lat: Number(lat), lon: Number(lon),
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(p))
    setProfile(p)
    setEditing(false)
  }

  const selectPlace = (name: string) => {
    setPlace(name)
    const p = PLACES.find((p) => p.name === name)
    if (p) {
      setLat(String(p.lat))
      setLon(String(p.lon))
    }
  }

  return (
    <div className="panel input-panel profile-panel">
      <h2>My profile — can I trade?</h2>

      {!editing && profile && (
        <>
          <div className="profile-summary">
            Born {profile.year}-{String(profile.month).padStart(2, '0')}-
            {String(profile.day).padStart(2, '0')}{' '}
            {String(profile.hour).padStart(2, '0')}:
            {String(profile.minute).padStart(2, '0')}
            <button className="link-btn" onClick={() => setEditing(true)}>
              edit
            </button>
          </div>
          {check && (
            <div className={`trade-verdict verdict-${check.verdict.toLowerCase()}`}>
              <div className="verdict-label">{check.verdict}</div>
              <div className="verdict-detail">
                Janma rasi {check.birth_rasi.ta} · Moon at sunrise
                {check.cast ? ` (${check.cast})` : ''} in{' '}
                {check.transit_rasi.ta} ({check.count} from your rasi)
                {check.rasi_until !== '—' && (
                  <> · leaves this rasi {check.rasi_until}</>
                )}
              </div>
              <div className="verdict-note">{check.note}</div>
            </div>
          )}
          {error && <div className="error-box">{error}</div>}
        </>
      )}

      {editing && (
        <form onSubmit={save}>
          <div className="row">
            <div>
              <label htmlFor="pf-day">Day</label>
              <input id="pf-day" value={day} onChange={(e) => setDay(e.target.value)}
                inputMode="numeric" />
            </div>
            <div>
              <label htmlFor="pf-month">Month</label>
              <input id="pf-month" value={month} onChange={(e) => setMonth(e.target.value)}
                inputMode="numeric" />
            </div>
            <div>
              <label htmlFor="pf-year">Year</label>
              <input id="pf-year" value={year} onChange={(e) => setYear(e.target.value)}
                inputMode="numeric" />
            </div>
          </div>
          <div className="row">
            <div>
              <label htmlFor="pf-hour">Birth hour</label>
              <input id="pf-hour" value={hour} onChange={(e) => setHour(e.target.value)}
                inputMode="numeric" />
            </div>
            <div>
              <label htmlFor="pf-minute">Minute</label>
              <input id="pf-minute" value={minute} onChange={(e) => setMinute(e.target.value)}
                inputMode="numeric" />
            </div>
          </div>
          <div className="row">
            <div>
              <label htmlFor="pf-place">Birth place</label>
              <select id="pf-place" value={place}
                onChange={(e) => selectPlace(e.target.value)}>
                {PLACES.map((p) => (
                  <option key={p.name} value={p.name}>{p.name}</option>
                ))}
                <option value="Custom">Custom…</option>
              </select>
            </div>
          </div>
          {place === 'Custom' && (
            <div className="row">
              <div>
                <label htmlFor="pf-lat">Latitude</label>
                <input id="pf-lat" value={lat} onChange={(e) => setLat(e.target.value)}
                  inputMode="decimal" />
              </div>
              <div>
                <label htmlFor="pf-lon">Longitude</label>
                <input id="pf-lon" value={lon} onChange={(e) => setLon(e.target.value)}
                  inputMode="decimal" />
              </div>
            </div>
          )}
          <button className="compute-btn" type="submit">Save profile</button>
        </form>
      )}
    </div>
  )
}
