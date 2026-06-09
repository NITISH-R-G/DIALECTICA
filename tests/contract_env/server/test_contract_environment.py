import pytest
from contract_env.server.contract_environment import _contains_any

def test_contains_any_exact_match():
    assert _contains_any("hello world", ["hello"]) == ["hello"]
    assert _contains_any("hello world", ["world"]) == ["world"]

def test_contains_any_case_insensitive():
    assert _contains_any("Hello World", ["hello"]) == ["hello"]
    assert _contains_any("hello world", ["WORLD"]) == ["WORLD"]
    assert _contains_any("HeLlO wOrLd", ["hElLo"]) == ["hElLo"]

def test_contains_any_no_match():
    assert _contains_any("hello world", ["foo", "bar"]) == []

def test_contains_any_empty_phrases():
    assert _contains_any("hello world", []) == []

def test_contains_any_empty_text():
    assert _contains_any("", ["hello"]) == []

def test_contains_any_multiple_matches():
    assert _contains_any("hello world foo bar", ["hello", "foo", "baz"]) == ["hello", "foo"]

def test_contains_any_substring_match():
    # Since the implementation does `p.lower() in t`, it's a substring match.
    assert _contains_any("caterpillar", ["cat", "pill"]) == ["cat", "pill"]

def test_contains_any_empty_phrase_in_list():
    # An empty string is always a substring of any string.
    assert _contains_any("hello", [""]) == [""]
    assert _contains_any("", [""]) == [""]
