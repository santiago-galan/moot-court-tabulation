from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


class Pairing(Base):
    __tablename__ = "pairings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"), nullable=False)
    petitioner_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    respondent_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    room: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    round = relationship("Round", back_populates="pairings")
    petitioner_team = relationship("Team", foreign_keys=[petitioner_team_id])
    respondent_team = relationship("Team", foreign_keys=[respondent_team_id])
    judge_assignments = relationship("JudgeAssignment", back_populates="pairing", cascade="all, delete-orphan")


class JudgeAssignment(Base):
    __tablename__ = "judge_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pairing_id: Mapped[int] = mapped_column(ForeignKey("pairings.id"), nullable=False)
    judge_name: Mapped[str] = mapped_column(String(200), nullable=False)
    access_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)

    pairing = relationship("Pairing", back_populates="judge_assignments")
    ballot = relationship("Ballot", back_populates="judge_assignment", uselist=False, cascade="all, delete-orphan")
