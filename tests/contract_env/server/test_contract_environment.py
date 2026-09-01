from contract_env.server.contract_environment import _coverage_score

def test_coverage_score_all_covered():
    draft = "This policy ensures purpose limitation, data minimization, and lawful basis."
    reqs = ["purpose limitation", "data minimization", "lawful basis"]
    covered, missing = _coverage_score(draft, reqs)
    assert covered == 3
    assert missing == []

def test_coverage_score_partial_coverage():
    draft = "We adhere to data minimization."
    reqs = ["purpose limitation", "data minimization", "lawful basis"]
    covered, missing = _coverage_score(draft, reqs)
    assert covered == 1
    assert missing == ["purpose limitation", "lawful basis"]

def test_coverage_score_no_coverage():
    draft = "This policy says nothing relevant."
    reqs = ["purpose limitation", "data minimization"]
    covered, missing = _coverage_score(draft, reqs)
    assert covered == 0
    assert missing == ["purpose limitation", "data minimization"]

def test_coverage_score_empty_draft():
    draft = ""
    reqs = ["purpose limitation", "data minimization"]
    covered, missing = _coverage_score(draft, reqs)
    assert covered == 0
    assert missing == ["purpose limitation", "data minimization"]

def test_coverage_score_empty_requirements():
    draft = "This policy ensures purpose limitation, data minimization, and lawful basis."
    reqs = []
    covered, missing = _coverage_score(draft, reqs)
    assert covered == 0
    assert missing == []

def test_coverage_score_case_insensitivity():
    draft = "This policy ensures PURPOSE LIMITATION."
    reqs = ["purpose limitation", "DaTa MiNiMiZaTiOn"]
    covered, missing = _coverage_score(draft, reqs)
    assert covered == 1
    assert missing == ["DaTa MiNiMiZaTiOn"]

def test_coverage_score_substring_match():
    # As currently implemented, substring matches are allowed
    draft = "I love caterpillars"
    reqs = ["cat", "dog"]
    covered, missing = _coverage_score(draft, reqs)
    assert covered == 1
    assert missing == ["dog"]
