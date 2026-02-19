import { useRef, useEffect } from 'react'
import './CountryCard.css'

const COUNTRY_COLORS: Record<string, string> = {
    'Turkey': '#e74c3c',
    'Saudi Arabia': '#2ecc71',
    'Egypt': '#f39c12',
    'Pakistan': '#27ae60',
    'United States': '#3498db',
    'Russia': '#9b59b6',
    'China': '#e67e22',
    'India': '#1abc9c',
    'Brazil': '#16a085',
    'France': '#2980b9',
    'Germany': '#8e44ad',
    'Japan': '#c0392b',
    'UK': '#2c3e50',
    'Korea': '#d35400',
}

function getCountryColor(country: string): string {
    return COUNTRY_COLORS[country] || `hsl(${Math.abs(country.split('').reduce((a, c) => a + c.charCodeAt(0), 0)) % 360}, 65%, 55%)`
}

function getCountryEmoji(country: string): string {
    const emojis: Record<string, string> = {
        'Turkey': '🇹🇷',
        'Saudi Arabia': '🇸🇦',
        'Egypt': '🇪🇬',
        'Pakistan': '🇵🇰',
        'United States': '🇺🇸',
        'Russia': '🇷🇺',
        'China': '🇨🇳',
        'India': '🇮🇳',
        'Brazil': '🇧🇷',
        'France': '🇫🇷',
        'Germany': '🇩🇪',
        'Japan': '🇯🇵',
        'UK': '🇬🇧',
        'Korea': '🇰🇷',
    }
    return emojis[country] || '🌍'
}

interface CountryCardProps {
    country: string
    score: number
    position: number
    maxScore: number
    isWinner?: boolean
}

export function CountryCard({ country, score, position, maxScore, isWinner }: CountryCardProps) {
    const color = getCountryColor(country)
    const emoji = getCountryEmoji(country)
    const fillPct = maxScore > 0 ? Math.max(4, (score / maxScore) * 100) : 4

    const positionLabel = ['🥇', '🥈', '🥉', '4️⃣'][position - 1] || `${position}`
    const positionClass = ['gold', 'silver', 'bronze', 'fourth'][position - 1] || 'fourth'

    return (
        <div className={`country-card ${positionClass} ${isWinner ? 'winner-card' : ''}`} id={`card-${country.replace(/\s+/g, '-')}`}>
            {/* Rank badge */}
            <div className={`rank-badge rank-${positionClass}`}>{positionLabel}</div>

            {/* Country info */}
            <div className="country-info">
                <span className="country-emoji">{emoji}</span>
                <span className="country-name">{country}</span>
            </div>

            {/* Score */}
            <div className="country-score" style={{ color }}>
                {score.toLocaleString()}
                <span className="score-unit"> pts</span>
            </div>

            {/* Vertical progress bar */}
            <div className="progress-container">
                <div
                    className="progress-bar"
                    style={{
                        height: `${fillPct}%`,
                        background: `linear-gradient(to top, ${color}, ${color}aa)`,
                        boxShadow: `0 0 20px ${color}66`,
                    }}
                />
            </div>
        </div>
    )
}
