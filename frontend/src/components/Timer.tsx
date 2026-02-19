import { useMemo } from 'react'
import './Timer.css'

interface TimerProps {
    seconds: number
    totalSeconds: number
}

export function Timer({ seconds, totalSeconds }: TimerProps) {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    const pct = totalSeconds > 0 ? (seconds / totalSeconds) * 100 : 0

    const colorClass = pct > 50 ? 'timer-green' : pct > 20 ? 'timer-yellow' : 'timer-red'

    const timeStr = `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`

    return (
        <div className={`timer-wrapper ${colorClass}`} id="battle-timer">
            <div className="timer-ring">
                <svg viewBox="0 0 64 64" className="timer-svg">
                    <circle cx="32" cy="32" r="28" className="timer-track" />
                    <circle
                        cx="32" cy="32" r="28"
                        className="timer-progress"
                        style={{
                            strokeDashoffset: `${176 - (176 * pct) / 100}`,
                            stroke: pct > 50 ? '#2ecc71' : pct > 20 ? '#f39c12' : '#e74c3c',
                        }}
                    />
                </svg>
                <div className="timer-text">{timeStr}</div>
            </div>
            <div className="timer-label">Time Left</div>
        </div>
    )
}
