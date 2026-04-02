import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { Tournament } from '../../types/models'

export default function TournamentPage() {
  const { id } = useParams<{ id: string }>()
  const [t, setT] = useState<Tournament | null>(null)

  useEffect(() => { api.get<Tournament>(`/tournaments/${id}`).then(setT) }, [id])

  if (!t) return <p className="text-slate-400">Loading...</p>

  const links = [
    { to: `/tournaments/${id}/teams`, label: 'Teams', desc: 'Manage team rosters and CSV import' },
    { to: `/tournaments/${id}/rounds`, label: 'Rounds', desc: 'Create rounds, generate pairings, manage judges' },
    { to: `/tournaments/${id}/standings`, label: 'Standings', desc: 'View live rankings and tiebreakers' },
    { to: `/tournaments/${id}/bracket`, label: 'Bracket', desc: 'Generate and view elimination bracket' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t.name}</h1>
        <p className="text-sm text-slate-500">
          {t.event_date || 'No date'} &middot; Ruleset: {t.ruleset?.name ?? `#${t.ruleset_id}`}
          &middot; Status: <span className="capitalize">{t.status}</span>
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {links.map(l => (
          <Link key={l.to} to={l.to}
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
            <p className="font-semibold text-slate-900">{l.label}</p>
            <p className="text-sm text-slate-500">{l.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
