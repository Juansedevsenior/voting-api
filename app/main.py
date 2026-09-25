from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Candidate, Vote, Voter
from .schemas import (
    CandidateCreate,
    CandidateResponse,
    CandidateStatistics,
    VoteCreate,
    VoteResponse,
    VoterCreate,
    VoterResponse,
    VotingStatistics,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Voting System API",
    version="1.0.0",
    description="REST API for voters, candidates and voting statistics.",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def health_check():
    return {"message": "Voting System API is running"}


# -------------------------
# Voters
# -------------------------

@app.post("/voters", response_model=VoterResponse, status_code=status.HTTP_201_CREATED, tags=["Voters"])
def create_voter(payload: VoterCreate, db: Session = Depends(get_db)):
    # A person cannot be both voter and candidate.
    candidate_exists = db.scalar(
        select(Candidate).where(func.lower(Candidate.name) == payload.name.strip().lower())
    )
    if candidate_exists:
        raise HTTPException(
            status_code=409,
            detail="A person with this name is already registered as a candidate.",
        )

    voter = Voter(name=payload.name.strip(), email=str(payload.email).lower())
    db.add(voter)
    try:
        db.commit()
        db.refresh(voter)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email is already registered.")
    return voter


@app.get("/voters", response_model=list[VoterResponse], tags=["Voters"])
def list_voters(db: Session = Depends(get_db)):
    return db.scalars(select(Voter).order_by(Voter.id)).all()


@app.get("/voters/{voter_id}", response_model=VoterResponse, tags=["Voters"])
def get_voter(voter_id: int, db: Session = Depends(get_db)):
    voter = db.get(Voter, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found.")
    return voter


@app.delete("/voters/{voter_id}", tags=["Voters"])
def delete_voter(voter_id: int, db: Session = Depends(get_db)):
    voter = db.get(Voter, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found.")

    if voter.has_voted:
        raise HTTPException(
            status_code=409,
            detail="A voter who has already voted cannot be deleted.",
        )

    db.delete(voter)
    db.commit()
    return {"message": "Voter deleted successfully."}


# -------------------------
# Candidates
# -------------------------

@app.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED, tags=["Candidates"])
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    # A person cannot be both candidate and voter.
    voter_exists = db.scalar(
        select(Voter).where(func.lower(Voter.name) == payload.name.strip().lower())
    )
    if voter_exists:
        raise HTTPException(
            status_code=409,
            detail="A person with this name is already registered as a voter.",
        )

    candidate = Candidate(
        name=payload.name.strip(),
        party=payload.party.strip() if payload.party else None,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@app.get("/candidates", response_model=list[CandidateResponse], tags=["Candidates"])
def list_candidates(db: Session = Depends(get_db)):
    return db.scalars(select(Candidate).order_by(Candidate.id)).all()


@app.get("/candidates/{candidate_id}", response_model=CandidateResponse, tags=["Candidates"])
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return candidate


@app.delete("/candidates/{candidate_id}", tags=["Candidates"])
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    if candidate.votes > 0:
        raise HTTPException(
            status_code=409,
            detail="A candidate with votes cannot be deleted.",
        )

    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully."}


# -------------------------
# Votes
# -------------------------

@app.post("/votes", response_model=VoteResponse, status_code=status.HTTP_201_CREATED, tags=["Votes"])
def create_vote(payload: VoteCreate, db: Session = Depends(get_db)):
    voter = db.get(Voter, payload.voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found.")

    candidate = db.get(Candidate, payload.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    if voter.has_voted:
        raise HTTPException(
            status_code=409,
            detail="This voter has already voted.",
        )

    # The unique constraint on votes.voter_id is the database-level second line
    # of defense against duplicate votes.
    vote = Vote(voter_id=voter.id, candidate_id=candidate.id)
    voter.has_voted = True
    candidate.votes += 1

    db.add(vote)
    try:
        db.commit()
        db.refresh(vote)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This voter has already voted.",
        )

    return vote


@app.get("/votes", response_model=list[VoteResponse], tags=["Votes"])
def list_votes(db: Session = Depends(get_db)):
    return db.scalars(select(Vote).order_by(Vote.id)).all()


@app.get("/votes/statistics", response_model=VotingStatistics, tags=["Votes"])
def voting_statistics(db: Session = Depends(get_db)):
    total_votes = db.scalar(select(func.count(Vote.id))) or 0
    total_voters_who_voted = db.scalar(
        select(func.count(Voter.id)).where(Voter.has_voted.is_(True))
    ) or 0

    candidates = db.scalars(select(Candidate).order_by(Candidate.id)).all()

    stats = []
    for candidate in candidates:
        percentage = round((candidate.votes / total_votes) * 100, 2) if total_votes else 0.0
        stats.append(
            CandidateStatistics(
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                party=candidate.party,
                votes=candidate.votes,
                percentage=percentage,
            )
        )

    return VotingStatistics(
        total_votes=total_votes,
        total_voters_who_voted=total_voters_who_voted,
        candidates=stats,
    )
