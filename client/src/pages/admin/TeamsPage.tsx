import { useEffect, useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { Team, Tournament } from '../../types/models'

export default function TeamsPage() {
  const { id } = useParams<{ id: string }>()
  const [teams, setTeams] = useState<Team[]>([])
  const [tournament, setTournament] = useState<Tournament | null>(null)
  const [code, setCode] = useState('')
  const [school, setSchool] = useState('')
  const [email, setEmail] = useState('')
  const [oralistNames, setOralistNames] = useState<string[]>([])
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    api.get<Tournament>(`/tournaments/${id}`).then(t => {
      setTournament(t)
      setOralistNames(Array(t.ruleset?.oralists_per_team ?? 2).fill(''))
    })
    api.get<Team[]>(`/tournaments/${id}/teams`).then(setTeams)
  }, [id])

  const addTeam = async () => {
    if (!code || !school) return
    const t = await api.post<Team>(`/tournaments/${id}/teams`, {
      team_code: code, school_name: school, contact_email: email,
      oralists: oralistNames.map((n, i) => ({ name: n, position: i + 1 })).filter(o => o.name),
    })
    setTeams(prev => [...prev, t])
    setCode(''); setSchool(''); setEmail('')
    setOralistNames(Array(tournament?.ruleset?.oralists_per_team ?? 2).fill(''))
  }

  const importCsv = async () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    const imported = await api.upload<Team[]>(`/tournaments/${id}/teams/import`, file)
    setTeams(prev => [...prev, ...imported])
    if (fileRef.current) fileRef.current.value = ''
  }

  const remove = async (teamId: number) => {
    await api.delete(`/tournaments/${id}/teams/${teamId}`)
    setTeams(prev => prev.filter(t => t.id !== teamId))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/tournaments/${id}`} className="text-sm text-blue-600 hover:underline">&larr; Back</Link>
        <h1 className="text-2xl font-bold text-slate-900">Teams</h1>
      </div>

      <div className="bg-white shadow rounded-lg p-4 space-y-3">
        <h2 className="font-semibold text-slate-700">Add Team</h2>
        <div className="flex flex-wrap gap-3 items-end text-sm">
          <label className="flex flex-col">Code
            <input className="border rounded px-2 py-1 mt-1 w-24" value={code} onChange={e => setCode(e.target.value)} />
          </label>
          <label className="flex flex-col">School
            <input className="border rounded px-2 py-1 mt-1" value={school} onChange={e => setSchool(e.target.value)} />
          </label>
          <label className="flex flex-col">Email
            <input className="border rounded px-2 py-1 mt-1" value={email} onChange={e => setEmail(e.target.value)} />
          </label>
          {oralistNames.map((n, i) => (
            <label key={i} className="flex flex-col">Oralist {i + 1}
              <input className="border rounded px-2 py-1 mt-1" value={n}
                onChange={e => { const a = [...oralistNames]; a[i] = e.target.value; setOralistNames(a) }} />
            </label>
          ))}
          <button onClick={addTeam} className="bg-slate-900 text-white px-4 py-1.5 rounded hover:bg-slate-700">Add</button>
        </div>
        <div className="flex gap-2 items-center pt-2 border-t border-slate-100 text-sm">
          <input ref={fileRef} type="file" accept=".csv" className="text-xs" />
          <button onClick={importCsv} className="bg-emerald-600 text-white px-3 py-1 rounded text-xs hover:bg-emerald-500">Import CSV</button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm bg-white shadow rounded-lg">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="text-left px-3 py-2">Code</th>
              <th className="text-left px-3 py-2">School</th>
              <th className="text-left px-3 py-2">Oralists</th>
              <th className="text-left px-3 py-2">Email</th>
              <th className="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {teams.map(t => (
              <tr key={t.id} className="border-t border-slate-100">
                <td className="px-3 py-2 font-medium">{t.team_code}</td>
                <td className="px-3 py-2">{t.school_name}</td>
                <td className="px-3 py-2 text-xs text-slate-500">{t.oralists.map(o => o.name).join(', ') || '-'}</td>
                <td className="px-3 py-2 text-xs">{t.contact_email || '-'}</td>
                <td className="px-3 py-2">
                  <button onClick={() => remove(t.id)} className="text-red-500 text-xs hover:underline">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
