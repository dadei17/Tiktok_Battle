import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ws.manager import WebSocketManager
    from app.repository.battle_repo import BattleRepository

logger = logging.getLogger(__name__)


class Battle:
    """
    Represents a single live battle between countries.
    All score updates are in-memory; DB writes happen only on battle end.
    An asyncio.Lock prevents double-ending race conditions.
    """

    def __init__(
        self,
        battle_id: uuid.UUID,
        creator_username: str,
        countries: list[str],
        duration_seconds: int,
    ):
        self.id = battle_id
        self.creator_username = creator_username
        self.countries = countries
        self.duration_seconds = duration_seconds
        self.started_at: datetime = datetime.now(timezone.utc)

        # In-memory scores
        self.scores: dict[str, int] = {country: 0 for country in countries}

        # Concurrency safety
        self._lock = asyncio.Lock()
        self.battle_finished: bool = False

    def add_score(self, country: str, points: int) -> bool:
        """Thread-safe score add (no lock needed — asyncio single-threaded per event loop)."""
        if self.battle_finished:
            return False
        if country not in self.scores:
            logger.warning(f"Country '{country}' not found in battle.")
            return False
        self.scores[country] = max(0, self.scores[country] + points)
        return True

    def get_rankings(self) -> list[dict]:
        """Return countries sorted by score descending with their positions."""
        sorted_countries = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {"country": name, "score": score, "position": idx + 1}
            for idx, (name, score) in enumerate(sorted_countries)
        ]

    def get_state(self) -> dict:
        """Return current battle state for WebSocket broadcast."""
        now = datetime.now(timezone.utc)
        elapsed = (now - self.started_at).total_seconds()
        remaining = max(0, self.duration_seconds - elapsed)
        return {
            "type": "state_update",
            "battle_id": str(self.id),
            "creator_username": self.creator_username,
            "scores": self.scores.copy(),
            "rankings": self.get_rankings(),
            "time_remaining": int(remaining),
            "total_seconds": self.duration_seconds,
            "battle_finished": self.battle_finished,
        }

    async def end_battle(
        self,
        ws_manager: "WebSocketManager",
        battle_repo: "BattleRepository",
    ) -> None:
        """
        Atomically end the battle:
        1. Acquire lock
        2. Check finished flag (prevent double-end)
        3. Persist to DB in one transaction
        4. Set flag and broadcast game_over
        """
        async with self._lock:
            if self.battle_finished:
                logger.info(f"Battle {self.id} already finished — skipping.")
                return

            now = datetime.now(timezone.utc)
            elapsed = int((now - self.started_at).total_seconds())
            rankings = self.get_rankings()
            winner = rankings[0]["country"] if rankings else None

            logger.info(f"Ending battle {self.id}, winner: {winner}")

            try:
                await battle_repo.save_battle_result(
                    battle_id=self.id,
                    creator_username=self.creator_username,
                    started_at=self.started_at,
                    ended_at=now,
                    duration_seconds=elapsed,
                    winner_country=winner,
                    rankings=rankings,
                )
            except Exception as e:
                logger.exception(f"Failed to save battle {self.id}: {e}")
                raise

            self.battle_finished = True

        # Broadcast outside the lock to avoid holding it during WS I/O
        await ws_manager.broadcast({
            "type": "game_over",
            "battle_id": str(self.id),
            "winner": winner,
            "rankings": rankings,
            "duration_seconds": elapsed,
        })
        logger.info(f"Battle {self.id} ended and broadcasted.")
