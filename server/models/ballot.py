from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


class Ballot(Base):
    __tablename__ = "ballots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    judge_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("judge_assignments.id"), nullable=False, unique=True
    )
    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    submitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    judge_assignment = relationship("JudgeAssignment", back_populates="ballot")
    winner_team = relationship("Team", foreign_keys=[winner_team_id])
    scores = relationship("OralistScore", back_populates="ballot", cascade="all, delete-orphan")


class OralistScore(Base):
    __tablename__ = "oralist_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ballot_id: Mapped[int] = mapped_column(ForeignKey("ballots.id"), nullable=False)
    oralist_id: Mapped[int] = mapped_column(ForeignKey("oralists.id"), nullable=False)
    criterion_name: Mapped[str] = mapped_column(String(200), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    ballot = relationship("Ballot", back_populates="scores")
    oralist = relationship("Oralist")
