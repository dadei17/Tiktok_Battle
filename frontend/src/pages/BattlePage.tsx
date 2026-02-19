import { useCallback, useEffect, useRef, useState } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import { CountryCard } from '../components/CountryCard'
import { Timer } from '../components/Timer'
import { WinnerModal } from '../components/WinnerModal'
import './BattlePage.css'

const API = `http://${window.location.hostname}:8000`
const DEFAULT_DURATION = 300

export default function BattlePage() {
    const [showWinner, setShowWinner] = useState(false)
    const [winnerData, setWinnerData] = useState<{ winner: string; rankings: any[] } | null>(null)
    const lionAudio = useRef<HTMLAudioElement | null>(null)
    const gameoverAudio = useRef<HTMLAudioElement | null>(null)
    const [manualCountry, setManualCountry] = useState('')
    const [manualPoints, setManualPoints] = useState(100)
    const [toast, setToast] = useState<string | null>(null)

    const showToast = (msg: string) => {
        setToast(msg)
        setTimeout(() => setToast(null), 3000)
    }

    const onLionGift = useCallback(() => {
        try {
            if (!lionAudio.current) {
                lionAudio.current = new Audio('/sounds/lion.mp3')
            }
            lionAudio.current.currentTime = 0
            lionAudio.current.play().catch(() => { })
        } catch { }
    }, [])

    const onGameOver = useCallback(() => {
        try {
            if (!gameoverAudio.current) {
                gameoverAudio.current = new Audio('/sounds/gameover.mp3')
            }
            gameoverAudio.current.currentTime = 0
            gameoverAudio.current.play().catch(() => { })
        } catch { }
    }, [])

    const { state, connected } = useWebSocket(onLionGift, onGameOver)

    // Show winner modal on game_over event (must be in useEffect, not render body)
    useEffect(() => {
        if (state?.type === 'game_over' && state.winner && state.rankings) {
            setShowWinner(true)
            setWinnerData({ winner: state.winner, rankings: state.rankings })
        }
    }, [state])

    const handleManualScore = async () => {
        if (!manualCountry) return
        try {
            const res = await fetch(`${API}/manual-score`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ country: manualCountry, points: manualPoints }),
            })
            const data = await res.json()
            showToast(res.ok ? `✅ ${data.detail}` : `❌ ${data.detail}`)
        } catch {
            showToast('❌ Failed to update score')
        }
    }

    const handleReset = async () => {
        if (!confirm('Reset the current battle and start a new one?')) return
        try {
            const res = await fetch(`${API}/reset`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' })
            const data = await res.json()
            setShowWinner(false)
            showToast(`🔄 ${data.message}`)
        } catch {
            showToast('❌ Failed to reset battle')
        }
    }

    const scores = state?.scores || {}
    const rankings = state?.rankings || []
    const maxScore = Math.max(1, ...(Object.values(scores) as number[]))
    const timeRemaining = state?.time_remaining ?? DEFAULT_DURATION
    const totalSeconds = state?.total_seconds ?? DEFAULT_DURATION
    const countries = Object.keys(scores)

    return (
        <div className="battle-page container">
            {showWinner && winnerData && (
                <WinnerModal
                    winner={winnerData.winner}
                    rankings={winnerData.rankings}
                    onClose={() => setShowWinner(false)}
                />
            )}

            {toast && <div className="toast animate-slide-up">{toast}</div>}

            {/* Header */}
            <div className="battle-header">
                <div className="ws-status">
                    <span className={`ws-dot ${connected ? 'connected' : 'disconnected'}`} />
                    {connected ? 'Live' : 'Connecting…'}
                </div>
                {state?.creator_username && (
                    <div className="creator-tag">@{state.creator_username}</div>
                )}
                <Timer seconds={timeRemaining} totalSeconds={totalSeconds} />
            </div>

            {/* Last gift notification */}
            {state?.last_gift && (
                <div className={`gift-toast animate-slide-up ${state.last_gift.is_lion ? 'lion-gift' : ''}`}>
                    {state.last_gift.is_lion ? '🦁' : '🎁'}{' '}
                    <strong>{state.last_gift.user}</strong> sent {state.last_gift.gift}{' '}
                    <span className="gift-pts">+{state.last_gift.points} pts</span> →{' '}
                    <strong>{state.last_gift.country}</strong>
                </div>
            )}

            {/* Country cards */}
            {countries.length > 0 ? (
                <div className="countries-grid">
                    {rankings.map(({ country, score, position }) => (
                        <CountryCard
                            key={country}
                            country={country}
                            score={score}
                            position={position}
                            maxScore={maxScore}
                            isWinner={state?.battle_finished && position === 1}
                        />
                    ))}
                </div>
            ) : (
                <div className="no-battle-card card">
                    <div className="no-battle-icon">⚔️</div>
                    <h2>No Active Battle</h2>
                    <p>Start a battle using the controls below or via TikTok live.</p>
                </div>
            )}

            {/* Admin Controls */}
            <div className="admin-panel card">
                <h3 className="admin-title">⚙️ Admin Controls</h3>
                <div className="admin-row">
                    <select
                        className="admin-select"
                        value={manualCountry}
                        onChange={e => setManualCountry(e.target.value)}
                        id="manual-country-select"
                    >
                        <option value="">Select country…</option>
                        {countries.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                    <input
                        type="number"
                        className="admin-input"
                        value={manualPoints}
                        onChange={e => setManualPoints(Number(e.target.value))}
                        min={1}
                        id="manual-points-input"
                    />
                    <button className="btn btn-primary" onClick={handleManualScore} id="manual-score-btn">
                        Add Points
                    </button>
                    <button className="btn btn-danger" onClick={handleReset} id="reset-battle-btn">
                        🔄 Reset Battle
                    </button>
                </div>
            </div>
        </div>
    )
}
