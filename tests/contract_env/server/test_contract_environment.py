from src.contract_env.server.contract_environment import Draft, Clause


def test_draft_to_markdown_empty():
    draft = Draft(
        topic="Open Source AI",
        requirements=[],
        forbidden_phrases=[],
        numeric_constraints={},
        clauses=[],
        definitions={},
    )
    expected = "# Policy Draft\n\n**Topic**: Open Source AI\n"
    assert draft.to_markdown() == expected


def test_draft_to_markdown_with_clauses():
    draft = Draft(
        topic="Data Privacy",
        requirements=[],
        forbidden_phrases=[],
        numeric_constraints={},
        clauses=[
            Clause(
                id="c_1", section="Retention", text="Data will be retained for 30 days."
            ),
            Clause(id="c_2", section="Access", text="Users can request access."),
            Clause(id="c_3", section="Retention", text="Logs are kept separately."),
        ],
        definitions={},
    )
    expected = (
        "# Policy Draft\n\n"
        "**Topic**: Data Privacy\n"
        "## Access\n"
        "- (c_2) Users can request access.\n\n"
        "## Retention\n"
        "- (c_1) Data will be retained for 30 days.\n"
        "- (c_3) Logs are kept separately.\n"
    )
    assert draft.to_markdown() == expected


def test_draft_to_markdown_with_definitions():
    draft = Draft(
        topic="Terms of Service",
        requirements=[],
        forbidden_phrases=[],
        numeric_constraints={},
        clauses=[],
        definitions={
            "User": "Any person accessing the service.",
            "Service": "The web application provided.",
        },
    )
    expected = (
        "# Policy Draft\n\n"
        "**Topic**: Terms of Service\n"
        "## Definitions\n"
        "- **Service**: The web application provided.\n"
        "- **User**: Any person accessing the service.\n"
    )
    assert draft.to_markdown() == expected


def test_draft_to_markdown_full():
    draft = Draft(
        topic="Acceptable Use",
        requirements=[],
        forbidden_phrases=[],
        numeric_constraints={},
        clauses=[
            Clause(id="c_1", section="Prohibited Activities", text="No spamming."),
        ],
        definitions={
            "Spam": "Unsolicited bulk messages.",
        },
    )
    expected = (
        "# Policy Draft\n\n"
        "**Topic**: Acceptable Use\n"
        "## Prohibited Activities\n"
        "- (c_1) No spamming.\n\n"
        "## Definitions\n"
        "- **Spam**: Unsolicited bulk messages.\n"
    )
    assert draft.to_markdown() == expected
