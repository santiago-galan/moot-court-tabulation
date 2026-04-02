import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { TeamStanding } from '../../types/models'

export default function StandingsPage() {
  const { id } = useParams<{ id: string }>()
  const [standings, setStandings] = useState<TeamStanding[]>([])

  useEffect(() => {
    api.get<TeamStanding[]>(`/tournaments/${id}/standings`).then(setStandings)
  }, [id])

  const downloadReport = () => {
    window.open(`/api/tournaments/${id}/reports/tournament`, '_blank')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/tournaments/${id}`} className="text-sm text-blue-600 hover:underline">&larr; Back</Link>
        <h1 className="text-2xl font-bold text-slate-900">Standings</h1>
        <button onClick={() => api.get<TeamStanding[]>(`/tournaments/${id}/standings`).then(setStandings)}
          className="text-sm text-blue-600 hover:underline ml-auto">Refresh</button>
        <button onClick={downloadReport}
          className="bg-slate-900 text-white px-3 py-1 rounded text-sm hover:bg-slate-700">Download PDF</button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm bg-white shadow rounded-lg">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="text-center px-3 py-2 w-12">Rank</th>
              <th className="text-left px-3 py-2">Team</th>
              <th className="text-left px-3 py-2">School</th>
              <th className="text-center px-3 py-2">W</th>
              <th className="text-center px-3 py-2">L</th>
              <th className="text-center px-3 py-2">Points</th>
              <th className="text-center px-3 py-2">Opp W</th>
              <th className="text-center px-3 py-2">Pt Diff</th>
              <th className="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {standings.map(s => (
              <tr key={s.team_id} className="border-t border-slate-100">
                <td className="text-center px-3 py-2 font-bold text-slate-700">{s.rank}</td>
                <td className="px-3 py-2 font-medium">{s.team_code}</td>
                <td className="px-3 py-2">{s.school_name}</td>
                <td className="text-center px-3 py-2">{s.wins}</td>
                <td className="text-center px-3 py-2">{s.losses}</td>
                <td className="text-center px-3 py-2">{s.total_points.toFixed(1)}</td>
                <td className="text-center px-3 py-2">{s.opponent_wins}</td>
                <td className="text-center px-3 py-2">{s.point_differential >= 0 ? '+' : ''}{s.point_differential.toFixed(1)}</td>
                <td className="px-3 py-2">
                  <a href={`/api/tournaments/${id}/reports/ballots/team/${s.team_id}`}
                    target="_blank" className="text-blue-600 text-xs hover:underline">Ballot PDF</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
