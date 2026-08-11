// The X / X1 / Y / Y1 chain, shown the way the teacher's slides do:
// an overridden X/Y is struck out ("X1 COME MEANS X DNT WORK") and the
// FINAL pair is highlighted.
import type { PredictionChain } from '../types'

function Var({ label, v, overridden, final }: {
  label: string
  v: { planet: string; count: number } | null
  overridden?: boolean
  final?: boolean
}) {
  if (!v) {
    return (
      <div className="chain-var chain-var-empty">
        <span className="chain-var-label">{label}</span>
        <span className="chain-var-value">—</span>
      </div>
    )
  }
  return (
    <div className={'chain-var' + (overridden ? ' chain-var-struck' : '')
      + (final ? ' chain-var-final' : '')}>
      <span className="chain-var-label">{label}</span>
      <span className="chain-var-value">{v.planet}({v.count})</span>
    </div>
  )
}

export default function ChainVariables({ chain }: { chain: PredictionChain }) {
  const xOverridden = chain.x1 !== null
  const yOverridden = chain.y1 !== null
  return (
    <div className="chain-vars">
      <div className="chain-vars-group">
        <Var label="X" v={chain.x} overridden={xOverridden}
          final={!xOverridden} />
        <Var label="X1" v={chain.x1} final={xOverridden} />
      </div>
      <div className="chain-vars-group">
        <Var label="Y" v={chain.y} overridden={yOverridden}
          final={!yOverridden} />
        <Var label="Y1" v={chain.y1} final={yOverridden} />
      </div>
      <div className="chain-vars-note">
        Final: {chain.first} (first half) · {chain.second} (second half)
        {(xOverridden || yOverridden) && ' — "X1 come means X don\'t work"'}
      </div>
    </div>
  )
}
