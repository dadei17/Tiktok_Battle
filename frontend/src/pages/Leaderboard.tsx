import { useEffect, useState } from 'react'
import './Leaderboard.css'

const API = `http://${window.location.hostname}:8000`

interface LeaderboardEntry {
    country_name: string
    total_wins: number
    total_second_place: number
    total_third_place: number
    total_battles: number
}

function getEmoji(country: string): string {
    const emojis: Record<string, string> = {
        'Turkey': '🇹🇷', 'Saudi Arabia': '🇸🇦', 'Egypt': '🇪🇬', 'Pakistan': '🇵🇰',
        'United States': '🇺🇸', 'Russia': '🇷🇺', 'China': '🇨🇳', 'India': '🇮🇳',
        'Brazil': '🇧🇷', 'France': '🇫🇷', 'Germany': '🇩🇪', 'Japan': '🇯🇵',
    }
    return emojis[country] || '🌍'
}

export default function Leaderboard() {
    const [data, setData] = useState<LeaderboardEntry[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetch(`${API}/leaderboard`)
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => { setError('Failed to load leaderboard'); setLoading(false) })
    }, [])

    return (
        <div className="container leaderboard-page">
            <div className="page-header">
                <h1 className="page-title">🏆 Country Leaderboard</h1>
                <p className="page-subtitle">All-time battle statistics</p>
            </div>

            {loading && <div className="loading-state">Loading leaderboard…</div>}
            {error && <div className="error-state">{error}</div>}

            {!loading && !error && data.length === 0 && (
                <div className="empty-state card">
                    <div style={{ fontSize: '3rem' }}>📊</div>
                    <h3>No battles yet</h3>
                    <p>Complete a battle to see statistics here.</p>
                </div>
            )}

            {data.length > 0 && (
                <div className="leaderboard-table card">
                    <table id="leaderboard-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Country</th>
                                <th>🥇 Wins</th>
                                <th>🥈 2nd</th>
                                <th>🥉 3rd</th>
                                <th>Battles</th>
                                <th>Win Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((entry, i) => {
                                const winRate = entry.total_battles > 0
                                    ? Math.round((entry.total_wins / entry.total_battles) * 100)
                                    : 0
                                return (
                                    <tr key={entry.country_name} className={i < 3 ? `top-${i + 1}` : ''}>
                                        <td className="rank-cell">
                                            {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1}
                                        </td>
                                        <td className="country-cell">
                                            <span>{getEmoji(entry.country_name)}</span>
                                            <span>{entry.country_name}</span>
                                        </td>
                                        <td className="wins-cell">{entry.total_wins}</td>
                                        <td>{entry.total_second_place}</td>
                                        <td>{entry.total_third_place}</td>
                                        <td>{entry.total_battles}</td>
                                        <td>
                                            <div className="winrate-bar">
                                                <div className="winrate-fill" style={{ width: `${winRate}%` }} />
                                                <span>{winRate}%</span>
                                            </div>
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}
