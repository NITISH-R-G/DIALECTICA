# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

from fastmcp import FastMCP

try:
    from openenv.core.env_server.mcp_environment import MCPEnvironment
    from openenv.core.env_server.types import Action, Observation, State
except ImportError:
    from openenv.core.env_server.mcp_environment import MCPEnvironment
    from openenv.core.env_server.types import Action, Observation, State


@dataclass
class Clause:
    id: str
    section: str
    text: str


@dataclass
class Draft:
    topic: str
    requirements: list[str]
    forbidden_phrases: list[str]
    numeric_constraints: dict[str, int]
    clauses: list[Clause] = field(default_factory=list)
    definitions: dict[str, str] = field(default_factory=dict)

    _req_tuples: list[tuple[str, str]] = field(init=False)
    _forb_tuples: list[tuple[str, str]] = field(init=False)

    def __post_init__(self):
        self._req_tuples = [(r, r.lower()) for r in self.requirements]
        self._forb_tuples = [(p, p.lower()) for p in self.forbidden_phrases]

    def to_markdown(self) -> str:
        by_section: dict[str, list[Clause]] = {}
        for c in self.clauses:
            by_section.setdefault(c.section, []).append(c)

        parts: list[str] = [f"# Policy Draft\n\n**Topic**: {self.topic}\n"]
        for sec in sorted(by_section.keys()):
            parts.append(f"## {sec}\n")
            for c in by_section[sec]:
                parts.append(f"- ({c.id}) {c.text}\n")
            parts.append("\n")

        if self.definitions:
            parts.append("## Definitions\n")
            for k in sorted(self.definitions.keys()):
                parts.append(f"- **{k}**: {self.definitions[k]}\n")
            parts.append("\n")
        return "".join(parts).strip() + "\n"


def _contains_any(text_lower: str, phrases_tuples: list[tuple[str, str]]) -> list[str]:
    return [p for p, p_lower in phrases_tuples if p_lower in text_lower]


def _coverage_score(
    text_lower: str, requirements_tuples: list[tuple[str, str]]
) -> tuple[int, list[str]]:
    missing: list[str] = []
    for r, r_lower in requirements_tuples:
        if r_lower not in text_lower:
            missing.append(r)
    covered = len(requirements_tuples) - len(missing)
    return covered, missing


def _contradiction_checks(text_lower: str) -> list[str]:
    # Lightweight, objective checks (expand later):
    # - retention days must be consistent with constraint marker if present.
    issues: list[str] = []
    if "retain" in text_lower and "indefinitely" in text_lower:
        issues.append(
            "Mentions retention and 'indefinitely' (potentially contradictory)."
        )
    if "we will never" in text_lower and "may" in text_lower and "share" in text_lower:
        issues.append(
            "Contains 'we will never' and 'may share' (potential contradiction)."
        )
    return issues


def _compute_reward(draft: Draft) -> dict[str, Any]:
    md = draft.to_markdown()
    md_lower = md.lower()

    covered, missing = _coverage_score(md_lower, draft._req_tuples)
    forbidden_hits = _contains_any(md_lower, draft._forb_tuples)
    contradictions = _contradiction_checks(md_lower)

    # Reward components (simple but informative; RLVR-friendly)
    r_coverage = covered / max(1, len(draft.requirements))  # 0..1
    r_forbidden = -0.25 * len(forbidden_hits)  # penalty
    r_contra = -0.15 * len(contradictions)
    r_defs = 0.05 * min(6, len(draft.definitions))  # small bonus for defining terms

    total = (1.5 * r_coverage) + r_forbidden + r_contra + r_defs

    return {
        "reward_total": float(total),
        "reward_components": {
            "coverage": float(r_coverage),
            "forbidden_penalty": float(r_forbidden),
            "contradiction_penalty": float(r_contra),
            "definitions_bonus": float(r_defs),
        },
        "audit": {
            "covered": covered,
            "missing": missing,
            "forbidden_hits": forbidden_hits,
            "contradictions": contradictions,
            "constraints": draft.numeric_constraints,
        },
        "draft_markdown": md,
    }


