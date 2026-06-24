from __future__ import annotations

import classify_research_asset as curator  # noqa: E402


def test_tool_workflow_routes_to_tool_creator() -> None:
    result = curator.classify("repeatable API workflow for a new web platform", repeatable=True)
    assert result["primary"] == "tool-creator"


def test_experiment_result_routes_to_knowledge_base() -> None:
    result = curator.classify("experiment result and literature decision for project")
    assert result["primary"] == "knowledge-base"


def test_team_specific_workflow_routes_to_team_skill() -> None:
    result = curator.classify("repeatable internal protocol workflow", repeatable=True, team_specific=True)
    assert result["primary"] == "team-research-skill"
