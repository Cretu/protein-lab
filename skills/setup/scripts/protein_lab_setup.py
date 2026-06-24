#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("~/.config/protein-lab/config.json").expanduser()
DEFAULT_WORKSPACE_ROOT = Path("~/Documents/Protein Lab").expanduser()
PROJECT_CONFIG_DIR = ".protein-lab"
PROJECT_CONFIG_FILE = "project.json"
REQUIRED_PYTHON = (3, 10)
SECRET_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "COOKIE")
# Reject strings that look like real credentials (long hex or base64 chunks)
# even when the field name itself is innocuous. Slashes are excluded from the
# base64 alternative so filesystem paths do not match as one giant blob.
# The base64 alternative additionally requires a lowercase letter or a digit
# so long all-uppercase amino-acid sequences are not mistaken for a token.
HEX_RUN_RE = re.compile(r"\b[A-Fa-f0-9]{40,}\b")
BASE64_RUN_RE = re.compile(r"\b[A-Za-z0-9+]{40,}={0,2}\b")


def _looks_like_credential(value: str) -> bool:
    if HEX_RUN_RE.search(value):
        return True
    for match in BASE64_RUN_RE.finditer(value):
        token = match.group(0)
        if any(c.islower() or c.isdigit() for c in token):
            return True
    return False


def slugify_project_id(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower())
    return re.sub(r"-+", "-", slug).strip("-") or "protein-lab-project"


def project_config_path(workspace_root: Path) -> Path:
    return workspace_root / PROJECT_CONFIG_DIR / PROJECT_CONFIG_FILE


