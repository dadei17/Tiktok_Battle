import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Battle(Base):
    __tablename__ = "battles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    creator_username: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    winner_country: Mapped[str | None] = mapped_column(String(255), nullable=True)

    results: Mapped[list["BattleResult"]] = relationship(
        "BattleResult", back_populates="battle", cascade="all, delete-orphan"
    )


class BattleResult(Base):
    __tablename__ = "battle_results"
    __table_args__ = (
        UniqueConstraint("battle_id", "country_name", name="uq_battle_country"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    battle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("battles.id", ondelete="CASCADE"), nullable=False
    )
    country_name: Mapped[str] = mapped_column(String(255), nullable=False)
    final_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    battle: Mapped["Battle"] = relationship("Battle", back_populates="results")


class CountryStatistics(Base):
    __tablename__ = "country_statistics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    country_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    total_wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_second_place: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_third_place: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_battles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
