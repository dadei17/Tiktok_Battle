import uuid
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Battle as BattleModel, BattleResult
from app.schemas import BattleDetailResponse, BattleHistoryItem
from app.repository.battle_repo import BattleRepository

router = APIRouter(tags=["Battles"])
logger = logging.getLogger(__name__)
repo = BattleRepository()


@router.get("/history", response_model=list[BattleHistoryItem])
async def get_history():
    """Return the last 20 completed battles."""
    battles = await repo.get_history(limit=20)
    return battles


@router.get("/battle/{battle_id}", response_model=BattleDetailResponse)
async def get_battle(battle_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Return full details of a specific battle including country results."""
    result = await db.execute(
        select(BattleModel).where(BattleModel.id == battle_id)
    )
    battle = result.scalar_one_or_none()
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")

    results_q = await db.execute(
        select(BattleResult)
        .where(BattleResult.battle_id == battle_id)
        .order_by(BattleResult.position)
    )
    battle.results = list(results_q.scalars().all())
    return battle
