import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { Tournament, Ruleset } from '../../types/models'

interface NetworkInfo {
  lan_ip: string
  port: number
  judge_url: string
  tunnel_url: string | null
}

export default function Dashboard() {
  const [tournaments, setTournaments] = useState<Tournament[]>([])
  const [rulesets, setRulesets] = useState<Ruleset[]>([])
  const [name, setName] = useState('')
  const [date, setDate] = useState('')
  const [rulesetId, setRulesetId] = useState<number | ''>('')
  const [net, setNet] = useState<NetworkInfo | null>(null)

  useEffect(() => {
    api.get<Tournament[]>('/tournaments').then(setTournaments)
    api.get<Ruleset[]>('/rulesets').then(setRulesets)
    api.get<NetworkInfo>('/network/info').then(setNet)
  }, [])

  const create = async () => {
    if (!name || !rulesetId) return
    const t = await api.post<Tournament>('/tournaments', {
      name, event_date: date || null, ruleset_id: rulesetId,
    })
    setTournaments(prev => [...prev, t])
    setName(''); setDate(''); setRulesetId('')
  }

  const remove = async (id: number) => {
    await api.delete(`/tournaments/${id}`)
    setTournaments(prev => prev.filter(t => t.id !== id))
  }

  const toggleTunnel = async () => {
    if (net?.tunnel_url) {
      await api.post('/network/tunnel/stop')
    } else {
      await api.post('/network/tunnel/start')
    }
    const updated = await api.get<NetworkInfo>('/network/info')
    setNet(updated)
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Tournaments</h1>
        {net && (
          <div className="flex items-center gap-3">
            <span className="text-xs bg-emerald-100 text-emerald-800 px-2 py-1 rounded">
              LAN: {net.lan_ip}:{net.port}
            </span>
            {net.tunnel_url && (
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                Tunnel: {net.tunnel_url}
              </span>
            )}
          </div>
        )}
      </div>

      {net && (
        <div className="bg-white rounded-lg shadow p-4 flex flex-wrap gap-6 items-center">
          <div>
            <h2 className="font-semibold text-slate-700 text-sm mb-1">Judge Portal</h2>
            <p className="text-sm text-slate-600">{net.judge_url}</p>
            <p className="text-xs text-slate-400 mt-0.5">Judges scan the QR code or visit this URL and enter their access code.</p>
            <div className="flex gap-2 mt-2">
              <button onClick={toggleTunnel}
                className={`text-xs px-3 py-1 rounded ${net.tunnel_url ? 'bg-red-100 text-red-700 hover:bg-red-200' : 'bg-blue-100 text-blue-700 hover:bg-blue-200'}`}>
                {net.tunnel_url ? 'Stop Remote Access' : 'Enable Remote Access'}
              </button>
            </div>
          </div>
          <img src="/api/network/qr" alt="Judge Portal QR" className="w-28 h-28 rounded" />
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-4 space-y-3">
        <h2 className="font-semibold text-slate-700">Create Tournament</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <label className="flex flex-col text-sm">
            Name
            <input className="border rounded px-2 py-1 mt-1" value={name}
              onChange={e => setName(e.target.value)} />
          </label>
          <label className="flex flex-col text-sm">
            Date
            <input type="date" className="border rounded px-2 py-1 mt-1" value={date}
              onChange={e => setDate(e.target.value)} />
          </label>
          <label className="flex flex-col text-sm">
            Ruleset
            <select className="border rounded px-2 py-1 mt-1" value={rulesetId}
              onChange={e => setRulesetId(Number(e.target.value) || '')}>
              <option value="">Select...</option>
              {rulesets.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </label>
          <button onClick={create}
            className="bg-slate-900 text-white px-4 py-1.5 rounded text-sm hover:bg-slate-700">
            Create
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {tournaments.map(t => (
          <div key={t.id} className="bg-white rounded-lg shadow p-4 flex flex-col gap-2">
            <div className="flex justify-between items-start">
              <div>
                <Link to={`/tournaments/${t.id}`}
                  className="text-lg font-semibold text-slate-900 hover:underline">{t.name}</Link>
                <p className="text-xs text-slate-500">{t.event_date || 'No date'}</p>
              </div>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 capitalize">{t.status}</span>
            </div>
            <p className="text-sm text-slate-600">Ruleset: {t.ruleset?.name ?? `#${t.ruleset_id}`}</p>
            <div className="flex gap-2 mt-auto pt-2">
              <Link to={`/tournaments/${t.id}/teams`}
                className="text-xs text-blue-600 hover:underline">Teams</Link>
              <Link to={`/tournaments/${t.id}/rounds`}
                className="text-xs text-blue-600 hover:underline">Rounds</Link>
              <Link to={`/tournaments/${t.id}/standings`}
                className="text-xs text-blue-600 hover:underline">Standings</Link>
              <Link to={`/tournaments/${t.id}/bracket`}
                className="text-xs text-blue-600 hover:underline">Bracket</Link>
              <button onClick={() => remove(t.id)}
                className="text-xs text-red-500 hover:underline ml-auto">Delete</button>
            </div>
          </div>
        ))}
        {tournaments.length === 0 && (
          <p className="text-slate-400 text-sm col-span-full">No tournaments yet. Create one above or <Link to="/rulesets" className="underline">define a ruleset</Link> first.</p>
        )}
      </div>
    </div>
  )
}
