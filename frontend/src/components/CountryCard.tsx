import { forwardRef, useEffect, useRef, useState } from 'react'
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

const COUNTRY_ISO: Record<string, string> = {
    'Turkey': 'tr',
    'Saudi Arabia': 'sa',
    'Egypt': 'eg',
    'Pakistan': 'pk',
    'United States': 'us',
    'Russia': 'ru',
    'China': 'cn',
    'India': 'in',
    'Brazil': 'br',
    'France': 'fr',
    'Germany': 'de',
    'Japan': 'jp',
    'UK': 'gb',
    'Korea': 'kr',
}

function getCountryColor(country: string): string {
    return COUNTRY_COLORS[country] ||
        `hsl(${Math.abs(country.split('').reduce((a, c) => a + c.charCodeAt(0), 0)) % 360}, 65%, 55%)`
}

function getFlagUrl(country: string): string | null {
    const iso = COUNTRY_ISO[country]
    return iso ? `https://flagcdn.com/w80/${iso}.png` : null
}

interface CountryCardProps {
    country: string
    score: number
    position: number
    maxScore: number
    isWinner?: boolean
}

export const CountryCard = forwardRef<HTMLDivElement, CountryCardProps>(
    ({ country, score, position, maxScore, isWinner }, ref) => {
        const color = getCountryColor(country)
        const flagUrl = getFlagUrl(country)

        const prevPositionRef = useRef(position)
        const [isRankUp, setIsRankUp] = useState(false)

        useEffect(() => {
            if (position < prevPositionRef.current) {
                // Moved up (e.g., 4 -> 3)
                setIsRankUp(true)
                const timer = setTimeout(() => setIsRankUp(false), 2000)
                return () => clearTimeout(timer)
            }
            prevPositionRef.current = position
        }, [position])

        // Fill is 0–80% of the bar container (never reaches the edge)
        const fillPct = maxScore > 0 ? Math.max(4, (score / maxScore) * 80) : 4

        const positionLabel = ['🥇', '🥈', '🥉', '4️⃣'][position - 1] || `#${position}`
        const positionClass = ['gold', 'silver', 'bronze', 'fourth'][position - 1] || 'fourth'

        return (
            <div
                ref={ref}
                className={`country-card ${positionClass} ${isWinner ? 'winner-card' : ''} ${isRankUp ? 'rank-up' : ''}`}
                id={`card-${country.replace(/\s+/g, '-')}`}
            >
                {/* Rank */}
                <span className="rank-badge">{positionLabel}</span>

                {/* Flag circle */}
                <div className="flag-circle" style={{ boxShadow: `0 0 0 2px ${color}66` }}>
                    {flagUrl ? (
                        <img
                            className="flag-img"
                            src={flagUrl}
                            alt={country}
                            onError={e => { (e.currentTarget as HTMLImageElement).style.display = 'none' }}
                        />
                    ) : (
                        <span className="flag-fallback">{country.slice(0, 2).toUpperCase()}</span>
                    )}
                </div>

                {/* Country name */}
                <span className="country-name">{country}</span>

                {/* Bar track */}
                <div className="bar-track">
                    <div
                        className="bar-fill"
                        style={{
                            width: `${fillPct}%`,
                            background: `linear-gradient(to right, ${color}cc, ${color})`,
                            boxShadow: `0 0 10px ${color}55`,
                        }}
                    >
                        <span className="bar-score">{score.toLocaleString()} pts</span>
                    </div>
                </div>
            </div>
        )
    }
)