class ContractComplianceEnvironment(MCPEnvironment):
    """
    Contract-to-Compliance environment (multi-agent roles via tools).

    Tools expose stepwise actions (draft clause edits) and return an objective
    reward breakdown from multiple verifiers (coverage, forbidden phrases,
    contradictions, etc).
    """

    def __init__(self):
        mcp = FastMCP("contract_to_compliance")

        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._draft: Draft | None = None

        @mcp.tool
        def reset_episode(topic: str = "AI should be open source") -> dict:
            """Start a fresh episode with a topic and default compliance rubric."""
            self._state = State(episode_id=str(uuid4()), step_count=0)

            # Demo rubric (expand to GDPR/CCPA + org constraints later)
            requirements = [
                "purpose limitation",
                "data minimization",
                "lawful basis",
                "user consent",
                "data retention",
                "access & deletion request",
                "security safeguards",
                "third-party sharing disclosure",
            ]
            forbidden_phrases = [
                "we sell your data",
                "no refunds",
                "we are not responsible",
                "indefinitely",
                "without consent",
            ]
            numeric_constraints = {"retention_days_max": 30}

            self._draft = Draft(
                topic=topic,
                requirements=requirements,
                forbidden_phrases=forbidden_phrases,
                numeric_constraints=numeric_constraints,
                clauses=[],
                definitions={},
            )

            payload = _compute_reward(self._draft)
            payload["event"] = "reset"
            payload["episode_id"] = self._state.episode_id
            payload["step_count"] = self._state.step_count
            return payload

        @mcp.tool
        def get_state() -> dict:
            """Return current draft + audit + reward breakdown."""
            if self._draft is None:
                return {"error": "Call reset_episode first."}
            payload = _compute_reward(self._draft)
            payload["event"] = "state"
            payload["episode_id"] = self._state.episode_id
            payload["step_count"] = self._state.step_count
            return payload

        @mcp.tool
        def add_clause(section: str, text: str) -> dict:
            """Policy Drafter: add a clause in a section."""
            if self._draft is None:
                return {"error": "Call reset_episode first."}
            cid = f"c_{uuid4().hex[:8]}"
            self._draft.clauses.append(
                Clause(id=cid, section=section.strip(), text=text.strip())
            )
            self._state.step_count += 1
            payload = _compute_reward(self._draft)
            payload["event"] = "add_clause"
            payload["clause_id"] = cid
            payload["episode_id"] = self._state.episode_id
            payload["step_count"] = self._state.step_count
            return payload

        @mcp.tool
        def edit_clause(clause_id: str, new_text: str) -> dict:
            """Policy Drafter: edit an existing clause by id."""
            if self._draft is None:
                return {"error": "Call reset_episode first."}
            for c in self._draft.clauses:
                if c.id == clause_id:
                    c.text = new_text.strip()
                    self._state.step_count += 1
                    payload = _compute_reward(self._draft)
                    payload["event"] = "edit_clause"
                    payload["clause_id"] = clause_id
                    payload["episode_id"] = self._state.episode_id
                    payload["step_count"] = self._state.step_count
                    return payload
            return {"error": f"Unknown clause_id: {clause_id}"}

        @mcp.tool
        def delete_clause(clause_id: str) -> dict:
            """Policy Drafter: delete a clause by id."""
            if self._draft is None:
                return {"error": "Call reset_episode first."}
            before = len(self._draft.clauses)
            self._draft.clauses = [c for c in self._draft.clauses if c.id != clause_id]
            if len(self._draft.clauses) == before:
                return {"error": f"Unknown clause_id: {clause_id}"}
            self._state.step_count += 1
            payload = _compute_reward(self._draft)
            payload["event"] = "delete_clause"
            payload["clause_id"] = clause_id
            payload["episode_id"] = self._state.episode_id
            payload["step_count"] = self._state.step_count
            return payload

        @mcp.tool
        def add_definition(term: str, definition: str) -> dict:
            """Policy Drafter: add/overwrite a definition."""
            if self._draft is None:
                return {"error": "Call reset_episode first."}
            self._draft.definitions[term.strip()] = definition.strip()
            self._state.step_count += 1
            payload = _compute_reward(self._draft)
            payload["event"] = "add_definition"
            payload["episode_id"] = self._state.episode_id
            payload["step_count"] = self._state.step_count
            return payload

        @mcp.tool
        def redteam_probe(question: str) -> dict:
            """Red Team: add an adversarial probe (doesn't mutate draft, but scores robustness later)."""
            if self._draft is None:
                return {"error": "Call reset_episode first."}
            # For v1 we simply surface the probe in the audit payload.
            payload = _compute_reward(self._draft)
            payload["event"] = "redteam_probe"
            payload["probe"] = question.strip()
            payload["episode_id"] = self._state.episode_id
            payload["step_count"] = self._state.step_count
            return payload

        super().__init__(mcp)

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Observation:
        # This env is driven via MCP tools; reset() just returns readiness.
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)
        return Observation(done=False, reward=0.0, metadata={"status": "ready"})

    def _step_impl(
        self,
        action: Action,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> Observation:
        return Observation(
            done=False,
            reward=0.0,
            metadata={
                "error": f"Unknown action type: {type(action).__name__}. "
                "Use ListToolsAction or CallToolAction for MCP interactions."
            },
        )
