import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine
from app.models import Base
from app.battle.manager import BattleManager
from app.battle.tiktok import TikTokListener
from app.ws.manager import WebSocketManager
from app.repository.battle_repo import BattleRepository
from app.routers import battles, leaderboard, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Starting up Country Battle Live...")

    # Initialize singleton services
    ws_manager = WebSocketManager()
    battle_repo = BattleRepository()
    battle_manager = BattleManager()

    # Store on app.state (no global mutable state)
    app.state.ws_manager = ws_manager
    app.state.battle_repo = battle_repo
    app.state.battle_manager = battle_manager

    # Start initial battle automatically
    await battle_manager.start_battle(
        creator_username=settings.TIKTOK_USERNAME or "system",
        countries=None,
        duration_seconds=None,
        ws_manager=ws_manager,
        battle_repo=battle_repo,
    )

    # Start TikTok listener if configured
    tiktok_listener = TikTokListener(
        username=settings.TIKTOK_USERNAME,
        session_id=settings.TIKTOK_SESSION_ID or None,
        battle_manager=battle_manager,
        ws_manager=ws_manager,
        battle_repo=battle_repo,
    )
    app.state.tiktok_listener = tiktok_listener
    await tiktok_listener.start()

    logger.info("Startup complete.")
    yield

    # --- Shutdown ---
    logger.info("Shutting down...")
    await tiktok_listener.stop()
    await engine.dispose()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Country Battle Live",
    description="Real-time TikTok gift battle between countries",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(battles.router)
app.include_router(leaderboard.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Country Battle Live"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ws_manager: WebSocketManager = websocket.app.state.ws_manager
    battle_manager: BattleManager = websocket.app.state.battle_manager

    await ws_manager.connect(websocket)
    try:
        # Send current state immediately on connect
        battle = battle_manager.get_active_battle()
        if battle:
            await ws_manager.send_to(websocket, battle.get_state())
        else:
            await ws_manager.send_to(websocket, {"type": "no_battle", "message": "No active battle"})

        # Keep connection alive — client can send pings
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await ws_manager.send_to(websocket, {"type": "pong"})
            except asyncio.TimeoutError:
                # Send keepalive
                try:
                    await ws_manager.send_to(websocket, {"type": "ping"})
                except Exception:
                    break
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(websocket)
