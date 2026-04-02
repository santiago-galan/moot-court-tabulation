from sqlalchemy import JSON, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


class Ruleset(Base):
    __tablename__ = "rulesets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    oralists_per_team: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    num_preliminary_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    judges_per_round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    pairing_method: Mapped[str] = mapped_column(String(20), nullable=False, default="swiss")
    same_school_constraint: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    win_determination: Mapped[str] = mapped_column(String(20), nullable=False, default="ballot")
    ranking_method: Mapped[str] = mapped_column(String(30), nullable=False, default="wins_then_points")
    scoring_criteria: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    ranking_tiebreakers: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    tournaments = relationship("Tournament", back_populates="ruleset")
