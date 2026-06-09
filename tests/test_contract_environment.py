import pytest
from contract_env.server.contract_environment import _coverage_score

def test_coverage_all_present():
    draft_md = "This draft contains purpose limitation, data minimization, and lawful basis."
    requirements = ["purpose limitation", "data minimization", "lawful basis"]
    covered, missing = _coverage_score(draft_md, requirements)
    assert covered == 3
    assert missing == []

def test_coverage_partial():
    draft_md = "This draft contains purpose limitation and lawful basis."
    requirements = ["purpose limitation", "data minimization", "lawful basis"]
    covered, missing = _coverage_score(draft_md, requirements)
    assert covered == 2
    assert missing == ["data minimization"]

def test_coverage_none_present():
    draft_md = "This draft contains nothing relevant."
    requirements = ["purpose limitation", "data minimization", "lawful basis"]
    covered, missing = _coverage_score(draft_md, requirements)
    assert covered == 0
    assert missing == ["purpose limitation", "data minimization", "lawful basis"]

def test_coverage_case_insensitive():
    draft_md = "This draft contains PurPosE LiMiTaTiOn and DATA MINIMIZATION."
    requirements = ["purpose limitation", "data minimization"]
    covered, missing = _coverage_score(draft_md, requirements)
    assert covered == 2
    assert missing == []

def test_coverage_empty_requirements():
    draft_md = "Some random text."
    requirements = []
    covered, missing = _coverage_score(draft_md, requirements)
    assert covered == 0
    assert missing == []

def test_coverage_empty_draft():
    draft_md = ""
    requirements = ["purpose limitation"]
    covered, missing = _coverage_score(draft_md, requirements)
    assert covered == 0
    assert missing == ["purpose limitation"]
