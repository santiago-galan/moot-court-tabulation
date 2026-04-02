from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


class Tournament(Base):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    event_date: Mapped[str] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="setup")
    ruleset_id: Mapped[int] = mapped_column(ForeignKey("rulesets.id"), nullable=False)

    ruleset = relationship("Ruleset", back_populates="tournaments")
    teams = relationship("Team", back_populates="tournament", cascade="all, delete-orphan")
    rounds = relationship("Round", back_populates="tournament", cascade="all, delete-orphan")
