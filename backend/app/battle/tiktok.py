import logging
import asyncio
from typing import TYPE_CHECKING
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, ConnectEvent, DisconnectEvent, CommentEvent

if TYPE_CHECKING:
    from app.battle.manager import BattleManager
    from app.ws.manager import WebSocketManager
    from app.repository.battle_repo import BattleRepository

logger = logging.getLogger(__name__)

# Gift name → points mapping
GIFT_POINTS: dict[str, int] = {
    "Rose": 1,
    "TikTok": 1,
    "Panda": 5,
    "Ice Cream Cone": 5,
    "Finger Heart": 5,
    "Sunglasses": 10,
    "Heart Me": 10,
    "Rainbow Puke": 50,
    "Drama Queen": 50,
    "Interstellar": 100,
    "Lion": 500,
    "Drama Queen": 100,
    "Universe": 1000,
}

# Fallback: 1 point per coin value
COIN_VALUE_MULTIPLIER: float = 0.01


def gift_to_points(gift_name: str, coin_value: int) -> int:
    """Convert a TikTok gift to battle points."""
    if gift_name in GIFT_POINTS:
        return GIFT_POINTS[gift_name]
    # Fallback: proportional to coin cost
    points = max(1, int(coin_value * COIN_VALUE_MULTIPLIER))
    return points


def detect_country_from_comment(comment: str, countries: list[str]) -> str | None:
    """Very simple country mention detection from comment text."""
    lower = comment.lower()
    for country in countries:
        if country.lower() in lower:
            return country
    return None


class TikTokListener:
    """
    Connects to a TikTok Live stream and translates gift/comment events
    into battle score updates. Runs as an async background task.
    """

    def __init__(
        self,
        username: str,
        session_id: str | None,
        battle_manager: "BattleManager",
        ws_manager: "WebSocketManager",
        battle_repo: "BattleRepository",
    ):
        self.username = username
        self.session_id = session_id
        self.battle_manager = battle_manager
        self.ws_manager = ws_manager
        self.battle_repo = battle_repo
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Launch listener as a background asyncio task."""
        if not self.username:
            logger.warning("No TikTok username configured — listener not started.")
            return
        self._task = asyncio.create_task(self._run())
        logger.info(f"TikTokListener task started for @{self.username}")

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("TikTokListener stopped.")

    async def _run(self) -> None:
        """Main loop — reconnects on disconnect."""
        while True:
            try:
                await self._connect()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"TikTok connection error: {e}. Reconnecting in 10s…")
                await asyncio.sleep(10)

    async def _connect(self) -> None:
        kwargs = {}
        if self.session_id:
            kwargs["sessionid"] = self.session_id

        client = TikTokLiveClient(unique_id=f"@{self.username}", **kwargs)

        @client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            logger.info(f"Connected to @{self.username} live stream.")

        @client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            logger.warning(f"Disconnected from @{self.username} live stream.")

        @client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            battle = self.battle_manager.get_active_battle()
            if not battle:
                return

            gift_name = event.gift.name if event.gift else "Unknown"
            coin_value = event.gift.diamond_count if event.gift else 0
            points = gift_to_points(gift_name, coin_value)

            # Map sender's country to a battle country
            # For simplicity: gift country determined by sender nickname hints or first country
            country = _pick_country_for_user(event.user, battle.countries)

            if battle.add_score(country, points):
                state = battle.get_state()
                state["last_gift"] = {
                    "user": event.user.nickname if event.user else "Unknown",
                    "gift": gift_name,
                    "points": points,
                    "country": country,
                    "is_lion": gift_name.lower() == "lion",
                }
                await self.ws_manager.broadcast(state)

        @client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            battle = self.battle_manager.get_active_battle()
            if not battle:
                return

            comment_text = event.comment or ""
            country = detect_country_from_comment(comment_text, battle.countries)
            if country:
                # Comments give 1 point to mentioned country
                if battle.add_score(country, 1):
                    await self.ws_manager.broadcast(battle.get_state())

        await client.start()


def _pick_country_for_user(user, countries: list[str]) -> str:
    """
    Pick a battle country for the gifting user.
    Strategy: hash user ID to consistently assign them a country.
    This is stable per-user within a session.
    """
    if not user or not countries:
        return countries[0] if countries else "Unknown"
    user_id = getattr(user, "id", None) or getattr(user, "uid", "") or ""
    index = abs(hash(str(user_id))) % len(countries)
    return countries[index]
