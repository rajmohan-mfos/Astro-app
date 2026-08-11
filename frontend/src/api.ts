import type { CanTradeResult, ComputeRequest, ComputeResult } from './types'

export async function canTrade(
  birth: ComputeRequest,
  on: { year: number; month: number; day: number; tz_offset: number },
): Promise<CanTradeResult> {
  const res = await fetch('/api/can-trade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ birth, ...on }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

// /api/panchang-chart = /api/compute plus the KP day-chart tables (`kp`)
export async function compute(req: ComputeRequest): Promise<ComputeResult> {
  const res = await fetch('/api/panchang-chart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export async function health(): Promise<{ ok: boolean }> {
  const res = await fetch('/api/health')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
