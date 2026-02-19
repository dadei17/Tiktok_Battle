# Country Battle Live 🏆⚔️

A production-ready real-time TikTok gift battle application where viewers support countries by sending gifts during a live stream.

## Quick Start

```bash
cd CountryBattleLive

# Copy and configure environment (optionally set TikTok username)
cp .env.example .env

# Start everything
docker-compose up --build
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Configuration

Edit `.env` in the project root:

| Variable | Default | Description |
|---|---|---|
| `TIKTOK_USERNAME` | (empty) | TikTok live creator username |
| `TIKTOK_SESSION_ID` | (empty) | TikTok session ID for authenticated requests |
| `BATTLE_DURATION_SECONDS` | `300` | Battle timer length (seconds) |
| `DEFAULT_COUNTRIES` | `Turkey,Saudi Arabia,Egypt,Pakistan` | Countries in each battle |

## Sounds

Place MP3 files in `frontend/public/sounds/`:
- `lion.mp3` — played when a Lion gift is received
- `gameover.mp3` — played when battle ends

## Architecture

```
backend/
  app/
    battle/battle.py      # Battle class (async lock, in-memory scores)
    battle/manager.py     # BattleManager (single active battle)
    battle/tiktok.py      # TikTokListener (background task)
    ws/manager.py         # WebSocketManager (broadcast)
    repository/           # Async DB writes (atomic transactions)
    routers/              # API endpoints
    models.py             # SQLAlchemy ORM
    main.py               # FastAPI app + lifespan

frontend/
  src/
    hooks/useWebSocket.ts # Auto-reconnecting WS hook
    pages/BattlePage.tsx  # Live battle view
    pages/Leaderboard.tsx # Country statistics
    pages/History.tsx     # Past battles
    components/           # CountryCard, Timer, WinnerModal
```

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/history` | Last 20 battles |
| `GET` | `/leaderboard` | All-time country stats |
| `GET` | `/battle/{id}` | Specific battle detail |
| `GET` | `/active-battle` | Current active battle state |
| `POST` | `/manual-score` | Add points (body: `{country, points}`) |
| `POST` | `/reset` | Reset battle (keeps history) |
| `WS` | `/ws` | Real-time updates |

## Concurrency Safety

- **asyncio.Lock** on `Battle.end_battle()` prevents double-ending
- **`battle_finished` flag** acts as a guard inside the lock
- **Single DB transaction** ensures no partial writes
- **UNIQUE constraint** on `(battle_id, country_name)` prevents duplicate results
- **ON CONFLICT DO UPDATE** for atomic statistics upserts
