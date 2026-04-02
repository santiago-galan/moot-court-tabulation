import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/admin/Dashboard'
import RulesetsPage from './pages/admin/RulesetsPage'
import TournamentPage from './pages/admin/TournamentPage'
import TeamsPage from './pages/admin/TeamsPage'
import RoundsPage from './pages/admin/RoundsPage'
import RoundDetailPage from './pages/admin/RoundDetailPage'
import StandingsPage from './pages/admin/StandingsPage'
import BracketPage from './pages/admin/BracketPage'
import JudgeEntry from './pages/judge/JudgeEntry'

const NAV_LINKS = [
  { to: '/', label: 'Dashboard' },
  { to: '/rulesets', label: 'Rulesets' },
]

function AdminLayout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-slate-900 text-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-6">
          <Link to="/" className="text-lg font-bold tracking-tight">MCTS</Link>
          <nav className="flex gap-4 text-sm">
            {NAV_LINKS.map(l => (
              <Link key={l.to} to={l.to}
                className={`hover:text-slate-300 ${pathname === l.to ? 'text-white underline underline-offset-4' : 'text-slate-400'}`}>
                {l.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/judge" element={<JudgeEntry />} />
      <Route path="/*" element={
        <AdminLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/rulesets" element={<RulesetsPage />} />
            <Route path="/tournaments/:id" element={<TournamentPage />} />
            <Route path="/tournaments/:id/teams" element={<TeamsPage />} />
            <Route path="/tournaments/:id/rounds" element={<RoundsPage />} />
            <Route path="/tournaments/:tid/rounds/:rid" element={<RoundDetailPage />} />
            <Route path="/tournaments/:id/standings" element={<StandingsPage />} />
            <Route path="/tournaments/:id/bracket" element={<BracketPage />} />
          </Routes>
        </AdminLayout>
      } />
    </Routes>
  )
}
