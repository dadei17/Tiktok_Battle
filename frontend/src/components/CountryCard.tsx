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

// ISO 3166-1 alpha-2 codes for flagcdn.com
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
    return COUNTRY_COLORS[country] || `hsl(${Math.abs(country.split('').reduce((a, c) => a + c.charCodeAt(0), 0)) % 360}, 65%, 55%)`
}

function getFlagUrl(country: string): string | null {
    const iso = COUNTRY_ISO[country]
    if (!iso) return null
    return `https://flagcdn.com/w80/${iso}.png`
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
    const flagUrl = getFlagUrl(country)
    const fillPct = maxScore > 0 ? Math.max(2, (score / maxScore) * 100) : 2

    const positionLabel = ['🥇', '🥈', '🥉', '4️⃣'][position - 1] || `${position}`
    const positionClass = ['gold', 'silver', 'bronze', 'fourth'][position - 1] || 'fourth'

    return (
        <div className={`country-card ${positionClass} ${isWinner ? 'winner-card' : ''}`} id={`card-${country.replace(/\s+/g, '-')}`}>
            {/* Rank badge */}
            <div className={`rank-badge rank-${positionClass}`}>{positionLabel}</div>

            {/* Flag circle */}
            <div className="flag-circle" style={{ boxShadow: `0 0 0 3px ${color}55, 0 0 18px ${color}33` }}>
                {flagUrl ? (
                    <img
                        className="flag-img"
                        src={flagUrl}
                        alt={country}
                        onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none' }}
                    />
                ) : (
                    <span className="flag-fallback">{country.slice(0, 2).toUpperCase()}</span>
                )}
            </div>

            {/* Country name + score */}
            <div className="country-meta">
                <span className="country-name">{country}</span>
                <span className="country-score" style={{ color }}>{score.toLocaleString()} <span className="score-unit">pts</span></span>
            </div>

            {/* Horizontal progress bar */}
            <div className="progress-container">
                <div
                    className="progress-bar"
                    style={{
                        width: `${fillPct}%`,
                        background: `linear-gradient(to right, ${color}, ${color}aa)`,
                        boxShadow: `0 0 14px ${color}66`,
                    }}
                />
            </div>
        </div>
    )
}

