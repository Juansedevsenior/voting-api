from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Voter(Base):
    __tablename__ = "voters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    has_voted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    vote: Mapped["Vote | None"] = relationship(
        back_populates="voter",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    party: Mapped[str | None] = mapped_column(String(120), nullable=True)
    votes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    vote_records: Mapped[list["Vote"]] = relationship(back_populates="candidate")


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    voter_id: Mapped[int] = mapped_column(
        ForeignKey("voters.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    voter: Mapped[Voter] = relationship(back_populates="vote")
    candidate: Mapped[Candidate] = relationship(back_populates="vote_records")
