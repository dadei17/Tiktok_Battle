import logging
from fastapi import APIRouter, HTTPException, Request
from app.schemas import ManualScoreRequest, StartBattleRequest, MessageResponse

router = APIRouter(tags=["Admin"])
logger = logging.getLogger(__name__)


@router.post("/manual-score", response_model=MessageResponse)
async def manual_score(request: Request, payload: ManualScoreRequest):
    """Add points manually to a country in the active battle."""
    battle_manager = request.app.state.battle_manager
    battle = battle_manager.get_active_battle()

    if not battle:
        raise HTTPException(status_code=404, detail="No active battle running.")

    if payload.country not in battle.scores:
        raise HTTPException(
            status_code=400,
            detail=f"Country '{payload.country}' not in current battle. "
                   f"Valid: {list(battle.scores.keys())}"
        )

    success = battle.add_score(payload.country, payload.points)
    if not success:
        raise HTTPException(status_code=409, detail="Battle already finished.")

    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast(battle.get_state())

    return MessageResponse(
        message="Score updated",
        detail=f"+{payload.points} pts → {payload.country}"
    )


@router.post("/reset", response_model=MessageResponse)
async def reset_battle(request: Request, payload: StartBattleRequest | None = None):
    """
    Reset the active battle (start a fresh one).
    Does NOT delete battle history from the database.
    """
    battle_manager = request.app.state.battle_manager
    ws_manager = request.app.state.ws_manager
    battle_repo = request.app.state.battle_repo

    creator = (payload.creator_username if payload else None) or "admin"
    countries = (payload.countries if payload else None)
    duration = (payload.duration_seconds if payload else None)

    new_battle = await battle_manager.start_battle(
        creator_username=creator,
        countries=countries,
        duration_seconds=duration,
        ws_manager=ws_manager,
        battle_repo=battle_repo,
    )

    return MessageResponse(
        message="Battle reset",
        detail=f"New battle {new_battle.id} started with {list(new_battle.countries)}"
    )


@router.get("/active-battle")
async def get_active_battle(request: Request):
    """Return the current active battle state."""
    battle_manager = request.app.state.battle_manager
    battle = battle_manager.get_active_battle()

    if not battle:
        return {"active": False, "battle": None}

    return {"active": True, "battle": battle.get_state()}
