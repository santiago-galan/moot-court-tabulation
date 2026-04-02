import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../../api/client'
import { useWebSocket } from '../../hooks/useWebSocket'
import type { RoundDetail } from '../../types/models'

export default function RoundDetailPage() {
  const { tid, rid } = useParams<{ tid: string; rid: string }>()
  const [round, setRound] = useState<RoundDetail | null>(null)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    api.get<RoundDetail>(`/tournaments/${tid}/rounds/${rid}`).then(setRound)
  }, [tid, rid])

  useEffect(load, [load])

  useWebSocket(useCallback((event: string) => {
    if (event === 'ballot_submitted') load()
  }, [load]))

  const generate = async () => {
    try {
      setError('')
      const r = await api.post<RoundDetail>(`/tournaments/${tid}/rounds/${rid}/generate`)
      setRound(r)
    } catch (e) { setError(e instanceof Error ? e.message : "Unknown error") }
  }

  const setStatus = async (status: string) => {
    await api.patch(`/tournaments/${tid}/rounds/${rid}/status?status=${status}`, {})
    load()
  }

  if (!round) return <p className="text-slate-400">Loading...</p>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/tournaments/${tid}/rounds`} className="text-sm text-blue-600 hover:underline">&larr; Rounds</Link>
        <h1 className="text-2xl font-bold text-slate-900">Round {round.round_number}</h1>
        <span className={`text-xs px-2 py-0.5 rounded capitalize ${
          round.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
          round.status === 'in_progress' ? 'bg-amber-100 text-amber-700' :
          'bg-slate-100 text-slate-600'
        }`}>{round.status.replace('_', ' ')}</span>
      </div>

      {error && <p className="text-red-600 text-sm bg-red-50 p-2 rounded">{error}</p>}

      <div className="flex gap-2">
        {round.pairings.length === 0 && (
          <button onClick={generate}
            className="bg-emerald-600 text-white px-4 py-1.5 rounded text-sm hover:bg-emerald-500">
            Auto-Generate Pairings
          </button>
        )}
        {round.status === 'pending' && round.pairings.length > 0 && (
          <button onClick={() => setStatus('in_progress')}
            className="bg-amber-500 text-white px-4 py-1.5 rounded text-sm hover:bg-amber-400">
            Start Round
          </button>
        )}
        {round.status === 'in_progress' && (
          <button onClick={() => setStatus('completed')}
            className="bg-slate-700 text-white px-4 py-1.5 rounded text-sm hover:bg-slate-600">
            Complete Round
          </button>
        )}
      </div>

      <div className="space-y-3">
        {round.pairings.map(p => (
          <div key={p.id} className="bg-white shadow rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="font-semibold text-slate-900">{p.petitioner_team_code}</span>
                <span className="text-xs text-slate-400 mx-1">({p.petitioner_school})</span>
                <span className="text-slate-500 mx-2">vs</span>
                <span className="font-semibold text-slate-900">{p.respondent_team_code}</span>
                <span className="text-xs text-slate-400 mx-1">({p.respondent_school})</span>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded capitalize ${
                p.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                p.status === 'scoring' ? 'bg-blue-100 text-blue-700' :
                'bg-slate-100 text-slate-600'
              }`}>{p.status}</span>
            </div>
            {p.room && <p className="text-xs text-slate-500 mb-2">Room: {p.room}</p>}
            <div className="text-xs space-y-1">
              {p.judge_assignments.map(ja => (
                <div key={ja.id} className="flex items-center gap-2">
                  <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded">{ja.access_code}</span>
                  <span className="text-slate-600">{ja.judge_name || 'Unassigned'}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
        {round.pairings.length === 0 && (
          <p className="text-slate-400 text-sm">No pairings yet. Generate them above.</p>
        )}
      </div>
    </div>
  )
}
