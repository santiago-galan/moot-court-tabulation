import { useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { Ruleset, ScoringCriterion } from '../../types/models'

const EMPTY_CRITERION: ScoringCriterion = { name: '', max_points: 25, weight: 1 }
const TIEBREAKER_OPTIONS = ['wins', 'total_points', 'opponent_wins', 'head_to_head', 'point_differential']

export default function RulesetsPage() {
  const [rulesets, setRulesets] = useState<Ruleset[]>([])
  const [editing, setEditing] = useState<Partial<Ruleset> | null>(null)

  useEffect(() => { api.get<Ruleset[]>('/rulesets').then(setRulesets) }, [])

  const openNew = () => setEditing({
    name: '', oralists_per_team: 2, num_preliminary_rounds: 4, judges_per_round: 1,
    pairing_method: 'swiss', same_school_constraint: true, win_determination: 'ballot',
    ranking_method: 'wins_then_points',
    scoring_criteria: [{ name: 'Legal Logic', max_points: 25, weight: 1 }],
    ranking_tiebreakers: ['wins', 'total_points'],
  })

  const save = async () => {
    if (!editing?.name) return
    if (editing.id) {
      const updated = await api.patch<Ruleset>(`/rulesets/${editing.id}`, editing)
      setRulesets(prev => prev.map(r => r.id === updated.id ? updated : r))
    } else {
      const created = await api.post<Ruleset>('/rulesets', editing)
      setRulesets(prev => [...prev, created])
    }
    setEditing(null)
  }

  const remove = async (id: number) => {
    await api.delete(`/rulesets/${id}`)
    setRulesets(prev => prev.filter(r => r.id !== id))
  }

  const criteria = editing?.scoring_criteria ?? []
  const setCriteria = (c: ScoringCriterion[]) => setEditing(e => e ? { ...e, scoring_criteria: c } : e)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Rulesets</h1>
        <button onClick={openNew}
          className="bg-slate-900 text-white px-4 py-1.5 rounded text-sm hover:bg-slate-700">New Ruleset</button>
      </div>

      {editing && (
        <div className="bg-white shadow rounded-lg p-5 space-y-4 border border-slate-200">
          <h2 className="font-semibold">{editing.id ? 'Edit' : 'New'} Ruleset</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <label className="flex flex-col">Name
              <input className="border rounded px-2 py-1 mt-1" value={editing.name ?? ''}
                onChange={e => setEditing(v => v ? { ...v, name: e.target.value } : v)} />
            </label>
            <label className="flex flex-col">Oralists / Team
              <input type="number" min={1} className="border rounded px-2 py-1 mt-1"
                value={editing.oralists_per_team ?? 2}
                onChange={e => setEditing(v => v ? { ...v, oralists_per_team: +e.target.value } : v)} />
            </label>
            <label className="flex flex-col">Prelim Rounds
              <input type="number" min={1} className="border rounded px-2 py-1 mt-1"
                value={editing.num_preliminary_rounds ?? 4}
                onChange={e => setEditing(v => v ? { ...v, num_preliminary_rounds: +e.target.value } : v)} />
            </label>
            <label className="flex flex-col">Judges / Round
              <input type="number" min={1} className="border rounded px-2 py-1 mt-1"
                value={editing.judges_per_round ?? 1}
                onChange={e => setEditing(v => v ? { ...v, judges_per_round: +e.target.value } : v)} />
            </label>
            <label className="flex flex-col">Pairing Method
              <select className="border rounded px-2 py-1 mt-1" value={editing.pairing_method ?? 'swiss'}
                onChange={e => setEditing(v => v ? { ...v, pairing_method: e.target.value } : v)}>
                <option value="swiss">Swiss</option>
                <option value="random">Random</option>
                <option value="manual">Manual</option>
              </select>
            </label>
            <label className="flex flex-col">Win Determination
              <select className="border rounded px-2 py-1 mt-1" value={editing.win_determination ?? 'ballot'}
                onChange={e => setEditing(v => v ? { ...v, win_determination: e.target.value } : v)}>
                <option value="ballot">Ballot-based</option>
                <option value="points">Points-based</option>
              </select>
            </label>
            <label className="flex items-center gap-2 mt-5">
              <input type="checkbox" checked={editing.same_school_constraint ?? true}
                onChange={e => setEditing(v => v ? { ...v, same_school_constraint: e.target.checked } : v)} />
              Same-school constraint
            </label>
          </div>

          <div>
            <h3 className="font-medium text-sm mb-2">Scoring Criteria</h3>
            {criteria.map((c, i) => (
              <div key={i} className="flex gap-2 items-center mb-1 text-sm">
                <input className="border rounded px-2 py-1 flex-1" placeholder="Name" value={c.name}
                  onChange={e => { const a = [...criteria]; a[i] = { ...c, name: e.target.value }; setCriteria(a) }} />
                <input type="number" className="border rounded px-2 py-1 w-20" placeholder="Max" value={c.max_points}
                  onChange={e => { const a = [...criteria]; a[i] = { ...c, max_points: +e.target.value }; setCriteria(a) }} />
                <input type="number" step="0.1" className="border rounded px-2 py-1 w-20" placeholder="Weight" value={c.weight}
                  onChange={e => { const a = [...criteria]; a[i] = { ...c, weight: +e.target.value }; setCriteria(a) }} />
                <button className="text-red-500 text-xs" onClick={() => setCriteria(criteria.filter((_, j) => j !== i))}>Remove</button>
              </div>
            ))}
            <button className="text-sm text-blue-600 mt-1" onClick={() => setCriteria([...criteria, { ...EMPTY_CRITERION }])}>+ Add criterion</button>
          </div>

          <div>
            <h3 className="font-medium text-sm mb-2">Ranking Tiebreakers (in order)</h3>
            <div className="flex flex-wrap gap-2">
              {TIEBREAKER_OPTIONS.map(tb => {
                const active = (editing.ranking_tiebreakers ?? []).includes(tb)
                return (
                  <button key={tb} onClick={() => {
                    const cur = editing.ranking_tiebreakers ?? []
                    setEditing(v => v ? { ...v, ranking_tiebreakers: active ? cur.filter(t => t !== tb) : [...cur, tb] } : v)
                  }}
                    className={`text-xs px-2 py-1 rounded border ${active ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-300'}`}>
                    {tb.replace(/_/g, ' ')}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button onClick={save} className="bg-emerald-600 text-white px-4 py-1.5 rounded text-sm hover:bg-emerald-500">Save</button>
            <button onClick={() => setEditing(null)} className="text-sm text-slate-500 hover:underline">Cancel</button>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {rulesets.map(r => (
          <div key={r.id} className="bg-white shadow rounded-lg p-4 flex items-center justify-between">
            <div>
              <p className="font-semibold text-slate-900">{r.name}</p>
              <p className="text-xs text-slate-500">
                {r.oralists_per_team} oralists, {r.num_preliminary_rounds} prelim rounds,
                {r.judges_per_round} judge(s), {r.pairing_method}, {r.win_determination}
              </p>
              <p className="text-xs text-slate-400 mt-0.5">
                Criteria: {r.scoring_criteria.map(c => `${c.name} (${c.max_points})`).join(', ') || 'none'}
              </p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setEditing(r)} className="text-sm text-blue-600 hover:underline">Edit</button>
              <button onClick={() => remove(r.id)} className="text-sm text-red-500 hover:underline">Delete</button>
            </div>
          </div>
        ))}
        {rulesets.length === 0 && !editing && (
          <p className="text-slate-400 text-sm">No rulesets defined yet.</p>
        )}
      </div>
    </div>
  )
}
