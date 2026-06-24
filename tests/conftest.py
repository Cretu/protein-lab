"""Pytest configuration: expose script modules under stable import names.

Each script is loaded eagerly but failures are isolated per module via a lazy
stub. If `skills/foo/scripts/foo.py` fails to import, only tests that actually
import the `foo` module fail; the rest of the session still runs.
"""
from __future__ import annotations

import importlib.abc
import importlib.machinery
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


class _LazyScriptLoader(importlib.abc.Loader):
    def __init__(self, path: Path) -> None:
        self._path = path

    def create_module(self, spec):  # noqa: D401 — importlib API
        return None

    def exec_module(self, module) -> None:
        spec = importlib.util.spec_from_file_location(module.__name__, self._path)
        assert spec and spec.loader
        spec.loader.exec_module(module)


class _LazyScriptFinder(importlib.abc.MetaPathFinder):
    def __init__(self, mapping: dict[str, Path]) -> None:
        self._mapping = mapping

    def find_spec(self, fullname, path=None, target=None):
        script_path = self._mapping.get(fullname)
        if script_path is None:
            return None
        return importlib.machinery.ModuleSpec(fullname, _LazyScriptLoader(script_path))


sys.meta_path.insert(0, _LazyScriptFinder(SCRIPT_MAP))
