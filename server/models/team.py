from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    team_code: Mapped[str] = mapped_column(String(50), nullable=False)
    school_name: Mapped[str] = mapped_column(String(300), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(300), nullable=False, default="")

    tournament = relationship("Tournament", back_populates="teams")
    oralists = relationship("Oralist", back_populates="team", cascade="all, delete-orphan")


class Oralist(Base):
    __tablename__ = "oralists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    team = relationship("Team", back_populates="oralists")
