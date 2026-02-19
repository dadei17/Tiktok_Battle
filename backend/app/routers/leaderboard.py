import logging
from fastapi import APIRouter
from app.schemas import LeaderboardEntry
from app.repository.battle_repo import BattleRepository

router = APIRouter(tags=["Leaderboard"])
logger = logging.getLogger(__name__)
repo = BattleRepository()


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard():
    """Return country statistics sorted by total wins descending."""
    stats = await repo.get_leaderboard()
    return stats
