import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from app.battle.battle import Battle
from app.config import get_settings

if TYPE_CHECKING:
    from app.ws.manager import WebSocketManager
    from app.repository.battle_repo import BattleRepository

logger = logging.getLogger(__name__)
settings = get_settings()


class BattleManager:
    """
    Manages the single active battle instance.
    Structured to support future multi-creator battles with minimal refactoring:
    - Replace `current_battle` dict with {creator_id: Battle}
    - Add `start_battle(creator_id, ...)` keyed routing
    """

    def __init__(self):
        self.current_battle: Battle | None = None
        self._timer_task: asyncio.Task | None = None

    async def start_battle(
        self,
        creator_username: str,
        countries: list[str] | None,
        duration_seconds: int | None,
        ws_manager: "WebSocketManager",
        battle_repo: "BattleRepository",
    ) -> Battle:
        """Start a new battle, canceling any existing one without saving it."""
        await self._cancel_timer()

        if countries is None:
            countries = settings.countries_list
        if duration_seconds is None:
            duration_seconds = settings.BATTLE_DURATION_SECONDS

        battle = Battle(
            battle_id=uuid.uuid4(),
            creator_username=creator_username,
            countries=countries,
            duration_seconds=duration_seconds,
        )
        self.current_battle = battle

        # Broadcast initial state
        await ws_manager.broadcast(battle.get_state())

        # Start countdown timer
        self._timer_task = asyncio.create_task(
            self._run_timer(battle, ws_manager, battle_repo)
        )

        logger.info(f"Battle started: {battle.id} by {creator_username}")
        return battle

    async def _run_timer(
        self,
        battle: Battle,
        ws_manager: "WebSocketManager",
        battle_repo: "BattleRepository",
    ) -> None:
        """Countdown timer — ticks every second, ends battle when time expires."""
        try:
            while not battle.battle_finished:
                await asyncio.sleep(1)
                if battle.battle_finished:
                    break
                # Broadcast current state every second so clients see live countdown
                await ws_manager.broadcast(battle.get_state())
                # Check if time has expired
                elapsed = (datetime.now(timezone.utc) - battle.started_at).total_seconds()
                if elapsed >= battle.duration_seconds:
                    logger.info(f"Timer expired for battle {battle.id}. Auto-ending.")
                    await battle.end_battle(ws_manager, battle_repo)
                    break
        except asyncio.CancelledError:
            logger.info(f"Timer cancelled for battle {battle.id}")

    async def _cancel_timer(self) -> None:
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
            try:
                await self._timer_task
            except asyncio.CancelledError:
                pass
        self._timer_task = None

    def get_active_battle(self) -> Battle | None:
        """Return the current active (unfinished) battle, or None."""
        if self.current_battle and not self.current_battle.battle_finished:
            return self.current_battle
        return None

    async def reset_battle(
        self,
        ws_manager: "WebSocketManager",
        battle_repo: "BattleRepository",
        creator_username: str = "admin",
    ) -> Battle:
        """Reset (replace) the active battle without saving current one."""
        await self._cancel_timer()
        self.current_battle = None
        return await self.start_battle(
            creator_username=creator_username,
            countries=None,
            duration_seconds=None,
            ws_manager=ws_manager,
            battle_repo=battle_repo,
        )
