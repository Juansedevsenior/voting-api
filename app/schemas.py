from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VoterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class VoterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    has_voted: bool


class CandidateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    party: str | None = Field(default=None, max_length=120)


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    party: str | None
    votes: int


class VoteCreate(BaseModel):
    voter_id: int = Field(gt=0)
    candidate_id: int = Field(gt=0)


class VoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    voter_id: int
    candidate_id: int


class CandidateStatistics(BaseModel):
    candidate_id: int
    candidate_name: str
    party: str | None
    votes: int
    percentage: float


class VotingStatistics(BaseModel):
    total_votes: int
    total_voters_who_voted: int
    candidates: list[CandidateStatistics]
