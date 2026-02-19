import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import './History.css'

const API = `http://${window.location.hostname}:8000`

interface HistoryItem {
    id: string
    creator_username: string
    started_at: string
    ended_at: string | null
    duration_seconds: number | null
    winner_country: string | null
}

function formatDate(iso: string): string {
    return new Date(iso).toLocaleString()
}

function formatDuration(seconds: number | null): string {
    if (!seconds) return '—'
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}m ${s}s`
}

function getEmoji(country: string | null): string {
    if (!country) return '—'
    const emojis: Record<string, string> = {
        'Turkey': '🇹🇷', 'Saudi Arabia': '🇸🇦', 'Egypt': '🇪🇬', 'Pakistan': '🇵🇰',
        'United States': '🇺🇸', 'Russia': '🇷🇺', 'China': '🇨🇳', 'India': '🇮🇳',
    }
    return (emojis[country] || '🌍') + ' ' + country
}

export default function History() {
    const [data, setData] = useState<HistoryItem[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetch(`${API}/history`)
            .then(r => r.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => { setError('Failed to load history'); setLoading(false) })
    }, [])

    return (
        <div className="container history-page">
            <div className="page-header">
                <h1 className="page-title">📜 Battle History</h1>
                <p className="page-subtitle">Last 20 completed battles</p>
            </div>

            {loading && <div className="loading-state">Loading history…</div>}
            {error && <div className="error-state">{error}</div>}

            {!loading && !error && data.length === 0 && (
                <div className="empty-state card">
                    <div style={{ fontSize: '3rem' }}>📭</div>
                    <h3>No history yet</h3>
                    <p>Battles will appear here once completed.</p>
                </div>
            )}

            <div className="history-list">
                {data.map((battle, i) => (
                    <Link to={`/battle/${battle.id}`} key={battle.id} className="history-card card" id={`battle-${battle.id}`}>
                        <div className="history-index">#{data.length - i}</div>
                        <div className="history-content">
                            <div className="history-winner">
                                <span className="winner-trophy">🏆</span>
                                <span>{getEmoji(battle.winner_country)}</span>
                            </div>
                            <div className="history-meta">
                                <span>@{battle.creator_username}</span>
                                <span className="history-sep">·</span>
                                <span>{formatDate(battle.started_at)}</span>
                                <span className="history-sep">·</span>
                                <span>⏱ {formatDuration(battle.duration_seconds)}</span>
                            </div>
                        </div>
                        <div className="history-arrow">→</div>
                    </Link>
                ))}
            </div>
        </div>
    )
}
