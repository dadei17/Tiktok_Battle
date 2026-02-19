import uuid
import logging
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models import Battle as BattleModel, BattleResult, CountryStatistics
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class BattleRepository:
    """
    All database writes are async and wrapped in a single transaction.
    Uses PostgreSQL upsert for country_statistics to handle concurrency.
    """

    async def save_battle_result(
        self,
        battle_id: uuid.UUID,
        creator_username: str,
        started_at: datetime,
        ended_at: datetime,
        duration_seconds: int,
        winner_country: str | None,
        rankings: list[dict],
    ) -> None:
        """
        Atomically:
        1. Insert battle row
        2. Insert 4 battle_result rows
        3. Upsert country_statistics for each country
        """
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # 1. Insert battle
                battle_row = BattleModel(
                    id=battle_id,
                    creator_username=creator_username,
                    started_at=started_at,
                    ended_at=ended_at,
                    duration_seconds=duration_seconds,
                    winner_country=winner_country,
                )
                session.add(battle_row)
                await session.flush()  # Ensure battle_id exists for FK

                # 2. Insert battle_results (one per country, unique constraint protected)
                for entry in rankings:
                    result_row = BattleResult(
                        id=uuid.uuid4(),
                        battle_id=battle_id,
                        country_name=entry["country"],
                        final_score=entry["score"],
                        position=entry["position"],
                    )
                    session.add(result_row)

                # 3. Upsert country_statistics using PostgreSQL ON CONFLICT
                for entry in rankings:
                    country = entry["country"]
                    position = entry["position"]

                    stmt = pg_insert(CountryStatistics).values(
                        id=uuid.uuid4(),
                        country_name=country,
                        total_wins=1 if position == 1 else 0,
                        total_second_place=1 if position == 2 else 0,
                        total_third_place=1 if position == 3 else 0,
                        total_battles=1,
                    ).on_conflict_do_update(
                        index_elements=["country_name"],
                        set_={
                            "total_wins": CountryStatistics.total_wins + (1 if position == 1 else 0),
                            "total_second_place": CountryStatistics.total_second_place + (1 if position == 2 else 0),
                            "total_third_place": CountryStatistics.total_third_place + (1 if position == 3 else 0),
                            "total_battles": CountryStatistics.total_battles + 1,
                        }
                    )
                    await session.execute(stmt)

        logger.info(f"Battle {battle_id} saved to DB successfully.")

    async def get_history(self, limit: int = 20) -> list[BattleModel]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(BattleModel)
                .order_by(BattleModel.started_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    async def get_battle_by_id(self, battle_id: uuid.UUID) -> BattleModel | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(BattleModel).where(BattleModel.id == battle_id)
            )
            battle = result.scalar_one_or_none()
            if battle:
                # Eager load results
                await session.execute(
                    select(BattleResult).where(BattleResult.battle_id == battle_id)
                )
            return battle

    async def get_leaderboard(self) -> list[CountryStatistics]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CountryStatistics)
                .order_by(CountryStatistics.total_wins.desc())
            )
            return list(result.scalars().all())
