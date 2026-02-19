import { useEffect, useRef, useCallback, useState } from 'react'

export interface BattleState {
    type: string
    battle_id?: string
    creator_username?: string
    scores?: Record<string, number>
    rankings?: Array<{ country: string; score: number; position: number }>
    time_remaining?: number
    total_seconds?: number
    battle_finished?: boolean
    last_gift?: {
        user: string
        gift: string
        points: number
        country: string
        is_lion: boolean
    }
    winner?: string
    duration_seconds?: number
    message?: string
}

const WS_URL = `ws://${window.location.hostname}:8000/ws`
const RECONNECT_DELAY = 3000

export function useWebSocket(onLionGift: () => void, onGameOver: () => void) {
    const [state, setState] = useState<BattleState | null>(null)
    const [connected, setConnected] = useState(false)
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
    const isMounted = useRef(true)

    const connect = useCallback(() => {
        if (!isMounted.current) return
        try {
            const ws = new WebSocket(WS_URL)
            wsRef.current = ws

            ws.onopen = () => {
                if (!isMounted.current) return
                setConnected(true)
                console.log('WebSocket connected')
            }

            ws.onmessage = (e) => {
                if (!isMounted.current) return
                try {
                    const data: BattleState = JSON.parse(e.data)

                    if (data.type === 'ping') {
                        ws.send('ping')
                        return
                    }

                    setState(data)

                    if (data.type === 'state_update' && data.last_gift?.is_lion) {
                        onLionGift()
                    }
                    if (data.type === 'game_over') {
                        onGameOver()
                    }
                } catch (err) {
                    console.error('WS parse error:', err)
                }
            }

            ws.onclose = () => {
                if (!isMounted.current) return
                setConnected(false)
                console.log('WebSocket closed. Reconnecting…')
                reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY)
            }

            ws.onerror = (e) => {
                console.error('WebSocket error', e)
                ws.close()
            }
        } catch (e) {
            console.error('WebSocket connection failed', e)
            reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY)
        }
    }, [onLionGift, onGameOver])

    useEffect(() => {
        isMounted.current = true
        connect()
        return () => {
            isMounted.current = false
            if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
            wsRef.current?.close()
        }
    }, [connect])

    return { state, connected }
}
