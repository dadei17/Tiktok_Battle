import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import BattlePage from './pages/BattlePage'
import Leaderboard from './pages/Leaderboard'
import History from './pages/History'
import './App.css'

function App() {
    return (
        <BrowserRouter>
            <div className="app-layout">
                <nav className="navbar">
                    <div className="navbar-brand">
                        <span className="navbar-logo">⚔️</span>
                        <span className="navbar-title">Country Battle Live</span>
                    </div>
                    <div className="navbar-links">
                        <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            🔴 Live Battle
                        </NavLink>
                        <NavLink to="/leaderboard" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            🏆 Leaderboard
                        </NavLink>
                        <NavLink to="/history" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            📜 History
                        </NavLink>
                    </div>
                </nav>
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<BattlePage />} />
                        <Route path="/leaderboard" element={<Leaderboard />} />
                        <Route path="/history" element={<History />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    )
}

export default App
