import type { Graha, Lagna } from '../types'

interface Props {
  grahas: Graha[]
  lagna: Lagna
}

export default function GrahaTable({ grahas, lagna }: Props) {
  return (
    <table className="graha-table">
      <thead>
        <tr>
          <th>Graha</th>
          <th>Rasi</th>
          <th>Degree</th>
          <th>Retro</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <span className="token-lagna">Lagna</span>
          </td>
          <td>
            {lagna.rasi} <span className="ta">{lagna.rasi_ta}</span>
          </td>
          <td>{lagna.deg_in_sign}</td>
          <td className="retro-no">—</td>
        </tr>
        {grahas.map((g) => (
          <tr key={g.name}>
            <td>
              {g.name} <span className="ta">{g.name_ta}</span>
            </td>
            <td>
              {g.rasi} <span className="ta">{g.rasi_ta}</span>
            </td>
            <td>{g.deg_in_sign}</td>
            <td className={g.retro ? 'retro-yes' : 'retro-no'}>
              {g.retro ? 'R' : '—'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
