import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { Round } from '../../types/models'

export default function RoundsPage() {
  const { id } = useParams<{ id: string }>()
  const [rounds, setRounds] = useState<Round[]>([])

  useEffect(() => {
    api.get<Round[]>(`/tournaments/${id}/rounds`).then(setRounds)
  }, [id])

  const create = async () => {
    const r = await api.post<Round>(`/tournaments/${id}/rounds`, { round_type: 'preliminary' })
    setRounds(prev => [...prev, r])
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/tournaments/${id}`} className="text-sm text-blue-600 hover:underline">&larr; Back</Link>
        <h1 className="text-2xl font-bold text-slate-900">Rounds</h1>
      </div>

      <button onClick={create}
        className="bg-slate-900 text-white px-4 py-1.5 rounded text-sm hover:bg-slate-700">
        + New Preliminary Round
      </button>

      <div className="space-y-2">
        {rounds.map(r => (
          <Link key={r.id} to={`/tournaments/${id}/rounds/${r.id}`}
            className="bg-white shadow rounded-lg p-4 flex items-center justify-between hover:shadow-md transition-shadow block">
            <div>
              <p className="font-semibold text-slate-900">Round {r.round_number}</p>
              <p className="text-xs text-slate-500 capitalize">{r.round_type}{r.elim_level ? ` - ${r.elim_level}` : ''}</p>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded capitalize ${
              r.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
              r.status === 'in_progress' ? 'bg-amber-100 text-amber-700' :
              'bg-slate-100 text-slate-600'
            }`}>{r.status.replace('_', ' ')}</span>
          </Link>
        ))}
        {rounds.length === 0 && (
          <p className="text-slate-400 text-sm">No rounds yet.</p>
        )}
      </div>
    </div>
  )
}
