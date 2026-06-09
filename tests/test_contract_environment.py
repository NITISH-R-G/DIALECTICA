import pytest
from contract_env.server.contract_environment import _contradiction_checks

def test_contradiction_checks_no_contradictions():
    text = "We will keep your data safe and share it responsibly."
    issues = _contradiction_checks(text)
    assert not issues

def test_contradiction_checks_retention():
    # Lowercase test
    text1 = "we may retain your data indefinitely."
    issues1 = _contradiction_checks(text1)
    assert len(issues1) == 1
    assert "Mentions retention and 'indefinitely'" in issues1[0]

    # Mixed case test
    text2 = "We will RETAIN your records INDEFINITELY if necessary."
    issues2 = _contradiction_checks(text2)
    assert len(issues2) == 1
    assert "Mentions retention and 'indefinitely'" in issues2[0]

def test_contradiction_checks_never_share():
    # Lowercase test
    text1 = "we will never sell your data, but we may share it with partners."
    issues1 = _contradiction_checks(text1)
    assert len(issues1) == 1
    assert "Contains 'we will never' and 'may share'" in issues1[0]

    # Mixed case test
    text2 = "We Will NEVER use your details. We MAY SHARE them occasionally."
    issues2 = _contradiction_checks(text2)
    assert len(issues2) == 1
    assert "Contains 'we will never' and 'may share'" in issues2[0]

def test_contradiction_checks_both_contradictions():
    text = "We will NEVER share your data, but we MAY do so. Also, we retain it INDEFINITELY."
    issues = _contradiction_checks(text)
    assert len(issues) == 2
    assert any("Mentions retention and 'indefinitely'" in issue for issue in issues)
    assert any("Contains 'we will never' and 'may share'" in issue for issue in issues)
