from __future__ import annotations

from pathlib import Path

import pytest

import scaffold_tool_skill as scaffold  # noqa: E402


def test_normalize_tool_name_adds_prefix() -> None:
    assert scaffold.normalize_tool_name("Tamarind PepMLM") == "tool-tamarind-pepmlm"


def test_scaffold_tool_skill_writes_valid_frontmatter(tmp_path: Path) -> None:
    path = scaffold.scaffold(tmp_path, "Example API", "api", "Example API")
    text = path.read_text()
    assert path == tmp_path / "tool-example-api" / "SKILL.md"
    assert "name: tool-example-api" in text
    assert "Result Audit" in text


def test_scaffold_refuses_overwrite_without_force(tmp_path: Path) -> None:
    scaffold.scaffold(tmp_path, "Example CLI", "cli", "Example CLI")
    with pytest.raises(FileExistsError):
        scaffold.scaffold(tmp_path, "Example CLI", "cli", "Example CLI")