def find_project_config(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        path = candidate / PROJECT_CONFIG_DIR / PROJECT_CONFIG_FILE
        if path.exists():
            return path
    return None


def default_config(
    workspace_root: Path | None = None,
    plugin_root: Path | None = None,
    *,
    project_id: str | None = None,
    config_scope: str = "global",
) -> dict[str, Any]:
    workspace = (workspace_root or Path.cwd()).expanduser().resolve()
    plugin = plugin_root.expanduser().resolve() if plugin_root else None
    resolved_project_id = slugify_project_id(project_id or workspace.name or "protein-lab-project")
    return {
        "schema_version": 1,
        "config_scope": config_scope,
        "project_id": resolved_project_id,
        "team_name": "Protein Lab",
        "language": "zh-CN",
        "workspace_root": str(workspace),
        "project_config_path": str(project_config_path(workspace)),
        "plugin_root": str(plugin) if plugin else "",
        "active_project": resolved_project_id if config_scope == "global" else "",
        "projects": {} if config_scope == "global" else None,
        "enabled_tools": {
            "af_server": True,
            "feishu": False,
            "tamarind": False,
            "modal": False,
        },
        "feishu": {
            "task_list_url": "",
            "docs_folder_url": "",
            "tenant_domain": "",
        },
        "wiki": {
            "type": "local-markdown",
            "root": "",
            "allow_write": False,
        },
    }


def load_json_config(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact json error varies
        return None, f"Config is not valid JSON: {exc}"
    if not isinstance(data, dict):
        return None, "Config root must be a JSON object."
    return data, None


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> tuple[dict[str, Any] | None, str | None]:
    return load_json_config(path)


def load_effective_config(config_path: Path, cwd: Path) -> tuple[dict[str, Any] | None, str | None, Path | None]:
    project_path = find_project_config(cwd)
    if project_path:
        config, error = load_json_config(project_path)
        return config, error, project_path
    config, error = load_config(config_path)
    return config, error, config_path if config else None


def write_config(config: dict[str, Any], path: Path = DEFAULT_CONFIG_PATH) -> Path:
    text = json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True)
    assert_no_secret_values(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")
    return path


def write_project_config(config: dict[str, Any], workspace_root: Path) -> Path:
    project_path = project_config_path(workspace_root)
    project_path.parent.mkdir(parents=True, exist_ok=True)
    return write_config(config, project_path)


def assert_no_secret_values(value: Any) -> None:
    """Catch accidental storage of obvious secret-like keys or credential-shaped values in config data."""
    if isinstance(value, dict):
        for key, child in value.items():
            if any(hint in str(key).upper() for hint in SECRET_HINTS):
                raise ValueError(f"Refusing to write secret-like config key: {key}")
            assert_no_secret_values(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_secret_values(child)
    elif isinstance(value, str):
        if _looks_like_credential(value):
            raise ValueError("Refusing to write secret-like value into config.")


def path_status(path_value: str | None, *, should_exist: bool = True) -> dict[str, Any]:
    if not path_value:
        return {"state": "needs_config", "path": "", "message": "not configured"}
    path = Path(path_value).expanduser()
    exists = path.exists()
    writable = False
    if exists:
        writable = os.access(path, os.W_OK)
    elif not should_exist:
        parent = path.parent if path.parent != path else Path.cwd()
        writable = parent.exists() and os.access(parent, os.W_OK)
    state = "ready" if exists and writable else "blocked" if exists and not writable else "needs_config"
    return {
        "state": state,
        "path": str(path),
        "exists": exists,
        "writable": writable,
        "message": "ok" if state == "ready" else "missing or not writable",
    }


def command_check(name: str) -> dict[str, Any]:
    found = shutil.which(name)
    return {
        "state": "ready" if found else "optional",
        "command": name,
        "path": found or "",
        "message": "available" if found else "not found",
    }


def browser_check() -> dict[str, Any]:
    candidates = []
    if platform.system() == "Darwin":
        candidates.extend(
            [
                "/Applications/Google Chrome.app",
                "/Applications/Chrome.app",
                "/Applications/Microsoft Edge.app",
                "/Applications/Safari.app",
            ]
        )
    candidates.extend([shutil.which("google-chrome") or "", shutil.which("chromium") or ""])
    found = next((item for item in candidates if item and Path(item).exists()), "")
    return {
        "state": "ready" if found else "optional",
        "path": found,
        "message": "browser found" if found else "browser not detected by static check",
    }


def env_presence(name: str) -> dict[str, Any]:
    present = bool(os.environ.get(name))
    return {
        "state": "ready" if present else "needs_config",
        "name": name,
        "present": present,
        "message": "present in environment" if present else "not set",
    }


def plugin_cache_check() -> dict[str, Any]:
    cache_root = Path("~/.codex/plugins/cache/personal/protein-lab").expanduser()
    versions = sorted([p.name for p in cache_root.iterdir() if p.is_dir()]) if cache_root.exists() else []
    return {
        "state": "ready" if versions else "needs_config",
        "path": str(cache_root),
        "versions": versions,
        "message": "installed cache found" if versions else "no personal plugin cache found",
    }


def run_doctor(config_path: Path, cwd: Path, out_dir: Path | None = None) -> dict[str, Any]:
    config, config_error, effective_path = load_effective_config(config_path, cwd)
    workspace = (config or {}).get("workspace_root") if config else ""
    plugin_root = (config or {}).get("plugin_root") if config else ""
    wiki_root = ((config or {}).get("wiki") or {}).get("root") if config else ""
    checks = {
        "python": {
            "state": "ready" if sys.version_info >= REQUIRED_PYTHON else "blocked",
            "version": sys.version.split()[0],
            "required": ".".join(str(x) for x in REQUIRED_PYTHON),
            "message": "ok" if sys.version_info >= REQUIRED_PYTHON else "Python 3.10+ required",
        },
        "config": {
            "state": "ready" if config and not config_error else "needs_config" if not config_error else "blocked",
            "path": str(effective_path or config_path),
            "message": "loaded" if config else config_error or "not configured",
        },
        "project_config": {
            "state": "ready" if effective_path and effective_path.name == PROJECT_CONFIG_FILE else "optional",
            "path": str(effective_path or ""),
            "project_id": (config or {}).get("project_id", ""),
            "message": "project-local config active" if effective_path and effective_path.name == PROJECT_CONFIG_FILE else "using global config or no config",
        },
        "workspace": path_status(workspace),
        "plugin_root": path_status(plugin_root) if plugin_root else {"state": "needs_config", "message": "not configured"},
        "plugin_cache": plugin_cache_check(),
        "wiki": path_status(wiki_root) if wiki_root else {"state": "optional", "message": "not configured"},
        "lark_cli": command_check("lark-cli"),
        "modal_cli": command_check("modal"),
        "browser": browser_check(),
        "tamarind_api_key": env_presence("TAMARIND_API_KEY"),
    }
    blocked = [name for name, check in checks.items() if check["state"] == "blocked"]
    needs_config = [name for name, check in checks.items() if check["state"] == "needs_config"]
    ready = [name for name, check in checks.items() if check["state"] == "ready"]
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "cwd": str(cwd.resolve()),
        "config_path": str(config_path),
        "effective_config_path": str(effective_path or ""),
        "summary": {
            "state": "blocked" if blocked else "needs_config" if needs_config else "ready",
            "ready": ready,
            "needs_config": needs_config,
            "blocked": blocked,
        },
        "checks": checks,
        "next_steps": next_steps(blocked, needs_config),
    }
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "protein_lab_doctor.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (out_dir / "protein_lab_doctor.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def next_steps(blocked: list[str], needs_config: list[str]) -> list[str]:
    if blocked:
        return [f"Fix blocked check: {blocked[0]}."]
    steps = []
    if "config" in needs_config or "workspace" in needs_config:
        steps.append("Run setup configure with the intended workspace root.")
    if "plugin_cache" in needs_config:
        steps.append("Install or reinstall the protein-lab plugin in Codex.")
    if "plugin_root" in needs_config:
        steps.append("Set plugin_root in config or PROTEIN_LAB_PLUGIN_ROOT in the shell.")
    if "tamarind_api_key" in needs_config:
        steps.append("Set TAMARIND_API_KEY in the environment only when Tamarind work is needed.")
    return steps or ["Environment is ready for a local-only smoke test."]


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Protein Lab Doctor",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Current directory: `{report['cwd']}`",
        f"- Overall state: **{report['summary']['state']}**",
        "",
        "## Checks",
        "",
        "| Area | State | Detail |",
        "|---|---:|---|",
    ]
    for name, check in report["checks"].items():
        detail = check.get("message") or check.get("path") or ""
        lines.append(f"| `{name}` | `{check['state']}` | {detail} |")
    lines.extend(["", "## Next Steps", ""])
    for step in report["next_steps"]:
        lines.append(f"- {step}")
    lines.append("")
    return "\n".join(lines)


def configure(args: argparse.Namespace) -> dict[str, Any]:
    config_path = Path(args.config).expanduser()
    workspace = Path(args.workspace_root).expanduser().resolve() if args.workspace_root else Path.cwd().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    plugin_root = Path(args.plugin_root).expanduser().resolve() if args.plugin_root else None
    project_id = slugify_project_id(getattr(args, "project_id", "") or args.team_name or workspace.name)
    project_config = default_config(workspace, plugin_root, project_id=project_id, config_scope="project")
    project_config["team_name"] = args.team_name or project_config["team_name"]
    project_config["enabled_tools"]["feishu"] = bool(args.enable_feishu or args.feishu_task_list_url or args.feishu_docs_folder_url)
    project_config["enabled_tools"]["tamarind"] = bool(args.enable_tamarind)
    project_config["enabled_tools"]["modal"] = bool(args.enable_modal)
    project_config["feishu"]["task_list_url"] = args.feishu_task_list_url or ""
    project_config["feishu"]["docs_folder_url"] = args.feishu_docs_folder_url or ""
    project_config["feishu"]["tenant_domain"] = args.feishu_tenant_domain or ""
    if args.wiki_root:
        wiki_root = Path(args.wiki_root).expanduser().resolve()
        if args.wiki_allow_write:
            wiki_root.mkdir(parents=True, exist_ok=True)
        project_config["wiki"]["root"] = str(wiki_root)
        project_config["wiki"]["allow_write"] = bool(args.wiki_allow_write)
    global_config = default_config(workspace, plugin_root, project_id=project_id, config_scope="global")
    for key in ("team_name", "enabled_tools", "feishu", "wiki"):
        global_config[key] = project_config[key]
    global_config["active_project"] = project_id
    global_config["projects"] = {
        project_id: {
            "team_name": project_config["team_name"],
            "workspace_root": project_config["workspace_root"],
            "project_config_path": project_config["project_config_path"],
        }
    }
    if args.dry_run:
        return global_config
    write_project_config(project_config, workspace)
    write_config(global_config, config_path)
    return global_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Protein Lab setup and environment doctor.")
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Run a read-only environment check.")
    doctor.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    doctor.add_argument("--out-dir", default=None)
    configure_p = sub.add_parser("configure", help="Write local Protein Lab configuration.")
    configure_p.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    configure_p.add_argument("--workspace-root", default=None, help="Defaults to the current directory.")
    configure_p.add_argument("--plugin-root", default=os.environ.get("PROTEIN_LAB_PLUGIN_ROOT", ""))
    configure_p.add_argument("--project-id", default="")
    configure_p.add_argument("--team-name", default="Protein Lab")
    configure_p.add_argument("--wiki-root", default=None)
    configure_p.add_argument("--wiki-allow-write", action="store_true")
    configure_p.add_argument("--feishu-task-list-url", default="")
    configure_p.add_argument("--feishu-docs-folder-url", default="")
    configure_p.add_argument("--feishu-tenant-domain", default="")
    configure_p.add_argument("--enable-feishu", action="store_true")
    configure_p.add_argument("--enable-tamarind", action="store_true")
    configure_p.add_argument("--enable-modal", action="store_true")
    configure_p.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "doctor":
        out_dir = Path(args.out_dir).expanduser() if args.out_dir else None
        report = run_doctor(Path(args.config).expanduser(), Path.cwd(), out_dir)
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
        return 0 if report["summary"]["state"] != "blocked" else 2
    if args.command == "configure":
        config = configure(args)
        print(json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
