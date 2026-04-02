import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { BracketMatch } from '../../types/models'

export default function BracketPage() {
  const { id } = useParams<{ id: string }>()
  const [matches, setMatches] = useState<BracketMatch[]>([])
  const [size, setSize] = useState(8)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get<BracketMatch[]>(`/tournaments/${id}/bracket`).then(setMatches).catch(() => {})
  }, [id])

  const generate = async () => {
    try {
      setError('')
      const m = await api.post<BracketMatch[]>(`/tournaments/${id}/bracket`, { size })
      setMatches(m)
    } catch (e) { setError(e instanceof Error ? e.message : "Unknown error") }
  }

  const grouped = matches.reduce<Record<string, BracketMatch[]>>((acc, m) => {
    const key = m.elim_level || `Round ${m.round_number}`
    ;(acc[key] ??= []).push(m)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/tournaments/${id}`} className="text-sm text-blue-600 hover:underline">&larr; Back</Link>
        <h1 className="text-2xl font-bold text-slate-900">Elimination Bracket</h1>
      </div>

      {error && <p className="text-red-600 text-sm bg-red-50 p-2 rounded">{error}</p>}

      {matches.length === 0 && (
        <div className="bg-white shadow rounded-lg p-4 flex gap-3 items-end">
          <label className="flex flex-col text-sm">
            Bracket Size
            <select className="border rounded px-2 py-1 mt-1" value={size} onChange={e => setSize(+e.target.value)}>
              <option value={8}>Top 8</option>
              <option value={16}>Top 16</option>
              <option value={32}>Top 32</option>
            </select>
          </label>
          <button onClick={generate}
            className="bg-emerald-600 text-white px-4 py-1.5 rounded text-sm hover:bg-emerald-500">
            Generate Bracket
          </button>
        </div>
      )}

      {Object.entries(grouped).map(([level, ms]) => (
        <div key={level}>
          <h2 className="text-lg font-semibold text-slate-700 capitalize mb-2">{level.replace('_', ' ')}</h2>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {ms.map(m => (
              <div key={m.pairing_id} className="bg-white shadow rounded-lg p-3 text-sm">
                <div className="flex justify-between">
                  <span className="font-medium">{m.petitioner_team_code || 'TBD'}</span>
                  <span className="text-slate-400">vs</span>
                  <span className="font-medium">{m.respondent_team_code || 'TBD'}</span>
                </div>
                <p className={`text-xs mt-1 capitalize ${
                  m.status === 'completed' ? 'text-emerald-600' : 'text-slate-400'
                }`}>{m.status}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
