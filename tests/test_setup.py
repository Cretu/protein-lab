from __future__ import annotations

import argparse
import json
from pathlib import Path

import protein_lab_setup as setup  # noqa: E402


def _configure_args(**overrides) -> argparse.Namespace:
    base = {
        "config": "/tmp/unused-config.json",
        "workspace_root": None,
        "plugin_root": "",
        "project_id": "",
        "team_name": "Team Alpha",
        "wiki_root": None,
        "wiki_allow_write": False,
        "feishu_task_list_url": "",
        "feishu_docs_folder_url": "",
        "feishu_tenant_domain": "",
        "enable_feishu": False,
        "enable_tamarind": False,
        "enable_modal": False,
        "dry_run": False,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def test_configure_defaults_to_current_directory(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    config_path = tmp_path / "config.json"
    config = setup.configure(_configure_args(config=str(config_path), enable_tamarind=True))
    assert config["workspace_root"] == str(tmp_path.resolve())
    assert config["team_name"] == "Team Alpha"
    assert config["enabled_tools"]["tamarind"] is True
    assert config["active_project"] == "team-alpha"
    assert (tmp_path / ".protein-lab" / "project.json").is_file()
    written = json.loads(config_path.read_text())
    assert "TAMARIND_API_KEY" not in json.dumps(written)


def test_configure_creates_writable_wiki_when_allowed(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    wiki = tmp_path / "wiki"
    config_path = tmp_path / "config.json"
    config = setup.configure(
        _configure_args(
            config=str(config_path),
            workspace_root=str(workspace),
            wiki_root=str(wiki),
            wiki_allow_write=True,
            feishu_task_list_url="https://example.test/tasklist",
        )
    )
    assert workspace.is_dir()
    assert wiki.is_dir()
    assert config["enabled_tools"]["feishu"] is True
    assert config["wiki"]["allow_write"] is True


def test_doctor_reports_bad_config_as_blocked(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.json"
    config_path.write_text("{bad json")
    report = setup.run_doctor(config_path, tmp_path)
    assert report["summary"]["state"] == "blocked"
    assert report["checks"]["config"]["state"] == "blocked"


def test_doctor_writes_reports_without_secret_values(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("TAMARIND_API_KEY", "super-secret-value")
    config_path = tmp_path / "config.json"
    setup.configure(_configure_args(config=str(config_path), workspace_root=str(tmp_path)))
    out_dir = tmp_path / "doctor"
    report = setup.run_doctor(config_path, tmp_path, out_dir)
    assert report["checks"]["project_config"]["state"] == "ready"
    assert report["checks"]["tamarind_api_key"]["present"] is True
    combined = (out_dir / "protein_lab_doctor.json").read_text() + (out_dir / "protein_lab_doctor.md").read_text()
    assert "super-secret-value" not in combined
