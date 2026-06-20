from __future__ import annotations

from pathlib import Path

import init_round  # noqa: E402  (loaded via conftest)


def test_slugify_handles_vs_and_special_chars() -> None:
    assert init_round.slugify("GRK4 vs. ZDHHC17 ANK1-305") == "GRK4_vs_ZDHHC17_ANK1_305"


def test_slugify_empty_falls_back() -> None:
    assert init_round.slugify("   ") == "experiment_round"


def test_resolve_root_prefers_cli(tmp_path: Path) -> None:
    assert init_round.resolve_root(str(tmp_path)) == tmp_path.resolve()


def test_resolve_root_uses_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PROTEIN_LAB_ROOT", str(tmp_path))
    assert init_round.resolve_root(None) == tmp_path.resolve()


def test_main_creates_plan_and_status(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("PROTEIN_LAB_ROOT", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["init_round", "--title", "Test Round vs Target"])
    assert init_round.main() == 0
    out = capsys.readouterr().out.strip()
    round_dir = Path(out)
    assert round_dir.is_dir()
    assert (round_dir / f"{round_dir.name}_plan.md").is_file()
    assert (round_dir / "status_log.md").is_file()
