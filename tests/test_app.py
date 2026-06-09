import pytest
from app import _debate_script

def test_debate_script_lengths_and_types():
    pro, con, pro_delta, con_delta, verdict = _debate_script("Test Topic")

    assert isinstance(pro, list)
    assert all(isinstance(line, str) for line in pro)
    assert len(pro) == 5

    assert isinstance(con, list)
    assert all(isinstance(line, str) for line in con)
    assert len(con) == 5

    assert isinstance(pro_delta, list)
    assert all(isinstance(val, int) for val in pro_delta)
    assert len(pro_delta) == 5

    assert isinstance(con_delta, list)
    assert all(isinstance(val, int) for val in con_delta)
    assert len(con_delta) == 5

    assert isinstance(verdict, str)

def test_debate_script_deltas():
    _, _, pro_delta, con_delta, _ = _debate_script("Another Topic")

    assert pro_delta == [2, 1, 2, 1, 2]
    assert con_delta == [1, 1, 1, 1, 1]

def test_debate_script_verdict_formatting():
    topic_str = "Is AI sentient?"
    _, _, _, _, verdict = _debate_script(topic_str)

    assert f"Verdict for topic: “{topic_str}”." in verdict
    assert "- PRO wins on governance" in verdict
    assert "- CON wins on irreversibility" in verdict
    assert "Final call: PRO by a narrow margin" in verdict

def test_debate_script_empty_topic():
    _, _, _, _, verdict = _debate_script("")
    assert "Verdict for topic: “”." in verdict
