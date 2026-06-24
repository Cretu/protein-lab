from __future__ import annotations

from pathlib import Path

import init_round  # noqa: E402  (loaded via conftest)


def test_slugify_handles_vs_and_special_chars() -> None:
    assert init_round.slugify("GRK4 vs. ZDHHC17 ANK1-305") == "GRK4_vs_ZDHHC17_ANK1_305"


def test_slugify_empty_falls_back() -> None:
    assert init_round.slugify("   ") == "experiment_round"


def test_resolve_root_prefers_cli(tmp_path: Path) -> None:
    assert init_round.resolve_root(str(tmp_path)) == tmp_path.resolve()


def test_resolve_root_defaults_to_cwd(tmp_path: Path) -> None:
    assert init_round.resolve_root(None, cwd=tmp_path) == tmp_path.resolve()


def test_resolve_root_uses_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PROTEIN_LAB_ROOT", str(tmp_path))
    assert init_round.resolve_root(None, use_cwd=False) == tmp_path.resolve()


def test_resolve_root_uses_config_when_cwd_disabled(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("PROTEIN_LAB_ROOT", raising=False)
    config = tmp_path / "config.json"
    workspace = tmp_path / "workspace"
    config.write_text('{"workspace_root": "' + str(workspace) + '"}')
    assert init_round.resolve_root(None, use_cwd=False, config_path=str(config)) == workspace.resolve()


def test_resolve_root_prefers_nearest_project_config(tmp_path: Path) -> None:
    workspace = tmp_path / "project-a"
    nested = workspace / "analysis" / "subdir"
    nested.mkdir(parents=True)
    config_dir = workspace / ".protein-lab"
    config_dir.mkdir()
    (config_dir / "project.json").write_text('{"workspace_root": "' + str(workspace) + '"}')
    assert init_round.resolve_root(None, cwd=nested) == workspace.resolve()


def test_main_creates_round_structure_in_cwd(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["init_round", "--title", "Test Round vs Target"])
    assert init_round.main() == 0
    out = capsys.readouterr().out.strip()
    round_dir = Path(out)
    assert round_dir.is_dir()
    assert (round_dir / f"{round_dir.name}_plan.md").is_file()
    assert (round_dir / "status_log.md").is_file()
    assert (round_dir / "inputs").is_dir()
    assert (round_dir / "outputs" / "raw").is_dir()
    assert (round_dir / "outputs" / "parsed").is_dir()
    assert (round_dir / "reports").is_dir()
