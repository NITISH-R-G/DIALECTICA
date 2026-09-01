from contract_env.server.contract_environment import Draft, Clause, _compute_reward

def test_compute_reward_empty_draft():
    draft = Draft(
        topic="Test Topic",
        requirements=["req1", "req2"],
        forbidden_phrases=["forbidden1"],
        numeric_constraints={"max_days": 30},
        clauses=[],
        definitions={}
    )
    reward = _compute_reward(draft)

    assert reward["reward_components"]["coverage"] == 0.0
    assert reward["reward_components"]["forbidden_penalty"] == 0.0
    assert reward["reward_components"]["contradiction_penalty"] == 0.0
    assert reward["reward_components"]["definitions_bonus"] == 0.0
    assert reward["reward_total"] == 0.0
    assert reward["audit"]["covered"] == 0
    assert reward["audit"]["missing"] == ["req1", "req2"]
    assert reward["audit"]["forbidden_hits"] == []

def test_compute_reward_full_coverage():
    draft = Draft(
        topic="Test Topic",
        requirements=["req1", "req2"],
        forbidden_phrases=["forbidden1"],
        numeric_constraints={"max_days": 30},
        clauses=[
            Clause(id="c1", section="1", text="This covers req1 and req2.")
        ],
        definitions={"term1": "def1"}
    )
    reward = _compute_reward(draft)

    assert reward["reward_components"]["coverage"] == 1.0  # 2/2 requirements met
    assert reward["reward_components"]["forbidden_penalty"] == 0.0
    assert reward["reward_components"]["contradiction_penalty"] == 0.0
    assert reward["reward_components"]["definitions_bonus"] == 0.05 * 1
    # total = 1.5 * 1.0 + 0 + 0 + 0.05
    assert reward["reward_total"] == 1.55
    assert reward["audit"]["covered"] == 2
    assert reward["audit"]["missing"] == []
    assert reward["audit"]["forbidden_hits"] == []

def test_compute_reward_forbidden_hits():
    draft = Draft(
        topic="Test Topic",
        requirements=["req1"],
        forbidden_phrases=["forbidden1", "forbidden2"],
        numeric_constraints={"max_days": 30},
        clauses=[
            Clause(id="c1", section="1", text="This is forbidden1 and forbidden2.")
        ],
        definitions={}
    )
    reward = _compute_reward(draft)

    assert reward["reward_components"]["coverage"] == 0.0  # req1 not met
    assert reward["reward_components"]["forbidden_penalty"] == -0.25 * 2
    assert reward["reward_total"] == -0.5
    assert reward["audit"]["forbidden_hits"] == ["forbidden1", "forbidden2"]

def test_compute_reward_contradictions():
    draft = Draft(
        topic="Test Topic",
        requirements=["req1"],
        forbidden_phrases=["forbidden1"],
        numeric_constraints={"max_days": 30},
        clauses=[
            Clause(id="c1", section="1", text="We will retain data indefinitely.")
        ],
        definitions={}
    )
    reward = _compute_reward(draft)

    assert reward["reward_components"]["contradiction_penalty"] == -0.15 * 1
    assert "Mentions retention and 'indefinitely' (potentially contradictory)." in reward["audit"]["contradictions"]

def test_compute_reward_definition_bonus_capped():
    draft = Draft(
        topic="Test Topic",
        requirements=["req1"],
        forbidden_phrases=["forbidden1"],
        numeric_constraints={"max_days": 30},
        clauses=[],
        definitions={f"term{i}": f"def{i}" for i in range(10)} # 10 definitions
    )
    reward = _compute_reward(draft)

    # Bonus is capped at 6 definitions: 6 * 0.05 = 0.3
    import math
    assert math.isclose(reward["reward_components"]["definitions_bonus"], 0.3)
    assert math.isclose(reward["reward_total"], 0.3)
