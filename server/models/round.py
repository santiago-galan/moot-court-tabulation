from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


class Round(Base):
    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    round_type: Mapped[str] = mapped_column(String(20), nullable=False, default="preliminary")
    elim_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    tournament = relationship("Tournament", back_populates="rounds")
    pairings = relationship("Pairing", back_populates="round", cascade="all, delete-orphan")
