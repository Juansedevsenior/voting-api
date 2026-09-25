from app.schemas import CandidateCreate, VoterCreate, VoteCreate


def test_voter_schema():
    voter = VoterCreate(name=" Test User ", email="TEST@EXAMPLE.COM")
    assert voter.name == " Test User "
    assert str(voter.email) == "TEST@example.com"


def test_candidate_schema():
    candidate = CandidateCreate(name="Candidate", party="Party")
    assert candidate.party == "Party"


def test_vote_schema():
    vote = VoteCreate(voter_id=1, candidate_id=2)
    assert vote.voter_id == 1
    assert vote.candidate_id == 2
