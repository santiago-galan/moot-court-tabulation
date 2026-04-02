import { useState } from 'react'
import { api } from '../../api/client'
import type { JudgeLoginData, OralistScoreEntry, ScoringCriterion, Oralist } from '../../types/models'

export default function JudgeEntry() {
  const [code, setCode] = useState('')
  const [data, setData] = useState<JudgeLoginData | null>(null)
  const [scores, setScores] = useState<Record<string, number>>({})
  const [winnerId, setWinnerId] = useState<number | null>(null)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')

  const login = async () => {
    try {
      setError('')
      const d = await api.get<JudgeLoginData>(`/judge/login/${code.toUpperCase()}`)
      setData(d)
      if (d.already_submitted) setSubmitted(true)
    } catch { setError('Invalid access code.') }
  }

  const scoreKey = (oId: number, cName: string) => `${oId}:${cName}`

  const submit = async () => {
    if (!data) return
    const entries: OralistScoreEntry[] = []
    const allOralists = [...data.petitioner.oralists, ...data.respondent.oralists]
    for (const o of allOralists) {
      for (const c of data.scoring_criteria) {
        entries.push({
          oralist_id: o.id,
          criterion_name: c.name,
          score: scores[scoreKey(o.id, c.name)] ?? 0,
        })
      }
    }

    try {
      setError('')
      await api.post(`/judge-assignments/${data.assignment_id}/ballot`, {
        winner_team_id: data.win_determination === 'ballot' ? winnerId : null,
        scores: entries,
      })
      setSubmitted(true)
    } catch (e) { setError(e instanceof Error ? e.message : "Unknown error") }
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-sm space-y-4 text-center">
          <h1 className="text-xl font-bold text-slate-900">Judge Portal</h1>
          <p className="text-sm text-slate-500">Enter the 6-character access code provided by the tournament administrator.</p>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <input className="w-full text-center text-2xl tracking-[0.3em] font-mono border-2 border-slate-300 rounded-lg px-3 py-3 uppercase focus:border-slate-900 focus:outline-none"
            maxLength={6} value={code} onChange={e => setCode(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && login()} placeholder="------" />
          <button onClick={login} disabled={code.length < 6}
            className="w-full bg-slate-900 text-white py-2.5 rounded-lg font-medium disabled:opacity-40 hover:bg-slate-700">
            Enter
          </button>
        </div>
      </div>
    )
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-emerald-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-sm text-center space-y-3">
          <div className="text-4xl">&#10003;</div>
          <h1 className="text-xl font-bold text-slate-900">Ballot Submitted</h1>
          <p className="text-sm text-slate-500">Thank you. Your scores have been recorded.</p>
        </div>
      </div>
    )
  }

  const renderOralistScores = (oralists: Oralist[], criteria: ScoringCriterion[], side: string) => (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">{side}</h3>
      {oralists.map(o => (
        <div key={o.id} className="bg-slate-50 rounded-lg p-3 space-y-2">
          <p className="font-medium text-slate-900">{o.name} <span className="text-xs text-slate-400">(Position {o.position})</span></p>
          {criteria.map(c => (
            <label key={c.name} className="flex items-center justify-between text-sm">
              <span className="text-slate-600">{c.name} <span className="text-xs text-slate-400">(0-{c.max_points})</span></span>
              <input type="number" min={0} max={c.max_points} step={0.5}
                className="border rounded px-2 py-1 w-20 text-right"
                value={scores[scoreKey(o.id, c.name)] ?? ''}
                onChange={e => setScores(s => ({ ...s, [scoreKey(o.id, c.name)]: +e.target.value }))} />
            </label>
          ))}
        </div>
      ))}
    </div>
  )

  return (
    <div className="min-h-screen bg-slate-100 p-4">
      <div className="max-w-lg mx-auto space-y-4">
        <div className="bg-white rounded-xl shadow p-4">
          <h1 className="text-lg font-bold text-slate-900">{data.tournament_name}</h1>
          <p className="text-sm text-slate-500">Round {data.round_number} &middot; {data.room || 'No room assigned'}</p>
          <div className="mt-2 flex justify-between text-sm">
            <span><strong>Pet:</strong> {data.petitioner.team_code} ({data.petitioner.school_name})</span>
            <span><strong>Res:</strong> {data.respondent.team_code} ({data.respondent.school_name})</span>
          </div>
        </div>

        {error && <p className="text-red-600 text-sm bg-red-50 p-2 rounded">{error}</p>}

        <div className="bg-white rounded-xl shadow p-4 space-y-4">
          {renderOralistScores(data.petitioner.oralists, data.scoring_criteria, 'Petitioner')}
          {renderOralistScores(data.respondent.oralists, data.scoring_criteria, 'Respondent')}
        </div>

        {data.win_determination === 'ballot' && (
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-semibold text-sm text-slate-700 mb-2">Select Round Winner</h3>
            <div className="flex gap-3">
              {[
                { id: data.petitioner.team_id, label: data.petitioner.team_code },
                { id: data.respondent.team_id, label: data.respondent.team_code },
              ].map(t => (
                <button key={t.id} onClick={() => setWinnerId(t.id)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium border-2 transition ${
                    winnerId === t.id ? 'border-emerald-600 bg-emerald-50 text-emerald-800' : 'border-slate-200 text-slate-600'
                  }`}>
                  {t.label}
                </button>
              ))}
            </div>
          </div>
        )}

        <button onClick={submit}
          className="w-full bg-emerald-600 text-white py-3 rounded-xl font-semibold text-lg hover:bg-emerald-500 shadow-lg">
          Submit Ballot
        </button>
      </div>
    </div>
  )
}
