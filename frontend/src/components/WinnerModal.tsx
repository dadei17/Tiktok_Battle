import { useEffect, useState } from 'react'
import './WinnerModal.css'

interface WinnerModalProps {
    winner: string
    rankings: Array<{ country: string; score: number; position: number }>
    onClose: () => void
}

const CONFETTI_COLORS = ['#f5c518', '#4a9eff', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']

function getEmoji(country: string): string {
    const emojis: Record<string, string> = {
        'Turkey': '🇹🇷', 'Saudi Arabia': '🇸🇦', 'Egypt': '🇪🇬', 'Pakistan': '🇵🇰',
        'United States': '🇺🇸', 'Russia': '🇷🇺', 'China': '🇨🇳', 'India': '🇮🇳',
    }
    return emojis[country] || '🌍'
}

export function WinnerModal({ winner, rankings, onClose }: WinnerModalProps) {
    const [confetti, setConfetti] = useState<Array<{ id: number; x: number; color: string; delay: number; size: number }>>([])

    useEffect(() => {
        const pieces = Array.from({ length: 60 }, (_, i) => ({
            id: i,
            x: Math.random() * 100,
            color: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
            delay: Math.random() * 2,
            size: 6 + Math.random() * 8,
        }))
        setConfetti(pieces)
    }, [])

    return (
        <div className="modal-overlay animate-fade-in" onClick={onClose} id="winner-modal">
            {/* Confetti */}
            {confetti.map(c => (
                <div
                    key={c.id}
                    className="confetti-piece"
                    style={{
                        left: `${c.x}%`,
                        background: c.color,
                        animationDelay: `${c.delay}s`,
                        width: c.size,
                        height: c.size,
                    }}
                />
            ))}

            <div className="modal-card animate-slide-up" onClick={e => e.stopPropagation()}>
                <div className="winner-crown">👑</div>
                <h2 className="winner-title">Battle Over!</h2>
                <div className="winner-name">
                    <span className="winner-flag">{getEmoji(winner)}</span>
                    <span>{winner}</span>
                </div>
                <p className="winner-sub">WINS THE BATTLE!</p>

                {/* Final rankings */}
                <div className="final-rankings">
                    {rankings.map(r => (
                        <div key={r.country} className="ranking-row">
                            <span className="ranking-pos">{['🥇', '🥈', '🥉', '4️⃣'][r.position - 1]}</span>
                            <span className="ranking-flag">{getEmoji(r.country)}</span>
                            <span className="ranking-name">{r.country}</span>
                            <span className="ranking-score">{r.score.toLocaleString()} pts</span>
                        </div>
                    ))}
                </div>

                <button className="btn btn-primary mt-close" onClick={onClose}>
                    Continue →
                </button>
            </div>
        </div>
    )
}
