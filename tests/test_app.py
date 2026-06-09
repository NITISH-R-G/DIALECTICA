import json
from app import _event


def test_event_serialization():
    result = _event(
        topic="AI",
        mode="test",
        round_idx=1,
        rounds_total=3,
        pro_line="Pro",
        con_line="Con",
        pro_score=10,
        con_score=5,
        momentum=2,
        speaker="Pro",
        timer_s=1.5,
        verdict="Win",
    )

    parsed = json.loads(result)

    assert parsed["topic"] == "AI"
    assert parsed["mode"] == "test"
    assert parsed["round"] == 1
    assert parsed["roundsTotal"] == 3
    assert parsed["proLine"] == "Pro"
    assert parsed["conLine"] == "Con"
    assert parsed["proScore"] == 10
    assert parsed["conScore"] == 5
    assert parsed["momentum"] == 2
    assert parsed["speaker"] == "Pro"
    assert parsed["timerS"] == 1.5
    assert parsed["verdict"] == "Win"
    assert "ts" in parsed


def test_event_serialization_no_verdict():
    result = _event(
        topic="AI",
        mode="test",
        round_idx=1,
        rounds_total=3,
        pro_line="Pro",
        con_line="Con",
        pro_score=10,
        con_score=5,
        momentum=2,
        speaker="Pro",
        timer_s=1.5,
    )

    parsed = json.loads(result)

    assert parsed["topic"] == "AI"
    assert parsed["mode"] == "test"
    assert parsed["round"] == 1
    assert parsed["roundsTotal"] == 3
    assert parsed["proLine"] == "Pro"
    assert parsed["conLine"] == "Con"
    assert parsed["proScore"] == 10
    assert parsed["conScore"] == 5
    assert parsed["momentum"] == 2
    assert parsed["speaker"] == "Pro"
    assert parsed["timerS"] == 1.5
    assert parsed["verdict"] == ""
    assert "ts" in parsed
