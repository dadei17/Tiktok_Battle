import uuid
from datetime import datetime
from pydantic import BaseModel


# --- Battle Schemas ---

class RankingEntry(BaseModel):
    country: str
    score: int
    position: int


class BattleStateResponse(BaseModel):
    type: str
    battle_id: str
    creator_username: str
    scores: dict[str, int]
    rankings: list[RankingEntry]
    time_remaining: int
    battle_finished: bool
    last_gift: dict | None = None


# --- Battle Result DB Schemas ---

class BattleResultSchema(BaseModel):
    id: uuid.UUID
    country_name: str
    final_score: int
    position: int

    model_config = {"from_attributes": True}


class BattleDetailResponse(BaseModel):
    id: uuid.UUID
    creator_username: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    winner_country: str | None
    results: list[BattleResultSchema]

    model_config = {"from_attributes": True}


class BattleHistoryItem(BaseModel):
    id: uuid.UUID
    creator_username: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    winner_country: str | None

    model_config = {"from_attributes": True}


# --- Leaderboard ---

class LeaderboardEntry(BaseModel):
    country_name: str
    total_wins: int
    total_second_place: int
    total_third_place: int
    total_battles: int

    model_config = {"from_attributes": True}


# --- Admin Request Schemas ---

class ManualScoreRequest(BaseModel):
    country: str
    points: int
    gift: str | None = None


class StartBattleRequest(BaseModel):
    creator_username: str = "admin"
    countries: list[str] | None = None
    duration_seconds: int | None = None


# --- Generic ---

class MessageResponse(BaseModel):
    message: str
    detail: str | None = None
