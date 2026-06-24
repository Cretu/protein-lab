"""Pytest configuration: expose script modules under stable import names."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_MAP = {
    "protein_lab_setup": REPO_ROOT / "skills/setup/scripts/protein_lab_setup.py",
    "init_round": REPO_ROOT / "skills/local-rounds/scripts/init_round.py",
    "afserver_audit": REPO_ROOT / "skills/tool-af-server/scripts/afserver_audit.py",
    "prepare_pepmlm_payload": REPO_ROOT / "skills/tool-tamarind-pepmlm/scripts/prepare_pepmlm_payload.py",
    "inspect_pepmlm_result": REPO_ROOT / "skills/tool-tamarind-pepmlm/scripts/inspect_pepmlm_result.py",
    "tamarind_api": REPO_ROOT / "skills/tool-tamarind-api/scripts/tamarind_api.py",
    "scaffold_tool_skill": REPO_ROOT / "skills/tool-creator/scripts/scaffold_tool_skill.py",
    "classify_research_asset": REPO_ROOT / "skills/skill-curator/scripts/classify_research_asset.py",
    "knowledge_base": REPO_ROOT / "skills/knowledge-base/scripts/knowledge_base.py",
}


def _load(name: str, path: Path) -> None:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)


for module_name, module_path in SCRIPT_MAP.items():
    _load(module_name, module_path)
